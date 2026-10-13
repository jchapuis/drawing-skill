#!/usr/bin/env python3
"""Read coordinates off a picture: a gridded magnified crop to place points,
and pixel probes to confirm them. It measures and never writes a mark.

    python3 look.py grid subject.png 600,400,300,200 --out look.png
    python3 look.py probe subject.png drawing.png --at 640,1850 700,1900
    python3 look.py edge subject.png --ray 640,1850,1,0 --ray 640,1850,0,-1
    python3 look.py axis --seg shoulders:640,2080,1700,2090/520,2140,1800,2040 \
                         --seg eyes:800,980,1190,980/790,940,1210,955 --pair shoulders,eyes

`grid` crops a box, magnifies it and rules it with lines labelled in the
picture's coordinates, every line labelled, every fifth one stronger. Read a
point's position off it to type into draw.py. A position read by eye off a
grid is a placement, not a measurement: confirm it with `probe` or `edge`
before you judge a fault by it.

`probe` prints, per point, the median colour of a small patch, its hue,
saturation, value and grey, and the nearest palette.json name, in each image
given (the subject, the render).

`edge` walks a ray from a point and prints where the colour first changes
sharply, with the colour and palette name either side, then the next few
edges. It finds the outline of a form from a point inside it.

`axis` measures the angles that carry a pose. You type two points per segment,
read off the subject and then off the render, and it prints each segment's
angle on both, and the angle between named pairs (the shoulder line against
the eye line, the beak against the neck). It reads no pixels: the points are
your reading, the angles are arithmetic. Given images and `--out`, it draws the
segments on them so you can see the points sit where you meant.

Several images (the subject, then a render) are read at the first one's size,
so a render at --scale 0.5 is probed at the subject's coordinates. `--scale F`
multiplies the image's pixels into the coordinates you work in: 4 reads
subject_1x.png in the 4x working space.
"""
import argparse
import colorsys
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import _step  # noqa: E402

Image.MAX_IMAGE_PIXELS = None


def load(paths):
    """The images, each at the first one's size."""
    images = [Image.open(path).convert("RGB") for path in paths]
    return [images[0]] + [image.resize(images[0].size, Image.LANCZOS) for image in images[1:]]


def numbers(text, count, what):
    try:
        values = [float(part) for part in text.split(",")]
    except ValueError:
        sys.exit(f"{what}: {text!r} is not {count} comma-separated numbers")
    if len(values) != count:
        sys.exit(f"{what}: {text!r} is not {count} comma-separated numbers")
    return values


def read_palette(path):
    """{name: (r, g, b)}, `background` included, so a probe on the ground says so."""
    if not path or not os.path.exists(path):
        return {}
    with open(path) as handle:
        raw = json.load(handle)
    return {name: tuple(int(value[at:at + 2], 16) for at in (1, 3, 5))
            for name, value in raw.items() if isinstance(value, str) and value.startswith("#")}


def _lab(rgb):
    """CIELAB, lightness 0-100 and a*b* centred on 0, one row per colour."""
    lab = cv2.cvtColor(np.clip(np.asarray(rgb, dtype=float), 0, 255).astype(np.uint8)
                       .reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(float)
    return lab * np.array([100 / 255, 1, 1]) - np.array([0, 128, 128])


def nearest(rgb, palette):
    """(name, distance in Lab units) of the palette entry nearest `rgb`."""
    if not palette:
        return None, None
    names = list(palette)
    distances = np.linalg.norm(_lab([palette[name] for name in names]) - _lab([rgb])[0], axis=1)
    best = int(np.argmin(distances))
    return names[best], float(distances[best])


def describe(rgb, palette):
    r, g, b = (int(round(c)) for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    name, far = nearest((r, g, b), palette)
    named = f"  ~{name} ({far:.0f})" if name else ""
    return f"#{r:02x}{g:02x}{b:02x} h{h * 360:3.0f} s{s:.2f} v{v:.2f} grey{0.299 * r + 0.587 * g + 0.114 * b:4.0f}{named}"


def patch(pixels, x, y, radius):
    """Median colour of the (2r+1)^2 patch round (x, y), clipped to the image."""
    height, width = pixels.shape[:2]
    x, y = int(round(x)), int(round(y))
    if not (0 <= x < width and 0 <= y < height):
        return None
    block = pixels[max(0, y - radius):y + radius + 1, max(0, x - radius):x + radius + 1]
    return np.median(block.reshape(-1, 3), axis=0)


def probe(images, points, scale, radius, palette, names):
    rows = []
    for x, y in points:
        cells = [patch(pixels, x / scale, y / scale, radius) for pixels in images]
        rows.append(((x, y), cells))
        print(f"({x:g},{y:g})")
        for name, cell in zip(names, cells):
            print(f"    {name:12s} " + ("outside the image" if cell is None else describe(cell, palette)))
    return rows


def edges(pixels, x, y, dx, dy, scale, contrast=18.0, length=None, run=3):
    """The places along a ray where the colour changes sharply: [(t, x, y,
    before, after)], t in working-space pixels from the start.

    The ray is sampled every image pixel. At each step the Lab colour of the
    `run` samples behind is compared with the `run` ahead; a step is an edge
    where that difference is over `contrast` (Lab units, 0-100 lightness) and
    is the largest within `run` either side, so one soft edge is one edge."""
    norm = float(np.hypot(dx, dy))
    if not norm:
        sys.exit("edge: the ray's direction dx,dy is zero")
    dx, dy = dx / norm, dy / norm
    height, width = pixels.shape[:2]
    sx, sy = x / scale, y / scale
    steps = []
    t = 0
    while True:
        px, py = sx + dx * t, sy + dy * t
        if not (0 <= px < width - 0.5 and 0 <= py < height - 0.5):
            break
        if length is not None and t * scale > length:
            break
        steps.append((px, py))
        t += 1
    if len(steps) < 2 * run + 1:
        return []
    track = np.array([pixels[int(round(py)), int(round(px))] for px, py in steps], dtype=float)
    lab = _lab(track)
    diff = np.zeros(len(lab))
    for at in range(run, len(lab) - run + 1):
        diff[at] = np.linalg.norm(lab[at:at + run].mean(0) - lab[at - run:at].mean(0))
    found = []
    for at in range(run, len(lab) - run + 1):
        window = diff[max(0, at - run):at + run + 1]
        if diff[at] > contrast and diff[at] == window.max() and \
                (not found or at - found[-1] > run):
            found.append(at)
    out = []
    for at in found:
        px, py = steps[at]
        out.append((at * scale, px * scale, py * scale,
                    np.median(track[max(0, at - run):at], axis=0),
                    np.median(track[at:at + run], axis=0)))
    return out


def grid(images, box, scale, step, size, names):
    """The box from each image, magnified to about `size` px on its longer
    side, ruled every `step` in working coordinates, side by side."""
    x, y, w, h = box
    step = step or _step(max(w, h), 10)
    zoom = size / max(w, h)
    views = []
    for image, name in zip(images, names):
        crop = image.crop((round(x / scale), round(y / scale),
                           round((x + w) / scale), round((y + h) / scale)))
        crop = crop.resize((max(1, round(w * zoom)), max(1, round(h * zoom))), Image.LANCZOS)
        pen = ImageDraw.Draw(crop, "RGBA")
        for axis in (0, 1):
            origin, span = (x, w) if axis == 0 else (y, h)
            first = -(-origin // step) * step
            for at in range(int(first), int(origin + span) + 1, int(step)):
                where = (at - origin) * zoom
                strong = (at // step) % 5 == 0
                colour = (255, 0, 200, 220) if strong else (0, 200, 255, 160)
                line = [(where, 0), (where, crop.height)] if axis == 0 else [(0, where), (crop.width, where)]
                pen.line(line, fill=colour, width=2 if strong else 1)
                label = str(at)
                spot = (where + 2, 2) if axis == 0 else (2, where + 2)
                box_ = pen.textbbox(spot, label)
                pen.rectangle(box_, fill=(255, 255, 255, 200))
                pen.text(spot, label, fill=(0, 0, 0, 255))
        views.append((crop, name))
    gap, top = 12, 16
    sheet = Image.new("RGB", (sum(p.width for p, _ in views) + gap * (len(views) - 1),
                              views[0][0].height + top), (250, 250, 248))
    pen = ImageDraw.Draw(sheet)
    left = 0
    for crop, name in views:
        sheet.paste(crop, (left, top))
        pen.text((left + 2, 2), f"{name}  every {step:g}px", fill=(25, 25, 25))
        left += crop.width + gap
    return sheet


def angle(x1, y1, x2, y2):
    """Direction from the first point to the second, in degrees counterclockwise
    from rightward as the picture is seen (image y runs down, so up is +),
    in (-180, 180]."""
    if (x1, y1) == (x2, y2):
        return None
    return wrap(np.degrees(np.arctan2(-(y2 - y1), x2 - x1)))


def wrap(degrees):
    """An angle folded into (-180, 180]."""
    folded = (degrees + 180.0) % 360.0 - 180.0
    return 180.0 if folded == -180.0 else float(folded)


def segment(text):
    """NAME:x1,y1,x2,y2[/x1,y1,x2,y2] -> (name, subject points, render points or None)."""
    name, sep, rest = text.partition(":")
    if not sep or not name:
        sys.exit(f"--seg: {text!r} is not NAME:x1,y1,x2,y2 or NAME:x1,y1,x2,y2/x1,y1,x2,y2")
    halves = rest.split("/")
    if len(halves) > 2:
        sys.exit(f"--seg {name}: at most two point sets, subject/render")
    sets = [numbers(half, 4, f"--seg {name}") for half in halves]
    for points in sets:
        if points[:2] == points[2:]:
            sys.exit(f"--seg {name}: its two points are the same point, so it has no direction")
    return name, sets[0], sets[1] if len(sets) == 2 else None


def axes(segments, pairs):
    """{name: (subject angle, render angle or None, subject length, render length or None)}
    and [(a, b, subject a->b, render a->b or None)]: the angle that turns a onto b."""
    table = {}
    for name, subject, render in segments:
        table[name] = (angle(*subject), render and angle(*render),
                       float(np.hypot(subject[2] - subject[0], subject[3] - subject[1])),
                       render and float(np.hypot(render[2] - render[0], render[3] - render[1])))
    between = []
    for a, b in pairs:
        for name in (a, b):
            if name not in table:
                sys.exit(f"--pair {a},{b}: no segment named {name!r}")
        sa, ra = table[a][0], table[a][1]
        sb, rb = table[b][0], table[b][1]
        between.append((a, b, wrap(sb - sa), None if ra is None or rb is None else wrap(rb - ra)))
    return table, between


def show_axes(images, segments, scale):
    """Each image with its segments drawn on it, first point dotted, name beside."""
    views = []
    for index, image in enumerate(images[:2]):
        view = image.copy()
        pen = ImageDraw.Draw(view)
        width = max(2, round(max(view.size) / 400))
        for name, subject, render in segments:
            points = subject if index == 0 else render
            if points is None:
                continue
            x1, y1, x2, y2 = (value / scale for value in points)
            pen.line([(x1, y1), (x2, y2)], fill=(255, 0, 200), width=width)
            pen.ellipse([x1 - 2 * width, y1 - 2 * width, x1 + 2 * width, y1 + 2 * width], fill=(255, 0, 200))
            pen.text((x2 + 2 * width, y2), name, fill=(255, 0, 200))
        views.append(view)
    sheet = Image.new("RGB", (sum(v.width for v in views) + 12 * (len(views) - 1), views[0].height), (250, 250, 248))
    left = 0
    for view in views:
        sheet.paste(view, (left, 0))
        left += view.width + 12
    return sheet


def axis_report(segments, pairs):
    table, between = axes(segments, pairs)
    both = any(render for _, _, render in segments)
    print("angle: direction from the first point to the second, degrees counterclockwise "
          "from rightward (up is +)")
    print(f"{'segment':14s} {'subject':>9s} {'render':>9s} {'render-subject':>15s}   length subject/render")
    for name, (s, r, ls, lr) in table.items():
        rtext = f"{r:+9.1f}" if r is not None else f"{'-':>9s}"
        dtext = f"{wrap(r - s):+15.1f}" if r is not None else f"{'-':>15s}"
        ltext = f"{ls:.0f}" + (f" / {lr:.0f}" if lr is not None else "")
        print(f"{name:14s} {s:+9.1f} {rtext} {dtext}   {ltext}")
    if between:
        print(f"\n{'between':24s} {'subject':>9s} {'render':>9s} {'render-subject':>15s}")
        for a, b, s, r in between:
            rtext = f"{r:+9.1f}" if r is not None else f"{'-':>9s}"
            dtext = f"{wrap(r - s):+15.1f}" if r is not None else f"{'-':>15s}"
            print(f"{a + ' -> ' + b:24s} {s:+9.1f} {rtext} {dtext}")
    if not both:
        print("\nsubject only: give the render's points after a slash, NAME:subject/render")
    return table, between


def main():
    parse = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parse.add_subparsers(dest="mode", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("images", nargs="+", help="the subject first, then any render to read beside it")
    common.add_argument("--scale", type=float, default=1.0,
                        help="working coordinates per image pixel (4: subject_1x.png in the 4x space)")
    common.add_argument("--palette", default="palette.json")
    one = sub.add_parser("grid", parents=[common],
                         help="a magnified crop ruled in picture coordinates, for placing points")
    one.add_argument("--box", required=True, help="x,y,w,h in working coordinates")
    one.add_argument("--step", type=float, default=0, help="grid spacing (default: about 10 lines)")
    one.add_argument("--size", type=int, default=1000, help="longer side of each magnified crop")
    one.add_argument("--out", default="look.png")
    two = sub.add_parser("probe", parents=[common], help="colour and nearest palette name at points")
    two.add_argument("--at", nargs="+", required=True, help="x,y points in working coordinates")
    two.add_argument("--radius", type=int, default=2, help="patch half-size in image pixels")
    three = sub.add_parser("edge", parents=[common], help="the first sharp colour change along a ray")
    three.add_argument("--ray", action="append", required=True,
                       help="x,y,dx,dy: start point and direction; repeat for several rays")
    three.add_argument("--contrast", type=float, default=18.0,
                       help="Lab difference (lightness 0-100) that counts as an edge")
    three.add_argument("--length", type=float, default=None, help="stop after this many working px")
    three.add_argument("--more", type=int, default=3, help="edges listed after the first")
    four = sub.add_parser("axis", help="angles of typed segments on subject and render, and between pairs")
    four.add_argument("images", nargs="*", help="optional: subject, render, to draw the segments on (--out)")
    four.add_argument("--seg", action="append", required=True,
                      help="NAME:x1,y1,x2,y2 on the subject, then /x1,y1,x2,y2 on the render; repeat")
    four.add_argument("--pair", action="append", default=[],
                      help="A,B: the angle that turns segment A onto B; repeat (default: every pair)")
    four.add_argument("--scale", type=float, default=1.0,
                      help="working coordinates per image pixel, for drawing on the images")
    four.add_argument("--out", default=None, help="with images: write them with the segments drawn on")
    args = parse.parse_args()

    if args.mode == "axis":
        segments = [segment(text) for text in args.seg]
        if len({name for name, _, _ in segments}) != len(segments):
            sys.exit("--seg: two segments share a name")
        pairs = [tuple(text.split(",")) for text in args.pair]
        if any(len(pair) != 2 for pair in pairs):
            sys.exit("--pair: write it as A,B, two segment names")
        if not args.pair:
            pairs = [(a[0], b[0]) for i, a in enumerate(segments) for b in segments[i + 1:]]
        axis_report(segments, pairs)
        if args.out:
            if not args.images:
                sys.exit("--out: give the subject (and the render) to draw the segments on")
            show_axes(load(args.images), segments, args.scale).save(args.out)
            print(f"\nwrote {args.out}: check that each segment sits on the line you read")
        print("\nthe points are your reading; confirm the ones a verdict rests on with "
              "`look.py probe` or `edge`")
        return

    images = load(args.images)
    names = [os.path.basename(path) for path in args.images]
    palette = read_palette(args.palette)
    if args.mode == "grid":
        box = [int(v) for v in numbers(args.box, 4, "--box")]
        grid(images, box, args.scale, args.step, args.size, names).save(args.out)
        print(f"wrote {args.out}: read positions off it to place points, then confirm the ones "
              "you judge by\nwith `look.py probe` or `look.py edge`; a grid read by eye is a "
              "placement, not a measurement")
        return
    pixels = [np.asarray(image) for image in images]
    if args.mode == "probe":
        points = [numbers(text, 2, "--at") for text in args.at]
        probe(pixels, points, args.scale, args.radius, palette, names)
        print("\nmedian of a patch; ~name is the nearest palette.json entry, (n) its Lab distance")
        return
    for text in args.ray:
        x, y, dx, dy = numbers(text, 4, "--ray")
        print(f"ray from ({x:g},{y:g}) toward ({dx:g},{dy:g})")
        for name, plane in zip(names, pixels):
            found = edges(plane, x, y, dx, dy, args.scale, args.contrast, args.length)
            if not found:
                print(f"    {name:12s} no edge over {args.contrast:g}")
                continue
            for rank, (t, ex, ey, before, after) in enumerate(found[:1 + args.more]):
                lead = f"{name:12s} edge" if rank == 0 else f"{'':12s} then"
                print(f"    {lead} at ({ex:.0f},{ey:.0f}), {t:.0f}px: "
                      f"{describe(before, palette)}  ->  {describe(after, palette)}")
    print("\nan edge is the first sample of the new colour; positions in working coordinates")


if __name__ == "__main__":
    main()
