# Light, value, edges, and how line alone carries volume


## Contents

- The anatomy of light on form
- Separation of the families
- Plane-based shading
- Cross-contour: the main technique for line
- How line alone describes form
- Edges
- The primitives, and what each teaches
## The anatomy of light on form

Lightest to darkest, on a 10-step scale:

| Zone | Value | Rule |
|---|---|---|
| **Highlight** | — | A reflection *of the source*. Only on shiny surfaces. It moves when the **viewer** moves |
| **Centre light** | 9–10 | The plane facing the source most directly. Fixed by geometry whatever the viewer does, which is how you tell it from the highlight |
| **Halftones** | 4–9 | Planes partly facing the light, lighter the more they face it. Most of the lit area, and most of the work |
| **Terminator** | — | Not a value: the *boundary* where a surface stops facing the light |
| **Core shadow** | 1–2 | The darkest part of the form shadow, just past the terminator, where the least bounced light reaches |
| **Reflected light** | ~4 | Light bounced back into the shadow, in the colour of what it bounced off |
| **Occlusion / contact** | 0 | Where surfaces meet and *all* light is blocked. **The darkest note in the picture**, darker than the core shadow |
| **Cast shadow** | 2–3 | A separate shape over other surfaces, not part of the form shadow |

**Reflected light must never be as light as *any* halftone.** Overstating it is
the most commonly cited failure: the two families merge and the form flattens.

**Cast shadow edges** are hard from a point source and soft from a diffuse one,
and sharp where the shadow meets the object casting it, softening with distance.

**Model one family and keep the other flat.** Rendering both fully looks fussy.

**Under diffuse light** there is no terminator and no core shadow. Planes facing
up go lighter, planes facing down darker, and occlusion shadows are the only
sharp accents.

## Separation of the families

**The lightest value in shadow must be darker than the darkest value in light.
The two families never overlap.** This is the most important rule in rendering.

Work it as **notan** (a two-value study): before any halftone, reduce everything
to one pale value for all that is lit and one dark value for all that is in
shadow. Fill the whole shadow shape at a single value (~3) *before* separating
core shadow, reflected light and occlusion inside it. If that two-value pattern
does not read when squinted at or shrunk, no detail inside it will fix it.

**Finding the terminator:** on a simple solid it is a clean line or ellipse. On an organic form it is **not one
smooth curve**: it bends with each local plane, for example around a brow ridge,
a muscle or a fold. Work it out plane by plane.

You decide where it falls, before committing: moving the light toward the
viewer enlarges the lit side, and moving it behind does the reverse.

**Plan the edges before filling values.** There are three families: terminator
and core-shadow edges (soft or hard depending on curvature), cast-shadow edges
(usually sharper), and silhouette edges (sharp unless deliberately lost).

## Plane-based shading

Value follows **which way a plane faces, not its distance from the light**.

Give **each plane one flat value** from its angle to the light before attempting
any transition, and start with boxes, where each face is one flat value with a
hard jump to the next.

Working flat first lets you *choose* the edge at each transition: hard at a box
corner, soft where a sphere rounds. A gradient applied everywhere erases those
decisions, and the object reads as mush instead of an assembly of surfaces.

Separate lights from darks, then split the midtones. Never start from a blend.

## Cross-contour: the main technique for line

A contour describes a form's outer silhouette. A **cross-contour** describes the
*surface*, running across the form like a contour line on a map. In a drawing
made only of line, it is the main way to show volume.

- **The stroke curves as the surface curves**: straight on a flat surface,
  curved on a round one. The more curved the stroke, the rounder the form reads.
- **Spacing shows how fast the surface turns.** Tightly clustered lines mean it
  is turning away fast; wide, even spacing means a flat or gently curving area.
- **Arcs tighten toward the silhouette.** A cross-contour is shallow across the
  part facing the viewer and steepens near the outer edge, where foreshortening
  speeds up. Its curvature changes along the stroke.
- Use **parallel** cross-contours on forms curving around one axis (limbs,
  branches, cylinders) and **two crossing sets**, like latitude and longitude, on
  forms curving both ways (a sphere, a skull).
- **Anchor them to structure** (a ridge, a muscle boundary, a plane change), not
  to a uniform grid.
- Draw them **after** the block-in and **before** rendering, as a check on the
  volume, not a decorative finish. There is no numeric spacing system; place
  them by the rules above.

## How line alone describes form

- **Weight shows light**: heavier on the side away from the light, and thin,
  broken or absent where the light hits hardest.
- **Weight shows depth**: thicker on the edges nearest the viewer, lighter as a
  contour recedes.
- **Weight shows contact**: heaviest where two forms touch or overlap, as the
  occlusion shadow is the darkest note.
- **Weight shows mass**: taper a stroke along its length to suggest a bulge,
  whatever the light.
- **Lost and found**: draw, leave a gap, resume. Drawn segments read as a hard
  edge and gaps as a soft one. **Without value, this is the only way to soften an
  edge.** Use it where a surface rounds away, goes out of focus or fades into
  shadow.

**Never draw a uniform, unbroken outline.** Every source names it as the main
cause of a flat-looking drawing: a contour stated all the way round every form
leaves no sense of space.

Picture the volume before making the mark. The contour comes from forms
overlapping in the round, not from tracing a silhouette.

## Edges

Four kinds, each with a physical cause:

- **Sharp**: a sudden plane change. Keep it for the focal point.
- **Firm**: a rounded corner with a slight blur.
- **Soft**: a large, gently rounding form.
- **Lost**: a boundary that vanishes because the values match or it is blurred.

Hard edges come forward and catch the eye; soft edges recede.

**Put the one hardest edge at the focal point** and grade every other edge
against it, on a continuous scale from hard through soft to lost. Soften any
edge that does not need to be sharp, but not all by the same amount.

**Deliberately lose two or three edges per form** where similar values meet.
This merges small neighbouring shapes into one, lets the eye travel through the
areas outside the focus, and keeps contrast where it belongs. Hard edges
everywhere come from thinking in line instead of form, and look like a colouring
book.

## The primitives, and what each teaches

- **Box**: one value per plane, no curvature, hard edges only, no terminator.
  Learn this first.
- **Cylinder**: curvature around one axis. The terminator runs **straight and
  parallel to the axis**, curving only around the cross-section. This carries
  over to limbs, fingers, stems and pipes.
- **Sphere**: curvature in every direction. The terminator curves on two axes,
  and **the value steps bunch up near it**: values change slowly near the
  brightest light and darken fast toward the terminator. Do not space the steps
  evenly across the lit side.
- **Cone**: a straight terminator along the axis, like the cylinder's, converging
  and sharpening toward the tip.

**The terminator and the core shadow are different things.** The main light
fixes the terminator. The core shadow sits a little past it, where the surface
gets the least direct and bounced light *combined*, so it moves when the
reflected light moves, even if the terminator does not.
