#!/usr/bin/env python3
"""What a blind viewer takes away from each part, scored against the subject.

Every other instrument here measures presence, placement, value or design, and
an object can pass all of them while reading as a different object: present,
in its box, at the right weight, inside a design that matches — and a viewer
calls it a plate of food. Nothing else in the kit asks what the thing IS.

Three steps, and the separation between them is the whole method:

1. A blind viewer writes a PARAGRAPH about the subject's crop. Never a name.
   A name is too coarse to score with: asked to name a crude mask a viewer
   says "face", which matches the subject's "laughing woman's face" on its
   head word and scores full marks. A paragraph has to commit to the kind of
   thing, its proportions, its parts and its angle, so losing any of that
   shows up as a difference in the text.
2. A second blind viewer writes a paragraph about the drawing's crop.
3. A judge that has seen NEITHER IMAGE reads only the two paragraphs and
   scores how fully the second conveys the same specific thing as the first,
   with vagueness penalised and contradiction penalised harder.

Keeping the judge away from the pictures is what makes it hard to flatter: it
cannot see that the candidate is a drawing, so it cannot be kind to it.

    python3 concepts.py subject.png drawing.png parts.json
    python3 concepts.py subject.png drawing.png parts.json --bar 0.7

Read MISSING and WRONG, not only the number. They are the worklist, and a
confident wrong reading is a better diagnosis than any score: "an animal paw
with toes and a heel pad" says fingers became toes and the cuff is gone;
"an oval seen front-on" says a profile was drawn without its depth.

NOISE: three blind passes stack, so a part's score moves about +/-0.1 between
runs and a mean moves with it. The RANKING is stable and the ranking is what
you spend against; do not read a 0.05 change between rounds as progress. Run
it twice at a gate that decides something.

SCOPE: this measures what a viewer takes away — kind, specificity, parts,
proportion, angle. It does not judge the marks. A part can score well and
still be drawn badly, and a low score never says which stage to go back to.
"""
import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

DESCRIBE = """This image shows one object cropped out of a larger picture.
Describe what it is in one paragraph of 4-6 sentences, for someone who cannot
see it. Be specific and concrete: what kind of thing it is, its shape and
proportions, its parts, its materials, its angle to the viewer, and if it
shows a person, their apparent age, sex and expression.
Describe only what is visible. Where something is unclear, say so plainly
rather than guessing."""

JUDGE = """Below are two descriptions, A and B, each written by someone who saw
one picture and not the other. They may or may not describe the same thing.
You cannot see either picture. Judge only from the text.

A (the reference):
{reference}

B (the candidate):
{candidate}

Answer in exactly this format:
SCORE: <0.00-1.00> how fully B conveys the same specific thing as A. 1.00 means
a reader of B would picture what A describes, at A's level of specificity.
Penalise vagueness: if B is merely a less specific version of A, that is NOT a
high score. Penalise contradictions harder.
MISSING: <the specific things A states that B does not, semicolon separated, max 5>
WRONG: <the things B states that contradict A, semicolon separated, or: none>"""


def call(prompt, image=None, timeout=300):
    """One blind pass. With `image`, the viewer may read that file and no other;
    without it, the judge gets text alone and no tools at all."""
    if image:
        prompt = (f"Use the Read tool to look at exactly one file: {image}. "
                  f"Do not read anything else.\n{prompt}")
    reading = ["--allowedTools", "Read"] if image else []
    done = subprocess.run(
        ["perl", "-e", "alarm shift; exec @ARGV", str(timeout),
         "claude", "-p", prompt, "--model", "sonnet"] + reading,
        capture_output=True, text=True)
    return done.stdout.strip()


def verdict(pair):
    reference, candidate, timeout = pair
    if not reference or not candidate:
        return None, "a describer returned nothing — re-run", ""
    said = call(JUDGE.format(reference=reference, candidate=candidate), timeout=timeout)
    score = re.search(r"SCORE:\s*([01]?\.\d+|[01])", said)
    missing = re.search(r"MISSING:\s*(.+)", said)
    wrong = re.search(r"WRONG:\s*(.+)", said)
    return (float(score.group(1)) if score else None,
            missing.group(1).strip() if missing else "",
            wrong.group(1).strip() if wrong else "")


def main():
    parse = argparse.ArgumentParser(description=__doc__,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parse.add_argument("subject")
    parse.add_argument("drawing")
    parse.add_argument("inventory", help="parts.json; every entry with a box is scored")
    parse.add_argument("--bar", type=float, default=0.7,
                       help="a part below this has not earned its place (default 0.7)")
    parse.add_argument("--width", type=int, default=520, help="crop is scaled to this width")
    parse.add_argument("--timeout", type=int, default=300)
    parse.add_argument("--full", action="store_true", help="print both paragraphs per part")
    args = parse.parse_args()

    subject = Image.open(args.subject).convert("RGB")
    drawing = Image.open(args.drawing).convert("RGB")
    if drawing.size != subject.size:
        drawing = drawing.resize(subject.size, Image.LANCZOS)

    inventory = json.load(open(args.inventory))
    parts = {name: entry["box"] for name, entry in inventory.items()
             if isinstance(entry, dict) and entry.get("box")}
    if not parts:
        sys.exit("no inventory entry has a box")

    holding = tempfile.mkdtemp(prefix="concepts.")
    crops = {}
    for name, (x, y, w, h) in parts.items():
        for tag, image in (("subject", subject), ("drawing", drawing)):
            cut = image.crop((x, y, x + w, y + h))
            cut = cut.resize((args.width, max(1, round(cut.height * args.width / cut.width))),
                             Image.LANCZOS)
            path = os.path.join(holding, f"{name.replace('/', '_')}.{tag}.png")
            cut.save(path)
            crops[(name, tag)] = path

    with concurrent.futures.ThreadPoolExecutor(min(16, len(crops))) as pool:
        paragraphs = dict(zip(crops, pool.map(
            lambda path: call(DESCRIBE, path, args.timeout), crops.values())))

    with concurrent.futures.ThreadPoolExecutor(min(8, len(parts))) as pool:
        scored = dict(zip(parts, pool.map(verdict, [
            (paragraphs[(name, "subject")], paragraphs[(name, "drawing")], args.timeout)
            for name in parts])))

    rows, failed = {}, []
    for name in parts:
        score, missing, wrong = scored[name]
        if score is None:
            print(f"{name:16s}   —   {missing}")
            continue
        rows[name] = score
        print(f"{name:16s} {score:.2f}   missing: {missing[:96]}")
        if wrong and wrong.lower() != "none":
            print(f"{'':16s}        WRONG: {wrong[:96]}")
        if args.full:
            print(f"{'':16s}   subject: {paragraphs[(name, 'subject')]}")
            print(f"{'':16s}   drawing: {paragraphs[(name, 'drawing')]}")
        if score < args.bar:
            failed.append((name, score))

    if rows:
        print(f"\nmean conceptual fidelity {sum(rows.values()) / len(rows):.2f} "
              f"over {len(rows)} parts (1.00 = as legible as the subject)")
    for name, score in sorted(failed, key=lambda row: row[1]):
        print(f"  FAIL {name} {score:.2f}")
    if failed:
        print("\na part a viewer cannot take the right thing from is a failed stage,\n"
              "not a known fault: it goes back to its ladder before it is placed.\n"
              "Spend the next round in this order and none of it on a part already\n"
              "at the bar. WRONG before MISSING — a contradiction is a fault, an\n"
              "omission is often a choice.")
    else:
        print("\nevery part carries its own reading. This judges what a viewer takes\n"
              "away, never how well it is drawn.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
