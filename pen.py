#!/usr/bin/env python3
"""A pen. You say where the line goes; it decides how the line is made.

The control points are your decisions, and placing them requires looking at the
subject. What happens between them is hand mechanics, which follow measured
laws. Reproducing those laws is what makes a line read as drawn rather than
plotted. Three are implemented here.

**Speed follows curvature.** Under the two-thirds power law, velocity is
proportional to curvature to the power minus one third. A hand slows into a
tight turn and runs through a gentle one without being told to. Everything else
below is driven off that speed rather than off position, so the variation lands
where a person's would.

**Variation is between marks, not along them.** A trained hand draws a smooth
line. What differs from one mark to the next is where it landed, how hard it
leaned, and a slight bow across the whole arc. Physiological tremor is measured
in tens of microns, which is invisible at the scale a drawing is viewed, and
drawing it in makes a line look like a beginner's. So the variation here is an
offset, a lean and one gentle bend, with nothing of higher frequency.

**Nothing repeats.** Two signatures that match too closely are evidence of
forgery, because authentic handwriting varies between instances. The same
instruction issued twice here produces two different strokes.

    from pen import stroke, write
    write("ops.json", [stroke([(340, 280), (360, 275), (385, 284)], stage="ink")])
"""
import ast
import itertools
import json
import math
import os
import re
import sys
import zlib

import numpy as np
from scipy.ndimage import gaussian_filter1d

_HAND = np.random.default_rng(11)


_SEED = 11
_SEED_GIVEN = False


def seed(value):
    """Re-seed the hand. The same seed gives the same drawing; a different seed
    gives the same drawing with different small variations. A seed set here wins
    over the one in style.json."""
    global _SEED, _SEED_GIVEN
    _SEED, _SEED_GIVEN = value, True


def _hand_for(points, stage, tag, *salt):
    """A hand seeded by the mark itself, so editing one stroke changes only that
    stroke. With one running generator, inserting or deleting a mark would
    reshuffle the jitter of every mark after it, and a gate that had passed on
    the far side of the picture could fail again.

    `salt` gives a second, independent hand for the same mark. The style draws
    from that one, so turning a style on never changes the draws the plain hand
    makes."""
    key = zlib.crc32(repr((stage, tag, [tuple(round(float(c), 1) for c in p[:2])
                                        for p in points])).encode())
    return np.random.default_rng([_SEED, key, *salt])


# --- the style of the hand ---------------------------------------------------
#
# `style.json` beside draw.py says whose hand this is: how loose, which hand, in
# what medium. It changes only how a point list lands: where its ends fall,
# which way it is drawn, how it presses. It never adds a mark, moves a control
# point or invents one. With no style the pen draws exactly as it always has.
#
# `finish`, `paper` and `scan` are read by finish.py, not here. They are checked
# here so that a typo fails on the first stroke instead of after the render.

STYLE_CHOICES = {
    "medium": ("ink-pen", "brush-pen", "pencil", "marker", "watercolour+ink", "gouache"),
    "finish": ("clean", "sketch"),
    "handedness": ("right", "left"),
    "paper": ("none", "smooth", "cold-press", "newsprint", "sketchbook"),
    "renderer": ("tldraw", "brush"),
}
STYLE_KEYS = ("medium", "hand", "finish", "handedness", "paper", "scan", "seed", "renderer")

# What each medium draws with when the stroke does not name a tool. The second
# entry adjusts that instrument for the medium. A marker has no taper because
# its felt tip lays full width from the moment it touches.
MEDIA = {
    "ink-pen": ("brush", {"press": 0.6}),     # a nib swells less than a brush
    "brush-pen": ("brush", {}),
    "pencil": ("pencil", {}),
    "marker": ("marker", {"taper": False}),
    "watercolour+ink": ("brush", {}),
    "gouache": ("gouache", {}),
}

# The stages whose ends a viewer reads as the drawing's own line. Construction
# and fills are not drawn as finished line, so they get no hook, blob or gap.
INKED = ("ink", "correct")

_STYLE = None          # None until looked for; {} when there is no style


def _checked(spec, where):
    if not isinstance(spec, dict):
        raise ValueError(f"{where}: a style is a JSON object of settings, got {type(spec).__name__}")
    unknown = sorted(set(spec) - set(STYLE_KEYS))
    if unknown:
        raise ValueError(f"{where}: unknown style key(s) {unknown}; the known keys are {list(STYLE_KEYS)}")
    for key, allowed in STYLE_CHOICES.items():
        if key in spec and spec[key] not in allowed:
            raise ValueError(f"{where}: {key} {spec[key]!r} is not one of {list(allowed)}")
    if "hand" in spec:
        hand = spec["hand"]
        if isinstance(hand, bool) or not isinstance(hand, (int, float)) or not 0.0 <= hand <= 1.0:
            raise ValueError(f"{where}: hand {hand!r} must be a number from 0 (tight) to 1 (loose)")
    if "scan" in spec and not isinstance(spec["scan"], bool):
        raise ValueError(f"{where}: scan {spec['scan']!r} must be true or false")
    if "seed" in spec and (isinstance(spec["seed"], bool) or not isinstance(spec["seed"], int)):
        raise ValueError(f"{where}: seed {spec['seed']!r} must be a whole number")
    return dict(spec)


def style(spec):
    """Set the style: a dict, or the path of a JSON file. `None` clears it, and
    the pen goes back to drawing as it does with no style.json.

    Without this call, the first stroke reads `style.json` from the working
    directory if there is one. An unknown key or value stops the drawing with
    the reason, because a misspelt setting that is silently ignored gives a
    drawing in a style nobody asked for.
    """
    global _STYLE, _SEED
    if spec is None:
        _STYLE = {}
        return _STYLE
    where = "style"
    if isinstance(spec, (str, os.PathLike)):
        where = os.fspath(spec)
        try:
            with open(spec) as handle:
                spec = json.load(handle)
        except json.JSONDecodeError as error:
            raise ValueError(f"{where}: not valid JSON ({error})") from error
    _STYLE = _checked(spec, where)
    if "seed" in _STYLE and not _SEED_GIVEN:
        _SEED = _STYLE["seed"]
    return _STYLE


def _style():
    if _STYLE is None:
        return style("style.json") if os.path.exists("style.json") else style(None)
    return _STYLE


def _looseness(spec):
    """How much a styled hand varies, as a multiple of the plain pen.

    `hand` 0.5 is the plain pen (1x). 0 is a careful hand at a quarter of that,
    never none, because a hand with no variation at all is a plotter. 1 is a
    loose one at 1.75x."""
    return 0.25 + 1.5 * float(spec.get("hand", 0.5))


def _pull(points, closed, handedness, chance):
    """Put the points in the order the hand would draw them.

    A right hand pulls a line from left to right, and a near-vertical one from
    top to bottom. Most left-handers pull horizontals from right to left. The
    points stay the same points and the line passes through each of them; only
    where it starts, and so where the lead and tail taper fall, changes.

    A closed loop has no ends, but it has a direction. Right-handers draw a
    circle anticlockwise in all but about 1% of cases, left-handers clockwise in
    about 39%. `chance` is a draw from 0 to 1 that picks which this loop is. The
    loop keeps its first point and runs the other way round.
    """
    if len(points) < 2:
        return points
    if closed:
        if len(points) < 3:
            return points
        xs = np.asarray([float(p[0]) for p in points])
        ys = np.asarray([float(p[1]) for p in points])
        # with y pointing down the page, a positive shoelace sum runs clockwise
        clockwise = float(np.sum(xs * np.roll(ys, -1) - np.roll(xs, -1) * ys)) > 0
        wanted = chance < (0.01 if handedness == "right" else 0.39)
        return points if clockwise == wanted else [points[0]] + list(points[:0:-1])
    dx = float(points[-1][0]) - float(points[0][0])
    dy = float(points[-1][1]) - float(points[0][1])
    if abs(dy) > 1.7 * abs(dx):            # within about 30 degrees of vertical
        backwards = dy < 0
    else:
        backwards = dx < 0 if handedness == "right" else dx > 0
    return list(points[::-1]) if backwards else points


def _arc(points):
    steps = np.linalg.norm(np.diff(points, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(steps)])


def _fall_short(points, speed, gap, at_start):
    """Stop `gap` pixels before the end, where a line meets the one it runs into.

    A drawing whose every junction closes exactly reads as assembled. A hand
    lifts a little early, and leaves a hair of paper between the two lines. The
    end is cut back along the line, so the mark is shorter, not moved.
    """
    if at_start:
        points, speed = points[::-1], speed[::-1]
    along = _arc(points)
    total = along[-1]
    if total <= gap * 3:
        return (points[::-1], speed[::-1]) if at_start else (points, speed)
    stop = total - gap
    keep = int(np.searchsorted(along, stop, side="right"))
    before, after = points[keep - 1], points[keep]
    t = (stop - along[keep - 1]) / max(along[keep] - along[keep - 1], 1e-9)
    end = before + (after - before) * t
    points = np.vstack([points[:keep], end])
    speed = np.concatenate([speed[:keep], speed[keep:keep + 1]])
    return (points[::-1], speed[::-1]) if at_start else (points, speed)


def _hook(points, size, turn):
    """The curl a fast stroke starts with.

    A stroke is a sum of overlapping velocity pulses that each rise and fall on
    a lognormal curve (the sigma-lognormal model of handwriting). When the hand
    sets off fast, the first pulse is still turning the pen into its direction
    as it touches down, and the line starts with a small hook off its axis.
    `size` is how far off the axis the first point sits, in pixels; the curl
    eases back onto the line over the first few pixels.
    """
    along = _arc(points)
    reach = min(4.0 * size, along[-1] / 4.0)
    if reach <= 0 or size <= 0:
        return points
    near = along < reach
    fade = (1.0 - along[near] / reach) ** 2
    out = points.copy()
    out[near] += _normals(points)[near] * (turn * size * fade)[:, None]
    return out


def _blob(press, points, size):
    """The ink a slow start leaves behind.

    When the hand sets down and then gathers speed slowly, the pen dwells on
    its first point and the line opens with a small dot of extra ink. `size` is
    the extra pressure at the first point; it fades over the first few pixels.
    """
    along = _arc(points)
    reach = max(3.0, min(10.0, along[-1] / 6.0))
    return np.clip(press + size * np.exp(-along / (reach / 2.0)), 0.0, 1.0)


# --- the shape you asked for -------------------------------------------------

def _catmull(points, per_span=12, alpha=0.5, closed=False):
    """Smooth curve through every control point, not near them.

    Catmull-Rom interpolates: the curve passes through the points you chose, so
    a mark lands where you put it. A Bezier or a smoothing spline would pull the
    line off them.

    The spline is centripetal, not uniform: the knots are spaced by the square
    root of the distance between points rather than evenly. On evenly spaced
    points the two are the same. On unevenly spaced points the uniform form takes
    the tangent at a vertex as half the vector between its neighbours, so a
    vertex with one near and one far neighbour gets a very large tangent and the
    curve can cusp or cross itself. The centripetal form avoids both.

    It does not make corners. No interpolating spline can turn a right angle at
    a single vertex whose neighbours are far away. The curve leaves the corner by
    a wide margin whichever parameterisation is used (a wall's base can bow a
    hundred pixels onto the floor), and no check catches it because the shape is
    not where its points are. A shape with a corner is not a curve. Draw it with
    `smooth=False`, which densifies the points instead of interpolating, or
    place a point close in on each side of every corner.
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
    is given. A sparse polygon comes back with every corner rounded off, which
    is what the block-in is meant to avoid.
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

    Returned normalised to roughly 0..1: slow through tight turns, fast along
    gentle runs. Every other quantity below is driven off this speed rather than
    off arc length.
    """
    turn = _curvature(points)
    scale = np.percentile(turn, 85)
    turn = np.clip(turn / (scale + 1e-9), 0.02, 12.0)
    fast = turn ** (-1.0 / 3.0)
    return (fast - fast.min()) / (fast.ptp() + 1e-9)


def _wander(count, sigma):
    """Smooth, self-correlated noise (pink rather than white).

    Scaled by how much the filter is known to shrink white noise, not by the
    spread this particular sample came out with. Dividing by the realised
    standard deviation would put whole marks tens of pixels off their control
    points: sigma here is a large fraction of the stroke, so the slice that
    survives the filter is nearly constant, its spread is nearly zero, and the
    quotient becomes a large rigid offset that no `hand` value bounds. A mark
    must land on the points it was given, because the control points are the
    drawing.
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

    A trained hand does not tremble along a stroke, so the line is smooth. What
    varies between one mark and the next is where it landed, how hard the hand
    leaned, and a slight bow across the whole arc. Tremor comes from a hand that
    is unsure, unsupported or moving too slowly, and adding it to every line
    makes a drawing look amateur.

    So the variation here is low-order:

    - an offset: the whole mark sits a little off where it was aimed,
    - a bow: at most one gentle bend across the stroke, from the arm swinging
      about a joint rather than tracking a mathematical path,
    - nothing above that. The physiological tremor (about 10 Hz) is measured in
      tens of microns and is invisible at the scale a drawing is viewed, so it
      is not modelled.

    Signal-dependent motor noise still applies. It shows up as variability in
    where the stroke ends up, not as shake along it, so speed scales the offset
    and there is no per-point jitter.
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

    A stroke arriving fast carries past its target, and one arriving slowly stops
    near it. Fixed jitter at the ends does not capture this, and a drawing whose
    lines all meet exactly reads as assembled rather than drawn.
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

    Flat pressure is the clearest sign that a line was issued rather than drawn.
    The slow parts of a stroke lay down more ink, as a pen thickens into a
    corner.

    The ends must taper to nothing. A drawn line is pointed at both ends: thick
    through the middle, tapering as the tool speeds up and slows down. A line
    held at even a tenth of its width ends bluntly, and a drawing made of tubes
    with cut ends reads as a diagram however well placed. So the ramp goes to
    zero, and the weight floor only stops a mark vanishing along its middle.

    `floor` is the exception, and it belongs to the medium rather than to the
    hand: paint has a minimum bead. Ink and graphite come off a point and can
    taper to nothing, but a loaded brush of body colour lays a mark with width
    in it from the moment it touches. A correction that tapers to nothing does
    not cover what it was put there to cover.
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

    Line weight is meaningless in absolute pixels. The heaviest line in a
    drawing is heavy relative to the subject: a silhouette that reads as
    confident around a head 400px tall is a blot around one 120px tall. Call
    this once, with the height of the subject on the canvas, before drawing.

    Draw a weight swatch before you trust a weight: one stroke per weight you
    intend to use, rendered and read back with `check.py --weights`. You cannot
    predict a width from the numbers, because the renderer's own scaling sits
    between them and the pixels.

    Draw the swatch in its own document, never in the drawing. `frame()` with
    `--padding 0` clips to the subject's rectangle, so a swatch outside the frame
    is invisible, and one inside it becomes part of the drawing, because the
    document on disk is the drawing. Use a throwaway `swatch.py` -> `swatch.json`
    with the same `--palette` and `--padding`, and delete it after.

    Read the swatch in subject pixels, not render pixels. The export comes back
    at the browser's device pixel ratio, normally 2, so a 928-wide frame renders
    1848 wide, and nothing in the render says so. Divide every width you read off
    a render by (png width / frame width) before comparing it to anything
    measured off the subject. Without that, a hairline can read as 6px against a
    subject whose whole line span is 2-5px.

    `gauge` is for a single subject. On a scene, skip it. A scene has no one
    subject height: gauging on a 920px figure sets `_GAUGE = 2.14` and multiplies
    every nib by it, against a subject whose lines are 4px. In a scene, set
    `size`/`scale` directly from your own measured swatch and ignore the nib
    names. The internal span of `WEIGHTS` is 5.3x, while a flat cel subject
    wants about 4x, and no choice of gauge makes the names land on it.

    Draw the swatch with the instrument you will use. Each `tool` has its own
    weights and nothing in the numbers says so. A swatch measured with `brush`
    and then applied with `flat` came out at 0.42x, a 5px line where 12px had
    been asked for. Calibrate the instrument, not the weight. `scale` dominates;
    `size` barely moves it.
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
    # graphite: pressure changes how dark it is more than how wide, and tldraw
    # can vary only width, so the swing is small and the mark slightly see-
    # through. It still tapers, but not to nothing, because a lead point has a
    # width of its own.
    "pencil": dict(dash="draw", press=0.35, passes=1, alpha=0.85, spread=0.0, floor=0.2),
}


# --- marks -------------------------------------------------------------------

def trap_outward(points, distance):
    """Grow a closed flat outward, so the ink laid over it covers its edge and
    the ground does not show between them.

    A fill outline measured with trace.py sits at the colour transition, which
    is inside the ink line. Rendered as measured, the flat falls short by half a
    line width, and wherever the contour bulges outward the ground shows through
    as a pale notch in the object. Printers call the fix trapping: the colour is
    made slightly larger than the line that will cover it, so a registration
    error cannot open a gap. The flat's true edge is never visible anyway,
    because the ink is on top of it.

    A miter offset along each vertex's angle bisector, with the spike at a sharp
    corner clamped.
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


def stroke(points, stage="ink", tag=None, closed=False, weight=1.0, lead=None,
           tail=None, smooth=True, per_span=12, hand=1.0, tool=None, nib=None,
           trap=None, **look):
    """One mark. `points` are your decisions; everything else is the hand.

    `tool` picks the instrument and `nib` the weight; a crayon returns several
    overlapping passes rather than one stroke, so this may return a list. `write`
    flattens.

    `stage` says when in the stage sequence the mark was made, and `tag` says
    which object it belongs to. They are independent, and `--only` / `--hide`
    match either. For an object tagged `bike`, `--only bike,frame` renders it at
    every stage and `--only bike,blockin,frame` renders it over the composition
    rough. Tag every mark of a tier-1 object. The stage is still recorded, so
    the stage audit is unaffected.

    Pitfalls:

    - A corner needs `smooth=False`. No interpolating spline passes through a
      corner. Sent as a smooth path, the curve leaves each of your points by a
      wide margin, so the shape is not where its points are. A row of teeth
      measured as a straight-sided block can come back as a lens. Draw it with
      straights, or place a point close in on each side of every corner.
    - `closed=True` closes the path for you. If you repeat the first point as
      well, the spline turns through a zero-length segment, which renders as a
      cusp. A closed stroke carries no taper, because a loop has no ends, and
      its closing side is built like every other side, so three points render
      a triangle.
    - `color=` is a palette name (see `write`). On a stock name the palette
      does not repoint, `fill="solid"` is a pale tint and `fill="fill"` is
      saturated. On any palette name the two are the same colour, its value.
    - A flat is its polygon plus a stroke of that path. `tool="flat"` fills and
      outlines, and with no `size`/`scale` the outline takes tldraw's default,
      roughly 5px each side. On a big flat that is free trapping and invisible.
      On a small one it silently swells the shape: an 11px iris rendered at
      21.5px, and shrinking the polygon changed nothing because the polygon was
      never what rendered. Pin `size`/`scale` on every flat.
    - Flats need `tool="flat"`. At any translucency every overlap shows as a
      seam. Only `flat` fills: every other tool draws a closed path as its
      outline, so a closed `stage="fill"` mark with another tool is refused
      unless it passes `fill=` itself (`fill="none"` for an outline on purpose).

    The style (see `style`) changes only how these points land. A flat
    (`tool="flat"`) has no drift and no run-on: it lands on its points. `hand`
    scales the drift, the run-on and the weight from mark to mark, and on ink and
    correction marks it can leave a small gap at an end and starts the line
    with a hook (fast) or a blob (slow). `handedness` sets which end the line is
    drawn from. `medium` picks the tool when you did not name one. A `tool`,
    `lead` or `tail` you pass always wins.
    """
    explicit = {"tool": tool is not None, "lead": lead is not None, "tail": tail is not None}
    tool = "brush" if tool is None else tool
    lead = 0.18 if lead is None else lead
    tail = 0.22 if tail is None else tail
    if tool == "pen" and (lead, tail) != (0.18, 0.22):
        # the technical pen draws at constant pressure, so a lead or tail would
        # be ignored and a line meant to end in a point would end square
        raise ValueError("stroke: the pen has no taper -- lead/tail do nothing on tool='pen'; "
                         "use tool='brush' for a line that ends in a point")

    # `trap=<px>` grows a closed flat outward so the ink laid over it covers its
    # edge. It is opt-in and not a default, because trapping suits only some
    # flats. It belongs on a body flat, whose edge is meant to be hidden under a
    # contour. It spoils any flat that is a mark in its own right (a vent, an
    # eye, a cast shadow), and applied to every closed flat it swells the
    # interior shapes until they eat the form. `--unfilled` says which flats
    # need it.
    look["authored"] = _origin(points)
    if tool == "flat" and closed and trap and len(points) >= 3:
        points = trap_outward(points, float(trap))

    global _HAND
    _HAND = _hand_for(points, stage, tag)
    styled = _style()
    kit = INSTRUMENTS.get(tool, INSTRUMENTS["brush"])
    loose = 1.0
    if styled:
        loose = _looseness(styled)
        mine = _hand_for(points, stage, tag, 1)   # the style's own draws
        if styled.get("medium") and not explicit["tool"] and stage != "frame":
            tool, adjust = MEDIA[styled["medium"]]
            kit = dict(INSTRUMENTS[tool], **{k: v for k, v in adjust.items() if k != "taper"})
            if adjust.get("taper") is False:
                lead = 0.0 if not explicit["lead"] else lead
                tail = 0.0 if not explicit["tail"] else tail
        if stage != "frame" and tool != "flat":
            points = _pull(points, closed, styled.get("handedness", "right"), float(mine.random()))
    if nib:
        step, thickness = WEIGHTS[nib]
        look.setdefault("size", step)
        look.setdefault("scale", round(thickness * _GAUGE, 3))
    look.setdefault("dash", kit["dash"])
    if tool == "flat":
        look.setdefault("fill", "fill")   # a flat with no fill is an outline
    elif stage == "fill" and closed and "fill" not in look:
        # Only `flat` fills by itself. Any other tool lays the path's outline and
        # leaves the inside bare, so a closed fill-stage mark meant as a solid
        # shape (an eye, a patch) would render as a ring.
        raise ValueError(
            f"stroke: a closed stage='fill' mark with tool={tool!r} renders as an outline, "
            "not a filled shape. Only tool='flat' fills. Use tool='flat' for a region of "
            "colour, or pass fill='none' to say the outline is meant")
    if kit["alpha"] < 1.0:
        look.setdefault("opacity", kit["alpha"])

    flat_points = [tuple(point[:2]) for point in points]
    if closed:
        # a loop has no ends: close the control points, so the closing side is
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
    amount = hand * loose * min(1.9, 0.4 + reach / 700.0)
    if tool == "flat":
        # A flat lands on its points. Drift moved a whole flat 3-5px, which
        # changes the ratio of two bands set side by side (a tyre and its rim)
        # with no gate noticing. The hand shows in the ink, not in the fill.
        amount = 0.0

    # The style's end dynamics, decided once per mark so that every pass of a
    # crayon ends and starts alike. Only open ink marks get them, and only from
    # a hand that is not ruling a line (`hand` > 0).
    gaps, hook, blob = [0.0, 0.0], 0.0, 0.0
    if styled and stage in INKED and not closed and hand > 0 and tool != "flat":
        looseness = float(styled.get("hand", 0.5))
        for end in (0, 1):
            if mine.random() < 0.3 * looseness:
                gaps[end] = 1.0 + 3.0 * float(mine.random())
        # 1 px on a short tight mark up to 3 px on a long loose one
        size = min(3.0, hand * (1.0 + 2.0 * looseness) * min(1.0, 0.4 + reach / 250.0))
        turn = 1.0 if mine.random() < 0.5 else -1.0
        start = float(speed[0])
        if speed.max() < 1e-6 or start >= 0.5:   # a straight line is drawn fast
            hook = size * turn
        elif start <= 0.25:
            blob = 0.12 * size

    marks = []
    for pass_index in range(kit["passes"]):
        laid = _drift(body, speed, amount + kit["spread"] * pass_index)
        if not closed and hand > 0 and tool != "flat":
            drifted = laid
            laid = np.asarray(_run_on(laid, speed, amount), dtype=float)
        pace = speed
        for end, gap in enumerate(gaps):
            if gap:
                # an end that stops short does not also carry past its target
                laid[-end] = drifted[-end]
                laid, pace = _fall_short(laid, pace, gap, at_start=end == 0)
        if hook:
            laid = _hook(laid, abs(hook), math.copysign(1.0, hook))
        # A technical pen has no pressure response: flat z, uniform width. A
        # brush has all of it. `press` scales between those two extremes.
        lively = _pressure(pace, lead, tail,
                           weight * (1.0 + float(_HAND.normal(0, 0.07 * hand * loose))),
                           kit.get("floor", 0.0))
        if blob:
            lively = _blob(lively, laid, blob)
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
# `stroke` is the only mark. There is no ellipse helper, no ruled-line helper and
# no block-in helper, and none should be added. A straight is a stroke with
# `smooth=False`. A block-in chord is a stroke with `smooth=False`. A ruled
# construction line is a stroke with `smooth=False` and the hand turned down.
# It is still drawn.
#
# `frame` below is not a mark. It is the edge of the picture.
#
# A shape computed from a centre and two radii (an ellipse for a head, say) has
# no errors and no information. It is the generic shape, supplied before the
# subject has been looked at, at the stage whose job is to find the particular
# one. A head built that way as a frontal ball on a head turned three quarters
# gives features that each measure within ten pixels and still do not make the
# face. A round form drawn by hand is six or eight points chosen after looking,
# and its errors are where the looking was wrong. If a form is round, say where
# its curve goes, in points.


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


# --- colour -------------------------------------------------------------------
#
# A palette (palette.json) is any number of named colours, each #rrggbb, with
# names you choose: `coat.lit`, `roof`, `sky`. `color=` takes one of them. The
# 13 stock names below are always valid as well: a stage's default look uses
# them, and an older palette repoints them. `background` is the ground and never
# a mark's colour.

STOCK = ("black", "grey", "light-violet", "violet", "blue", "light-blue", "yellow",
         "orange", "green", "light-green", "light-red", "red", "white")
# no comma or plus: names travel through `--ink a,b`, `--value a,b` and parts.json's
# `"value": "a+b"`
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")


def read_palette(path):
    """palette.json as {name: "#rrggbb"}, in file order. Stops on a name the
    tools cannot pass through a list, or a value that is not #rrggbb."""
    with open(path) as handle:
        palette = json.load(handle)
    if not isinstance(palette, dict):
        raise SystemExit(f"palette {path}: want a JSON object of name -> #rrggbb")
    bad = [f"{name!r}: {value!r}" for name, value in palette.items()
           if not _NAME.match(name) or not isinstance(value, str) or not _HEX.match(value)]
    if bad:
        raise SystemExit(f"palette {path}: {', '.join(bad)} -- a name is letters, digits, '.', '_' "
                         "or '-' (starting with a letter or digit), and a value is #rrggbb")
    return palette


def unknown_colours(ops, palette):
    """The failures among the ops' `color=` names: `background`, and any name
    neither the palette nor the stock set holds."""
    used = {op["color"] for op in ops if op.get("op") == "stroke" and "color" in op}
    failures = []
    if "background" in used:
        failures.append("color='background': the ground is not a mark colour. Give the "
                        "paper's colour a name of its own in palette.json")
    missing = sorted(used - set(palette) - set(STOCK) - {"background"})
    if missing:
        names = [name for name in palette if name != "background"]
        failures.append(f"color={', '.join(map(repr, missing))} not in palette.json. Its names are: "
                        f"{', '.join(names) or '(none)'}; the 13 stock names also work")
    return failures


STAGES = ("gesture", "blockin", "contour", "ink")


def audit(ops):
    """The stages, read off the script. Returns (counts, first index per stage,
    list of failures). A failure is a drawing with ink and no gesture, block-in
    or contour stage anywhere in it, or a stage whose first mark comes after the
    first mark of the stage above it. It checks that the stages exist, not that
    each ink mark has a contour under it. On three finished drawings, 26-81% of
    ink strokes had no contour stroke within two line widths, so a per-mark rule
    would refuse ordinary drawings."""
    counts, first = {}, {}
    for index, op in enumerate(ops):
        if op.get("op") != "stroke":
            continue
        stage = op.get("stage", "ink")
        counts[stage] = counts.get(stage, 0) + 1
        first.setdefault(stage, index)
    failures = []
    if counts.get("ink"):
        for stage in STAGES[:-1]:
            if not counts.get(stage):
                failures.append(f"ink with no {stage} stage: the stages were skipped")
        # gesture, then block-in, then ink. The contour must exist but need not
        # come first, because forms drawn in depth order interleave their stages
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
    `at` carries the instruction offset too, so two calls on one line differ,
    while one call reached twice (a loop, a comprehension, an import) does not."""
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
    """Were these marks written by you in the script, or generated?

    Returns (facts, failures). There are three signals, each chosen because
    hand-written work does not trip it. They were measured on six hand-written
    drawings (89 to 498 strokes):

    - a stroke whose call sits in a different file from the script, such as a
      generated section module or a helper library. Hand-written: 0 of 1,674
      strokes.
    - one call site in the script reached more than once (a loop, a
      comprehension, or an `import` of a module that draws). Hand-written: 0.
    - control points that are not written as numbers in the script's own text,
      because they were loaded from JSON, computed from pixels or scaled.
      Hand-written: at least 99.5% are literal (the rest are frame corners
      written as W, H). A drawing whose points come from a skeleton or a trace
      is at 0.2%. The floor is LITERAL_FLOOR.

    None of them can see generated output pasted into the script as literal
    lines, including lines a script wrote by adding an offset to your points.
    That is still a generated drawing, and the rule against it is what forbids
    it, not this check. No sound check exists: hand-typed hatching repeats one
    offset exactly as often as a script does (SKILL.md, "What the checks cannot
    see").
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
    """Flatten the ops, audit the stages, and save them.

    Refuses to write ink into a drawing with no gesture, block-in and contour
    stage. A drawing inked straight off its measurements passes every placement
    check and reads as a diagram. The stages must exist, but no mark is checked
    for a contour under it. Also refuses marks the script did not write: strokes
    generated in another file, stamped by a loop, or whose points were loaded or
    computed rather than written down (see `provenance`). `swatch=True` skips
    both, for a weight swatch or a calibration strip that is not a drawing.

    `color=` takes a name from `palette.json` beside the script, which holds as
    many named colours as the subject has flats; the CLI's `--palette` renders
    each at its value. A name the palette does not hold is refused here, with
    the palette's names. The 13 stock names stay valid (an older palette
    repoints them). `background` is the ground, not a colour: a mark may not use
    it, and a drawing that paints in the paper's own colour gives that colour a
    name of its own.

    The ground has a right answer: measure it off the subject. Everything on the
    ground is judged by its contrast with it, so a wrong ground flattens every
    relationship in the picture at once and no check that compares marks will
    notice. For example, a ground of `#FAF1D2` against a subject wall of
    `#EFE9D1` is eleven levels too light. An object on that wall then differs
    from it by five grey levels where the subject's differ by seventeen, and the
    object fails to separate from what it hangs on.
    """
    flat = []
    for op in ops:
        flat.extend(op) if isinstance(op, list) else flat.append(op)
    counts, _, failures = audit(flat)
    if failures and not swatch:
        raise SystemExit("stages: " + "; ".join(failures) + f"  (stages on the page: {counts})")
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    beside = os.path.dirname(os.path.abspath(main)) if main else None
    found = os.path.join(beside or ".", "palette.json")
    wrong = unknown_colours(flat, read_palette(found) if os.path.exists(found) else {})
    if wrong:
        raise SystemExit("colour: " + "; ".join(wrong))
    if not swatch:
        _, generated = provenance(flat, script_source(flat, beside))
        if generated:
            raise SystemExit("authored: " + "; ".join(generated))
    with open(path, "w") as handle:
        json.dump(flat, handle)
    return path
