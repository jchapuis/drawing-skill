# Redrawing a generated image

A diffusion model's output is neither a photograph nor a drawing. It is a picture
*of* a drawing, and it differs from both in ways that change how you read and
check it. It is also a common subject for drawing, usually with the brief
*make this look drawn rather than generated*, so the differences are stated here.

The brief matters. Redrawing a photograph means finding the form under an
appearance. Redrawing a generated image means **finding the form that was never
there**, and declining to copy the things that make it read as machine-made.

For a photograph as subject, see `photograph.md`.

## What it hands you free

A generated flat-cel source is the most *measurable* subject you will get, and
the reading stage should use that instead of squinting at it.

- **An exact palette.** The regions are flat and the palette is small. Sample it
  and the ground, and every flat has a right answer instead of a judgement.
  `method.md`'s "measure the ground" becomes a lookup. Record **where** each
  entry was sampled. Two points inside one region that disagree mean one of them
  landed on something else, which is the measuring failure described below,
  caught early and cheaply.
- **A posterised read.** `scene.md`'s step 0 asks you to posterise the source and
  measure the masses. Here you can do better. Classify every pixel to its
  nearest palette entry and print the picture as one character per block, in the
  picture's own coordinates. The bands, the depth planes and every object's
  extent become readable in one look. Do it **before** the inventory, not after.
  It is the cheapest reading instrument available for this kind of subject, and
  the only one that shows the design and the coordinates at the same time. The
  same classification finds the palette's gaps: pixels far from every entry clump
  where a flat is missing and scatter where it is grain (`trace.py` prints the
  share and the largest clumps). Two missing flats were found this way in one case: a shade on a fork and a brown
  horizon line.
- **Boundaries you can measure instead of judge.** A row or column scan returns
  exact runs, such as `field:465-486`, and not "about here". Every landmark can
  be a boundary between two named colours at a stated coordinate. A block map is
  for reading *shape*. Never place a point off it, because a block is as imprecise
  as it is wide.

## Its edges invert the rule in `scene.md`

`scene.md` says most junctions in a scene should be lost, and that a closed
contour per object is what breaks a picture. **Establish which kind of source you
have before you apply that here.** In a flat-cel generated image nearly every
boundary between two *different* flats carries its own dark line. The question
stops being *is this edge found or lost* and becomes:

> **Is this edge stated exactly once?**

The failure mode moves with it, from a drawing that sticks to the picture plane
to a drawing that is a field of crossing loops. `--doubled` is the gate, and the
shared-vertex construction in `method.md` is the fix.

This applies to a massed object too. When a massed shape in such a source has a
line on its boundary, keep it, stated once, at the heaviest weight, because the
line is the source's style and not emphasis. Massing still withholds the object
stages, the sub-forms and every interior mark. Leaving the mass bare is a
departure from the source and belongs in `reading.md` as one.

Where two **same-valued** regions abut, such as a dark animal against a dark
animal or a black glove against black shorts, the edge is genuinely lost, and
drawing one there invents an edge the subject does not have. **Decide it by
measuring the two flats, not by naming the two objects.** An object whose
neighbours are all its own value has no silhouette for most of its length, and a
closed contour round it is two-thirds an edge that is not there.

Read that in both directions. An edge missing in *one* instrument's field of view
is not necessarily missing. If you test an edge only against the backdrop, in a
window that excludes the neighbours, you can declare it lost when it is really an
edge against the neighbouring objects. Drawing nothing there then leaves a dark
field with no object in it.

## The line has almost no hierarchy, and your instrument may not reach its floor

Measure the source's own span and expect it to be narrow: `line.md`'s 2–3×
flat-cel figure, not a comic's 8–10×. Two traps:

- **Measure true lines only**: runs bounded by non-ink on *both* sides and under a
  stated ceiling. Counting every dark run counts filled regions as lines and
  inflates the heavy end of the weight swatch by roughly half, which then
  licenses a heavy contour everywhere.
- **Measure your own instrument's floor.** A renderer with a minimum stroke width
  cannot reach the finest weight of a source drawn at higher resolution. When it
  cannot, that finest weight is *unreachable*. Decide in writing what the bottom
  of your range now means and re-set the weights, instead of matching them on
  paper and quietly missing them on the page.

## What must **not** be copied

A photograph has no equivalent of this section, and it is the reason the redraw
exists at all. A generated image carries, as part of its surface, several of the
things principles 7 and 8 forbid:

- **repeated elements that are one element stamped**, such as a herd, a crowd, a
  row of windows or a pair of hands;
- **bilateral symmetry** a real instance would not have;
- **curves with no variation along them**, and weight that never changes for a
  reason.

Copying these faithfully reproduces the fault. *Faithful* is the default stance
of every check in this kit, since they all ask whether the drawing agrees with
the subject. So **write down at stage 0 which properties of the subject you are
departing from, and in which direction, and put them in the acceptance list.**
Without that, the departure is indistinguishable from an error later, and a
correction round puts the stamp back.

For repeated animals, six drawn the same way are one animal stamped six times.
What prevents it is not that no two neighbours face the same way but that no two
share the same *amount* of turn (`quadruped.md`). The herd case is measured. The general
claim about generated sources is so far a hypothesis with one instance behind it.

## Structure that does not survive measurement

A generated picture is locally plausible and globally unchecked: posts that do
not share a spacing, tubes that do not meet, a count that is wrong. So an
inventory read off one will contain **entries for objects that are not in it**.
The reading supplies what the category implies where the picture only gestured.

Measured: an inventory recorded three fence uprights, while a scan for dark
vertical runs found two of them at every row and clean ground where the third
was. An entry for an absent object propagates into the block-in, the
flats, the overlaps table and the depth order, and it reaches a critic as a drawn
object whose origin nobody can fault.

So run `scene.md`'s count against **scan data rather than against the
impression**, and run it before the block-in. It is the one check pointed at the
reading and not at the marks.

## Ask where the boundary EXISTS, not where to break the line

Occlusion in a flat-cel source has an exact test, and it is not the one you will
reach for first. The tempting method is to draw the background line all the way
and then break it wherever something seems to be in front. That is judgement
about a region where you have already decided the answer.

The reliable method inverts it. **A boundary between two flats exists exactly
where one flat is on one side of it and the other is on the other.** Walk the
line's own path and ask, at every step, whether the subject holds the upper
value just above it and the lower value just below. Where both hold, the
boundary is visible. Everywhere else something covers it, and you do not need to
know what.

In one picture, a horizon drawn as a full-width line with two breaks guessed into
it turned out to be visible over **two short runs totalling 85px
of a 928px span**, and the rest was covered by animals, a figure and a limb. The
line as first drawn was mostly an edge the subject does not have.

The same scan also recovers junctions the inventory names independently. In that
picture, one of the two visible runs was exactly the wedge of background showing
between a forearm and a torso, which the parts list had recorded separately as a
negative shape. **Two readings of one gap arriving from opposite directions is
the check**, and it is free, because you ran the scan for something else.

Two cautions:

- **A dark run is not the line you are looking for.** Scanning for "is there dark
  here" cannot tell a background line from the dark object standing in front of
  it. It will report the line visible along its whole length exactly where it is
  most thoroughly hidden. Test for the two *values*, not for ink.
- **Where a contour and an occluder land on the same path, move the contour.**
  The occluder is the thing that was measured, and the contour is the thing that
  can be re-placed. Two marks running together read as one line drawn twice,
  whatever their depth order says.

## Measure the object, never a box round it

One error recurs more than any other on this kind of subject: **measuring a
region that is not the object named.** It takes many forms:

- a bounding box mostly full of background;
- a scan column run down *through* the figure;
- a sample that landed on a neighbouring pale object;
- connected components over a colour mask, where the ink network joins every dark
  thing into a single blob;
- a rectangular mask over a cone;
- point probes on a 4px outline;
- counting all the ink in a row instead of one band's.

Flat regions make it worse. A wrong sample comes back as a clean, confident
palette entry and not as noise, so nothing in the answer signals that it came
from the wrong place.

The recipe that works on a flat-cel subject is to **isolate by the ground, not by
the object.** Scan each column for a long run (say 45px or more) of anything that
is *not* the background flat, and take the object as the union of those runs.
Thresholding on darkness fails because every ink line in the picture is dark and
the ink network is continuous, so one component swallows the whole frame. A
long-run test throws away every thin line by construction and keeps only the
filled body of a form. Measure the background's own value first, since everything
here is judged against it.

Four cheap fixes:

- **isolate the thing**: render it alone (`--only <tag>`) instead of reasoning
  about it in place;
- **sample interiors, not boxes**;
- **sample along an object's medial axis**, not its bounding rectangle;
- **always include a control span whose answer you already know.** This is the fix
  that actually catches the error. A probe that returns the expected value for the
  control and a surprising one for the object is a measurement. A probe that gets
  the control wrong was never measuring the object, and its surprising number is
  worth nothing.
