#!/usr/bin/env python3
"""Render the drawing's marks as a medium would lay them, from ops.json.

    python3 brush.py --ops ops.json --style style.json [--palette palette.json] \\
                     --out brush.png [--hide STAGE,...] [--offset fill:dx,dy]

tldraw draws every mark as a clean vector: even width, a perfect edge, flat
colour. This draws the same marks again as a raster, by stamping dabs along
each stroke's own points, so that a line has the weight the pressure gave it
and an edge the paper gave it. For the flats it lays brush passes inside the
flat's own outline. finish.py then puts the paper and the scan on it, when
style.json says `"renderer": "brush"`.

What it never does: add a mark. Every pixel it paints sits inside the
footprint of a stroke in ops.json (its points, its width from size, scale and
pressure, and a pixel or two of edge). There is no hatching, no restated line
and no new shape. Texture is how the paint lands, never a new mark. The stack
is the one ops.json makes: strokes in the order written, `back` sends a stage
under the rest, `fade` sets its opacity, `erase` takes it away. So a near flat
written after a far line still covers it.

Coordinates are those of the harness render with `--padding 0`: the frame's
bounds are the picture's edges, at two pixels per page unit. brush.png is the
size drawing.png is. By default the stages drawing.png hides (gesture,
construction, block-in, contour) are hidden here as well.

Per medium, a line is laid with:

    ink-pen    a sharp nib: ink pools where the pen slows (starts, corners),
               the line swells a little on a pull toward the hand, and the
               ink feathers a hair into the paper's fibres
    brush-pen  a loaded brush: the bristles split and the line breaks into
               dry brush on a fast tail, and the ink runs low on a long stroke
    pencil     graphite: darkness from pressure, caught on the paper's tooth
    marker     felt: multiplied, so overlaps darken, with streaks along the
               stroke and a bleed where it touches down
    gouache    opaque, matte paint with the brush's streaks along it
    watercolour+ink  a brush-pen line over colour laid with a brush

and a flat is laid as side-by-side brush passes: one cut along the flat's
outline, the middle filled along the flat's long axis (or the hand's slant on
a round flat), each pass with its own load of paint, bristle streaks along
its direction and a ridge where it overlaps the last.

Everything random comes from the style's `seed`. It uses numpy, scipy and PIL.
The gates never read brush.png; they judge drawing.png.
"""
import argparse
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import cKDTree

import finish

RATIO = 2                     # render pixels per page unit at the harness's --scale 1
STROKE_SIZES = {"s": 2.0, "m": 3.5, "l": 5.0, "xl": 10.0}
DRAWING_HIDES = ("gesture", "construction", "blockin", "contour")
RENDERERS = ("tldraw", "brush")

# the harness's STAGE_LOOK: what a stroke that names no look takes from its stage
STAGE_LOOK = {
    "gesture": dict(color="blue", size="m", dash="draw", opacity=0.85),
    "construction": dict(color="grey", size="s", dash="draw", opacity=0.6),
    "blockin": dict(color="violet", size="s", dash="solid", opacity=0.9),
    "contour": dict(color="black", size="s", dash="draw", opacity=0.9),
    "ink": dict(color="black", size="m", dash="draw", opacity=1.0),
    "fill": dict(color="orange", size="s", dash="draw", opacity=1.0),
    "mend": dict(color="orange", size="s", dash="solid", opacity=1.0),
    "correct": dict(color="white", size="s", dash="draw", opacity=1.0),
    "frame": dict(color="grey", size="s", dash="solid", opacity=0.03),
}

# tldraw 3.15's light theme, as shipped: a stock name's `solid` (the line),
# `semi` (fill="solid") and `fill` (fill="fill")
STOCK = {
    "black": ("#1d1d1d", "#e8e8e8", "#1d1d1d"),
    "grey": ("#9fa8b2", "#eceef0", "#9fa8b2"),
    "light-violet": ("#e085f4", "#f5eafa", "#e085f4"),
    "violet": ("#ae3ec9", "#ecdcf2", "#ae3ec9"),
    "blue": ("#4465e9", "#dce1f8", "#4465e9"),
    "light-blue": ("#4ba1f1", "#ddedfa", "#4ba1f1"),
    "yellow": ("#f1ac4b", "#f9f0e6", "#f1ac4b"),
    "orange": ("#e16919", "#f8e2d4", "#e16919"),
    "green": ("#099268", "#d3e9e3", "#099268"),
    "light-green": ("#4cb05e", "#dbf0e0", "#4cb05e"),
    "light-red": ("#f87777", "#f4dadb", "#f87777"),
    "red": ("#e03131", "#f4dadb", "#e03131"),
    "white": ("#FFFFFF", "#f5f5f5", "#FFFFFF"),
}
STOCK_BACKGROUND = "#f9fafb"
SEMI_FILL = "#fcfffe"         # fill="semi" is the theme's own near-white

# How each medium lays a line. Lengths are render pixels.
#   edge     -- how far (px) the edge wanders in or out, slowly and on the grain
#   feather  -- how strongly ink wicks a hair out along the paper's fibres
#   pool     -- how much a slow point (a start, a corner) widens and darkens the line
#   swell    -- how much a pull toward the hand (downward) widens a nib line
#   spacing  -- dab spacing as a share of the radius, slow and fast
#   dry      -- how readily a fast tail breaks into dry brush
#   streak   -- strength of the bristle streaks along the stroke
#   alpha    -- how much of the ground the mark hides at full coverage
#   mode     -- over (opaque) or multiply (translucent, overlaps darken)
LINES = {
    "nib": dict(edge=(0.4, 0.12), feather=0.18, pool=0.22, swell=0.22, spacing=(0.08, 0.16),
                dry=0.0, streak=0.0, alpha=0.98, mode="over"),
    "brush-pen": dict(edge=(0.6, 0.2), feather=0.1, pool=0.12, swell=0.0, spacing=(0.1, 0.3),
                      dry=1.0, streak=0.0, alpha=0.97, mode="over"),
    "graphite": dict(edge=(0.35, 0.35), feather=0.0, pool=0.05, swell=0.0, spacing=(0.15, 0.35),
                     dry=0.0, streak=0.0, alpha=1.0, mode="multiply"),
    "marker": dict(edge=(0.35, 0.1), feather=0.2, pool=0.2, swell=0.0, spacing=(0.1, 0.3),
                   dry=0.0, streak=0.10, alpha=0.82, mode="multiply"),
    "paint": dict(edge=(0.5, 0.15), feather=0.0, pool=0.1, swell=0.0, spacing=(0.1, 0.3),
                  dry=0.45, streak=0.06, alpha=1.0, mode="over"),
}
# How each medium lays a flat (and a colour line, a fill-stage stroke).
#   load    -- how much one pass's paint differs from the next
#   streak  -- strength of the bristle streaks along a pass
#   ridge   -- darkening where a pass overlaps the one before
#   edge    -- how far the brush's edge wanders off the outline
#   alpha   -- opacity; mode as for lines
FLATS = {
    "paint": dict(load=0.035, streak=0.07, ridge=0.035, edge=1.1, alpha=1.0, mode="over"),
    "colour": dict(load=0.025, streak=0.045, ridge=0.025, edge=0.9, alpha=1.0, mode="over"),
    "marker": dict(load=0.05, streak=0.07, ridge=0.18, edge=0.6, alpha=0.88, mode="multiply"),
    "pencil": dict(load=0.04, streak=0.12, ridge=0.05, edge=0.7, alpha=0.9, mode="multiply"),
}
# medium -> (instrument for ink and correction lines, instrument for colour)
MEDIA = {
    "ink-pen": ("nib", "colour"),
    "brush-pen": ("brush-pen", "colour"),
    "pencil": ("graphite", "pencil"),
    "marker": ("marker", "marker"),
    "watercolour+ink": ("brush-pen", "colour"),
    "gouache": ("paint", "paint"),
}
LINE_STAGES = ("ink", "contour", "correct", "gesture", "blockin", "construction")
COLOUR_LINE = {"paint": "paint", "colour": "paint", "marker": "marker", "pencil": "graphite"}


def fail(message):
    raise SystemExit(f"brush: {message}")


def hex_rgb(value):
    digits = value.lstrip("#")
    return np.array([int(digits[at:at + 2], 16) for at in (0, 2, 4)], dtype=float) / 255.0


# --- the stack ------------------------------------------------------------------

def stack(ops):
    """The strokes in paint order, after every fade, erase and back, as the harness
    applies them. Each is the op with its stage and opacity filled in."""
    shapes = []
    for at, op in enumerate(ops):
        kind = op.get("op")
        stage = op.get("stage", "ink")
        if kind == "stroke":
            if len(op.get("points", [])) < 2:
                continue   # the harness makes no shape of a single point
            look = STAGE_LOOK.get(stage, STAGE_LOOK["ink"])
            shapes.append(dict(op, stage=stage, opacity=op.get("opacity", look["opacity"]), index=at))
        elif kind == "fade":
            for shape in shapes:
                if shape["stage"] == op["stage"]:
                    shape["opacity"] = op.get("opacity", 0.12)
        elif kind == "erase":
            if "ids" in op:
                fail(f"op {at}: an erase by tldraw shape ids cannot be replayed from ops.json")
            shapes = [shape for shape in shapes if shape["stage"] != op["stage"]]
        elif kind == "back":
            moved = [shape for shape in shapes if shape["stage"] == op.get("stage", "fill")]
            shapes = moved + [shape for shape in shapes if shape["stage"] != op.get("stage", "fill")]
        elif kind == "clear":
            shapes = []
        else:
            fail(f"op {at}: unknown op {kind!r}")
    return shapes


def frame_bounds(shapes):
    frames = [shape for shape in shapes if shape["stage"] == "frame"]
    if not frames:
        fail("ops.json has no frame stroke (pen.frame), so there is no picture edge to render to")
    points = np.asarray([point[:2] for point in frames[0]["points"]], dtype=float)
    return points.min(axis=0), points.max(axis=0)


def colours(palette, stock_only=False):
    """name -> (line, fill="solid", fill="fill") as RGB, and the ground."""
    table = {name: tuple(hex_rgb(value) for value in values) for name, values in STOCK.items()}
    ground = hex_rgb(STOCK_BACKGROUND)
    for name, value in (palette or {}).items():
        if name == "background":
            if not stock_only:
                ground = hex_rgb(value)
        elif name in STOCK and stock_only:
            continue
        else:
            table[name] = (hex_rgb(value),) * 3
    return table, ground


# --- the paper the marks land on -------------------------------------------------

class Paper:
    """Fields shared by every mark, because they belong to the sheet: where its
    grain pushes an edge in or out, its fibres, its tooth, and a bristle texture."""

    def __init__(self, rng, shape, ratio):
        self.shape = shape
        # the sheet's features have a size on paper, so in pixels they scale with
        # the render; `reach` scales an edge's wander the same way
        self.reach = math.sqrt(ratio / RATIO)
        # an edge wanders slowly (the hand, the ink's spread) and catches a
        # little on the paper's grain; the first moves it far more than the second
        self.sway = finish.noise(rng, shape, 9.0 * ratio)
        self.wander = finish.noise(rng, shape, 2.5 * ratio)
        self.grain = finish.noise(rng, shape, max(0.45 * ratio, 0.5))
        self.fibres = finish.fibre_field(rng, shape, 900, length=(5, 14))
        self.tooth = finish.tooth_field(rng, shape, 1.1)
        bristles = finish.noise(rng, (256, 512), 0.9)
        self.bristles = bristles / (np.abs(bristles).max() + 1e-12)   # -1..1, wraps
        self.warp = finish.noise(rng, (128, 128), 6.0)

    def sample(self, field, rows, cols):
        return ndimage.map_coordinates(field, [rows, cols], order=1, mode="grid-wrap")


# --- lines -----------------------------------------------------------------------

STREAMLINE = 0.62            # tldraw's own; build.sh lowers it for the finished look


def streamlined(raw, streamline):
    """The points as tldraw's freehand lays them: a start of near-zero pressure
    dropped, and each point pulled toward the one before by `streamline`, which
    cuts a curve's bulge and pulls a ring a little in. The last point is kept."""
    points = np.asarray(raw, dtype=float)
    if points.shape[1] < 3:
        points = np.hstack([points, np.full((len(points), 1), 0.5)])
    start = int(np.argmax(points[:, 2] >= 0.025)) if (points[:, 2] >= 0.025).any() else 0
    above = np.nonzero(points[:, 2] >= 0.01)[0]
    end = int(above[-1]) + 1 if len(above) else len(points)
    points = points[start:max(end, start + 1)]
    pull = 0.15 + (1 - streamline) * 0.85
    laid = points.copy()
    for at in range(1, len(points) - 1):
        laid[at, :2] = laid[at - 1, :2] + (points[at, :2] - laid[at - 1, :2]) * pull
    return laid


def pen_easing(t):
    return t * 0.65 + np.sin(t * np.pi / 2) * 0.35


def radius_px(op, pressure, ratio):
    """The radius tldraw gives this stroke at each pressure, in render pixels."""
    look = STAGE_LOOK.get(op["stage"], STAGE_LOOK["ink"])
    width = (STROKE_SIZES[op.get("size", look["size"])] + 1) * float(op.get("scale", 1.0))
    if op.get("dash", look["dash"]) == "draw":
        return ratio * (1 + 1.2 * width) * pen_easing(0.5 - 0.62 * (0.5 - np.asarray(pressure)))
    return np.full(len(pressure), ratio * width / 2)


def dynamics(xy):
    """Per point: arclength, unit tangent, and speed 0 (stopped) .. 1 (fast).
    pen.py lays a fixed count of points per span, so a long sweep between two
    decisions has wide spacing (the hand moving fast) and a corner has tight
    spacing and a sharp turn (the hand slowing)."""
    step = np.linalg.norm(np.diff(xy, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(step)])
    ahead = np.diff(xy, axis=0) / np.maximum(step, 1e-9)[:, None]
    tangent = np.vstack([ahead[:1], (ahead[:-1] + ahead[1:]) / 2, ahead[-1:]])
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1), 1e-9)[:, None]
    spacing = np.concatenate([step[:1], (step[:-1] + step[1:]) / 2, step[-1:]])
    moving = step[step > 1e-6]
    typical = np.median(moving) if len(moving) else 1.0
    turn = np.zeros(len(xy))
    if len(ahead) > 1:
        cross = ahead[:-1, 0] * ahead[1:, 1] - ahead[:-1, 1] * ahead[1:, 0]
        dot = (ahead[:-1] * ahead[1:]).sum(axis=1)
        turn[1:-1] = np.abs(np.arctan2(cross, dot)) / np.maximum(spacing[1:-1], 1e-6)
    speed = np.clip(spacing / (1.4 * typical), 0.2, 1.0) / (1 + 14.0 * along_arc(turn, arc, 3.0))
    # a hand's speed changes over a stretch of the line, not point to point: read
    # point by point, pen.py's even count per span would swell the line at every
    # one of its control points, like beads on a string
    return arc, tangent, along_arc(speed, arc, 18.0)


def along_arc(values, arc, sigma):
    """`values` smoothed over `sigma` px of arclength, whatever the point spacing."""
    if arc[-1] < 2:
        return values
    even = np.arange(0, arc[-1] + 1.0, 1.0)
    smooth = ndimage.gaussian_filter1d(np.interp(even, arc, values), sigma, mode="nearest")
    return np.interp(arc, even, smooth)


def dabs(op, offset, instrument, rng, ratio, streamline):
    """Where each dab of this stroke lands: centre, radius, arclength, speed,
    pressure and tangent, in render pixels. The spacing opens up with speed."""
    raw = streamlined(op["points"], streamline)
    xy = (raw[:, :2] - offset) * ratio
    pressure = raw[:, 2]
    if op.get("closed"):
        xy = np.vstack([xy, xy[:1]])
        pressure = np.concatenate([pressure, pressure[:1]])
    keep = np.concatenate([[True], np.linalg.norm(np.diff(xy, axis=0), axis=1) > 1e-6])
    xy, pressure = xy[keep], pressure[keep]
    if len(xy) > 1:
        # tldraw's streamline smooths the pressure along with the points; without
        # it, pen.py's per-point pressure beads the line at each control point
        pressure = along_arc(pressure, np.concatenate([[0.0], np.cumsum(
            np.linalg.norm(np.diff(xy, axis=0), axis=1))]), 4.0 * ratio)
    radius = radius_px(op, pressure, ratio)
    if len(xy) == 1:
        return xy, radius, np.zeros(1), np.full(1, 0.5), pressure, np.array([[1.0, 0.0]])
    arc, tangent, speed = dynamics(xy)
    spec = LINES[instrument]
    # the instrument's response to the hand, kept near 1 on average so the line
    # stays as heavy as the one tldraw draws (and the gates judged)
    slow = (1 - speed) ** 2
    factor = 1 + spec["pool"] * (slow - slow.mean())
    if spec["swell"]:
        down = np.clip(tangent[:, 1], 0, 1)
        factor *= 1 + spec["swell"] * (down - down.mean())
    if not op.get("closed"):
        # ink pools where the point touches down, more when slow, and where it
        # stops still pressed; a tail that lifts away leaves no pool
        ends = np.exp(-arc / (2.5 * radius)) * (1 - speed[0]) + \
            np.exp(-(arc[-1] - arc) / (2.5 * radius)) * (1 - speed[-1]) * np.clip(pressure[-1] - 0.3, 0, 1)
        factor *= 1 + spec["pool"] * 0.8 * ends
    radius = radius * factor
    # walk the path in steps that widen with speed
    low, high = spec["spacing"]
    where, at = [], 0.0
    while at < arc[-1]:
        where.append(at)
        here_r = np.interp(at, arc, radius)
        here_v = np.interp(at, arc, speed)
        at += max(0.35, (low + (high - low) * here_v) * here_r)
    where.append(arc[-1])
    where = np.asarray(where)
    centre = np.stack([np.interp(where, arc, xy[:, 0]), np.interp(where, arc, xy[:, 1])], axis=1)
    if instrument in ("graphite", "brush-pen", "paint"):
        # a hand-held point never sits exactly on the path: a little jitter, under a pixel
        centre += rng.normal(0, 0.18, centre.shape)
    tangents = np.stack([np.interp(where, arc, tangent[:, 0]), np.interp(where, arc, tangent[:, 1])], axis=1)
    tangents /= np.maximum(np.linalg.norm(tangents, axis=1), 1e-9)[:, None]
    return (centre, np.interp(where, arc, radius), where, np.interp(where, arc, speed),
            np.interp(where, arc, pressure), tangents)


def stamp(centre, radius, arc, speed, pressure, tangent, shape, reach):
    """Lay the dabs. Returns the box, and per pixel of it: how far inside the
    union of dabs it is (px, negative outside), and the arclength, speed,
    pressure, radius and position across the stroke (-1..1) of the dab whose
    edge is farthest from it, which is the dab that laid that pixel."""
    height, width = shape
    pad = reach + 2
    x0 = max(int(np.floor((centre[:, 0] - radius).min() - pad)), 0)
    y0 = max(int(np.floor((centre[:, 1] - radius).min() - pad)), 0)
    x1 = min(int(np.ceil((centre[:, 0] + radius).max() + pad)) + 1, width)
    y1 = min(int(np.ceil((centre[:, 1] + radius).max() + pad)) + 1, height)
    if x1 <= x0 or y1 <= y0:
        return None
    box = (y0, y1, x0, x1)
    depth = np.full((y1 - y0, x1 - x0), -1e9)
    fields = {name: np.zeros_like(depth) for name in ("arc", "speed", "pressure", "radius", "across")}
    for (cx, cy), r, s, v, p, (tx, ty) in zip(centre, radius, arc, speed, pressure, tangent):
        reach_here = r + pad
        a0, a1 = max(int(cx - reach_here), x0), min(int(cx + reach_here) + 2, x1)
        b0, b1 = max(int(cy - reach_here), y0), min(int(cy + reach_here) + 2, y1)
        if a1 <= a0 or b1 <= b0:
            continue
        dx = np.arange(a0, a1) + 0.5 - cx
        dy = (np.arange(b0, b1) + 0.5 - cy)[:, None]
        inside = r - np.sqrt(dx ** 2 + dy ** 2)
        patch = (slice(b0 - y0, b1 - y0), slice(a0 - x0, a1 - x0))
        wins = inside > depth[patch]
        depth[patch][wins] = inside[wins]
        fields["arc"][patch][wins] = s
        fields["speed"][patch][wins] = v
        fields["pressure"][patch][wins] = p
        fields["radius"][patch][wins] = r
        fields["across"][patch][wins] = np.broadcast_to((dx * -ty + dy * tx) / max(r, 0.5), inside.shape)[wins]
    return box, depth, fields


def coverage(depth, wobble):
    """0..1 per pixel from the distance inside the edge, with a one-pixel ramp."""
    return np.clip(depth + wobble + 0.5, 0, 1)


def lay_line(canvas, paper, op, colour, instrument, offset, rng, ratio, streamline):
    spec = LINES[instrument]
    laid = dabs(op, offset, instrument, rng, ratio, streamline)
    centre, radius, arc, speed, pressure, tangent = laid
    result = stamp(centre, radius, arc, speed, pressure, tangent, canvas.shape[:2], reach=4)
    if result is None:
        return
    box, depth, fields = result
    y0, y1, x0, x1 = box
    slow_edge, grain_edge = spec["edge"]
    fibres = paper.fibres[y0:y1, x0:x1]
    # a hairline cannot lose more of its width to the grain than it has
    thin = paper.reach * np.clip(fields["radius"] / (1.5 * ratio + 1.5), 0.25, 1.0)
    length = max(float(arc[-1]), 1.0)
    along = fields["arc"] / length
    wobble = thin * (slow_edge * (0.85 * paper.sway[y0:y1, x0:x1] + 0.35 * paper.wander[y0:y1, x0:x1])
                     + grain_edge * paper.grain[y0:y1, x0:x1])
    alpha = None
    if spec["dry"]:
        # dry brush: a fast tail runs out of ink first, and so does a long
        # stroke. The bristles part, each carrying its own load
        tail = np.clip((along - 0.55) / 0.45, 0, 1) ** 1.5
        fast = np.clip((fields["speed"] - 0.35) / 0.45, 0, 1)
        lift = np.clip((0.75 - fields["pressure"]) / 0.5, 0, 1)
        dryness = spec["dry"] * (0.9 * tail * fast * (0.5 + 0.5 * lift)
                                 + 0.25 * np.clip((fields["arc"] - 900) / 2500, 0, 1))
        count = np.clip(fields["radius"] / 1.4, 3, 28)
        lane = (fields["across"] + 1) * 0.5 * count
        row0, col0 = rng.uniform(0, 256), rng.uniform(0, 512)
        # each bristle's load changes slowly along the stroke, so a gap is a long
        # streak in the stroke's direction, never a notch across it
        load = paper.sample(paper.bristles, row0 + lane * 3.1, col0 + fields["arc"] / 90.0)
        streak = paper.sample(paper.bristles, row0 + 90 + lane * 4.0, col0 + fields["arc"] / 30.0)
        bristle = 0.65 * load + 0.35 * streak            # -1..1-ish
        # the lanes near the edge of a brush dry first
        bristle -= 0.35 * np.abs(fields["across"]) ** 3
        gap = np.clip((bristle + 1.0 - 2.2 * dryness) / 0.25, 0, 1)
        gap = np.where(dryness > 0.02, gap, 1.0)
        wobble = wobble + 0.4 * dryness * paper.grain[y0:y1, x0:x1]
        alpha = coverage(depth, wobble) * gap
    if alpha is None:
        alpha = coverage(depth, wobble)
    if spec["feather"]:
        # ink wicks a hair out along the paper's fibres just past the edge
        near = np.clip(1 + depth / 1.4, 0, 1) * (depth < 0.5)
        alpha = np.maximum(alpha, spec["feather"] * near * np.clip(fibres * 2.5, 0, 1))
    tone = np.broadcast_to(colour, alpha.shape + (3,)).copy()
    if instrument == "nib":
        # a pool is a little denser and darker than the line it sits in
        pool = np.clip((1 - fields["speed"]) - 0.4, 0, 1)
        tone = tone * (1 - 0.25 * pool[..., None] * (1 - tone))
        alpha = alpha * (0.97 + 0.03 * np.clip(pool * 3, 0, 1))
    elif instrument == "graphite":
        dark = finish.luminance(np.asarray(colour)[None, None])[0, 0] < 0.35
        if dark:
            tone[:] = finish.GRAPHITE
        tooth = paper.tooth[y0:y1, x0:x1]
        press = fields["pressure"]
        caught = np.clip((tooth - (0.78 - 0.65 * press)) / 0.3, 0.06, 1.0)
        alpha = alpha * (0.3 + 0.65 * press) * caught
    elif instrument in ("marker", "paint"):
        row0, col0 = rng.uniform(0, 256), rng.uniform(0, 512)
        streak = paper.sample(paper.bristles, row0 + fields["across"] * 9.0, col0 + fields["arc"] / 40.0)
        if instrument == "marker":
            alpha = alpha * np.clip(1 - spec["streak"] * (0.5 + streak), 0.5, 1)
            # the felt bleeds where it rests at the start
            alpha = np.clip(alpha * (1 + 0.25 * np.exp(-fields["arc"] / (2 * fields["radius"] + 1))), 0, 1)
        else:
            tone = tone ** np.exp(spec["streak"] * streak)[..., None]
    lay(canvas, box, alpha * spec["alpha"] * float(op["opacity"]), tone, spec["mode"])


# --- flats -----------------------------------------------------------------------

def polygon_depth(points, box, pad_shape):
    """Signed distance (px) to the polygon's outline over the box, positive inside,
    and the nearest outline pixel of every pixel."""
    y0, y1, x0, x1 = box
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(mask).polygon([(float(x - x0), float(y - y0)) for x, y in points], fill=1)
    inside = np.asarray(mask, dtype=bool)
    if not inside.any():
        return None
    outline = inside & ~ndimage.binary_erosion(inside)
    distance, (rows, cols) = ndimage.distance_transform_edt(~outline, return_indices=True)
    depth = np.where(inside, distance + 0.5, -(distance - 0.5))
    return inside, depth, rows, cols


def outline_arc(points, box, rows, cols, inside):
    """How far along the outline (px) the nearest outline point of each pixel lies."""
    y0, y1, x0, x1 = box
    ring = np.vstack([points, points[:1]])
    step = np.linalg.norm(np.diff(ring, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(step)])
    dense_at = np.arange(0, arc[-1], 1.0)
    dense = np.stack([np.interp(dense_at, arc, ring[:, 0]), np.interp(dense_at, arc, ring[:, 1])], axis=1)
    code = rows * inside.shape[1] + cols
    unique, back = np.unique(code.ravel(), return_inverse=True)
    where = np.stack([unique % inside.shape[1] + x0 + 0.5, unique // inside.shape[1] + y0 + 0.5], axis=1)
    _, nearest = cKDTree(dense).query(where)
    return dense_at[nearest][back].reshape(inside.shape)


def passes(paper, rng, u, v, width, spec, shape_index):
    """The paint texture of brush passes running along u, side by side across v,
    each about `width` px wide: a value near 0 (mean) per pixel, and where a pass
    overlaps the one before it (0..1)."""
    # a hand does not keep a pass straight: it bows a little across its run
    bow = 0.22 * width * paper.sample(paper.warp, u / (7 * width) + 13 * shape_index, v / (9 * width))
    lane = (v + bow) / (0.78 * width)
    index = np.floor(lane)
    across = lane - index
    # each pass carries its own paint, which runs thicker and thinner along it as
    # the brush is pressed and lifts; the change is smooth along a pass and
    # steps only from one pass to the next
    row0, col0 = rng.uniform(0, 256), rng.uniform(0, 512)
    load = paper.sample(paper.warp, (index * 5.37 + row0) % 128, col0 + u / (1.2 * width))
    load = load / (np.abs(paper.warp).max() + 1e-12) * 2.5
    bristle = paper.sample(paper.bristles, row0 + v / 1.6, col0 + u / 70.0)
    fine = paper.sample(paper.bristles, row0 + 128 + v / 0.9, col0 + u / 25.0)
    overlap = np.clip(1 - across / 0.16, 0, 1) ** 2
    texture = (spec["load"] * load
               + spec["streak"] * (0.7 * bristle + 0.3 * fine)
               + spec["ridge"] * (overlap - 0.12))
    return texture, overlap


def lay_flat(canvas, paper, op, colour, instrument, offset, rng, handedness, shape_index, ratio, streamline):
    spec = FLATS[instrument]
    look = STAGE_LOOK.get(op["stage"], STAGE_LOOK["ink"])
    raw = streamlined(op["points"], streamline)
    points = (raw[:, :2] - offset) * ratio
    outline_half = ratio * (STROKE_SIZES[op.get("size", look["size"])] + 1) * float(op.get("scale", 1.0)) / 2
    height, width = canvas.shape[:2]
    pad = int(outline_half + spec["edge"] * 3 + 4)
    x0 = max(int(np.floor(points[:, 0].min())) - pad, 0)
    y0 = max(int(np.floor(points[:, 1].min())) - pad, 0)
    x1 = min(int(np.ceil(points[:, 0].max())) + pad + 1, width)
    y1 = min(int(np.ceil(points[:, 1].max())) + pad + 1, height)
    if x1 <= x0 or y1 <= y0:
        return
    box = (y0, y1, x0, x1)
    found = polygon_depth(points, box, canvas.shape[:2])
    if found is None:
        return
    inside, depth, rows, cols = found
    # the flat's outline is stroked as well, which widens it by half that stroke
    reach = depth + outline_half
    # a brush edge sways over a long run as well as wandering and catching the grain
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    sway = paper.sample(paper.warp, yy / 9.0 + 40 * shape_index, xx / 9.0)
    wobble = paper.reach * spec["edge"] * (0.6 * sway + 0.45 * paper.wander[y0:y1, x0:x1] + 0.15 * paper.grain[y0:y1, x0:x1])
    alpha = coverage(reach, wobble)
    if instrument == "pencil":
        tooth = paper.tooth[y0:y1, x0:x1]
        alpha = alpha * np.clip((tooth + 0.35) / 0.8, 0.25, 1.0)

    # how wide a brush this flat takes: broad for a big flat, small for a pane
    inner = max(float(depth.max()), 1.0)
    brush = float(np.clip(1.1 * inner, 7.0, 60.0))
    # the middle: passes along the flat's long axis, or the hand's slant on a round one
    held = np.stack([xx[inside], yy[inside]], axis=1)
    centred = held - held.mean(axis=0)
    values, vectors = np.linalg.eigh(np.cov(centred.T) if len(held) > 2 else np.eye(2))
    if values[0] > 0 and values[1] / max(values[0], 1e-9) > 2.2:
        direction = vectors[:, 1]
    else:
        slant = np.radians(rng.uniform(25, 50))
        direction = np.array([np.cos(slant), -np.sin(slant) if handedness == "right" else np.sin(slant)])
    turn = np.radians(rng.normal(0, 6))
    direction = np.array([direction[0] * np.cos(turn) - direction[1] * np.sin(turn),
                          direction[0] * np.sin(turn) + direction[1] * np.cos(turn)])
    u_mid = xx * direction[0] + yy * direction[1]
    v_mid = -xx * direction[1] + yy * direction[0]
    middle, overlap_mid = passes(paper, rng, u_mid, v_mid, brush, spec, shape_index)
    # the edge: one or two passes cut along the outline itself
    u_edge = outline_arc(points, box, rows, cols, inside)
    v_edge = np.maximum(reach, 0)
    edge, overlap_edge = passes(paper, rng, u_edge, v_edge, min(brush, 26.0), spec, shape_index + 0.5)
    blend = np.clip((reach - 0.6 * min(brush, 26.0)) / (0.5 * min(brush, 26.0)), 0, 1)
    blend = blend * blend * (3 - 2 * blend)
    texture = (1 - blend) * edge + blend * middle
    overlap = (1 - blend) * overlap_edge + blend * overlap_mid

    tone = np.broadcast_to(colour, alpha.shape + (3,)).astype(float)
    if spec["mode"] == "over":
        # lighter and darker paint: a power keeps white white and black black,
        # with the change showing most in the middle values
        tone = np.clip(tone, 1e-4, 1) ** np.exp(texture)[..., None]
        if instrument == "paint":
            # matte body colour: the darks lift a touch, as dried gouache does
            tone = 0.03 + 0.97 * tone
    else:
        alpha = np.clip(alpha * (1 + 2.5 * texture) * (1 + 0.9 * spec["ridge"] * overlap), 0, 1)
    lay(canvas, box, alpha * spec["alpha"] * float(op["opacity"]), tone, spec["mode"])


# --- putting it together ---------------------------------------------------------

def lay(canvas, box, alpha, tone, mode):
    y0, y1, x0, x1 = box
    region = canvas[y0:y1, x0:x1]
    weight = np.clip(alpha, 0, 1)[..., None]
    if mode == "over":
        region[:] = region * (1 - weight) + tone * weight
    else:
        region[:] = region * (1 - weight + weight * tone)


def visible(shape, hide, only):
    names = {shape["stage"], shape.get("tag") or ""} - {""}
    if shape["stage"] == "frame":
        return False
    if only and not names & only:
        return False
    return not names & hide


def render(ops, style, palette=None, hide=DRAWING_HIDES, only=(), offsets=None, medium=None, scale=1.0,
           streamline=STREAMLINE):
    """The picture as an HxWx3 array in 0..1, on the ground colour, at the size
    the harness renders the frame with `--scale scale --padding 0`."""
    shapes = stack(ops)
    low, high = frame_bounds(shapes)
    ratio = RATIO * scale
    width, height = (int(round(value)) for value in (high - low) * ratio)
    table, ground = colours(palette)
    medium = medium or style["medium"]
    if medium not in MEDIA:
        fail(f"medium {medium!r} is not one of {', '.join(MEDIA)}")
    line_tool, colour_tool = MEDIA[medium]
    seed = style["seed"]
    paper = Paper(np.random.default_rng([seed, 1]), (height, width), ratio)
    canvas = np.empty((height, width, 3))
    canvas[:] = ground
    hide, only = set(hide or ()), set(only or ())
    offsets = offsets or {}
    handedness = style.get("handedness", "right")
    for order, shape in enumerate(shapes):
        if not visible(shape, hide, only):
            continue
        rng = np.random.default_rng([seed, 2, order])
        look = STAGE_LOOK.get(shape["stage"], STAGE_LOOK["ink"])
        name = shape.get("color", look["color"])
        if name not in table:
            fail(f"op {shape['index']}: colour {name!r} is in neither palette.json nor the stock set")
        line, semi, full = table[name]
        shift = np.asarray(offsets.get(shape["stage"], (0.0, 0.0)), dtype=float)
        origin = low - shift
        fill = shape.get("fill", "none")
        closed = bool(shape.get("closed"))
        if fill in ("pattern", "lined-fill"):
            fail(f"op {shape['index']}: fill={fill!r} is tldraw's hatch; the brush lays no hatch "
                 "nobody wrote. Use fill='fill' or draw the hatching as strokes")
        colour_fill = {"fill": full, "solid": semi, "semi": hex_rgb(SEMI_FILL)}.get(fill)
        if closed and colour_fill is not None and len(shape["points"]) >= 3:
            lay_flat(canvas, paper, shape, colour_fill, colour_tool, origin, rng, handedness, order, ratio,
                     streamline)
            if not np.allclose(colour_fill, line):
                lay_line(canvas, paper, shape, line, COLOUR_LINE[colour_tool], origin, rng, ratio, streamline)
            continue
        instrument = line_tool if shape["stage"] in LINE_STAGES else COLOUR_LINE[colour_tool]
        lay_line(canvas, paper, shape, line, instrument, origin, rng, ratio, streamline)
    return np.clip(canvas, 0, 1)


def parse_offsets(values):
    found = {}
    for raw in values or ():
        try:
            stage, shift = raw.split(":")
            dx, dy = (float(part) for part in shift.split(","))
        except ValueError:
            fail(f"--offset wants STAGE:dx,dy, got {raw!r}")
        found[stage] = (dx, dy)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--ops", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--palette")
    parser.add_argument("--out", required=True)
    parser.add_argument("--hide", default=",".join(DRAWING_HIDES),
                        help="stages or tags to leave out (default: what drawing.png hides)")
    parser.add_argument("--only", default="")
    parser.add_argument("--offset", action="append", help="STAGE:dx,dy in page units, repeatable")
    parser.add_argument("--medium", help="render in this medium instead of the style's")
    parser.add_argument("--like", help="a harness render (drawing.png) whose size and scale to match")
    parser.add_argument("--scale", type=float, default=1.0, help="the harness --scale, if not --like")
    parser.add_argument("--streamline", type=float, default=STREAMLINE,
                        help="the smoothing on every stroke, as the harness's --streamline")
    args = parser.parse_args(argv)
    style = finish.read_style(args.style)
    try:
        with open(args.ops) as handle:
            ops = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read {args.ops}: {error}")
    palette = None
    if args.palette:
        sys.path.insert(0, __file__.rsplit("/", 1)[0])
        from pen import read_palette
        palette = read_palette(args.palette)
    scale = args.scale
    if args.like:
        low, high = frame_bounds(stack(ops))
        with Image.open(args.like) as like:
            size = like.size
        scale = size[0] / ((high[0] - low[0]) * RATIO)
    picture = render(ops, style, palette, hide=[n for n in args.hide.split(",") if n],
                     only=[n for n in args.only.split(",") if n], offsets=parse_offsets(args.offset),
                     medium=args.medium, scale=scale, streamline=args.streamline)
    if args.like and picture.shape[1::-1] != tuple(size):
        fail(f"{args.like} is {size[0]}x{size[1]} but the frame renders {picture.shape[1]}x{picture.shape[0]} "
             "at that scale; was it rendered from this ops.json with --padding 0?")
    Image.fromarray(np.round(picture * 255).astype(np.uint8)).save(args.out)
    print(f"brushed {args.out}")


if __name__ == "__main__":
    main()
