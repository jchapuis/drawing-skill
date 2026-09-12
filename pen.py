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
import json
import math

import numpy as np
from scipy.ndimage import gaussian_filter1d

_HAND = np.random.default_rng(11)


def seed(value):
    """Re-seed the hand: same seed, same drawing; different seed, the same
    drawing made again by the same person on a different day."""
    global _HAND
    _HAND = np.random.default_rng(value)


# --- the shape you asked for -------------------------------------------------

def _catmull(points, per_span=12, alpha=0.5):
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
    padded = [points[0]] + points + [points[-1]]
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
    curve.append(points[-1])
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

def stroke(points, stage="ink", tag=None, closed=False, weight=1.0, lead=0.18,
           tail=0.22, smooth=True, per_span=12, hand=1.0, tool="brush", nib=None,
           **look):
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
      the duplicate point.
    - **A small closed form takes a technical nib.** `closed=True` sets
      `lead = tail = 0.06`, but a brush still ramps to nothing at both ends, and
      on a 20px loop the two tapers land on the same point and cancel -- the
      form renders OPEN at the join, and looks closed at 1:1. Seven sweat drops
      came back as "C" shapes at 4x. `tool="pen"` closes cleanly. The smaller
      the form, the more of it the taper eats.
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
    kit = INSTRUMENTS.get(tool, INSTRUMENTS["brush"])
    if nib:
        step, thickness = WEIGHTS[nib]
        look.setdefault("size", step)
        look.setdefault("scale", round(thickness * _GAUGE, 3))
    look.setdefault("dash", kit["dash"])
    if kit["alpha"] < 1.0:
        look.setdefault("opacity", kit["alpha"])

    path = _catmull(points, per_span) if (smooth and len(points) > 2) \
        else _densify([tuple(point[:2]) for point in points])
    if closed and path[0] != path[-1]:
        path = path + [path[0]]
        lead = tail = 0.06
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


def write(path, ops):
    """Flatten the ops and save them.

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
    with open(path, "w") as handle:
        json.dump(flat, handle)
    return path
