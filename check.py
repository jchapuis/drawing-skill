#!/usr/bin/env python3
"""Put the drawing in front of yourself in every way that exposes a different error.

    python3 check.py look.png --ref subject.png --grid 6 --out check.png

The output is one image, so one look costs one Read: the reference, the
drawing, the drawing mirrored, and the drawing squinted. Each view catches a
class of error the others hide. Mirroring breaks the habituation that makes your
own proportion errors invisible. Squinting throws away line and leaves only the
masses. Having the reference alongside stops you comparing against memory, which
reverts to the symbol you already believed.

`--overlay` instead lays the drawing over the reference so proportion drift
shows directly, without judging across a gap.

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

# a 4x working image is past PIL's decompression-bomb limit, and so is what
# --masses would make of it. These are our own images, so the limit is lifted
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


def contact(views, pad=14, label_height=26):
    width = sum(image.width for image, _ in views) + pad * (len(views) + 1)
    height = max(image.height for image, _ in views) + pad * 2 + label_height
    sheet = Image.new("RGB", (width, height), (250, 250, 248))
    pen = ImageDraw.Draw(sheet)
    x = pad
    for image, caption in views:
        sheet.paste(image, (x, pad + label_height))
        pen.text((x + 2, pad + 6), caption, fill=(35, 35, 35))
        x += image.width + pad
    return sheet



def corners(points, tolerance):
    """Ramer-Douglas-Peucker: the vertices a polyline actually turns on.

    A stroke in ops.json is the rendered polyline, interpolated to hundreds of
    points whatever was authored, so counting its points measures the renderer.
    Simplifying it back down measures the drawing: how many faces the shape
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
    carries a serration of 5-15px along every edge at 4x. No simplifying
    tolerance that still keeps the real corners removes it, but opening and
    closing the region's own mask does, and leaves the corners where they were."""
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

    An interior flat (a shade, a highlight, a cast shadow lying on a form) is
    bounded by that form's curvature and cannot be simpler than it. Drawn as a
    quad on a form the tracer returns with twenty-five points, it reads as a
    paste-on: a hard-edged patch sitting on the object rather than a turn of its
    surface. No other gate sees this. The flat is the right colour, in the right
    place and covers the right area, and the describer has no word for it.

    This is not an absolute floor. A paving joint or a step riser is a quad, and
    adding points to it only adds noise. The count comes from the traced region
    the flat sits in, so the subject sets it.
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
        # The region is the one the flat overlaps, not one whose box holds its
        # centre: a thin tube's centre can sit in the box of a whole wheel
        # behind it, and the tube flat would be compared against that region's
        # 366 corners. The region is also simplified at the flat's own
        # tolerance, which scales with the shape. At the tracer's fixed
        # tolerance a grainy source serrates every edge (a straight tube came
        # back with 70-230 points), and 31 tube flats in one picture read TOO
        # FEW FACES.
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
          f"stuck to the object, not as its surface turning away.")
    return thin


def colour(text):
    """A colour given as #rrggbb or as R,G,B. Both forms are accepted."""
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
    value, not a fixed level. A weight swatch drawn at the `fill` stage sits well
    above any constant a line swatch would use, and a fixed threshold would
    report it as an empty row, so the check would fail without a message on the
    stage you are asked to calibrate.
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
    """Runs as `width@x`, x the run's centre, in the order they sit, so each
    weight in a swatch keeps its identity: a sorted list of widths cannot say
    which weight is which. Printed at the run's start, two lines placed on the
    printed x came back half a line off (8px) on both sides."""
    return "  ".join(f"{width}@{start + (width - 1) // 2}" for start, width in runs) or "-"


def report(subject, drawing, rows):
    """The weight hierarchy, as numbers rather than as an impression.

    The ratio between a drawing's finest mark and its heaviest depends on the
    style being drawn: a heavily inked comic runs 8-10x, a flat cel design nearer
    2-3x. A wrong ratio is invisible at full size and obvious at 4x, so measure
    the subject's own range and match it.
    """
    for y in rows:
        found = marks(list(subject.crop((0, y, subject.width, y + 1)).getdata()))
        made = marks(list(drawing.crop((0, y, drawing.width, y + 1)).getdata()))
        print(f"y={y:4d}  subject {said(found)}")
        print(f"        drawing {said(made)}")
    print("\nwidth@x, left to right. Match the span, not the individual runs: the "
          "finest, the\nheaviest, and the ratio between them.")


def line_marks(grey, line, contrast=30, light=False):
    """The thin line marks in a grey crop, with the flats left out: (mask, lift).

    A mark is darker than what surrounds it and no wider than `line`. A black
    top-hat with a disc of 2*line+1 lifts exactly those, so a dark flat wider
    than the disc (a black boot, a shadow mass) reads as nothing however dark it
    is, while a hatch stroke on a mid flat reads in full. `contrast` is how much
    darker than its surround a pixel must be: paper grain and a print's dot
    screen stay under it. `light` reads pale lines on a dark ground instead,
    the white line an engraver cuts into a black."""
    grey = np.asarray(grey, dtype=float)
    if light:
        grey = 255 - grey
    size = 2 * line + 1
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    lift = cv2.morphologyEx(np.clip(grey, 0, 255).astype(np.uint8), cv2.MORPH_BLACKHAT,
                            disc).astype(float)
    mask = lift > contrast
    labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
    if count:
        # a speck the size of the grain is not a mark
        sizes = ndimage.sum(mask, labels, range(1, count + 1))
        mask = np.isin(labels, np.flatnonzero(sizes >= max(12, 2 * line)) + 1)
    return mask, lift


def _bend(angle):
    """A line direction folded into 0..180."""
    return angle % 180.0


def _apart(one, other):
    """The angle between two line directions, 0..90."""
    gap = abs(_bend(one) - _bend(other))
    return min(gap, 180.0 - gap)


def _slant(angle):
    return "-" if _apart(angle, 0) < 22.5 else "|" if _apart(angle, 90) < 22.5 else \
        "/" if angle < 90 else "\\"


def hatching(grey, line, light=False, contrast=30, groups=3):
    """Where the line marks in a crop run, as numbers: coverage and per group of
    parallel marks its direction, spacing, length and width.

    Angles are line directions as seen on the page, 0 horizontal, 90 vertical,
    45 a `/` and 135 a `\\`. The direction of each mark pixel comes from the
    structure tensor, so where two groups cross (cross-hatching) each keeps its
    own angle instead of averaging into a diagonal neither has."""
    mask, lift = line_marks(grey, line, contrast, light)
    area = mask.size
    found = {"coverage": float(mask.sum()) / area if area else 0.0, "groups": []}
    spine = across = None
    if mask.sum() < 3 * line:
        return found
    soft = cv2.GaussianBlur(lift, (0, 0), max(1.0, line / 3))
    gx = cv2.Sobel(soft, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(soft, cv2.CV_64F, 0, 1, ksize=3)
    reach = max(1.5, line / 2)
    jxx, jyy, jxy = (cv2.GaussianBlur(product, (0, 0), reach) for product in (gx * gx, gy * gy, gx * gy))
    across = 0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy))   # the gradient, y down
    # the line runs at right angles to its gradient; flip y so 45 is `/` on the page
    angle = _bend(-(across + 90.0))
    sure = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-9)
    usable = mask & (sure > 0.4)
    if usable.sum() < 3 * line:
        return found
    weights = sure[usable]
    bins = np.histogram(angle[usable], bins=36, range=(0, 180), weights=weights)[0]
    smooth = sum(np.roll(bins, shift) * w for shift, w in ((-2, 1), (-1, 2), (0, 3), (1, 2), (2, 1)))
    peaks = [at for at in range(36)
             if smooth[at] >= smooth[at - 1] and smooth[at] > smooth[(at + 1) % 36]
             and smooth[at] >= 0.3 * smooth.max()]
    peaks.sort(key=lambda at: -smooth[at])
    chosen = []
    for at in peaks:
        centre = at * 5 + 2.5
        if all(_apart(centre, other) > 25 for other in chosen):
            chosen.append(centre)
    total = weights.sum()
    pooled = []
    for centre in chosen[:groups]:
        near = usable & (np.minimum(np.abs(angle - centre), 180 - np.abs(angle - centre)) <= 15)
        if not near.any():
            continue
        # the group's own direction: a circular mean of the doubled angles
        doubled = np.radians(2 * angle[near])
        mean = _bend(np.degrees(np.arctan2((np.sin(doubled) * sure[near]).sum(),
                                           (np.cos(doubled) * sure[near]).sum())) / 2)
        member = mask & (np.minimum(np.abs(angle - mean), 180 - np.abs(angle - mean)) <= 20)
        labels, count = ndimage.label(member, structure=np.ones((3, 3)))
        along = np.array([math.cos(math.radians(mean)), -math.sin(math.radians(mean))])
        lengths, widths, kept = [], [], np.zeros_like(member)
        for index, piece in enumerate(ndimage.find_objects(labels), 1):
            rows, cols = np.nonzero(labels[piece] == index)
            if rows.size < 4:
                continue
            reach_along = cols * along[0] + rows * along[1]
            length = reach_along.max() - reach_along.min() + 1
            width = rows.size / length
            if length < 2 * width or length < line:
                continue    # a dot or a blot, not a stroke
            if spine is None:
                spine, across = _centre_widths(mask, lift, line)
            # the mark's own width on its centre line; area over length for a mark too
            # short to have one
            on = spine[piece] & (labels[piece] == index)
            lengths.append(length)
            widths.append(float(np.median(across[piece][on])) if on.sum() >= 3 else width)
            kept[piece] |= labels[piece] == index
        if len(lengths) < 2:
            continue
        pooled.extend(lengths)
        found["groups"].append({"angle": mean, "share": float(weights[near[usable]].sum() / total),
                                "marks": len(lengths), "length": float(np.median(lengths)),
                                "lengths": (float(np.percentile(lengths, 25)), float(np.percentile(lengths, 75))),
                                "width": float(np.median(widths)),
                                "spacing": _spacing(kept, mean),
                                "coverage": float(kept.sum()) / area})
    if pooled:
        found["grain"] = _grain(grey, mask, line, light, float(np.median(pooled)))
    return found


def _centre_widths(mask, lift, line):
    """Each line mark's width read on its centre line at half its own darkness:
    (centre-line mask, width per pixel). A mark is taken to end where its lift
    falls under half the peak within `line` of it, not where it falls under the
    `contrast` floor, so an upscaled subject's soft edge does not read wider
    than a render's crisp one of the same weight."""
    peak = ndimage.maximum_filter(lift, size=line | 1)
    core = mask & (lift >= 0.5 * peak)
    distance = cv2.distanceTransform(core.astype(np.uint8), cv2.DIST_L2, 5)
    # the widest point within 2px, as weight_span reads it
    return _thin(core), 2 * ndimage.maximum_filter(distance, size=5) - 1


def outline_weight(grey, line, contrast=30):
    """The outline's weight: the 95th percentile of the dark line widths in a
    crop, read as hatching() reads a group's width. None with too few marks."""
    mask, lift = line_marks(grey, line, contrast)
    if mask.sum() < 3 * line:
        return None
    spine, across = _centre_widths(mask, lift, line)
    if spine.sum() < 10:
        return None
    return float(np.percentile(across[spine], 95))


HATCH_WIDTH = 1.6   # a hatch mark over this many times the subject's width is too heavy
HATCH_SLACK = 2.0   # ... and over it by at least this many px, so a 1px reading is not a fail


def hatch_weight(theirs, ours, outlines):
    """FAIL lines for a drawing's hatch group heavier than the subject's, and
    the numbers either way: (fails, text). Both widths are in the subject's
    pixels. `outlines` is (subject, drawing) outline weight, either None."""
    fails, text = [], []
    seen, made = theirs["width"], ours["width"]
    ratio = made / max(seen, 1.0)
    text.append(f"mark width {made:.1f}px against the subject's {seen:.1f}px: {ratio:.1f}x")
    if ratio > HATCH_WIDTH and made - seen >= HATCH_SLACK:
        fails.append(f"hatch marks {ratio:.1f}x the subject's width (over {HATCH_WIDTH}x): "
                     "draw them with a lighter weight from the swatch")
    if all(outlines):
        want, have = seen / outlines[0], made / outlines[1]
        text.append(f"hatch/outline {have:.2f} against the subject's {want:.2f} "
                    f"(outline {outlines[1]:.0f}px, subject's {outlines[0]:.0f}px)")
        if have > HATCH_WIDTH * want and made - want * outlines[1] >= HATCH_SLACK:
            fails.append(f"hatch is {have:.2f} of the outline's weight where the subject's is "
                         f"{want:.2f}: thin the hatch, or weight the outline if it is the one too light")
    return fails, text


GRAIN_LENGTH = 3       # marks whose median length is under this many --line widths are short
GRAIN_SURVIVAL = 0.3   # ... and grain when under this share of them outlives the blur


def _grain(grey, mask, line, light, median_length):
    """Are these marks grain rather than strokes? A dict when they are, else None.

    A photograph's grain, a print's dot screen or fur texture breaks into short
    fragments that the threshold reads as marks, and those come out as a group
    with an angle, a spacing and a length like real hatching. Two things tell
    them apart. The marks are short: their median length is under GRAIN_LENGTH
    line widths. And they do not survive a blur of a quarter of `--line`: a drawn
    stroke keeps its contrast under it, while a fragment of grain sits just over
    the `contrast` floor and drops under it. Measured on a photographed lawn,
    under a fifth of the mark pixels survived; on a hand-coloured print's
    hatching, 46-84%. The same print's leg boxes, whose marks were mostly the
    limb's own edges rather than hatching, came out at 18-21% and are flagged."""
    blurred = cv2.GaussianBlur(np.asarray(grey, dtype=float), (0, 0), max(1.0, line / 3.5))
    survival = float(line_marks(blurred, line, light=light)[0].sum()) / max(1.0, float(mask.sum()))
    if median_length < GRAIN_LENGTH * line and survival < GRAIN_SURVIVAL:
        return {"length": median_length, "survival": survival}
    return None


def grain_text(found, line):
    grain = found.get("grain")
    if not grain:
        return None
    return (f"WARN grain, not hatching: the marks' median length is {grain['length']:.0f}px "
            f"(under {GRAIN_LENGTH} x --line {line}px) and {grain['survival']:.0%} of them outlive "
            "a light blur.\n     These are fragments of texture (a photograph's grain, fur, a "
            "dot screen). Do not\n     write them as a hatch entry; simplify the values first "
            "(reference/photograph.md)\n     and read the real strokes off --zoom.")


def _spacing(member, angle):
    """Centre-to-centre distance between neighbouring parallel marks: the group
    turned upright, then each row's runs read across. (median, p25, p75), or None
    when no row crosses two marks."""
    height, width = member.shape
    side = int(math.ceil(math.hypot(height, width)))
    canvas = np.zeros((side, side), np.uint8)
    top, left = (side - height) // 2, (side - width) // 2
    canvas[top:top + height, left:left + width] = member.astype(np.uint8) * 255
    turn = cv2.getRotationMatrix2D((side / 2, side / 2), 90.0 - angle, 1.0)
    upright = cv2.warpAffine(canvas, turn, (side, side), flags=cv2.INTER_NEAREST) > 0
    gaps = []
    for row in upright[::2]:
        if row.sum() < 2:
            continue
        edges = np.flatnonzero(np.diff(np.concatenate(([0], row.astype(np.int8), [0]))))
        centres = (edges[0::2] + edges[1::2] - 1) / 2
        gaps.extend(np.diff(centres))
    if not gaps:
        return None
    return tuple(float(np.percentile(gaps, q)) for q in (50, 25, 75))


def _thin(mask):
    """A mask's centre lines, one pixel wide (Zhang and Suen's thinning)."""
    image = np.pad(mask.astype(np.uint8), 1)
    while True:
        changed = False
        for first in (True, False):
            p2, p3, p4 = image[:-2, 1:-1], image[:-2, 2:], image[1:-1, 2:]
            p5, p6, p7 = image[2:, 2:], image[2:, 1:-1], image[2:, :-2]
            p8, p9 = image[1:-1, :-2], image[:-2, :-2]
            ring = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            count = sum(ring[:8])
            turns = sum(((a == 0) & (b == 1)).astype(np.uint8) for a, b in zip(ring, ring[1:]))
            if first:
                side = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                side = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            drop = (image[1:-1, 1:-1] == 1) & (count >= 2) & (count <= 6) & (turns == 1) & side
            if drop.any():
                image[1:-1, 1:-1][drop] = 0
                changed = True
        if not changed:
            return image[1:-1, 1:-1].astype(bool)


def weight_span(grey, line, light=False, contrast=30):
    """The finest and the heaviest line widths in a crop, flats left out:
    (finest, middle, heaviest, count). Each width is read on a mark's centre
    line, as twice the distance to its nearer edge, so a line crossing a row on
    a slant is not read wide and every pixel of length counts once whatever the
    line's weight. Finest is the 10th percentile and heaviest the 95th, so a
    stray speck or one blot does not set the span."""
    mask, _ = line_marks(grey, line, contrast, light)
    if mask.sum() < 3 * line:
        return None
    distance = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
    # the widest point within 2px, so the frayed tip of a centre line does not
    # read as a hairline
    widths = 2 * ndimage.maximum_filter(distance, size=5)[_thin(mask)] - 1
    if widths.size < 10:
        return None
    return (float(np.percentile(widths, 10)), float(np.percentile(widths, 50)),
            float(np.percentile(widths, 95)), int(widths.size))


def _crop_grey(image, box):
    x, y, w, h = box
    return np.asarray(image.convert("L").crop((x, y, x + w, y + h)), dtype=float)


def _group_text(group):
    if group is None:
        return "none"
    spacing = group["spacing"]
    return (f"{group['angle']:5.0f}deg {_slant(group['angle'])}  spacing "
            + (f"{spacing[0]:.0f}px" if spacing else "-")
            + f"  length {group['length']:.0f}px  width {group['width']:.0f}px  "
              f"{group['marks']} marks  {group['share']:.0%} of the line")


def match_group(groups, angle):
    """The group nearest `angle`, and how far off it runs."""
    if not groups:
        return None, None
    best = min(groups, key=lambda group: _apart(group["angle"], angle))
    return best, _apart(best["angle"], angle)


def hatch_flags(want, made, coverage_want, coverage_made):
    """What differs between a subject group and the drawing's nearest one."""
    flags = []
    group, off = match_group(made, want["angle"])
    if group is None:
        return ["missing: the drawing has no line group here"]
    if off > 20:
        flags.append(f"angle off {off:.0f}deg: no group within 20deg of {want['angle']:.0f}")
    if want.get("spacing") and group.get("spacing"):
        ratio = group["spacing"][0] / want["spacing"][0]
        if abs(ratio - 1) > 0.5:
            flags.append(f"spacing {ratio:.1f}x the subject's")
    if coverage_want and coverage_made < 0.5 * coverage_want:
        flags.append(f"coverage {coverage_made:.0%} under half of {coverage_want:.0%}")
    return flags


def hatch_report(subject, drawing, box, line, light=False, names=("subject", "drawing")):
    """--hatch: the line marks inside one box, measured, and with a drawing the
    same box measured beside it. Prints numbers only, never points: where the
    marks run, how far apart and how long. Placing each one is yours."""
    print(f"--hatch {','.join(map(str, box))}: line marks up to {line}px wide (--line), "
          f"{'paler' if light else 'darker'} than their surround by 30+.\n"
          "angle is the line's direction on the page: 0 horizontal, 90 vertical, 45 /, 135 \\.")
    seen = hatching(_crop_grey(subject, box), line, light)
    print(f"\n{names[0]}: line marks cover {seen['coverage']:.0%} of the box, "
          f"{len(seen['groups'])} group(s) of parallel marks")
    for number, group in enumerate(seen["groups"], 1):
        lo, hi = group["lengths"]
        spacing = group["spacing"]
        print(f"  group {number}: {_group_text(group)}"
              + (f"\n           spacing {spacing[1]:.0f}-{spacing[2]:.0f}px, length {lo:.0f}-{hi:.0f}px "
                 "(middle half)" if spacing else ""))
    if grain_text(seen, line):
        print("  " + grain_text(seen, line))
    if drawing is None:
        print("\nwrite each mark of a group as its own stroke, from points you read off the "
              "subject.\nVary length and spacing inside the ranges above the way a hand does.")
        return seen, None, 0
    if drawing.size != subject.size:
        print(f"{names[1]} is {drawing.width}x{drawing.height}; resized to the subject's "
              f"{subject.width}x{subject.height}, so every width below is in the subject's pixels")
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    made = hatching(_crop_grey(drawing, box), line, light)
    print(f"{names[1]}: line marks cover {made['coverage']:.0%} of the box, "
          f"{len(made['groups'])} group(s)")
    for number, group in enumerate(made["groups"], 1):
        print(f"  group {number}: {_group_text(group)}")
    outlines = tuple(outline_weight(np.asarray(image.convert("L"), dtype=float), line)
                     for image in (subject, drawing))
    print("\nsubject group -> the drawing's nearest group")
    failures = 0
    for number, group in enumerate(seen["groups"], 1):
        near, off = match_group(made["groups"], group["angle"])
        flags = hatch_flags({"angle": group["angle"], "spacing": group["spacing"]},
                            made["groups"], seen["coverage"], made["coverage"])
        print(f"  {group['angle']:4.0f}deg -> {_group_text(near)}"
              + ("".join(f"\n      << {flag}" for flag in flags)))
        if near is not None and off <= 20:
            fails, text = hatch_weight(group, near, outlines)
            failures += len(fails)
            print("".join(f"\n      {line_text}" for line_text in text)[1:]
                  + "".join(f"\n      FAIL: {fail}" for fail in fails))
    if not seen["groups"]:
        print("  the subject has no group of parallel marks in this box")
    print("\n<< marks a group missing, an angle off by more than 20deg, a spacing off by "
          "more than half,\nor coverage under half the subject's. FAIL is a hatch mark over "
          f"{HATCH_WIDTH}x the subject's width,\nor over {HATCH_WIDTH}x its share of the "
          "outline's weight (outline = the 95th percentile line\nover the whole picture). "
          "Numbers say where the hatching is; they are not marks.")
    return seen, made, failures


def linework(drawing, subject, inventory_path, line, box=None):
    """--linework: every parts.json entry that carries `hatch` is measured on
    the drawing, and the drawing's line weight span against the subject's.
    Returns (failures, unchecked)."""
    raw = load_parts(inventory_path)
    if drawing.size != subject.size:
        print(f"the drawing is {drawing.width}x{drawing.height}; resized to the subject's "
              f"{subject.width}x{subject.height}, so every width below is in the subject's pixels")
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    failures = unchecked = 0
    if box is None:
        boxes = [entry["box"] for name, entry in raw.items()
                 if not name.startswith("_") and isinstance(entry, dict) and "box" in entry]
        if boxes:
            box = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                   max(b[0] + b[2] for b in boxes), max(b[1] + b[3] for b in boxes)]
            box = [max(0, box[0]), max(0, box[1]), min(subject.width, box[2]) - max(0, box[0]),
                   min(subject.height, box[3]) - max(0, box[1])]
    if box is None:
        box = [0, 0, subject.width, subject.height]
    rows = [(name, entry) for name, entry in raw.items()
            if not name.startswith("_") and isinstance(entry, dict) and entry.get("hatch")]
    print(f"{len(rows)} entries carry a hatch measurement (line marks up to {line}px wide)")
    outlines = tuple(outline_weight(_crop_grey(image, box), line) for image in (subject, drawing))
    if rows:
        print("outline weight (95th percentile line over "
              f"{','.join(map(str, box))}): subject "
              + ", drawing ".join("none" if found is None else f"{found:.0f}px" for found in outlines))
    if not rows:
        print("  NOTHING TO CHECK for hatching: no entry carries `hatch`. If the subject has "
              "hatched\n  or textured regions, measure each with --hatch and write it into its entry.")
    for name, entry in rows:
        want = entry["hatch"]
        if "angle" not in want:
            sys.exit(f"parts.json: {name!r} hatch has no angle")
        light = bool(want.get("light"))
        seen = hatching(_crop_grey(subject, entry["box"]), line, light)
        made = hatching(_crop_grey(drawing, entry["box"]), line, light)
        theirs, their_off = match_group(seen["groups"], want["angle"])
        ours, our_off = match_group(made["groups"], want["angle"])
        print(f"\n  {name}  box {','.join(map(str, entry['box']))}  written {want['angle']:.0f}deg"
              + (f", spacing {want['spacing']}px" if want.get("spacing") else "")
              + (f", length {want['length']}px" if want.get("length") else "")
              + (", pale lines" if light else ""))
        print(f"    subject: {_group_text(theirs)}  (coverage {seen['coverage']:.0%})")
        if grain_text(seen, line):
            print("    " + grain_text(seen, line))
        print(f"    drawing: {_group_text(ours)}  (coverage {made['coverage']:.0%})")
        if theirs is None or their_off > 20:
            unchecked += 1
            print(f"    UNCHECKED: the subject has no line group within 20deg of the written "
                  f"{want['angle']:.0f}deg here")
            continue
        if ours is None or our_off > 20:
            failures += 1
            print(f"    FAIL: no line group within 20deg of {want['angle']:.0f}deg"
                  + (f" (nearest {ours['angle']:.0f}deg)" if ours else ""))
            wide = weight_span(_crop_grey(drawing, entry["box"]), 2 * line)
            if wide is not None and wide[2] > line:
                print(f"    hint: lines here run to {wide[2]:.0f}px, wider than --line {line}px. "
                      "A line over --line\n    reads as a dark flat, not a mark, so a narrow part "
                      "between two such edges\n    reads as one flat and its hatching is not seen. "
                      "Thin the edge under --line first.")
            continue
        flags = hatch_flags({"angle": want["angle"], "spacing": theirs["spacing"]},
                            made["groups"], seen["coverage"], made["coverage"])
        fails, text = hatch_weight(theirs, ours, outlines)
        failures += bool(fails)
        print("".join(f"    {line_text}\n" for line_text in text)
              + ("".join(f"    FAIL: {fail}\n" for fail in fails)[:-1] if fails else "    pass")
              + "".join(f"\n    << {flag}" for flag in flags))
    span = [weight_span(_crop_grey(image, box), line) for image in (subject, drawing)]
    print(f"\nline weights over {','.join(map(str, box))} (finest = 10th percentile, "
          "heaviest = 95th, on each mark's centre line):")
    for label, found in zip(("subject", "drawing"), span):
        print(f"  {label}: " + ("no line marks" if found is None else
                                f"finest {found[0]:.0f}px  middle {found[1]:.0f}px  heaviest "
                                f"{found[2]:.0f}px  span {found[2] / found[0]:.1f}x"))
    if span[0] is None:
        unchecked += 1
        print("  UNCHECKED: the subject has no line marks here")
    elif span[1] is None:
        failures += 1
        print("  FAIL: the drawing has no line marks here")
    else:
        want, have = span[0][2] / span[0][0], span[1][2] / span[1][0]
        if have < 0.5 * want:
            failures += 1
            ends = []
            if span[1][0] > 1.5 * span[0][0]:
                ends.append(f"its finest line is {span[1][0] / span[0][0]:.1f}x the subject's: "
                            "thin the interior lines")
            if span[1][2] < span[0][2] / 1.5:
                ends.append(f"its heaviest is {span[1][2] / span[0][2]:.1f}x the subject's: "
                            "weight the silhouette and the contact shadows")
            print(f"  FAIL: the drawing's span {have:.1f}x is under half the subject's {want:.1f}x"
                  + "".join(f"\n    {end}" for end in ends))
        else:
            print(f"  pass: span {have:.1f}x against {want:.1f}x")
    return failures, unchecked


def zoom(drawing, subject, box, factor=4):
    """One feature, magnified: subject left and drawing right for a box taller
    than wide, subject above and drawing below otherwise.

    The other checks measure placement: whether a mark landed where it was
    meant to. None of them can see whether the mark is any good: whether it
    tapers, whether its weight fits the hierarchy, whether the shape has one
    continuous curvature or three lumps. These only show at the scale a hand
    works at, which is much larger than the scale a drawing is judged at, and
    they account for most of the difference between a sketch and a finished
    drawing.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    x, y, width, height = box
    size = (max(1, round(width * factor)), max(1, round(height * factor)))
    above = ruled(subject.crop((x, y, x + width, y + height)).resize(size, Image.LANCZOS), box, factor)
    below = ruled(drawing.crop((x, y, x + width, y + height)).resize(size, Image.LANCZOS), box, factor)
    # a tall box stacked twice came out 8646x16472 and was shown at an eighth of
    # its size, so tall boxes go side by side and only wide ones are stacked
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
    """A crop with its picture coordinates ticked along the top and left margin,
    so what you see can be named. Ticks orient and do not measure: points read
    off a ticked crop by eye came out 30-60px off at 4x, and `--scan` is what
    gives a coordinate."""
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
    """The two sets of lines over one box, in one image: the subject's ink in
    blue, the drawing's in red, black where they coincide, over the subject in
    pale grey.

    An outline can match row for row while the likeness is wrong, because
    interior lines carry likeness too (a nose's ridge, a brow, the fold of a
    cheek). In one case a face's right edge sat within 10px of the subject's on
    every row and still read wrong, because the nose's ridge line ran diagonally
    from brow to nostril in the subject and near-vertically down the far edge in
    the drawing. An outline scan cannot see an interior line. This can. It gives
    no number: for each blue line you decide which red line is meant to be it,
    and a distance between the two inks would shrink as more ink is added."""
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    x, y, w, h = box
    grey = [np.asarray(image.crop((x, y, x + w, y + h)).convert("L"), dtype=float)
            for image in (subject, drawing)]
    base = 255 - (255 - grey[0]) * 0.22
    out = np.stack([base] * 3, axis=-1)
    if value:
        # a dark flat (a glove, a hat) is under the darkness threshold and
        # would come back as one blue mass, so classify to the palette's line names
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
    column), subject beside drawing. This is the tool that settles proportion.

    Per row, `edge` is the first pixel, coming in from `side`, that is not the
    ground, and `ink` lists the dark runs from that side inward. Read the diff
    column for the outline and the ink columns for the lines inside it. A thick
    line drawn as two strokes shows as one run against two, and an interior line
    in the wrong place shows as runs that drift apart while the edges agree.
    With `value` (palette colours, indices wanted) the runs are of those palette
    names instead of dark. Use that for a group of vents, an orange insert in a
    grey shell or a set of bands, which a darkness threshold cannot tell apart."""
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
          f"{runs_of}, from the {side} inward. picture coordinates.")
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
                         for start, width in found][:12])
        diff = "" if None in edges else f"{edges[1] - edges[0]:+5d}"
        flag = ("  <<" if diff and abs(edges[1] - edges[0]) > loose else "") + \
               (f"  runs {len(runs[0])}|{len(runs[1])}" if len(runs[0]) != len(runs[1]) else "")
        cells = ["  ".join(f"{a}-{b}" for a, b in found) or "-" for found in runs]
        print(f"{origin + at:6d}  {str(edges[0]):>7s} {str(edges[1]):>7s} {diff:>5s}   "
              f"{cells[0]}  |  {cells[1]}{flag}")
    print(f"\n<< marks an edge more than {loose}px off; `runs a|b` a row whose line count "
          "differs.\nA number here tells you how far to move a mark; a look at a "
          "side-by-side does not.\nProportion judged by eye from a pair was wrong in "
          "both directions on one\npicture, and a scan settled every case.")


def masses(drawing, subject, box=None, colours=3, blow=3):
    """Both pictures reduced to flat value masses, side by side, with no line.

    This check sees shape, which the rest of the kit cannot. Everything else
    here compares marks: where they landed, how wide they are, whether colour
    agrees with them. A head can pass all of those, with every feature inside its
    own measured box and every box within ten pixels of the subject's, and still
    not be a face, because a wedge and an oval share a bounding rectangle and
    differ in the way that matters.

    Reducing each picture to a few values removes the line, the detail and the
    rendering, and leaves the masses the eye reads first. Do it early, before any
    contour. If the masses do not match the subject's, nothing drawn on top of
    them will fix it.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    if box:
        x, y, width, height = box
        subject = subject.crop((x, y, x + width, y + height))
        drawing = drawing.crop((x, y, x + width, y + height))
    # the line is closed away at a working size, then the design is read at
    # thumbnail size: a whole picture is brought down to it, a small crop blown up
    work = min(1.0, 1800 / max(subject.size))
    size = (max(1, round(subject.width * work)), max(1, round(subject.height * work)))
    subject, drawing = (image.resize(size, Image.BOX) for image in (subject, drawing))
    # one line width for both, the subject's. Measured on each picture, a
    # drawing inked heavier than its subject would have its tyres closed away as
    # line
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
    """The picture with its line closed away and its dark masses kept.

    Line is dark and thin: a dark pixel that a disc of the image's own line width
    cannot sit in. Those pixels, and a one-pixel skin of anti-aliasing round
    them, take the colour of the nearest pixel that is not line. A dark mass (a
    tyre, a solid hat) is wider than the disc and stays.

    This must happen before any value is chosen. Quantising first and dropping
    the darkest cluster afterwards goes wrong in two measured ways. An inked
    subject's line drags its skin into the light class, while the same skin on
    an ink-less stage-2 drawing falls dark, so the gate reports a difference
    that is only the ink the stage forbids. And on a drawing whose ground
    outnumbers everything else, a median cut spends every cluster but one on
    shades of the ground, the whole figure lands in the darkest cluster, and
    dropping it leaves a blank field.
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
    """`colours` value levels, by 1-D k-means on the subject's lightness, and the
    mean colour of each. Lightness is used because a design is read in value.
    K-means is used because a median cut splits the most populous colour and, on
    a picture that is mostly ground, spends its levels on the ground. The
    subject's levels are used for both pictures because quantising each to its
    own levels can put the same palette colour in the mid class of one and the
    dark class of the other."""
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


def unfilled(drawing, subject, paper, ground, ink=90, thickness=3, box=None):
    """Paper inside the subject's silhouette: a flat that stops short of its ink.

    `--registration` alone finds only paper that the line art walls in
    completely. A fill that falls short along an open boundary leaves a bay, not
    an island: the background flood reaches it and the check calls it outside.
    That bay is by far the commoner fault, and it reads as a pale notch in the
    object wherever the ink is thin or the contour bulges.

    The subject settles it: anywhere the subject carries the object, the drawing
    must carry ink or colour and never bare paper. That takes two colours, which
    are not the same one. The subject's ground (palette.json's `background`)
    says where the object is, and the render's paper says where the drawing is
    bare. If they are read as one colour, a check copy rendered on a paper that
    nothing paints with makes every pixel of the subject count as object (the
    space between spokes, the inside of a wheel), and every region holding
    spokes or pebbles is reported as unfilled. The rule this enforces is the
    one in the stages: a flat is drawn past where its ink will go, so the ink
    covers the flat's edge and never the other way round. Trap outward by at
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
    inside = np.zeros(bare.shape, bool)
    if box:
        # one part's own patches: in a split scene the whole-picture list holds
        # patches that belong to other agents' parts, which hides the result for
        # the part being checked
        x, y, w, h = box
        inside[y:y + h, x:x + w] = True
    else:
        inside[:] = True
    holes = ndimage.binary_opening(object_here & bare & inside, np.ones((thickness, thickness)))
    # the inverse: a flat painted where the subject is bare ground. A mass whose
    # crest overshot a rock pile put 40k px of tan on bare ground in six places
    # and no gate listed it. Opened wide, so the ink's own ramp beside every
    # line does not count
    painted = ~bare & (drawn.mean(axis=2) >= ink) & ~object_here & inside
    painted = ndimage.binary_opening(painted, np.ones((thickness * 3, thickness * 3)))
    floor = max(120, bare.size * 1.1e-4)
    over, over_count = ndimage.label(painted)
    over_sizes = ndimage.sum(painted, over, range(1, over_count + 1)) if over_count else []
    over_keep = [index for index in range(1, over_count + 1) if over_sizes[index - 1] >= floor]
    if over_keep:
        print(f"{len(over_keep)} painted patch(es) — a flat where the subject shows bare ground:")
        for index in sorted(over_keep, key=lambda i: -over_sizes[i - 1]):
            ys, xs = np.nonzero(over == index)
            print(f"  {int(over_sizes[index - 1]):6d}px at x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
        print()

    labels, count = ndimage.label(holes)
    if not count:
        print("no bare paper inside the subject's silhouette: every flat reaches its ink.")
        return len(over_keep)
    sizes = ndimage.sum(holes, labels, range(1, count + 1))
    # 120px at a delivered size of about a megapixel, and the same share of a
    # 4x working space. A fixed floor would list every hairline of drift at 4x
    keep = [index for index in range(1, count + 1) if sizes[index - 1] >= floor]
    print(f"{len(keep)} unfilled patch(es) — bare paper where the subject has the object:")
    # every patch, not the largest dozen: a bare triangle at a seam between two
    # agents' sections can be the 18th of 30 and be missed
    for index in sorted(keep, key=lambda i: -sizes[i - 1]):
        ys, xs = np.nonzero(labels == index)
        print(f"  {int(sizes[index - 1]):6d}px at x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
    print("\na flat is drawn past where its ink will go, so the ink covers the flat's\n"
          "edge. A fill outline taken from the tracer sits at the colour transition,\n"
          "which is inside the ink: the flat then falls short by half a line width\n"
          "and the ground shows through wherever the contour bulges out.")
    return len(keep) + len(over_keep)


def registration(drawing, paper, ink=90, floor=40):
    """Where colour and line disagree, checked on a render.

    `colour.md` names two failures, and each has an exact definition in pixels.
    Flood the picture inward from its border, through anything that is not line,
    and the drawing splits in two: what the line encloses, and what it does not.

    - A spill is colour the flood reached. It lies outside the line art, so
      nothing covers its edge and it reads as a smear beside the drawing.
    - A gap is paper the flood did not reach. It is walled in by line and colour
      on every side, so it reads as a hole.
    - Where the flood pours into a region it should not have reached, the line
      art is open. A contour that does not close is the same defect seen from the
      other side.

    This finds them and does not fix them. What to do about each is up to you,
    and the answer is often nothing: a trap that runs under its own line is
    meant to be there.
    """
    pixels = np.asarray(drawing.convert("RGB"), dtype=np.int16)
    tone = pixels.mean(axis=2)
    is_paper = np.abs(pixels - np.asarray(paper, dtype=np.int16)).max(axis=2) <= 18
    is_line = tone < ink

    # Everything reachable from the paper at the border without crossing a line.
    # The seeds are the bare paper only, not every border pixel: a shape is
    # meant to run off the edge of the picture rather than stop on it, and
    # seeding the whole border would call each of those a spill.
    open_ground = ~is_line
    border = np.zeros_like(open_ground)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    outside = ndimage.binary_propagation(border & is_paper & open_ground, mask=open_ground)

    spill = outside & ~is_paper & ~is_line
    gap = is_paper & ~outside

    # a one-pixel skin of both is the renderer's anti-aliasing; open the masks
    # so only faults with real thickness survive
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
    solid until part of it runs back the other way. That part winds to zero and
    shows the ground. For example, points typed at the head of a traced list
    instead of at their place round the outline can leave ground across a
    forehead, and every other gate passes it. Yields (op index, hole area, a
    point in it)."""
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
# The script-reading gates below must not treat every stroke as visible. The
# canvas paints in write order, `erase` removes a stage, `back` sends one under
# everything, and a closed flat hides whatever was written before it. A gate
# that ignores this lists every correct occlusion as a fault. In one picture the
# --doubled list had 29 items, and each was a far edge that a nearer flat,
# written after it, already hid.

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
    painted above z bury it."""

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


CROSSING_FLOOR = 5.0   # degrees: two lines meeting at less than this are one edge


def _crossing(run, other, tree, touch, length, ends, near_ends):
    """Is this run two lines crossing or meeting, rather than one edge stated twice?

    Two lines that cross at an angle are within `touch` of each other for
    2 * touch / sin(angle), and no further, and they end the run on opposite
    sides of each other. Crossing spokes and a chain over a spoke do exactly
    that. Two lines that meet in a V or a T (two spokes into one hub hole, one
    ending on the other) touch for half that, and the run holds an end of one
    of them. Two guesses at one edge run alongside each other for longer than
    their angle explains, or meet at under CROSSING_FLOOR degrees, and stay
    listed."""
    nearest = tree.query(run)[1]
    nearest = nearest[nearest < len(other)]
    if len(nearest) < 2 or len(run) < 2:
        return False
    seg = other[nearest.min():nearest.max() + 1]
    along_other = seg[-1] - seg[0]
    along_run = run[-1] - run[0]
    if np.hypot(*along_other) < 1e-6 or np.hypot(*along_run) < 1e-6:
        return False
    cosine = abs(float(along_other @ along_run)) / (np.hypot(*along_other) * np.hypot(*along_run))
    angle = math.degrees(math.acos(min(1.0, cosine)))
    if angle < CROSSING_FLOOR:
        return False
    if length > 1.5 * 2 * touch / math.sin(math.radians(angle)):
        return False
    if np.linalg.norm(run[:, None, :] - ends[None, :, :], axis=2).min() <= near_ends:
        return True     # a V or a T: one of the two lines ends here
    normal = np.array([-along_other[1], along_other[0]]) / np.hypot(*along_other)
    sides = (run[[0, -1]] - seg[0]) @ normal
    return bool(sides[0] * sides[1] < 0)


def doubled(ops, touch=3.0, near_ends=8.0, floor=15.0):
    """Is any edge stated twice on the page? Reads the script, and replays it.

    The commonest mark-level fault in a scene is one boundary drawn once as one
    object's silhouette and again as its neighbour's, from two different
    guesses. On the page it reads as a field of crossing loops and is easily
    mistaken for bad curve control. No check that looks at pixels finds it, since
    two contours 2px apart are two correct-looking contours.

    So it is checked where the fault lives, in the script, as two ink strokes
    whose centrelines run together for a long way. A simple version would flag
    correct work in three ways, and each is handled:

    1. A shared endpoint is not a doubled edge. Two strokes that meet at one
       named point must pass through that point, so every correct junction looks
       like an overlap. Runs anchored at a shared endpoint are excluded.
    2. Length is arc length, not a sample count. Densifying repeats each
       segment's endpoint as the next segment's start, so a 4px stretch counts
       as a dozen samples and every measured run comes out about twice its size.
    3. A covered edge is not on the page. The far form's outline runs on under
       the nearer form's flat, written after it, and so does the near form's ink
       over the same spot: two strokes in the script, one line on the page. Read
       without the write order, every correct occlusion in one picture came back
       as a doubling (29 items, none real). A run where the earlier stroke is
       buried under a later flat by half its own width is dropped. If that flat
       is later moved, the doubling shows up here again.
    4. A crossing is not a doubling. Two spokes that cross in an X touch for a
       short run fixed by their angle and end it on opposite sides of each
       other (see `_crossing`). Two lines that run side by side, such as a pair
       of parallel cables, are still listed: the gate cannot tell them from one
       edge drawn twice, so look before you merge.
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
                # is the sharing, not a second copy of the edge
                if np.linalg.norm(run[:, None, :] - ends[None, :, :], axis=2).min(axis=1).max() <= near_ends:
                    continue
                if cover.buried(run, lower[4], lower[5]).mean() >= 0.8:
                    continue
                length = float(np.linalg.norm(np.diff(run, axis=0), axis=1).sum())
                if _crossing(run, other[2], trees[second], touch, length, ends, near_ends):
                    continue
                worst = max(worst, length)
                if length > floor:
                    hits.append((one[0], one[1], other[0], other[1], round(length)))
    return hits, worst, len(lines)


HAND_GAP = 4.0          # px: the most a styled hand's line stops short (pen.py, 1-4 px)
NEAR_MISS = (1.0, 8.0)  # line widths: a gap in this band is neither a join nor a separation


def _object(tag):
    """The object a stroke belongs to: its tag up to the first '.'."""
    return str(tag or "").split("+")[0].split(".")[0]


def _pair_excused(one, other, gaps):
    """Is the pair named in parts.json's `_gaps` list, either way round, by tag
    or by a prefix of it?"""
    kin = lambda tag, name: tag == name or tag.startswith(name + ".")
    for row in gaps:
        a, _, b = str(row).partition("/")
        if (kin(one, a) and kin(other, b)) or (kin(one, b) and kin(other, a)):
            return True
    return False


def joins(ops, gaps=()):
    """Ink ends that stop just short of the mark they run at, in the same object.

    A chain, a cable, a frame member or an outline that is meant to meet another
    line and stops a few line widths away reads as a broken line. The eye
    accepts a join (the end touches) and a clear separation (the end stops well
    away), and reads anything between as a mistake. A pixel check cannot tell a
    near miss from a deliberate gap, so this reads the script.

    For each end of each open ink stroke on the page:

    1. Every other ink or fill mark of the same object (the tag up to its first
       '.') is measured edge to edge: the distance between centrelines less half
       of each mark's width. A fill counts by its outline. The stroke's own line
       counts too, beyond the stretch next to the end, so a ring left open is
       found.
    2. If any of them is closer than the lower bound, the end is joined and
       passes. The lower bound is one line width of the end's stroke, and never
       under HAND_GAP + 1, so the 1-4 px a styled hand leaves short of a
       junction is not listed.
    3. Otherwise every mark the end runs at, within the upper bound
       (NEAR_MISS[1] line widths), is listed. A mark the end runs at lies ahead
       of it, within 60 degrees of its direction. Marks beside the end (the next
       line of a hatched group, a parallel streak) are spacing, not a missed
       join. Three more are skipped: an ink mark under half the end's width,
       since a heavier line crosses a hairline (a spoke, a cable) and does not
       end on it; a mark with the end's own tag, since that is one group's
       spacing (so a path drawn in several strokes takes one tag per run); and a
       pair in `gaps`, parts.json's `_gaps` list of "tagA/tagB" pairs meant to
       stop short, matched by tag or a prefix of it, either way round.

    An end buried under a flat painted after it is not on the page and is
    skipped. Returns (end tag, end point, [(gap px, other tag), ...]), the
    smallest gap first."""
    cover = Cover(ops)
    marks = []
    for index, z in cover.z.items():
        op = ops[index]
        if op.get("stage") not in ("ink", "fill") or not op.get("points"):
            continue
        points = np.asarray([p[:2] for p in op["points"]], float)
        if op.get("closed") and len(points) > 2:
            points = np.vstack([points, points[:1]])
        walked = _walk(points) if len(points) > 1 else points
        along = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(walked, axis=0), axis=1))])
        marks.append((index, str(op.get("tag", "")), _object(op.get("tag")), op, points,
                      walked, along, cKDTree(walked), nib(op)))
    found = []
    for index, tag, thing, op, points, walked, along, _, width in marks:
        if op.get("stage") != "ink" or op.get("closed") or len(points) < 2 or along[-1] < 1.0:
            continue
        low, high = max(NEAR_MISS[0] * width, HAND_GAP + 1.0), NEAR_MISS[1] * width
        back = max(2.0 * width, 8.0)
        ends = ((walked[0], walked[int(np.searchsorted(along, min(back, along[-1])))], along > high + width),
                (walked[-1], walked[int(np.searchsorted(along, max(0.0, along[-1] - back)))],
                 along < along[-1] - high - width))
        for end, behind, own_far in ends:
            if cover.buried(end[None, :], cover.z[index], width / 2.0)[0]:
                continue
            heading = end - behind
            heading = heading / max(float(np.hypot(*heading)), 1e-9)
            near = []
            for other, other_tag, other_thing, other_op, _, other_walked, _, tree, other_width in marks:
                if other_thing != thing:
                    continue
                if other == index:
                    if not own_far.any():
                        continue
                    pool = walked[own_far]
                    at = pool[int(np.argmin(np.linalg.norm(pool - end, axis=1)))]
                else:
                    at = other_walked[tree.query(end)[1]]
                centre = float(np.hypot(*(at - end)))
                gap = centre - width / 2.0 - other_width / 2.0
                ahead = centre > 1e-9 and float(np.dot((at - end) / centre, heading)) >= 0.5
                fine = other_op.get("stage") == "ink" and other_width < width / 2.0
                sibling = other != index and other_tag == tag
                near.append((gap, other_tag, ahead and not fine and not sibling))
            if not near or min(gap for gap, _, _ in near) < low:
                continue
            missed = {}
            for gap, other_tag, runs_at in near:
                if runs_at and gap <= high and not _pair_excused(tag, other_tag, gaps):
                    missed[other_tag] = min(missed.get(other_tag, gap), gap)
            if missed:
                found.append((tag, tuple(int(round(c)) for c in end),
                              sorted((round(gap, 1), other_tag) for other_tag, gap in missed.items())))
    return sorted(found, key=lambda row: row[2][0][0])


def backwards_keys(inventory):
    """Overlap rows whose key is written near/far: `in_front` names the key's
    first half. The key is `far/near`. `depth` decides by `in_front` alone, so
    such a row is still checked the right way round, but a key that contradicts
    its own decision is a sign the decision was written in a hurry."""
    return [key for key, entry in inventory.items()
            if isinstance(entry, dict) and entry.get("in_front")
            and len(key.split("/")) == 2 and key.split("/")[0] == entry["in_front"]]


SAME = "same"   # in_front value for two sub-forms of one surface (a ruff and a chest)


def depth(ops, inventory):
    """Does the write order deliver the occlusion the inventory decided on?

    A row whose `in_front` is "same" names two sub-forms of one surface, such
    as a neck ruff and the chest, or a muzzle and the head, where each one's
    ink crosses the other's flat and neither order is right. It has no order
    to check. It still resolves only when both sides are tags on the page, and
    being a row, it takes the pair off the UNLISTED list.

    Occlusion comes only from the order marks are written in. A flat cannot hide
    ink, because the ink is above it. So for any two forms that overlap, every
    ink stroke of the far one has to be written before the first flat of the
    near one. If they are written the other way round, with all the fills
    together and then all the inks (which is what you get by taking the stages
    as four passes over the whole drawing), the far form's outline is laid down
    on top of the near form's colour and runs straight across it. On the page
    that is a stray edge through the middle of the nearer object, and it reads
    as a crease or seam that is not there.

    Nothing that looks at pixels finds it, because the pixels are fine: every
    flat is present, filled, registered and inside its box, and the stray edge
    is a perfectly good line. It is checked here, in the script, against the
    `in_front` column the overlaps table already records.

    Two points are easy to get wrong:

    1. It compares the far form's last ink against the near form's first fill. A
       form is many ops, so comparing any other pair of extremes would pass a
       document that interleaves the two forms wrongly in the middle.
    2. An unmatched name must fail, not pass. The gate can only see a pair whose
       inventory names and stroke tags use one vocabulary. If the tags use a
       private shorthand, every pair resolves to nothing and the gate would
       report success on an unchecked drawing. Unresolved rows are reported as
       loudly as failures and exit non-zero.
    """
    def owns(tag, name):
        return any(part == name or part.startswith(name + ".")
                   for part in str(tag).split("+"))

    pairs, same = [], []
    for key, entry in inventory.items():
        near = entry.get("in_front") if isinstance(entry, dict) else None
        if not near:
            continue
        sides = key.split("/")
        if near == SAME:
            same.append((key, sides))
            continue
        far = [side for side in sides if side != near]
        pairs.append((key, near, far[0] if len(sides) == 2 and len(far) == 1 else None))

    rows = [(near, far) for _, near, far in pairs if far]

    def counts(tag, name, other):
        """A mark counts for `name` unless a row names its sub-form more
        precisely: a sub-form with a row of its own is decided there and opts
        out of its parent's rows. For example, a part tagged `wheel.front.hub.axle`
        and written in front of `bike.fork.near` would fail three
        `wheel.front/bike.*` rows by prefix, though its own row
        `bike.fork.near/wheel.front.hub.axle` was honoured."""
        if not owns(tag, name):
            return False
        top = other.split(".")[0]
        return not any(owns(tag, longer) and longer.startswith(name + ".")
                       and mate.split(".")[0] == top
                       for a, b in rows for longer, mate in ((a, b), (b, a)))

    hits, unresolved = [], []
    for key, sides in same:
        # two sub-forms of one surface: neither is in front, so there is no
        # order to check, but both names must still be tags on the page
        if len(sides) != 2:
            unresolved.append((key, "the key does not name exactly two forms"))
            continue
        for side in sides:
            if not any(owns(op.get("tag"), side) for op in ops if op.get("stage") in ("fill", "ink")):
                unresolved.append((key, f"nothing is tagged '{side}'"))
    for key, near, far in pairs:
        if far is None:
            unresolved.append((key, f"the key does not name exactly two objects either side of '{near}'"))
            continue
        near_fill = [i for i, op in enumerate(ops)
                     if op.get("stage") == "fill" and counts(op.get("tag"), near, far)]
        near_ink = [i for i, op in enumerate(ops)
                    if op.get("stage") == "ink" and counts(op.get("tag"), near, far)]
        far_ink = [i for i, op in enumerate(ops)
                   if op.get("stage") == "ink" and counts(op.get("tag"), far, near)]
        far_fill = [i for i, op in enumerate(ops)
                    if op.get("stage") == "fill" and counts(op.get("tag"), far, near)]
        # the near form's cover is its first flat. A form with no flat (a
        # cable, a spoke) covers with its first ink, and without that its row
        # would never resolve
        cover = near_fill[0] if near_fill else (near_ink[0] if near_ink else None)
        # before any ink (S2), the order still exists between the flats
        behind = far_ink[-1] if far_ink else (far_fill[-1] if far_fill else None)
        tagged = lambda name: any(owns(op.get("tag"), name) for op in ops
                                  if op.get("stage") in ("fill", "ink"))
        if (cover is None and tagged(near)) or (behind is None and tagged(far)):
            continue  # every mark of one side is decided by its sub-forms' own rows
        if cover is None:
            unresolved.append((key, f"nothing is tagged '{near}'"))
        elif behind is None:
            unresolved.append((key, f"nothing is tagged '{far}'"))
        elif behind > cover:
            hits.append((key, far, behind, near, cover))
    return hits, unresolved, len(pairs) + len(same)


def crossings(ops, inventory, floor=None):
    """Where one part's ink runs inside another part's flat, for pairs that no
    overlap row decides. --depth checks only the rows it is given, so a pair
    nobody listed would pass it unchecked while the gate printed PASSES.

    Parts are the inventory's own keys. A stroke belongs to the longest key its
    tag starts with, and two parts related as parent and child, or named
    together in one '+' tag, count as one form here. For each unlisted pair it
    reports how far the ink runs inside the other's flat and whether the write
    order shows it (drawn across that flat) or hides it (buried under it).
    Neither is a verdict: an unlisted strap drawn over a jacket is right to
    show, and a far outline buried under a near flat is how occlusion is drawn.
    This is the list of overlaps nobody decided."""
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
    """Fold the typography a shape note is written with down to what the default
    bitmap font can draw. An em dash rendered as a tofu box in the middle of a
    claim leaves you guessing at the claim."""
    for fancy, flat in (("\u2014", "--"), ("\u2013", "-"), ("\u2018", "'"),
                        ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
                        ("\u2026", "..."), ("\u00d7", "x"), ("\u00b0", "deg"),
                        ("\u2192", "->"), ("\u00a0", " ")):
        text = text.replace(fancy, flat)
    return "".join(character if character.isprintable() and ord(character) < 127
                   else "?" for character in text)


ENTRY_KEYS = {"shape", "box", "tier", "front_of", "touches", "gap", "in_front", "count",
              "value", "hatch"}
HATCH_KEYS = {"angle", "spacing", "length", "light"}
_WARNED = set()


def unknown_keys(raw):
    """Keys in parts.json entries that no check reads. A key in the wrong place
    is silently ignored: `"light": true` beside `hatch` instead of inside it
    checks dark lines where pale ones were meant."""
    found = []
    for name, entry in raw.items():
        if name.startswith("_") or not isinstance(entry, dict):
            continue
        for key in sorted(set(entry) - ENTRY_KEYS):
            hint = " (it belongs inside \"hatch\")" if key in HATCH_KEYS else ""
            found.append(f"{name!r} has a key no check reads: {key!r}{hint}")
        hatch = entry.get("hatch")
        if isinstance(hatch, dict):
            for key in sorted(set(hatch) - HATCH_KEYS):
                found.append(f"{name!r} hatch has a key no check reads: {key!r}")
    return found


def load_parts(path):
    """parts.json, with a warning on stderr for every key no check reads."""
    with open(path) as handle:
        raw = json.load(handle)
    if os.path.abspath(path) not in _WARNED:
        _WARNED.add(os.path.abspath(path))
        for warning in unknown_keys(raw):
            print(f"WARN parts.json: {warning}", file=sys.stderr)
    return raw


def read_inventory(path):
    """Load `parts.json`, in either of the two forms an entry may take.

    The old form is a bare box, `"nose": [540, 336, 45, 50]`, and it still
    loads, but it is not the form to write a new one in. A box states where a
    part is and says nothing about what it is, so a box is all any check can
    compare it against, and the check then passes anything of the right size in
    the right place. In one drawing, a body described in shape notes came out
    structurally right, and a face described in boxes came out distorted.

    The form to write is a shape note with a box derived from it:

        "nose": {
          "shape": "a hooked wedge, bridge dead straight, tip dropping below
                    the nostril line",
          "box": [540, 336, 45, 50],
          "front_of": "face",
          "touches": "moustache"
        }

    An overlap is an entry like any other: `"bike.bar/rider.hand"`, keyed in
    the stroke-tag vocabulary so --depth can resolve it, with a shape note saying
    which is in front and how wide the gap is. It needs no machinery of its own.
    Overlaps are where scenes most often go wrong.
    """
    raw = load_parts(path)
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

    A reference's list of sub-forms is easy to read and not act on: an inventory
    can stop at a vehicle's crank and leave out the chain and gears. Prose that
    is read and skipped is not a gate, so each reference carries a ```checklist
    block:

        object: bike|bicycle
        sub-forms: tyre|tire rim spoke ...

    An object is present when any dotted segment of any key names it. A sub-form
    is present when a later segment of a key naming that object is the word or
    its plural, so a car's window does not stand in for a house's. Alternatives
    are joined by |. A block may hold several `object:` lines, each followed by
    its `sub-forms:` line. `_absent` in parts.json is one string,
    "name: reason; ..."."""
    raw = load_parts(inventory_path)
    sides = _key_sides(raw)
    excused = {item.split(":")[0].strip() for item in str(raw.get("_absent", "")).split(";")
               if ":" in item}
    words_of = lambda alternatives: alternatives.split("|")
    hit = lambda word, parts: word in parts or word + "s" in parts

    def under(objects):
        """The segments that follow the object's own segment, in every key naming it."""
        return [parts[parts.index(word) + 1:] for parts in sides
                for word in words_of(objects) if word in parts]

    missing = []
    for source, objects, subforms in _checklists(references):
        tails = under(objects)
        if not tails:
            continue
        gone = [alternatives for alternatives in subforms.split()
                if not any(hit(word, tail) for tail in tails for word in words_of(alternatives))
                and not set(words_of(alternatives)) & excused]
        if gone:
            missing.append((objects, source, gone))
    return missing


def _key_sides(raw):
    """Every side of every inventory key, as its dotted segments."""
    return [side.split(".") for key in raw if not key.startswith("_") for side in key.split("/")]


def _checklists(references=None):
    """Every (reference file, object alternatives, sub-forms) a ```checklist block holds."""
    import glob
    import re
    found = []
    for path in sorted(references or glob.glob(os.path.join(HERE, "reference", "*.md"))):
        text = open(path).read()
        for block in re.findall(r"```checklist\n(.*?)```", text, re.S):
            lines = [line.split(":", 1) for line in block.strip().splitlines() if ":" in line]
            pairs = [(value.strip(), lines[i + 1][1]) for i, (field, value) in enumerate(lines)
                     if field.strip() == "object"]
            if not pairs or any(len(lines) <= 2 * i + 1 or lines[2 * i + 1][0].strip() != "sub-forms"
                                for i in range(len(pairs))):
                raise SystemExit(f"--checklist: {os.path.basename(path)} has a block that is not "
                                 "'object:' / 'sub-forms:' line pairs")
            found += [(os.path.basename(path), objects, subforms) for objects, subforms in pairs]
    return found


def checklist_unmatched(inventory_path, references=None):
    """When the inventory has objects and no checklist object names any of them,
    (the inventory's top-level names, the checklist objects there are); else None.

    `checklist` passes such an inventory with nothing checked: a `rooster.*`
    inventory against a checklist keyed `bird` reads as every sub-form present.
    This is a warning and not a failure, because a subject may have no reference."""
    raw = load_parts(inventory_path)
    sides = _key_sides(raw)
    if not sides:
        return None
    available = [(objects, source) for source, objects, _ in _checklists(references)]
    named = {word for objects, _ in available for word in objects.split("|")}
    if any(named & set(parts) for parts in sides):
        return None
    return sorted({parts[0] for parts in sides}), available


def count_forms(drawing, subject, inventory_path, palette_path, min_area):
    """The count of a group of repeated forms, on the subject and on the drawing,
    against the number written in parts.json.

    Every other gate passes when something is absent. A group of small forms can
    be dropped before any drawing rule sees it (under a trace's minimum area,
    handed to a neighbour as line, or never counted) and the masses gate still
    passes, because at thumbnail size a spray of droplets does not change the
    design. An entry opts in with `"count": N` and `"value": "black+grey"`, the
    palette names its forms carry. Each box is classified to the palette on both
    images and the connected forms of those values are counted."""
    raw = load_parts(inventory_path)
    with open(palette_path) as handle:
        palette = json.load(handle)
    # the ground is classified too but never counted. If it were left out, it
    # would go to the nearest real name and a field of ground would count as one
    # of the forms
    names = list(palette)
    colours = np.array([[int(palette[name][at:at + 2], 16) for at in (1, 3, 5)]
                        for name in names], dtype=float)
    drawing = drawing.resize(subject.size, Image.NEAREST) if drawing.size != subject.size else drawing
    # a form must be thick, not merely large. An upscale's ramp along every line
    # classifies as thin, long specks of a real flat, and at 4x an area floor
    # counted 90 of a subject's 14 droplets. An inscribed radius of a quarter of
    # the line's half-width counts 14 and drops no real form, at 1x or 4x
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

    The other checks all ask whether a mark is right, and none of them can see an
    absence. A registration flood finds colour that disagrees with a line,
    `--weights` compares the widths of marks that exist, and `--zoom` confirms
    that one mark landed where it was aimed. A face with no nose passes all
    three, because nothing in the drawing is wrong. Something is missing, and
    missing has no pixels to measure.

    So the inventory is written first, before any mark, and this puts all of it
    in front of you at once, at a size where form can be judged. The boxes come
    from the subject, and the drawing is cropped by the same box, so it catches
    displacement as well as absence: a box that frames an ear in the subject and
    a blank cheek in the drawing tells you something that measuring the marks
    that are there never would.

    Each box is padded by a fifth before cropping, so a part that has moved
    reads as a moved part rather than as two unrelated pictures. Cropped tight, a
    displaced feature and an absent one look the same and you cannot tell which
    way it went.

    The percentages are the share of dark pixels in each box. On a single part
    they are a weak hint: they flag a part missing from bare ground and say
    nothing when some other part has drifted into its box. Read them across the
    whole inventory instead. A consistent offset in the same direction on every
    part is a real finding, and this check is the one that can make it. A
    drawing running ten to twenty points heavier than its subject in every box
    is not a set of local faults. It means the heaviest weight was matched and
    the lighter weights are being used far too freely, and there is no other way
    to see it.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    down = math.ceil(len(inventory) / across)
    label, gap, line = 15, 10, 11
    # The shape note is printed above the crops, so the verdict is read against
    # what the note claimed rather than against a bare picture. A check can only
    # verify what was stated; if the band is empty, this check is comparing a box
    # to a box.
    said = [plain(" -- ".join(part for part in (entry["shape"], entry["rel"]) if part))
            for entry in inventory.values()]
    # Four lines, and an overflow is flagged rather than trimmed away. A note
    # that will not fit in four lines of this band is too long to be a shape
    # note, and cutting one without a sign would leave you checking against half
    # a claim, which is the fault this band exists to remove.
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
            # How much is going on in this box, measured against the box's own
            # ground rather than against black. `share` above asks how dark the
            # box is, which only makes sense for ink on pale paper: on a dark
            # ground every box reads about 100% in both pictures, and a part
            # drawn as a pale shape reads about 0% in both, so the absence
            # detector below would not work. The local median is the ground, so
            # the fraction departing from it is the part, on whichever side of
            # the ground the part sits.
            # Measured on the tight box, never the padded one. The padding is
            # there so a part that has moved still shows something to look at.
            # If it were included in the statistic, the neighbours would hold the
            # number up and an erased part would read half-present instead of
            # gone. Measured: the same absent object scores 49% padded and 0%
            # tight.
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
            pen.text((left, top + label), "no shape note", fill=(200, 30, 30))
        # a quarter, not a third: an under-rendered part lands near a third (a
        # mat texture reading 0.33 of the subject's is thin, not absent), while a
        # part that is not there reads 0.
        # Normalised by how far along the whole drawing is. At a block-in every
        # part carries a fraction of the subject's activity because nothing is
        # filled in yet, so an absolute threshold would report all 81 parts
        # missing at the stage where this check is meant to be run. What matters
        # is whether a part is behind the drawing it belongs to: if the picture
        # as a whole is at 30% of the subject, a part at 30% is on schedule and
        # one at 3% is not there.
        want = body[0] * pace
        gone = body[0] > 4.0 and body[1] < want / 4.0
        numbers = (f"ink {share[0]:.0f}%->{share[1]:.0f}%  form {body[0]:.0f}%->{body[1]:.0f}%"
                   + ("   MISSING?" if gone else ""))
        pen.text((left, top + head + cell * 2 + 1), numbers,
                 fill=(200, 30, 30) if gone else (90, 90, 90))
        print(f"  {name[:28]:28s} {numbers}")
    return sheet


def ranking(drawing, subject, inventory):
    """What leads the eye, ranked: the drawing's order against the subject's.

    Every other check in this file asks whether a part is right. This one asks
    how loud it is, then discards the magnitude and keeps only the order. `ink`
    and `form` both rise wherever marks are added, so working harder anywhere
    moves them, but a ranking does not move. Add marks to every part and the
    order comes back unchanged. The only way to move a part up this list is to
    move another part down, which is the only kind of change a whole-picture
    pass should make, and this is the check for it.

    The statistic is the spread of value inside the part's own box. It is not how
    dark the box is or how much is going on in it. A thread of line on bare
    ground is busy and quiet, and a black mass against cream is one shape and
    shouts. The eye competes over spread, and that is how a tier-3 object can
    out-shout the subject of the picture without one mark in it being wrong.

    Read it in both directions:

    - A part far above its subject rank is competing with what it should be
      supporting. Knock it back. On most scenes this is the whole finish pass,
      because a picture cannot afford to build all its furniture but can always
      afford to quieten it, and quieting the furniture makes the built thing read
      as built.
    - A part far below is not carrying its share. At an overlap, whose box holds
      two objects meeting rather than one object, that is the specific failure
      of two forms merging into one value: the overlap has stopped existing, and
      drawing either object more will not bring it back.

    It ranks and does not decide, and a box is still only a box. Crop the part
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
    parse.add_argument("render", nargs="?", default="",
                       help="the render; the script-only checks (--joins, --doubled, --depth, "
                            "--stages, --checklist, --faces) do without it")
    parse.add_argument("--ref")
    parse.add_argument("--out", default="check.png")
    parse.add_argument("--width", type=int, default=460)
    parse.add_argument("--grid", type=int, default=0)
    parse.add_argument("--plumb", default="", help="comma-separated fractions of width")
    parse.add_argument("--squint", type=float, default=7.0)
    parse.add_argument("--overlay", action="store_true",
                       help="lay the drawing over the reference instead of beside it")
    parse.add_argument("--zoom", default="",
                       help="x,y,w,h in the reference's own pixels, so comparing "
                            "two renders of the same drawing needs the box in render "
                            "coordinates, not the subject's. Shows the two magnified: "
                            "side by side (subject left) for a box taller than wide, "
                            "else stacked (subject above, drawing below)")
    parse.add_argument("--unfilled", action="store_true",
                       help="with --ref: bare paper where the subject has the object")
    parse.add_argument("--faces", default="",
                       help="ops.json: flag fills simpler than their traced region")
    parse.add_argument("--regions", default="regions.json")
    parse.add_argument("--face-ratio", type=float, default=0.5)
    parse.add_argument("--grain", type=float, default=0.0,
                       help="--faces: serration narrower than this, in px, is the source's "
                            "grain, not a corner. 3x the upscale factor on an upscaled subject")
    parse.add_argument("--weights", default="",
                       help="comma-separated rows: print the mark widths each one crosses, "
                            "as width@centre")
    parse.add_argument("--hatch", default="",
                       help="x,y,w,h: the line marks in that box of the positional image (the "
                            "subject): coverage, and per group of parallel marks its angle, "
                            "spacing, length and width. With --ref drawing.png, the drawing's "
                            "box beside it, << on what differs, FAIL (exit 1) on hatch marks "
                            "over 1.6x the subject's width. Numbers only, never strokes")
    parse.add_argument("--linework", default="",
                       help="parts.json (needs --ref subject.png): FAIL where an entry's `hatch` "
                            "angle has no line group in the drawing's box, where that group's "
                            "marks are over 1.6x the subject's width or its share of the "
                            "outline's weight, and where the drawing's line weight span is "
                            "under half the subject's")
    parse.add_argument("--line", type=int, default=0,
                       help="--hatch, --linework: the widest mark read as a line; wider is a "
                            "flat. Default: the image's longer side / 200, at least 6")
    parse.add_argument("--light", action="store_true",
                       help="--hatch: read pale lines on a dark ground (a white line cut into a black)")
    parse.add_argument("--masses", action="store_true",
                       help="both pictures as flat masses, no line. This is the "
                            "check that sees shape. Takes --box x,y,w,h and --colours N")
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
                       help="a JSON file of {name: [x,y,w,h]}: every named part of "
                            "the picture, subject above and drawing below")
    parse.add_argument("--ranking", default="",
                       help="parts.json: what leads the eye, the drawing's order "
                            "against the subject's")
    parse.add_argument("--doubled", default="",
                       help="an ops JSON: is any edge stated twice? Reads the "
                            "script, not the render")
    parse.add_argument("--joins", default="",
                       help="an ops JSON: ink ends that stop one to eight line widths short of "
                            "another mark of the same object, neither joined nor clearly apart. "
                            "With --parts parts.json, pairs in its \"_gaps\" list are excused")
    parse.add_argument("--depth", nargs=2, metavar=("OPS", "PARTS"), default=None,
                       help="write order against the inventory's in_front column")
    parse.add_argument("--checklist", default="",
                       help="parts.json: every sub-form a reference's checklist names for an "
                            "object in the inventory has an entry, or a reason in _absent")
    parse.add_argument("--counts", default="",
                       help="parts.json (needs --ref): every entry with a count, counted "
                            "on the subject and on the drawing")
    parse.add_argument("--min-area", type=int, default=40,
                       help="--counts: the smallest form counted, in render pixels")
    parse.add_argument("--stages", default="",
                       help="an ops JSON: which stages exist, how many marks each, "
                            "and whether a drawing with ink has a gesture, block-in and "
                            "contour stage at all. Reads the script, not the render")
    parse.add_argument("--registration", action="store_true",
                       help="report every place the colour and the line disagree")
    parse.add_argument("--paper", default="#FAF1D2",
                       help="the render's paper, #rrggbb or R,G,B")
    parse.add_argument("--ground", default="",
                       help="--unfilled: the subject's ground, if not palette.json's background")
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
        unmatched = checklist_unmatched(args.checklist)
        if unmatched:
            tops, available = unmatched
            print(f"  WARN no checklist object matched any inventory object, so nothing was checked.\n"
                  f"  inventory's top-level objects: {', '.join(tops)}\n"
                  f"  checklist objects there are: "
                  + "; ".join(f"{objects} ({source})" for objects, source in available)
                  + "\n  if one of these is your subject under another name, key the inventory by "
                  "that name.\n  A subject with no reference has no checklist, and this is "
                  "then expected.")
            return
        print("  PASSES — every checklisted sub-form has an entry or a reason")
        return
    if args.stages:
        from pen import audit, STAGES, provenance, script_source
        with open(args.stages) as handle:
            ops = json.load(handle)
        counts, first, failures = audit(ops)
        for stage in STAGES + tuple(s for s in counts if s not in STAGES):
            print(f"  {stage:14s} {counts.get(stage, 0):4d} marks"
                  + (f"   first at op {first[stage]}" if stage in first else "   ABSENT"))
        for failure in failures:
            print(f"  FAIL {failure}")
        for index, area, at in self_crossing(ops):
            print(f"  HOLE fill at op {index}{' ' + ops[index]['tag'] if ops[index].get('tag') else ''}: "
                  f"{area}px near {at} winds to zero and shows the ground. A ring drawn as one "
                  "polygon has one on purpose; anywhere else the outline doubles back. Keep "
                  "perimeter order, run-on points included")
        if not failures and not counts.get("ink"):
            print("  no ink yet: the stages are gated from the first ink mark")
        elif not failures:
            print("  PASSES — the gesture, block-in and contour stages exist, in order. Whether "
                  "each ink mark\n  has a contour under it is not checked: on three finished "
                  "drawings 26-81% had none")
        source = script_source(ops, os.path.dirname(os.path.abspath(args.stages)))
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
        print("\ncounts are not a score: one token gesture stroke passes this and would "
              "not fool\nanyone who opens gesture.png. What this catches is a stage that "
              "does not exist,\nand a mark that was generated rather than drawn. "
              "Generated output pasted into\nthe script as literal lines passes it; "
              "the rule forbids that, not this gate.")
        sys.exit(1 if failures or generated else 0)

    if args.depth:
        with open(args.depth[0]) as handle:
            written = json.load(handle)
        inventory = load_parts(args.depth[1])
        hits, unresolved, count = depth(written, inventory)
        loose = crossings(written, inventory)
        print(f"{count} overlap rows carry an in_front decision")
        for key, far, ink_at, near, fill_at in hits:
            print(f"  FAIL {key}: '{far}' at op{ink_at} is written after "
                  f"'{near}''s cover at op{fill_at}, so that edge draws across it")
        for key, why in unresolved:
            print(f"  UNRESOLVED {key}: {why}")
        for key in backwards_keys(inventory):
            print(f"  WARN {key}: key written near/far, since in_front names its first half. "
                  "The key is far/near; in_front decides, so check it is the one in front")
        if not hits and not unresolved and count:
            print(f"  PASSES — the {count} listed occlusions are delivered by the write order")
        if not count:
            print("  NOTHING TO CHECK — no inventory entry carries in_front")
        shown = [row for row in loose if row[3] == "drawn across"]
        if shown:
            print(f"\n{len(shown)} unlisted overlaps show on the page, longest first. "
                  "This is a list to work through, not a verdict:")
            for length, ink, flat, how in shown[:20]:
                print(f"  UNLISTED {ink} ink {how} {flat}'s flat for {length}px")
            print("each is either the ink's part in front of that flat, or a crease across a "
                  "nearer\nform. Decide, and write the row into parts.json so the next run "
                  "checks it.")
        if len(loose) > len(shown):
            print(f"\n{len(loose) - len(shown)} more unlisted overlaps are buried under a flat "
                  "written after the\nink: occlusion the write order already delivers, "
                  "unchecked against any decision.")
        print("\nthe far form's ink must precede the near form's fill. A flat cannot "
              "hide ink,\nso written the other way the far outline runs straight across "
              "the nearer object\nand reads as a crease that is not there. An UNRESOLVED "
              "row is not a pass. It\nmeans the stroke tags and the inventory names do "
              "not use one vocabulary, and the\npair went unchecked.")
        sys.exit(1 if (hits or unresolved or not count) else 0)

    if args.doubled:
        with open(args.doubled) as handle:
            hits, worst, count = doubled(json.load(handle))
        print(f"{count} ink strokes; longest non-junction overlap {worst:.0f}px")
        for first, here, second, there, length in hits:
            print(f"  FAIL op{first}({here}) x op{second}({there})  {length}px")
        if not hits:
            print("  PASSES — no edge is stated twice")
        print("\na run at a shared endpoint is a junction, not a doubling, and is "
              "excluded.\nwhat this finds is one boundary drawn from two guesses, which "
              "reads as a\nfield of crossing loops and is easily mistaken for bad curve "
              "control.")
        sys.exit(1 if hits else 0)

    if args.joins:
        with open(args.joins) as handle:
            written = json.load(handle)
        gaps = load_parts(args.parts).get("_gaps", []) if args.parts else []
        if not isinstance(gaps, list):
            sys.exit('parts.json: "_gaps" is a list of "tagA/tagB" pairs')
        hits = list(joins(written, gaps))
        for tag, end, missed in hits:
            print(f"  NEAR MISS {tag} end at {end[0]},{end[1]} stops "
                  + ", ".join(f"{gap:.0f}px short of {other}" for gap, other in missed))
        if not hits:
            print("  PASSES — every ink end either meets a mark of its object or stops well clear")
        print(f"\na gap of {NEAR_MISS[0]:.0f} to {NEAR_MISS[1]:.0f} line widths reads as a line "
              "that missed, not as a join or a\nseparation. Close it by ending both strokes on one "
              "named point, or, where the subject\nshows the gap, add the pair to parts.json's "
              "\"_gaps\" list (\"tagA/tagB\").")
        sys.exit(1 if hits else 0)

    if args.faces:
        sys.exit(1 if faces(args.faces, args.regions, args.face_ratio, args.grain) else 0)

    if not args.render:
        parse.error("this check needs a render")
    drawing = Image.open(args.render).convert("RGB")
    plumbs = [float(value) for value in args.plumb.split(",") if value.strip()]

    if args.unfilled:
        if not args.ref:
            sys.exit("--unfilled needs --ref")
        paper = colour(args.paper)
        sys.exit(1 if unfilled(Image.open(args.render), Image.open(args.ref).convert("RGB"),
                               paper, colour(args.ground) if args.ground else ground_of(paper),
                               box=[int(part) for part in args.box.split(",")] if args.box else None)
                 else 0)

    if args.weights:
        rows = [int(part) for part in args.weights.split(",")]
        if not args.ref:
            # a bare weight swatch: the drawing's own runs, nothing to match
            grey = drawing.convert("L")
            for y in rows:
                print(f"y={y:4d}  drawing {said(marks(list(grey.crop((0, y, grey.width, y + 1)).getdata())))}")
            print("\nwidth@x, left to right, in the render's own pixels")
            return
        subject = Image.open(args.ref).convert("L")
        report(subject, drawing.convert("L").resize(subject.size, Image.LANCZOS), rows)
        return

    if args.hatch:
        box = [int(part) for part in args.hatch.split(",")]
        line = args.line or max(6, round(max(drawing.size) / 200))
        other = Image.open(args.ref).convert("RGB") if args.ref else None
        failures = hatch_report(drawing, other, box, line, args.light,
                                (f"subject ({os.path.basename(args.render)})",
                                 f"drawing ({os.path.basename(args.ref)})" if args.ref else "drawing"))[2]
        sys.exit(1 if failures else 0)

    if args.linework:
        if not args.ref:
            sys.exit("--linework needs --ref subject.png")
        subject = Image.open(args.ref).convert("RGB")
        line = args.line or max(6, round(max(subject.size) / 200))
        failures, unchecked = linework(drawing, subject, args.linework, line,
                                       [int(part) for part in args.box.split(",")] if args.box else None)
        print("\nFAIL is a subject's hatching left out, hatching heavier than the subject's "
              f"(over {HATCH_WIDTH}x its\nmark width, or over {HATCH_WIDTH}x its share of the "
              "outline's weight), or one weight where the\nsubject has a range. UNCHECKED means "
              "the written measurement does not reproduce on the subject;\nre-measure it with --hatch. Exit 1 is a FAIL, 2 UNCHECKED rows. Neither is a pass.")
        sys.exit(1 if failures else 2 if unchecked else 0)

    if args.masses:
        if not args.ref:
            sys.exit("--masses needs --ref")
        box = [int(part) for part in args.box.split(",")] if args.box else None
        masses(drawing, Image.open(args.ref).convert("RGB"), box, args.colours).save(args.out)
        print(f"wrote {args.out}")
        print("line, detail and rendering are gone; what is left is what the eye "
              "reads first.\nsay in words what shape each one is. If they are not "
              "the same shape, stop:\nnothing drawn on top of these masses will "
              "make them agree.")
        return

    if args.parts:
        if not args.ref:
            sys.exit("--parts needs --ref")
        inventory = read_inventory(args.parts)
        subject = Image.open(args.ref).convert("RGB")
        mute = [name for name, entry in inventory.items() if not entry["shape"]]
        # A full inventory runs to dozens of parts, and one sheet of them is too
        # tall to look at. Split it into pages that fit a single look each,
        # because a sheet you have to scroll gets skimmed.
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
              "one direction is a real\nfinding: a whole range of weights used too freely, "
              "which nothing else here can see.\nWhether a part that is present is "
              "any good is for you to judge.")
        if mute:
            # Loud on purpose. If this were silent, the sheet would still render,
            # the numbers would still look like a measurement, and nothing in it
            # would be comparing a shape to a shape.
            print(f"\n{len(mute)} of {len(inventory)} parts carry NO shape note, "
                  "so for those this check\ncompares a box against a box and can only "
                  "see absence and displacement:\n  " + ", ".join(mute[:12])
                  + (" ..." if len(mute) > 12 else ""))
        return

    if args.counts:
        if not args.ref:
            sys.exit("--counts needs --ref")
        rows = count_forms(drawing, Image.open(args.ref).convert("RGB"), args.counts,
                      "palette.json", args.min_area)
        if not rows:
            sys.exit("--counts: no entry carries a count -- write the counts into parts.json")
        wrong = unchecked = 0
        print(f"  {'entry':34s} count subject drawing")
        for key, want, seen, made in rows:
            if seen != want:
                # the instrument does not reproduce the written count on the
                # subject itself, so its count of the drawing means nothing
                # either way (spokes cut by spokes, slots joined by their own
                # ink, grain)
                verdict = "  UNCHECKED: the subject does not count to the written number here"
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
                  "box, and\nwhere that does not give the written count on the subject (forms crossing, "
                  "touching,\nor bounded by ink of their own value) it has no verdict on the "
                  "drawing. Count\nthose on --zoom, subject and drawing, and write both numbers in "
                  "notes.md.")
        print("\nthe count is the only gate that fails on an absence, and only where it can "
              "count\nthe subject. It reads a tight box on separate forms of one value "
              "(droplets, pebbles,\nteeth with dark gaps). Exit 1 is a FAIL, 2 is "
              "UNCHECKED rows. Neither is a pass.")
        sys.exit(1 if wrong else 2 if unchecked else 0)

    if args.ranking:
        if not args.ref:
            sys.exit("--ranking needs --ref")
        subject = Image.open(args.ref).convert("RGB")
        rows = ranking(drawing, subject, read_inventory(args.ranking))
        print(f"what leads the eye, worst disagreement first. value spread inside each "
              f"part's own\nbox, ranked 1..{len(rows)} in each picture. tier is the entry's "
              "`tier`; J is an overlap.\n")
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
              "down. An overlap that has gone\nquiet is two objects merged into one "
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
        print(f"{len(faults)} faults, largest first: area, kind, box in drawing coords\n")
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
              "walled in.\nboth are mistakes. a trap that runs under its own "
              "line is neither, and will\nnot appear here, but a flat mixed at "
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

    views = []
    if args.ref:
        views.append((fit(rule(Image.open(args.ref).convert("RGB"), args.grid, plumbs),
                          args.width), "subject"))
    views.append((fit(rule(drawing, args.grid, plumbs), args.width), "drawing"))
    views.append((fit(drawing.transpose(Image.FLIP_LEFT_RIGHT), args.width), "mirrored"))
    views.append((fit(drawing.filter(ImageFilter.GaussianBlur(args.squint)), args.width),
                  "squinted"))
    contact(views).save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
