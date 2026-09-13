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
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage


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


def marks(row, dark=100):
    widths, run = [], 0
    for value in row:
        if value < dark:
            run += 1
        elif run:
            widths.append(run)
            run = 0
    if run:
        widths.append(run)
    return sorted(width for width in widths if width > 1)


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
        print(f"y={y:4d}  subject {found}")
        print(f"        drawing {made}")
    print("\nmatch the span, not the individual runs: finest and heaviest, and "
          "the ratio between them.")


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
    size = (width * factor, height * factor)
    above = subject.crop((x, y, x + width, y + height)).resize(size, Image.LANCZOS)
    below = drawing.crop((x, y, x + width, y + height)).resize(size, Image.LANCZOS)
    sheet = Image.new("RGB", (size[0], size[1] * 2 + 40), (250, 250, 248))
    pen = ImageDraw.Draw(sheet)
    sheet.paste(above, (0, 16))
    pen.text((4, 2), "subject", fill=(25, 25, 25))
    sheet.paste(below, (0, size[1] + 34))
    pen.text((4, size[1] + 20), "drawing", fill=(25, 25, 25))
    return sheet


def masses(drawing, subject, box=None, colours=5, blow=3):
    """Both pictures reduced to flat masses, side by side, with no line at all.

    This is the check that sees *shape*, and it is the one the rest of the kit
    cannot do. Everything else here compares marks: where they landed, how wide
    they are, whether colour agrees with them. A head can pass every one of those
    -- every feature inside its own measured box, every box within ten pixels of
    the subject's -- and still not be a face, because a wedge and an oval share a
    bounding rectangle and differ in the only way that matters.

    Reducing each picture to a few flat areas throws away the line, the detail
    and the rendering, and leaves the masses the eye actually reads first. Do it
    early, before any contour: if the masses do not say the same thing as the
    subject's, nothing drawn on top of them will fix it.

    Each image is quantised to its own dominant colours rather than to a shared
    palette, because the two need not share one -- what is being compared is the
    shape of the areas, not their hues.
    """
    drawing = drawing.resize(subject.size, Image.LANCZOS)
    if box:
        x, y, width, height = box
        subject = subject.crop((x, y, x + width, y + height))
        drawing = drawing.crop((x, y, x + width, y + height))
    flat = [_flatten(image, colours).resize((image.width * blow, image.height * blow),
                                            Image.NEAREST)
            for image in (subject, drawing)]
    gap, label = 20, 18
    sheet = Image.new("RGB", (flat[0].width + flat[1].width + gap * 3,
                              flat[0].height + label + gap * 2), (255, 255, 255))
    pen = ImageDraw.Draw(sheet)
    pen.text((gap, gap), "subject — masses only", fill=(30, 30, 30))
    pen.text((gap * 2 + flat[0].width, gap), "drawing — masses only", fill=(30, 30, 30))
    sheet.paste(flat[0], (gap, gap + label))
    sheet.paste(flat[1], (gap * 2 + flat[0].width, gap + label))
    return sheet


def _flatten(image, colours):
    """Reduce to a few flat areas and close the line art away.

    Quantising alone is not enough: the black line survives as one of the areas
    and takes all the drawing's detail with it, which is the very thing being
    thrown away. So the darkest area is removed and the areas around it grow
    into the space it leaves, which is what "no line at all" has to mean.
    """
    banded = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=colours)
    table = np.asarray(banded.getpalette()[:colours * 3], dtype=float).reshape(-1, 3)
    label = np.asarray(banded, dtype=int)
    darkest = int(table.mean(axis=1).argmin())
    keep = label != darkest
    if keep.any():
        _, source = ndimage.distance_transform_edt(~keep, return_indices=True)
        label = label[source[0], source[1]]
    return Image.fromarray(table[label].astype(np.uint8), "RGB")


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

    A junction is an entry like any other -- `"hand/bar"` with a sentence saying
    which is in front and how wide the gap is. It needs no machinery of its own,
    and it is where every scene here has failed.
    """
    with open(path) as handle:
        raw = json.load(handle)
    inventory = {}
    for name, entry in raw.items():
        if isinstance(entry, dict):
            if "box" not in entry:
                sys.exit(f"parts.json: {name!r} has no box")
            inventory[name] = {"box": entry["box"],
                               "shape": " ".join(str(entry.get("shape", "")).split()),
                               "rel": " ".join(part for part in (
                                   f"in front of {entry['front_of']}" if entry.get("front_of") else "",
                                   f"touches {entry['touches']}" if entry.get("touches") else "",
                                   f"gap {entry['gap']}" if entry.get("gap") else "") if part)}
        else:
            inventory[name] = {"box": entry, "shape": "", "rel": ""}
    return inventory


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
        pen.text((left, top + head + cell * 2 + 1),
                 f"ink {share[0]:.0f}%->{share[1]:.0f}%  form {body[0]:.0f}%->{body[1]:.0f}%"
                 + ("   MISSING?" if gone else ""),
                 fill=(200, 30, 30) if gone else (90, 90, 90))
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
        tier = next((digit for digit in "123" if f"TIER {digit}" in said),
                    "J" if "JUNCTION" in said else "-")
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
    parse.add_argument("--weights", default="",
                       help="comma-separated rows: print the mark widths each one crosses")
    parse.add_argument("--masses", action="store_true",
                       help="both pictures as flat masses, no line — the check that "
                            "sees shape. Takes --box x,y,w,h and --colours N")
    parse.add_argument("--box", default="", help="x,y,w,h to crop both to")
    parse.add_argument("--colours", type=int, default=5)
    parse.add_argument("--parts", default="",
                       help="a JSON file of {name: [x,y,w,h]} — every named part of "
                            "the picture, subject above and drawing below")
    parse.add_argument("--ranking", default="",
                       help="parts.json: what leads the eye, the drawing's order "
                            "against the subject's")
    parse.add_argument("--registration", action="store_true",
                       help="report every place the colour and the line disagree")
    parse.add_argument("--paper", default="#FAF1D2", help="the ground colour")
    parse.add_argument("--space", default="",
                       help="x0,y0,x1,y1 the render covers, so faults are reported "
                            "in the drawing's own coordinates")
    args = parse.parse_args()

    drawing = Image.open(args.render).convert("RGB")
    plumbs = [float(value) for value in args.plumb.split(",") if value.strip()]

    if args.weights:
        if not args.ref:
            sys.exit("--weights needs --ref")
        subject = Image.open(args.ref).convert("L")
        report(subject, drawing.convert("L").resize(subject.size, Image.LANCZOS),
               [int(part) for part in args.weights.split(",")])
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

    if args.ranking:
        if not args.ref:
            sys.exit("--ranking needs --ref")
        subject = Image.open(args.ref).convert("RGB")
        rows = ranking(drawing, subject, read_inventory(args.ranking))
        print(f"what leads the eye, worst disagreement first. value spread inside each "
              f"part's own\nbox, ranked 1..{len(rows)} in each picture. tier is read off "
              "the shape sentence; J is a junction.\n")
        print(f"  {'part':26s} tier {'subject':>15s} {'drawing':>15s}   moved")
        for name, tier, loud, now, seat, place in rows:
            move = seat - place
            print(f"  {name[:26]:26s} {tier:4s} {loud:8.1f} #{seat:<5d} {now:8.1f} #{place:<5d} "
                  f"{move:+4d}  " + ("LOUDER than the subject ranks it" if move > 0 else
                                     "quieter" if move < 0 else ""))
        print("\nmoved is the subject's rank minus the drawing's. + means the drawing "
              "pushes the part\nforward of where the subject has it, - means it has "
              "dropped back.\nA rank is zero-sum: this is the one number here that "
              "adding marks cannot lift,\nso the only way up is to put something else "
              "down. A junction that has gone\nquiet is two objects welded into one "
              "value. Crop the part and look before\nyou believe any row.")
        return

    if args.registration:
        paper = tuple(int(args.paper.lstrip("#")[at:at + 2], 16) for at in (0, 2, 4))
        faults = registration(drawing, paper)
        span = [float(part) for part in args.space.split(",")] if args.space else \
            [0, 0, drawing.width, drawing.height]
        across = (span[2] - span[0]) / drawing.width
        down = (span[3] - span[1]) / drawing.height
        marked = drawing.convert("RGB").copy()
        pen = ImageDraw.Draw(marked)
        print(f"{len(faults)} faults, largest first — area, kind, box in drawing coords\n")
        for number, (area, kind, x, y, width, height) in enumerate(faults, 1):
            colour = (215, 40, 40) if kind == "spill" else (30, 90, 220)
            pen.rectangle([x - 3, y - 3, x + width + 2, y + height + 2], outline=colour, width=2)
            pen.text((x - 2, y - 16), f"{number}", fill=colour)
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
