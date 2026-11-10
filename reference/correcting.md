# Correcting

A drawing needs one more pass after the last mark, like an hour going round it
with a rag and a small brush: put colour back where it fell short of a line, and
take it off where it ran past one. This pass draws nothing new and redraws
nothing.

It is separate because it looks at something else. Drawing looks at the subject.
Correcting looks at the drawing against its own line art, for places where two
marks, each aimed correctly, do not agree.

## Contents

- What the corrective pass may not do
- Aiming
- A corrective pass does not survive upstream changes
- Prove each one, or take it out
- The other pass: relationships, not marks
- Finding them

## What the corrective pass may not do

The pass is only for small local faults caused by a decision that is right
everywhere else. For example, a flat is correctly trapped seven pixels past its
contour along its whole length, but for forty rows near a corner the contour
turns in faster than the flat, so the trap shows in the open. Pulling the flat
back far enough to fix those rows would un-trap the four hundred correct ones.
Fix the forty rows locally, with a mark on top.

Every other fault goes back to the stage that made it:

| The fault | Where it belongs |
|---|---|
| A flat trapped correctly, exposed for a short run | **correct it** |
| A line two pixels fat over a short run | **correct it** |
| A stray tick, a speck, a hole in a black | **correct it** |
| A shape in the wrong place, a blunt tip, a mass the wrong size | redraw the stage |
| A contour that stops on the frame instead of running past it | redraw the stage |
| Anything wrong along its whole length | redraw the stage |

A drawing patched with body colour all over looks scraped, and reliably means a
stage was signed off before it was right.

## Aiming

- **Put corrections underneath by default.** A correction on the `mend` stage
  sits above the flats and under the ink, so it cannot damage the line. One on
  `correct` sits above everything and can damage anything it touches. Use
  `correct` only to correct the ink itself.
- **Correct with the colour of what you are restoring**: the paper's colour
  outside a contour, the flat's colour inside it, the ink's colour to close a
  hole in a black. Never use white. On a cream ground, white is lighter than
  anything else in the picture, and the eye goes to it before the drawing.
- **Aim a trim at the excess, not at the edge you want.** Centre it halfway
  between the edge you have and the edge you want, and make it at least as wide
  as the strip between them. A trim centred on the target edge cuts a pale gash
  through the middle of the mark and leaves its real edge floating above a hole.
- **Measure where the mark actually landed**, never where it was sent. A
  correction placed from an impression lands beside the fault, leaving two
  faults where there was one.
- **Turn the hand down** (`hand=`, the pen's built-in variation). Elsewhere that
  imprecision is wanted. Here it does harm, because no later pass will catch
  what this one misses.
- **Every correction leaves a speck**: the tip of whatever it removed, stranded
  beyond the new edge. Finish by going round and removing these.
- **Use one mark per fault.** When a correction falls short, widen it. Do not lay
  a second mark beside it. Two overlapping marks of the same colour leave a seam
  between them that is a straighter, more visible line than what they covered.

## A corrective pass does not survive upstream changes

Every corrective mark is aimed at where the marks underneath landed. Anything
that moves them (a changed control point, a different seed, a fix to the pen)
invalidates the whole pass: the cuts that covered a spill now sit beside it.
After such a change, run the registration check again and expect to redo work.
This is the cost of correcting pixels instead of decisions, and why a fault goes
back to its own stage whenever it can.

## Prove each one, or take it out

**Render with the corrective stage hidden, and compare the two frames at 4x.** If
switching a correction off makes no visible difference, remove it. Most
candidates fail this test: a fault that measures three pixels wrong can be
invisible because the subject is broken up at the same place. Then keep the
fault.

This is the only check in the skill that compares the drawing with itself
instead of with the subject, and the corrective pass cannot skip it.

## The other pass: relationships, not marks

A finished picture also has to pass a test that no trimming reaches: do its
parts stand out in the same order as the subject's? A picture can be correct
part by part and still put its furniture ahead of its subject. That, more than
how thinly the tier-3 objects are drawn, is what makes an economical drawing look
unfinished. The furniture is not too crude; it draws too much attention.

`check.py --ranking parts.json` measures this. For each part it takes the spread
of value inside the part's own box, ranks the parts, and compares the drawing's
order with the subject's.

**Raising one part means lowering another.** Adding marks to every part leaves
the order unchanged. The only way to raise what should lead is to tone down what
competes with it.

**There is no cheap way to tone a part down.** The obvious tool is a translucent
glaze over the region, ink included. Do not use it: it was built and measured,
and the first person to look at the result rejected it. The numbers improved
(three glazes moved one picture's rank agreement with its subject from +0.77 to
+0.80, and settled a standing describer disagreement about which part dominates
by area), but a glaze does not push an object back in space. It makes a dirty
copy of it in place: the blacks lift to brown, the lights go tan, and a veiled
object next to an unveiled one of the same kind reads as a ghost, not as
distance. A whole-picture number can improve while the drawing gets worse, which
is why `method.md` says never to let one stand in for the verdict.

What makes an object recede is losing its contour and letting it merge into the
mass behind it. That is a decision for the masses stage. Running the object
stages object by object never offers it, because by then every object already
has a closed outline. See `scene.md`.

So `--ranking` is a diagnostic with no corrective pass attached. Read a large
delta as a pointer to the stage that caused it. **Most large deltas are not
relationship faults at all.** A flat filled in the wrong colour, a background
contour drawn across the object in front of it, and a badly constructed form all
look exactly like a merged junction in this report, because they share its
signature: low spread where the subject has high. In one case the report's two
worst rows were both a single fill in the wrong colour, and the fix belonged at
stage 9. Crop the part and look. The report names a region, never a repair.

## Finding them

You will not find registration faults by eye at 1:1: they are two or three
pixels wide, yet a viewer's eye lands on them first. `check.py --registration`
finds them mechanically, from the drawing alone:

```bash
python3 check.py drawing.png --registration --space x0,y0,x1,y1 --out faults.png
```

It floods the picture inward from the bare paper at its border, through anything
that is not line, which splits the drawing in two: what the line encloses and
what it does not.

- A **spill** is colour the flood reached. It lies outside the line art, so
  nothing covers its edge.
- A **gap** is paper the flood did not reach. It is walled in by line and colour
  on every side, so it reads as a hole.
- If the flood pours into a region it should not reach, the line art is **open**
  somewhere. This is the most common flatting fault, seen from the other side.

The flood starts only from bare paper, never from every border pixel, because a
shape is supposed to run off the edge of the picture, not stop on it.

The check reports and does not decide. A flat mixed at the paper's own value (an
eye white on cream paper, for instance) is reported as a gap every time. A trap
that wanders under its own line is not reported at all, because it is not a
fault. Look at every hit before correcting any of them.

**Its smallest hits usually come from the renderer, not the drawing.** Where a
hairline crosses paper the two blend, and a blended pixel counts as neither ink
nor paper, so it is reported as a spill a few pixels long. Measure two or three
before chasing any. If the pixels run smoothly from the line's value to the
paper's, it is anti-aliasing: leave it. List the ones you have cleared in the
drawing's own notes so the next pass does not chase them again.

**It is a check for vignettes.** It assumes bare paper surrounds the subject,
which is what makes the flood meaningful. On a full-bleed scene (a room, a
landscape, anything whose colour reaches the frame on every side) the wall and
the floor come back as the two largest spills. The report is still usable, but
only from the small end: sort by size and work upward, since a real
misregistration is two or three pixels wide and the top of the list is the
picture itself. A cast shadow drawn without an outline is reported every time,
and correctly: the check cannot tell it from a spill, and only you know it is
meant to be there.
