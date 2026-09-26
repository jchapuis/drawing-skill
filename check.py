#!/usr/bin/env python3
"""Put the drawing in front of yourself in every way that exposes a different error.

    python3 check.py look.png --ref subject.png --grid 6 --out check.png

One image back, so one look costs one Read: the reference, the drawing, the
drawing mirrored, and the drawing squinted. Each panel catches a class of error
the others hide -- mirroring breaks the habituation that makes your own
proportion errors invisible, squinting throws away line and leaves only the
masses, and the reference sitting alongside stops you comparing against memory,
which silently reverts to the symbol you already believed.

`--overlay` instead lays the drawing over the reference so proportion drift
shows up directly rather than having to be judged across a gap.

`--registration` needs no reference at all: it reads the drawing against its own
line art and reports every place the colour and the line disagree.
"""
import argparse
import json
import math
import os
import sys
import textwrap

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))

# a 4x working panel is past PIL's decompression-bomb limit, and so is what
# --masses would make of it; these are our own images
Image.MAX_IMAGE_PIXELS = None


def fit(image, width):
    return image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)


def rule(image, grid, plumbs):
    """Grid and plumb lines. Verticals are judged far more reliably than angles,
    so a landmark that should sit above another is checked against a true
    vertical, never by eye across open space."""
    if not grid and not plumbs:
        return image
    marked = image.convert("RGB").copy()
    pen = ImageDraw.Draw(marked, "RGBA")
    if grid:
        for step in range(1, grid):
            x = marked.width * step / grid
            y = marked.height * step / grid
            pen.line([(x, 0), (x, marked.height)], fill=(220, 60, 60, 70), width=1)
            pen.line([(0, y), (marked.width, y)], fill=(220, 60, 60, 70), width=1)
    for fraction in plumbs:
        x = marked.width * fraction
        pen.line([(x, 0), (x, marked.height)], fill=(30, 110, 230, 150), width=2)
    return marked


def contact(panels, pad=14, label_height=26):
    width = sum(image.width for image, _ in panels) + pad * (len(panels) + 1)
    height = max(image.height for image, _ in panels) + pad * 2 + label_height
    sheet = Image.new("RGB", (width, height), (250, 250, 248))
    pen = ImageDraw.Draw(sheet)
    x = pad
    for image, caption in panels:
        sheet.paste(image, (x, pad + label_height))
        pen.text((x + 2, pad + 6), caption, fill=(35, 35, 35))
        x += image.width + pad
    return sheet



def corners(points, tolerance):
    """Ramer-Douglas-Peucker: the vertices a polyline actually turns on.

    A stroke in ops.json is the RENDERED polyline, interpolated to hundreds of
    points whatever was authored, so counting its points measures the renderer.
    Simplifying it back down measures the drawing: how many faces this shape
    really has.
    """
    if len(points) < 3:
        return len(points)
    start, end = np.array(points[0], float), np.array(points[-1], float)
    line = end - start
    length = np.hypot(*line)
    coords = np.array(points, float)
    if length < 1e-9:
        away = np.hypot(*(coords - start).T)
    else:
        away = np.abs(np.cross(line, coords - start)) / length
    worst = int(np.argmax(away))
    if away[worst] <= tolerance:
        return 2
    return (corners(points[:worst + 1], tolerance)
            + corners(points[worst:], tolerance) - 1)


def _overlap(one, other, cells=160):
    """Intersection over union of two polygons, rasterised on their joint box."""
    both = np.asarray(list(one) + list(other), float)
    low = both.min(axis=0)
    step = max(float(np.ptp(both, axis=0).max()) / cells, 1e-6)
    size = (int(np.ceil(np.ptp(both, axis=0)[1] / step)) + 2,
            int(np.ceil(np.ptp(both, axis=0)[0] / step)) + 2)
    masks = []
    for shape in (one, other):
        mask = np.zeros(size, np.uint8)
        cv2.fillPoly(mask, [np.round((np.asarray(shape, float) - low) / step).astype(np.int32)], 1)
        masks.append(mask.astype(bool))
    union = (masks[0] | masks[1]).sum()
    return float((masks[0] & masks[1]).sum()) / union if union else 0.0


def _settled(outline, reach):
    """A polygon with every bite and spike narrower than `reach` closed away,
    as a closed point list. A traced region of a grainy or upscaled source
    carries a serration of 5-15px along every edge at 4x, which no simplifying
    tolerance that still keeps the real corners removes; opening and closing
    the region's own mask does, and leaves its corners where they were."""
    shape = np.asarray(outline, float)
    low = shape.min(axis=0) - 3 * reach - 2
    step = max(1.0, reach / 4.0)
    size = np.ceil((shape.max(axis=0) - low + 3 * reach + 2) / step).astype(int)
    mask = np.zeros((size[1] + 1, size[0] + 1), np.uint8)
    cv2.fillPoly(mask, [np.round((shape - low) / step).astype(np.int32)], 1)
    radius = max(1, int(round(reach / step)))
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    mask = cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_OPEN, disc), cv2.MORPH_CLOSE, disc)
    found, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not found:
        return list(map(tuple, shape)) + [tuple(shape[0])]
    ring = max(found, key=cv2.contourArea)[:, 0, :] * step + low
    return [tuple(point) for point in ring] + [tuple(ring[0])]


def faces(ops_path, regions_path, ratio, grain=0.0):
    """A flat simpler than the form it lies on.

    An interior flat — a shade, a highlight, a cast shadow lying on a form — is
    bounded by that form's curvature and cannot be simpler than it. Drawn as a
    quad on a form the tracer returns with twenty-five points, it reads as a
    paste-on: a hard-edged patch sitting on the object rather than a turn of its
    surface. No other gate sees it: the flat is the right colour, in the right
    place, covering the right area, and the describer has no word for it.

    Not an absolute floor. A paving joint or a step riser IS a quad, and adding
    points to it only adds noise. The count comes from the traced region the
    flat sits in, so the subject sets it.
    """
    drawn = [op for op in json.load(open(ops_path))
             if op.get("op") == "stroke" and op.get("stage") == "fill"]
    regions = json.load(open(regions_path))
    regions = regions if isinstance(regions, list) else regions.get("regions", [])
    traced = [(reg["box"], [tuple(p[:2]) for p in (reg.get("contour") or reg.get("blockin") or [])])
              for reg in regions if reg.get("box")]
    print(f"{'fill':>5s} {'faces':>6s} {'region':>7s} {'overlap':>8s}  verdict")
    thin = 0
    for index, op in enumerate(drawn):
        points = [(p[0], p[1]) for p in (op.get("points") or [])]
        if len(points) < 3:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        width, height = max(xs) - min(xs), max(ys) - min(ys)
        if width * height < 2500:
            continue
        # The region is the one the flat OVERLAPS, not one whose box holds its
        # centre: a thin tube's centre sits in the box of the whole wheel
        # behind it, and a tube flat was compared against that region's 366
        # corners. And the region is simplified at the flat's own tolerance,
        # which scales with the shape: counted at the tracer's fixed one, a
        # grainy source serrates every edge -- a straight tube came back with
        # 70-230 points, and 31 tube flats on one panel read TOO FEW FACES.
        match, best = None, 0.0
        for box, outline in traced:
            if len(outline) < 3 or box[0] > max(xs) or box[1] > max(ys) \
                    or box[0] + box[2] < min(xs) or box[1] + box[3] < min(ys):
                continue
            share = _overlap(points, outline)
            if share > best:
                match, best = outline, share
        if match is None or best < 0.5:
            continue
        tolerance = max(width, height) * 0.02
        reach = max(tolerance, grain)
        want = corners(_settled(match, reach), tolerance) - 1
        has = corners(_settled(points, reach), tolerance) - 1
        short = has < want * ratio
        thin += short
        print(f"{index:5d} {has:6d} {want:7d} {best:8.2f}{'  TOO FEW FACES' if short else ''}")
    print(f"\n{thin} flat(s) turn fewer corners than the region they sit in. A flat\n"
          f"cannot turn a corner the form under it does not turn: take the count\n"
          f"from the tracer, not from the four corners the shape suggests at a\n"
          f"glance. A shade drawn as a quad on a curved form reads as a patch\n"
          f"stuck to the object rather than as its surface turning away.")
    return thin


def colour(text):
    """A colour given as #rrggbb or as R,G,B -- both forms get typed."""
    text = text.strip()
    if "," in text:
        parts = tuple(int(part) for part in text.split(","))
    else:
        digits = text.lstrip("#")
        if len(digits) != 6:
            sys.exit(f"not a colour: {text!r} (give #rrggbb or R,G,B)")
        parts = tuple(int(digits[at:at + 2], 16) for at in (0, 2, 4))
    if len(parts) != 3 or not all(0 <= part <= 255 for part in parts):
        sys.exit(f"not a colour: {text!r} (give #rrggbb or R,G,B)")
    return parts


def ground_of(fallback, path="palette.json"):
    """The subject's ground: palette.json's `background`, else the fallback."""
    try:
        with open(path) as handle:
            return colour(json.load(handle)["background"])
    except (OSError, ValueError, KeyError):
        return fallback


def marks(row, dark=None):
    """Runs of mark in one row as (start, width), left to right.

    The threshold is the midpoint between the row's ground and its darkest
    value, not a fixed level: a ladder drawn at the `fill` stage sits well
    above any constant a line ladder would use, and a fixed threshold reports
    it as an empty row — the instrument silently failing on exactly the stage
    the skill asks you to calibrate.
    """
    if dark is None:
        ground, deepest = max(row), min(row)
        if ground - deepest < 12:
            return []
        dark = (ground + deepest) / 2
    runs, run = [], 0
    for at, value in enumerate(row):
        if value < dark:
            run += 1
        elif run:
            runs.append((at - run, run))
            run = 0
    if run:
        runs.append((len(row) - run, run))
    return [(start, width) for start, width in runs if width > 1]


def said(runs):
    """Runs as `width@x`, x the run's CENTRE, in the order they sit, so a
    ladder's rungs keep their names: sorted, a list of widths cannot say which
    rung is which. Printed at the run's start, a pole's two lines placed on the
    printed x came back half a line off, 8px, on both sides."""
    return "  ".join(f"{width}@{start + (width - 1) // 2}" for start, width in runs) or "-"


def report(subject, drawing, rows):
    """The weight hierarchy, as numbers rather than as an impression.

    The ratio between a drawing's finest mark and its heaviest is a property of
    the style being drawn, not a universal: a heavily inked comic runs 8-10x, a
    flat cel design nearer 2-3x. Importing the wrong one is invisible at full
    size and unmistakable at 4x, so measure the subject's own range and match it.
    """
    for y in rows:
        found = marks(list(subject.crop((0, y, subject.width, y + 1)).getdata()))
        made = marks(list(drawing.crop((0, y, drawing.width, y + 1)).getdata()))
        print(f"y={y:4d}  subject {said(found)}")
        print(f"        drawing {said(made)}")
    print("\nwidth@x, left to right. match the span, not the individual runs: finest "
          "and heaviest,\nand the ratio between them.")


def zoom(drawing, subject, box, factor=4):
    """One feature, magnified, subject above and drawing below.

    The other checks all measure *placement*: whether a mark landed where it was
    meant to. None of them can see whether the mark is any good -- whether it
    tapers, whether its weight belongs to a hierarchy, whether the shape has one
    continuous curvature or three lumps. Those only show at the scale a hand
    works at, which is much larger than the scale a drawing is judged at, and
    they are most of the difference between a sketch and a finished drawing.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    x, y, width, height = box
    size = (max(1, round(width * factor)), max(1, round(height * factor)))
    above = ruled(subject.crop((x, y, x + width, y + height)).resize(size, Image.LANCZOS), box, factor)
    below = ruled(drawing.crop((x, y, x + width, y + height)).resize(size, Image.LANCZOS), box, factor)
    # a tall box stacked twice came back 8646x16472 and was shown at an eighth
    # of its size: side by side unless the box is wide
    if height > width:
        sheet = Image.new("RGB", (above.width * 2 + 18, above.height + 16), (250, 250, 248))
        pen = ImageDraw.Draw(sheet)
        sheet.paste(above, (0, 16))
        pen.text((4, 2), "subject", fill=(25, 25, 25))
        sheet.paste(below, (above.width + 18, 16))
        pen.text((above.width + 22, 2), "drawing", fill=(25, 25, 25))
        return sheet
    sheet = Image.new("RGB", (above.width, above.height * 2 + 40), (250, 250, 248))
    pen = ImageDraw.Draw(sheet)
    sheet.paste(above, (0, 16))
    pen.text((4, 2), "subject", fill=(25, 25, 25))
    sheet.paste(below, (0, above.height + 34))
    pen.text((4, above.height + 20), "drawing", fill=(25, 25, 25))
    return sheet


def _step(span, target=8):
    """A round tick spacing giving about `target` ticks over `span`."""
    for nice in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000):
        if nice >= span / target:
            return nice
    return 10000


def ruled(image, box, scale):
    """A crop with its panel coordinates ticked along the top and left margin,
    so what you see can be named. Ticks orient; they do not measure -- points
    read off a ticked crop by eye came out 30-60px off at 4x, and `--scan` is
    what gives a coordinate."""
    left, top = 46, 16
    out = Image.new("RGB", (image.width + left, image.height + top), (250, 250, 248))
    out.paste(image, (left, top))
    pen = ImageDraw.Draw(out)
    x, y, width, height = box
    step = _step(max(width, height))
    for at in range(math.ceil(x / step) * step, x + width + 1, step):
        across = left + (at - x) * scale
        pen.line([(across, top - 5), (across, top - 1)], fill=(20, 20, 20))
        pen.text((across + 2, 2), str(at), fill=(20, 20, 20))
    for at in range(math.ceil(y / step) * step, y + height + 1, step):
        down = top + (at - y) * scale
        pen.line([(left - 5, down), (left - 1, down)], fill=(20, 20, 20))
        pen.text((2, down - 5), str(at), fill=(20, 20, 20))
    return out


def palette_value(names_csv):
    """(palette colours, indices wanted) for --value, or None when not given."""
    if not names_csv:
        return None
    with open("palette.json") as handle:
        palette = json.load(handle)
    names = list(palette)
    unknown = [name for name in names_csv.split(",") if name not in names]
    if unknown:
        sys.exit(f"--value: {', '.join(unknown)} is not in palette.json")
    return (np.array([[int(palette[name][at:at + 2], 16) for at in (1, 3, 5)]
                      for name in names], dtype=float),
            [names.index(name) for name in names_csv.split(",")])


def _named(pixels, value):
    """Where an RGB array classifies to one of `value`'s wanted palette names."""
    colours, wanted = value
    flat = pixels.reshape(-1, 3)
    named = np.argmin((colours ** 2).sum(-1) - 2 * flat @ colours.T, axis=1)
    return np.isin(named, wanted).reshape(pixels.shape[:2])


def inks(drawing, subject, box, dark=90, width=1500, value=None):
    """The two LINES over one box, in one image: the subject's ink in blue, the
    drawing's in red, black where they coincide, over the subject in pale grey.

    An outline can match row for row while the likeness is wrong, because a
    likeness is carried by interior lines too -- a nose's ridge, a brow, the
    fold of a cheek. Measured: a face whose right edge sat within 10px of the
    subject's on every row still read wrong, and the fault was the nose's ridge
    line, which ran diagonally from the brow to the nostril in the subject and
    near-vertically down the far edge in the drawing. No outline scan sees an
    interior line. This does, and it gives no number: the question for every
    blue line is which red line is meant to be it, which is a reading, and a
    distance between the two inks would fall as more ink is added."""
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    x, y, w, h = box
    grey = [np.asarray(image.crop((x, y, x + w, y + h)).convert("L"), dtype=float)
            for image in (subject, drawing)]
    base = 255 - (255 - grey[0]) * 0.22
    out = np.stack([base] * 3, axis=-1)
    if value:
        # a dark flat (a glove, bar tape) is under the darkness threshold and
        # came back as one blue mass: classify to the palette's line names
        theirs, ours = (_named(np.asarray(image.crop((x, y, x + w, y + h)).convert("RGB"),
                                          dtype=float), value) for image in (subject, drawing))
    else:
        theirs, ours = grey[0] < dark, grey[1] < dark
    out[theirs & ~ours] = (40, 90, 235)
    out[ours & ~theirs] = (225, 40, 40)
    out[theirs & ours] = (30, 10, 30)
    scale = width / max(w, h)
    image = Image.fromarray(out.astype(np.uint8)).resize(
        (max(1, round(w * scale)), max(1, round(h * scale))), Image.NEAREST)
    return ruled(image, box, scale)


def scan(drawing, subject, box, side, step, ground, dark=90, tolerance=24, value=None):
    """The form's outline and its interior lines, row by row (or column by
    column), subject beside drawing -- the instrument that settles proportion.

    Per row: `edge` is the first pixel, coming in from `side`, that is not the
    ground; `ink` lists the dark runs from that side inward. Read the diff
    column for the outline and the ink columns for the lines inside it: a
    thick line drawn as two strokes shows as one run against two, and an
    interior line drawn in the wrong place shows as runs that drift apart
    while the edges agree. With `value` -- (palette colours, indices wanted) --
    the runs are of those palette names instead of dark: the scan a group of
    vents, an orange insert in a grey shell or a wheel's bands needs, which a
    darkness threshold cannot tell apart."""
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    x, y, w, h = box
    crops = [np.asarray(image.crop((x, y, x + w, y + h)).convert("RGB"), dtype=float)
             for image in (subject, drawing)]
    if side in ("top", "bottom"):
        crops = [np.transpose(crop, (1, 0, 2)) for crop in crops]
        origin, along, lines = x, y, w
    else:
        origin, along, lines = y, x, h
    backwards = side in ("right", "bottom")
    step = step or max(1, round(lines / 40))
    loose = max(4, round(0.02 * (h if side in ("left", "right") else w)))
    axis = "y" if side in ("left", "right") else "x"
    runs_of = "of the --value names" if value else f"darker than {dark}"
    print(f"from the {side}, every {step}px; edge = first non-ground pixel, ink = runs "
          f"{runs_of}, from the {side} inward. panel coordinates.")
    print(f"{axis:>6s}  {'subject':>7s} {'drawing':>7s} {'diff':>5s}   subject ink  |  drawing ink")
    for at in range(0, lines, step):
        edges, runs = [], []
        for crop in crops:
            row = crop[at][::-1] if backwards else crop[at]
            off = np.abs(row - np.asarray(ground, float)).max(axis=1) > tolerance
            first = int(np.argmax(off)) if off.any() else None
            edges.append(None if first is None else
                         (along + len(row) - 1 - first if backwards else along + first))
            if value:
                found = marks(list(np.where(_named(row[None], value)[0], 0, 255)), dark)
            else:
                found = marks(list(row.mean(axis=1)), dark)
            runs.append([(along + len(row) - start - width, along + len(row) - 1 - start)
                         if backwards else (along + start, along + start + width - 1)
                         for start, width in found][:4])
        diff = "" if None in edges else f"{edges[1] - edges[0]:+5d}"
        flag = ("  <<" if diff and abs(edges[1] - edges[0]) > loose else "") + \
               (f"  runs {len(runs[0])}|{len(runs[1])}" if len(runs[0]) != len(runs[1]) else "")
        cells = ["  ".join(f"{a}-{b}" for a, b in found) or "-" for found in runs]
        print(f"{origin + at:6d}  {str(edges[0]):>7s} {str(edges[1]):>7s} {diff:>5s}   "
              f"{cells[0]}  |  {cells[1]}{flag}")
    print(f"\n<< marks an edge more than {loose}px off; `runs a|b` a row whose line count "
          "differs.\nA number here moves a mark; a look at a side-by-side does not: "
          "proportion judged by\neye from a pair was wrong in both directions on one "
          "panel, and a scan settled\nevery case.")


def masses(drawing, subject, box=None, colours=3, blow=3):
    """Both pictures reduced to flat value masses, side by side, with no line.

    This is the check that sees *shape*, and it is the one the rest of the kit
    cannot do. Everything else here compares marks: where they landed, how wide
    they are, whether colour agrees with them. A head can pass every one of those
    -- every feature inside its own measured box, every box within ten pixels of
    the subject's -- and still not be a face, because a wedge and an oval share a
    bounding rectangle and differ in the only way that matters.

    Reducing each picture to a few values throws away the line, the detail and
    the rendering, and leaves the masses the eye actually reads first. Do it
    early, before any contour: if the masses do not say the same thing as the
    subject's, nothing drawn on top of them will fix it.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    if box:
        x, y, width, height = box
        subject = subject.crop((x, y, x + width, y + height))
        drawing = drawing.crop((x, y, x + width, y + height))
    # the line is closed away at a working size, then the design is read at
    # thumbnail size: a panel is brought down to it, a small crop blown up
    work = min(1.0, 1800 / max(subject.size))
    size = (max(1, round(subject.width * work)), max(1, round(subject.height * work)))
    subject, drawing = (image.resize(size, Image.BOX) for image in (subject, drawing))
    # one line width for both, the SUBJECT's: measured on each picture, a
    # drawing inked heavier than its subject had its tyres closed away as line
    radius = _line_radius(subject)
    subject, drawing = (_lineless(image, radius) for image in (subject, drawing))
    fit_to = 900
    shrink = min(1.0, fit_to / max(size))
    size = (max(1, round(size[0] * shrink)), max(1, round(size[1] * shrink)))
    subject, drawing = subject.resize(size, Image.BOX), drawing.resize(size, Image.BOX)
    blow = max(1, min(blow, fit_to // max(size)))
    centres, paint = _levels(subject, colours)
    flat = [_flatten(image, centres, paint).resize((image.width * blow, image.height * blow),
                                                   Image.NEAREST)
            for image in (subject, drawing)]
    gap, label = 20, 18
    sheet = Image.new("RGB", (flat[0].width + flat[1].width + gap * 3,
                              flat[0].height + label + gap * 2), (255, 255, 255))
    pen = ImageDraw.Draw(sheet)
    pen.text((gap, gap), f"subject -- {colours} values, no line", fill=(30, 30, 30))
    pen.text((gap * 2 + flat[0].width, gap), f"drawing -- {colours} values, no line",
             fill=(30, 30, 30))
    sheet.paste(flat[0], (gap, gap + label))
    sheet.paste(flat[1], (gap * 2 + flat[0].width, gap + label))
    return sheet


def _line_radius(image, ink=90):
    """Half the picture's line width: the p75 of per-pixel min(row, column) dark
    runs, runs over 1.5% of the shorter side being dark masses, not line."""
    from trace import line_width
    dark = np.asarray(image.convert("L")) < ink
    widths = line_width(dark, max(4, round(0.015 * min(dark.shape))))
    return max(1, int(np.ceil(np.percentile(widths, 75) / 2))) if widths.size else 0


def _lineless(image, radius, ink=90):
    """The picture with its LINE closed away and its dark masses kept.

    Line is dark and thin: a dark pixel a disc of the image's own line width
    cannot sit in. Those pixels, and a one-pixel skin of anti-aliasing round
    them, take the colour of the nearest pixel that is not line. A dark MASS --
    black shorts, a tyre -- is wider than the disc and stays.

    This happens before any value is chosen, and it has to. Quantising first
    and dropping the darkest cluster afterwards did two wrong things, both
    measured: an inked subject's line dragged its skin into the light class
    while the same skin on an ink-less stage-2 drawing fell dark, so the gate
    reported a difference that was only the ink the stage forbids; and on a
    drawing whose ground outnumbers everything else, a median cut spent every
    cluster but one on shades of the ground, the whole figure landed in the
    darkest cluster, and dropping it left the drawing as a blank field.
    """
    pixels = np.asarray(image.convert("RGB"))
    dark = np.asarray(image.convert("L")) < ink
    if not radius:
        return image
    span = np.arange(-radius, radius + 1)
    disc = (span[:, None] ** 2 + span[None, :] ** 2) <= radius ** 2
    line = dark & ~ndimage.binary_opening(dark, structure=disc)
    line = ndimage.binary_dilation(line) & ~ndimage.binary_opening(dark, structure=disc)
    if not line.any() or line.all():
        return image
    _, (rows, cols) = ndimage.distance_transform_edt(line, return_indices=True)
    return Image.fromarray(pixels[rows, cols])


def _levels(image, colours):
    """`colours` value levels, by 1-D k-means on the SUBJECT's lightness, and the
    mean colour of each. Lightness, because a design is read in value; k-means,
    because a median cut splits the most POPULOUS colour and on a picture that
    is mostly ground spends its levels on the ground. The subject's, because
    each picture quantised to its own levels put one flat -- the same palette
    colour on both -- in the mid class of one and the dark class of the other."""
    pixels = np.asarray(image.convert("RGB"), dtype=float)
    value = pixels.mean(axis=2)
    centres = np.percentile(value, np.linspace(5, 95, colours))
    for _ in range(30):
        label = np.abs(value[..., None] - centres).argmin(axis=2)
        moved = np.array([value[label == level].mean() if (label == level).any() else centres[level]
                          for level in range(colours)])
        if np.allclose(moved, centres):
            break
        centres = moved
    label = np.abs(value[..., None] - centres).argmin(axis=2)
    paint = np.array([pixels[label == level].mean(axis=0) if (label == level).any() else (0, 0, 0)
                      for level in range(colours)])
    return centres, paint


def _flatten(image, centres, paint):
    """Every pixel to the nearest of the subject's value levels."""
    value = np.asarray(image.convert("RGB"), dtype=float).mean(axis=2)
    label = np.abs(value[..., None] - centres).argmin(axis=2)
    return Image.fromarray(paint[label].astype(np.uint8), "RGB")


def unfilled(drawing, subject, paper, ground, ink=90, thickness=3):
    """Paper inside the subject's silhouette: a flat that stops short of its ink.

    `--registration` alone finds only paper the line art walls in completely. A
    fill that falls short along an OPEN boundary leaves a bay, not an island —
    the background flood reaches it and the gate calls it outside. That bay is
    the commoner fault by far, and it reads as a pale notch bitten out of the
    object wherever the ink is thin or the contour bulges.

    The subject settles it: anywhere the subject carries the object, the drawing
    must carry ink or colour and never bare paper. Two colours, then, and they
    are not the same one: the subject's GROUND (palette.json's `background`)
    says where the object is, and the render's PAPER says where the drawing is
    bare. Read as one colour, a check copy rendered on a paper nothing paints
    with made every pixel of the subject "object" -- the road between spokes,
    a wheel's interior -- and on one panel every region holding spokes or
    pebbles reported as unfilled. The rule this enforces is
    already in the ladder — a flat is drawn PAST where its ink will go, so the
    ink covers the flat's edge, never the other way round. Trap outward by at
    least half the heaviest nib.
    """
    drawing = drawing.convert("RGB").resize(subject.size, Image.LANCZOS)
    drawn = np.asarray(drawing, dtype=np.int16)
    try:
        painted = json.load(open("palette.json"))
        clash = [name for name, value in painted.items()
                 if name != "background" and isinstance(value, str)
                 and value.lstrip("#").lower() ==
                 "".join(f"{int(c):02x}" for c in paper)]
        if clash:
            print(f"WARNING: --paper is also {', '.join(clash)} in palette.json. "
                  f"Every flat\nyou paint in it will read as bare ground and this "
                  f"gate is then noise.\nPass a colour the drawing never paints with.\n")
    except (OSError, ValueError):
        pass
    shown = np.asarray(subject.convert("RGB"), dtype=np.int16)
    object_here = np.abs(shown - np.asarray(ground, dtype=np.int16)).max(axis=2) > 24
    paper = np.asarray(paper, dtype=np.int16)

    bare = np.abs(drawn - paper).max(axis=2) <= 18
    bare &= drawn.mean(axis=2) >= ink
    holes = ndimage.binary_opening(object_here & bare, np.ones((thickness, thickness)))

    labels, count = ndimage.label(holes)
    if not count:
        print("no bare paper inside the subject's silhouette: every flat reaches its ink.")
        return 0
    sizes = ndimage.sum(holes, labels, range(1, count + 1))
    # 120px at a delivered size of about a megapixel, and the same share of a
    # 4x working space: a fixed floor lists every hairline of drift at 4x
    floor = max(120, holes.size * 1.1e-4)
    keep = [index for index in range(1, count + 1) if sizes[index - 1] >= floor]
    print(f"{len(keep)} unfilled patch(es) — bare paper where the subject has the object:")
    # every patch, not the largest dozen: a bare triangle of jersey at a seam
    # between two drawers' sections was the 18th of 30 and no drawer saw it
    for index in sorted(keep, key=lambda i: -sizes[i - 1]):
        ys, xs = np.nonzero(labels == index)
        print(f"  {int(sizes[index - 1]):6d}px at x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
    print("\na flat is drawn PAST where its ink will go, so the ink covers the flat's\n"
          "edge. Taking a fill's outline from the tracer puts it at the colour\n"
          "transition, which is INSIDE the ink: the flat then falls short by half a\n"
          "line width and the ground shows through wherever the contour bulges out.")
    return len(keep)


def registration(drawing, paper, ink=90, floor=40):
    """Where colour and line disagree — the flatter's own check, run on a render.

    `colour.md` names two failures exactly, and they have an exact definition in
    pixels once you stop to write it down. Flood the picture inward from its
    border, through anything that is not line, and the drawing splits in two:
    what the line encloses, and what it does not.

    - A **spill** is colour the flood reached: it lies outside the line art, so
      nothing covers its edge and it reads as a smear beside the drawing.
    - A **gap** is paper the flood did *not* reach: it is walled in by line and
      colour on every side, so it reads as a hole.
    - And where the flood pours into a region it should not have reached, the
      line art is **open** — the recurring flatting fault, a contour that does
      not close, which is the same defect seen from the other side.

    This finds them; it does not fix them. What to do about each one is a
    drawing decision, and the answer is often "nothing" — a trap that wanders
    under its own line is supposed to be there.
    """
    pixels = np.asarray(drawing.convert("RGB"), dtype=np.int16)
    tone = pixels.mean(axis=2)
    is_paper = np.abs(pixels - np.asarray(paper, dtype=np.int16)).max(axis=2) <= 18
    is_line = tone < ink

    # Everything reachable from the paper at the border without crossing a line.
    # The seeds are the bare paper only, never every border pixel: a shape is
    # *supposed* to run off the edge of the picture rather than stop on it, and
    # seeding the whole border would call every one of those a spill.
    open_ground = ~is_line
    border = np.zeros_like(open_ground)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    outside = ndimage.binary_propagation(border & is_paper & open_ground, mask=open_ground)

    spill = outside & ~is_paper & ~is_line
    gap = is_paper & ~outside

    # a one-pixel skin of both is just the renderer's anti-aliasing; open the
    # masks so only faults with real thickness survive
    found = []
    for name, mask in (("spill", spill), ("gap", gap)):
        solid = ndimage.binary_opening(mask, np.ones((3, 3)), iterations=1)
        labels, count = ndimage.label(solid)
        for index in range(1, count + 1):
            ys, xs = np.where(labels == index)
            if len(ys) < floor:
                continue
            found.append((len(ys), name, int(xs.min()), int(ys.min()),
                          int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)))
    return sorted(found, reverse=True)


def self_crossing(ops, step=2, floor=400):
    """Closed fills whose outline doubles back on itself and leaves a hole.

    The renderer fills by winding number, so an outline that crosses itself is
    solid until part of it runs back the other way; that part winds to zero and
    shows the ground. A face's run-on points typed at the head of its traced
    list instead of at their place round it left ground across the forehead,
    and every other gate passed. Yields (op index, hole area, a point in it)."""
    for index, op in enumerate(ops):
        points = np.asarray([p[:2] for p in op.get("points") or []], dtype=float)
        if op.get("op") != "stroke" or op.get("stage") != "fill" or not op.get("closed") \
                or len(points) < 4:
            continue
        low, high = points.min(axis=0), points.max(axis=0)
        xs, ys = np.meshgrid(np.arange(low[0], high[0], step), np.arange(low[1], high[1], step))
        winding = np.zeros(xs.shape, dtype=int)
        for (x0, y0), (x1, y1) in zip(points, np.roll(points, -1, axis=0)):
            side = (x1 - x0) * (ys - y0) - (xs - x0) * (y1 - y0)
            winding += ((y0 <= ys) & (y1 > ys) & (side > 0)).astype(int)
            winding -= ((y1 <= ys) & (y0 > ys) & (side < 0)).astype(int)
        filled = winding != 0
        hole = ndimage.binary_fill_holes(filled) & ~filled
        area = int(hole.sum()) * step * step
        if area >= floor:
            row, column = np.argwhere(hole)[0]
            yield index, area, (int(xs[row, column]), int(ys[row, column]))


# --- what the script puts on the page -----------------------------------------
#
# The script-reading gates below used to read the op list as if every stroke
# were visible. It is not: the canvas paints in write order, `erase` removes a
# stage, `back` sends one under everything, and a closed flat hides whatever
# was written before it. A gate that ignores that lists every correct occlusion
# as a fault -- one panel's --doubled worklist was 29 items, and on inspection
# every one was a far edge that a nearer flat, written after it, already hid.

STROKE_SIZES = {"s": 2.0, "m": 3.5, "l": 5.0, "xl": 10.0}
STAGE_SIZE = {"gesture": "m", "ink": "m"}


def nib(op):
    """A stroke's rendered width in page units: (tldraw size + 1) x scale."""
    size = op.get("size") or STAGE_SIZE.get(op.get("stage"), "s")
    return (STROKE_SIZES.get(size, 3.5) + 1.0) * float(op.get("scale") or 1.0)


def paint_order(ops):
    """{op index: z} for every stroke still on the page after erase/back/clear,
    and the set of those faded or translucent, replayed as the canvas does."""
    live, faded = [], set()
    for index, op in enumerate(ops):
        kind, stage = op.get("op"), op.get("stage")
        if kind == "stroke":
            live.append(index)
            if float(op.get("opacity", 1.0)) < 1.0:
                faded.add(index)
        elif kind == "erase":
            live = [at for at in live if ops[at].get("stage") != stage]
        elif kind == "back":
            live = ([at for at in live if ops[at].get("stage") == stage]
                    + [at for at in live if ops[at].get("stage") != stage])
        elif kind == "fade":
            faded |= {at for at in live if ops[at].get("stage") == stage}
        elif kind == "clear":
            live = []
    return {at: z for z, at in enumerate(live)}, faded


class Cover:
    """Every opaque closed flat on the page, rasterised with its depth: how far
    inside its own edge a point lies, counting the outline stroke a flat is
    drawn with. `under(points, z)` says, per point, how deeply the flats
    painted ABOVE z bury it."""

    def __init__(self, ops):
        self.z, faded = paint_order(ops)
        spread = [p for at in self.z for p in ops[at].get("points", [])[:1]]
        extent = max([abs(c) for p in spread for c in p[:2]] + [1.0])
        self.cell = max(1.0, extent / 1500.0)
        self.flats = []
        for at, z in self.z.items():
            op = ops[at]
            if (not op.get("closed") or op.get("fill") in (None, "none") or at in faded
                    or len(op.get("points", [])) < 3):
                continue
            points = np.asarray([p[:2] for p in op["points"]], float) / self.cell
            low = np.floor(points.min(axis=0)).astype(int) - 2
            high = np.ceil(points.max(axis=0)).astype(int) + 2
            mask = np.zeros((high[1] - low[1] + 1, high[0] - low[0] + 1), np.uint8)
            cv2.fillPoly(mask, [np.round(points - low).astype(np.int32)], 1)
            inside = cv2.distanceTransform(mask, cv2.DIST_L2, 3) * self.cell
            self.flats.append((at, z, low, inside, nib(op) / 2.0, op.get("tag", "")))

    def depth(self, points, flat):
        """How deep inside one flat each point lies; negative outside."""
        _, _, low, inside, rim, _ = flat
        cells = np.round(points / self.cell).astype(int) - low
        rows, cols = inside.shape
        ok = (cells[:, 0] >= 0) & (cells[:, 0] < cols) & (cells[:, 1] >= 0) & (cells[:, 1] < rows)
        out = np.full(len(points), -1.0)
        out[ok] = inside[cells[ok, 1], cells[ok, 0]]
        out[ok & (out > 0)] += rim
        return out

    def buried(self, points, z, reach):
        """Per point: is it covered by `reach` or more under a flat above z?"""
        hidden = np.zeros(len(points), bool)
        if not len(points):
            return hidden
        low, high = points.min(axis=0), points.max(axis=0)
        for flat in self.flats:
            if flat[1] <= z:
                continue
            corner = flat[2] * self.cell
            far = corner + np.array(flat[3].shape[::-1]) * self.cell
            if (far < low).any() or (corner > high).any():
                continue
            hidden |= self.depth(points, flat) >= reach
        return hidden


def doubled(ops, touch=3.0, near_ends=8.0, floor=15.0):
    """Is any edge stated twice ON THE PAGE? Reads the script, and replays it.

    The commonest mark-level fault in a scene is one boundary drawn once as one
    object's silhouette and again as its neighbour's, from two different
    guesses. On the page it reads as a field of crossing loops and gets
    diagnosed for rounds as bad curve control, which it is not. No check that
    looks at pixels finds it: two contours 2px apart are two correct-looking
    contours.

    So it is checked where the fault actually lives -- in the script, as two ink
    strokes whose centrelines run together for a long way. Three things make a
    naive version flag correct work, and all three look right:

    1. **A shared endpoint is not a doubled edge.** Two strokes that meet at one
       named point must pass through that point, so every correct junction looks
       like an overlap. Runs anchored at a shared endpoint are excluded.
    2. **Length is arc length, not a sample count.** Densifying repeats each
       segment's endpoint as the next segment's start, so a 4px stretch counts
       as a dozen samples and every measured run comes back about twice its
       size.
    3. **A covered edge is not on the page.** The far form's outline runs on
       under the nearer form's flat, written after it, and so does the near
       form's ink over the same spot: two strokes in the script, one line on
       the page. Read without the write order, every correct occlusion in one
       panel came back as a doubling (29 items, none real). A run where the
       earlier stroke is buried under a later flat by half its own width is
       dropped; if that flat is ever moved, the doubling comes back here.
    """
    cover = Cover(ops)
    lines = []
    for index, op in enumerate(ops):
        if op.get("op") != "stroke" or op.get("stage") != "ink" or index not in cover.z:
            continue
        points = np.asarray([[point[0], point[1]] for point in op["points"]], dtype=float)
        walked = _walk(points)
        lines.append((index, op.get("tag", "-"), walked, points, cover.z[index], nib(op) / 2.0,
                      walked.min(axis=0) - touch, walked.max(axis=0) + touch))
    trees = [cKDTree(line[2]) for line in lines]
    hits, worst = [], 0.0
    for first in range(len(lines)):
        for second in range(first + 1, len(lines)):
            one, other = lines[first], lines[second]
            if (one[7] < other[6]).any() or (other[7] < one[6]).any():
                continue
            here = one[2]
            ends = np.vstack([one[3][[0, -1]], other[3][[0, -1]]])
            close = trees[second].query(here, distance_upper_bound=touch)[0] < touch
            lower = one if one[4] < other[4] else other
            at = 0
            while at < len(close):
                if not close[at]:
                    at += 1
                    continue
                start = at
                while at < len(close) and close[at]:
                    at += 1
                run = here[start:at]
                if len(run) < 2:
                    continue
                # every point of the run sitting near a shared end means the run
                # IS the sharing, not a second copy of the edge
                if np.linalg.norm(run[:, None, :] - ends[None, :, :], axis=2).min(axis=1).max() <= near_ends:
                    continue
                if cover.buried(run, lower[4], lower[5]).mean() >= 0.8:
                    continue
                length = float(np.linalg.norm(np.diff(run, axis=0), axis=1).sum())
                worst = max(worst, length)
                if length > floor:
                    hits.append((one[0], one[1], other[0], other[1], round(length)))
    return hits, worst, len(lines)


def depth(ops, inventory):
    """Does the write order deliver the occlusion the inventory decided on?

    Occlusion is the order marks are written in and nothing else provides it: a
    flat cannot hide ink, because the ink is above it. So for any two forms that
    overlap, every ink stroke of the FAR one has to be written before the first
    flat of the NEAR one. Write them the other way round -- all the fills
    together, then all the inks, which is how the ladder reads if the stages are
    taken as four passes over the whole drawing -- and the far form's outline is
    laid down on top of the near form's colour and runs straight across it. On
    the page that is a stray edge through the middle of the nearer object, and
    it reads as a crease or a seam that is not there.

    Nothing that looks at pixels finds it, because there is nothing wrong with
    the pixels: every flat is present, filled, registered and inside its box,
    and the stray edge is a perfectly good line. It is checked here, in the
    script, against the `in_front` column the interfaces table already records.

    Two things a naive version gets wrong:

    1. **It is the far form's LAST ink against the near form's FIRST fill.** A
       form is many ops, so comparing any other pair of extremes passes a
       document that interleaves the two forms wrongly in the middle.
    2. **An unmatched name must fail, not pass.** The gate can only see a pair
       whose inventory names and stroke tags are one vocabulary. If the tags use
       a private shorthand, every pair silently resolves to nothing and the gate
       prints a clean bill over an unchecked drawing -- the worst thing a gate
       can do. Unresolved rows are reported as loudly as failures and exit
       non-zero.
    """
    def owns(tag, name):
        return any(part == name or part.startswith(name + ".")
                   for part in str(tag).split("+"))

    pairs = []
    for key, entry in inventory.items():
        near = entry.get("in_front") if isinstance(entry, dict) else None
        if not near:
            continue
        sides = key.split("/")
        far = [side for side in sides if side != near]
        pairs.append((key, near, far[0] if len(sides) == 2 and len(far) == 1 else None))

    names = {name for _, near, far in pairs for name in (near, far) if name}
    first_fill, last_ink = {}, {}
    for index, op in enumerate(ops):
        tag = op.get("tag")
        if not tag:
            continue
        for name in names:
            if not owns(tag, name):
                continue
            if op.get("stage") == "fill":
                first_fill.setdefault(name, index)
            elif op.get("stage") == "ink":
                last_ink[name] = index

    hits, unresolved = [], []
    for key, near, far in pairs:
        if far is None:
            unresolved.append((key, f"the key does not name exactly two objects either side of '{near}'"))
        elif near not in first_fill:
            unresolved.append((key, f"no fill is tagged '{near}'"))
        elif far not in last_ink:
            unresolved.append((key, f"no ink is tagged '{far}'"))
        elif last_ink[far] > first_fill[near]:
            hits.append((key, far, last_ink[far], near, first_fill[near]))
    return hits, unresolved, len(pairs)


def crossings(ops, inventory, floor=None):
    """Where one part's ink runs inside ANOTHER part's flat, for pairs that no
    interface row decides. --depth checks only the rows it is given, so a pair
    nobody listed passed it unchecked while its gate printed PASSES.

    Parts are the inventory's own keys; a stroke belongs to the longest key its
    tag starts with, and two parts related as parent and child, or named
    together in one '+' tag, are one form here. For each unlisted pair it says
    how far the ink runs inside the other's flat and whether the write order
    shows it (drawn across that flat) or hides it (buried under it). Neither is
    a verdict: an unlisted strap drawn over a jersey is right to show, and a
    far outline buried under a near flat is how occlusion is drawn. It is the
    list of occlusions nobody decided."""
    keys = sorted((key for key in inventory if "/" not in key and not key.startswith("_")),
                  key=len, reverse=True)
    rows = [key.split("/") for key, entry in inventory.items()
            if "/" in key and isinstance(entry, dict)]

    def part(name):
        return next((key for key in keys if name == key or name.startswith(key + ".")), name)

    def kin(one, other):
        return one == other or one.startswith(other + ".") or other.startswith(one + ".")

    def listed(one, other):
        return any((kin(one, a) and kin(other, b)) or (kin(one, b) and kin(other, a))
                   for a, b in (row for row in rows if len(row) == 2))

    cover = Cover(ops)
    frame = [op for op in ops if op.get("stage") == "frame"]
    span = np.ptp(np.asarray([p[:2] for p in frame[0]["points"]], float), axis=0) if frame else [1000, 1000]
    floor = floor or max(15.0, 0.005 * float(np.hypot(*span)))
    found = {}
    for index, z in cover.z.items():
        op = ops[index]
        if op.get("stage") != "ink" or not op.get("tag"):
            continue
        owners = [part(name) for name in str(op["tag"]).split("+")]
        samples = _walk(np.asarray([p[:2] for p in op["points"]], float), step=cover.cell)
        reach = nib(op) / 2.0
        mine = [flat for flat in cover.flats if any(kin(part(str(flat[5]).split("+")[0]), owner)
                                                     for owner in owners)]
        for flat in cover.flats:
            other = part(str(flat[5]).split("+")[0]) if flat[5] else None
            if other is None or any(kin(owner, other) for owner in owners) or \
                    listed(owners[0], other):
                continue
            inside = cover.depth(samples, flat) >= reach
            if not inside.any():
                continue
            above = flat[1] > z
            if not above:
                # the ink's own flat, painted over the other's, puts it in front
                for own in mine:
                    if own[1] > flat[1]:
                        inside &= ~(cover.depth(samples, own) >= 0)
            length = float(inside.sum()) * cover.cell
            if length < floor:
                continue
            key = (owners[0], other, "hidden under" if above else "drawn across")
            found[key] = found.get(key, 0.0) + length
    return sorted(((round(length),) + key for key, length in found.items()), reverse=True)


def _walk(points, step=1.0):
    """Even samples along a polyline, without repeating the shared endpoints."""
    out = [points[0]]
    for at in range(len(points) - 1):
        span = points[at + 1] - points[at]
        length = float(np.hypot(*span))
        if length < 1e-9:
            continue
        for part in range(1, max(1, round(length / step)) + 1):
            out.append(points[at] + span * (part / max(1, round(length / step))))
    return np.asarray(out)


def plain(text):
    """Fold the typography a shape sentence gets written with down to what the
    default bitmap font can actually draw. An em dash rendered as a tofu box in
    the middle of a claim is a claim the drawer has to guess at."""
    for fancy, flat in (("\u2014", "--"), ("\u2013", "-"), ("\u2018", "'"),
                        ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
                        ("\u2026", "..."), ("\u00d7", "x"), ("\u00b0", "deg"),
                        ("\u2192", "->"), ("\u00a0", " ")):
        text = text.replace(fancy, flat)
    return "".join(character if character.isprintable() and ord(character) < 127
                   else "?" for character in text)


def read_inventory(path):
    """Load `parts.json`, in either of the two forms an entry may take.

    The old form is a bare box -- `"nose": [540, 336, 45, 50]` -- and it still
    loads, because five drawings on disk are written that way. It is not the
    form to write a new one in. A box states where a part is and says nothing
    about what it is, so a box is the only thing any check can compare it
    against, and the check then passes anything of the right size in the right
    place. That is the measured difference between the two halves of one
    drawing: a body read in sentences came out structurally right, and a face
    read in boxes came out monstrous.

    The form to write is a sentence with a box derived from it:

        "nose": {
          "shape": "a hooked wedge, bridge dead straight, tip dropping below
                    the nostril line",
          "box": [540, 336, 45, 50],
          "front_of": "face",
          "touches": "moustache"
        }

    A junction is an entry like any other -- `"bike.bar/rider.hand"`, keyed in
    the stroke-tag vocabulary so --depth can resolve it, with a sentence saying
    which is in front and how wide the gap is. It needs no machinery of its own,
    and it is where every scene here has failed.
    """
    with open(path) as handle:
        raw = json.load(handle)
    inventory = {}
    for name, entry in raw.items():
        if name.startswith("_"):
            continue
        if isinstance(entry, dict):
            if "box" not in entry:
                sys.exit(f"parts.json: {name!r} has no box")
            inventory[name] = {"box": entry["box"],
                               "tier": entry.get("tier"),
                               "shape": " ".join(str(entry.get("shape", "")).split()),
                               "rel": " ".join(part for part in (
                                   f"in front of {entry['front_of']}" if entry.get("front_of") else "",
                                   f"touches {entry['touches']}" if entry.get("touches") else "",
                                   f"gap {entry['gap']}" if entry.get("gap") else "") if part)}
        else:
            inventory[name] = {"box": entry, "tier": None, "shape": "", "rel": ""}
    return inventory


def checklist(inventory_path, references=None):
    """Sub-forms a reference names for an object the inventory holds, with no
    entry of their own and no written reason in `_absent`.

    A reference's list of sub-forms was read and not acted on: the inventory of
    a bicycle stopped at the crank, and the drawing had no derailleur, chain or
    cassette. Prose that is read and skipped is a gate that does not exist, so
    each reference carries a ```checklist block --

        object: bike|bicycle
        sub-forms: tyre|tire rim spoke ...

    -- and an object is present when any dotted segment of any key names it. A
    sub-form is present when a segment is the word or its plural; alternatives
    are joined by |. `_absent` in parts.json is one string, "name: reason; ..."."""
    import glob
    import re
    with open(inventory_path) as handle:
        raw = json.load(handle)
    segments = {part for key in raw if not key.startswith("_")
                for side in key.split("/") for part in side.split(".")}
    excused = {item.split(":")[0].strip() for item in str(raw.get("_absent", "")).split(";")
               if ":" in item}
    named = lambda words: any(word in segments or word + "s" in segments for word in words.split("|"))
    missing = []
    for path in sorted(references or glob.glob(os.path.join(HERE, "reference", "*.md"))):
        text = open(path).read()
        for block in re.findall(r"```checklist\n(.*?)```", text, re.S):
            fields = dict(line.split(":", 1) for line in block.strip().splitlines() if ":" in line)
            if not named(fields["object"].strip()):
                continue
            gone = [words for words in fields["sub-forms"].split()
                    if not named(words) and not set(words.split("|")) & excused]
            if gone:
                missing.append((fields["object"].strip(), os.path.basename(path), gone))
    return missing


def census(drawing, subject, inventory_path, palette_path, min_area):
    """The count of a group of repeated forms, on the subject and on the drawing,
    against the number the census wrote down.

    Every other gate passes cleanly on an absence. A group of small forms can be
    culled before any drawing rule sees it -- dropped under a trace's minimum
    area, handed to a neighbour as line, deferred at the census and never
    counted -- and the masses gate still passes, because at thumbnail size a
    spray of droplets does not change the design. An entry opts in with
    `"count": N` and `"value": "black+grey"`, the palette names its forms carry;
    each box is classified to the palette on both images and the connected forms
    of those values are counted."""
    with open(inventory_path) as handle:
        raw = json.load(handle)
    with open(palette_path) as handle:
        palette = json.load(handle)
    # the ground is classified too, never counted: left out, it went to the
    # nearest real name and a field of ground counted as one of the forms
    names = list(palette)
    colours = np.array([[int(palette[name][at:at + 2], 16) for at in (1, 3, 5)]
                        for name in names], dtype=float)
    drawing = drawing.resize(subject.size, Image.NEAREST) if drawing.size != subject.size else drawing
    # a form must be THICK, not merely large: an upscale's ramp along every line
    # classifies as specks of a real flat, thin and long, and at 4x an area floor
    # counted 90 of a subject's 14 droplets. An inscribed radius of a quarter of
    # the line's half-width counts 14 and drops no real form, at 1x or 4x alike
    thick = _line_radius(subject) / 4
    rows = []
    for key, entry in raw.items():
        if not isinstance(entry, dict) or "count" not in entry:
            continue
        x, y, width, height = (int(round(value)) for value in entry["box"])
        wanted = [names.index(name) for name in str(entry.get("value", "black")).split("+")
                  if name in names and name != "background"]
        found = []
        for image in (subject, drawing):
            pixels = np.asarray(image.crop((x, y, x + width, y + height)), dtype=float)
            labels = np.argmin((colours ** 2).sum(-1) - 2 * pixels @ colours.T, axis=2)
            forms, count = ndimage.label(np.isin(labels, wanted), structure=np.ones((3, 3)))
            sizes = np.asarray(ndimage.sum(np.ones_like(forms), forms, range(1, count + 1)))
            depth = np.asarray(ndimage.maximum(ndimage.distance_transform_edt(forms > 0), forms,
                                               range(1, count + 1)))
            found.append(int(((sizes >= min_area) & (depth >= thick)).sum()) if count else 0)
        rows.append((key, int(entry["count"]), found[0], found[1]))
    return rows


def parts(drawing, subject, inventory, cell=210, across=4, ink=110, pad=0.2,
          ground=12.0):
    """Every named part of the picture, subject above and drawing below.

    The other checks all ask the same question -- is this mark right? -- and
    none of them can see an *absence*. A registration flood finds colour that
    disagrees with a line; `--weights` compares the widths of marks that exist;
    `--zoom` confirms that one mark landed where it was aimed. A face with no
    nose passes all three, because nothing in the drawing is wrong; something is
    missing, and missing has no pixels to measure.

    So the inventory is written first, before any mark, and this puts all of it
    in front of you at once, at a size where form can be judged. The boxes come
    from the *subject*, and the drawing is cropped by the same box, which is why
    it catches displacement as well as absence: a box that frames an ear in the
    subject and a blank cheek in the drawing has told you something no amount of
    measuring the marks that are there ever would.

    Each box is padded by a fifth before cropping, so a part that has *moved*
    reads as a part that has moved rather than as two unrelated pictures. Cropped
    tight, a displaced feature and an absent one look identical and you cannot
    tell which way it went.

    The percentages are the share of dark pixels in each box. On a single part
    they are a weak hint -- they flag one missing from bare ground and say
    nothing when some other part has drifted into its box. **Read them across
    the whole inventory instead**: a consistent offset in the same direction on
    every part is a real finding and one this check is uniquely placed to make.
    A drawing running ten to twenty points heavier than its subject in every box
    is not a collection of local faults, it is a weight ladder whose top rung was
    matched and whose lower rungs are being spent far too freely, and there is no
    other way to see it.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    down = math.ceil(len(inventory) / across)
    label, gap, line = 15, 10, 11
    # The sentence is printed above the crops, so the verdict is written against
    # what the reading actually claimed rather than against a bare picture. A
    # check can only verify what the reading stated; if the band is empty, this
    # check is comparing a box to a box.
    said = [plain(" -- ".join(part for part in (entry["shape"], entry["rel"]) if part))
            for entry in inventory.values()]
    # Four lines, and an overflow is shown rather than trimmed away. A sentence
    # that will not fit in four lines of this band is too long to be a shape
    # sentence, and silently cutting one is the fault this whole band exists to
    # remove -- it would leave the drawer checking against half a claim.
    wrapped, over = [], []
    for sentence in said:
        block = textwrap.wrap(sentence, width=max(12, cell // 6))
        wrapped.append(block[:4])
        over.append(len(block) > 4)
    head = label + line * max([len(block) for block in wrapped] + [0])
    sheet = Image.new("RGB", (across * (cell + gap) + gap,
                              down * (cell * 2 + head + label + gap) + gap), (250, 250, 248))
    pen = ImageDraw.Draw(sheet)
    whole = [np.asarray(image.convert("L")).astype(float) for image in (subject, drawing)]
    pace = min(1.0, (lambda a, b: b / a if a > 1e-6 else 1.0)(
        *[float((np.abs(g - np.median(g)) > ground).mean()) for g in whole]))
    for index, (name, entry) in enumerate(inventory.items()):
        x, y, width, height = entry["box"]
        spare = round(max(width, height) * pad)
        tight = (x, y, x + width, y + height)
        x, y = max(0, x - spare), max(0, y - spare)
        width = min(subject.width - x, width + spare * 2)
        height = min(subject.height - y, height + spare * 2)
        column, row = index % across, index // across
        left = gap + column * (cell + gap)
        top = gap + row * (cell * 2 + head + label + gap)
        share, body = [], []
        for half, source in enumerate((subject, drawing)):
            crop = source.crop((x, y, x + width, y + height))
            grey = np.asarray(crop.convert("L")).astype(float)
            share.append(100.0 * float((grey < ink).mean()))
            # How much is *going on* in this box, measured against the box's own
            # ground rather than against black. `share` above asks "how dark is
            # it", which is a question about ink on pale paper and about nothing
            # else: on a dark ground every box reads ~100% in both pictures, and
            # a part drawn as a pale shape reads ~0% in both. Either way the
            # absence detector below is dead. The local median IS the ground, so
            # the fraction departing from it is the part, whichever side of the
            # ground the part happens to sit on.
            # measured on the TIGHT box, never the padded one. The padding is
            # there so a part that has *moved* still shows something to look at;
            # include it in the statistic and the neighbours hold the number up,
            # so an erased part reads half-present instead of gone. Measured:
            # the same absent egg scores 49% padded and 0% tight.
            near = np.asarray(source.crop(tight).convert("L")).astype(float)
            body.append(100.0 * float((np.abs(near - np.median(near)) > ground).mean()))
            fit = min(cell / max(width, 1), cell / max(height, 1))
            crop = crop.resize((max(1, round(width * fit)), max(1, round(height * fit))),
                               Image.LANCZOS)
            sheet.paste(crop, (left + (cell - crop.width) // 2,
                               top + head + half * cell + (cell - crop.height) // 2))
        pen.text((left, top + 2), name[:30], fill=(25, 25, 25))
        if wrapped[index]:
            for number, strip in enumerate(wrapped[index]):
                pen.text((left, top + label + number * line), strip, fill=(70, 70, 70))
            if over[index]:
                pen.text((left + cell - 24, top + 2), "CUT", fill=(200, 30, 30))
        else:
            pen.text((left, top + label), "no shape sentence", fill=(200, 30, 30))
        # a quarter, not a third: an under-rendered part lands near a third
        # (this drawing's mat texture reads 0.33 of the subject's and is
        # thin, not absent), while a part that is genuinely not there reads 0.
        # Normalised by how far along the whole drawing is. At a block-in every
        # part carries a fraction of the subject's incident because *nothing* is
        # filled in yet, so an absolute threshold reports all 81 parts missing at
        # the exact gate the second law tells you to run this. What matters is
        # whether a part is behind the drawing it belongs to: if the panel as a
        # whole is at 30% of the subject, a part at 30% is on schedule and one at
        # 3% is genuinely not there.
        want = body[0] * pace
        gone = body[0] > 4.0 and body[1] < want / 4.0
        numbers = (f"ink {share[0]:.0f}%->{share[1]:.0f}%  form {body[0]:.0f}%->{body[1]:.0f}%"
                   + ("   MISSING?" if gone else ""))
        pen.text((left, top + head + cell * 2 + 1), numbers,
                 fill=(200, 30, 30) if gone else (90, 90, 90))
        print(f"  {name[:28]:28s} {numbers}")
    return sheet


def ranking(drawing, subject, inventory):
    """What leads the eye, ranked -- the drawing's order against the subject's.

    Every other check in this file asks whether a part is *right*. This one asks
    whether it is **loud**, then throws the magnitude away and keeps only the
    order. That is the point. `ink` and `form` both rise wherever marks are
    added, so both can be moved by working harder anywhere; a ranking cannot.
    Add marks to every part and the order comes back unchanged. **The only way
    to move a part up this list is to move another part down** -- which is the
    only kind of change a whole-picture pass is allowed to make, and the reason
    this is the instrument for one.

    The statistic is the spread of value inside the part's own box: not how dark
    it is, and not how much is going on in it. A thread of line on bare ground is
    busy and quiet; a black mass against cream is one shape and shouts. Spread is
    what the eye competes over, and it is why a tier-3 object can out-shout the
    subject of the picture without one mark in it being wrong.

    Read it in both directions:

    - A part far ABOVE its subject rank is **competing with what it should be
      supporting**. Knock it back. This is the whole finish pass on most scenes,
      because a panel cannot afford to build its furniture and can always afford
      to quieten it -- and quietening the furniture is what makes the built thing
      read as built.
    - A part far BELOW is not carrying its share. At a **junction**, whose box
      holds two objects meeting rather than one object, that is the specific
      failure of two forms welding into one value: the junction has stopped
      existing, and no amount of drawing either object will bring it back.

    It ranks, it does not decide, and a box is still only a box. Crop the part
    and look at it before believing any row.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    planes = [np.asarray(image.convert("L")).astype(float) for image in (subject, drawing)]
    rows = []
    for name, entry in inventory.items():
        x, y, width, height = entry["box"]
        x, y = max(0, x), max(0, y)
        width, height = min(subject.width - x, width), min(subject.height - y, height)
        said = entry["shape"]
        tier = ("J" if "/" in name or "JUNCTION" in said else
                str(entry["tier"]) if entry.get("tier") is not None else
                next((digit for digit in "123" if f"TIER {digit}" in said), "-"))
        spread = [float(plane[y:y + height, x:x + width].std()) for plane in planes]
        rows.append([name, tier, spread[0], spread[1], 0, 0])
    for loud, seat in ((2, 4), (3, 5)):
        for place, row in enumerate(sorted(rows, key=lambda one: -one[loud]), 1):
            row[seat] = place
    return sorted(rows, key=lambda row: -abs(row[4] - row[5]))


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("render")
    parse.add_argument("--ref")
    parse.add_argument("--out", default="check.png")
    parse.add_argument("--width", type=int, default=460)
    parse.add_argument("--grid", type=int, default=0)
    parse.add_argument("--plumb", default="", help="comma-separated fractions of width")
    parse.add_argument("--squint", type=float, default=7.0)
    parse.add_argument("--overlay", action="store_true",
                       help="lay the drawing over the reference instead of beside it")
    parse.add_argument("--zoom", default="",
                       help="x,y,w,h in the REFERENCE's own pixels — so comparing "
                            "two renders of the same drawing needs the box in render "
                            "coordinates, not the subject's: subject above, drawing "
                            "below, magnified")
    parse.add_argument("--unfilled", action="store_true",
                       help="with --ref: bare paper where the subject has the object")
    parse.add_argument("--faces", default="",
                       help="ops.json — flag fills simpler than their traced region")
    parse.add_argument("--regions", default="regions.json")
    parse.add_argument("--face-ratio", type=float, default=0.5)
    parse.add_argument("--grain", type=float, default=0.0,
                       help="--faces: serration narrower than this, in px, is the source's "
                            "grain, not a corner. 3x the upscale factor on an upscaled subject")
    parse.add_argument("--weights", default="",
                       help="comma-separated rows: print the mark widths each one crosses, "
                            "as width@centre")
    parse.add_argument("--masses", action="store_true",
                       help="both pictures as flat masses, no line — the check that "
                            "sees shape. Takes --box x,y,w,h and --colours N")
    parse.add_argument("--box", default="",
                       help="x,y,w,h to crop both to; with --overlay, the two inks over that box")
    parse.add_argument("--scan", default="",
                       help="x,y,w,h (needs --ref): per row, the outline and the ink runs of "
                            "subject and drawing, from --side")
    parse.add_argument("--side", default="right", choices=("left", "right", "top", "bottom"))
    parse.add_argument("--value", default="",
                       help="--scan, --overlay --box: comma-separated palette.json names read as "
                            "line instead of everything dark")
    parse.add_argument("--step", type=int, default=0, help="--scan: rows between readings")
    parse.add_argument("--colours", type=int, default=3,
                       help="--masses: value levels, line removed first (default 3)")
    parse.add_argument("--parts", default="",
                       help="a JSON file of {name: [x,y,w,h]} — every named part of "
                            "the picture, subject above and drawing below")
    parse.add_argument("--ranking", default="",
                       help="parts.json: what leads the eye, the drawing's order "
                            "against the subject's")
    parse.add_argument("--doubled", default="",
                       help="an ops JSON: is any edge stated twice? reads the "
                            "script, not the render")
    parse.add_argument("--depth", nargs=2, metavar=("OPS", "PARTS"), default=None,
                       help="write order against the inventory's in_front column")
    parse.add_argument("--checklist", default="",
                       help="parts.json: every sub-form a reference's checklist names for an "
                            "object in the inventory has an entry, or a reason in _absent")
    parse.add_argument("--census", default="",
                       help="parts.json (needs --ref): every entry with a count, counted "
                            "on the subject and on the drawing")
    parse.add_argument("--min-area", type=int, default=40,
                       help="--census: the smallest form counted, in render pixels")
    parse.add_argument("--ladder", default="",
                       help="an ops JSON: which stages exist, how many marks each, "
                            "and whether a drawing with ink has a gesture, block-in and "
                            "contour stage at all. Reads the script, not the render")
    parse.add_argument("--registration", action="store_true",
                       help="report every place the colour and the line disagree")
    parse.add_argument("--paper", default="#FAF1D2",
                       help="the render's paper, #rrggbb or R,G,B")
    parse.add_argument("--ground", default="",
                       help="--unfilled: the SUBJECT's ground, if not palette.json's background")
    parse.add_argument("--space", default="",
                       help="x0,y0,x1,y1 the render covers, so faults are reported "
                            "in the drawing's own coordinates")
    args = parse.parse_args()

    # the script-only checks need no render, so a first build can run them
    if args.checklist:
        missing = checklist(args.checklist)
        for thing, source, gone in missing:
            print(f"  FAIL {thing} ({source}): no entry for {', '.join(gone)}")
        if missing:
            print("\nadd an entry for each, or write it into parts.json's \"_absent\" as "
                  "\"name: reason; ...\".\nA sub-form left out without a reason was never "
                  "looked for, and every gate below\nchecks only what the inventory names.")
            sys.exit(1)
        print("  PASSES — every checklisted sub-form has an entry or a reason")
        return
    if args.ladder:
        import os
        from pen import audit, LADDER, provenance, script_source
        with open(args.ladder) as handle:
            ops = json.load(handle)
        counts, first, failures = audit(ops)
        for stage in LADDER + tuple(s for s in counts if s not in LADDER):
            print(f"  {stage:14s} {counts.get(stage, 0):4d} marks"
                  + (f"   first at op {first[stage]}" if stage in first else "   ABSENT"))
        for failure in failures:
            print(f"  FAIL {failure}")
        for index, area, at in self_crossing(ops):
            print(f"  HOLE fill at op {index}{' ' + ops[index]['tag'] if ops[index].get('tag') else ''}: "
                  f"{area}px near {at} winds to zero and shows the ground. A ring drawn as one "
                  "polygon has one on purpose; anywhere else the outline doubles back -- keep "
                  "perimeter order, run-on points included")
        if not failures and not counts.get("ink"):
            print("  no ink yet: the stages are gated from the first ink mark")
        elif not failures:
            print("  PASSES — the gesture, block-in and contour stages exist, in order. Whether "
                  "each ink mark\n  has a contour under it is NOT checked: on three finished "
                  "drawings 26-81% had none")
        source = script_source(ops, os.path.dirname(os.path.abspath(args.ladder)))
        facts, generated = provenance(ops, source)
        literal = "not read" if facts["literal"] is None else f"{facts['literal']:.1%}"
        print(f"\n  authored: {facts['strokes']} stroke calls, {facts['points']} control "
              f"points, {literal} of them written as numbers in the script")
        if source is None:
            generated.append("the script these ops name was not found beside them, so "
                             "nothing says the points were written there")
        for failure in generated:
            print(f"  FAIL {failure}")
        if not generated:
            print("  PASSES — every mark was written in the script, one call each, "
                  "from numbers written there")
        print("\ncounts are not a score: one token gesture stroke passes this and fools "
              "nobody\nwho opens gesture.png. What this catches is the stage that "
              "does not exist,\nand the mark that was generated rather than drawn. "
              "Generated output pasted into\nthe script as literal lines passes it; "
              "the rule forbids that, not this gate.")
        sys.exit(1 if failures or generated else 0)

    if args.depth:
        with open(args.depth[0]) as handle:
            written = json.load(handle)
        with open(args.depth[1]) as handle:
            hits, unresolved, count = depth(written, json.load(handle))
        with open(args.depth[1]) as handle:
            loose = crossings(written, json.load(handle))
        print(f"{count} interface rows carry an in_front decision")
        for key, far, ink_at, near, fill_at in hits:
            print(f"  FAIL {key}: ink of '{far}' at op{ink_at} is written AFTER "
                  f"the fill of '{near}' at op{fill_at} — that edge draws across it")
        for key, why in unresolved:
            print(f"  UNRESOLVED {key}: {why}")
        if not hits and not unresolved and count:
            print(f"  PASSES — the {count} listed occlusions are delivered by the write order")
        if not count:
            print("  NOTHING TO CHECK — no inventory entry carries in_front")
        shown = [row for row in loose if row[3] == "drawn across"]
        if shown:
            print(f"\n{len(shown)} unlisted overlaps SHOW on the page, longest first -- a "
                  "worklist, not a verdict:")
            for length, ink, flat, how in shown[:20]:
                print(f"  UNLISTED {ink} ink {how} {flat}'s flat for {length}px")
            print("each is either the ink's part in front of that flat, or a crease across a "
                  "nearer\nform. Decide, and write the row into parts.json so the next run "
                  "checks it.")
        if len(loose) > len(shown):
            print(f"\n{len(loose) - len(shown)} more unlisted overlaps are buried under a flat "
                  "written after the\nink: occlusion the write order already delivers, "
                  "unchecked against any decision.")
        print("\nthe far form's ink must precede the near form's fill: a flat cannot "
              "hide ink,\nso written the other way the far outline runs straight across "
              "the nearer object\nand reads as a crease that is not there. an UNRESOLVED "
              "row is not a pass — it\nmeans the stroke tags and the inventory names are "
              "not one vocabulary, and the\npair went unchecked.")
        sys.exit(1 if (hits or unresolved or not count) else 0)

    if args.doubled:
        with open(args.doubled) as handle:
            hits, worst, count = doubled(json.load(handle))
        print(f"{count} ink strokes; longest non-junction overlap {worst:.0f}px")
        for first, here, second, there, length in hits:
            print(f"  FAIL op{first}({here}) x op{second}({there})  {length}px")
        if not hits:
            print("  PASSES — no edge is stated twice")
        print("\na run at a shared endpoint is the junction, not a doubling, and is "
              "excluded.\nwhat this finds is one boundary drawn from two guesses: the "
              "fault that reads as\na field of crossing loops and gets diagnosed for "
              "rounds as bad curve control.")
        sys.exit(1 if hits else 0)

    if args.faces:
        sys.exit(1 if faces(args.faces, args.regions, args.face_ratio, args.grain) else 0)

    drawing = Image.open(args.render).convert("RGB")
    plumbs = [float(value) for value in args.plumb.split(",") if value.strip()]

    if args.unfilled:
        if not args.ref:
            sys.exit("--unfilled needs --ref")
        paper = colour(args.paper)
        sys.exit(1 if unfilled(Image.open(args.render), Image.open(args.ref).convert("RGB"),
                               paper, colour(args.ground) if args.ground else ground_of(paper))
                 else 0)

    if args.weights:
        rows = [int(part) for part in args.weights.split(",")]
        if not args.ref:
            # a bare weight ladder: the drawing's own runs, nothing to match
            grey = drawing.convert("L")
            for y in rows:
                print(f"y={y:4d}  drawing {said(marks(list(grey.crop((0, y, grey.width, y + 1)).getdata())))}")
            print("\nwidth@x, left to right, in the render's own pixels")
            return
        subject = Image.open(args.ref).convert("L")
        report(subject, drawing.convert("L").resize(subject.size, Image.LANCZOS), rows)
        return

    if args.masses:
        if not args.ref:
            sys.exit("--masses needs --ref")
        box = [int(part) for part in args.box.split(",")] if args.box else None
        masses(drawing, Image.open(args.ref).convert("RGB"), box, args.colours).save(args.out)
        print(f"wrote {args.out}")
        print("line, detail and rendering are gone; what is left is what the eye "
              "reads first.\nsay in words what shape each one is. If they are not "
              "the same shape, stop —\nnothing drawn on top of these masses will "
              "make them agree.")
        return

    if args.parts:
        if not args.ref:
            sys.exit("--parts needs --ref")
        inventory = read_inventory(args.parts)
        subject = Image.open(args.ref).convert("RGB")
        mute = [name for name, entry in inventory.items() if not entry["shape"]]
        # A full inventory runs to dozens of parts, and one sheet of them is
        # taller than anything can be looked at. Split it into pages that fit a
        # single look each -- a sheet you have to scroll is a sheet you skim.
        named = list(inventory.items())
        stem, dot, suffix = args.out.rpartition(".")
        pages = [named[at:at + 16] for at in range(0, len(named), 16)] or [[]]
        for number, page in enumerate(pages, 1):
            where = args.out if len(pages) == 1 else f"{stem}-{number}{dot}{suffix}"
            parts(drawing, subject, dict(page)).save(where)
            print(f"wrote {where} — {len(page)} parts")
        print(f"{len(inventory)} parts, subject above, drawing below, boxes padded "
              "a fifth.\nthe percentages are dark-pixel share. On one part they only "
              "say whether it is\nthere. Across all of them, a consistent offset in "
              "one direction is a real\nfinding — a whole ladder spent too freely, "
              "which nothing else here can see.\nWhether a part that is present is "
              "any good is yours, and only yours.")
        if mute:
            # Loud, because a silent one of these is the whole failure: the
            # sheet still renders, the numbers still look like a measurement,
            # and nothing in it is comparing a shape to a shape.
            print(f"\n{len(mute)} of {len(inventory)} parts carry NO shape sentence, "
                  "so for those this check\ncompares a box against a box and can only "
                  "see absence and displacement:\n  " + ", ".join(mute[:12])
                  + (" ..." if len(mute) > 12 else ""))
        return

    if args.census:
        if not args.ref:
            sys.exit("--census needs --ref")
        rows = census(drawing, Image.open(args.ref).convert("RGB"), args.census,
                      "palette.json", args.min_area)
        if not rows:
            sys.exit("--census: no entry carries a count -- write the census into parts.json")
        wrong = unchecked = 0
        print(f"  {'entry':34s} census subject drawing")
        for key, want, seen, made in rows:
            if seen != want:
                # the instrument does not reproduce the census on the subject
                # itself, so its count of the drawing means nothing either way:
                # spokes cut by spokes, slots joined by their own ink, grain
                verdict = "  UNCHECKED: the subject does not count to the census here"
                unchecked += 1
            elif made != want:
                verdict = "  FAIL culled" if made < want else "  FAIL extra"
                wrong += 1
            else:
                verdict = ""
            print(f"  {key[:34]:34s} {want:6d} {seen:7d} {made:7d}{verdict}")
        checked = len(rows) - unchecked
        print(f"\n{checked} of {len(rows)} entries checked" + (", all agree" if checked and not wrong else ""))
        if unchecked:
            print(f"{unchecked} UNCHECKED: this counts connected forms of the entry's values in its "
                  "box, and\nwhere that does not give the census on the SUBJECT -- forms crossing, "
                  "touching,\nor bounded by ink of their own value -- it has no verdict on the "
                  "drawing. Count\nthose on --zoom, subject and drawing, and write both numbers in "
                  "notes.md.")
        print("\na census is the only gate that fails on an absence, and only where it can "
              "count\nthe subject: a tight box on separate forms of one value (droplets, "
              "pebbles, teeth\nwith dark gaps) is what it reads. exit 1 is a FAIL, 2 is "
              "UNCHECKED rows: neither is a pass.")
        sys.exit(1 if wrong else 2 if unchecked else 0)

    if args.ranking:
        if not args.ref:
            sys.exit("--ranking needs --ref")
        subject = Image.open(args.ref).convert("RGB")
        rows = ranking(drawing, subject, read_inventory(args.ranking))
        print(f"what leads the eye, worst disagreement first. value spread inside each "
              f"part's own\nbox, ranked 1..{len(rows)} in each picture. tier is the entry's "
              "`tier`; J is a junction.\n")
        print(f"  {'part':26s} tier {'subject':>15s} {'drawing':>15s}   moved")
        for name, tier, loud, now, seat, place in rows:
            move = seat - place
            print(f"  {name[:26]:26s} {tier:4s} {loud:8.1f} #{seat:<5d} {now:8.1f} #{place:<5d} "
                  f"{move:+4d}  " + ("LOUDER than the subject ranks it" if move > 0 else
                                     "quieter" if move < 0 else ""))
        tiers = sorted({row[1] for row in rows if row[1].isdigit()})
        if len(tiers) > 1:
            lead = min(row[5] for row in rows if row[1] == tiers[0])
            led = min(row[4] for row in rows if row[1] == tiers[0])
            loud = [row for row in rows if row[1].isdigit() and row[1] != tiers[0]
                    and row[5] < lead and row[4] > led]
            print(f"\ntier {tiers[0]}'s loudest part is #{led} in the subject and #{lead} in the drawing.")
            for row in sorted(loud, key=lambda one: one[5]):
                print(f"  ABOVE ITS TIER: {row[0]} (tier {row[1]}) is #{row[5]} in the drawing, "
                      f"ahead of every tier-{tiers[0]} part, and #{row[4]} in the subject")
            if not loud:
                print("  nothing ranks ahead of the focus tier that the subject does not put there")
        elif not tiers:
            print("\nno entry carries a `tier`: nothing here can say what shouts above its tier")
        print("\nmoved is the subject's rank minus the drawing's. + means the drawing "
              "pushes the part\nforward of where the subject has it, - means it has "
              "dropped back.\nA rank is zero-sum: this is the one number here that "
              "adding marks cannot lift,\nso the only way up is to put something else "
              "down. A junction that has gone\nquiet is two objects welded into one "
              "value. Crop the part and look before\nyou believe any row.")
        return

    if args.registration:
        faults = registration(drawing, colour(args.paper))
        span = [float(part) for part in args.space.split(",")] if args.space else \
            [0, 0, drawing.width, drawing.height]
        across = (span[2] - span[0]) / drawing.width
        down = (span[3] - span[1]) / drawing.height
        marked = drawing.convert("RGB").copy()
        pen = ImageDraw.Draw(marked)
        print(f"{len(faults)} faults, largest first — area, kind, box in drawing coords\n")
        for number, (area, kind, x, y, width, height) in enumerate(faults, 1):
            hue = (215, 40, 40) if kind == "spill" else (30, 90, 220)
            pen.rectangle([x - 3, y - 3, x + width + 2, y + height + 2], outline=hue, width=2)
            pen.text((x - 2, y - 16), f"{number}", fill=hue)
            print(f"{number:2d}  {area:6d}px  {kind:5s}  "
                  f"{span[0] + x * across:6.0f},{span[1] + y * down:6.0f}  "
                  f"{width * across:4.0f}x{height * down:.0f}")
        marked.save(args.out)
        print(f"\nwrote {args.out} — red is spill, blue is gap")
        print("a spill is colour with no line over it; a gap is paper the line "
              "walled in.\nboth are mistakes. a trap that wanders under its own "
              "line is neither, and will\nnot appear here — but a flat mixed at "
              "the paper's own value will, so look\nbefore you correct.")
        return

    if args.zoom:
        if not args.ref:
            sys.exit("--zoom needs --ref")
        zoom(drawing, Image.open(args.ref).convert("RGB"),
             [int(part) for part in args.zoom.split(",")]).save(args.out)
        print(f"wrote {args.out}")
        return

    if args.scan:
        if not args.ref:
            sys.exit("--scan needs --ref")
        value = palette_value(args.value)
        scan(drawing, Image.open(args.ref).convert("RGB"),
             [int(part) for part in args.scan.split(",")], args.side, args.step,
             ground_of(colour(args.paper)), value=value)
        return

    if args.overlay and args.box:
        if not args.ref:
            sys.exit("--overlay needs --ref")
        inks(drawing, Image.open(args.ref).convert("RGB"),
             [int(part) for part in args.box.split(",")],
             value=palette_value(args.value)).save(args.out)
        print(f"wrote {args.out}: blue is the subject's line the drawing lacks there, red "
              "the drawing's\nline where the subject has none, black both. For every blue "
              "line inside the form,\nsay which red line is meant to be it and how far and "
              "which way it runs off.")
        return

    if args.overlay:
        if not args.ref:
            sys.exit("--overlay needs --ref")
        subject = Image.open(args.ref).convert("RGB").resize(drawing.size, Image.LANCZOS)
        both = Image.blend(subject, drawing, 0.55)
        contact([
            (fit(rule(subject, args.grid, plumbs), args.width), "subject"),
            (fit(rule(both, args.grid, plumbs), args.width), "drawing over subject"),
            (fit(rule(drawing, args.grid, plumbs), args.width), "drawing"),
        ]).save(args.out)
        print(f"wrote {args.out}")
        return

    panels = []
    if args.ref:
        panels.append((fit(rule(Image.open(args.ref).convert("RGB"), args.grid, plumbs),
                           args.width), "subject"))
    panels.append((fit(rule(drawing, args.grid, plumbs), args.width), "drawing"))
    panels.append((fit(drawing.transpose(Image.FLIP_LEFT_RIGHT), args.width), "mirrored"))
    panels.append((fit(drawing.filter(ImageFilter.GaussianBlur(args.squint)), args.width),
                   "squinted"))
    contact(panels).save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
