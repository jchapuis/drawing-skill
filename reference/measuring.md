# Measuring, block-in, and checking

The block-in is the stage that most determines whether a drawing looks trained
or amateur, and it is the stage most often skipped.

## Why straights

A straight line has an **angle and a length you can verify** against the subject.
A curve has neither — it can only be judged by whether it looks right, which is
exactly the judgement not yet worth trusting. The block-in converts the
unmeasurable question *"is this curve correct?"* into the measurable one *"is
this polygon correct?"*.

A curve drawn directly invites drawing what you expect rather than what is there,
and comes out loose and bulbous. That is the blobby amateur failure, and it has
one cause.

## The envelope

The largest single shape enclosing the whole subject. Everything else fits
inside it.

1. Draw a reference box touching all four extremes of the subject; reproduce that
   box at matching scale on the canvas first.
2. Plot the **four extremity points** — topmost, bottommost, leftmost, rightmost.
3. Connect them with as few straight lines as possible. **≤6 sides** for a full
   figure; worked examples start a head with about 5.
4. Subdivide: find the next-largest direction-change points and add straight
   chords between them.
5. Repeat in passes, each adding shorter and more numerous straights, until the
   polygon reads as the full form.
6. Verify every angle against the subject before committing it.

There is **no published segment count for a finished block-in** — only the ≤6-side
starting envelope. Do not invent one.

The ≤6 sides is a starting heuristic, not a limit. A subject with more genuine
direction changes than that — a helmet on a head has ten — needs a vertex at each
one, because the point of the envelope is that it *contains* the subject. Check
it: a chord drawn across a convex run cuts inside the form, and 25px of a helmet
outside the envelope is a failed gate, not an acceptable simplification.

## Sighting by pixels

When the subject is an image file rather than a thing in front of you, sight it by
reading it. Walk a row or a column and record where the flat colours change: that
returns the same information as a held-up pencil and a plumb line, with none of
the estimation. Trace a mass by taking, column by column, the first and last pixel
belonging to it.

Two cautions, both of which cost real time here. A run-length reading crossing
two features at once attributes both to whichever it names first — a moustache
measured through the mouth line comes back 12px too deep — so **window the scan to
one feature at a time**. And a colour that classifies to the nearest palette entry
will silently fold a near-black navy into a dark grey; check the raw values of
anything structurally important before trusting the label.

## Reading a value off the subject

Sampling a colour is a scan like any other, and it has one failure that is worth
a section because it is silent and it is expensive.

**Take the mode of a clean interior patch. Never a small median.** A median over
an 8x8 window sitting anywhere near a contour returns *the contour's* value, and
it returns it as a confident number with no sign that anything is wrong. Measured
here: a shoe's body sampled that way read L=37.9 and a chainring L=25.9, from
which followed a diagnosis that the two shared a value they should not have,
four edits to fix it, and a revert. Re-read as the histogram mode of a patch
placed wholly inside each form, the same two are **L=60 and L=59** — the same
value, which is what the panel already had and what the subject actually does.

So:

- **Place the window inside the form, not on it**, and check what is in it before
  believing what comes out. A patch that can contain an edge will eventually
  contain one.
- **Mode, not median, and report the sample count.** A mode over a few hundred
  interior pixels is stable; a median over sixty is a coin toss weighted by
  whatever line crosses the corner.
- **Sample every part of a comparison the same way in the same pass.** The error
  above survived because the shoe and the chainring were sampled together and
  were wrong together, so they stayed plausible relative to each other.
- A value difference you cannot see at 4x is not a value difference. Look at the
  crop before acting on the number, and if the eye and the number disagree,
  re-sample before believing either.
- **Two dark values a few levels apart cannot be separated by a darkness
  threshold** [bought: drawing]. A shell and the webbing lying on it, seven levels
  apart, both fall under any luminance cut called "ink", and the scan then reports
  a silhouette several times its real width — confidently, with nothing to say it
  is wrong. Sample the mode of each form separately and classify by distance to
  those modes; no choice of cut does it.
- **A box whose edge lands exactly on its scan window's edge is the window, not
  the part** [bought: drawing]. Flag every measurement that touches its own window
  and re-scan wider before believing it — on a first pass roughly a third of them
  are the window. The same fault in colour form: a mask loose enough to admit the
  ground silently clips every box that reaches the subject's edge.

## Measurement gives position, never shape

This is the limit of the whole method, and it is worth stating plainly because
accurate measurement makes a drawing feel finished when it is not.

**Sampling an edge every few pixels writes the sampling noise into the
silhouette.** Thirteen measured points along a moustache produce thirteen small
inflections, and the result reads as a lumpy slab where the subject reads as a
clean crescent. A shape is **constructed** — few deliberate control points, one
continuous curvature, a decision about where it is thickest and where it comes to
a point — and only its *extremes* come from measurement.

The same failure at the level of a whole feature: scanning for a helmet's vents
finds the coloured area inside each slot and never the slot, so the drawing gets
seven short floating blobs instead of a radial fan cutting the crown edge. When a
feature has an underlying construction — a fan, a cylinder, a repeating rhythm —
**build the construction and check it by looking**, rather than tracing what the
scan returned.

Overlay checking cannot catch any of this: at 1:1 a lumpy shape and a clean one
occupy the same box. Only the detail check at 4x shows it.

## Which instrument gives a coordinate, and which settles a proportion [bought: drawing]

**A look places nothing.** On one 4x panel three instruments were used to read
positions, and they ranked cleanly:

- **Points read by eye off a gridded or ticked crop came out 30-60px off** — a
  helmet's right edge, a thigh, a forearm's upper edge. A grid is fine for
  saying which structure is where; it is not a coordinate.
- **A scan across the subject** — `check.py --scan x,y,w,h --side S`, or a
  column or row of its dark runs — fixed every one of those, and is the only
  source for a point typed into `draw.py`.
- **Judging proportion from a side-by-side misled in both directions.** A drawn
  head *looked* 10% large with its chin 70px low; measured on the same image,
  the chin was 6px off and the helmet 3% wide. The jersey band looked broken
  where the subject's was continuous, and the subject's was broken too. A
  person reading the same thumbnails made the same kind of error, half right
  and half wrong on each item. Every case was settled by a scan or by
  `--overlay --box`, never by looking harder. So an item raised by eye —
  your own, a critic's, a person's — is a hypothesis until a number on subject
  and drawing reproduces it, and no mark moves before that.

**A thick line can read as two.** A 40px rim line in a magnified crop looked
like a rim and a separate brim, and was drawn as two strokes 30px apart —
which `--doubled` cannot see, because they do not overlap. A scan across it
shows one dark run per column in the subject and two in the drawing (`runs
1|2`).

### The outline is not the likeness; interior lines carry it too

A form whose likeness lives in its outline — a face in profile or three
quarters, a nose, a chin — gets an edge scan on the side the silhouette faces:
per row, the outermost non-ground pixel on subject and drawing. It is the only
thing that catches a wrong turn **between** two measured landmarks (a nose
bulb that tucked in 20px early passed a chin check, a width check and
`--masses`).

It is necessary and it is not sufficient. A face passed its outline scan row
by row and still read wrong, because the fault was **inside** the outline: the
nose's ridge line ran diagonally from the brow to the nostril in the subject,
making the nose a wide wedge, and near-vertically down the far edge in the
drawing. No outline instrument can see an interior line. `--overlay --box`
over the focus shows both inks at once — the subject's blue, the drawing's
red, coincident black — and the question for every blue line inside the form
is **which red line is meant to be it, and how far and which way it runs
off**. Answer it for the lines that carry the likeness (ridge, brow, the
mouth's corners, the fold of the cheek) and measure any disagreement with
`--scan`, whose ink columns list the interior runs row by row.

This is a look with a question attached, not a gate with a threshold, on
purpose. Which drawn line corresponds to which subject line is a reading, and
any number built on the two inks — a distance, an overlap share — falls as
more ink is added, which is the wrong direction for a gate to move.

## Landmarks are the block-in's vertices

The landmark method and the straight-line block-in are one operation seen two
ways. A landmark sits where a line changes direction.

- Place the envelope and its strongest outer angles first, then work **inward**.
- Put landmarks at **hard places** — bony points where the skeleton sits close to
  the skin — and at direction changes.
- **Every new landmark is placed relative to one already fixed**, never
  independently by eye.
- **Connect landmarks with straight chords**, never freehand curve.

Why this beats drawing a continuous contour: an unchecked tilted line drifts
toward vertical or horizontal as your perception regularises it, and the error
accumulates with nothing to catch it. Landmarks give discrete, individually
verifiable checkpoints.

## The gate

**No curve exists until the straights have been checked and corrected at least
once.** In an atelier an instructor will refuse to look at curve work before the
block-in is signed off. Hold to that.

Then round the transitions between straights. A curve is only ever as good as the
straight it replaced.

## Sighting and measurement

Comparative measurement uses a unit from the subject and expresses everything
else as a ratio to it. The **head length** is the standard unit; adults run
7.5 heads naturalistically, 8 in the idealised canon.

Procedure:

1. Position so the subject and the drawing are both visible without moving.
2. Extend the arm and **lock the elbow straight every time** — a bent arm changes
   the measurement.
3. Close one eye, collapsing the scene to 2D.
4. Hold the tool perpendicular to the line of sight; align its tip with landmark
   A and slide your thumb to landmark B. That span is the unit.
5. Keeping the thumb fixed, count how many units fit across a larger span.
6. Apply the same locked-arm procedure to the drawing and check the ratio.

**Angles.** Rotate the tool at the wrist until it aligns with the tilted edge,
note which other landmarks that line crosses, then freeze the wrist, turn to the
drawing, and check the same tilt crosses the equivalent points. The **clock face**
is the standard mnemonic — "two o'clock to eight o'clock". There is no
degree-based protocol, and there is **no "two-pencil method"** in the literature;
the real technique is single-tool and sequential.

**Plumb lines.** Hold a true vertical through one landmark and note every other
point it crosses; transfer that relationship and check. Verticals and horizontals
are judged far more reliably than diagonals, which is the whole point. Drop
several plumb lines over a drawing, not one.

## Negative shape

The gap between forms is a shape in its own right. You hold no preconception
about what an odd gap should look like, so you judge it honestly — whereas your
brain silently corrects the "arm" toward the arm you expect.

- Check the **largest** negative shape first, then progressively smaller ones.
- Ask explicitly: too wide? too narrow? does it pinch in too early?
- When a gap is wrong, **fix the positive contour**, not the gap.
- Use it **continuously**, through block-in and into contour — not once at the end.

Because adjacent positive shapes are proportionally coupled, a wrong gap reveals
*relational* errors that are invisible when each element is judged alone.

## Sight-size vs comparative

**Sight-size** fixes the subject, easel and your viewing spot for the whole
session and renders the drawing at the exact apparent size of the subject from
that spot. A direct 1:1 transcription — simpler to teach, directly verifiable,
but rigid and broken by any change of distance.

**Comparative** works at any distance and any scale by expressing everything as
ratios to a chosen unit. Flexible, but each measurement depends on the previous
one, so **early errors compound**.

Sight-size is a transcription; comparative is a translation. Use sight-size when
the setup can stay fixed, comparative when it cannot.

## Working from a reference image

Measure it; do not be impressed by it.

- Sample landmark positions numerically rather than by eye — read the pixel rows
  where the brow, eye, nose base, mouth and chin actually fall, and the width at
  each.
- Express them as ratios and compare against the canonical proportions in
  `head.md`. **The difference is the character** — see "the deviation" under
  Reading the subject in `method.md`.
- Draw in the reference's own coordinate space and pin the render frame, so an
  overlay comparison is exact rather than approximate.
- Never compare from memory. You will silently revert to the symbol you already
  believed.
