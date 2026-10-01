#!/usr/bin/env python3
"""finish.py and the harness flags it relies on, each checked both ways.

Every case shows the behaviour holds, and also that the check would catch it
failing, so a case cannot pass by measuring nothing. The images are tiny and
synthetic; the harness cases render through node and take a few seconds.

    python3 test_finish.py
"""
import contextlib
import io
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

import finish  # noqa: E402

failed = []
STYLE = {"medium": "watercolour+ink", "hand": 0.5, "finish": "sketch", "handedness": "right",
         "paper": "cold-press", "scan": True, "seed": 11}
DARK = 0.35            # luminance below this counts as a dark pixel
REACH = 5              # how far (px) a dark pixel may sit from its source: tilt, blur, soak


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


def drawing():
    """Off-white ground, a blue flat, a red flat, black lines over their edges."""
    image = Image.new("RGB", (320, 240), "#fbfaf6")
    pen = ImageDraw.Draw(image)
    pen.rectangle([40, 40, 170, 200], fill="#5b7fa8")
    pen.ellipse([190, 90, 290, 190], fill="#c4553b")
    pen.rectangle([40, 40, 170, 200], outline="#141210", width=5)
    pen.ellipse([190, 90, 290, 190], outline="#141210", width=4)
    pen.line([20, 210, 300, 206], fill="#141210", width=3)
    return np.asarray(image, dtype=float) / 255


def construction():
    """Stage-coloured bands, as the harness renders gesture and block-in."""
    image = Image.new("RGB", (320, 240), "#ffffff")
    pen = ImageDraw.Draw(image)
    pen.line([100, 30, 110, 215], fill="#4465e9", width=9)
    pen.rectangle([180, 80, 300, 200], outline="#ae3ec9", width=6)
    pen.line([60, 20, 260, 20], fill="#ae3ec9", width=6)     # over bare paper only
    return np.asarray(image, dtype=float) / 255


def dark(image):
    return finish.luminance(image) < DARK


def invented(result, *sources):
    """Dark pixels of `result` with no dark source pixel within REACH."""
    allowed = np.zeros(result.shape[:2], bool)
    for source in sources:
        allowed |= finish.luminance(source) < 0.6
    return dark(result) & ~ndimage.binary_dilation(allowed, iterations=REACH)


def with_style(**changes):
    return {**STYLE, **changes}


@case("no dark pixel is invented, for every medium and paper; a planted one is caught")
def _():
    art, sketch = drawing(), construction()
    for medium in finish.MEDIA:
        for paper in finish.PAPERS:
            result = finish.finish(with_style(medium=medium, paper=paper), art, sketch)
            extra = invented(result, art, sketch).sum()
            assert extra == 0, f"{medium} on {paper}: {extra} dark pixels with no source"
            # and the ink is still there: a finish that washed everything out would pass the above
            kept = (dark(result) & dark(art)).sum() / dark(art).sum()
            assert medium == "pencil" or kept > 0.6, f"{medium} on {paper}: only {kept:.0%} of the ink stays dark"
    planted = finish.finish(with_style(scan=False), art, sketch)
    planted[10:16, 290:300] = 0.05
    assert invented(planted, art, sketch).sum() > 0, "the check misses a dark mark on bare paper"


@case("a flat lighter than a full-bleed ground keeps its colour; the ground itself is not the paper")
def _():
    # a mid-tone ground covering most of the picture, with a pale sky band and an ink line:
    # the commonest colour is paint, not paper, and the sky must not sink into it
    image = np.zeros((120, 160, 3))
    image[:] = (186 / 255, 180 / 255, 125 / 255)
    image[:30] = (241 / 255, 202 / 255, 132 / 255)
    image[60:64, 20:140] = (38 / 255, 21 / 255, 19 / 255)
    style = dict(STYLE, paper="none", scan=False, finish="clean")
    for medium in ("watercolour+ink", "ink-pen", "marker", "gouache", "pencil", "brush-pen"):
        out = finish.finish(dict(style, medium=medium), image)
        sky, field = out[5:25, 40:120].mean(axis=(0, 1)), out[80:110, 40:120].mean(axis=(0, 1))
        assert np.abs(sky - image[10, 80]).max() < 0.12, (medium, sky * 255)
        assert sky.mean() > field.mean() + 0.05, (medium, sky * 255, field * 255)
    # the check can fail: a sky that sank to the ground's colour is caught
    sunk = image.copy(); sunk[:30] = image[100, 80]
    assert np.abs(sunk[5:25, 40:120].mean(axis=(0, 1)) - image[10, 80]).max() >= 0.12


@case("pencil turns ink to graphite grey; ink-pen keeps it near black")
def _():
    art = drawing()
    line = dark(art)
    pencil = finish.finish(with_style(medium="pencil", paper="none", scan=False, finish="clean"), art)
    pen = finish.finish(with_style(medium="ink-pen", paper="none", scan=False, finish="clean"), art)
    assert finish.luminance(pencil)[line].mean() > 0.25, finish.luminance(pencil)[line].mean()
    assert finish.luminance(pen)[line].mean() < 0.15, finish.luminance(pen)[line].mean()


@case("paper none and scan false is near identity; a paper and a scan are not")
def _():
    art = drawing()
    plain = finish.finish(with_style(medium="ink-pen", paper="none", scan=False, finish="clean"), art)
    change = np.abs(plain - art).max(axis=2)
    assert change.mean() < 0.01, change.mean()
    # the ink soaks a pixel or so into the paper, and nothing else changes
    near_ink = ndimage.binary_dilation(finish.luminance(art) < 0.6, iterations=2)
    assert change[~near_ink].max() < 0.02, change[~near_ink].max()
    scanned = finish.finish(with_style(medium="ink-pen", paper="sketchbook", scan=True, finish="clean"), art)
    assert np.abs(scanned - art).mean() > 0.02, np.abs(scanned - art).mean()


@case("the same seed gives the same file; another seed does not")
def _():
    with tempfile.TemporaryDirectory() as folder:
        Image.fromarray(np.round(drawing() * 255).astype(np.uint8)).save(f"{folder}/drawing.png")
        Image.fromarray(np.round(construction() * 255).astype(np.uint8)).save(f"{folder}/construction.png")

        def run(seed, out):
            with open(f"{folder}/style.json", "w") as handle:
                json.dump(with_style(seed=seed), handle)
            with contextlib.redirect_stdout(io.StringIO()):
                finish.main(["--style", f"{folder}/style.json", "--drawing", f"{folder}/drawing.png",
                             "--construction", f"{folder}/construction.png", "--out", f"{folder}/{out}"])
            with open(f"{folder}/{out}", "rb") as handle:
                return handle.read()

        assert run(11, "a.png") == run(11, "b.png"), "same seed, different bytes"
        assert run(11, "a.png") != run(12, "c.png"), "a different seed changed nothing"


@case("a bad style value stops the run and names the key; a good style runs")
def _():
    bad = {
        "medium": with_style(medium="crayon"),
        "paper": with_style(paper="vellum"),
        "finish": with_style(finish="rough"),
        "scan": with_style(scan="yes"),
        "seed": with_style(seed=1.5),
        "hand": with_style(hand=1.4),
        "handedness": with_style(handedness="both"),
        "unknown": with_style(texture="on"),
        "missing": {key: value for key, value in STYLE.items() if key != "paper"},
    }
    with tempfile.TemporaryDirectory() as folder:
        path = f"{folder}/style.json"
        for key, style in bad.items():
            with open(path, "w") as handle:
                json.dump(style, handle)
            try:
                finish.read_style(path)
            except SystemExit as stop:
                word = "paper" if key == "missing" else ("texture" if key == "unknown" else key)
                assert word in str(stop), f"{key}: the message does not say what is wrong: {stop}"
            else:
                raise AssertionError(f"{key}: a bad style was accepted")
        with open(path, "w") as handle:
            json.dump(STYLE, handle)
        assert finish.read_style(path) == STYLE
    try:
        finish.finish(with_style(finish="sketch"), drawing(), None)
    except SystemExit as stop:
        assert "construction" in str(stop)
    else:
        raise AssertionError("a sketch finish ran with no construction render")


@case("sketch construction shows through watercolour flats, and only on paper for gouache")
def _():
    art, sketch = drawing(), construction()
    # the gesture line crosses the blue flat at x 100..110: average the flat's
    # rows into one profile across the line, and see whether the line dips it
    def dip(medium, finish_kind):
        result = finish.finish(with_style(medium=medium, finish=finish_kind, paper="none", scan=False), art,
                               sketch if finish_kind == "sketch" else None)
        profile = finish.luminance(result)[70:180, 85:130].mean(axis=0)
        return np.median(profile) - profile.min()

    for medium, shows in (("watercolour+ink", True), ("marker", True), ("gouache", False)):
        assert (dip(medium, "sketch") > 0.04) == shows, f"{medium}: the line under the flat dips it by {dip(medium, 'sketch'):.3f}"
        assert dip(medium, "clean") < 0.04, f"{medium}: a clean finish shows a line: {dip(medium, 'clean'):.3f}"

    def darkening(medium, finish_kind):
        result = finish.finish(with_style(medium=medium, finish=finish_kind, paper="none", scan=False), art,
                               sketch if finish_kind == "sketch" else None)
        return finish.luminance(result)

    # and on bare paper both show it
    for medium in ("watercolour+ink", "gouache"):
        light = darkening(medium, "sketch")
        assert light[17:24, 120:170].min() < light[28:36, 120:170].min() - 0.05, medium


def harness(folder, ops, *flags):
    doc = f"{folder}/doc.json"
    if os.path.exists(doc):
        os.remove(doc)
    with open(f"{folder}/ops.json", "w") as handle:
        json.dump(ops, handle)
    out = f"{folder}/out.png"
    done = subprocess.run(["node", f"{HERE}/harness/cli.mjs", doc, "--ops", f"{folder}/ops.json",
                           "--png", out, "--padding", "0", *flags], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return np.asarray(Image.open(out).convert("RGB"), dtype=float) / 255


def mark(stage, points, **look):
    return {"op": "stroke", "stage": stage, "points": points, **look}


HARNESS_OPS = [
    # a frame needs points all along its sides, as pen.frame gives it, or the
    # smoothing rounds its corners in and the render bounds move with it
    mark("frame", [[x, 0] for x in range(0, 200, 10)] + [[200, y] for y in range(0, 120, 10)]
         + [[x, 120] for x in range(200, 0, -10)] + [[0, y] for y in range(120, 0, -10)],
         closed=True, color="grey", size="s", opacity=0.03, dash="solid"),
    mark("fill", [[40, 30], [120, 30], [120, 90], [40, 90]], closed=True, fill="fill",
         color="orange", size="s", dash="solid"),
    mark("ink", [[30, 60, 0.5], [60, 55, 0.6], [100, 64, 0.6], [150, 58, 0.5], [180, 62, 0.4]],
         color="black", size="m", dash="draw"),
    {"op": "back", "stage": "fill"},
]


def centre(mask):
    rows, cols = np.nonzero(mask)
    return np.array([cols.mean(), rows.mean()])


def corner(mask):
    rows, cols = np.nonzero(mask)
    return np.array([cols.min(), rows.min()])


def orange(image):
    return (image[..., 0] > 0.8) & (image[..., 1] > 0.4) & (image[..., 2] < 0.3)


@case("--offset moves the fill and not the ink; without it nothing moves")
def _():
    with tempfile.TemporaryDirectory() as folder:
        still = harness(folder, HARNESS_OPS)
        again = harness(folder, HARNESS_OPS)
        moved = harness(folder, HARNESS_OPS, "--offset", "fill:6,4")
        ratio = still.shape[1] / 200
        assert np.array_equal(still, again), "two plain renders differ"
        # the fill's top-left corner: the ink runs through its middle and hides the rest
        shift = corner(orange(moved)) - corner(orange(still))
        assert np.allclose(shift, [6 * ratio, 4 * ratio], atol=1.0), shift
        ink_shift = centre(dark(moved)) - centre(dark(still))
        assert np.allclose(ink_shift, 0, atol=0.5), ink_shift
        # the moved fill stays under the ink: where the line crosses it, it is still dark
        crossing = dark(still) & orange(np.roll(still, (int(4 * ratio), int(6 * ratio)), axis=(0, 1)))
        assert dark(moved)[crossing].mean() > 0.95
        try:
            harness(folder, HARNESS_OPS, "--offset", "fill:6")
        except AssertionError as error:
            assert "STAGE:dx,dy" in str(error)
        else:
            raise AssertionError("a malformed --offset was accepted")


@case("--streamline 0.62 is tldraw's own smoothing for a pen line; a lower value changes it")
def _():
    # 0.62 is the value tldraw fixes for a pen stroke drawn with dash "draw"; a
    # solid stroke uses another, so the comparison takes the ink and frame alone
    lines = [op for op in HARNESS_OPS if op.get("stage") in ("frame", "ink")]
    with tempfile.TemporaryDirectory() as folder:
        stock = harness(folder, lines)
        same = harness(folder, lines, "--streamline", "0.62")
        loose = harness(folder, lines, "--streamline", "0.1")
        assert np.array_equal(stock, same), np.abs(stock - same).max()
        assert np.abs(stock - loose).max() > 0.2, "--streamline 0.1 changed nothing"
        try:
            harness(folder, lines, "--streamline", "2")
        except AssertionError as error:
            assert "0..1" in str(error)
        else:
            raise AssertionError("--streamline 2 was accepted")


sys.exit(1 if failed else 0)
