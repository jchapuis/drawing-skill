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

## Simplify the values before tracing

Reduce the picture to **3 to 5 value groups** before any trace. A drawing has
few values, and a trace of a photograph with all of its values is a map of its
noise.

1. Blur or posterise a copy of `subject_1x.png`: a median filter a few pixels
   wide, then k-means or a fixed set of levels down to the groups you chose.
   Squint at the result beside the photograph. It should still read as the
   subject. If a form you need has merged into its ground, move a level, and do
   not add more groups.
2. Build `palette.json` from that simplified copy, one name per group plus the
   few accents the picture needs (an eye, a nose, a collar).
3. Trace with `trace.py --smooth PX`, PX near the size of the grain. Check that
   the unmatched-colour figure falls and that the region count drops to tens,
   not hundreds. If it does not, the values are not simple enough yet.

The simplified copy is a measuring aid, like a crop. The masses and flats are
still typed into `draw.py` by you, from points you read off it.

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
where the silhouette turns, as for any traced contour. Where nothing separates
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

Lose the rest: a silhouette edge where object and ground share a value is drawn
broken and fine, or not at all, and the value change inside a soft form is left
to the flats. Weight follows the same choice: heaviest on the shadow side and at
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
- Grass in front of a body breaks its base: a few blades drawn over the
  silhouette say "in the grass" better than a field of strokes behind it.
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
shows there.

## Overlapping sub-forms of one surface

A furred body is one surface with sub-forms (a ruff over the chest, a muzzle on
the head) whose ink crosses each other's flats, so neither is in front. Write
their overlap row with `"in_front": "same"` (SKILL.md § The object stages).

## What the describer will say

A drawing in flats and line from a photograph can be read as "a flat-colour
illustration". That is a change of medium, not a fault, if it was decided at
stage 0: write it into `reading.md` with the acceptance list, so the describer
saying it does not count against the drawing.
