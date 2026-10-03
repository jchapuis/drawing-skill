#!/usr/bin/env python3
"""The measuring tools and the gates, each checked against a case it has to get right.

Each case is a fault a tool can have: a crash, a number that cannot be read, a
gate that passes a wrong result or buries a right one in noise. Each is built on
a tiny synthetic image or op list, so the test shows what the tool must do
without needing a real drawing.

    python3 test_tools.py
"""
import json
import os
import shutil
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
        assert abs(x - 123) <= 3 and abs(y - 83) <= 3, orange[0]["box"]   # picture coordinates
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


@case("--weights runs without --ref and names each weight by its position")
def _():
    with tempfile.TemporaryDirectory() as folder:
        image = Image.new("RGB", (200, 60), "white")
        pen = ImageDraw.Draw(image)
        for x, width in ((20, 3), (80, 9), (150, 5)):
            pen.rectangle([x, 5, x + width - 1, 55], fill="black")
        image.save(f"{folder}/swatch.png")
        code, said = tool(f"{HERE}/check.py", "swatch.png", "--weights", "30", cwd=folder)
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


@case("--unfilled also lists a flat painted where the subject is bare, and --box scopes both")
def _():
    subject = Image.new("RGB", (200, 200), PALETTE["background"])
    ImageDraw.Draw(subject).rectangle([50, 50, 150, 150], fill=PALETTE["orange"])
    drawing = Image.new("RGB", (200, 200), (0, 255, 102))
    ImageDraw.Draw(drawing).rectangle([50, 10, 150, 150], fill=PALETTE["orange"])  # 40px over the top
    paper, ground = (0, 255, 102), check.colour(PALETTE["background"])
    assert check.unfilled(drawing, subject, paper, ground) == 1
    assert check.unfilled(drawing, subject, paper, ground, box=[0, 100, 200, 100]) == 0


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


@case("--counts gives no verdict where it cannot count the subject, and fails a real cull")
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
                          "--counts", "parts.json", cwd=folder)
        assert code == 1 and "FAIL culled" in said and "UNCHECKED" in said, said


@case("--counts counts thick forms, not thin ramp specks of the same value")
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
                          "--counts", "parts.json", cwd=folder)
        assert code == 0 and "all agree" in said, said


@case("--stages lists a fill whose outline doubles back, and not one that loops the same way")
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


@case("--checklist counts a sub-form only under its own object, and reads two objects in one block")
def _():
    with tempfile.TemporaryDirectory() as folder:
        with open(f"{folder}/ref.md", "w") as handle:
            handle.write("```checklist\nobject: house\nsub-forms: window door\n"
                         "object: car\nsub-forms: wheel window\n```\n")
        parts = {"house.wall.door": {"box": [0, 0, 1, 1]},
                 "car.body.window.rear": {"box": [0, 0, 1, 1]},
                 "car.wheel.front": {"box": [0, 0, 1, 1]}}
        json.dump(parts, open(f"{folder}/parts.json", "w"))
        missing = check.checklist(f"{folder}/parts.json", [f"{folder}/ref.md"])
        assert [(name, gone) for name, _, gone in missing] == [("house", ["window"])], missing
        parts["house.wall.windows"] = {"box": [0, 0, 1, 1]}
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


@case("--doubled passes spokes crossing in an X or meeting in a V; keeps lines run together")
def _():
    one = stroke("ink", "spoke", [(0, 200), (400, 200)])
    for degrees in (8, 20, 60):                       # an X at a clear angle
        rise = 200 * np.tan(np.radians(degrees))
        other = stroke("ink", "spoke", [(0, 200 - rise), (400, 200 + rise)])
        hits, _, _ = check.doubled([one, other])
        assert not hits, (degrees, hits)
    v = stroke("ink", "spoke", [(0, 200 - 400 * np.tan(np.radians(8))), (400, 200)])
    assert not check.doubled([one, v])[0]               # a V into one hub hole
    shallow = stroke("ink", "spoke", [(0, 197), (400, 203)])   # under 1 degree: one edge
    assert check.doubled([one, shallow])[0]
    wavy = stroke("ink", "edge", [(0, 201), (100, 199), (200, 201), (300, 199), (400, 201)])
    assert check.doubled([one, wavy])[0]                # two guesses wandering across each other


@case("--depth lists an overlap that no row decides")
def _():
    inventory = {"a": {"box": [0, 0, 1, 1]}, "b": {"box": [0, 0, 1, 1]}}
    ops = [{"op": "stroke", "stage": "frame", "points": [[0, 0], [400, 0], [400, 400], [0, 400]]},
           stroke("fill", "b", BOX, closed=True, fill="fill"),
           stroke("ink", "a", [(120, 200), (280, 200)])]
    rows = check.crossings(ops, inventory)
    assert rows and rows[0][1:] == ("a", "b", "drawn across"), rows
    inventory["a/b"] = {"in_front": "a"}
    assert not check.crossings(ops, inventory)


@case("parts.json: a key no check reads warns, and names hatch for a misplaced light")
def _():
    good = {"rock": {"shape": "a face", "box": [0, 0, 4, 4], "tier": 1,
                     "hatch": {"angle": 45, "spacing": 9, "length": 30, "light": True}},
            "a/b": {"shape": "", "box": [0, 0, 1, 1], "in_front": "same"}, "_absent": "x: y"}
    assert not check.unknown_keys(good)
    bad = {"rock": {"shape": "a face", "box": [0, 0, 4, 4], "light": True,
                    "hatch": {"angle": 45, "spacing": 9, "lenght": 30}}}
    said = check.unknown_keys(bad)
    assert len(said) == 2 and 'inside "hatch"' in said[0] and "'lenght'" in said[1], said
    with tempfile.TemporaryDirectory() as folder:
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump(bad, handle)
        code, said = tool(f"{HERE}/check.py", "x.png", "--checklist", "parts.json", cwd=folder)
        assert "WARN parts.json: 'rock' has a key no check reads: 'light'" in said, said


@case("--depth: an in_front \"same\" row takes two sub-forms of one surface off the unlisted list")
def _():
    inventory = {"a": {"box": [0, 0, 1, 1]}, "b": {"box": [0, 0, 1, 1]}}
    ops = [{"op": "stroke", "stage": "frame", "points": [[0, 0], [400, 0], [400, 400], [0, 400]]},
           stroke("fill", "b", BOX, closed=True, fill="fill"),
           stroke("ink", "a", [(120, 200), (280, 200)])]
    assert check.crossings(ops, inventory)
    inventory["b/a"] = {"in_front": "same"}
    assert not check.crossings(ops, inventory)


@case("describe.sh refuses an answer that is the CLI's own error, and names a second run")
def _():
    with tempfile.TemporaryDirectory() as folder:
        fake = f"{folder}/bin"
        os.makedirs(fake)
        for text, name in (("I can't help with that", "broken"),
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


def fake_claude(folder, script):
    """A `claude` on PATH that runs `script` (sh) instead of the real CLI."""
    os.makedirs(f"{folder}/bin", exist_ok=True)
    with open(f"{folder}/bin/claude", "w") as handle:
        handle.write("#!/bin/sh\n" + script)
    os.chmod(f"{folder}/bin/claude", 0o755)
    return dict(os.environ, PATH=f"{folder}/bin:{os.environ['PATH']}")


@case("describe.sh shows the describer a neutral copy of the image, and removes it after")
def _():
    with tempfile.TemporaryDirectory() as folder:
        # echo the prompt and the working directory back as the five answers
        env = fake_claude(folder, 'printf "1. %s\n2. %s\n3. a\n4. b\n5. c\n" "$2" "$(pwd)"\n')
        os.makedirs(f"{folder}/rooster")
        Image.new("RGB", (4, 4)).save(f"{folder}/rooster/head_comb.png")
        done = subprocess.run([f"{HERE}/describe.sh", f"{folder}/rooster/head_comb.png"], env=env,
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
        said = open(f"{folder}/rooster/head_comb.describe.md").read()
        assert "comb" not in said and "rooster" not in said, said
        shown = said.split("exactly one file: ")[1].split(". Do not")[0]
        assert shown.endswith(".png") and not os.path.exists(shown), shown


@case("describe.sh stops on a usage limit with exit 3, without retrying, and caps parallel runs")
def _():
    with tempfile.TemporaryDirectory() as folder:
        env = fake_claude(folder, f'echo call >> "{folder}/calls"\n'
                                  'printf "%s\\n" "You\'ve hit your session limit"\n')
        Image.new("RGB", (4, 4)).save(f"{folder}/a.png")
        done = subprocess.run([f"{HERE}/describe.sh", f"{folder}/a.png"], env=env,
                              capture_output=True, text=True)
        calls = len(open(f"{folder}/calls").read().split())
        assert done.returncode == 3 and calls == 1, (done.returncode, calls, done.stderr)
        assert "at most 4" in done.stderr and not os.path.exists(f"{folder}/a.describe.md"), done.stderr


@case("build.sh STAGE=blockin renders only up to block-in, and unset renders everything")
def _():
    with tempfile.TemporaryDirectory() as folder:
        draw = ("from pen import stroke, frame, write\nops = [frame(0, 0, 400, 300)]\n"
                "ops.append(stroke([(10, 10), (200, 150)], stage='gesture'))\n"
                "ops.append(stroke([(10, 10), (200, 150)], stage='blockin', smooth=False))\n"
                "ops.append(stroke([(20, 10), (200, 150)], stage='construction', smooth=False))\n"
                "ops.append(stroke([(10, 10), (200, 150), (10, 150)], stage='fill', closed=True))\n"
                "ops.append(stroke([(10, 10), (200, 150)], stage='contour'))\n"
                "ops.append(stroke([(10, 10), (200, 150)], stage='ink'))\n"
                "write('ops.json', ops)\n")
        with open(f"{folder}/draw.py", "w") as handle:
            handle.write(draw)
        shutil.copy(f"{HERE}/build.sh", folder)   # build.sh runs where it sits
        # a `node` that records which render it was asked for and the stages it was given
        os.makedirs(f"{folder}/bin")
        with open(f"{folder}/bin/node", "w") as handle:
            handle.write(f"#!{sys.executable}\nimport json, sys\nargs = sys.argv[1:]\n"
                         "ops = json.load(open(args[args.index('--ops') + 1]))\n"
                         "png = args[args.index('--png') + 1]\nopen(png, 'w').close()\n"
                         "print(png, sorted({o.get('stage', 'ink') for o in ops}), file=open('renders', 'a'))\n")
        os.chmod(f"{folder}/bin/node", 0o755)
        env = dict(os.environ, PATH=f"{folder}/bin:{os.environ['PATH']}", SKILL=HERE, STAGE="blockin")
        done = subprocess.run(["bash", "build.sh"], cwd=folder, env=env,
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
        renders = open(f"{folder}/renders").read()
        stages = {op.get("stage") for op in json.load(open(f"{folder}/ops.json"))}
        assert stages == {"frame", "gesture", "blockin"}, stages
        assert "drawing.png" not in renders and "contour.png" not in renders, renders
        assert not os.path.exists(f"{folder}/drawing.png"), renders
        os.remove(f"{folder}/renders")
        del env["STAGE"]
        done = subprocess.run(["bash", "build.sh"], cwd=folder, env=env,
                              capture_output=True, text=True)
        assert done.returncode == 0 and "drawing.png" in open(f"{folder}/renders").read(), done.stderr
        assert "ink" in {op.get("stage") for op in json.load(open(f"{folder}/ops.json"))}
        env["STAGE"] = "inking"
        done = subprocess.run(["bash", "build.sh"], cwd=folder, env=env,
                              capture_output=True, text=True)
        assert done.returncode != 0 and "not a stage" in done.stderr, done.stderr


@case("--checklist warns when no checklist object matches the inventory, and not when one does")
def _():
    with tempfile.TemporaryDirectory() as folder:
        with open(f"{folder}/ref.md", "w") as handle:
            handle.write("```checklist\nobject: bird\nsub-forms: beak wing\n```\n")
        parts = {"rooster.head.beak": {"box": [0, 0, 1, 1]}, "rock": {"box": [0, 0, 1, 1]}}
        json.dump(parts, open(f"{folder}/parts.json", "w"))
        found = check.checklist_unmatched(f"{folder}/parts.json", [f"{folder}/ref.md"])
        assert found == (["rock", "rooster"], [("bird", "ref.md")]), found
        json.dump({"bird.head.beak": {"box": [0, 0, 1, 1]}}, open(f"{folder}/parts.json", "w"))
        assert check.checklist_unmatched(f"{folder}/parts.json", [f"{folder}/ref.md"]) is None
        json.dump({"zzqx.head": {"box": [0, 0, 1, 1]}}, open(f"{folder}/parts.json", "w"))
        code, said = tool(f"{HERE}/check.py", "none.png", "--checklist", "parts.json", cwd=folder)
        assert code == 0 and "WARN" in said and "zzqx" in said and "PASSES" not in said, said


@case("--zoom: a tall box goes side by side, a wide one stacked, as the help says")
def _():
    subject = Image.new("RGB", (200, 200), "white")
    # each magnified crop is 80x400 (or 400x80); two stacked along 400 would pass 800
    tall = check.zoom(subject, subject, [0, 0, 20, 100], factor=4)
    wide = check.zoom(subject, subject, [0, 0, 100, 20], factor=4)
    assert tall.height < 600 and tall.width > 160, tall.size
    assert wide.width < 600 and wide.height > 160, wide.size
    _, said = tool(f"{HERE}/check.py", "--help", cwd=HERE)
    said = " ".join(said.split())
    assert "side by side (subject left) for a box taller than wide" in said, said


@case("trace.py --smooth classifies a grainy flat as one, with its box where it was")
def _():
    with tempfile.TemporaryDirectory() as folder:
        panel(folder)
        pixels = np.asarray(Image.open(f"{folder}/subject.png")).astype(int)
        grain = np.random.default_rng(0).choice([-70, 0, 70], size=pixels.shape[:2], p=[.2, .6, .2])
        pixels = np.clip(pixels + grain[..., None], 0, 255).astype(np.uint8)
        Image.fromarray(pixels).save(f"{folder}/subject.png")
        reads = {}
        for smooth in ("0", "2"):
            code, said = tool(f"{HERE}/trace.py", "subject.png", "palette.json", "--line", "8",
                              "--smooth", smooth, "--out", f"r{smooth}.json", cwd=folder)
            assert code == 0, said
            share = float(said.split("% of pixels are over")[0].split()[-1])
            orange = [r for r in json.load(open(f"{folder}/r{smooth}.json")) if r["colour"] == "orange"]
            reads[smooth] = share, orange
        assert reads["0"][0] > 10 and reads["2"][0] < 2, reads
        assert len(reads["2"][1]) == 1, reads["2"][1]
        x, y = reads["2"][1][0]["box"][:2]
        assert abs(x - 123) <= 3 and abs(y - 83) <= 3, reads["2"][1][0]["box"]


@case("line_width takes the smaller of the row and column run")
def _():
    mask = np.zeros((100, 100), bool)
    for at in range(10, 90):
        mask[at, at:at + 6] = True     # a diagonal band, 6 wide along the rows
    assert np.percentile(line_width(mask), 90) <= 6


def hatched(angle, size=(400, 400), spacing=16, width=3, ground=(240, 230, 210)):
    """A box of parallel strokes at `angle` (0 horizontal, 45 a `/`), `spacing`
    apart measured across them."""
    image = Image.new("RGB", size, ground)
    pen = ImageDraw.Draw(image)
    turn = np.radians(angle)
    along, across = np.array([np.cos(turn), -np.sin(turn)]), np.array([np.sin(turn), np.cos(turn)])
    middle = np.array(size) / 2
    for step in range(-12, 13):
        centre = middle + across * step * spacing
        ends = [tuple(centre - along * 90), tuple(centre + along * 90)]
        pen.line(ends, fill=(30, 20, 20), width=width)
    return image


def flat_box(size=(400, 400)):
    image = Image.new("RGB", size, (240, 230, 210))
    ImageDraw.Draw(image).rectangle([60, 60, 340, 340], fill=(30, 20, 20))
    return image


def grey(image):
    return np.asarray(image.convert("L"), dtype=float)


@case("--hatch: a hatched box gives one group at its angle and spacing; a flat box gives none")
def _():
    for angle in (30, 135):
        found = check.hatching(grey(hatched(angle)), 6)
        assert found["groups"], found
        group = found["groups"][0]
        assert check._apart(group["angle"], angle) <= 5, (angle, group)
        assert abs(group["spacing"][0] - 16) <= 2, group
        assert 150 <= group["length"] <= 200, group
        assert found["coverage"] > 0.05, found
    flat = check.hatching(grey(flat_box()), 6)
    assert not flat["groups"] and flat["coverage"] < 0.01, flat   # a dark flat is not line


def grainy(seed=3):
    """A photograph's grain: noise streaked along 45deg, upscaled 4x as a
    working-space subject is. It reads as a group of short parallel marks."""
    rng = np.random.default_rng(seed)
    small = np.clip(150 + rng.normal(0, 50, (100, 100)), 0, 255).astype(np.uint8)
    streak = np.zeros((7, 7))
    for at in range(7):
        streak[6 - at, at] = 1.0 / 7
    from scipy import ndimage as nd
    small = nd.convolve(small.astype(float), streak).clip(0, 255).astype(np.uint8)
    return Image.fromarray(small).resize((400, 400), Image.BILINEAR).convert("RGB")


@case("--hatch warns that photo grain is not hatching, and does not warn on drawn hatching")
def _():
    noise = check.hatching(grey(grainy()), 14)
    assert noise["groups"] and noise.get("grain"), noise      # it looks like a group, and is grain
    drawn = check.hatching(grey(hatched(45, width=5)), 14)
    assert drawn["groups"] and not drawn.get("grain"), drawn
    with tempfile.TemporaryDirectory() as folder:
        grainy().save(f"{folder}/photo.png")
        code, said = tool(f"{HERE}/check.py", "photo.png", "--hatch", "0,0,400,400",
                          "--line", "14", cwd=folder)
        assert code == 0 and "WARN grain" in said, said
        hatched(45).save(f"{folder}/print.png")
        code, said = tool(f"{HERE}/check.py", "print.png", "--hatch", "0,0,400,400", cwd=folder)
        assert code == 0 and "WARN grain" not in said, said


@case("--hatch --ref: the drawing's flat box is flagged missing, its own hatching is not")
def _():
    with tempfile.TemporaryDirectory() as folder:
        hatched(45).save(f"{folder}/subject.png")
        flat_box().save(f"{folder}/flat.png")
        hatched(45, spacing=18).save(f"{folder}/same.png")
        code, said = tool(f"{HERE}/check.py", "subject.png", "--hatch", "0,0,400,400",
                          "--ref", "flat.png", cwd=folder)
        assert code == 0 and "<< missing" in said, said
        code, said = tool(f"{HERE}/check.py", "subject.png", "--hatch", "0,0,400,400",
                          "--ref", "same.png", cwd=folder)
        assert code == 0 and "<<" not in said.split("subject group")[1].split("<< marks")[0], said
        assert "stroke(" not in said, said    # numbers, never marks


def linework_case(folder, drawing, hatch_angle=45):
    hatched(45).save(f"{folder}/subject.png")
    drawing.save(f"{folder}/drawing.png")
    with open(f"{folder}/parts.json", "w") as handle:
        json.dump({"rock": {"shape": "hatched face", "box": [0, 0, 400, 400],
                            "hatch": {"angle": hatch_angle, "spacing": 16, "length": 180}}}, handle)
    return tool(f"{HERE}/check.py", "drawing.png", "--linework", "parts.json", "--ref",
                "subject.png", cwd=folder)


@case("--linework: hatching at the measured angle passes; at the wrong angle or absent, FAIL")
def _():
    with tempfile.TemporaryDirectory() as folder:
        code, said = linework_case(folder, hatched(50, spacing=20))
        assert code == 0 and "FAIL:" not in said, said
        code, said = linework_case(folder, hatched(135))
        assert code == 1 and "FAIL: no line group within 20deg of 45deg" in said, said
        code, said = linework_case(folder, flat_box())
        assert code == 1 and "FAIL:" in said, said
        code, said = linework_case(folder, hatched(45), hatch_angle=100)
        assert code == 2 and "UNCHECKED" in said, said   # written angle not on the subject


@case("--linework: a FAIL names the line width when the box's lines run wider than --line")
def _():
    heavy = Image.new("RGB", (400, 400), (240, 230, 210))
    pen = ImageDraw.Draw(heavy)
    for x in (120, 280):
        pen.line([(x, 20), (x, 380)], fill=(30, 20, 20), width=10)   # edges over --line 6
    with tempfile.TemporaryDirectory() as folder:
        code, said = linework_case(folder, heavy)
        assert code == 1 and "wider than --line 6px" in said, said
        code, said = linework_case(folder, flat_box())
        assert code == 1 and "wider than --line" not in said, said


def framed(hatch, outline, spacing=16):
    """Hatching `hatch` px wide at 45deg inside a square outline `outline` px wide."""
    image = hatched(45, spacing=spacing, width=hatch)
    ImageDraw.Draw(image).rectangle([40, 40, 360, 360], outline=(30, 20, 20), width=outline)
    return image


def framed_case(folder, drawing, *flags):
    framed(3, 13).save(f"{folder}/subject.png")
    drawing.save(f"{folder}/drawing.png")
    with open(f"{folder}/parts.json", "w") as handle:
        json.dump({"rock": {"shape": "hatched face", "box": [30, 30, 340, 340],
                            "hatch": {"angle": 45, "spacing": 16, "length": 180}}}, handle)
    return tool(f"{HERE}/check.py", "drawing.png", "--linework", "parts.json", "--ref",
                "subject.png", "--line", "14", *flags, cwd=folder)


@case("--linework, --hatch: fine hatching passes against fine; heavy hatching FAILs on width")
def _():
    with tempfile.TemporaryDirectory() as folder:
        code, said = framed_case(folder, framed(3, 13, spacing=17))
        assert code == 0 and "FAIL" not in said.split("FAIL is")[0], said
        assert "mark width" in said and "hatch/outline" in said, said
        code, said = framed_case(folder, framed(9, 13))
        assert code == 1 and "FAIL: hatch marks" in said and "FAIL: hatch is" in said, said
        # the same widths through --hatch, on the drawing's own scale: a render at
        # twice the subject's size is read in the subject's pixels
        framed(3, 13).resize((800, 800), Image.LANCZOS).save(f"{folder}/fine2x.png")
        framed(9, 13).resize((800, 800), Image.LANCZOS).save(f"{folder}/heavy2x.png")
        for name, want in (("fine2x.png", 0), ("heavy2x.png", 1)):
            code, said = tool(f"{HERE}/check.py", "subject.png", "--hatch", "60,60,280,280",
                              "--ref", name, "--line", "14", cwd=folder)
            assert code == want and ("FAIL: hatch marks" in said) == bool(want), said
            assert "in the subject's pixels" in said, said


@case("--linework: hatch light in pixels but heavy against a thin outline FAILs on the ratio")
def _():
    with tempfile.TemporaryDirectory() as folder:
        code, said = framed_case(folder, framed(6, 4))
        assert code == 1 and "FAIL: hatch is" in said and "FAIL: hatch marks" not in said, said


def weighted(widths, size=(400, 400)):
    image = Image.new("RGB", size, (240, 230, 210))
    pen = ImageDraw.Draw(image)
    for at, width in enumerate(widths):
        x = 30 + at * 50
        pen.line([(x, 40), (x, 360)], fill=(30, 20, 20), width=width)
    return image


@case("--linework: a drawing at one weight fails against a subject's range; a matching range passes")
def _():
    varied = check.weight_span(grey(weighted([3, 3, 5, 9, 17, 17, 17])), 20)
    uniform = check.weight_span(grey(weighted([9] * 7)), 20)
    assert varied[2] / varied[0] > 4, varied
    assert uniform[2] / uniform[0] < 1.5, uniform
    with tempfile.TemporaryDirectory() as folder:
        weighted([3, 3, 5, 9, 17, 17, 17]).save(f"{folder}/subject.png")
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump({"post": {"shape": "posts", "box": [0, 0, 400, 400]}}, handle)
        for widths, want in (([9] * 7, 1), ([3, 3, 5, 7, 15, 15, 15], 0)):
            weighted(widths).save(f"{folder}/drawing.png")
            code, said = tool(f"{HERE}/check.py", "drawing.png", "--linework", "parts.json",
                              "--ref", "subject.png", "--line", "20", cwd=folder)
            assert code == want, said
            assert ("FAIL: the drawing's span" in said) == (want == 1), said


def ring(cx, cy, radius, count=24):
    return [(cx + radius * np.cos(2 * np.pi * at / count), cy + radius * np.sin(2 * np.pi * at / count))
            for at in range(count)]


CHAIN = dict(size="m", scale=2.0)   # a 9px line: (3.5 + 1) x 2


@case("--joins lists a chain stopping a few widths short of its sprocket, not one that meets it")
def _():
    sprocket = stroke("fill", "bike.cassette", ring(100, 200, 50), closed=True, fill="fill", size="s", scale=0.3)
    # the run's left end aims at the ring's top-right, the gap measured edge to edge
    for stop, listed in ((180, True), (108, False), (500, False)):
        run = stroke("ink", "bike.chain.upper", [(600, 150), (stop, 150)], **CHAIN)
        found = check.joins([sprocket, run])
        assert bool(found) == listed, (stop, found)
        if listed:
            tag, end, missed = found[0]
            assert tag == "bike.chain.upper" and end == (180, 150), found
            assert missed[0][1] == "bike.cassette" and 9 <= missed[0][0] <= 72, missed


@case("--joins passes a hand's 1-4px fall-short, a hatch line beside the next, and a hairline crossed")
def _():
    post = stroke("ink", "fence.post", [(300, 100), (300, 300)], **CHAIN)
    rail = stroke("ink", "fence.rail", [(100, 200), (291.5, 200)], **CHAIN)   # 3px of paper
    assert not check.joins([post, rail])
    hatch = [stroke("ink", "rock.hatch", [(100, 100 + 20 * at), (200, 100 + 20 * at)], **CHAIN)
             for at in range(4)]
    assert not check.joins(hatch)
    spoke = stroke("ink", "bike.spoke", [(400, 100), (400, 300)], size="s", scale=1.0)
    chain = stroke("ink", "bike.chain", [(100, 200), (380, 200)], **CHAIN)
    assert not check.joins([spoke, chain])
    other = stroke("ink", "rider.arm", [(400, 100), (400, 300)], **CHAIN)
    assert not check.joins([other, chain]), "another object's mark is not a join target"


@case("--joins: a ring left open is found, and a pair in _gaps is excused")
def _():
    points = ring(200, 200, 80, 36)[:-2]          # two segments short of closing
    found = check.joins([stroke("ink", "bike.chainring", points, **CHAIN)])
    assert found and found[0][2][0][1] == "bike.chainring", found
    sprocket = stroke("fill", "bike.cassette", ring(100, 200, 50), closed=True, fill="fill", size="s", scale=0.3)
    run = stroke("ink", "bike.chain.upper", [(600, 150), (180, 150)], **CHAIN)
    assert not check.joins([sprocket, run], ["bike.cassette/bike.chain"])
    with tempfile.TemporaryDirectory() as folder:
        with open(f"{folder}/ops.json", "w") as handle:
            json.dump([sprocket, run], handle)
        code, said = tool(f"{HERE}/check.py", "--joins", "ops.json", cwd=folder)
        assert code == 1 and "bike.chain.upper end at 180,150" in said and "bike.cassette" in said, said
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump({"_gaps": ["bike.chain.upper/bike.cassette"]}, handle)
        code, said = tool(f"{HERE}/check.py", "--joins", "ops.json", "--parts", "parts.json", cwd=folder)
        assert code == 0 and "PASSES" in said, said


@case("--checklist: a small figure, under any of its names, needs head, torso, arms, legs and feet")
def _():
    with tempfile.TemporaryDirectory() as folder:
        for name in ("figures", "walker", "rider", "people"):
            with open(f"{folder}/parts.json", "w") as handle:
                json.dump({name: {"shape": "a small figure walking", "box": [0, 0, 9, 9]}}, handle)
            person = [gone for _, source, gone in check.checklist(f"{folder}/parts.json")
                      if source == "figure.md"]
            assert person and set(person[0]) == {"head", "torso|body", "arm", "leg", "foot|feet"}, (name, person)
        built = {f"rider.{part}": {"shape": part, "box": [0, 0, 9, 9]}
                 for part in ("head", "torso", "arm.near", "arm.far", "leg.near", "leg.far", "foot.near")}
        built["bike.bar/rider.hand"] = {"shape": "the hand closes on the bar", "box": [0, 0, 9, 9]}
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump(built, handle)
        assert not [row for row in check.checklist(f"{folder}/parts.json") if row[1] == "figure.md"]


def coat(folder, name, light, mid, shade, ground=(59, 77, 34)):
    """A green ground, a three-step coat and a black outline. The light band is the
    largest, so the median is the light and only the mid-tone reading sees the mid."""
    image = Image.new("RGB", (300, 240), ground)
    pen = ImageDraw.Draw(image)
    pen.rectangle([60, 40, 240, 200], fill=light)
    pen.rectangle([60, 136, 240, 175], fill=mid)
    pen.rectangle([60, 176, 240, 200], fill=shade)
    pen.rectangle([60, 40, 240, 200], outline=(20, 18, 16), width=6)
    image.save(os.path.join(folder, name))
    return image


GOLD = ((243, 226, 165), (196, 138, 72), (147, 112, 63))


@case("--colour: the same coat in a box half ground and outline passes; a beige mid-tone is flagged")
def _():
    with tempfile.TemporaryDirectory() as folder:
        subject = coat(folder, "subject.png", *GOLD)
        same = coat(folder, "same.png", *GOLD).resize((600, 480))
        beige = coat(folder, "beige.png", GOLD[0], (184, 160, 120), GOLD[2])
        box = {"coat": [20, 20, 260, 200]}
        (_, theirs, ours, flags), = check.colour_match(same, subject, box, (59, 77, 34))
        assert flags == [], (theirs, ours, flags)
        assert abs(theirs[0] - ours[0]) < 3 and abs(theirs[3] - ours[3]) < 0.03, (theirs, ours)
        (_, theirs, ours, flags), = check.colour_match(beige, subject, box, (59, 77, 34))
        assert "mid-tone saturation" in flags, (theirs, ours, flags)
        assert flags == ["mid-tone saturation"], flags


@case("--colour: a hue turned green-yellow, a greyed coat and a darker coat are each flagged")
def _():
    with tempfile.TemporaryDirectory() as folder:
        subject = coat(folder, "subject.png", *GOLD)
        box = {"coat": [60, 40, 181, 161]}
        lime = coat(folder, "lime.png", (226, 243, 165), (160, 196, 72), (120, 147, 63))
        grey = coat(folder, "grey.png", (225, 220, 205), (165, 150, 135), (125, 118, 105))
        dark = coat(folder, "dark.png", *[tuple(int(c * 0.7) for c in step) for step in GOLD])
        assert "hue" in check.colour_match(lime, subject, box, (59, 77, 34))[0][3]
        assert "saturation" in check.colour_match(grey, subject, box, (59, 77, 34))[0][3]
        assert "value" in check.colour_match(dark, subject, box, (59, 77, 34))[0][3]


@case("--colour on the command line: a box or parts.json, exit 1 only when a part is flagged")
def _():
    with tempfile.TemporaryDirectory() as folder:
        coat(folder, "subject.png", *GOLD)
        coat(folder, "same.png", *GOLD)
        coat(folder, "beige.png", GOLD[0], (184, 160, 120), GOLD[2])
        with open(f"{folder}/palette.json", "w") as handle:
            json.dump({"background": "#3b4d22"}, handle)
        with open(f"{folder}/parts.json", "w") as handle:
            json.dump({"coat": {"shape": "a gold coat", "box": [20, 20, 260, 200]},
                       "coat/ground": {"shape": "an overlap, not read", "box": [0, 0, 9, 9]}}, handle)
        code, said = tool(f"{HERE}/check.py", "same.png", "--ref", "subject.png",
                          "--colour", "20,20,260,200", cwd=folder)
        assert code == 0 and "<<" not in said.split("\n\n<<")[0], said
        code, said = tool(f"{HERE}/check.py", "beige.png", "--ref", "subject.png",
                          "--colour", "parts.json", cwd=folder)
        assert code == 1 and "mid-tone saturation" in said and "coat/ground" not in said, said


sys.exit(1 if failed else 0)
