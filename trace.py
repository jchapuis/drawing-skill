#!/usr/bin/env python3
"""Measure a flat-cel subject's regions once, mechanically, in its own space.

    python3 trace.py subject.png palette.json [--out regions.json] [--png regions.png]
                     [--ink black] [--line 8] [--min-area 150] [--fringe 0]
                     [--offset X,Y] [--space W,H]

Every pixel is classified to its nearest palette entry. Pixels of the ink colour
that lie in a run no wider than --line are handed to whichever region is
nearest, so two flats that share a drawn line meet along that line's centre --
which is where the ink stroke belongs. Ink wider than a line is a flat of that
colour and keeps its own region. Regions are cut before the line is handed out,
so two flats of one colour that a line separates stay two. Each becomes an entry:

    {"id": 3, "colour": "orange", "area": 22641, "box": [x, y, w, h],
     "centre": [x, y],            # the CENTROID -- often not inside the region
     "inside": [x, y],            # the region's deepest point: probe HERE
     "median": "#d37201",         # the region's own median pixel
     "blockin": [[x, y], ...],    # the outline as a few straights (6px tolerance)
     "contour": [[x, y], ...],    # the outline as a curve (1.5px tolerance)
     "holes": [[[x, y], ...]]}    # every hole's outline: a ring is not a disc

`centre` is a centroid, and a centroid is not a point in the region: on any
crescent, ring or bent form it lands in a neighbour. Probing there returns the
NEIGHBOUR's colour, which looks exactly like proof that the region is an
anti-aliasing artefact -- and culling on that basis throws away real flats and
flattens the form they were shading. Probe `inside`, or compare `median`
against the palette entry, which needs no probe at all: an artefact's median
sits between two palette colours, a real flat's sits on one.

This is the measuring instrument for stages 2, 3 and 6. It cannot supply a form
the subject does not have, which is the test a tool here must pass. What it does
not do is decide anything: which regions matter, which edges are stated and
which are lost, what is left out, and what weight a line takes are still the
drawing -- and it writes no mark: its points are read, and the ones that carry
a form are typed into the script. Regions come out largest first.

What it drops is a decision too. A region under --min-area is gone, and so is
every dark form narrower than --line, which is handed to its neighbours as line:
a spray of droplets or a thin tail vanishes here, silently. Compare the census
against the regions before trusting the count. --ink takes every palette name
that is line, not only the darkest: a near-black a few levels off the ink
classifies as its own flat and the line network comes back as one huge region.
A small ink-coloured region where three lines meet is a junction, where the
lines are wider than --line, not a flat. On an upscaled subject, --fringe 60
hands the ramp beside every line to the line; without it the ramp comes back as
a ring region round every outlined form.

--offset X,Y shifts every coordinate by a crop's corner, so an object measured in
its own crop (crop.py prints the offset) comes back in panel coordinates.

--space W,H rescales the output into another coordinate space. Scaling a small
trace UP puts every boundary on a lattice the size of the factor: measure at the
resolution you draw at instead, and use this only to scale down.
"""
import argparse
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def classify(image, palette):
    names = list(palette)
    colours = np.array([[int(palette[name][at:at + 2], 16) for at in (1, 3, 5)]
                        for name in names], dtype=float)
    pixels = np.asarray(image, dtype=float).reshape(-1, 3)
    labels = np.argmin(((pixels[:, None, :] - colours[None]) ** 2).sum(-1), axis=1)
    return names, labels.reshape(image.height, image.width)


def separate(labels, ink, line):
    """Split the classified subject into regions, and give every LINE pixel to
    the region nearest it.

    The ink colour is also a flat wherever it is wider than a line -- a tyre, a
    pair of shorts, a shoe -- so only what a disc of the line's width can pass
    through is line. Anything thicker keeps its own region at full extent.

    Regions are cut BEFORE the line is handed out, so two flats of one colour
    that only a line separates -- an eye white and the sky beside it -- stay two
    regions. Handed out first, the line joins them and the eye is the sky.
    Returns (region id per pixel, colour index per region id)."""
    line_mask = np.zeros(labels.shape, bool)
    mask = np.isin(labels, ink)
    if mask.any():
        radius = max(1, int(round(line / 2)))
        span = np.arange(-radius, radius + 1)
        disc = (span[:, None] ** 2 + span[None, :] ** 2) <= radius ** 2
        line_mask = mask & ~ndimage.binary_opening(mask, structure=disc)
    ids = np.zeros(labels.shape, np.int32)
    colour_of = [-1]
    for index in np.unique(labels[~line_mask]):
        parts, count = ndimage.label((labels == index) & ~line_mask, structure=np.ones((3, 3)))
        ids[parts > 0] = parts[parts > 0] + len(colour_of) - 1
        colour_of += [int(index)] * count
    if line_mask.any():
        _, (rows, cols) = ndimage.distance_transform_edt(line_mask, return_indices=True)
        ids = ids[rows, cols]
    return ids, colour_of


def outline(contour, tolerance, dx, dy):
    simplified = cv2.approxPolyDP(contour, tolerance, True)
    return [[int(x) + dx, int(y) + dy] for [[x, y]] in simplified]


def trace(image, palette, ink, line, min_area, fringe=0.0):
    image_rgb = np.asarray(image.convert("RGB"))
    names, labels = classify(image, palette)
    ink_ids = [names.index(name) for name in ink if name in names]
    if fringe and ink_ids:
        # the ramp between a line and the flat beside it is a mid-tone, and its
        # nearest palette entry is some third colour: left alone it comes back as
        # a ring region round every outlined form. Steep pixels are ramp.
        grey = np.asarray(image.convert("L"), dtype=float)
        steep = np.hypot(ndimage.sobel(grey, 0), ndimage.sobel(grey, 1)) > fringe
        labels = np.where(steep, ink_ids[0], labels)
    ids, colour_of = separate(labels, ink_ids, line)
    regions = []
    for number, where in enumerate(ndimage.find_objects(ids), 1):
        if where is None:
            continue
        mask = ids[where] == number
        area = int(mask.sum())
        if area < min_area:
            continue
        top, left = where[0].start, where[1].start
        padded = np.pad(mask, 1).astype(np.uint8)
        found, tree = cv2.findContours(padded, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        outer = max((k for k in range(len(found)) if tree[0][k][3] < 0), key=lambda k: len(found[k]))
        holes = [found[k] for k in range(len(found))
                 if tree[0][k][3] == outer and cv2.contourArea(found[k]) >= min_area]
        ys, xs = np.nonzero(mask)
        # `centre` is a centroid and a centroid is NOT a point in the region:
        # any crescent, ring or bent form puts it in a neighbour. Probing
        # there reports the neighbour's colour and reads as proof that the
        # region is an anti-aliasing artefact, so real flats get culled.
        # `inside` is the deepest point of the region itself; probe that.
        deep = cv2.distanceTransform(padded, cv2.DIST_L2, 3)
        iy, ix = np.unravel_index(int(deep.argmax()), deep.shape)
        median = np.median(image_rgb[where][mask], axis=0)
        dx, dy = left - 1, top - 1
        regions.append({
            "colour": names[colour_of[number]], "area": area,
            "box": [int(xs.min()) + left, int(ys.min()) + top,
                    int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)],
            "centre": [round(float(xs.mean()) + left, 1), round(float(ys.mean()) + top, 1)],
            "inside": [int(ix) + dx, int(iy) + dy],
            "median": "#%02x%02x%02x" % tuple(int(v) for v in median),
            "blockin": outline(found[outer], 6.0, dx, dy),
            "contour": outline(found[outer], 1.5, dx, dy),
            "holes": [outline(hole, 1.5, dx, dy) for hole in holes],
        })
    regions.sort(key=lambda region: -region["area"])
    for number, region in enumerate(regions):
        region["id"] = number
    return regions


def move(regions, sx=1.0, sy=1.0, dx=0.0, dy=0.0):
    """Every coordinate scaled by (sx, sy), then shifted by (dx, dy)."""
    def point(p):
        return [round(p[0] * sx + dx, 1), round(p[1] * sy + dy, 1)]
    for region in regions:
        x, y, w, h = region["box"]
        region["box"] = point((x, y)) + [round(w * sx, 1), round(h * sy, 1)]
        for key in ("centre", "inside"):
            region[key] = point(region[key])
        for key in ("blockin", "contour"):
            region[key] = [point(p) for p in region[key]]
        region["holes"] = [[point(p) for p in hole] for hole in region.get("holes", [])]
    return regions


def sheet(image, regions):
    """Every block-in polygon over the subject, numbered, so the trace can be
    looked at before it is trusted."""
    out = image.copy()
    pen = ImageDraw.Draw(out)
    for region in regions:
        points = [tuple(p) for p in region["blockin"]]
        if len(points) > 1:
            pen.line(points + [points[0]], fill=(220, 30, 30), width=1)
        pen.text((region["centre"][0] - 4, region["centre"][1] - 6),
                 str(region["id"]), fill=(20, 60, 220))
    return out


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("subject")
    parse.add_argument("palette")
    parse.add_argument("--out", default="regions.json")
    parse.add_argument("--png", default="")
    parse.add_argument("--ink", default="black", help="comma-separated palette names that are line, not flat")
    parse.add_argument("--line", type=float, default=8.0,
                       help="widest run of the ink colour that is still a line, in px; "
                            "measure it (p90 of true line runs). Thicker ink is a flat")
    parse.add_argument("--min-area", type=int, default=150)
    parse.add_argument("--fringe", type=float, default=0.0,
                       help="Sobel magnitude above which a pixel is the ramp beside a line "
                            "and goes to the line; 60 on an upscaled subject. 0 is off")
    parse.add_argument("--space", default="", help="W,H to report coordinates in")
    parse.add_argument("--offset", default="",
                       help="X,Y added to every coordinate: a crop's corner in the panel, "
                            "as crop.py prints it")
    args = parse.parse_args()

    image = Image.open(args.subject).convert("RGB")
    with open(args.palette) as handle:
        palette = json.load(handle)
    regions = trace(image, palette, args.ink.split(","), args.line, args.min_area, args.fringe)
    if args.png:
        sheet(image, regions).save(args.png)
    if args.space:
        width, height = (float(part) for part in args.space.split(","))
        regions = move(regions, sx=width / image.width, sy=height / image.height)
    if args.offset:
        dx, dy = (float(part) for part in args.offset.split(","))
        regions = move(regions, dx=dx, dy=dy)
    with open(args.out, "w") as handle:
        json.dump(regions, handle)

    by_colour = {}
    for region in regions:
        by_colour.setdefault(region["colour"], []).append(region["area"])
    print(f"{len(regions)} regions -> {args.out}" + (f", sheet -> {args.png}" if args.png else ""))
    for name, areas in sorted(by_colour.items(), key=lambda item: -sum(item[1])):
        print(f"  {name:12s} {len(areas):3d} regions  {sum(areas):8d}px  largest {max(areas)}")
    print("\nlargest first:")
    for region in regions[:24]:
        print(f"  #{region['id']:<3d} {region['colour']:12s} {region['area']:7d}px  box {region['box']}"
              f"  {len(region['blockin']):2d} straights / {len(region['contour']):3d} contour points"
              + (f"  {len(region['holes'])} holes" if region["holes"] else ""))
    print("\na region is a flat, not an object: one object is several regions and one\n"
          "region can span two objects of the same colour. Naming them is the reading.")


if __name__ == "__main__":
    main()
