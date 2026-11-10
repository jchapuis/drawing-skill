# Redrawing a generated image

The output of a diffusion model is a picture *of* a drawing. It differs from
both a photograph and a drawing in ways that change how you read and check it,
and it is a common subject, usually with the brief *make this look drawn rather
than generated*. Redrawing a photograph (see `photograph.md`) means finding the
form under an appearance. Redrawing a generated image means **finding a form
that was never there**, and not copying what makes it look machine-made.

## Contents

- What it hands you free
- Its edges invert the rule in `scene.md`
- The line has almost no hierarchy, and your instrument may not reach its floor
- What must **not** be copied
- Structure that does not survive measurement
- Ask where the boundary EXISTS, not where to break the line
- Measure the object, never a box round it

## What it hands you free

A generated flat-cel source is the most measurable subject you will get. Use
that at the reading stage.

- **An exact palette.** The regions are flat and the palette is small. Sample
  it and the ground, and every flat has a right answer instead of a judgement:
  `method.md`'s "measure the ground" becomes a lookup. Record **where** each
  entry was sampled. If two samples inside one region disagree, one of them
  landed on something else (the measuring error described below).
- **A posterised read.** `scene.md`'s S0 asks you to posterise the source
  and measure the masses. Here you can do better: classify every pixel to its
  nearest palette entry and print the picture as one character per block, in
  the picture's own coordinates. The bands, the depth planes and every object's
  extent then show in one look. Do it **before** the inventory: it is the
  cheapest reading tool here, and the only one that shows the design and the
  coordinates together. The same classification finds gaps
  in the palette: pixels far from every entry clump where a flat is missing and
  scatter where they are grain (`trace.py` prints the share and the largest
  clumps). In one case this found two missing flats, a shade on a fork and a
  brown horizon line.
- **Boundaries you can measure instead of judge.** A row or column scan returns
  exact runs, such as `field:465-486`, so every landmark can be a boundary
  between two named colours at a stated coordinate. Use a block map to read
  *shape* only. Never place a point from it: a block is as imprecise as it is
  wide.

## Its edges invert the rule in `scene.md`

`scene.md` says most junctions in a scene should be lost, and that giving each
object a closed contour breaks a picture. **Find out which kind of source you
have before applying that here.** In a flat-cel generated image, nearly every
boundary between two *different* flats carries its own dark line. The question
to ask of each edge becomes:

> **Is this edge stated exactly once?**

The typical failure changes too, from a drawing that sticks flat to the picture
plane to a field of crossing loops. `--doubled` is the gate,
and the shared-vertex construction in `method.md` is the fix.

This applies to a massed object too. When a massed shape in such a source has a
line on its boundary, keep that line, stated once, at the heaviest weight: it is
the source's style, not emphasis. Massing still skips the object stages, the
sub-forms and every interior mark. If you leave the mass without its line, that
is a departure from the source; record it in `reading.md`.

Where two regions of the **same value** meet, such as two dark animals or a
black glove against black shorts, the edge really is lost, and drawing a line
there invents an edge the subject does not have. **Decide this by measuring the
two flats, not by naming the two objects.** An object whose neighbours all share
its value has no silhouette for most of its length, and a closed contour round it
is two-thirds made-up edge.

The reverse error also happens. If you test an edge only against the backdrop,
in a window that leaves out the neighbouring objects, you can call it lost when
it is really an edge against those neighbours. Drawing nothing there leaves a
dark field with no object in it.

## The line has almost no hierarchy, and your instrument may not reach its floor

Measure the source's own weight span and expect it to be narrow: `line.md`'s
2–3× flat-cel figure, not a comic's 8–10×. Two traps:

- **Measure true lines only**: runs bounded by non-ink on *both* sides and under
  a stated maximum width. Counting every dark run counts filled regions as lines,
  inflates the heavy end of the weight swatch by about half, and then seems to
  justify a heavy contour everywhere.
- **Measure the finest line your renderer can draw.** A renderer with a minimum
  stroke width cannot reach the finest weight of a source drawn at higher
  resolution. When it cannot, decide in writing what the bottom of your range now
  means and re-set the weights. Otherwise they match on paper and fall short on
  the page.

## What must **not** be copied

This is the reason to redraw at all. A generated image carries, in its surface, several things that
`method.md`'s principles 7 and 8 (vary execution, never mirror) forbid:

- **repeated elements that are one element stamped**, such as a herd, a crowd, a
  row of windows or a pair of hands;
- **bilateral symmetry** that a real instance would not have;
- **curves with no variation along them**, and weight that never changes for a
  reason.

Copying these reproduces the fault, yet every check in this kit asks whether
the drawing agrees with the subject. So **write down at stage 0 which properties of the subject you are
departing from, and in which direction, and put them in the acceptance list.**
Otherwise the departure later looks like an error, and a correction round puts
the stamp back.

For repeated animals, six drawn the same way are one animal stamped six times.
What prevents it is that no two share the same *amount* of turn; it is not
enough that no two neighbours face the same way (`quadruped.md`). The herd case
has been measured. That generated images in general carry the three faults
listed above rests on that one case so far, so check your source for each of
them instead of assuming it.

## Structure that does not survive measurement

A generated picture is plausible locally and unchecked globally: posts that do
not share a spacing, tubes that do not meet, a wrong count. So an inventory read
off one will contain **entries for objects that are not there**, because your
reading fills in what the category implies where the picture only hinted.

For example, an inventory recorded three fence uprights, while a scan for dark
vertical runs found two at every row and clean ground where the third should
be. An entry for an absent object carries into the block-in, the flats, the
overlaps table and the depth order, and reaches a critic as a drawn object
nobody can fault.

So run `scene.md`'s count against **scan data, not your impression**, before the
block-in. It is the one check that tests the reading instead of the marks.

## Ask where the boundary EXISTS, not where to break the line

Occlusion in a flat-cel source has an exact test. The tempting method is to draw
the background line all the way and break it wherever something seems to be in
front, which is guesswork. Work the other way instead. **A boundary between two flats exists
exactly where one flat is on one side of it and the other flat is on the other.**
Walk the line's own path and check, at every step, whether the subject has the
upper value just above it and the lower value just below. Where both hold, the
boundary is visible. Everywhere else something covers it, and you do not need to
know what.

For example, a horizon drawn as a full-width line with two guessed breaks turned
out to be visible over **two short runs totalling 85px of a 928px span**. Animals,
a figure and a limb covered the rest, so the line as first drawn was mostly an
edge the subject does not have.

The same scan also confirms junctions recorded elsewhere. In that picture, one
of the two visible runs was exactly the wedge of background between a forearm
and a torso, which the parts list had recorded as a negative shape. **When two
independent readings find the same gap, that confirms both**, at no extra cost.

Two cautions:

- **A dark run is not the line you are looking for.** A scan for "is there dark
  here" cannot tell a background line from the dark object standing in front of
  it, so it reports the line visible along its whole length, even where it is
  most hidden. Test for the two *values*, not for ink.
- **Where a contour and an occluder land on the same path, move the contour.**
  The occluder is what was measured, and the contour is what can be re-placed.
  Two marks running together read as one line drawn twice, whatever their depth
  order says.

## Measure the object, never a box round it

The most common error on this kind of subject is **measuring a region that is
not the named object.** It takes many forms:

- a bounding box mostly full of background;
- a scan column run down *through* the figure;
- a sample that landed on a neighbouring pale object;
- connected components over a colour mask, where the ink network joins every dark
  thing into a single blob;
- a rectangular mask over a cone;
- point probes on a 4px outline;
- counting all the ink in a row instead of one band's.

Flat regions make it worse: a wrong sample comes back as a clean palette entry,
so nothing shows it came from the wrong place.

What works on a flat-cel subject is to **isolate by the ground, not by the
object.** Scan each column for a long run (say 45px or more) of anything that is
*not* the background flat, and take the object as the union of those runs.
Thresholding on darkness fails, because every ink line is dark and the ink
network is continuous, so one component swallows the whole frame. A long-run
test discards every thin line by design and keeps only the filled body of a
form. Measure the background's own value first, since everything here is judged
against it.

Four cheap fixes:

- **isolate the thing**: render it alone (`--only <tag>`) instead of reasoning
  about it in place;
- **sample interiors, not boxes**;
- **sample along an object's medial axis**, not its bounding rectangle;
- **always include a control span whose answer you already know.** This is the
  fix that actually catches the error. A probe that gets the control right and
  the object surprising is a measurement. A probe that gets the control wrong
  was never measuring the object, and its number is worthless.
