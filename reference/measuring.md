# Measuring, block-in, and checking

The block-in decides more than any other stage whether a drawing looks trained
or amateur, and it is the one most often skipped.

## Contents

- Why straights
- The envelope
- Sighting by pixels
- Reading a value off the subject
- Measurement gives position, never shape
- Which instrument gives a coordinate, and which settles a proportion
- Landmarks are the block-in's vertices
- The gate
- Sighting and measurement
- Negative shape
- Sight-size vs comparative
- Working from a reference image

## Why straights

A straight line has an angle and a length you can check against the subject. A
curve has neither: you can only judge whether it looks right, and that judgement
is not yet trustworthy. Blocking in replaces "is this curve correct?", which you
cannot measure, with "is this polygon correct?", which you can.

A curve drawn directly invites you to draw what you expect instead of what is
there, and it comes out loose and bulbous. That is the one cause of the blobby
amateur look.

## The envelope

The envelope is the largest single shape enclosing the whole subject. Everything
else fits inside it.

1. Draw a reference box touching the subject's four extremes, and reproduce it
   at matching scale on the canvas first.
2. Plot the four extreme points: topmost, bottommost, leftmost, rightmost.
3. Connect them with as few straight lines as possible: 6 sides or fewer for a
   full figure. Worked examples start a head with about 5.
4. Subdivide: find the next-largest changes of direction and add straight chords
   between them.
5. Repeat in passes, each adding more and shorter straights, until the polygon
   reads as the full form.
6. Check every angle against the subject before committing it.

No source gives a segment count for a finished block-in, only the 6-side
starting envelope. Do not invent one.

The 6-side limit is a starting point, not a cap. A subject with more real
changes of direction (a helmet on a head can have ten) needs a vertex at each,
because the envelope must contain the subject. Check it: a chord across a convex
run cuts inside the form, and 25px of helmet outside the envelope fails the gate.

## Sighting by pixels

When the subject is an image file, sight it by reading the pixels: walk a row or
column and record where the flat colours change. That gives what a held-up pencil
and a plumb line give, without the estimating. To trace a mass, take the first
and last pixel belonging to it in each column.

Two cautions:

- A run-length reading that crosses two features gives both to whichever it
  names first: a moustache measured through the mouth line came back 12px too
  deep. Limit each scan to one feature.
- Classifying a colour to its nearest palette entry can silently turn a
  near-black navy into a dark grey. Check the raw values of anything
  structurally important before trusting the label.

## Reading a value off the subject

Sampling a colour is a scan like any other, with one silent and expensive
failure.

**Take the mode of a clean interior patch, never the median of a small window.**
A median over an 8x8 window anywhere near a contour returns the contour's value,
as a confident number with no sign of error. For example, a shoe's body sampled
that way read L=37.9 and a chainring L=25.9, which led to a wrong diagnosis,
four edits and a revert. The histogram mode of a patch wholly inside each form
gave L=60 and L=59: the same value, as the drawing already had and the subject
actually has.

- **Place the window inside the form, not on its edge**, and look at what is in
  it before believing the result. A patch that can contain an edge eventually
  will.
- **Use the mode, not the median, and report the sample count.** A mode over a
  few hundred interior pixels is stable. A median over sixty is a coin toss,
  weighted by whatever line crosses the corner.
- **Sample every part of a comparison the same way, in the same pass.** In the
  example above both parts were wrong together, which made the error look
  plausible.
- A value difference you cannot see at 4x is not real. Look at the crop before
  acting on the number, and if eye and number disagree, re-sample before
  believing either.
- **A darkness threshold cannot separate two dark values a few levels apart.**
  A shell and the webbing on it, seven levels apart, both fall under any
  luminance cut-off called "ink", so the scan reports a silhouette several times
  its real width, with no sign of error, whatever the cut-off. Sample the mode of
  each form separately and classify pixels by distance to those modes.
- **A box whose edge lands exactly on the edge of its scan window is measuring
  the window, not the part.** Flag every measurement that touches its own window
  and re-scan wider; on a first pass roughly a third of them are the window.
  Colour has the same fault: a mask loose enough to let in the ground silently
  clips every box that reaches the subject's edge.

## Measurement gives position, never shape

This is the limit of the whole method, and accurate measurement hides it by
making a drawing feel finished when it is not.

**Sampling an edge every few pixels copies the sampling noise into the
silhouette.** Thirteen measured points along a moustache give thirteen small
bumps, and the result reads as a lumpy slab where the subject reads as a clean
crescent. Build a shape from a few deliberate control points, with one
continuous curvature and a decision about where it is thickest and where it
comes to a point. Take only its extremes from measurement.

The same happens with whole features. A scan for a helmet's vents finds the
coloured area inside each slot, never the slot, so the drawing gets seven
floating blobs instead of a fan of slots cutting the crown's edge. When a feature has an underlying construction (a fan, a cylinder, a
repeating rhythm), build that construction and check it by looking, instead of
tracing what the scan returned.

An overlay check cannot catch this: at 1:1 a lumpy shape and a clean one fill
the same box. Only the detail check at 4x shows it.

## Which instrument gives a coordinate, and which settles a proportion

**Looking does not give you a position.** Three ways of reading positions off a
4x picture ranked clearly:

- **Points read by eye off a gridded or ticked crop were 30-60px off** (a
  helmet's right edge, a thigh, the upper edge of a forearm). A grid tells you
  which structure is where; it never gives a coordinate or evidence of a fault.
- **A scan across the subject** (`check.py --scan x,y,w,h --side S`, or a column
  or row of its dark runs) corrected every one of those. Use it as the source for
  any landmark you type into `draw.py`. `look.py edge` gives the same kind of
  number along any ray, and `look.py probe` gives the colour and palette name at
  a point. You may read an outline of hundreds of points off a magnified grid
  crop (`look.py grid`), but only as a draft: then probe or scan the placed
  points against the subject and move the ones that are off.
- **Judging proportion from a side-by-side view misled in both directions.** A
  drawn head looked 10% too large with its chin 70px low; measured on the same
  image, the chin was 6px off and the helmet 3% wide. A jersey band looked broken
  where the subject's was continuous, and the subject's was in fact broken too. A
  person reading the same thumbnails was half right and half wrong on each item.
  Every case was settled by a scan or by `--overlay --box`, never by looking
  harder. So anything raised by eye (yours, a critic's or a person's) is a
  hypothesis until a number measured on subject and drawing confirms it. Move no
  mark before that.

**A thick line can look like two.** A 40px rim line in a magnified crop looked
like a rim plus a separate brim, and was drawn as two strokes 30px apart.
`--doubled` cannot catch this, because the strokes do not overlap. A scan across
it shows one dark run per column in the subject and two in the drawing
(`runs 1|2`).

### The outline is not the likeness; interior lines carry it too

When a form's likeness lives in its outline (a face in profile or three
quarters, a nose, a chin), run an edge scan on the side the silhouette faces:
for each row, the outermost non-ground pixel on subject and drawing. It is the
only check that catches a wrong turn between two measured landmarks. For
example, a nose bulb that tucked in 20px too early passed a chin check, a width
check and `--masses`.

The edge scan is necessary but not sufficient: a face can pass it row by row and
still look wrong because the fault is inside the outline. For example, the ridge
of the nose may run diagonally from the brow to the nostril
in the subject, making the nose a wide wedge, and almost vertically down the far
edge in the drawing. No outline check can see an interior line.

`--overlay --box` over the focus shows both inks at once: the subject's in blue,
the drawing's in red, and black where they coincide. For every blue line inside
the form, ask which red line is meant to be it, and how far and in which
direction it is off. Answer that for the lines that carry the likeness (the
nose's ridge, the brow, the corners of the mouth, the fold of the cheek), and
measure any disagreement with `--scan`, whose ink columns list the interior runs
row by row.

This is deliberately a question answered by looking, not a gate with a
threshold. Matching lines is a judgement, and any number computed from the two
inks (a distance, a share of overlap) gets worse as ink is added, which is the
wrong direction for a gate.

## Landmarks are the block-in's vertices

Placing landmarks and blocking in with straights are the same operation seen two
ways: a landmark sits where a line changes direction.

- Place the envelope and its strongest outer angles first, then work inward.
- Put landmarks at hard places (bony points where the skeleton sits close to the
  skin) and at changes of direction.
- Place every new landmark relative to one already fixed, never on its own by
  eye.
- Connect landmarks with straight chords, never a freehand curve.

This beats a continuous contour, where perception pulls an unchecked tilted line
toward vertical or horizontal and the error builds up unseen. Each landmark is a
checkpoint you can verify on its own.

## The gate

Draw no curve until the straights have been checked and corrected at least
once. In an atelier, the instructor refuses to look at curve work before the
block-in is signed off. Hold yourself to that.

Then round off the transitions between the straights. A curve can only be as
good as the straight it replaced.

## Sighting and measurement

Comparative measurement takes one length from the subject as a unit and
expresses everything else as a ratio to it. The standard unit is the head
length. Adults are 7.5 heads tall in life and 8 in the idealised canon.

Procedure:

1. Sit where you can see subject and drawing without moving.
2. Extend your arm and lock the elbow every time; a bent arm changes the
   measurement.
3. Close one eye, to flatten the scene to 2D.
4. Hold the pencil perpendicular to your line of sight, line its tip up with
   landmark A, and slide your thumb to landmark B. That span is the unit.
5. Keeping the thumb fixed, count how many units fit across a larger span.
6. Measure the drawing the same way, arm locked, and check the ratio.

**Angles.** Turn the pencil at the wrist until it lines up with the tilted edge,
and note which other landmarks that line crosses. Then freeze the wrist, turn to
the drawing, and check that the same tilt crosses the matching points. The usual
way to remember the angle is a clock face: "two o'clock to eight o'clock". There
is no degree-based protocol, and the literature has no "two-pencil method": the
real technique uses one pencil, one measurement at a time.

**Plumb lines.** Hold a true vertical through one landmark and note every other
point it crosses, then carry that relationship over to the drawing and check it.
This works because people judge verticals and horizontals far more reliably than
diagonals. Drop several plumb lines over a drawing, not one.

## Negative shape

A gap between forms is a shape in its own right. You have no expectation of how
an odd gap should look, so you judge it honestly, whereas your brain silently
corrects an arm toward the arm you expect.

- Check the largest negative shape first, then smaller ones in turn.
- Ask explicitly: is it too wide, too narrow, does it pinch in too early?
- When a gap is wrong, fix the positive contour, not the gap.
- Keep checking negative shapes throughout the block-in and the contour, not
  once at the end.

Neighbouring shapes are linked in proportion, so a wrong gap exposes errors you
cannot see when judging each shape alone.

## Sight-size vs comparative

**Sight-size** fixes subject, easel and viewing position for the session and
draws the subject at exactly its apparent size from there: a 1:1 transcription,
easy to teach and check, but broken by any change of distance.

**Comparative** measurement works at any distance and scale, because everything
is a ratio to a unit. It is flexible, but each measurement depends on the one
before, so early errors compound.

Use sight-size when the setup can stay fixed, and comparative when it cannot.

## Working from a reference image

Measure the reference instead of being impressed by it.

- Take landmark positions from the pixels, not by eye. Read the rows where the
  brow, eye, nose base, mouth and chin actually fall, and the width at each.
- Express them as ratios and compare them with the standard proportions in
  `head.md`. The difference is the subject's character; see "how this subject
  differs from the typical one" under Reading the subject in `method.md`.
- Draw in the reference's own coordinates and pin the render frame, so an
  overlay comparison is exact.
- Never compare from memory. You will silently fall back on the symbol you
  already believed in.
