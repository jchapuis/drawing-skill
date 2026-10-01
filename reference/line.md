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

## Cross-hatching

- **Bad**: all hatch lines the same length, intersecting at right angles. This
  reads as a mechanical mathematical pattern.
- **Also bad**: two layers nearly parallel, which produces a moiré.
- **Good**: varied lengths, some short and broken, getting heavier as they merge
  toward a black; lines curving *around* the form to imply volume.

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
