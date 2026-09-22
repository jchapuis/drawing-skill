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

Describe THE THING ITSELF, not the picture of it. In one paragraph of 4-6
sentences, for someone who cannot see it: what kind of thing it is, its shape
and proportions, its parts and how they are arranged, its angle to the viewer,
and if it shows a person, their apparent age, sex and expression.

Say NOTHING about how the image is made or how it looks as an image. No
mention of sharpness, blur, focus, resolution, grain or image quality; none of
photograph, illustration, drawing, render, cartoon, cel shading, vector,
outlines, line weight, brushwork or artistic style. A reader must not be able
to tell from your paragraph whether this is a photograph or a drawing.

Describe only what is visible. Where the thing itself is unclear, say plainly
that you cannot tell what it is, rather than guessing."""

JUDGE = """Below are two descriptions, A and B, each written by someone who saw
one picture and not the other. They may or may not describe the same thing.
You cannot see either picture. Judge only from the text.

A (the reference):
{reference}

B (the candidate):
{candidate}

Judge ONLY the thing described, never the manner of depiction. Ignore entirely
any difference in sharpness, blur, focus, resolution, grain, image quality,
medium, or whether one reads as a photograph and the other as a drawing. Those
are properties of the two pictures, not of the thing, and a difference there is
NOT a contradiction. If a paragraph mentions them, discount that clause.

Work claim by claim, not as an impression. Do not rate how similar the two
paragraphs feel — two people describing the same thing word it differently and
that is not a difference in the thing.

1. Extract from A every concrete claim about the thing: what it is, its parts,
   their number and arrangement, its proportions, its orientation. Ignore
   hedges, atmosphere and anything about the picture rather than the thing.
2. For each claim, mark it against B only:
   SUPPORTED   - B states it, or states something that entails it
   CONTRADICTED- B states something incompatible with it
   ABSENT      - B neither states nor contradicts it
   Wording need not match; the same fact said differently is SUPPORTED.

Answer in exactly this format:
CLAIMS: <total number of claims extracted from A>
SUPPORTED: <count>
CONTRADICTED: <count>
SCORE: <(SUPPORTED - CONTRADICTED) / CLAIMS, clamped to 0.00-1.00, two decimals>
MISSING: <the absent claims, semicolon separated, max 5>
WRONG: <the contradicted claims, semicolon separated, or: none>"""


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


def hedges(paragraph):
    """Whether the reference itself failed to read.

    A box whose crop the SUBJECT cannot carry is not a box the drawing can be
    scored against: the reference paragraph is then a guess, it moves between
    runs, and the score measures that movement. This is the skill's "a clause
    the drawing will not earn", detected instead of chased. The usual cause is
    a box small enough that magnifying it yields out-of-focus gradients.
    """
    unsure = ("cannot tell", "can't tell", "unclear", "hard to tell",
              "difficult to tell", "impossible to tell", "not clear what",
              "ambiguous", "indeterminate", "cannot determine", "abstract")
    said = paragraph.lower()
    return sum(said.count(phrase) for phrase in unsure) >= 2


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
    parse.add_argument("--floor", type=float, default=0.45,
                       help="a box whose subject-vs-itself ceiling is below this cannot "
                            "be scored at all (default 0.45)")
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

    # Three paragraphs per part, not two. The subject is described TWICE, by two
    # independent blind viewers, because two viewers shown the same picture do
    # not write the same paragraph and a judge scores their agreement well below
    # 1.00. That agreement is this instrument's ceiling, it differs per box, and
    # without dividing it out the raw score says more about describer variance
    # than about the drawing. Measuring it costs one extra pass and is the only
    # thing that makes the number mean anything.
    passes = [(name, tag) for name in parts for tag in ("subject", "subject2", "drawing")]
    with concurrent.futures.ThreadPoolExecutor(min(24, len(passes))) as pool:
        paragraphs = dict(zip(passes, pool.map(
            lambda job: call(DESCRIBE, crops[(job[0], job[1].replace("2", ""))], args.timeout),
            passes)))

    with concurrent.futures.ThreadPoolExecutor(min(16, 2 * len(parts))) as pool:
        raw = dict(zip(parts, pool.map(verdict, [
            (paragraphs[(name, "subject")], paragraphs[(name, "drawing")], args.timeout)
            for name in parts])))
        ceiling = dict(zip(parts, pool.map(verdict, [
            (paragraphs[(name, "subject")], paragraphs[(name, "subject2")], args.timeout)
            for name in parts])))

    scored = {}
    for name in parts:
        got, missing, wrong = raw[name]
        top = ceiling[name][0]
        if got is None or top is None or top < args.floor:
            scored[name] = (None, missing or
                            f"ceiling {top} — the subject does not describe consistently "
                            f"enough for this box to be scored", wrong)
        else:
            scored[name] = (min(got / top, 1.0), missing, wrong)
    ceilings = {name: ceiling[name][0] for name in parts}

    rows, failed, broken, unscoreable = {}, [], [], []
    for name in parts:
        score, missing, wrong = scored[name]
        if score is None:
            broken.append(name)
            print(f"{name:16s}   —   {missing}")
            continue
        if hedges(paragraphs[(name, "subject")]):
            unscoreable.append(name)
            print(f"{name:16s}   —   the SUBJECT's own crop does not read; box unscoreable")
            continue
        rows[name] = score
        print(f"{name:16s} {score:.2f}  (raw {raw[name][0]:.2f} / ceiling "
              f"{ceilings[name]:.2f})  missing: {missing[:70]}")
        if wrong and wrong.lower() != "none":
            print(f"{'':16s}        WRONG: {wrong[:96]}")
        if args.full:
            print(f"{'':16s}   subject: {paragraphs[(name, 'subject')]}")
            print(f"{'':16s}   drawing: {paragraphs[(name, 'drawing')]}")
        if score < args.bar:
            failed.append((name, score))

    if broken:
        print(f"\n{len(broken)} of {len(parts)} parts returned nothing: "
              f"{', '.join(broken)}.\nThat is the describer failing, not the drawing. "
              f"Re-run before reading anything below.")
    if unscoreable:
        print(f"\n{len(unscoreable)} box(es) unscoreable — the subject's own crop does not "
              f"read: {', '.join(unscoreable)}.\nEither the box is too small to magnify or "
              f"it is on nothing. Fix the box or record it\nat S0 as a clause the drawing "
              f"will not earn. It is excluded from the mean.")
    if not rows:
        sys.exit("\nnothing was scored. No mean, no verdict, no pass.")
    usable = [ceilings[n] for n in rows if ceilings[n]]
    print(f"\nmean conceptual fidelity {sum(rows.values()) / len(rows):.2f} over "
          f"{len(rows)} scored parts, against a measured ceiling of "
          f"{sum(usable)/len(usable):.2f}\n(1.00 = the drawing reads as consistently as "
          f"the subject reads against itself)")
    for name, score in sorted(failed, key=lambda row: row[1]):
        print(f"  FAIL {name} {score:.2f}")
    if failed or broken or unscoreable:
        print("\na part a viewer cannot take the right thing from is a failed stage,\n"
              "not a known fault: it goes back to its ladder before it is placed.\n"
              "Spend the next round in this order and none of it on a part already\n"
              "at the bar. WRONG before MISSING — a contradiction is a fault, an\n"
              "omission is often a choice.")
    else:
        print("\nevery part carries its own reading. This judges what a viewer takes\n"
              "away, never how well it is drawn.")
    sys.exit(1 if (failed or broken or unscoreable) else 0)


if __name__ == "__main__":
    main()
