#!/usr/bin/env python3
"""Make the finished picture look like a drawing on paper that was scanned.

    python3 finish.py --style style.json --drawing drawing.png \\
                      [--construction construction.png] --out final.png

The tldraw render is flat vector colour on a perfect ground. This takes it and,
in order:

1. treats the marks the way the named medium sits on paper: pencil turns the
   dark marks into graphite that skips the paper's tooth; marker and
   watercolour put grain and uneven strength into the large flats (watercolour
   also darkens a flat at its edge, where the pigment dries); ink-pen and
   brush-pen make the ink a warm black that soaks a little into the paper;
   gouache stays matte and even;
2. for `finish: sketch`, lays the construction render under the picture as
   faint graphite (through the colour for see-through media, only on bare
   paper for gouache);
3. multiplies a paper made from noise (its tint, mottling, fibres and tooth
   set by the paper type), so white paper stays white where the texture is at
   its lightest and every mark takes the paper's grain;
4. for `scan: true`, tilts the sheet a fraction of a degree, lights it
   unevenly, adds sensor noise and saves it through JPEG once.

It never adds a mark. Every step either keeps a pixel's darkness, scales it, or
spreads it by a pixel or two, so a dark pixel in the output always sits on or
next to a dark pixel of drawing.png or construction.png. The paper and the
light can only take the ground down a few percent.

Everything random comes from the style's `seed`, so the same inputs give the
same file. It uses numpy, scipy and PIL only; nothing is downloaded.

The gates never look at final.png. They judge the tldraw renders.
"""
import argparse
import io
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, signal

MEDIA = ("ink-pen", "brush-pen", "pencil", "marker", "watercolour+ink", "gouache")
PAPERS = ("none", "smooth", "cold-press", "newsprint", "sketchbook")
FINISHES = ("clean", "sketch")
HANDS = ("right", "left")

# How each paper looks, in render pixels (a render is two pixels per page unit).
#   tint      -- the paper's own colour, multiplied in
#   mottle    -- strength of the broad, cloudy unevenness of the sheet
#   tooth     -- strength and size of the fine bumps that catch graphite and pigment
#   fibres    -- how many short fibres per million pixels, and how much they show
PAPER = {
    "smooth": dict(tint=(1.0, 0.996, 0.988), mottle=0.010, tooth=(0.012, 0.7),
                   fibres=(60, 0.010)),
    "cold-press": dict(tint=(1.0, 0.992, 0.972), mottle=0.018, tooth=(0.055, 1.6),
                       fibres=(40, 0.010)),
    "newsprint": dict(tint=(0.945, 0.925, 0.865), mottle=0.030, tooth=(0.022, 0.8),
                      fibres=(500, 0.040)),
    "sketchbook": dict(tint=(0.995, 0.982, 0.948), mottle=0.016, tooth=(0.028, 1.1),
                       fibres=(160, 0.016)),
}
# with no paper, a medium that needs grain still gets a fine one, but no colour
NO_PAPER_TOOTH = 0.9

GRAPHITE = np.array([0.30, 0.30, 0.325])   # the colour of a heavy pencil line
WARM_INK = np.array([0.94, 1.0, 1.07])     # per-channel ink strength: less red absorbed, so warmer


def fail(message):
    raise SystemExit(f"finish: {message}")


def read_style(path):
    """The style, checked. A value it cannot use stops the run with the reason."""
    try:
        with open(path) as handle:
            style = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read {path}: {error}")
    if not isinstance(style, dict):
        fail(f"{path} must hold one JSON object")
    known = {"medium", "hand", "finish", "handedness", "paper", "scan", "seed", "sophistication"}
    unknown = sorted(set(style) - known)
    if unknown:
        fail(f"{path}: unknown key(s) {unknown}; the keys are {sorted(known)}")
    missing = [key for key in ("medium", "finish", "paper", "scan", "seed") if key not in style]
    if missing:
        fail(f"{path}: missing {missing}")
    for key, allowed in (("medium", MEDIA), ("finish", FINISHES), ("paper", PAPERS)):
        if style[key] not in allowed:
            fail(f"{path}: {key} is {style[key]!r}; it must be one of {', '.join(allowed)}")
    if "handedness" in style and style["handedness"] not in HANDS:
        fail(f"{path}: handedness is {style['handedness']!r}; it must be right or left")
    if not isinstance(style["scan"], bool):
        fail(f"{path}: scan is {style['scan']!r}; it must be true or false")
    if not isinstance(style["seed"], int) or isinstance(style["seed"], bool):
        fail(f"{path}: seed is {style['seed']!r}; it must be a whole number")
    hand = style.get("hand", 0.5)
    if isinstance(hand, bool) or not isinstance(hand, (int, float)) or not 0 <= hand <= 1:
        fail(f"{path}: hand is {hand!r}; it must be a number from 0 to 1")
    return style


def load(path):
    try:
        return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    except OSError as error:
        fail(f"cannot read {path}: {error}")


def ground_colour(image):
    """The commonest colour, taken as the paper the render was drawn on."""
    codes = (np.round(image * 255).astype(np.int64) @ np.array([65536, 256, 1])).ravel()
    values, counts = np.unique(codes, return_counts=True)
    code = values[np.argmax(counts)]
    return np.array([(code >> 16) & 255, (code >> 8) & 255, code & 255]) / 255.0


def luminance(image):
    return image @ np.array([0.299, 0.587, 0.114])


def noise(rng, shape, sigma):
    """Smooth random field with mean 0 and spread 1, features about `sigma` pixels across."""
    field = ndimage.gaussian_filter(rng.standard_normal(shape), sigma, mode="wrap")
    return (field - field.mean()) / (field.std() + 1e-12)


def fibre_field(rng, shape, per_million, length=(10, 34)):
    """Short thin strands at random angles, 0 where there are none, up to about 1."""
    count = int(per_million * shape[0] * shape[1] / 1e6)
    field = np.zeros(shape)
    if count == 0:
        return field
    seeds = np.zeros(shape)
    seeds[rng.integers(0, shape[0], count), rng.integers(0, shape[1], count)] = 1.0
    # a few orientations, each a line-shaped blur of a share of the seeds
    for angle in rng.uniform(0, np.pi, 5):
        size = int(rng.uniform(*length))
        kernel = np.zeros((size, size))
        middle = (size - 1) / 2
        for step in np.linspace(-middle, middle, size * 2):
            kernel[int(round(middle + step * np.sin(angle))), int(round(middle + step * np.cos(angle)))] = 1
        share = seeds * (rng.random(shape) < 0.2)
        field += signal.fftconvolve(share, kernel, mode="same")
    field = ndimage.gaussian_filter(field, 0.5)
    return np.clip(field / (field.max() + 1e-12), 0, 1)


def tooth_field(rng, shape, size):
    """The paper's surface height, 0 (valley) to 1 (peak): rounded bumps with a
    network of ridges between them, like the grain of a sheet seen up close."""
    bumps = noise(rng, shape, size)
    ridges = 1 - np.abs(noise(rng, shape, size * 1.8))
    height = 0.55 * bumps + 0.45 * (ridges - ridges.mean()) / (ridges.std() + 1e-12)
    low, high = np.percentile(height, [1, 99])
    return np.clip((height - low) / (high - low), 0, 1)


def make_paper(rng, shape, paper):
    """The sheet: a multiplier near 1 per pixel and channel, and its tooth (0 valley .. 1 peak)."""
    if paper == "none":
        return np.ones(shape + (3,)), tooth_field(rng, shape, NO_PAPER_TOOTH)
    spec = PAPER[paper]
    mottle = 0.6 * noise(rng, shape, 90) + 0.3 * noise(rng, shape, 30) + 0.1 * noise(rng, shape, 9)
    strength, size = spec["tooth"]
    tooth = tooth_field(rng, shape, size)
    # light raking across the sheet from the top left: the side of a bump facing
    # it is lit and the far side is in shade, which is what makes grain read as relief
    relief = ndimage.sobel(tooth, axis=1) + ndimage.sobel(tooth, axis=0)
    relief = relief / (relief.std() + 1e-12)
    per_million, fibre_strength = spec["fibres"]
    fibres = fibre_field(rng, shape, per_million)
    shade = spec["mottle"] * mottle + strength * (0.6 * (tooth - 0.5) - 0.4 * relief / 2.5)
    shade -= fibre_strength * fibres
    # the brightest parts of the sheet read as the tint itself, as a scanner's white point does
    value = np.clip(1.0 + shade - 0.004, 0.85, 1.0)
    return value[..., None] * np.array(spec["tint"]), tooth


def regions(drawing, ground):
    """How much each pixel is ink (dark mark), the mask of the large even flats
    of colour, and a number per flat (0 off the flats)."""
    light = luminance(drawing)
    chroma = drawing.max(axis=2) - drawing.min(axis=2)
    paper_light = float(luminance(ground[None, None])[0, 0])
    ink = (light < 0.32 * paper_light) | ((light < 0.5 * paper_light) & (chroma < 0.1))
    # how much each pixel is ink, soft at the antialiased edge
    ink_amount = np.clip((0.55 * paper_light - light) / (0.4 * paper_light), 0, 1) * (chroma < 0.25)
    off_ground = np.abs(drawing - ground).max(axis=2) > 0.05
    spread = sum(ndimage.uniform_filter(drawing[..., c] ** 2, 5) - ndimage.uniform_filter(drawing[..., c], 5) ** 2
                 for c in range(3))
    even = spread < 0.0015
    candidate = off_ground & even & ~ndimage.binary_dilation(ink, iterations=1)
    labels, count = ndimage.label(candidate)
    if count:
        sizes = ndimage.sum(candidate, labels, np.arange(1, count + 1))
        keep = np.concatenate([[False], sizes > max(300, 0.0015 * light.size)])
        flats = keep[labels]
    else:
        flats = np.zeros_like(candidate)
        labels = np.zeros(candidate.shape, dtype=int)
    return ink_amount, flats, labels * flats


def density(image, ground):
    """How much light each channel of a pixel takes away from the ground (0 on bare paper)."""
    return -np.log(np.clip(image, 1e-4, 1) / np.clip(ground, 1e-4, 1))


def from_density(amount, ground):
    return np.clip(ground * np.exp(-amount), 0, 1)


def side_by_side(rng, shape, slant, width, overlap):
    """Strokes laid side by side to fill an area. Returns two fields: 1 on a
    strip covered twice (0 elsewhere), and each stroke's own small difference in
    strength (mean 0, spread 1). The strokes run at `slant` radians from the
    horizontal, are about `width` pixels wide, and each overlaps the last by
    about `overlap` of its width. Widths, overlaps and paths all wander, as a
    hand's do."""
    height, wide = shape
    yy, xx = np.mgrid[0:height, 0:wide].astype(float)
    across = (xx * np.sin(slant) + yy * np.cos(slant)
              + 0.15 * width * noise(rng, shape, 160) + 0.02 * width * noise(rng, shape, 30))
    low, high = across.min() - width, across.max() + width
    count = int((high - low) / (width * 0.4)) + 2
    widths = width * rng.uniform(0.65, 1.35, count)
    steps = widths[:-1] * (1 - np.clip(overlap * rng.uniform(0.2, 1.8, count - 1), 0, 0.8))
    starts = low + np.concatenate([[0], np.cumsum(steps)])
    index = np.clip(np.searchsorted(starts, across, side="right") - 1, 1, count - 1)
    twice = across < starts[index - 1] + widths[index - 1]
    own = rng.standard_normal(count)[index]
    return ndimage.gaussian_filter(twice.astype(float), 0.8), ndimage.gaussian_filter(own, 0.8)


def fill_strokes(rng, shape, slant, flat_number, width, overlap):
    """`side_by_side` with each flat filled in its own direction: three
    directions near the hand's slant, one picked per flat."""
    layers = [side_by_side(rng, shape, slant + turn, width, overlap) for turn in np.radians((-14, 0, 17))]
    pick = rng.integers(0, len(layers), flat_number.max() + 1)[flat_number]
    twice = np.choose(pick, [layer[0] for layer in layers])
    own = np.choose(pick, [layer[1] for layer in layers])
    return twice, own


def treat_medium(rng, drawing, ground, medium, tooth, handedness):
    """Apply the medium to the drawing, still on its own flat ground. Returns the
    image and how much each pixel is covered by paint or ink (for gouache)."""
    ink_amount, flats, flat_number = regions(drawing, ground)
    shape = drawing.shape[:2]
    # density is measured from white paper, not from the commonest colour. On a
    # full-bleed picture the commonest colour is paint (a field, a sky), and any
    # flat lighter than it would come out with negative density and be pushed
    # back to the ground's colour
    paper = np.ones(3)
    dense = density(drawing, paper)
    flat_weight = ndimage.gaussian_filter(flats.astype(float), 1.0)
    # strokes that fill an area lean like / for a right hand and like \ for a left one
    slant = np.radians(rng.uniform(50, 65)) * (1 if handedness == "right" else -1)

    if medium == "pencil":
        # graphite is grey however hard it is pressed, and the paper's valleys stay white
        light_dense = dense.mean(axis=2, keepdims=True)
        graphite_dense = np.minimum(light_dense * 0.75, 1.05) * density(GRAPHITE, np.ones(3)) / density(GRAPHITE, np.ones(3)).mean()
        grain = np.clip(0.35 + 0.95 * tooth, 0.25, 1.0)[..., None]
        streak = 1 + 0.10 * noise(rng, shape, (0.8, 6))[..., None]
        graphite_dense = graphite_dense * grain * streak
        # coloured pencil: hatched strokes, darker where two cross, skipping the valleys
        twice, own = fill_strokes(rng, shape, slant, flat_number, 9, 0.25)
        colour_grain = np.clip(0.5 + 0.65 * tooth, 0.35, 1.0) * (0.8 + 0.3 * twice + 0.06 * own)
        colour_dense = dense * colour_grain[..., None]
        weight = ink_amount[..., None]
        dense = weight * graphite_dense + (1 - weight) * colour_dense

    elif medium in ("marker", "watercolour+ink"):
        water = medium == "watercolour+ink"
        # broad uneven strength, then pigment settling into the paper's valleys
        if water:
            variation = 1 + 0.10 * noise(rng, shape, 55) + 0.05 * noise(rng, shape, 14)
            granulation = 1 + 0.32 * (0.5 - tooth) + 0.03 * noise(rng, shape, 1.2)
        else:
            variation = 1 + 0.05 * noise(rng, shape, 25)
            granulation = 1 + 0.06 * (0.5 - tooth)
        if not water:
            # marker strokes lie side by side, and the ink doubles where they overlap
            twice, own = fill_strokes(rng, shape, slant, flat_number, 34, 0.25)
            granulation = granulation * (1 + 0.16 * twice + 0.04 * own)
        factor = variation * granulation
        if water:
            # the pigment creeps to a flat's edge as it dries, and leaves a darker rim
            inside = ndimage.distance_transform_edt(flats)
            rim = np.exp(-inside / 4.0) * flats
            factor = factor * (1 + 0.55 * rim)
        factor = 1 + (factor - 1) * flat_weight
        dense = dense * np.clip(factor, 0.6, 1.8)[..., None]

    elif medium == "gouache":
        # even, matte paint: a faint unevenness, a touch of chalk on the darks
        twice, own = side_by_side(rng, shape, slant, 40, 0.2)
        brush = 1 + 0.025 * noise(rng, shape, 30) + 0.03 * twice + 0.015 * own
        factor = 1 + (brush - 1) * flat_weight
        dense = dense * factor[..., None] * 0.95

    if medium in ("ink-pen", "brush-pen", "marker", "watercolour+ink"):
        # ink: warm black, soaking a little into the paper along the fibres
        ink_dense = dense * ink_amount[..., None]
        reach = 0.9 if medium == "brush-pen" else 0.6
        soaked = np.stack([ndimage.gaussian_filter(ink_dense[..., c], reach) for c in range(3)], axis=2)
        soak = (0.55 + 0.35 * np.clip(0.5 + 0.5 * noise(rng, shape, 1.5), 0, 1))[..., None]
        dense = np.maximum(dense, soaked * soak)
        warm = 1 + (WARM_INK - 1) * ink_amount[..., None]
        dense = dense * warm

    covered = np.clip(flat_weight + ink_amount, 0, 1)
    return from_density(dense, paper), covered


def middles(image, marked):
    """The middle two or three pixels of every band in `marked`. Each stage has
    its own colour, so the bands are split by colour first: where a gesture
    crosses a block-in, both lines keep their own middle."""
    codes = (np.round(image * 255).astype(np.int64) @ np.array([65536, 256, 1]))[marked]
    values, counts = np.unique(codes, return_counts=True)
    main = values[np.argsort(counts)[::-1][:6]]
    main = main[counts[np.argsort(counts)[::-1][:6]] >= 0.02 * marked.sum()]
    if len(main) == 0:
        return marked
    colours = np.stack([(main >> 16) & 255, (main >> 8) & 255, main & 255], axis=1) / 255.0
    apart = ((image[..., None, :] - colours) ** 2).sum(axis=3)
    nearest = np.argmin(apart, axis=2)
    # only pixels close to a stage colour: an antialiased edge or an overlap is
    # a mixture, and taken as a band of its own it would outline the real one
    pure = apart.min(axis=2) < 0.004
    result = np.zeros_like(marked)
    for index in range(len(colours)):
        band = marked & pure & (nearest == index)
        # bridge where another line crossed this one
        band = marked & ndimage.binary_closing(band, iterations=4)
        depth = ndimage.distance_transform_edt(band)
        result |= band & (depth >= ndimage.maximum_filter(depth, 5) - 1.0)
    return result


def sketch_layer(construction, medium, covered, tooth, opacity):
    """The construction render as faint graphite: a per-pixel multiplier near 1.

    The stage looks are broad translucent bands, which no pencil makes, so each
    band is narrowed to its middle few pixels first. That only takes pixels
    away; it never puts a line where the render had none."""
    ground = ground_colour(construction)
    amount = np.clip(np.abs(construction - ground).max(axis=2) / 0.45, 0, 1)
    line = ndimage.gaussian_filter(middles(construction, amount > 0.25).astype(float), 0.6)
    amount = np.minimum(amount, np.clip(line * 1.6, 0, 1))
    amount = amount * opacity * np.clip(0.6 + 0.6 * tooth, 0.5, 1.0)
    if medium == "gouache":
        # opaque paint hides the pencil under it
        amount = amount * (1 - covered)
    return 1 - amount[..., None] * (1 - GRAPHITE)


def scan(rng, image):
    """A flatbed scan: a slight tilt, light falling off unevenly, noise, a JPEG."""
    height, width = image.shape[:2]
    angle = rng.uniform(0.12, 0.4) * rng.choice([-1, 1])
    tilted = np.stack([ndimage.rotate(image[..., c], angle, reshape=False, order=1, mode="nearest")
                       for c in range(3)], axis=2)
    yy, xx = np.mgrid[0:height, 0:width]
    yy = yy / height - 0.5
    xx = xx / width - 0.5
    lean = rng.uniform(-1, 1, 2)
    light = 1 - 0.035 * (lean[0] * xx + lean[1] * yy + 0.5) - 0.05 * (xx ** 2 + yy ** 2)
    light = light + 0.01 * noise(rng, (height, width), 120)
    light = np.clip(light / light.max(), 0.93, 1.0)
    lit = tilted * light[..., None]
    # a scanner never reads full black, and a little blur from its optics
    lit = 0.045 + 0.95 * lit
    lit = np.stack([ndimage.gaussian_filter(lit[..., c], 0.45) for c in range(3)], axis=2)
    lit = lit + rng.normal(0, 0.007, lit.shape) + rng.normal(0, 0.004, (height, width, 1))
    encoded = io.BytesIO()
    Image.fromarray(np.round(np.clip(lit, 0, 1) * 255).astype(np.uint8)).save(encoded, "JPEG", quality=86)
    encoded.seek(0)
    return np.asarray(Image.open(encoded).convert("RGB"), dtype=np.float64) / 255.0


def finish(style, drawing, construction=None):
    """The whole pipeline on arrays in 0..1. Returns the finished image."""
    if style["finish"] == "sketch" and construction is None:
        fail("finish is sketch, so a construction render is needed (--construction)")
    if construction is not None and construction.shape != drawing.shape:
        fail(f"construction is {construction.shape[1]}x{construction.shape[0]} but the drawing is "
             f"{drawing.shape[1]}x{drawing.shape[0]}; render both with the same frame and flags")
    rng = np.random.default_rng(style["seed"])
    shape = drawing.shape[:2]
    ground = ground_colour(drawing)
    sheet, tooth = make_paper(rng, shape, style["paper"])
    image, covered = treat_medium(rng, drawing, ground, style["medium"], tooth,
                                  style.get("handedness", "right"))
    if style["finish"] == "sketch":
        image = image * sketch_layer(construction, style["medium"], covered, tooth, opacity=0.55)
    if style["medium"] == "gouache":
        # the paint sits on top of the paper, so its grain shows only faintly through
        sheet = 1 - (1 - sheet) * (1 - 0.75 * covered[..., None])
    image = image * sheet
    if style["scan"]:
        image = scan(rng, image)
    return np.clip(image, 0, 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--style", required=True)
    parser.add_argument("--drawing", required=True)
    parser.add_argument("--construction")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    style = read_style(args.style)
    drawing = load(args.drawing)
    construction = load(args.construction) if args.construction else None
    if construction is not None and style["finish"] == "clean":
        print("finish: finish is clean, so the construction render is not used", file=sys.stderr)
        construction = None
    result = finish(style, drawing, construction)
    Image.fromarray(np.round(result * 255).astype(np.uint8)).save(args.out)
    print(f"finished {args.out}")


if __name__ == "__main__":
    main()
