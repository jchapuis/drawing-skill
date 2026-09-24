# Redrawing a generated image

A diffusion model's output is neither a photograph nor a drawing. It is a picture
*of* a drawing, and it differs from both in ways that change what the ladder is
for. It is also, in practice, the subject this skill is pointed at most often —
usually with the brief *make this look drawn rather than generated* — so the
differences are worth stating rather than rediscovering.

The brief matters. Redrawing a photograph means finding the form under an
appearance. Redrawing a generated image means **finding the form that was never
there**, and declining to copy the things that make it read as machine-made.

## What it hands you free

A generated flat-cel source is the most *measurable* subject you will get, and
the reading stage should exploit that rather than squint at it.

- **An exact palette.** The regions are flat and the palette is small. Sample it
  and the ground, and every flat has a right answer instead of a judgement —
  `method.md`'s "measure the ground" stops being a discipline and becomes a
  lookup. Record **where** each entry was sampled: two points inside one region
  that disagree mean one of them landed on something else, and that is the whole
  measuring failure below arriving early and cheaply.
- **A posterised read, for free.** `scene.md`'s step 0 asks you to posterise the
  source and measure the masses. Here you can do better than posterise: classify
  every pixel to its nearest palette entry and print the picture as one character
  per block, in the panel's own coordinates. The bands, the depth planes and
  every object's extent become readable in one look. Do it **before** the
  inventory, not after — it is the cheapest reading instrument available on this
  class of subject, and the only one that shows the design and the coordinates at
  the same time.
- **Boundaries you can measure instead of judge.** A row or column scan returns
  exact runs — `field:465-486`, not "about here". Every landmark can be a
  boundary between two named colours at a stated coordinate. A block map is for
  reading *shape*; never place a point off it, because a block is as much slop as
  it is wide.

## Its edges invert the rule in `scene.md`

`scene.md` says the majority of junctions in a scene should be lost, and that a
closed contour per object is what breaks a picture. **Establish which kind of
source you have before you believe that here.** In a flat-cel generated image
nearly every boundary between two *different* flats carries its own dark line, so
the question stops being *is this edge found or lost* and becomes:

> **Is this edge stated exactly once?**

The failure mode moves with it — from a drawing that sticks to the picture plane,
to a drawing that is a field of crossing loops. `--doubled` is the gate, and the
shared-vertex construction in `method.md` is the fix.

That reaches the welded tier too. A welded shape in such a source keeps the line
its boundary carries — stated once, at the far end of the weight ladder — because
the line is the source's style, not emphasis; what welding still withholds is
the object ladder, the sub-forms and every interior mark. Leaving the mass bare
is a departure from the source, and belongs in `reading.md` as one.

Where two **same-valued** regions abut — a dark animal against a dark animal, a
black glove against black shorts — the edge is genuinely lost, and drawing one
there invents an edge the subject does not have. **Decide it by measuring the two
flats, not by naming the two objects.** An object whose neighbours are all its
own value has no silhouette for most of its length; a closed contour round it is
two-thirds an edge that is not there. [bought: drawing]

Read that in both directions. Absence of a boundary in *one* instrument's field
of view is not absence of an edge — an edge tested only against the backdrop, in
a window that excluded the neighbours, was declared lost when it was really an
edge against the neighbouring objects, and drawing nothing there produced a dark
field with no object in it. [bought: drawing]

## The line has almost no hierarchy, and your instrument may not reach its floor

Measure the source's own span and expect it narrow — `line.md`'s 2–3× flat-cel
figure, not a comic's 8–10×. Two traps, both paid for:

- **Measure true lines only** — runs bounded by non-ink on *both* sides and under
  a stated ceiling. Counting every dark run counts filled regions as lines and
  inflates the top of the ladder by roughly half, which then licences a heavy
  contour everywhere. [bought: drawing]
- **Measure your own instrument's floor.** A renderer with a minimum stroke width
  cannot reach the finest rung of a source drawn at higher resolution. When it
  cannot, the finest rung is *unreachable* and the ladder has to be **re-pitched**
  — decide in writing what the bottom of your range now means — rather than
  matched on paper and quietly missed on the page. [bought: drawing]

## What must **not** be copied

This section has no equivalent for a photograph, and it is the reason the redraw
exists at all. A generated image carries, as part of its surface, several of the
things principles 7 and 8 forbid:

- **repeated elements that are one element stamped** — a herd, a crowd, a row of
  windows, a pair of hands;
- **bilateral symmetry** a real instance would not have;
- **curves with no variation along them**, and weight that never changes for a
  reason.

Faithfully reproducing these reproduces the fault, and *faithful* is the default
posture of every check in this kit: they all ask whether the drawing agrees with
the subject. So **write down at stage 0 which properties of the subject you are
departing from, and in which direction, and put them in the acceptance list.**
Without that the departure is indistinguishable from an error later, and a
correction round dutifully puts the stamp back.

The herd case is measured — six animals drawn the same way is one animal stamped
six times, and what prevents it is not that no two neighbours face the same way
but that no two share the same *amount* of turn (`quadruped.md`) [bought:
drawing]. The general claim about generated sources is so far a hypothesis with
one instance behind it. [read: hypothesis]

## Structure that does not survive measurement

A generated picture is locally plausible and globally unchecked: posts that do
not share a spacing, tubes that do not meet, a count that is wrong. So an
inventory read off one will contain **entries for objects that are not in it** —
the reading supplies what the category implies where the picture only gestured.

Measured: an inventory recorded three fence uprights; scanning for dark vertical
runs found two of them at every row, and clean ground where the third was. An
entry for an absent object propagates into the block-in, the flats, the
interfaces table and the depth order, and arrives at a critic as a drawn object
with a provenance nobody can fault. [bought: drawing]

So run `scene.md`'s census against **scan data rather than against the
impression**, and run it before the block-in. It is the one check pointed at the
reading rather than at the marks.

## Ask where the boundary EXISTS, not where to break the line

Occlusion in a flat-cel source has an exact test, and it is not the one you will
reach for. The tempting method is to draw the background line all the way and
then break it wherever something seems to be in front — which is judgement, and
judgement about a region you have already decided the answer for.

The reliable method inverts it. **A boundary between two flats exists exactly
where one flat is on one side of it and the other is on the other.** So walk the
line's own path and ask, at every step, whether the subject holds the upper
value just above it and the lower value just below. Where both hold, the
boundary is visible; everywhere else something covers it, and you do not need to
know what. [bought: drawing]

Measured on one panel, a horizon drawn as a full-width line with two breaks
guessed into it turned out to be visible over **two short runs totalling 85px of
a 928px span** — the rest covered by animals, a figure and a limb. The line as
drawn was mostly an edge the subject does not have.

The same scan also recovers junctions the inventory names independently: one of
those two runs was exactly the wedge of background showing between a forearm and
a torso, which the parts list had recorded separately as a negative shape. **Two
readings of one gap arriving from opposite directions is the check** — and it is
free, because you ran the scan for something else.

Two cautions, both paid for:

- **A dark run is not the line you are looking for.** Scanning for "is there
  dark here" cannot tell a background line from the dark object standing in
  front of it, and it will report the line visible along its whole length
  precisely where it is most thoroughly hidden. Test for the two *values*, not
  for ink.
- **Where a contour and an occluder land on the same path, move the contour.**
  The occluder is the thing that was measured; the contour is the thing that can
  be re-placed. Two marks running together read as one line drawn twice whatever
  their depth order says.

## Measure the object, never a box round it

One error recurs more than any other on this class of subject: **measuring a
region that is not the object named.** It arrives in many disguises — a bounding
box mostly full of background; a scan column run down *through* the figure; a
sample that landed on a neighbouring pale object; connected components over a
colour mask, where the ink network joins every dark thing into a single blob; a
rectangular mask over a cone; point probes on a 4px outline; counting all the ink
in a row instead of one band's. [bought: drawing]

Flat regions make it worse rather than better, because a wrong sample comes back
as a clean, confident palette entry rather than as noise. There is nothing in the
answer to signal that it came from the wrong place.

The recipe that does work on a flat-cel subject: **isolate by the ground, not by
the object.** Scan each column for a long run — say 45px or more — of anything
that is *not* the background flat, and take the object as the union of those
runs. Thresholding on darkness fails because every ink line in the picture is
dark and the ink network is continuous, so one component swallows the whole
frame; a long-run test throws away every thin line by construction and keeps
only the filled body of a form. Measure the background's own value first, since
everything here is judged against it.

Four fixes, all cheap:

- **isolate the thing** — render it alone (`--only <tag>`) rather than reasoning
  about it in place;
- **sample interiors, not boxes**;
- **sample along an object's medial axis**, not its bounding rectangle;
- **always include a control span whose answer you already know.** This is the
  one that actually catches it. A probe that returns the expected value for the
  control and a surprising one for the object is a measurement; a probe that gets
  the control wrong was never measuring the object, and its surprising number is
  worth nothing.
