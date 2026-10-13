#!/usr/bin/env python3
"""segment.py against what it has to get right on a photograph-like subject.

Each case is built on a small synthetic picture: a few soft-edged shapes under
sensor-like noise, where trace.py's per-pixel classification breaks into specks.

    python3 test_segment.py
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
failed = []

GROUND = (96, 120, 70)
SHAPES = [  # colour, ellipse box (x0, y0, x1, y1)
    ((214, 170, 100), (30, 30, 150, 130)),
    ((70, 50, 40), (190, 40, 290, 110)),
    ((230, 225, 205), (60, 160, 200, 230)),
    ((150, 60, 50), (230, 150, 300, 220)),
]
PALETTE = {"background": "#60784a", "yellow": "#d6aa64", "black": "#463228",
           "white": "#e6e1cd", "red": "#963c32"}


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


def photo(folder, noise=22):
    """Four soft-edged shapes on a ground, blurred and under Gaussian noise."""
    image = Image.new("RGB", (330, 260), GROUND)
    pen = ImageDraw.Draw(image)
    for colour, box in SHAPES:
        pen.ellipse(box, fill=colour)
    image = image.filter(ImageFilter.GaussianBlur(3))
    grain = np.random.default_rng(7).normal(0, noise, (260, 330, 3))
    pixels = np.clip(np.asarray(image, float) + grain, 0, 255).astype(np.uint8)
    Image.fromarray(pixels).save(os.path.join(folder, "subject.png"))
    with open(os.path.join(folder, "palette.json"), "w") as handle:
        json.dump(PALETTE, handle)


@case("four soft shapes under noise come back as about five regions, one per shape, where trace.py "
      "returns many")
def _():
    with tempfile.TemporaryDirectory() as folder:
        photo(folder)
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--regions", "5", "--palette", "palette.json",
                          "--out", "seg.json", "--png", "seg.png", cwd=folder)
        assert code == 0, said
        regions = json.load(open(f"{folder}/seg.json"))
        assert 4 <= len(regions) <= 6, len(regions)
        for colour, (x0, y0, x1, y1) in SHAPES:
            hits = [r for r in regions if abs(r["box"][0] - x0) <= 6 and abs(r["box"][1] - y0) <= 6
                    and abs(r["box"][0] + r["box"][2] - x1) <= 6 and abs(r["box"][1] + r["box"][3] - y1) <= 6]
            assert len(hits) == 1, (colour, [r["box"] for r in regions])
        named = {r["colour"] for r in regions}
        assert {"yellow", "black", "white", "red"} <= named and "background" not in named, named
        for key in ("box", "contour", "holes", "median", "inside", "area", "blockin", "centre", "id"):
            assert key in regions[0], key
        assert os.path.exists(f"{folder}/seg.png")
        code, said = tool(f"{HERE}/trace.py", "subject.png", "palette.json", "--min-area", "20",
                          "--out", "trace.json", cwd=folder)
        assert code == 0, said
        assert len(json.load(open(f"{folder}/trace.json"))) >= 4 * len(regions), said.splitlines()[0]


@case("a region's contour runs in perimeter order and --faces reads the output")
def _():
    with tempfile.TemporaryDirectory() as folder:
        photo(folder)
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--regions", "5", "--out", "seg.json", cwd=folder)
        assert code == 0, said
        shape = next(r for r in json.load(open(f"{folder}/seg.json")) if abs(r["box"][0] - 190) <= 6)
        points = np.array(shape["contour"], float)
        steps = np.hypot(*np.diff(np.vstack([points, points[:1]]), axis=0).T)
        assert steps.max() < 0.6 * max(shape["box"][2:]), steps.max()   # no jump across the shape
        ops = [{"op": "stroke", "stage": "fill",
                "points": [[190, 40], [290, 40], [290, 110], [190, 110]]}]
        json.dump(ops, open(f"{folder}/ops.json", "w"))
        code, said = tool(f"{HERE}/check.py", "subject.png", "--faces", "ops.json", "--regions", "seg.json",
                          cwd=folder)
        assert "TOO FEW FACES" in said, said


@case("--box measures only the box, in picture coordinates, and a crop.py crop needs no offset")
def _():
    with tempfile.TemporaryDirectory() as folder:
        photo(folder)
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--box", "170,20,150,110", "--regions", "2",
                          "--out", "box.json", cwd=folder)
        assert code == 0, said
        regions = json.load(open(f"{folder}/box.json"))
        for region in regions:
            x, y, w, h = region["box"]
            assert x >= 170 and y >= 20 and x + w <= 320 and y + h <= 130, region["box"]
        dark = max(regions, key=lambda r: -sum(int(r["median"][at:at + 2], 16) for at in (1, 3, 5)))
        assert abs(dark["box"][0] - 190) <= 6 and abs(dark["box"][1] - 40) <= 6, dark["box"]
        code, said = tool(f"{HERE}/crop.py", "subject.png", "190,40,100,70", "meas/dark.png", cwd=folder)
        assert code == 0, said
        code, said = tool(f"{HERE}/segment.py", "meas/dark.png", "--regions", "2", "--out", "crop.json", cwd=folder)
        assert code == 0, said
        dark = max(json.load(open(f"{folder}/crop.json")),
                   key=lambda r: -sum(int(r["median"][at:at + 2], 16) for at in (1, 3, 5)))
        assert abs(dark["box"][0] - 190) <= 6 and abs(dark["box"][1] - 40) <= 6, dark["box"]
        code, said = tool(f"{HERE}/segment.py", "meas/dark.png", "--offset", "190,40", "--out", "x.json", cwd=folder)
        assert code != 0 and "disagrees" in said, said


@case("--silhouette finds the shape under the seed and stays inside its box, and needs a box")
def _():
    with tempfile.TemporaryDirectory() as folder:
        photo(folder)
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--silhouette", "90,80", "--box", "10,10,170,140",
                          "--out", "sil.json", "--png", "sil.png", cwd=folder)
        assert code == 0, said
        x, y, w, h = json.load(open(f"{folder}/sil.json"))[0]["box"]
        assert abs(x - 30) <= 6 and abs(y - 30) <= 6 and abs(x + w - 150) <= 6 and abs(y + h - 130) <= 6, (x, y, w, h)
        # a box that cuts the shape: the silhouette stops at the box, and says so
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--silhouette", "90,80", "--box", "60,50,120,100",
                          "--out", "cut.json", cwd=folder)
        assert code == 0, said
        x, y, w, h = json.load(open(f"{folder}/cut.json"))[0]["box"]
        assert x >= 60 and y >= 50 and x + w <= 180 and y + h <= 150, (x, y, w, h)
        assert abs(x + w - 150) <= 6 and abs(y + h - 130) <= 6, (x, y, w, h)   # the shape's own edge
        assert "the box's left, top edge" in said, said
        # a box wholly inside the shape: the box is all it finds, and every side says so
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--silhouette", "90,80", "--box", "60,50,60,60",
                          "--out", "inside.json", cwd=folder)
        assert code == 0 and "the box's left, top, right, bottom edge" in said, said
        x, y, w, h = json.load(open(f"{folder}/inside.json"))[0]["box"]
        assert x >= 60 and y >= 50 and x + w <= 120 and y + h <= 110, (x, y, w, h)
        code, said = tool(f"{HERE}/segment.py", "subject.png", "--silhouette", "90,80", cwd=folder)
        assert code != 0 and "needs --box" in said, said


@case("segment.py prints and writes measurements only: no stroke call anywhere in its output")
def _():
    with tempfile.TemporaryDirectory() as folder:
        photo(folder)
        outputs = []
        for args in (["--regions", "5", "--out", "seg.json"],
                     ["--silhouette", "90,80", "--box", "10,10,170,140", "--out", "sil.json"]):
            code, said = tool(f"{HERE}/segment.py", "subject.png", *args, cwd=folder)
            assert code == 0, said
            outputs.append(said)
        outputs += [open(f"{folder}/seg.json").read(), open(f"{folder}/sil.json").read()]
        for text in outputs:
            assert "stroke" not in text and "ops.append" not in text, text[:400]
        printed = outputs[1]
        assert "[[" not in printed and "[(" not in printed, printed   # no pasteable point list


sys.exit(1 if failed else 0)
