#!/usr/bin/env python3
"""The style layer in pen.py, each behaviour checked in both directions.

The style may change only how a point list lands: where its ends fall, which
way it is drawn, how it presses. So each case shows the change happening where
it should and not happening where it should not, and that no style at all
leaves the pen exactly as it was.

    python3 test_style.py
"""
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pen  # noqa: E402

failed = []


def case(name):
    def run(test):
        pen.style(None)
        try:
            test()
            print(f"ok   {name}")
        except Exception as error:  # a failed case is reported, the rest still run
            failed.append(name)
            print(f"FAIL {name}: {type(error).__name__}: {error}")
        finally:
            pen.style(None)
        return test
    return run


# A drawing that uses every instrument, both kinds of path, closed and open
# marks, every stage and a trap. Its ops were written by the pen before the
# style layer existed; with no style.json the pen must still write them.
FIXTURE = """from pen import stroke, frame, write, back, gauge
W, H = 400, 300
gauge(300)
ops = [frame(0, 0, W, H)]
ops.append(stroke([(40, 60), (200, 70), (360, 50)], stage='gesture'))
ops.append(stroke([(300, 40), (120, 260)], stage='blockin', smooth=False))
ops.append(stroke([(80, 80), (320, 80), (320, 220), (80, 220)], stage='blockin', closed=True, smooth=False))
ops.append(stroke([(90, 200), (150, 120), (240, 110), (310, 190)], stage='contour', tag='arch'))
ops.append(stroke([(310, 190), (240, 110), (150, 120), (90, 200)], stage='ink', tag='arch', nib='bold'))
ops.append(stroke([(200, 40), (205, 140), (198, 260)], stage='ink', nib='fine'))
ops.append(stroke([(350, 150), (60, 152)], stage='ink', tool='pen', size='s', scale=0.6))
ops.append(stroke([(100, 100), (140, 90), (180, 130), (150, 170), (110, 160)], stage='ink', closed=True, nib='medium'))
ops.append(stroke([(60, 250), (160, 240), (260, 262)], stage='ink', tool='crayon', nib='heavy'))
ops.append(stroke([(120, 100), (280, 100), (280, 200), (120, 200)], stage='fill', tool='flat', closed=True, trap=2, color='orange', size='s', scale=0.5))
ops.append(stroke([(230, 150), (250, 145), (262, 160)], stage='correct', tool='gouache', color='white'))
ops.append(stroke([(20, 20), (380, 280)], stage='ink', lead=0.3, tail=0.1, hand=0.4))
ops.append(back('fill'))
write('ops.json', ops)
"""
# sha256 of json.dumps(ops, sort_keys=True), from pen.py before the style layer
BEFORE = "6c6fa7f9aa41404248e4b1a9ace157ba705417bbd95a92490603f083640645bf"


def draw(style_text=None):
    """Run the fixture in its own folder. Returns (exit code, ops digest, last
    line of output)."""
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, "draw.py"), "w") as handle:
            handle.write(FIXTURE)
        if style_text is not None:
            with open(os.path.join(folder, "style.json"), "w") as handle:
                handle.write(style_text)
        done = subprocess.run([sys.executable, "draw.py"], cwd=folder, capture_output=True,
                              text=True, env=dict(os.environ, PYTHONPATH=HERE))
        if done.returncode:
            return done.returncode, None, (done.stderr or done.stdout).strip().splitlines()[-1]
        with open(os.path.join(folder, "ops.json")) as handle:
            digest = hashlib.sha256(json.dumps(json.load(handle), sort_keys=True).encode()).hexdigest()
        return 0, digest, ""


def mark(*args, **kwargs):
    """One stroke without its authorship record, which counts calls and so
    differs between any two strokes."""
    op = pen.stroke(*args, **kwargs)
    op.pop("authored")
    return op


def xy(op):
    return [(p[0], p[1]) for p in op["points"]]


@case("no style.json writes the same ops as before the style layer; a style.json changes them")
def _():
    code, digest, said = draw()
    assert code == 0 and digest == BEFORE, (code, digest, said)
    code, digest, said = draw('{"hand": 0.5, "handedness": "right"}')
    assert code == 0 and digest != BEFORE, (code, said)


@case("a style.json in the folder is read on the first stroke and a bad one stops the drawing")
def _():
    code, _, said = draw('{"hand": 0.5, "colour": "red"}')
    assert code != 0 and "unknown style key" in said and "colour" in said, said
    code, _, said = draw('{"hand": 0.5,')
    assert code != 0 and "not valid JSON" in said, said


@case("style validation accepts the documented settings and names what is wrong otherwise")
def _():
    pen.style({"medium": "watercolour+ink", "hand": 1, "finish": "sketch", "handedness": "left",
               "paper": "cold-press", "scan": True, "seed": 3})
    bad = {
        "unknown style key": {"loose": 0.4},
        "medium": {"medium": "crayon"},
        "hand": {"hand": 1.5},
        "hand ": {"hand": True},
        "handedness": {"handedness": "both"},
        "finish": {"finish": "rough"},
        "paper": {"paper": "canvas"},
        "scan": {"scan": "yes"},
        "seed": {"seed": 1.5},
        "JSON object": ["hand", 0.5],
    }
    for words, spec in bad.items():
        try:
            pen.style(spec)
        except ValueError as error:
            assert words.strip() in str(error), (words, str(error))
        else:
            raise AssertionError(f"{spec!r} was accepted")


@case("hand 0.5 draws a construction mark exactly as no style does; hand 1 does not")
def _():
    points = [(40, 60), (200, 75), (360, 50)]          # left to right: no reordering
    plain = mark(points, stage="gesture")
    pen.style({"hand": 0.5})
    assert mark(points, stage="gesture") == plain
    pen.style({"hand": 1.0})
    assert mark(points, stage="gesture") != plain


@case("hand 0 lands the ends closer to their points than hand 1")
def _():
    def offset(looseness):
        pen.style({"hand": looseness})
        miss = []
        for row in range(30):
            y = 20 + row * 9
            aimed = [(30, y), (200, y + 6), (370, y - 4)]
            got = xy(pen.stroke(aimed, stage="ink"))
            miss += [math.dist(got[0], aimed[0]), math.dist(got[-1], aimed[-1])]
        return float(np.mean(miss))
    tight, middle, loose = offset(0.0), offset(0.5), offset(1.0)
    assert tight < middle < loose and loose > 2 * tight, (tight, middle, loose)


@case("a right hand pulls left to right and down; the points stay the same points")
def _():
    def drawn(points, handedness, closed=False):
        pen.style({"handedness": handedness})
        return xy(pen.stroke(points, stage="contour", closed=closed, smooth=False, hand=0.0))

    leftward = [(300, 100), (200, 104), (100, 110)]
    right, left = drawn(leftward, "right"), drawn(leftward, "left")
    assert right[0] == (100, 110) and left[0] == (300, 100), (right[0], left[0])
    assert right == left[::-1] and sorted(right) == sorted(left)
    rightward = leftward[::-1]
    assert drawn(rightward, "right")[0] == (100, 110)          # already the hand's way
    upward = [(200, 260), (204, 150), (198, 40)]
    assert drawn(upward, "right")[0] == (198, 40) and drawn(upward, "left")[0] == (198, 40)

    def clockwise(points):
        xs, ys = np.array([p[0] for p in points]), np.array([p[1] for p in points])
        return float(np.sum(xs * np.roll(ys, -1) - np.roll(xs, -1) * ys)) > 0
    loop = [(100, 100), (200, 100), (150, 180)]                 # clockwise on the page
    assert clockwise(loop) and not clockwise(drawn(loop, "right", closed=True))
    assert sorted(drawn(loop, "right", closed=True)) == sorted(xy(pen.stroke(
        loop, stage="contour", closed=True, smooth=False, hand=0.0)))
    assert not clockwise(drawn(loop[::-1], "right", closed=True))  # left as drawn


@case("the start hook and blob land on ink and correction marks only")
def _():
    pen.style({"hand": 1.0})
    points = [(40, 120), (200, 126), (360, 118)]

    def with_and_without(stage, **extra):
        on = mark(points, stage=stage, **extra)
        kept, pen.INKED = pen.INKED, ()
        try:
            off = mark(points, stage=stage, **extra)
        finally:
            pen.INKED = kept
        return on, off

    for stage in ("ink", "correct"):
        on, off = with_and_without(stage)
        assert on != off, stage
        # subtle: the start moves by at most the 3px hook plus a 4px gap
        assert math.dist(xy(on)[0], xy(off)[0]) <= 7.01, (stage, xy(on)[0], xy(off)[0])
    for stage in ("gesture", "blockin", "contour"):
        on, off = with_and_without(stage)
        assert on == off, stage
    on, off = with_and_without("fill", tool="flat", closed=True)
    assert on == off
    on, off = with_and_without("ink", closed=True)              # a loop has no start
    assert on == off


@case("a hook curls the first pixels off the line and leaves the rest; a blob presses the start")
def _():
    line = np.stack([np.linspace(0, 100, 51), np.zeros(51)], axis=1)
    up, down = pen._hook(line, 2.0, 1.0), pen._hook(line, 2.0, -1.0)
    assert abs(abs(up[0, 1]) - 2.0) < 1e-9 and up[0, 1] == -down[0, 1]
    assert np.array_equal(up[10:], line[10:])                  # past 4 x 2px: untouched
    assert np.array_equal(pen._hook(line, 0.0, 1.0), line)
    press = np.linspace(0.0, 0.5, 51)
    pressed = pen._blob(press, line, 0.3)
    assert pressed[0] > press[0] + 0.25 and abs(pressed[-1] - press[-1]) < 1e-6


@case("a fall-short gap shortens the line at that end by the gap, and nowhere else")
def _():
    line = np.stack([np.linspace(0, 100, 51), np.zeros(51)], axis=1)
    speed = np.zeros(51)
    cut, pace = pen._fall_short(line, speed, 3.0, at_start=False)
    assert len(cut) == len(pace) and abs(cut[-1, 0] - 97.0) < 1e-9 and cut[0, 0] == 0.0
    cut, pace = pen._fall_short(line, speed, 3.0, at_start=True)
    assert len(cut) == len(pace) and abs(cut[0, 0] - 3.0) < 1e-9 and cut[-1, 0] == 100.0
    short = line[:3]                                            # 4px: no room to fall short
    assert np.array_equal(pen._fall_short(short, speed[:3], 3.0, at_start=False)[0], short)


@case("the medium picks the instrument only when the stroke names none")
def _():
    points = [(40, 120), (200, 126), (360, 118)]
    pen.style({"medium": "marker"})
    marker = pen.stroke(points, stage="ink")
    assert marker["dash"] == "solid" and marker["opacity"] == 0.75, marker["dash"]
    named = pen.stroke(points, stage="ink", tool="brush")
    assert named["dash"] == "draw" and "opacity" not in named
    pen.style({"medium": "pencil"})
    assert pen.stroke(points, stage="ink")["opacity"] == 0.85
    pen.style({"medium": "gouache"})
    painted = pen.stroke(points, stage="ink")
    assert min(p[2] for p in painted["points"]) > 0.2          # body colour has width at its ends
    pen.style({"medium": "gouache"})
    assert pen.stroke(points, stage="frame", hand=0.0)["dash"] == "draw"


@case("pen.style reads a path, and seed() in the script wins over the style's seed")
def _():
    points = [(40, 60), (200, 75), (360, 50)]
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "style.json")
        with open(path, "w") as handle:
            json.dump({"hand": 0.5, "seed": 5}, handle)
        kept = pen._SEED, pen._SEED_GIVEN
        try:
            pen.style(path)
            assert pen._SEED == 5
            five = mark(points, stage="gesture")
            pen.seed(11)
            pen.style(path)
            assert pen._SEED == 11 and mark(points, stage="gesture") != five
        finally:
            pen._SEED, pen._SEED_GIVEN = kept


sys.exit(1 if failed else 0)
