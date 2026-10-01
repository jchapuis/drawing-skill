import { createRoot } from 'react-dom/client'
import {
  Box,
  Circle2d,
  DefaultColorThemePalette,
  DrawShapeUtil,
  Polygon2d,
  Polyline2d,
  STROKE_SIZES,
  SVGContainer,
  Tldraw,
  createShapeId,
  getSnapshot,
  last,
  loadSnapshot,
  useDefaultColorTheme,
} from 'tldraw'
import 'tldraw/tldraw.css'
// tldraw does not export the pieces its draw shape is built from, so they are
// imported from the files themselves. They are the same module instances the
// package uses, read and never changed.
import {
  getFreehandOptions,
  getPointsFromSegments,
} from '../node_modules/tldraw/dist-esm/lib/shapes/draw/getPath.mjs'
import { getStrokePoints } from '../node_modules/tldraw/dist-esm/lib/shapes/shared/freehand/getStrokePoints.mjs'
import { getSvgPathFromStrokePoints } from '../node_modules/tldraw/dist-esm/lib/shapes/shared/freehand/svg.mjs'
import { svgInk } from '../node_modules/tldraw/dist-esm/lib/shapes/shared/freehand/svgInk.mjs'
import { ShapeFill } from '../node_modules/tldraw/dist-esm/lib/shapes/shared/ShapeFill.mjs'
import { getFillDefForExport } from '../node_modules/tldraw/dist-esm/lib/shapes/shared/defaultStyleDefs.mjs'

// Every mark carries the stage that made it, so a later stage can fade the
// construction back or wipe it entirely -- the pencil under the ink.
const STAGE_LOOK = {
  // saturated, so a stage look reads on its own and survives an overlay blend;
  // pastel at 0.6 has no pixel a threshold can find
  gesture: { color: 'blue', size: 'm', dash: 'draw', opacity: 0.85 },
  construction: { color: 'grey', size: 's', dash: 'draw', opacity: 0.6 },
  blockin: { color: 'violet', size: 's', dash: 'solid', opacity: 0.9 },
  contour: { color: 'black', size: 's', dash: 'draw', opacity: 0.9 },
  ink: { color: 'black', size: 'm', dash: 'draw', opacity: 1 },
  fill: { color: 'orange', size: 's', dash: 'draw', opacity: 1 },
  // the corrective pass: colour repainted under the line, body colour over it
  mend: { color: 'orange', size: 's', dash: 'solid', opacity: 1 },
  correct: { color: 'white', size: 's', dash: 'draw', opacity: 1 },
  frame: { color: 'grey', size: 's', dash: 'solid', opacity: 0.03 },
}

// tldraw ships 13 fixed colours. The palette object is a plain mutable export,
// so a drawing with its own palette repoints the names it needs at real values
// rather than settling for the nearest stock hue.
function repaint(palette) {
  for (const [name, value] of Object.entries(palette ?? {})) {
    if (name === 'background') {
      DefaultColorThemePalette.lightMode.background = value
      continue
    }
    const slot = DefaultColorThemePalette.lightMode[name]
    if (!slot) continue
    slot.solid = value
    slot.fill = value
    slot.semi = value
    slot.pattern = value
    slot.note = { ...(slot.note ?? {}), fill: value }
  }
}

function encode(blob) {
  return new Promise((done) => {
    const reader = new FileReader()
    reader.onloadend = () => done(String(reader.result).split(',')[1])
    reader.readAsDataURL(blob)
  })
}

/**
 * The two ways an artist catches their own mistakes, done to the export.
 *
 * Flipping breaks the habituation that hides a lopsided drawing from the person
 * who drew it -- errors you have stopped being able to see are obvious the
 * moment the image is mirrored. Squinting throws away the linework and leaves
 * only the value masses, which is how you check whether the thing reads as a
 * shape at all before you have spent any effort on detail.
 */
function redraw(blob, options) {
  return new Promise((done) => {
    const image = new Image()
    image.onload = () => {
      // The exported bitmap is not necessarily one pixel per page unit -- the
      // browser's own device ratio is in there too -- so a crop expressed in
      // page units is converted against what actually came back, never against
      // the scale that was asked for.
      const factor = options.pageWidth ? image.width / options.pageWidth : 1
      const crop = options.crop
        ? options.crop.map((value) => Math.round(value * factor))
        : [0, 0, image.width, image.height]
      const surface = document.createElement('canvas')
      // an export at the frame's bounds can come back a pixel short of the
      // frame: size the canvas from the frame, and copy the last row and
      // column into what is missing rather than resample the whole picture
      surface.width = options.size ? options.size[0] : crop[2]
      surface.height = options.size ? options.size[1] : crop[3]
      const pen = surface.getContext('2d')
      if (options.size) {
        pen.drawImage(image, image.width - 1, 0, 1, image.height,
          image.width - 1, 0, surface.width - image.width + 1, image.height)
        pen.drawImage(image, 0, image.height - 1, image.width, 1,
          0, image.height - 1, surface.width, surface.height - image.height + 1)
      }
      if (options.squint) pen.filter = `blur(${options.squint}px)`
      if (options.flip) {
        pen.translate(surface.width, 0)
        pen.scale(-1, 1)
      }
      pen.drawImage(image, crop[0], crop[1], crop[2], crop[3], 0, 0, crop[2], crop[3])
      surface.toBlob(done, 'image/png')
    }
    image.src = URL.createObjectURL(blob)
  })
}

function asPoints(raw) {
  return raw.map((point) =>
    Array.isArray(point)
      ? { x: point[0], y: point[1], z: point.length > 2 ? point[2] : 0.5 }
      : { x: point.x, y: point.y, z: point.z ?? 0.5 }
  )
}

function stroke(editor, op) {
  const look = STAGE_LOOK[op.stage] ?? STAGE_LOOK.ink
  const points = asPoints(op.points)
  if (points.length < 2) return null

  // tldraw stores a draw shape's points relative to the shape's own origin
  const originX = Math.min(...points.map((point) => point.x))
  const originY = Math.min(...points.map((point) => point.y))
  const id = createShapeId()

  editor.createShape({
    id,
    type: 'draw',
    x: originX,
    y: originY,
    opacity: op.opacity ?? look.opacity,
    meta: { stage: op.stage ?? 'ink', tag: op.tag ?? '', note: op.note ?? '' },
    props: {
      color: op.color ?? look.color,
      size: op.size ?? look.size,
      dash: op.dash ?? look.dash,
      fill: op.fill ?? 'none',
      isClosed: op.closed ?? false,
      isComplete: true,
      isPen: true,
      scale: op.scale ?? 1,
      segments: [
        {
          type: op.straight ? 'straight' : 'free',
          points: points.map((point) => ({
            x: point.x - originX,
            y: point.y - originY,
            z: point.z,
          })),
        },
      ],
    },
  })
  return id
}

function byStage(editor, stage) {
  return editor
    .getCurrentPageShapes()
    .filter((shape) => shape.meta?.stage === stage)
}

function apply(editor, ops) {
  const made = []
  for (const op of ops) {
    switch (op.op) {
      case 'stroke': {
        const id = stroke(editor, op)
        if (id) made.push(id)
        break
      }
      case 'fade': {
        const shapes = byStage(editor, op.stage)
        editor.updateShapes(
          shapes.map((shape) => ({
            id: shape.id,
            type: shape.type,
            opacity: op.opacity ?? 0.12,
          }))
        )
        break
      }
      case 'erase': {
        const ids = op.ids ?? byStage(editor, op.stage).map((shape) => shape.id)
        editor.deleteShapes(ids)
        break
      }
      case 'back': {
        // Flat colour belongs UNDER the ink: the line then covers the edge of
        // the fill, which is what hides the fact that no hand cuts a colour
        // exactly to a line.
        editor.sendToBack(byStage(editor, op.stage).map((shape) => shape.id))
        break
      }
      case 'clear':
        editor.deleteShapes(editor.getCurrentPageShapes().map((shape) => shape.id))
        break
      default:
        throw new Error(`unknown op: ${op.op}`)
    }
  }
  return made
}

// tldraw smooths every pen stroke with a fixed streamline and smoothing of
// 0.62. That irons out anything a few pixels across: a hook at the start of a
// fast stroke, a wobble, a small overshoot. `?streamline=X` in the page address
// swaps in this draw shape, which is tldraw's own one with those two numbers set
// to X (lower keeps more of the points as given). Without it the stock shape
// draws, so every render is exactly what it was.
const STREAMLINE = (() => {
  const raw = new URLSearchParams(window.location.search).get('streamline')
  if (raw === null) return null
  const value = Number(raw)
  if (!(value >= 0 && value <= 1)) throw new Error(`streamline must be 0..1, got ${raw}`)
  return value
})()

function freehand(props, width, complete, solid) {
  return { ...getFreehandOptions(props, width, complete, solid), streamline: STREAMLINE, smoothing: STREAMLINE }
}

function strokeWidth(shape) {
  return (STROKE_SIZES[shape.props.size] + 1) * shape.props.scale
}

// tldraw's DrawShapeSvg as it runs for an export (at zoom 1, so never forced
// solid), with `freehand` in place of its options
function LooseDrawSvg({ shape }) {
  const theme = useDefaultColorTheme()
  const points = getPointsFromSegments(shape.props.segments)
  const complete = shape.props.isComplete || last(shape.props.segments)?.type === 'straight'
  const width = strokeWidth(shape)
  const options = freehand(shape.props, width, complete, false)
  if (shape.props.dash === 'draw') {
    return (
      <>
        {shape.props.isClosed && shape.props.fill && points.length > 1 ? (
          <ShapeFill
            d={getSvgPathFromStrokePoints(getStrokePoints(points, options), shape.props.isClosed)}
            theme={theme}
            color={shape.props.color}
            fill={shape.props.isClosed ? shape.props.fill : 'none'}
            scale={shape.props.scale}
          />
        ) : null}
        <path d={svgInk(points, options)} strokeLinecap="round" fill={theme[shape.props.color].solid} />
      </>
    )
  }
  const strokePoints = getStrokePoints(points, options)
  const dot = strokePoints.length < 2
  const outline = dot
    ? `M ${points[0].x} ${points[0].y} m -0.5, 0 a 0.5,0.5 0 1,0 1,0 a 0.5,0.5 0 1,0 -1,0`
    : getSvgPathFromStrokePoints(strokePoints, shape.props.isClosed)
  const dashes = { draw: 'none', solid: 'none', dotted: `0.1 ${width * 2}`, dashed: `${width * 2} ${width * 2}` }
  return (
    <>
      <ShapeFill
        d={outline}
        theme={theme}
        color={shape.props.color}
        fill={dot || shape.props.isClosed ? shape.props.fill : 'none'}
        scale={shape.props.scale}
      />
      <path
        d={outline}
        strokeLinecap="round"
        fill={dot ? theme[shape.props.color].solid : 'none'}
        stroke={theme[shape.props.color].solid}
        strokeWidth={width}
        strokeDasharray={dot ? 'none' : dashes[shape.props.dash]}
        strokeDashoffset="0"
      />
    </>
  )
}

class LooseDrawShapeUtil extends DrawShapeUtil {
  getGeometry(shape) {
    const points = getPointsFromSegments(shape.props.segments)
    const width = strokeWidth(shape)
    if (shape.props.segments.length === 1) {
      const box = Box.FromPoints(points)
      if (box.width < width * 2 && box.height < width * 2) {
        return new Circle2d({ x: -width, y: -width, radius: width, isFilled: true })
      }
    }
    const outline = getStrokePoints(points, freehand(shape.props, width, shape.props.isPen, true))
      .map((point) => point.point)
    if (shape.props.isClosed && outline.length > 2) {
      return new Polygon2d({ points: outline, isFilled: shape.props.fill !== 'none' })
    }
    if (outline.length === 1) {
      return new Circle2d({ x: -width, y: -width, radius: width, isFilled: true })
    }
    return new Polyline2d({ points: outline })
  }

  component(shape) {
    return (
      <SVGContainer>
        <LooseDrawSvg shape={shape} />
      </SVGContainer>
    )
  }

  toSvg(shape, ctx) {
    ctx.addExportDef(getFillDefForExport(shape.props.fill))
    return (
      <g transform={`scale(${1 / shape.props.scale})`}>
        <LooseDrawSvg shape={shape} />
      </g>
    )
  }
}

// Move every shape of a stage by (dx, dy) page units for one export, in place,
// so its order in the stack is kept: a flat moved off its line still sits under
// the ink it sat under. Gives back the undo.
function offset(editor, shifts) {
  const moved = []
  for (const { stage, dx, dy } of shifts ?? []) {
    for (const shape of byStage(editor, stage)) {
      moved.push({ id: shape.id, type: shape.type, x: shape.x, y: shape.y })
      editor.updateShapes([{ id: shape.id, type: shape.type, x: shape.x + dx, y: shape.y + dy }])
    }
  }
  return () => editor.updateShapes(moved)
}

const SHAPE_UTILS = STREAMLINE === null ? [] : [LooseDrawShapeUtil]

function App() {
  return (
    <Tldraw
      shapeUtils={SHAPE_UTILS}
      onMount={(editor) => {
        window.editor = editor
        const exportShapes = async (options) => {
          // Hiding a stage renders the rest of the drawing without it. The
          // load-bearing case is the line-off test: if the flats alone no
          // longer separate foreground from background, the colour design has
          // failed and no amount of rendering will rescue it.
          const hide = new Set(options.hide ?? [])
          // `only` is the complement: keep these and nothing else.
          //
          // Both filters match a mark's STAGE (when in the stages it was made)
          // or its TAG (which object it belongs to), because a name is looked
          // up in both sets. The two axes are independent, so one flag covers
          // "just the ink", "just the bicycle", and "the bicycle over the
          // composition rough" -- the last being a view of one object worked
          // in place, which is what a detail pass on a scene needs.
          const named = (shape) => [shape.meta?.stage, shape.meta?.tag]
            .filter((name) => name)
          const only = new Set(options.only ?? [])
          const all = editor.getCurrentPageShapes()
          const shapes = all
            .filter((shape) => only.size === 0 || named(shape).some((name) => only.has(name)))
            .filter((shape) => !named(shape).some((name) => hide.has(name)))
            .map((shape) => shape.id)
          if (shapes.length === 0) return null
          const scale = options.scale ?? 1
          const padding = options.padding ?? 32
          // With the frame as the picture's edge, export exactly its bounds
          // and leave the frame itself out: drawn, its stroke took the colour
          // its stock name was repointed to, and a palette that spent that
          // name on a dark flat framed every render in a 3px line
          const frame = all.find((shape) => shape.meta?.stage === 'frame')
          const held = frame && editor.getShapePageBounds(frame)
          if (held && padding === 0 && !options.crop) {
            const drawn = shapes.filter((id) => id !== frame.id)
            if (drawn.length === 0) return null
            const { blob } = await editor.toImage(drawn, {
              format: 'png',
              background: true,
              scale,
              padding: 0,
              darkMode: false,
              bounds: held,
              pixelRatio: 2,
            })
            const ratio = 2 * scale
            const size = [Math.round(held.w * ratio), Math.round(held.h * ratio)]
            return encode(await redraw(blob, { ...options, size }))
          }
          const { blob } = await editor.toImage(shapes, {
            format: 'png',
            background: true,
            scale,
            padding,
            darkMode: false,
          })
          // The frame is what the picture is; anything drawn past it is
          // overrun, and a contour is *supposed* to overrun where it leaves
          // the picture, so that the flat trapped under it stays covered
          // right to the edge. But the export takes the union of every shape,
          // so a single overrunning stroke drags the border out and leaves a
          // margin of bare paper the drawing never reaches. Clip to the frame
          // and the overruns fall off the edge, which is where they were
          // aimed.
          const edge = all.find((shape) => shape.meta?.stage === 'frame')
          let crop = options.crop
          let pageWidth = null
          if (edge && !crop && padding === 0) {
            const held = editor.getShapePageBounds(edge)
            const spread = Box.Common(
              shapes.map((id) => editor.getShapePageBounds(id)).filter(Boolean)
            )
            if (held && spread) {
              crop = [held.x - spread.x, held.y - spread.y, held.w, held.h]
              pageWidth = spread.w
            }
          }
          return encode(await redraw(blob, { ...options, crop, pageWidth }))
        }
        window.canvas = {
          apply: (ops) => apply(editor, ops),
          repaint,
          load: (snapshot) => loadSnapshot(editor.store, snapshot),
          save: () => getSnapshot(editor.store),
          shapeCounts: () =>
            editor.getCurrentPageShapes().reduce((tally, shape) => {
              const stage = shape.meta?.stage ?? 'unstaged'
              tally[stage] = (tally[stage] ?? 0) + 1
              return tally
            }, {}),
          shot: async (options = {}) => {
            const undo = offset(editor, options.offset)
            try {
              return await exportShapes(options)
            } finally {
              undo()
            }
          },
        }
        window.canvasReady = true
      }}
    />
  )
}

createRoot(document.getElementById('root')).render(<App />)
