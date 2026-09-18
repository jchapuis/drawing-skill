#!/usr/bin/env python3
"""What a blind viewer thinks each part IS, scored against the subject.

Every other instrument here measures presence, placement, value or design, and
an object can pass all of them while reading as a different object entirely: a
helmet that is present, in its box, at the right weight, inside a design that
matches, and that a viewer calls a plate of food. Nothing else in the kit sees
that, because nothing else asks what the thing IS.

This crops each part's box out of BOTH images, asks a blind viewer for its top
three identifications with a confidence each, and scores the drawing by the
confidence it earns on the subject's own first answer:

    score = drawing's confidence in the subject's top concept
            ----------------------------------------------
            subject's confidence in its own top concept

1.00 means the part is as recognisable as the thing it was drawn from. The
subject's own top-1 usually lands at 0.90-0.95, so the denominator is close to
flat and the ratio is readable directly.

Read the losing answers, not only the number. They are a worklist: "animal paw"
says toes instead of fingers and no cuff; "plate of food" says a flat dish with
objects lying on it and no shell curvature. A confident wrong concept is a
better diagnosis than a low score.

SCOPE: this scores RECOGNITION, never likeness. A face can score 1.00 as a
laughing woman and still be the wrong shape for the woman in the subject.
Never quote it as a quality score.

    python3 concepts.py subject.png drawing.png parts.json
    python3 concepts.py subject.png drawing.png parts.json --tier 1 --bar 0.8
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

PROMPT = """This image shows one object cropped out of a larger picture.
Say what it is. Give your top 3 candidate identifications, most likely first,
each with a confidence between 0.00 and 1.00 (they need not sum to 1).
Judge only what is visible. Do not be generous: a low confidence is the right
answer for an unclear shape.
Output exactly three lines, nothing else:
1. <name> <confidence>
2. <name> <confidence>
3. <name> <confidence>"""


def identify(path, timeout):
    """Top three concepts for one crop, blind: a fresh process, one file."""
    asked = (f"Use the Read tool to look at exactly one file: {path}. "
             f"Do not read anything else.\n{PROMPT}")
    done = subprocess.run(
        ["perl", "-e", "alarm shift; exec @ARGV", str(timeout),
         "claude", "-p", asked, "--model", "sonnet", "--allowedTools", "Read"],
        capture_output=True, text=True)
    found = re.findall(r"^\s*\d\.\s*(.+?)\s+([01]?\.\d+|[01])\s*$", done.stdout, re.M)
    return [(name.strip().lower(), float(score)) for name, score in found][:3]


def agrees(concept, answer):
    """Whether one answer names the same thing as the subject's top concept.

    Both are noun phrases from a free-text answer, so compare on their head
    words rather than as strings: "bicycle front wheel" and "front wheel of a
    bicycle" are the same answer, "bicycle wheel" and "wagon wheel" are not.
    """
    stop = {"a", "an", "the", "of", "with", "and", "in", "on", "or", "front",
            "rear", "left", "right", "held", "two", "cartoon", "illustration"}
    heads = lambda text: {word for word in re.findall(r"[a-z]+", text)
                          if word not in stop and len(word) > 2}
    concept_words, answer_words = heads(concept), heads(answer)
    return bool(concept_words & answer_words)


def main():
    parse = argparse.ArgumentParser(description=__doc__,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parse.add_argument("subject")
    parse.add_argument("drawing")
    parse.add_argument("inventory", help="parts.json; every entry with a box is scored")
    parse.add_argument("--bar", type=float, default=0.8,
                       help="a part below this has not earned its name (default 0.8)")
    parse.add_argument("--tier", type=int, default=0,
                       help="only entries at or above this tier, if the inventory has tiers")
    parse.add_argument("--width", type=int, default=520, help="crop is scaled to this width")
    parse.add_argument("--timeout", type=int, default=300)
    args = parse.parse_args()

    subject = Image.open(args.subject).convert("RGB")
    drawing = Image.open(args.drawing).convert("RGB")
    if drawing.size != subject.size:
        drawing = drawing.resize(subject.size, Image.LANCZOS)

    inventory = json.load(open(args.inventory))
    parts = {name: entry["box"] for name, entry in inventory.items()
             if isinstance(entry, dict) and entry.get("box")
             and entry.get("tier", 1) <= (args.tier or 99)}
    if not parts:
        sys.exit("no inventory entry has a box")

    holding = tempfile.mkdtemp(prefix="concepts.")
    jobs = {}
    for name, (x, y, w, h) in parts.items():
        for tag, image in (("subject", subject), ("drawing", drawing)):
            crop = image.crop((x, y, x + w, y + h))
            crop = crop.resize((args.width, max(1, round(crop.height * args.width / crop.width))),
                               Image.LANCZOS)
            path = os.path.join(holding, f"{name.replace('/', '_')}.{tag}.png")
            crop.save(path)
            jobs[(name, tag)] = path

    with concurrent.futures.ThreadPoolExecutor(min(16, len(jobs))) as pool:
        answers = dict(zip(jobs, pool.map(lambda path: identify(path, args.timeout),
                                          jobs.values())))

    print(f"{'part':16s} {'subject reads as':34s} {'drawing reads as':34s}  score")
    scores, failed = {}, []
    for name in parts:
        said, drew = answers[(name, "subject")], answers[(name, "drawing")]
        if not said or not drew:
            print(f"{name:16s} no answer — describer failed, re-run")
            continue
        concept, ceiling = said[0]
        earned = next((score for answer, score in drew if agrees(concept, answer)), 0.0)
        score = min(earned / ceiling, 1.0) if ceiling else 0.0
        scores[name] = score
        if score < args.bar:
            failed.append((name, score, drew[0][0]))
        show = lambda got: f"{got[0][0][:28]} {got[0][1]:.2f}"
        print(f"{name:16s} {show(said):34s} {show(drew):34s}  {score:.2f}")

    if scores:
        mean = sum(scores.values()) / len(scores)
        print(f"\nmean conceptual fidelity {mean:.2f} over {len(scores)} parts "
              f"(1.00 = as recognisable as the subject)")
    for name, score, reading in sorted(failed, key=lambda row: row[1]):
        print(f"  FAIL {name} {score:.2f} — a viewer calls it {reading!r}")
    if failed:
        print("\na part that has not earned its own name is a failed stage, not a known\n"
              "fault: it goes back to its ladder before it is placed. Spend the next\n"
              "round's budget in this order, and none of it on a part already at 1.00.\n"
              "The losing concept is the diagnosis — read it before choosing a mark.")
    else:
        print("\nevery part earns its name. This says nothing about likeness: a part\n"
              "can be the right KIND of thing and the wrong one.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
