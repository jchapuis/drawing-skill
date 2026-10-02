# Line weight, inking, and blacks

## The weight hierarchy

Three tiers, and the ratio between finest and heaviest is roughly **8–10×**:

> **The ratio belongs to the style, not to drawing in general.** 8–10× is a
> heavily inked comic. A flat cel or *ligne claire* design runs nearer 2–3×, and
> its finest line is not fine at all. When there is a subject in front of you,
> **measure its own span** (the width of its lightest interior mark and its
> heaviest silhouette) and match that, instead of importing the number below.
>
> **Matching the span is only half of it. Match how much of the drawing sits at
> each weight.** Suppose the swatch is calibrated so its heaviest nib equals the
> subject's heaviest silhouette. The drawing will still come out far too heavy
> overall if the two weights below it are then spent freely, because a flat
> design reserves weight for the outer silhouette and drops to its finest line
> the moment it is inside a form. The symptom is a drawing that measures
> correctly feature by feature and reads as crude. `check.py --parts` shows it as
> a consistent ten to twenty points more ink than the subject in *every* box, and
> this is the one way it becomes visible. The error is invisible at full size and
> obvious at 4×. For example, a 22px band round a jaw whose subject uses 11px,
> with 2px threads inside a face whose subject never goes below 3px, reads as
> unfinished however well every mark is placed. `check.py --weights` reports both
> figures, in pixels.

1. **Heaviest**: the outer silhouette of the figure or object.
2. **Medium**: plane breaks, where two interior forms meet (sleeve against arm,
   jaw against neck).
3. **Finest**: surface detail inside a single plane. Even these should not be
   dead uniform: thicker in the middle, tapering to a point at open ends.

With four stroke sizes available, that maps to `xl`/`l` for silhouette, `m` for
plane breaks, `s` for detail.

### Measuring the hierarchy

Read the subject's span before choosing any weight, and read the drawing's after
its first ink. `check.py drawing.png --linework parts.json --ref subject.png`
prints the finest, middle and heaviest line width of each picture over the
inventory's boxes, read on each mark's centre line, and fails when the drawing's
span is under half the subject's. `--weights` on a few rows names single lines
(`width@centre`), so you can say which line is the heaviest and where it sits.

The common failure is one even, fairly heavy outline round every form, with the
interior lines nearly as heavy. It measures as a finest line two or three times
the subject's and a heaviest line about right. Fix it from the bottom:

- **Interior lines thin.** Surface detail and lines inside a form go down to the
  subject's finest width, usually a third or less of the silhouette.
- **Silhouette heavier**, and not evenly: heavier on the shadow side and where
  the form turns away, thinner on the lit side.
- **Heaviest at the contacts**: under a form resting on another, where a foot
  meets the ground, under an overhang, where a limb crosses the body. A heavy
  line there stands in for the cast shadow.

Each of these is a different `size` or pressure on a stroke you write, read back
on the swatch and on the drawing with `--weights`.

### How wide a span

Where line weight is quantified at all, it is quantified in technical pens, sold
from **0.03 mm to 0.8 mm**. The top of that range, 0.5–0.8 mm, is what panel
frames and backgrounds use. That puts the real span of a page at roughly **20×**,
wider than the **8–10×** that a single figure's contours span.

There is **no rule about how many weights**, and some artists ink a whole page
with one. What is not optional is that weight *varies*. Even *ligne claire*,
defined by flatness and the absence of hatching, varies it. Uniform weight is the
default nowhere in the medium.

## What decides the weight

**Decide the light source first.** Every later weight decision depends on it.

- **Shadow side heavy, light side thin**, on the same form. This works on
  anything solid; it does not apply to smoke, fire or cloud.
- **Depth**: foreground heavy, middle ground medium, background fine. This alone
  separates the planes with no shading at all.
- **Contact**: an edge touching another surface gets no extra weight; an edge
  pulled away into open air gets a thicker line. This is how "in front" reads.
- **Distance from the light**: further away, thicker. Under an overhead light the
  feet carry more weight than the head.
- **Anatomy**: thicker around fat and muscle mass, thinner around bone.
- **Curves**: thinnest at the apex of a curve. A motion swoosh is the exception
  and thickens at its apex.
- **Junctions**: thicken where structures meet, like jaw into neck.

**A top-lit face** gets heavier line under the top eyelid, under the nose, under
the top lip, under the bottom lip, and under the jaw, where heavy line stands in
for cast shadow. **Invert every weight** for underlighting, which is why
underlighting reads as sinister.

**Consistency**: keep all light-side lines roughly equal to each other and all
shadow-side lines roughly equal. Weight varies for a *reason*, never at random.

**Never give two adjacent objects on different depth planes the same weight.**
It merges them onto one plane, and a distant small figure starts to look like it
is standing on the near figure's shoulder.

## Line quality

- **Draw from the shoulder or elbow**, not the wrist, for anything longer than a
  few centimetres. That produces smooth even arcs instead of jittery pivoted
  segments.
- **Taper**: thick through the middle, pointed at both ends. Produce it by
  accelerating through the stroke and decelerating out of it, like a car
  reaching speed and coasting down instead of braking.
- **Ghost the stroke** two or three times before touching down, then execute in a
  single confident pass. Once the tool touches, do not hesitate or slow.
- **Never correct by overdrawing.** A second bolder mark makes the error *more*
  visible. Redraw the whole segment fresh.
- **A drawn line does not shake.** Watch anyone ink: the stroke is smooth. What
  varies between one mark and the next is where it landed, how hard they leaned,
  and a slight bow across the whole arc, never a wobble travelling along it.
  Physiological tremor is real and is measured in tens of microns; at the scale
  a drawing is looked at it is invisible. Rendering tremor is the loudest way to
  make a line read as a beginner's.
- **One contour, one stroke.** Chaining short segments end to end so they merely
  abut leaves a step at every join, because each carries its own placement error.
  A long contour really is laid in several passes, but they overlap *along the
  whole run*, retracing, and do not butt. **A change of weight is the only good
  reason to lift the pen**, and even then the two strokes should meet where both
  are at their thinnest, so the taper hides the join.
- **Do not reinforce by doubling.** With an opaque ink, a second pass beside the
  first makes a tramline and not a heavier line. Weight comes from the nib and
  the pressure profile.
- **A closed form is one closed contour.** An eye, a nostril, a vent slot: one
  continuous loop of varying weight, not two arcs meeting at the corners. Arcs
  that meet leave a knuckle at each corner, and the corners of an eye are where
  the subject's line is finest.
- **A heavy line has to be more precise than a fine one, not less.** Weight
  magnifies error. A kink that is invisible at 3px is a lump at 10px, and the
  pressure model makes it worse, because a hand leans into a tight turn and lays
  more ink exactly where the unintended corner is. So a heavy contour carries
  *fewer* control points, spaced further apart, with no direction change you did
  not mean. If a thick stroke looks jagged, take points out.
- A uniform-width mechanical line is **dead** however accurate it is. Variation
  along one continuous stroke is what makes a line look alive.
- For a small enclosed detail such as a nostril, **outline it and fill it**. One
  stroke distorts the shape.
- **A ring is a stroke, not a filled shape.** A tyre, a rim, a chainring, a clock
  bezel, a washer: these are annuli, and filling a closed circle fills the hole
  as well. State the band by running a single wide stroke along its centre line,
  so the stroke's own width is the band's. The same applies to any outline whose
  inside must stay open.
- **A band drawn as a stroke sits on its CENTRE line, and a scan of the subject
  gives you its EDGE.** The two are only the same for a hairline, and the error
  is half the band's width on every side at once. In one test, a tyre whose
  points were taken off the subject's outer silhouette and then drawn as a 24px
  stroke came out 14 to 55px too wide, worst at the bottom of the wheel, where
  both sides are nearly horizontal and the full band lands outside the form.
  Every point was measured correctly and the object was still wrong. So after
  measuring where a band ends, **move the path half a weight inward** before
  drawing it. Anything radiating to that band (spokes, hatching, a joint) stops
  at the new path, not at the old silhouette.
- **A mark that bounds a small pale shape is subtracting from it**, and past a
  certain width it has eaten the shape. An eye is the lid *and* the white
  beneath it, so thickening the lid does not strengthen the eye. It deletes the
  eye, and the expression goes with it while the lid stays exactly where it was
  measured. The same arithmetic applies to a nostril, a highlight, a gap between
  two tubes, or the slot inside a vent. **Where a form is stated by the gap
  between two marks, the gap is the measurement.** Take it off the subject and
  let the marks fall where it puts them, instead of choosing a weight and hoping
  the space survives. Halving one such mark is often the change that brings a
  feature back, and on the page it looks like drawing less.

Economy is a line-quality virtue as well as an editing one: *"the secret to
drawing is not the making of lines, but the elimination of unnecessary lines."*
It takes more skill to render a form in fewer lines than in more, and
over-rendering usually masks weak construction.

## Spotting blacks

Solid blacks are **placed**, not shaded. They separate figure from ground, set
depth, lead the eye, set mood, and unify scattered shapes into one read.

**Distribution is deliberately uneven**: a little black on most things, a lot on
some, a little on objects of interest. An even scatter reads as noise;
concentrated masses read as intentional.

**Three values across three planes.** Assign black, mid and white one each to
foreground, middle ground and background, and vary which gets which from panel
to panel to change what carries the weight. Never give two objects on different
depth planes the same value.

**Contrast tension**: leave small islands of white inside a black mass, or drop
small black accents into a large empty area. The local interruption pulls the eye
harder than a large uniform black does.

If a finished panel looks flat and grey when squinted, add a real black anchor
**and** a real white breathing space. More mid-tone detail will not fix it.

## Hatching and texture, by hand

On a subject whose look is fine ink (an engraving, a pen drawing, an old printed
illustration), the hatching carries the shading, the texture of each material and
most of what makes it look drawn. Flats with an outline and no hatching read as a
colouring-book copy of it, however well they are placed.

**Measure, then write.** For each hatched region:

1. Box it and run `check.py subject.png --hatch x,y,w,h`. It prints the share of
   the box covered by line marks and, per group of parallel marks, its angle (0
   horizontal, 90 vertical, 45 a `/`), the spacing between neighbours, the
   typical length and width, and the middle half of each range. Pale lines cut
   into a dark (feather shafts on a black wing, light grain on a dark rock) are
   read with `--light`.
2. Write the group into the part's `parts.json` entry as `"hatch": {"angle",
   "spacing", "length"}`, one entry per group, so `--linework` can check it.
3. Read the actual lines off a `--zoom` or a `--scan` across the group: where
   each line starts and ends. Then write each hatch line as its own `stroke`,
   on its own line of `draw.py`, with its own two or three measured points. Vary
   length and spacing within the measured ranges, as a hand does: no two lines
   the same length, no two gaps equal.
4. Re-run `--hatch` with `--ref drawing.png`. It flags (`<<`) a group missing,
   an angle more than 20° off, spacing off by more than half, or coverage under
   half the subject's.

The instrument prints numbers only. Nothing turns a group into strokes, and a
loop or comprehension that does is a generated mark, refused by `pen.write`. A
hatched region costing fifty or a hundred lines of `draw.py` is expected.

**Indicate; do not fill.** A hand does not hatch a whole surface evenly, and
neither should you. Hatching is kept affordable the way illustrators keep it
affordable:

- **At the edges and the turns.** Put the texture where the form turns away and
  along the shadow edge, and let it thin out and stop as the surface comes into
  the light. A few marks at the edge of a roof or a field of grass say the whole
  surface is tiled or grassy [read: Guptill, *Rendering in Pen and Ink*].
- **Near the centre of interest.** Spend the densest groups there and thin them
  with distance from it, as with every other kind of detail.
- **One group per plane.** Each plane of the form gets its own group, at its own
  angle. Where the plane turns, the group changes direction or curves round the
  form. A single angle across several planes flattens them into one.
- **Anchor each line in a dark.** Start it at the shadow edge or the contour and
  run it out into the light (`tone.md`), so the group has one hard edge and one
  ragged one.

**Line quality inside a group:**

- **Bad**: all hatch lines the same length, intersecting at right angles. This
  reads as a mechanical mathematical pattern.
- **Also bad**: two layers nearly parallel, which produces a moiré.
- **Good**: varied lengths, some short and broken, getting heavier as they merge
  toward a black; lines curving *around* the form to imply volume.
- A hatch line is a finer weight than the contour it sits against, and tapers at
  its free end (`lead=`/`tail=` on a `brush` or `marker`). The measured width is
  the target.

Texture that is not hatching (a rock's cracks, bark, the dashes of a stone wall)
follows the same rules: measure the marks' direction, length and spacing with
`--hatch`, write each mark, indicate at the edges and let it thin out.

## The inking pass

1. **Fix the light source.** Everything else depends on it.
2. **Ink the contours of the big shapes first**, applying light-side-thin /
   shadow-side-heavy as you go. Every later decision is placed relative to these.
3. **Establish depth** by contour weight per plane (heavy foreground, medium
   middle, fine background) before adding any other information.
4. **Spot the blacks as a planning decision while inking contours**: mark every
   area destined to be solid, but do **not** fill yet.
5. **Inking is not tracing.** Correct obvious errors in the underdrawing instead
   of reproducing them faithfully. Viewing the page mirrored defeats habituation
   and makes proportion errors visible.
6. **Feather and hatch** to soften hard black edges and add volume. Know what
   each mark is for; do not copy the pencil's rough marks literally.
7. **Erase all pencil, then fill the blacks.** Filling after erasing keeps them
   dense; filling first muddies them.
8. **Background, texture and effects last**, on top of the fixed contour-and-black
   structure, so they respect the hierarchy instead of competing with it.
9. **Final pass**: remove stray marks. Neatness counts even on a rush job.
