#!/usr/bin/env python3
"""The measuring tools and the gates, each held against a case it once got wrong.

Every case here is a fault a drawer hit on a real panel: a tool that crashed, a
number that could not be read, a gate that passed a wrong result or buried a
right one in noise. Each is rebuilt on a tiny synthetic image or op list, so the
test says what the tool must do without shipping anyone's drawing.

    python3 test_tools.py
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check  # noqa: E402
from trace import line_width  # noqa: E402

PALETTE = {"background": "#f9f2d5", "black": "#0a0806", "orange": "#db8106"}
failed = []


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


def tool(*args, cwd):
    done = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def panel(folder, size=(400, 300)):
    """Cream ground, an orange block with a black outline 6px wide."""
    image = Image.new("RGB", size, PALETTE["background"])
    pen = ImageDraw.Draw(image)
    pen.rectangle([120, 80, 280, 220], fill=PALETTE["orange"], outline=PALETTE["black"], width=6)
    image.save(os.path.join(folder, "subject.png"))
    with open(os.path.join(folder, "palette.json"), "w") as handle:
        json.dump(PALETTE, handle)
    return image


@case("crop.py stores its corner; trace.py uses it and refuses a box corner as offset")
def _():
    with tempfile.TemporaryDirectory() as folder:
        panel(folder)
        code, said = tool(f"{HERE}/crop.py", "subject.png", "120,80,160,140", "meas/block.png", cwd=folder)
        assert code == 0, said
        code, said = tool(f"{HERE}/trace.py", "meas/block.png", "palette.json", "--line", "8",
                          "--out", "meas/block.json", cwd=folder)
        assert code == 0, said
        orange = [r for r in json.load(open(f"{folder}/meas/block.json")) if r["colour"] == "orange"]
        x, y = orange[0]["box"][:2]
        assert abs(x - 123) <= 3 and abs(y - 83) <= 3, orange[0]["box"]   # panel coordinates
        code, said = tool(f"{HERE}/trace.py", "meas/block.png", "palette.json", "--offset", "120,80",
                          "--out", "x.json", cwd=folder)
        assert code != 0 and "disagrees" in said, said


@case("trace.py --measure-line reads a 6px line as 6, and refuses an unknown palette name")
def _():
    with tempfile.TemporaryDirectory() as folder:
        panel(folder)
        code, said = tool(f"{HERE}/trace.py", "subject.png", "palette.json", "--measure-line", cwd=folder)
        assert code == 0 and "p90 6" in said, said
        with open(f"{folder}/bad.json", "w") as handle:
            json.dump({"background": "#ffffff", "bleu": "#000000"}, handle)
        code, said = tool(f"{HERE}/trace.py", "subject.png", "bad.json", cwd=folder)
        assert code != 0 and "light-violet" in said, said


@case("--weights runs without --ref and names each rung by its position")
def _():
    with tempfile.TemporaryDirectory() as folder:
        image = Image.new("RGB", (200, 60), "white")
        pen = ImageDraw.Draw(image)
        for x, width in ((20, 3), (80, 9), (150, 5)):
            pen.rectangle([x, 5, x + width - 1, 55], fill="black")
        image.save(f"{folder}/ladder.png")
        code, said = tool(f"{HERE}/check.py", "ladder.png", "--weights", "30", cwd=folder)
        assert code == 0, said
        assert "3@21  9@84  5@152" in said, said


@case("--paper takes #hex and R,G,B alike")
def _():
    assert check.colour("#2b6cff") == check.colour("43,108,255") == (43, 108, 255)


@case("--unfilled reads the object off the subject's ground, bareness off the render's paper")
def _():
    subject = Image.new("RGB", (200, 200), PALETTE["background"])
    ImageDraw.Draw(subject).rectangle([50, 50, 150, 150], fill=PALETTE["orange"])
    drawing = Image.new("RGB", (200, 200), (0, 255, 102))          # a check copy's paper
    ImageDraw.Draw(drawing).rectangle([50, 50, 150, 110], fill=PALETTE["orange"])  # short by 40
    found = check.unfilled(drawing, subject, (0, 255, 102), check.colour(PALETTE["background"]))
    assert found == 1, found   # the one real bay, not the whole ground


@case("--masses keeps the figure on a drawing that is mostly ground, at every level count")
def _():
    subject = Image.new("RGB", (600, 600), PALETTE["background"])
    pen = ImageDraw.Draw(subject)
    pen.rectangle([200, 150, 400, 450], fill=PALETTE["orange"], outline=PALETTE["black"], width=5)
    drawing = Image.new("RGB", (600, 600), PALETTE["background"])
    ImageDraw.Draw(drawing).rectangle([200, 150, 400, 450], fill=PALETTE["orange"])  # no ink yet
    for colours in (2, 3, 4, 5):
        sheet = np.asarray(check.masses(drawing, subject, colours=colours))
        right = sheet[40:, sheet.shape[1] // 2 + 20:-20]
        assert len(np.unique(right.reshape(-1, 3), axis=0)) >= 2, f"blank at {colours}"


@case("--ranking reads the entry's tier and names a part louder than the focus tier")
def _():
    subject = Image.new("L", (300, 100), 200)
    pen = ImageDraw.Draw(subject)
    pen.rectangle([0, 0, 99, 99], fill=0)            # the focus shouts in the subject
    pen.rectangle([200, 0, 299, 99], fill=150)
    drawing = subject.copy()
    ImageDraw.Draw(drawing).rectangle([0, 0, 99, 99], fill=170)       # focus gone quiet
    ImageDraw.Draw(drawing).rectangle([200, 0, 249, 99], fill=0)      # a tier-3 part shouts
    inventory = {"focus": {"box": [0, 0, 100, 100], "tier": 1, "shape": "", "rel": ""},
                 "prop": {"box": [200, 0, 100, 100], "tier": 3, "shape": "", "rel": ""}}
    rows = {row[0]: row for row in check.ranking(drawing.convert("RGB"), subject.convert("RGB"),
                                                 inventory)}
    assert rows["focus"][1] == "1" and rows["prop"][1] == "3", rows


@case("--census gives no verdict where it cannot count the subject, and fails a real cull")
def _():
    with tempfile.TemporaryDirectory() as folder:
        subject = Image.new("RGB", (300, 100), PALETTE["background"])
        pen = ImageDraw.Draw(subject)
        for x in (20, 80, 140, 200):
            pen.ellipse([x, 30, x + 30, 60], fill=PALETTE["black"])
        drawing = subject.copy()
        ImageDraw.Draw(drawing).rectangle([190, 20, 240, 70], fill=PALETTE["background"])
        subject.save(f"{folder}/subject.png")
        drawing.save(f"{folder}/drawing.png")
        with open(f"{folder}/palette.json", "w") as handle:
            json.dump(PALETTE, handle)
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump({"drops": {"box": [0, 0, 300, 100], "count": 4, "value": "black"},
                       "miscount": {"box": [0, 0, 300, 100], "count": 6, "value": "black"}}, handle)
        code, said = tool(f"{HERE}/check.py", "drawing.png", "--ref", "subject.png",
                          "--census", "parts.json", cwd=folder)
        assert code == 1 and "FAIL culled" in said and "UNCHECKED" in said, said


@case("--census counts thick forms, not thin ramp specks of the same value")
def _():
    with tempfile.TemporaryDirectory() as folder:
        subject = Image.new("RGB", (1200, 800), PALETTE["background"])
        pen = ImageDraw.Draw(subject)
        pen.rectangle([20, 20, 1180, 780], outline=PALETTE["black"], width=12)
        for x in (200, 500, 800):
            pen.ellipse([x, 200, x + 60, 260], fill=PALETTE["orange"])
        for x in range(100, 1000, 60):
            pen.line([(x, 500), (x + 40, 500)], fill=PALETTE["orange"], width=2)
        subject.save(f"{folder}/subject.png")
        subject.save(f"{folder}/drawing.png")
        with open(f"{folder}/palette.json", "w") as handle:
            json.dump(PALETTE, handle)
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump({"drops": {"box": [0, 0, 1200, 800], "count": 3, "value": "orange"}}, handle)
        code, said = tool(f"{HERE}/check.py", "drawing.png", "--ref", "subject.png",
                          "--census", "parts.json", cwd=folder)
        assert code == 0 and "all agree" in said, said


@case("--ladder lists a fill whose outline doubles back, and not one that loops the same way")
def _():
    outer = [[0, 0], [200, 0], [200, 200], [0, 200]]
    fill = lambda points: {"op": "stroke", "stage": "fill", "closed": True, "points": points}
    same = fill(outer + [[0, 50], [150, 50], [150, 150], [50, 150], [50, 50], [0, 50]])
    back = fill(outer + [[0, 50], [50, 50], [50, 150], [150, 150], [150, 50], [0, 50]])
    found = [index for index, _, _ in check.self_crossing([same, back])]
    assert found == [1], found


@case("--checklist fails a sub-form neither named nor excused, and passes once one is")
def _():
    with tempfile.TemporaryDirectory() as folder:
        with open(f"{folder}/ref.md", "w") as handle:
            handle.write("```checklist\nobject: bike|bicycle\nsub-forms: chain chainring hood\n```\n")
        parts = {"bike.drivetrain.chainring": {"box": [0, 0, 1, 1]},
                 "bike.bar.hoods.near": {"box": [0, 0, 1, 1]}}
        json.dump(parts, open(f"{folder}/parts.json", "w"))
        missing = check.checklist(f"{folder}/parts.json", [f"{folder}/ref.md"])
        assert [gone for _, _, gone in missing] == [["chain"]], missing
        parts["_absent"] = "chain: behind the near leg"
        json.dump(parts, open(f"{folder}/parts.json", "w"))
        assert check.checklist(f"{folder}/parts.json", [f"{folder}/ref.md"]) == []


@case("--faces compares a flat with the region it overlaps, not one whose box holds it")
def _():
    with tempfile.TemporaryDirectory() as folder:
        tube = [(100, 100), (500, 110), (500, 140), (100, 130)]
        wheel = [(80 + 300 + 250 * np.cos(t), 120 + 250 * np.sin(t) + 10 * np.sin(9 * t))
                 for t in np.linspace(0, 2 * np.pi, 90, endpoint=False)]
        grain = [(x + 2 * np.sin(x), y + 2 * np.cos(x)) for x, y in
                 [(100 + t, 100 + t / 40) for t in range(0, 400, 4)] +
                 [(500 - t, 140 - t / 40) for t in range(0, 400, 4)]]
        regions = [{"box": [60, -140, 640, 520], "contour": [list(p) for p in wheel]},
                   {"box": [98, 98, 404, 44], "contour": [list(p) for p in grain]}]
        ops = [{"op": "stroke", "stage": "fill", "closed": True, "points": [list(p) for p in tube]}]
        json.dump(regions, open(f"{folder}/r.json", "w"))
        json.dump(ops, open(f"{folder}/ops.json", "w"))
        code, said = tool(f"{HERE}/check.py", "none.png", "--faces", "ops.json", "--regions",
                          "r.json", "--grain", "6", cwd=folder)
        assert code == 0 and "TOO FEW" not in said, said


def stroke(stage, tag, points, **more):
    return {"op": "stroke", "stage": stage, "tag": tag, "points": [list(p) for p in points], **more}


BOX = [(100, 100), (300, 100), (300, 300), (100, 300)]


@case("--doubled drops an edge a later flat buries, and keeps one it does not")
def _():
    far = stroke("ink", "far", [(150, 200), (250, 200)])
    near = stroke("ink", "near", [(150, 201), (250, 201)])
    lid = stroke("fill", "lid", BOX, closed=True, fill="fill")
    hits, _, _ = check.doubled([far, near])
    assert len(hits) == 1, hits
    hits, _, _ = check.doubled([far, lid, near])          # far is under the lid
    assert not hits, hits


@case("--depth lists an overlap no interface row decides")
def _():
    inventory = {"a": {"box": [0, 0, 1, 1]}, "b": {"box": [0, 0, 1, 1]}}
    ops = [{"op": "stroke", "stage": "frame", "points": [[0, 0], [400, 0], [400, 400], [0, 400]]},
           stroke("fill", "b", BOX, closed=True, fill="fill"),
           stroke("ink", "a", [(120, 200), (280, 200)])]
    rows = check.crossings(ops, inventory)
    assert rows and rows[0][1:] == ("a", "b", "drawn across"), rows
    inventory["a/b"] = {"in_front": "a"}
    assert not check.crossings(ops, inventory)


@case("describe.sh refuses an answer that is the CLI's own error, and names a second run")
def _():
    with tempfile.TemporaryDirectory() as folder:
        fake = f"{folder}/bin"
        os.makedirs(fake)
        for text, name in (("You've hit your session limit", "broken"),
                           ("1. a bike\n2. a wedge\n3. riding\n4. tyres on rocks\n5. strain", "fine")):
            with open(f"{fake}/claude", "w") as handle:
                handle.write(f"#!/bin/sh\nprintf '%s\\n' \"{text}\"\n")
            os.chmod(f"{fake}/claude", 0o755)
            Image.new("RGB", (4, 4)).save(f"{folder}/{name}.png")
            env = dict(os.environ, PATH=f"{fake}:{os.environ['PATH']}")
            done = subprocess.run([f"{HERE}/describe.sh", f"{folder}/{name}.png", "B"], env=env,
                                  capture_output=True, text=True)
            written = os.path.exists(f"{folder}/{name}.describe.B.md")
            if name == "broken":
                assert done.returncode == 1 and not written, (done.returncode, written)
            else:
                assert done.returncode == 0 and written, done.stderr


@case("line_width takes the smaller of the row and column run")
def _():
    mask = np.zeros((100, 100), bool)
    for at in range(10, 90):
        mask[at, at:at + 6] = True     # a diagonal band, 6 wide along the rows
    assert np.percentile(line_width(mask), 90) <= 6


sys.exit(1 if failed else 0)
