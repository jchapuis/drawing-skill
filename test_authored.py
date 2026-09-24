#!/usr/bin/env python3
"""The authored-marks gate, checked in both directions.

Each case is a tiny draw.py run in its own directory with the real pen; the
gate must pass the honest ones and name the fault in the generated ones. The
honest cases are the shapes authored scripts actually take -- a dict of named
points, a helper that looks points up, two calls on one line -- because a gate
that fires on those is worse than none.

    python3 test_authored.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = "from pen import stroke, frame, write\nW, H = 400, 300\nops = [frame(0, 0, W, H)]\n"
LADDER = ("ops.append(stroke([(10, 10), (200, 150)], stage='gesture'))\n"
          "ops.append(stroke([(10, 10), (200, 150)], stage='blockin', smooth=False))\n"
          "ops.append(stroke([(10, 10), (200, 150)], stage='contour'))\n")
TAIL = "write('ops.json', ops)\n"

CASES = {
    "named points, looked up by a helper": (True, {}, HEAD + LADDER +
        "V = {'a': (20, 30), 'b': (80, 40), 'c': (120, 90)}\n"
        "P = lambda *names: [V[n] for n in names]\n"
        "ops.append(stroke(P('a', 'b'), tag='x'))\n"
        "ops.append(stroke(P('b', 'c'), tag='y'))\n" + TAIL),
    "two calls on one line": (True, {}, HEAD + LADDER +
        "ops += [stroke([(1, 2), (30, 40)]), stroke([(5, 6), (70, 80)])]\n" + TAIL),
    "a loop stamping literal points": (False, {}, HEAD + LADDER +
        "for pts in ([(1, 2), (30, 40)], [(5, 6), (70, 80)]):\n"
        "    ops.append(stroke(pts))\n" + TAIL),
    "points loaded from a file, one call per line": (False,
        {"m.json": "[[[1.5, 2.5], [30.5, 40.5]], [[5.5, 6.5], [70.5, 80.5]]]"},
        HEAD + LADDER + "import json\nM = json.load(open('m.json'))\n"
        "ops.append(stroke(M[0]))\nops.append(stroke(M[1]))\n" + TAIL),
    "a generated section imported": (False,
        {"sec.py": "from pen import stroke\nOPS = [stroke([(1, 2), (30, 40)]), "
                   "stroke([(5, 6), (70, 80)])]\n"},
        HEAD + LADDER + "import sec\nops += sec.OPS\n" + TAIL),
}


def run(script, extra):
    with tempfile.TemporaryDirectory() as folder:
        for name, text in extra.items():
            with open(os.path.join(folder, name), "w") as handle:
                handle.write(text)
        with open(os.path.join(folder, "draw.py"), "w") as handle:
            handle.write(script)
        env = dict(os.environ, PYTHONPATH=HERE)
        done = subprocess.run([sys.executable, "draw.py"], cwd=folder, env=env,
                              capture_output=True, text=True)
        return done.returncode == 0, (done.stderr or done.stdout).strip().splitlines()[-1:]


failed = 0
for name, (honest, extra, script) in CASES.items():
    written, said = run(script, extra)
    right = written == honest
    failed += not right
    print(f"{'ok  ' if right else 'FAIL'} {name}: {'written' if written else 'refused'}"
          + ("" if written else f" -- {said[0][:110]}"))
sys.exit(1 if failed else 0)
