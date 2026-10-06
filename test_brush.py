#!/usr/bin/env python3
"""brush.py, each behaviour checked both ways.

Every case shows the behaviour holds, and also that the check would catch it
failing, so a case cannot pass by measuring nothing. The ops are small and
synthetic. The registration case renders drawing.png through the harness
(node), as build.sh does, and takes a few seconds.

    python3 test_brush.py
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import brush  # noqa: E402
import finish  # noqa: E402

failed = []
STYLE = {"medium": "ink-pen", "hand": 0.5, "finish": "clean", "handedness": "right",
         "paper": "none", "scan": False, "seed": 7, "renderer": "brush"}
NEAR = 3        # px a brushed dark pixel may sit from a tldraw dark pixel
EDGE = 4        # px a brushed mark may reach past its stroke's geometric footprint


def case(name):
    def run(test):
        try:
            test()
            print(f"ok   {name}")
        except Exception as error:  # a failed case is reported, the rest still run
            failed.append(name)
            print(f"FAIL {name}: {type(error).__name__}: {error}")
        return test
    return run


def mark(stage, points, **look):
    return {"op": "stroke", "stage": stage, "points": points, **look}


def frame(width, height):
    edge = ([[x, 0] for x in range(0, width, 10)] + [[width, y] for y in range(0, height, 10)]
            + [[x, height] for x in range(width, 0, -10)] + [[0, y] for y in range(height, 0, -10)])
    return mark("frame", edge, closed=True, color="grey", size="s", opacity=0.03, dash="solid")


def curve(x0, x1, y, bend, count=40, swell=True):
    """An open line with pressure that rises and falls, as pen.py writes one."""
    t = np.linspace(0, 1, count)
    xs = x0 + (x1 - x0) * t
    ys = y + bend * np.sin(np.pi * t)
    zs = 0.3 + 0.5 * np.sin(np.pi * t) if swell else np.full(count, 0.5)
    return [[round(float(a), 2), round(float(b), 2), round(float(c), 3)] for a, b, c in zip(xs, ys, zs)]


def box(x0, y0, x1, y1, step=4.0):
    """A rectangle's outline with a point every `step` units, as pen.py lays a
    straight-sided flat: with only its corners, the streamline cuts them off."""
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    points = []
    for (ax, ay), (bx, by) in zip(corners, corners[1:]):
        count = max(int(np.hypot(bx - ax, by - ay) / step), 1)
        points += [[round(ax + (bx - ax) * i / count, 2), round(ay + (by - ay) * i / count, 2)] for i in range(count)]
    return points


def ring(cx, cy, rx, ry, count=48):
    angle = np.linspace(0, 2 * np.pi, count, endpoint=False)
    return [[round(float(cx + rx * np.cos(a)), 2), round(float(cy + ry * np.sin(a)), 2)] for a in angle]


SCENE = [
    frame(240, 160),
    mark("fill", box(30, 30, 120, 110), closed=True, fill="fill",
         color="orange", size="s", scale=0.5, dash="solid"),
    mark("fill", ring(170, 70, 40, 30), closed=True, fill="fill", color="light-blue", size="s",
         scale=0.5, dash="solid"),
    mark("ink", curve(20, 220, 130, 12), size="m", dash="draw"),
    mark("ink", curve(40, 200, 20, -8, swell=False), size="s", scale=1.4, dash="solid"),
    mark("ink", ring(170, 70, 40, 30), closed=True, size="m", dash="draw"),
    mark("blockin", curve(10, 230, 80, 30), size="s", dash="solid"),   # hidden, as drawing.png hides it
]


def render(ops, **style):
    return brush.render(ops, dict(STYLE, **style), scale=1.0)


def harness(folder, ops):
    doc = f"{folder}/doc.json"
    with open(f"{folder}/ops.json", "w") as handle:
        json.dump(ops, handle)
    out = f"{folder}/drawing.png"
    done = subprocess.run(["node", f"{HERE}/harness/cli.mjs", doc, "--ops", f"{folder}/ops.json", "--png", out,
                           "--padding", "0", "--hide", ",".join(brush.DRAWING_HIDES)],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return np.asarray(Image.open(out).convert("RGB"), dtype=float) / 255


def dark(image, level=0.35):
    return finish.luminance(image) < level


def stray(result, reference):
    """Dark pixels of `result` with no dark pixel of `reference` within NEAR."""
    return dark(result) & ~ndimage.binary_dilation(dark(reference, 0.5), iterations=NEAR)


def footprint(ops, shape, ratio):
    """Every pixel some visible stroke covers by its geometry: a line's centre
    path widened by its largest radius, a flat's polygon widened by its outline,
    each grown by EDGE. Worked out here from the ops, not from brush's dabs."""
    covered = Image.new("L", shape[::-1], 0)
    pen = ImageDraw.Draw(covered)
    for shape_op in brush.stack(ops):
        if not brush.visible(shape_op, set(brush.DRAWING_HIDES), set()):
            continue
        raw = np.asarray(shape_op["points"], dtype=float)
        points = [tuple(p) for p in raw[:, :2] * ratio]
        pressure = raw[:, 2] if raw.shape[1] > 2 else np.full(len(raw), 0.5)
        radius = float(brush.radius_px(shape_op, pressure, ratio).max())
        if shape_op.get("closed"):
            if shape_op.get("fill", "none") != "none":
                pen.polygon(points, fill=1)
            points = points + points[:1]
        pen.line(points, fill=1, width=int(2 * radius * 1.35) + 1, joint="curve")
        for x, y in points:
            pen.ellipse([x - radius * 1.35, y - radius * 1.35, x + radius * 1.35, y + radius * 1.35], fill=1)
    return ndimage.binary_dilation(np.asarray(covered, dtype=bool), iterations=EDGE)


@case("registration: brush.png's dark pixels sit within a few px of drawing.png's, in every medium; a shifted one is caught")
def _():
    with tempfile.TemporaryDirectory() as folder:
        drawn = harness(folder, SCENE)
    for medium in brush.MEDIA:
        laid = render(SCENE, medium=medium)
        assert laid.shape == drawn.shape, (medium, laid.shape, drawn.shape)
        extra = stray(laid, drawn).sum()
        assert extra <= 0.002 * dark(laid).sum(), f"{medium}: {extra} dark pixels off the tldraw lines"
        # and the lines are there: most of tldraw's dark pixels have a brushed one close by
        # graphite is grey however hard it is pressed, so a pencil line counts at a lighter level
        laid_dark = dark(laid, 0.8 if medium == "pencil" else 0.5)
        found = (dark(drawn) & ndimage.binary_dilation(laid_dark, iterations=NEAR)).sum() / dark(drawn).sum()
        assert found > 0.9, f"{medium}: only {found:.0%} of the tldraw ink is laid"
    shifted = np.roll(render(SCENE), 9, axis=1)
    assert stray(shifted, drawn).sum() > 0.05 * dark(shifted).sum(), "the check misses a line 9px off"


@case("occlusion: a flat written after a line covers it, written before it does not; `back` sends it under")
def _():
    line = mark("ink", curve(20, 220, 70, 0, swell=False), size="l", dash="draw")
    flat = mark("fill", box(80, 40, 160, 100), closed=True, fill="fill",
                color="yellow", size="s", scale=0.5, dash="solid")
    under = (slice(134, 146), slice(200, 280))   # the line's middle (y 70 = 140px), inside the flat
    for medium in ("ink-pen", "brush-pen", "gouache", "watercolour+ink"):
        over = render([frame(240, 160), line, flat], medium=medium)
        assert not dark(over)[under].any(), f"{medium}: the near flat lets the line through"
        before = render([frame(240, 160), flat, line], medium=medium)
        assert dark(before)[under].mean() > 0.3, f"{medium}: the line written last is not on top"
        sent = render([frame(240, 160), line, flat, {"op": "back", "stage": "fill"}], medium=medium)
        assert dark(sent)[under].mean() > 0.3, f"{medium}: `back` did not send the flat under the line"
    # the check can fail: a renderer that lays every flat first would be caught here
    reordered = render([frame(240, 160), flat, line])
    assert dark(reordered)[under].any()


@case("no mark outside any stroke's footprint, in every medium; a planted mark is caught")
def _():
    for medium in brush.MEDIA:
        laid = render(SCENE, medium=medium)
        ground = brush.colours(None)[1]
        marked = np.abs(laid - ground).max(axis=2) > 0.03
        outside = marked & ~footprint(SCENE, laid.shape[:2], brush.RATIO)
        assert outside.sum() == 0, f"{medium}: {outside.sum()} marked pixels outside every footprint"
    planted = render(SCENE)
    planted[300:306, 20:26] = 0.2      # bare paper, under no stroke
    marked = np.abs(planted - brush.colours(None)[1]).max(axis=2) > 0.03
    assert (marked & ~footprint(SCENE, planted.shape[:2], brush.RATIO)).sum() > 0, "the check misses a planted mark"


@case("hidden stages stay hidden: the block-in line drawn under the scene leaves no mark")
def _():
    bare = render(SCENE[:-1])
    full = render(SCENE)
    assert np.array_equal(bare, full), "a hidden stage changed the picture"
    shown = brush.render(SCENE, STYLE, hide=(), scale=1.0)
    assert not np.array_equal(bare, shown), "the check cannot see a block-in line at all"


@case("deterministic by seed: the same seed gives the same pixels, another seed different ones")
def _():
    for medium in ("ink-pen", "brush-pen", "gouache", "pencil", "marker"):
        first, again = render(SCENE, medium=medium), render(SCENE, medium=medium)
        assert np.array_equal(first, again), f"{medium}: two renders with one seed differ"
        other = render(SCENE, medium=medium, seed=8)
        assert np.abs(first - other).max() > 0.02, f"{medium}: the seed changes nothing"


@case("the line has living weight: its width varies along a stroke of even pressure; an even line's does not")
def _():
    path = curve(20, 220, 80, 25, swell=False)
    straight = [frame(240, 160), mark("ink", path, size="m", scale=1.4, dash="solid")]
    # the same path as an even vector line, as tldraw draws a solid stroke
    even = Image.new("L", (480, 320), 0)
    centre = [tuple(p) for p in np.asarray(brush.streamlined(path, brush.STREAMLINE))[:, :2] * 2]
    ImageDraw.Draw(even).line(centre, fill=255, width=13, joint="curve")
    reference = (np.asarray(even) > 127)[:, 80:400].sum(axis=0).astype(float)

    def spread(widths):
        ratio = widths / reference          # per column, so the curve's slope cancels
        return ratio.std() / ratio.mean()
    for medium in ("ink-pen", "brush-pen", "gouache"):
        laid = dark(render(straight, medium=medium), 0.5)[:, 80:400].sum(axis=0)
        assert spread(laid) > 0.04, f"{medium}: width varies only {spread(laid):.1%} along the line"
    # the check can fail: the even line itself measures no variation
    assert spread(reference) < 0.01, spread(reference)


@case("a flat shows its brush: passes vary its colour, where tldraw's flat is one value")
def _():
    big = [frame(240, 160), mark("fill", box(20, 20, 220, 140), closed=True,
                                  fill="fill", color="blue", size="s", scale=0.5, dash="solid")]
    for medium in ("gouache", "ink-pen", "marker"):
        inside = render(big, medium=medium)[80:240, 80:400]
        spread = finish.luminance(inside).std()
        assert 0.004 < spread < 0.08, f"{medium}: the flat's value spread is {spread:.4f}"
    flat = np.ones((160, 320, 3)) * brush.hex_rgb(brush.STOCK["blue"][2])
    assert finish.luminance(flat).std() < 0.004


@case("style: renderer must be tldraw or brush; finish.py leaves a brush render's marks as they are")
def _():
    with tempfile.TemporaryDirectory() as folder:
        path = f"{folder}/style.json"
        with open(path, "w") as handle:
            json.dump(dict(STYLE, renderer="skia"), handle)
        try:
            finish.read_style(path)
            raise AssertionError("renderer 'skia' was accepted")
        except SystemExit as error:
            assert "renderer" in str(error), error
        with open(path, "w") as handle:
            json.dump(STYLE, handle)
        assert finish.read_style(path)["renderer"] == "brush"
    laid = render(SCENE)
    kept = finish.finish(dict(STYLE, paper="none", scan=False), laid)
    assert np.abs(kept - laid).max() < 1e-9, "finish.py re-treated a brush render with no paper"
    treated = finish.finish(dict(STYLE, renderer="tldraw", paper="none", scan=False), laid)
    assert np.abs(treated - laid).max() > 0.01, "the check cannot see the medium treatment"


@case("CLI: --like takes drawing.png's size and scale; a size the frame cannot make is refused")
def _():
    with tempfile.TemporaryDirectory() as folder:
        with open(f"{folder}/ops.json", "w") as handle:
            json.dump(SCENE, handle)
        with open(f"{folder}/style.json", "w") as handle:
            json.dump(STYLE, handle)
        Image.new("RGB", (240, 160), "white").save(f"{folder}/like.png")   # --scale 0.5
        args = ["--ops", f"{folder}/ops.json", "--style", f"{folder}/style.json", "--out", f"{folder}/brush.png"]
        brush.main(args + ["--like", f"{folder}/like.png"])
        assert Image.open(f"{folder}/brush.png").size == (240, 160)
        Image.new("RGB", (240, 170), "white").save(f"{folder}/odd.png")
        try:
            brush.main(args + ["--like", f"{folder}/odd.png"])
            raise AssertionError("a drawing.png of another shape was accepted")
        except SystemExit as error:
            assert "frame renders" in str(error), error


sys.exit(1 if failed else 0)
