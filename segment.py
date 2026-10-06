#!/usr/bin/env python3
"""Measure a photograph's or a painting's regions: tens of value and colour
regions that follow its forms, where trace.py returns hundreds of specks.

    python3 segment.py subject.png [--regions N] [--box x,y,w,h] [--detail D]
                       [--palette palette.json] [--out regions.json] [--png regions.png]
                       [--offset X,Y | --local]
    python3 segment.py subject.png --silhouette x,y --box x,y,w,h
                       [--out silhouette.json] [--png silhouette.png]

trace.py classifies every pixel to its nearest palette entry. That suits a
flat-cel or printed subject, made of flats and ink. A photograph or a painted
subject has neither: a surface is a gradient, fur and grass break into
fragments at every threshold, and the trace comes back as hundreds of small
regions of noise, even with --smooth.

This tool groups pixels by their neighbours instead of by a fixed palette:

1. Edge-preserving smoothing (mean shift) washes out grain, fur and brush
   texture finer than --detail and keeps the steps between forms.
2. The smoothed colours are clustered in Lab, and each cluster is cut into
   connected pieces. Pieces under about --detail squared go to their
   neighbours.
3. The two adjacent regions that are most alike merge, again and again, until
   about --regions remain. Likeness is the colour difference in Lab, weighted
   by size (a small region goes before a large one), lowered for a strip much
   longer than it is wide (a grass blade, a hair), and raised where the two
   share a strong edge in the subject.

`--detail D` is the smallest form you want kept, in px. Its default is a
hundredth of the shorter side of the area measured, so `--box` gives the same
number of regions at a finer scale: measure a part on its own box, as for
trace.py. Large images are segmented on a copy at most 900px on a side and the
boundaries are then refined at full size, so they do not sit on a lattice.

The output is trace.py's: one entry per region, largest first, with `box`,
`centre` (a centroid, which can fall outside the region), `inside` (its
deepest point: probe here), `median`, `blockin`, `contour` (perimeter order)
and `holes`, plus `colour`, the nearest palette name, when --palette is given.
`check.py --faces ops.json --regions regions.json` reads it unchanged.

`--png` writes the subject with every boundary drawn and each region's
number at its `inside` point, beside a map of the regions in their median
colours. Look at it and name the regions before relying on any of them.

--silhouette x,y grows the object under that point, bounded by --box. The
object's colours are learnt from around the seed and the ground's from a ring
just outside the box, and every pixel in the box goes to whichever it fits
better, with the cut drawn along steps in colour and value (GrabCut). The box
is required. A region-growing measure needs a bound that is not a colour, or
it runs into every other object of the same colours. Where the box cuts
through the object, the ring there has the seed's colour and is read as the
object running on, so the outline stops at the box, and the tool names the
sides where that happened. The outline is printed as numbered points where it
turns, and written to --out as one region entry. A pale head on pale straw,
or a dark leg in shadowed grass, has no step to stop at, and a flat inside
the object much darker than the seed (a nose, a collar) can be cut out of it:
look at --png and check the outline against the subject. Where nothing
separates object from ground, the edge is your decision.

Coordinates are the input's pixels. A crop cut by crop.py carries its own
corner, and the regions come back in picture coordinates with no flag, as
with trace.py; --offset is for a crop made any other way, and --local keeps
a crop's own coordinates. --box is in the input's own pixels (the crop's,
for a crop).

This is a measuring instrument. It writes no mark, and nothing it prints is a
stroke. Which regions make up an object, which edges are stated and which are
lost, and what is left out are yours to decide. You read its points and type
the ones that carry a form into draw.py.
"""
import argparse
import heapq
import json
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from pen import read_palette
from trace import corner, move, region_entry

WORKING_SIDE = 900
CLUSTERS = 24
# Lab distance from the seed's colour under which a pixel of the ring round a
# --silhouette box counts as probably the object
RING_LIKENESS = 12.0


def lab_of(rgb):
    """Lab, L in 0..100, a and b about -100..100, as float32."""
    return cv2.cvtColor(np.ascontiguousarray(rgb).astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)


def smoothed(rgb, detail):
    """Mean shift over a window `detail` px wide: grain finer than that goes,
    steps between forms stay. Same size as the input."""
    spatial = max(2, int(round(detail)))
    out = cv2.pyrMeanShiftFiltering(np.ascontiguousarray(rgb), spatial, 18, maxLevel=1)
    return cv2.medianBlur(out, 3)


def gradient(lab):
    """Colour edge strength per pixel: the Sobel magnitude summed over L, a, b."""
    total = np.zeros(lab.shape[:2], np.float32)
    for channel in range(3):
        plane = np.ascontiguousarray(lab[..., channel])
        total += np.hypot(cv2.Sobel(plane, cv2.CV_32F, 1, 0, ksize=3),
                          cv2.Sobel(plane, cv2.CV_32F, 0, 1, ksize=3))
    return total / 8.0


def absorb(ids, keep):
    """Every pixel whose label is not in `keep` goes to the nearest kept one."""
    gone = ~keep[ids]
    if gone.any():
        _, (rows, cols) = ndimage.distance_transform_edt(gone, return_indices=True)
        ids = ids[rows, cols]
    return ids


def relabel(ids):
    """Labels made 0..n-1, every one a single 4-connected piece."""
    out = np.zeros(ids.shape, np.int32)
    count = 0
    for value in np.unique(ids):
        parts, found = ndimage.label(ids == value)
        out[parts > 0] = parts[parts > 0] + count - 1
        count += found
    return out, count


def oversegment(lab, min_area):
    """Lab k-means, cut into connected pieces, pieces under `min_area` given
    to their nearest neighbour."""
    pixels = lab.reshape(-1, 3)
    sample = pixels[np.random.default_rng(0).choice(len(pixels), min(len(pixels), 60000), replace=False)]
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    cv2.setRNGSeed(0)
    _, _, centres = cv2.kmeans(sample, CLUSTERS, None, criteria, 2, cv2.KMEANS_PP_CENTERS)
    far = (centres ** 2).sum(-1)[None] - 2 * pixels @ centres.T
    clusters = np.argmin(far, axis=1).reshape(lab.shape[:2])
    ids, count = relabel(clusters)
    for _ in range(3):
        sizes = np.bincount(ids.ravel(), minlength=count)
        keep = sizes >= min_area
        if keep.all():
            break
        if not keep.any():
            keep[np.argmax(sizes)] = True
        ids, count = relabel(absorb(ids, keep))
    return ids, count


def pairs(ids, edge):
    """For every pair of 4-adjacent labels: the boundary length and the summed
    edge strength along it."""
    first = np.concatenate([ids[:, :-1].ravel(), ids[:-1, :].ravel()])
    second = np.concatenate([ids[:, 1:].ravel(), ids[1:, :].ravel()])
    strength = np.concatenate([np.maximum(edge[:, :-1], edge[:, 1:]).ravel(),
                               np.maximum(edge[:-1, :], edge[1:, :]).ravel()])
    cross = first != second
    low = np.minimum(first, second)[cross].astype(np.int64)
    high = np.maximum(first, second)[cross].astype(np.int64)
    key = low * (int(ids.max()) + 1) + high
    unique, inverse, length = np.unique(key, return_inverse=True, return_counts=True)
    total = np.bincount(inverse, weights=strength[cross])
    span = int(ids.max()) + 1
    return [(int(k // span), int(k % span), int(n), float(s))
            for k, n, s in zip(unique, length, total)]


class Regions:
    """Region statistics under merging: size, summed Lab, perimeter, and per
    neighbour the shared boundary length and summed edge strength."""

    def __init__(self, ids, lab, edge):
        count = int(ids.max()) + 1
        flat = ids.ravel()
        self.size = np.bincount(flat, minlength=count).astype(float)
        self.total = np.stack([np.bincount(flat, weights=lab[..., c].ravel(), minlength=count)
                               for c in range(3)], axis=1)
        self.near = [dict() for _ in range(count)]
        self.perimeter = np.zeros(count)
        for a, b, length, strength in pairs(ids, edge):
            self.near[a][b] = [length, strength]
            self.near[b][a] = [length, strength]
            self.perimeter[a] += length
            self.perimeter[b] += length
        self.alive = np.ones(count, bool)
        self.version = np.zeros(count, np.int64)
        self.parent = np.arange(count)

    def mean(self, a):
        return self.total[a] / self.size[a]

    def cost(self, a, b):
        length, strength = self.near[a][b]
        difference = float(((self.mean(a) - self.mean(b)) ** 2).sum())
        ward = self.size[a] * self.size[b] / (self.size[a] + self.size[b])
        # a strip much longer than it is wide (a blade, a hair, a seam of
        # anti-aliasing) is texture before it is a form
        thin = min(self.perimeter[a] ** 2 / (12.6 * self.size[a]),
                   self.perimeter[b] ** 2 / (12.6 * self.size[b]))
        # the subject's own edge strength along the shared boundary: a seam
        # inside a sky's gradient goes early, a timber against a white panel
        # late. Weaker than this and the panels merged into the timbers;
        # stronger and the roof, timbers and windows became one dark region
        contrast = strength / length
        return ward * (difference + 4.0) * (contrast + 0.5) / 6.0 / max(1.0, thin) ** 0.5

    def merge(self, a, b):
        """b into a."""
        self.size[a] += self.size[b]
        self.total[a] += self.total[b]
        shared = self.near[a].pop(b)
        self.near[b].pop(a)
        self.perimeter[a] += self.perimeter[b] - 2 * shared[0]
        for c, (length, strength) in self.near[b].items():
            self.near[c].pop(b)
            have = self.near[a].setdefault(c, [0, 0.0])
            have[0] += length
            have[1] += strength
            self.near[c][a] = have
        self.near[b] = {}
        self.alive[b] = False
        self.parent[b] = a
        self.version[a] += 1

    def root(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a


def merge_down(ids, lab, edge, target):
    """Merge the most alike adjacent pair until `target` regions remain."""
    state = Regions(ids, lab, edge)
    heap = []

    def push(a):
        for b in state.near[a]:
            heapq.heappush(heap, (state.cost(a, b), a, b, state.version[a], state.version[b]))

    for a in range(len(state.size)):
        push(a)
    left = int(state.alive.sum())
    while left > target and heap:
        _, a, b, va, vb = heapq.heappop(heap)
        if not (state.alive[a] and state.alive[b]) or state.version[a] != va or state.version[b] != vb:
            continue
        if state.size[b] > state.size[a]:
            a, b = b, a
        state.merge(a, b)
        left -= 1
        push(a)
        for c in state.near[a]:
            state.version[c] += 1
            push(c)
    lookup = np.array([state.root(a) for a in range(len(state.size))])
    return lookup[ids]


def refine(ids_small, rgb, lab_full, rounds=2):
    """Labels from a reduced copy, brought to full size: nearest-neighbour
    upscaling puts every boundary on the reduction's lattice, so each pixel
    near a boundary goes to whichever adjacent region its own colour is
    nearest."""
    height, width = rgb.shape[:2]
    ids = cv2.resize(ids_small.astype(np.int32), (width, height), interpolation=cv2.INTER_NEAREST)
    reach = max(1, int(math.ceil(max(height / ids_small.shape[0], width / ids_small.shape[1]))))
    soft = cv2.GaussianBlur(lab_full, (0, 0), max(0.8, reach / 3))
    for _ in range(rounds):
        count = int(ids.max()) + 1
        size = np.maximum(np.bincount(ids.ravel(), minlength=count), 1)
        means = np.stack([np.bincount(ids.ravel(), weights=soft[..., c].ravel(), minlength=count)
                          for c in range(3)], axis=1) / size[:, None]
        border = cv2.morphologyEx(ids.astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3))) > 0
        band = cv2.dilate(border.astype(np.uint8), np.ones((2 * reach + 1,) * 2)) > 0
        rows, cols = np.nonzero(band)
        best = ids[rows, cols].copy()
        best_far = ((soft[rows, cols] - means[best]) ** 2).sum(-1)
        step = max(1, reach // 2)
        for dy in range(-reach, reach + 1, step):
            for dx in range(-reach, reach + 1, step):
                other = ids[np.clip(rows + dy, 0, height - 1), np.clip(cols + dx, 0, width - 1)]
                far = ((soft[rows, cols] - means[other]) ** 2).sum(-1)
                better = far < best_far
                best[better], best_far[better] = other[better], far[better]
        ids[rows, cols] = best
    return ids


def segment(rgb, target, detail):
    """A label map of about `target` regions over `rgb`, at full size."""
    height, width = rgb.shape[:2]
    scale = min(1.0, WORKING_SIDE / max(height, width))
    small = rgb if scale == 1.0 else cv2.resize(rgb, (max(1, round(width * scale)), max(1, round(height * scale))),
                                                interpolation=cv2.INTER_AREA)
    grain = max(1.5, detail * scale)
    flat = smoothed(small, grain)
    lab = lab_of(flat)
    ids, _ = oversegment(lab, max(4, int(grain ** 2)))
    ids = merge_down(ids, lab, gradient(lab_of(cv2.GaussianBlur(small, (0, 0), 1.0))), target)
    ids, _ = relabel(ids)
    if scale < 1.0:
        ids = refine(ids, rgb, lab_of(rgb))
    return whole(ids)


def whole(ids):
    """Each region as one piece: a region that refining or absorbing left in
    several keeps its largest, and the other pieces go to their neighbours."""
    pieces, count = relabel(ids)
    owner = np.zeros(count, np.int64)
    owner[pieces.ravel()] = ids.ravel()
    sizes = np.bincount(pieces.ravel(), minlength=count)
    largest = np.zeros(int(ids.max()) + 1, np.int64)
    np.maximum.at(largest, owner, sizes)
    keep = sizes == largest[owner]
    _, first = np.unique(owner[keep], return_index=True)
    chosen = np.zeros(count, bool)
    chosen[np.flatnonzero(keep)[first]] = True
    ids, _ = relabel(absorb(pieces, chosen))
    return ids


def entries(ids, rgb, min_area):
    """Every region of the label map as a trace.py entry, largest first."""
    out = []
    for number, where in enumerate(ndimage.find_objects(ids + 1), 1):
        entry = region_entry(ids + 1, number, where, rgb, min_area)
        if entry:
            out.append(entry)
    out.sort(key=lambda region: -region["area"])
    for number, region in enumerate(out):
        region["id"] = number
    return out


def name_colours(regions, palette):
    """Each region's nearest palette name, by Lab distance from its median."""
    names = [name for name in palette if name != "background"] or list(palette)
    swatch = np.array([[[int(palette[name][at:at + 2], 16) for at in (1, 3, 5)] for name in names]], np.uint8)
    targets = lab_of(swatch)[0]
    for region in regions:
        median = np.array([[[int(region["median"][at:at + 2], 16) for at in (1, 3, 5)]]], np.uint8)
        far = ((lab_of(median)[0, 0] - targets) ** 2).sum(-1)
        region["colour"] = names[int(np.argmin(far))]
    return regions


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def label(pen, at, text, size):
    x, y = at
    box = pen.textbbox((x, y), text, font=font(size), anchor="mm")
    pen.rectangle([box[0] - 2, box[1] - 1, box[2] + 2, box[3] + 1], fill=(255, 255, 255))
    pen.text((x, y), text, fill=(10, 40, 200), font=font(size), anchor="mm")


def sheet(rgb, ids, regions, origin=(0, 0)):
    """The subject with every boundary in red and each region's number at its
    `inside` point, beside the regions filled with their median colours."""
    height, width = rgb.shape[:2]
    border = cv2.morphologyEx(ids.astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3))) > 0
    lines = rgb.copy()
    lines[border] = (230, 20, 20)
    fills = np.zeros_like(rgb)
    for region in regions:
        x, y = region["inside"]
        number = ids[int(y) - origin[1], int(x) - origin[0]]
        fills[ids == number] = [int(region["median"][at:at + 2], 16) for at in (1, 3, 5)]
    fills[border] = (40, 40, 40)
    out = Image.new("RGB", (width * 2 + 12, height), (255, 255, 255))
    out.paste(Image.fromarray(lines), (0, 0))
    out.paste(Image.fromarray(fills), (width + 12, 0))
    pen = ImageDraw.Draw(out)
    size = max(11, min(28, round(min(width, height) / 45)))
    for region in regions:
        x, y = region["inside"][0] - origin[0], region["inside"][1] - origin[1]
        for shift in (0, width + 12):
            label(pen, (x + shift, y), str(region["id"]), size)
    return out


def grow(rgb, seed, box, detail):
    """The object under `seed`, bounded by `box` (x, y, w, h in rgb's
    pixels), as a mask over the whole of rgb.

    The object's colours and the ground's are each modelled as a mixture of a
    few colours (GrabCut): the ground's from a ring just outside the box (or,
    where the box meets the image's edge, a thin band inside it), the
    object's from the seed, each relearned from the cut and the cut made
    again, five times over. Every pixel in the box then goes to whichever
    model it fits, with a cost for cutting between two alike neighbours, so
    the cut follows the steps in colour and value. Nothing outside the box
    can be the object."""
    height, width = rgb.shape[:2]
    x, y, w, h = box
    margin = max(8, round(0.1 * max(w, h)))
    x0, y0 = max(0, x - margin), max(0, y - margin)
    x1, y1 = min(width, x + w + margin), min(height, y + h + margin)
    crop = np.ascontiguousarray(rgb[y0:y1, x0:x1])
    scale = min(1.0, 640 / max(crop.shape[:2]))
    size = (max(1, round(crop.shape[1] * scale)), max(1, round(crop.shape[0] * scale)))
    small = crop if scale == 1.0 else cv2.resize(crop, size, interpolation=cv2.INTER_AREA)
    at = lambda value: int(round(value * scale))
    left, top, right, bottom = at(x - x0), at(y - y0), at(x + w - x0), at(y + h - y0)
    # the ring outside the box is certain ground. Made only probable, the
    # object ran out through it into a ground of nearby colours (a dog into
    # the grass beside it), and the box clipped it there
    mask = np.full(small.shape[:2], cv2.GC_BGD, np.uint8)
    mask[top:bottom, left:right] = cv2.GC_PR_FGD
    band = max(2, round(0.02 * min(right - left, bottom - top)))
    if x == x0:
        mask[top:bottom, left:left + band] = cv2.GC_PR_BGD
    if y == y0:
        mask[top:top + band, left:right] = cv2.GC_PR_BGD
    if x + w == x1:
        mask[top:bottom, right - band:right] = cv2.GC_PR_BGD
    if y + h == y1:
        mask[bottom - band:bottom, left:right] = cv2.GC_PR_BGD
    centre = (at(seed[0] - x0), at(seed[1] - y0))
    radius = max(2, round(0.03 * min(right - left, bottom - top)))
    # where the box cuts through the object, the ring is the object's own
    # colour running on past the box. Taken as ground there, it taught the
    # cut that the object is ground, and the cut kept nothing but the seed.
    # So a ring pixel of the seed's colour counts as probably object; the
    # box clips it afterwards
    lab = lab_of(cv2.GaussianBlur(small, (0, 0), 1.5))
    disc = np.zeros(small.shape[:2], np.uint8)
    cv2.circle(disc, centre, radius, 1, -1)
    own = np.median(lab[disc > 0], axis=0)
    alike = np.sqrt(((lab - own) ** 2).sum(-1)) < RING_LIKENESS
    mask[(mask == cv2.GC_BGD) & alike] = cv2.GC_PR_FGD
    cv2.circle(mask, centre, radius, cv2.GC_FGD, -1)
    ground, thing = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), mask, None, ground, thing, 5, cv2.GC_INIT_WITH_MASK)
    found = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.int32)
    if scale < 1.0:
        found = refine(found, crop, lab_of(crop))
    inside = np.zeros(found.shape, bool)
    inside[y - y0:y + h - y0, x - x0:x + w - x0] = True
    found = (found > 0) & inside
    reach = max(1, int(round(detail / 2)))
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * reach + 1, 2 * reach + 1))
    found = cv2.morphologyEx(cv2.morphologyEx(found.astype(np.uint8), cv2.MORPH_OPEN, disc),
                             cv2.MORPH_CLOSE, disc) > 0
    found &= inside
    parts, _ = ndimage.label(found)
    piece = parts[seed[1] - y0, seed[0] - x0]
    if piece == 0:
        raise SystemExit(f"--silhouette {seed[0]},{seed[1]}: the point fell on the ground side of the cut. "
                         f"Move it into the object's own colour, away from its edge")
    seed_disc = math.pi * (radius / scale) ** 2
    if (parts == piece).sum() <= 2 * seed_disc:
        raise SystemExit(f"--silhouette {seed[0]},{seed[1]}: the cut kept little more than the seed, so "
                         f"nothing around it in the box matches its colour. Move the seed off the "
                         f"highlight or edge it is on, into the middle of the object's own colour")
    whole_mask = np.zeros((height, width), bool)
    whole_mask[y0:y1, x0:x1] = parts == piece
    return whole_mask


def parse_box(text, width, height):
    x, y, w, h = (int(round(float(part))) for part in text.split(","))
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > width or y + h > height:
        raise SystemExit(f"--box {text} is not inside the {width}x{height} image (x,y,w,h in its pixels)")
    return x, y, w, h


def main():
    parse = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parse.add_argument("subject")
    parse.add_argument("--regions", type=int, default=40, help="about how many regions to keep")
    parse.add_argument("--box", default="", help="x,y,w,h: measure only this part, in the input's pixels")
    parse.add_argument("--detail", type=float, default=0.0,
                       help="smallest form kept, in px (default a hundredth of the shorter side "
                            "of the image or box)")
    parse.add_argument("--palette", default="", help="palette.json: name each region's nearest entry")
    parse.add_argument("--silhouette", default="",
                       help="x,y: grow the object under this point, bounded by --box, and print its outline")
    parse.add_argument("--out", default="")
    parse.add_argument("--png", default="")
    parse.add_argument("--offset", default="",
                       help="X,Y added to every coordinate, for a crop not cut by crop.py "
                            "(a crop.py crop carries its own)")
    parse.add_argument("--local", action="store_true", help="keep a crop.py crop in its own coordinates")
    args = parse.parse_args()

    opened = Image.open(args.subject)
    stored = (opened.info or {}).get("offset")
    rgb = np.asarray(opened.convert("RGB"))
    height, width = rgb.shape[:2]
    offset = corner(stored, args.offset, args.local, args.subject)
    dx, dy = (float(part) for part in offset.split(",")) if offset else (0.0, 0.0)
    box = parse_box(args.box, width, height) if args.box else (0, 0, width, height)
    detail = args.detail or max(2.0, min(box[2], box[3]) / 100.0)
    if args.regions < 1:
        raise SystemExit(f"--regions takes a count, 1 or more, not {args.regions}")

    if args.silhouette:
        if not args.box:
            raise SystemExit("--silhouette needs --box: a region grown by colour alone runs into "
                             "every other object of the same colours. Pass the part's box from "
                             "parts.json (in this image's pixels)")
        sx, sy = (int(round(float(part))) for part in args.silhouette.split(","))
        if not (box[0] <= sx < box[0] + box[2] and box[1] <= sy < box[1] + box[3]):
            raise SystemExit(f"--silhouette {args.silhouette} is outside --box {args.box}")
        ids = grow(rgb, (sx, sy), box, detail).astype(np.int32)
        found = region_entry(ids, 1, ndimage.find_objects(ids)[0], rgb, int(detail ** 2))
        found["id"] = 0
        regions = move([found], dx=dx, dy=dy) if offset else [found]
        region = regions[0]
        out = args.out or "silhouette.json"
        with open(out, "w") as handle:
            json.dump(regions, handle)
        if args.png:
            view = rgb.copy()
            border = cv2.morphologyEx(ids.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3))) > 0
            view[border] = (230, 20, 20)
            image = Image.fromarray(view)
            pen = ImageDraw.Draw(image)
            pen.rectangle([box[0], box[1], box[0] + box[2] - 1, box[1] + box[3] - 1], outline=(20, 60, 220))
            image.save(args.png)
        touching = [side for side, hit in (
            ("left", region["box"][0] - dx <= box[0]), ("top", region["box"][1] - dy <= box[1]),
            ("right", region["box"][0] - dx + region["box"][2] >= box[0] + box[2]),
            ("bottom", region["box"][1] - dy + region["box"][3] >= box[1] + box[3])) if hit]
        print(f"silhouette under {args.silhouette}: {region['area']}px, box {region['box']}, "
              f"inside {region['inside']}, median {region['median']} -> {out}"
              + (f", sheet -> {args.png}" if args.png else ""))
        if touching:
            print(f"  it reaches the box's {', '.join(touching)} edge: there the box, not the "
                  f"subject, stopped it. Check those sides on the sheet")
        print(f"\nwhere the outline turns ({len(region['blockin'])} of {len(region['contour'])} "
              f"contour points, in perimeter order; the full contour is in {out}):")
        for number, (px, py) in enumerate(region["blockin"], 1):
            print(f"  {number:3d}  x {px:g}  y {py:g}")
        print("\nthese are measurements to read, not a mark list. Type the points where the\n"
              "silhouette turns into draw.py yourself, with more between them where a run\n"
              "would be left straight, and decide every edge this outline does not find.")
        return

    crop = np.ascontiguousarray(rgb[box[1]:box[1] + box[3], box[0]:box[0] + box[2]])
    ids = segment(crop, args.regions, detail)
    regions = entries(ids, crop, 1)
    regions = move(regions, dx=box[0], dy=box[1])
    if args.palette:
        name_colours(regions, read_palette(args.palette))
    if args.png:
        sheet(crop, ids, regions, origin=(box[0], box[1])).save(args.png)
    if offset:
        regions = move(regions, dx=dx, dy=dy)
    out = args.out or "regions.json"
    with open(out, "w") as handle:
        json.dump(regions, handle)
    print(f"{len(regions)} regions -> {out}" + (f", sheet -> {args.png}" if args.png else "")
          + f"  (detail {detail:g}px over a {box[2]}x{box[3]} area)")
    print("\nlargest first:")
    for region in regions:
        print(f"  #{region['id']:<3d} {region.get('colour', ''):12s} {region['median']}  {region['area']:7d}px  "
              f"box {region['box']}  inside {region['inside']}  {len(region['contour']):3d} contour points"
              + (f"  {len(region['holes'])} holes" if region["holes"] else ""))
    print("\na region is a patch of like colour, not an object: one object is several\n"
          "regions, and one region can run from an object into its ground where nothing\n"
          "separates them. Naming the regions and deciding which edges to state is your job.")


if __name__ == "__main__":
    main()
