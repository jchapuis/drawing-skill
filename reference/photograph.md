# Drawing from a photograph

A photograph is the hardest subject to measure with these tools, which were
mostly built for flats and ink. A photograph has neither:

- **No ink.** Every edge is a value edge, where one tone meets another. There is
  no line for `--measure-line` to measure, so the line character is a decision
  you make at stage 0 and write in `reading.md`.
- **Continuous tone.** A surface is a gradient, not a flat. Sampled pixel by
  pixel, a palette of a dozen names still leaves a large share of the picture
  unmatched, and `trace.py` returns hundreds of small regions of noise.
- **Grain.** Sensor noise, fur, grass and foliage break into short fragments at
  every threshold, and the tools read those fragments as marks.

So at stage 0, first turn the photograph into flats and edges with `segment.py`
(not `trace.py`), and choose which edges the drawing will state. The same holds
for a painted subject, whose brushwork and soft shading break up under
`trace.py` like grain.

## Contents

- Write the pose and the acceptance list first
- Simplify the values with segment.py
- Sample colour at the saturated mid-tones
- Typed shapes from a photograph
- Find the silhouette
- Choose which edges to keep
- Fur, grass and foliage: directional strokes
- Do not trust `--hatch` on grain
- Weights at the delivered size
- Overlapping sub-forms of one surface
- What the describer will say

## Write the pose and the acceptance list first

Before any trace, write two things in `reading.md`:

- **A construction line for the pose**: one sentence on how the body is arranged
  and where its weight rests (for example "lying on its chest, one foreleg
  forward, paw on the ground"). The pose decides the big shape of the mass and
  how it meets the ground; skip it and the drawing tends to show another pose.
- **The acceptance list**: what the finished drawing must show, including the
  parts that are easy to lose (the paw as its own shape, the tail, a closed
  mouth). Check the drawing against it, not against whatever the describer
  happens to say.

## Simplify the values with segment.py

To find the masses, reduce the picture to **3 to 5 value steps per object**
(not for the picture as a whole). These are steps of value within one object,
not the drawing's two value groups. A drawing has few values, and a trace of a
photograph with all its values is a map of its noise. Keep the object's hue
ramp: a golden coat stays gold from light to shadow, and shade makes it darker
and redder, not brown. Then draw **each mass as the steps you see inside it**,
with at least 3 steps on the head, and soften the boundaries. Never draw a step
boundary as a straight facet.

1. Segment the whole picture: `python3 segment.py subject_1x.png --palette
   palette.json --png regions.png`. It smooths away grain finer than `--detail`
   with an edge-preserving filter, then merges similar neighbours until about
   `--regions` (default 40) remain. In `regions.png`, the left half shows the
   subject with every boundary and region number, and the right half is the
   simplified copy, each region in its median colour. Squint at it beside the
   photograph: it should still read as the subject, and you should be able to name most regions (the head's lit plane, the ear, the
   chest, the paw, the ground). If a form you need has merged into its
   neighbour, raise `--regions`. If the ground breaks into many pieces, lower it.
2. Segment each object on its own box: `--box x,y,w,h` from `parts.json`, or a
   `crop.py` crop of `subject.png`. The detail scales to the box, so a head's
   eye, nose and muzzle come back as separate regions where the whole picture
   had them as one. Name each region as the lit step, the shade step, a cast
   shadow or an accent, as for any trace.
3. Build `palette.json` with one name per step, plus the few accents the
   picture needs (an eye, a nose, a collar). The regions tell you **where** each
   step lies, not its colour. A region's `median` averages all its pixels,
   including the highlights, the shadow edge and spill from the ground, so it
   comes out greyer than the surface (see "Sample colour at the saturated
   mid-tones" below). The `colour` each region carries is only the palette name
   nearest to that median.

The regions are a measuring aid, like a crop. You still type the masses and
flats into `draw.py` from points you read off them.

## Sample colour at the saturated mid-tones

A photographed surface shows its own colour most strongly in the mid-tones of
the lit side and in the core of its shadow. The highlight is washed towards the
light's colour and towards white, the shadow edge mixes with its surroundings,
and on fur or grass the ground's colour spills into the edge. An average over
the whole object includes all of that.

- For each value step of an object, find the patch inside the form where that
  step is most saturated (away from edges, highlights and specular spots), and
  take its median there, over a patch a few grain sizes wide so that one hair
  does not decide it. Write the patch's coordinates beside the name in
  `reading.md`.
- Keep the ramp you read. Shadow steps are darker and, on fur, skin and most
  warm materials, warmer or more saturated than the lit step, not greyer. Read
  this off the subject; do not assume it.
- Check the palette's saturation against the subject's: compare each step's
  saturation with that of the subject's most saturated tenth of the object's
  pixels at that value. A step well below it is still an average.
- After the first flats, run `check.py drawing.png --ref subject.png --colour
  parts.json`. A `<<` on `mid` while the medians agree means this fault. A
  `value` flag alone does not overrule the sample, because the subject's median
  includes the dark between hairs and the side in shade. Add the darker step
  where the subject is darker, and re-sample only when the flagged box holds the
  patch the entry came from (`reference/judging.md` § Judges, `--colour`).

## Typed shapes from a photograph

A contour or fill read off a crop gets points no more than 40 to 60 px apart (a
starting spacing; adjust it to the object's size) and is drawn with
`smooth=True`. Only edges that are straight in the subject (a wall, a post) use
`smooth=False`. After the fills, look at 1x. If any outline shows a straight
segment longer than about 8% of the object (also a starting figure), add points.

## Find the silhouette

A photographed object often has the same value as its ground somewhere (a pale
head against pale straw, a dark leg in shadowed grass). Measure its silhouette
with `segment.py --silhouette x,y --box x,y,w,h`. The seed is a point inside the
object, in its own mid-tone, away from a highlight or an accent. The box is the
part's box from `parts.json` (see "A region-growing measurement needs a bound" in
`reference/marks.md`). The tool learns the object's colours around the seed and the
ground's from just outside the box, so the outline follows whatever separates
them: value where the object is lighter or darker than what is behind it, and
hue where the values match but the colours do not (a tan coat against green
grass).

It prints the points where the outline turns, numbered in perimeter order,
writes the full contour to `--out`, and names each side of the box the outline
ran into: there the box stopped it, not the subject. Look at `--png` before
using the result. A dark accent inside the object (a nose, a
collar) can come back cut out of it, and a box that holds a neighbour with the
object's colours (a white sleeve beside a cat with white eyes) lets the outline
take in part of it. Tighten the box and run it again.

Then type the points where the silhouette turns, plus more between them so no
run is left straight (see "Typed shapes from a photograph"), as for any traced
contour. Copying every printed point in order is pasting, not drawing. Where
nothing separates object from ground (a body lost in tall grass), the edge is
your decision: record it in `reading.md` as one.

## Choose which edges to keep

A photograph has an edge wherever the value changes, and most of those are not
lines. Keep:

- the silhouette where it is **found**: a strong value step against the ground;
- the edges of the features that carry identity and expression (eyes, nose,
  mouth, ear openings), usually the darkest accents in the picture;
- shadow edges where a form turns sharply, and the contact shadows where one
  form meets another.

Lose the rest, and leave the value change inside a soft form to the flats. A
silhouette that is lost into its ground is still drawn: use a thin, broken
graphite line on top of the fill, or soften the fill edge with a second, lighter
fill. Never leave a bare polygon edge. Weight follows the same choice: heaviest
on the shadow side and at contacts, finest where an edge is nearly lost.

## Fur, grass and foliage: directional strokes

Texture in a photograph is too fine to draw mark for mark, and a trace of it is
noise. Suggest it instead, as `line.md` § Hatching and texture says:

- Read the **direction** off `--zoom`: the way the hair grows, the way the
  blades lean. Long fur and grass are long strokes: a blade that runs a long way
  in the photograph is one long mark, not a row of short ones.
- Put the strokes **at the edges and the turning points**: the silhouette, where
  a lock or a ruff breaks the outline, where the form turns into shadow, and
  under the chin or the ear. Let them thin out and stop on the lit planes.
- Make fur strokes **lighter than the flat, the same value, or one step darker,
  never the darkest value on the page**. Start at 2 to 4 px at delivered size.
  Vary their length and spacing, and run them along the growth direction. Add a
  few stray strokes that cross the silhouette (at an ear, a ruff, a tail). Never
  draw fur as a regular row of the same curve.
- Grass in front of a body breaks its base: a few blades drawn over the
  silhouette say "in the grass" better than a field of strokes behind it.
- Draw the ground as a textured mass, not two flat polygons: lay the dark and the
  mid green as overlapping soft-edged flats, and put the blades on top in two or
  three directions at varied lengths. Soften any boundary between masses.
- Each stroke is still its own `stroke`, with points you read.

## Do not trust `--hatch` on grain

`--hatch` reads a photograph's grain as short parallel marks whose angle,
spacing and length look like hatching. An entry written from them sets a target
the drawing should not meet.
`--hatch` warns (**WARN grain**) when the marks are short (median under three
times `--line`) and fade under a light blur. A drawn stroke keeps its contrast
under that blur; grain does not. When it warns:

- write no `hatch` entry for that box;
- record the direction of the real strokes, read off `--zoom`, in `reading.md`,
  and check the drawing against them on `--zoom`, not with `--linework`;
- distrust `--linework`'s weight span over a photograph for the same reason:
  over a textured area it measures the texture.

## Weights at the delivered size

The drawing is made at 4x, and viewed and described at 1x. A fine line matched
to texture at 4x is under a pixel wide at delivered size, so it vanishes and the
picture reads as flat colour. Downsample the weight swatch and the first ink to
the delivered size and look at them. Raise the finest weight until it shows at
1x, but keep fur strokes low in contrast. Heavy dark ink is for the nose, eyes,
mouth and contact shadows only.

## Overlapping sub-forms of one surface

A furred body is one surface with sub-forms (a ruff over the chest, a muzzle on
the head) whose ink crosses each other's flats, so neither is in front. Write
their overlap row with `"in_front": "same"` (SKILL.md § The object stages).

## What the describer will say

The describer may call a drawing in flats and line from a photograph "a
flat-colour illustration". If you decided that change of medium at stage 0, it
is not a fault: write it into `reading.md` with the pose line and the acceptance
list, so the remark does not count against the drawing.
