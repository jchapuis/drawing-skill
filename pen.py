#!/usr/bin/env python3
"""A pen. You say where the line goes; it decides how the line is made.

That split is the whole point. Control points are a drawing decision and stay
yours -- placing them is the part that requires looking at the subject. What
happens between them is hand mechanics, and hand mechanics are not decoration:
they follow measured laws, and reproducing those laws is what separates a line
that reads as drawn from a line that reads as plotted.

Three of them are implemented here.

**Speed follows curvature.** The two-thirds power law -- velocity proportional to
curvature to the power minus one third -- is one of the most established
invariants in human movement. A hand slows into a tight turn and runs through a
gentle one, always, without being told to. Everything else below is driven off
that speed rather than off position, which is why the variation lands where a
person's would.

**Variation lives between marks, not along them.** A trained hand draws a
*smooth* line; what differs from one mark to the next is where it landed, how
hard it leaned, and a slight bow across the whole arc. It does not shake en
route. Physiological tremor is real and is measured in tens of microns -- at the
scale a drawing is looked at it is invisible, and drawing it in is the loudest
way to make a line look like a beginner's. So the deviation here is offset, lean
and one lazy bend, and nothing of higher frequency than that.

**Nothing repeats.** In forensic document examination, two signatures that match
too closely are evidence of forgery -- authenticity is measurable variation
between instances, not fidelity to a template. The same instruction issued twice
here produces two different strokes.

    from pen import stroke, write
    write("ops.json", [stroke([(340, 280), (360, 275), (385, 284)], stage="ink")])
"""
import ast
import itertools
import json
import math
import os
import sys
import zlib

import numpy as np
from scipy.ndimage import gaussian_filter1d

_HAND = np.random.default_rng(11)


_SEED = 11


def seed(value):
    """Re-seed the hand: same seed, same drawing; different seed, the same
    drawing made again by the same person on a different day."""
    global _SEED
    _SEED = value


def _hand_for(points, stage, tag):
    """A hand seeded by the mark itself, so editing one stroke moves only that
    stroke. Drawn from one running generator, inserting or deleting a mark
    reshuffled the jitter of every mark after it, and a gate that had passed
    on the far side of the picture failed again."""
    key = zlib.crc32(repr((stage, tag, [tuple(round(float(c), 1) for c in p[:2])
                                        for p in points])).encode())
    return np.random.default_rng([_SEED, key])


# --- the shape you asked for -------------------------------------------------

def _catmull(points, per_span=12, alpha=0.5, closed=False):
    """Smooth curve through every control point, not near them.

    Catmull-Rom interpolates: the curve passes through the points you chose, so
    a mark lands where you decided it should. A Bezier or a smoothing spline
    would treat your decisions as suggestions and pull the line off them.

    **Centripetal**, not uniform: the knots are spaced by the square root of the
    distance between points rather than evenly. On evenly spaced points the two
    are indistinguishable; on unevenly spaced ones the uniform form takes the
    tangent at a vertex as half the vector between its neighbours, so a vertex
    with one near neighbour and one far one gets an enormous tangent, and the
    curve can cusp or cross itself. Centripetal is provably free of both.

    **It does not make corners, and nothing here does.** No interpolating spline
    can turn a right angle at a single vertex whose neighbours are far away --
    it will leave the corner by a wide margin whatever the parameterisation,
    and the two forms merely disagree about which axis it bulges along. A wall's
    base bowed a hundred pixels onto the floor that way, and no trap covers a
    fault like that, because the shape is not where its points are. **A shape
    with a corner in it is not a curve**: draw it with `smooth=False`, which
    densifies instead of interpolating -- what the block-in has always done -- or
    plant a point on each side of every corner, close in.
    """
    points = [tuple(point[:2]) for point in points]
    if len(points) < 3:
        return points
    # a closed curve wraps its tangents round the join instead of clamping them
    padded = ([points[-1]] + points + [points[0], points[1]]) if closed \
        else ([points[0]] + points + [points[-1]])
    curve = []
    for index in range(len(padded) - 3):
        knot, span = [0.0], padded[index:index + 4]
        for start, end in zip(span, span[1:]):
            reach = math.hypot(end[0] - start[0], end[1] - start[1])
            knot.append(knot[-1] + max(reach, 1e-9) ** alpha)
        for step in range(per_span):
            t = knot[1] + (knot[2] - knot[1]) * step / per_span
            first = _blend(span[0], span[1], knot[0], knot[1], t)
            second = _blend(span[1], span[2], knot[1], knot[2], t)
            third = _blend(span[2], span[3], knot[2], knot[3], t)
            curve.append(_blend(
                _blend(first, second, knot[0], knot[2], t),
                _blend(second, third, knot[1], knot[3], t),
                knot[1], knot[2], t))
    curve.append(points[0] if closed else points[-1])
    return curve


def _blend(start, end, from_knot, to_knot, t):
    span = to_knot - from_knot
    if span < 1e-12:
        return end
    near, far = (to_knot - t) / span, (t - from_knot) / span
    return (near * start[0] + far * end[0], near * start[1] + far * end[1])


def _densify(points, step=4.0):
    """Plant a point every few pixels along each segment.

    A straight run must be delivered as many close points. tldraw renders
    freehand through perfect-freehand, which smooths between whatever points it
    is given -- hand it a sparse polygon and every corner comes back rounded
    off, which is the shape the block-in exists to avoid.
    """
    dense = []
    for index in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[index][:2], points[index + 1][:2]
        span = math.hypot(x2 - x1, y2 - y1)
        for part in range(max(1, int(span / step))):
            along = part / max(1, int(span / step))
            dense.append((x1 + (x2 - x1) * along, y1 + (y2 - y1) * along))
    dense.append(tuple(points[-1][:2]))
    return dense


# --- the hand that draws it --------------------------------------------------

def _curvature(points):
    first = np.gradient(points, axis=0)
    second = np.gradient(first, axis=0)
    cross = np.abs(first[:, 0] * second[:, 1] - first[:, 1] * second[:, 0])
    return cross / np.maximum(np.linalg.norm(first, axis=1) ** 3, 1e-9)


def _speed(points):
    """The two-thirds power law: v proportional to curvature^(-1/3).

    Returned normalised to roughly 0..1. Slow through tight turns, fast along
    gentle runs -- the hand does this on its own, and every other quantity below
    is driven off it rather than off arc length.
    """
    turn = _curvature(points)
    scale = np.percentile(turn, 85)
    turn = np.clip(turn / (scale + 1e-9), 0.02, 12.0)
    fast = turn ** (-1.0 / 3.0)
    return (fast - fast.min()) / (fast.ptp() + 1e-9)


def _wander(count, sigma):
    """Smooth, self-correlated noise -- pink rather than white.

    Scaled by how much the filter is known to shrink white noise, not by the
    spread this particular sample happened to come out with. Dividing by a
    realised standard deviation is what used to put whole marks tens of pixels
    off their own control points: the sigma here is a large fraction of the
    stroke, so the slice that survives the filter is nearly constant, its spread
    is nearly zero, and the quotient comes back as a large rigid offset that no
    `hand` value bounds. A mark that does not land on the points it was given
    is not a hand, it is a broken instrument -- the control points are the
    drawing, and everything else in this file exists to serve them.
    """
    pad = int(6 * sigma) + 3
    raw = _HAND.standard_normal(count + 2 * pad)
    smooth = gaussian_filter1d(raw, sigma)[pad:pad + count]
    return np.clip(smooth * math.sqrt(2.0 * math.sqrt(math.pi) * sigma), -3.0, 3.0)


def _normals(points):
    step = np.gradient(points, axis=0)
    length = np.linalg.norm(step, axis=1, keepdims=True)
    return np.stack([-step[:, 1], step[:, 0]], axis=1) / np.maximum(length, 1e-9)


def _drift(points, speed, amount):
    """Where a mark lands, not how much it shakes.

    A trained hand does not tremble along a stroke. Watch someone ink: the line
    is *smooth*. What varies between one of their marks and the next is where it
    landed, how hard they leaned, and a slight systematic bow across the whole
    arc -- never a wobble travelling along it. Tremor is what you get from a
    hand that is unsure, resting on nothing, or moving too slowly, and putting
    it into every line is the single loudest way to make a drawing look amateur.

    So the deviation here is deliberately low-order:

    - **an offset**: the whole mark sits a little off where it was aimed,
    - **a bow**: at most one gentle bend across the stroke, from the arm
      swinging about a joint rather than tracking a mathematical path,
    - **nothing above that**. The ~10 Hz physiological tremor is real and is
      measured in tens of microns; at the scale a drawing is looked at it is
      invisible, and rendering it is a lie about what a hand does.

    Signal-dependent motor noise still applies, but it shows up as variability
    in *where the stroke ends up*, not as shake en route -- so speed scales the
    offset, not a per-point jitter.
    """
    count = len(points)
    if count < 4 or amount <= 0:
        return points
    # sigma of the full length: less than one cycle across the stroke, so this
    # reads as a single lazy bend rather than as a wave
    bow = _wander(count, max(6.0, count * 1.2)) * 0.55
    lean = float(np.mean(speed)) * 0.5 + 0.5
    swing = bow * amount * lean
    swing = swing + _HAND.normal(0, amount * 0.9)   # the whole mark lands off
    return points + _normals(points) * swing[:, None]


def _run_on(points, speed, amount):
    """Overshoot or fall short, in proportion to the speed of arrival.

    A stroke arriving fast carries past its target; one arriving slowly stops
    near it. Fixed jitter at the ends misses this -- and a drawing whose lines
    all meet exactly reads as assembled rather than drawn.
    """
    out = [tuple(point) for point in points]
    for end, inner in ((0, 1), (-1, -2)):
        if _HAND.random() > 0.78:
            continue
        (x1, y1), (x2, y2) = out[end], out[inner]
        span = math.hypot(x1 - x2, y1 - y2)
        if span < 1e-6:
            continue
        reach = float(_HAND.normal(1.5, 1.7)) * amount * (0.4 + 1.4 * float(speed[end]))
        out[end] = (x1 + (x1 - x2) / span * reach, y1 + (y1 - y2) / span * reach)
    return out


def _pressure(speed, lead, tail, weight, floor=0.0):
    """Press into the stroke, lift out of it, and lean where the hand slows.

    Flat pressure is the loudest tell that a line was issued rather than drawn.
    The slow parts of a stroke lay down more ink, which is the same fact as a
    pen thickening into a corner.

    **The ends must reach nothing.** A drawn line is pointed at both ends --
    thick through the middle, tapering out as the tool accelerates in and
    decelerates away. A line held at a floor of even a tenth of its width ends
    bluntly, and a drawing whose every mark is a tube with cut ends reads as a
    sketch no matter how well placed it is. So the ramp goes to zero, and the
    weight floor exists only to stop a mark vanishing along its middle.

    `floor` is the exception, and it belongs to the medium rather than to the
    hand: **paint has a minimum bead**. Ink and graphite come off a point and
    can taper to nothing, but a loaded brush of body colour lays a mark with
    width in it from the moment it touches. A correction that tapers away to
    nothing does not cover the thing it was put there to cover.
    """
    count = len(speed)
    along = np.linspace(0.0, 1.0, count)
    rise = np.minimum(1.0, along / lead) ** 1.4 if lead > 0 else np.ones(count)
    fall = np.minimum(1.0, (1 - along) / tail) ** 1.4 if tail > 0 else np.ones(count)
    lean = 1.25 - 0.45 * speed
    ramp = np.clip(rise * fall, 0.0, 1.0)
    return np.clip(weight * lean, 0.10, 1.0) * (floor + (1.0 - floor) * ramp)


# --- instruments -------------------------------------------------------------

# Effective stroke width on the canvas is (STROKE_SIZES[size] + 1) * scale, with
# STROKE_SIZES = {s:2, m:3.5, l:5, xl:10}. Using the four size names alone gives
# barely a 2.5x range; the ratio between the finest detail line and the heaviest
# silhouette in a drawn illustration is nearer 8-10x. `scale` is a free float, so
# the weights below span that properly.
_GAUGE = 1.0


def gauge(subject_height, reference=430.0):
    """Scale every nib to the size of the thing being drawn.

    Draw a ladder before you trust it: one stroke per weight you intend to use,
    rendered, read back with `check.py --weights`. You cannot predict a width
    from the numbers, because the renderer's own scaling sits between them and
    the pixels.

    **Draw the ladder in its own document, never in the drawing.** There is no
    "off to the side": `frame()` with `--padding 0` clips to the subject's
    rectangle, so a ladder outside the frame is invisible and one inside it is
    now part of the drawing, permanently, because the document on disk IS the
    drawing. Use a throwaway `ladder.py` -> `ladder.json` with the same
    `--palette` and `--padding`, and delete it after.

    **Read the ladder in subject pixels, not render pixels.** The export comes
    back at the browser's device pixel ratio -- normally 2x, so a 928-wide frame
    renders 1848 wide -- and nothing in the render says so. Divide every width
    you read off a render by (png width / frame width) before comparing it to
    anything measured off the subject. A first ladder read came back "hairline =
    6px" against a subject whose entire line span is 2-5px.

    **`gauge` is for a single subject. On a scene, skip it.** A scene has no one
    subject height: gauging on a 920px rider sets `_GAUGE = 2.14` and multiplies
    every nib by it, against a subject whose lines are 4px. Both scene drawers
    abandoned the nib names and calibrated `size`/`scale` directly off their own
    measured ladder, which is what worked. `WEIGHTS`' internal span is 5.3x; a
    flat cel subject wants about 4x, and no choice of gauge makes the names land
    on it.

    **Draw the ladder with the instrument you will use.** Each `tool` has its
    own ladder and nothing about the numbers says so: one measured with a
    `brush` and then applied with `flat` came out at 0.42x -- a top tube 5px
    wide where 12px had been asked for, and a whole bicycle arriving at
    `reference/bicycle.md`'s "reads as wire" failure by a route that file does
    not name. Calibrate the instrument, not the weight. `scale` dominates;
    `size` barely moves it.

    Line weight is meaningless in absolute pixels. The heaviest line in a
    drawing is heavy *relative to the subject* -- a silhouette that reads as
    confident around a head 400px tall is a blot around one 120px tall. Call
    this once, with the height of the subject on the canvas, before drawing.
    """
    global _GAUGE
    _GAUGE = max(0.15, subject_height / reference)
    return _GAUGE


WEIGHTS = {
    "hairline": ("s", 0.18),
    "fine": ("s", 0.34),
    "medium": ("m", 0.46),
    "bold": ("l", 0.62),
    "heavy": ("l", 0.95),
}

# What the mark is made WITH, which is a different question from how wide it is.
#   brush   -- swings thin to thick with pressure; the expressive contour tool
#   pen     -- technical nib, dead uniform width, no pressure response at all
#   marker  -- broad, flat, slightly translucent so overlaps darken
#   crayon  -- does not lay a solid mark: builds in broken grainy passes
INSTRUMENTS = {
    "brush": dict(dash="draw", press=1.0, passes=1, alpha=1.0, spread=0.0),
    "pen": dict(dash="solid", press=0.0, passes=1, alpha=1.0, spread=0.0),
    "marker": dict(dash="solid", press=0.15, passes=1, alpha=0.75, spread=0.0),
    "crayon": dict(dash="draw", press=0.7, passes=3, alpha=0.42, spread=1.5),
    # for flats: opaque, even, no pressure. A flat is a region of colour, not a
    # mark, and any translucency turns every overlap into a visible seam.
    "flat": dict(dash="solid", press=0.0, passes=1, alpha=1.0, spread=0.0),
    # body colour on a brush -- process white, and the only instrument that goes
    # ON TOP of dry ink. It has less swing than a brush loaded with ink because
    # paint is thicker, and it never tapers to nothing, because a bead of paint
    # has width from the moment it touches.
    "gouache": dict(dash="draw", press=0.55, passes=1, alpha=1.0, spread=0.0, floor=0.45),
}


# --- marks -------------------------------------------------------------------

def trap_outward(points, distance):
    """Grow a closed flat outward, so its ink covers its edge rather than the
    ground showing between them.

    A fill outline measured off the tracer sits at the colour transition, which
    is INSIDE the ink line. Rendered verbatim the flat falls short by half a line
    width, and wherever the contour bulges outward the ground shows through as a
    pale notch bitten out of the object. Printers have always solved this by
    trapping: the colour is made slightly larger than the line that will cover
    it, so no registration error can open a gap. Nothing about the drawing wants
    the flat's true edge to be visible, because it never is -- the ink is on top
    of it.

    A miter offset along each vertex's angle bisector, with the spike at a sharp
    corner clamped rather than allowed to shoot off.
    """
    import numpy as _np
    seen = _np.asarray([[float(p[0]), float(p[1])] for p in points])
    if len(seen) < 3 or distance <= 0:
        return points
    twice_area = float(_np.sum(seen[:, 0] * _np.roll(seen[:, 1], -1)
                               - _np.roll(seen[:, 0], -1) * seen[:, 1]))
    facing = 1.0 if twice_area > 0 else -1.0

    def unit(vectors):
        length = _np.hypot(vectors[:, 0], vectors[:, 1])
        length[length < 1e-9] = 1e-9
        return vectors / length[:, None]

    into = unit(seen - _np.roll(seen, 1, axis=0))
    outof = unit(_np.roll(seen, -1, axis=0) - seen)
    normal_in = _np.stack([into[:, 1], -into[:, 0]], axis=1) * facing
    normal_out = _np.stack([outof[:, 1], -outof[:, 0]], axis=1) * facing
    bisector = unit(normal_in + normal_out)
    reach = _np.clip(_np.sum(bisector * normal_in, axis=1), 0.3, 1.0)
    moved = seen + bisector * (distance / reach)[:, None]
    return [(float(x), float(y)) + tuple(p[2:]) for (x, y), p in zip(moved, points)]


def stroke(points, stage="ink", tag=None, closed=False, weight=1.0, lead=0.18,
           tail=0.22, smooth=True, per_span=12, hand=1.0, tool="brush", nib=None,
           trap=None, **look):
    """One mark. `points` are your decisions; everything else is the hand.

    `tool` picks the instrument and `nib` the weight; a crayon returns several
    overlapping passes rather than one stroke, so this may return a list. `write`
    flattens.

    `stage` says WHEN in the ladder the mark was made; `tag` says WHICH OBJECT it
    belongs to. They are independent, and `--only` / `--hide` match either, so
    `--only bike,frame` renders the bicycle at every stage and
    `--only bike,blockin,frame` renders it over the composition rough. Tag every
    mark of a tier-1 object; the ladder machinery is untouched, because the stage
    is still there.

    Traps, all of them paid for:

    - **A corner needs `smooth=False`.** No interpolating spline passes through
      a corner: sent as a smooth path the curve leaves each of your points by a
      wide margin, and the shape is then not where its points are -- you
      measured honestly and the mark landed somewhere else. A row of teeth
      measured as a straight-sided block came back as a lens. Either draw it
      with straights, or plant a point either side of every corner, close in.
    - **`closed=True` closes the path for you.** Repeat the first point as well
      and the spline turns through a zero-length segment, which renders as a
      cusp. A clock rim spent a round being blamed on its closure when it was
      the duplicate point. A closed stroke carries no taper -- a loop has no
      ends -- and its closing side is built like every other side, so a
      triangle of three points renders three sides.
    - **`fill="solid"` is a pale tint and `fill="fill"` is saturated -- until
      `--palette` repoints that colour.** `repaint()` writes one value into
      `solid`, `fill`, `semi` and `pattern`, so on a repointed name the two are
      identical. True for the stock palette, false for the workflow this skill
      prescribes.
    - **A flat is its polygon PLUS a stroke of that path.** `tool="flat"` fills
      *and* outlines, and with no `size`/`scale` given the outline takes
      tldraw's own default -- roughly 5px each side. On a big flat that is free
      trapping and invisible. On a small one it is a disaster and it is silent:
      an 11px iris rendered at 21.5px, and three rounds of shrinking the same
      polygon measured no change, because the polygon was never what rendered.
      Pin `size`/`scale` on every flat.
    - **Flats need `tool="flat"`.** At any translucency every overlap shows as
      a seam.
    """
    if tool == "pen" and (lead, tail) != (0.18, 0.22):
        # the technical pen draws at constant pressure: a lead or tail was
        # silently ignored, and a spoke meant to end in a point ended square
        raise ValueError("stroke: the pen has no taper -- lead/tail do nothing on tool='pen'; "
                         "use tool='brush' for a line that ends in a point")

    # `trap=<px>` grows a closed flat outward so the ink laid over it covers its
    # edge. OPT-IN, and deliberately not a default: trapping is directional. It
    # belongs on a body flat, whose edge is meant to be hidden under a contour,
    # and it ruins any flat that is a mark in its own right -- a vent, an eye, a
    # cast shadow, a shade. Applied to every closed flat it swells the interior
    # shapes until they eat the form. `--unfilled` says which flats need it.
    look["authored"] = _origin(points)
    if tool == "flat" and closed and trap and len(points) >= 3:
        points = trap_outward(points, float(trap))

    global _HAND
    _HAND = _hand_for(points, stage, tag)
    kit = INSTRUMENTS.get(tool, INSTRUMENTS["brush"])
    if nib:
        step, thickness = WEIGHTS[nib]
        look.setdefault("size", step)
        look.setdefault("scale", round(thickness * _GAUGE, 3))
    look.setdefault("dash", kit["dash"])
    if tool == "flat":
        look.setdefault("fill", "fill")   # a flat with no fill is an outline
    if kit["alpha"] < 1.0:
        look.setdefault("opacity", kit["alpha"])

    flat_points = [tuple(point[:2]) for point in points]
    if closed:
        # a loop has no ends: close the CONTROL points, so the closing side is
        # densified or interpolated like every other, and carry no taper
        lead = tail = 0.0
    path = _catmull(flat_points, per_span, closed=closed) if (smooth and len(points) > 2) \
        else _densify(flat_points + ([flat_points[0]] if closed else []))
    body = np.asarray(path, dtype=float)
    if len(body) < 4:
        return _emit(body, np.full(len(body), 0.5 * weight), stage, tag, closed, look)

    speed = _speed(body)
    reach = float(np.linalg.norm(np.diff(body, axis=0), axis=1).sum())
    # a short mark has no room to wander; scale the imprecision to the gesture
    amount = hand * min(1.9, 0.4 + reach / 700.0)

    marks = []
    for pass_index in range(kit["passes"]):
        laid = _drift(body, speed, amount + kit["spread"] * pass_index)
        if not closed and hand > 0:
            laid = np.asarray(_run_on(laid, speed, amount), dtype=float)
        # A technical pen has no pressure response: flat z, uniform width. A
        # brush has all of it. `press` scales between those two extremes.
        lively = _pressure(speed, lead, tail,
                           weight * (1.0 + float(_HAND.normal(0, 0.07 * hand))),
                           kit.get("floor", 0.0))
        flat = np.full(len(lively), float(np.clip(weight * 0.72, 0.12, 1.0)))
        press = flat + (lively - flat) * kit["press"]
        marks.append(_emit(laid, press, stage, tag, closed, dict(look)))
    return marks[0] if len(marks) == 1 else marks


def _emit(body, press, stage, tag, closed, look):
    op = {
        "op": "stroke",
        "stage": stage,
        "closed": closed,
        "points": [[round(float(x), 2), round(float(y), 2), round(float(press[i]), 3)]
                   for i, (x, y) in enumerate(body)],
    }
    if tag:
        op["tag"] = tag
    op.update(look)
    return op


# --- one verb -----------------------------------------------------------------
#
# `stroke` is the whole repertoire. There is no ellipse, no ruled line, no
# block-in helper, and there will not be any: the marks a drawing is made of are
# the marks a hand makes, and a hand has one of them. A straight is a stroke with
# `smooth=False`. A block-in chord is a stroke with `smooth=False`. A ruled
# construction line is a stroke with `smooth=False` and the hand turned down --
# it is still drawn, and a ruled line laid by a person is not a different kind of
# thing from a contour, it is the same tool held still.
#
# `frame` below is not a mark. It is the edge of the picture.
#
# There was, and it is the single most expensive mistake this file has made. A
# head was constructed with `ellipse(505, 348, 74, 68)` and a centre line down
# the middle of it -- a frontal Loomis ball, for a head that is turned three
# quarters to the right. Every feature was then measured honestly and hung on
# that armature, every bounding box came out within ten pixels of the subject's,
# and the result was not a face. The tool supplied the shape, so nobody looked
# for it: the skull was a symbol before the subject was consulted.
#
# A ball drawn by hand is six or eight points that somebody chose after looking,
# and its errors are where the looking was wrong. A ball computed from a centre
# and two radii has no errors and no information -- it is the generic head,
# arriving free of charge at the exact stage whose whole job is to find the
# particular one. `stroke` is the language. If a form is round, say where its
# round goes, in points.


def frame(x0, y0, x1, y1):
    """A near-invisible rectangle pinning the render bounds, so the drawing
    stays in the subject's coordinate space and overlays compare exactly."""
    return stroke([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], stage="frame",
                  closed=True, smooth=False, hand=0.0, color="grey", size="s",
                  opacity=0.03)


def fade(stage, opacity=0.12):
    return {"op": "fade", "stage": stage, "opacity": opacity}


def erase(stage):
    return {"op": "erase", "stage": stage}


def back(stage="fill"):
    """Send a stage behind everything else -- colour belongs under the ink."""
    return {"op": "back", "stage": stage}


LADDER = ("gesture", "blockin", "contour", "ink")


def audit(ops):
    """The ladder, read off the script. Returns (counts, first index per stage,
    list of failures). A failure is a drawing with ink and no gesture, block-in
    or contour stage anywhere in it, or a stage whose first mark comes after the
    first mark of the stage above it. It is a check that the stages EXIST, not
    that each ink mark has a contour under it: on three finished drawings 26-81%
    of ink strokes had no contour stroke within two line widths, so a per-mark
    rule would refuse every drawing the skill has made."""
    counts, first = {}, {}
    for index, op in enumerate(ops):
        if op.get("op") != "stroke":
            continue
        stage = op.get("stage", "ink")
        counts[stage] = counts.get(stage, 0) + 1
        first.setdefault(stage, index)
    failures = []
    if counts.get("ink"):
        for stage in LADDER[:-1]:
            if not counts.get(stage):
                failures.append(f"ink with no {stage} stage: the ladder was skipped")
        # gesture, then block-in, then ink. The contour is required to exist,
        # not to come first: forms drawn in depth order interleave their stages
        ordered = ("gesture", "blockin", "ink")
        order = [first[stage] for stage in ordered if stage in first]
        if order != sorted(order):
            failures.append("stages out of order: "
                            + " > ".join(f"{stage}@{first[stage]}" for stage in ordered if stage in first))
    return counts, first, failures


_CALLS = itertools.count()


def _origin(points):
    """Where a stroke's points were written: the script line that asked for it,
    the file the call itself sits in, and the points as given, before trapping.
    `at` carries the instruction offset too, so two calls on one line differ and
    one call reached twice -- a loop, a comprehension, an import -- does not."""
    here = os.path.abspath(__file__)
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    main = os.path.abspath(main) if main else None
    by = at = None
    frame = sys._getframe(1)
    while frame is not None:
        name = os.path.abspath(frame.f_code.co_filename)
        if by is None and name != here:
            by = f"{os.path.basename(name)}:{frame.f_lineno}"
        if name == main:
            at = [frame.f_lineno, frame.f_lasti]
        frame = frame.f_back
    return {"call": next(_CALLS), "script": os.path.basename(main) if main else None,
            "by": by, "at": at,
            "points": [[round(float(p[0]), 2), round(float(p[1]), 2)] for p in points]}


def _literal_pairs(source):
    """Every (x, y) written as two numbers in the script's own text."""
    pairs = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Tuple, ast.List)) and len(node.elts) >= 2:
            values = []
            for element in node.elts[:2]:
                sign = 1.0
                if isinstance(element, ast.UnaryOp) and isinstance(element.op, ast.USub):
                    sign, element = -1.0, element.operand
                if isinstance(element, ast.Constant) and isinstance(element.value, (int, float)) \
                        and not isinstance(element.value, bool):
                    values.append(round(sign * float(element.value), 2))
            if len(values) == 2:
                pairs.add(tuple(values))
    return pairs


LITERAL_FLOOR = 0.9


def provenance(ops, source=None):
    """Were these marks written by the drawer, in the script, or generated?

    Returns (facts, failures). Three signals, each chosen because authored work
    cannot trip it, measured on six hand-written drawings (89 to 498 strokes):

    - a stroke whose call sits in another file than the script -- a generated
      section module, a helper library. Authored: 0 of 1,674 strokes.
    - one call site in the script reached more than once -- a loop, a
      comprehension, or an `import` of a module that draws. Authored: 0.
    - control points that are not written as numbers in the script's own text:
      loaded from JSON, computed from pixels, scaled. Authored: at least 99.5% are
      literal (the rest are frame corners written as W, H); a drawing whose points
      come out of a skeleton or a trace is at 0.2%. The floor is LITERAL_FLOOR.

    What none of them can see is generated output pasted into the script as
    literal lines. That is still a generated drawing, and the rule, not this
    gate, is what forbids it.
    """
    strokes = [op for op in ops if op.get("op") == "stroke" and op.get("stage") != "frame"]
    calls, unrecorded = {}, 0
    for op in strokes:
        origin = op.get("authored")
        if origin is None:
            unrecorded += 1
        else:
            calls.setdefault(origin["call"], origin)
    origins = list(calls.values())
    failures = []
    if unrecorded:
        failures.append(f"{unrecorded} strokes carry no record of where they were written: "
                        "built outside `stroke`, loaded from a file, or written by an older pen")
    foreign = [origin for origin in origins
               if origin["script"] and not str(origin["by"]).startswith(origin["script"] + ":")]
    if foreign:
        files = sorted({str(origin["by"]).split(":")[0] for origin in foreign})
        failures.append(f"{len(foreign)} strokes are called from outside the script, in "
                        + ", ".join(files) + ": a mark is written in the script, not generated into it")
    sites = {}
    for origin in origins:
        if origin["at"]:
            sites.setdefault(tuple(origin["at"]), []).append(origin)
    stamped = {site: group for site, group in sites.items() if len(group) > 1}
    if stamped:
        worst = max(stamped.items(), key=lambda item: len(item[1]))
        failures.append(f"{sum(len(group) for group in stamped.values())} strokes come from "
                        f"{len(stamped)} call sites reached more than once (line {worst[0][0]} "
                        f"made {len(worst[1])}): a loop, a comprehension or an import that draws")
    points = [tuple(point) for origin in origins for point in origin["points"]]
    literal = None
    if source is not None and points:
        written = _literal_pairs(source)
        literal = sum(1 for point in points if point in written) / len(points)
        if literal < LITERAL_FLOOR:
            failures.append(f"only {literal:.1%} of the control points are written as numbers in "
                            f"the script (floor {LITERAL_FLOOR:.0%}): the rest were loaded or computed")
    facts = {"strokes": len(origins), "points": len(points), "literal": literal,
             "unrecorded": unrecorded}
    return facts, failures


def script_source(ops, beside=None):
    """The text of the script these ops name, looked for beside `beside`."""
    names = {op["authored"]["script"] for op in ops
             if op.get("op") == "stroke" and op.get("authored") and op["authored"]["script"]}
    if len(names) != 1:
        return None
    path = os.path.join(beside or ".", names.pop())
    if not os.path.exists(path):
        return None
    with open(path) as handle:
        return handle.read()


def write(path, ops, swatch=False):
    """Flatten the ops, audit the ladder, and save them.

    Refuses to write ink into a drawing with no gesture, block-in and contour
    stage -- a drawing inked straight off its measurements passes every
    placement check and reads as a diagram. The stages must exist; no mark is
    checked for a contour under it. Refuses, too, marks the script did not write:
    strokes generated in another file, stamped by a loop, or whose points were
    loaded or computed rather than written down (see `provenance`). `swatch=True`
    skips both, for a weight ladder or a calibration strip that is not a drawing.

    Stock colours are 13 fixed names, but the palette is mutable: pass
    `--palette colours.json` to the CLI to repoint any name at a real hex value.
    `background` is repointable too, but it is **the ground, not a fourteenth
    colour** -- a mark may not use it, and a drawing that needs to paint in the
    paper's own colour must spend one of the 13 on it.

    **The ground has a right answer: measure it off the subject.** One panel
    carried `#FAF1D2` for six rounds against a subject wall of `#EFE9D1`, eleven
    levels darker. Nothing in the picture looked wrong, because everything
    sitting *on* the ground is judged by its contrast *with* it: the clock face
    and the wall differed by five grey levels where the subject's differ by
    seventeen, so a whole object failed to separate from the thing it hung on.
    One line fixed it, no marks touched, and its structure score went 0.39 to
    1.01. A wrong ground flattens every relationship in the picture at once and
    is invisible to every check that compares marks.
    """
    flat = []
    for op in ops:
        flat.extend(op) if isinstance(op, list) else flat.append(op)
    counts, _, failures = audit(flat)
    if failures and not swatch:
        raise SystemExit("ladder: " + "; ".join(failures) + f"  (stages on the page: {counts})")
    if not swatch:
        main = getattr(sys.modules.get("__main__"), "__file__", None)
        beside = os.path.dirname(os.path.abspath(main)) if main else None
        _, generated = provenance(flat, script_source(flat, beside))
        if generated:
            raise SystemExit("authored: " + "; ".join(generated))
    with open(path, "w") as handle:
        json.dump(flat, handle)
    return path
