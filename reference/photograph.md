# Drawing from a photograph

A photograph is the hardest subject to measure with these tools. Most of them
were built for subjects made of flats and ink, and a photograph has neither:

- **No ink.** Every edge is a value edge, where one tone meets another. There is
  no line to measure with `--measure-line`, so the line character is a decision
  you make at stage 0 and write in `reading.md`, not a measurement.
- **Continuous tone.** A surface is a gradient, not a flat. Sampled pixel by
  pixel, a palette of a dozen names still leaves a large share of the picture
  unmatched, and the trace returns hundreds of small regions of noise.
- **Grain.** Sensor noise, fur, grass and foliage break into short fragments at
  every threshold. The tools read those fragments as marks.

So the work at stage 0 is to turn the photograph into something with flats and
edges first, and to choose which of its edges the drawing will state.

## Write the pose and the acceptance list first

Before any trace, write two things in `reading.md`:

- **A construction line for the pose**: one sentence on how the body is
  arranged and where its weight rests (for example "lying on its chest, one
  foreleg forward, paw on the ground"). The pose decides the big shape of the
  mass and how it meets the ground, so a drawing that skips it tends to read as
  a different pose.
- **The acceptance list**: what the finished drawing must show, including the
  parts that are easy to lose (the paw as its own shape, the tail, a closed
  mouth). Write it before drawing, and check the drawing against it, not
  against whatever the describer happens to say.

## Simplify the values before tracing

Reduce the picture to **3 to 5 value groups per object**, not for the picture as
a whole, in order to find the masses. A drawing has few values, and a trace of a
photograph with all of its values is a map of its noise. Keep the object's hue
ramp: a golden coat stays gold from light to shadow, and shade makes it darker
and redder, not brown. Then draw **each mass as the groups you see inside it**,
with at least 3 steps on the head, and soften the boundaries: never type a group
boundary as a straight facet.

1. Blur or posterise a copy of `subject_1x.png`: a median filter a few pixels
   wide, then k-means or a fixed set of levels down to the groups you chose.
   Squint at the result beside the photograph. It should still read as the
   subject. If a form you need has merged into its ground, move a level, and do
   not add more groups to that object.
2. Build `palette.json` with one name per group plus the few accents the
   picture needs (an eye, a nose, a collar). The simplified copy says **where**
   each group lies; it does not give its colour. A k-means centre or a
   posterised level is an average of the group's pixels, including the
   highlights, the shadow edge and the ground's spill, and it comes out greyer
   than the surface (see "Sample colour at the saturated mid-tones" below).
3. Trace with `trace.py --smooth PX`, PX near the size of the grain. Check that
   the unmatched-colour figure falls and that the region count drops to tens,
   not hundreds. If it does not, the values are not simple enough yet.

The simplified copy is a measuring aid, like a crop. The masses and flats are
still typed into `draw.py` by you, from points you read off it.

## Sample colour at the saturated mid-tones

A photographed surface shows its own colour most strongly in the mid-tones of
the lit side and in the core of its shadow. The highlight is washed towards
the light's colour and towards white, the shadow edge mixes with what is
around it, and on fur or grass the ground's colour spills into the edge. An
average over the whole object takes all of that in.

- For each value step of an object, find the patch inside the form where that
  step is most saturated (away from edges, highlights and specular spots), and
  sample its median there, over a patch a few grain sizes wide so one hair
  does not decide it. Write the patch's coordinates beside the name in
  `reading.md`.
- Keep the ramp you read: shadow steps darker and, on fur, skin and most warm
  materials, warmer or more saturated than the lit step, not greyer. Read it
  off the subject; do not assume it.
- Check the palette's chroma against the subject's: put each step's saturation
  beside the saturation of the subject's most saturated tenth of the object's
  pixels at that value. A step well below it is still an average.
- After the first flats, run `check.py drawing.png --ref subject.png --colour
  parts.json`. A `<<` on `mid` with the medians in agreement is this fault.

## Typed shapes from a photograph

A contour or fill read off a crop gets a point every 40 to 60 px at most (a
starting spacing, adjust it to the size of the object) and is drawn with
`smooth=True`. Only edges that are straight in the subject (a wall, a post) use
`smooth=False`. After the fills, look at 1x: if any outline shows a straight
segment longer than about 8% of the object (also a starting figure), add points.

## Find the silhouette by value or hue

A photographed object often shares its value with its ground somewhere (a pale
head against pale straw, a dark leg in shadowed grass). Find its silhouette from
whatever separates it from the ground there:

- by **value**, where it is lighter or darker than what is behind it;
- by **hue**, where the values match but the colours do not (a tan coat against
  green grass: red minus green separates them when brightness does not);
- by both, combined into one mask, then closed and opened with a small kernel
  so grain does not fray its edge, and bounded by the part's box from
  `parts.json` (see "A region-growing measurement needs a bound" in SKILL.md).

A script that prints the mask's outline is measuring. You then type the points
where the silhouette turns, and more between them so no run is left straight
(see "Typed shapes from a photograph"), as for any traced contour. Where nothing separates
object from ground (a body lost in tall grass), the edge is your decision:
write it down in `reading.md` as one.

## Choose which edges to keep

A photograph has an edge wherever the value changes, and most of them are not
lines. Keep:

- the silhouette where it is **found**: a strong value step against the ground;
- the edges of the features that carry identity and expression (eyes, nose,
  mouth, ear openings), usually the darkest accents in the picture;
- shadow edges where a form turns sharply, and the contact shadows where one
  form meets another.

Lose the rest: the value change inside a soft form is left to the flats. A
silhouette that is lost into its ground is still drawn: use a thin, broken
graphite line on top of the fill, or soften the fill edge with a second, lighter
fill. Never leave a bare polygon edge. Weight follows the same choice: heaviest on the shadow side and at
contacts, finest where an edge is nearly lost.

## Fur, grass and foliage: directional strokes

Texture in a photograph is too fine and too dense to draw mark for mark, and a
trace of it is noise. Indicate it, as `line.md` § Hatching and texture says:

- Read the **direction** off `--zoom`: the way the hair grows, the way the blades
  lean. Long fur and grass are long strokes. A blade that runs a long way in the
  photograph is one long mark, not a row of short ones.
- Put the strokes **at the edges and the turning points**: the silhouette, where
  a lock or a ruff breaks the outline, where the form turns into shadow, and
  under the chin or the ear. Let them thin out and stop on the lit planes.
- Fur strokes are **lighter than the flat, the same value, or one step darker,
  never the darkest value on the page**. Start at 2 to 4 px at delivered size.
  Vary their length and spacing, and run them along the growth direction. Add a
  few stray strokes that cross the silhouette (at an ear, a ruff, a tail). A fur
  stroke may not be a regular row of the same curve.
- Grass in front of a body breaks its base: a few blades drawn over the
  silhouette say "in the grass" better than a field of strokes behind it.
- The ground is a textured mass, not two flat polygons: lay the dark and the mid
  green as overlapping soft-edged flats and put the blades on top in two or
  three directions at varied lengths. Soften any boundary between masses.
- Each stroke is still its own `stroke` with points you read.

## Do not trust `--hatch` on grain

`--hatch` reads a photograph's grain as a group of short parallel marks, with an
angle, a spacing and a length that look like hatching. They are not, and an entry
written from them sets a target the drawing should not meet. `--hatch` warns
(**WARN grain**) when the marks are short (median under three times `--line`) and
fade under a light blur. A drawn stroke keeps its contrast under that blur;
grain does not. When it warns:

- write no `hatch` entry for that box;
- record the direction of the real strokes, read off `--zoom`, in `reading.md`,
  and check the drawing against them on `--zoom`, not with `--linework`;
- treat `--linework`'s weight span over a photograph with the same suspicion:
  over a textured area it measures the texture.

## Weights at the delivered size

The drawing is made at 4x, and viewed and described at 1x. A fine line matched
to texture in the 4x space is under a pixel at delivered size and vanishes, and
the picture then reads as flat colour. Downsample the weight swatch and the first
ink to the delivered size and look at them. Raise the finest weight until it
shows at 1x, but keep fur strokes soft in contrast. Heavy dark ink is for the
nose, eyes, mouth and contact shadows only.

## Overlapping sub-forms of one surface

A furred body is one surface with sub-forms (a ruff over the chest, a muzzle on
the head) whose ink crosses each other's flats, so neither is in front. Write
their overlap row with `"in_front": "same"` (SKILL.md § The object stages).

## What the describer will say

A drawing in flats and line from a photograph can be read as "a flat-colour
illustration". That is a change of medium, not a fault, if it was decided at
stage 0: write it into `reading.md` with the pose line and the acceptance list, so the describer
saying it does not count against the drawing.
