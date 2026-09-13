# Correcting

A drawing is not finished when the last mark goes down. There is an hour after
that with a rag and a small brush, going round the whole picture putting colour
back where it fell short of a line and taking it off where it ran past one.
Nothing new is drawn in that hour and nothing is redrawn.

It is a separate pass because it uses a separate faculty. Drawing is looking at
the subject; correcting is looking at *the drawing*, against its own line art,
for the places where two marks that were each aimed correctly do not agree with
each other.

## What the corrective pass may not do

It is for faults that are **local consequences of decisions that are right
everywhere else**. The case that defines it: a flat is trapped seven pixels past
its contour along its whole length, correctly, and for forty rows near a corner
the contour turns in faster than the flat does, so the trap comes out from under
the line and stands clear of it in the open. The flat is not wrong. Pulling it
back far enough to clear those forty rows would un-trap the four hundred that
are correct. A fault local to forty rows is corrected locally, on top.

Everything else goes back to the stage that made it:

| The fault | Where it belongs |
|---|---|
| A flat trapped correctly, exposed for a short run | **correct it** |
| A line two pixels fat over a short run | **correct it** |
| A stray tick, a speck, a hole in a black | **correct it** |
| A shape in the wrong place, a blunt tip, a mass the wrong size | redraw the stage |
| A contour that stops on the frame instead of running past it | redraw the stage |
| Anything wrong along its whole length | redraw the stage |

A drawing rescued by body colour everywhere reads as scraped, and it is a
reliable sign that a stage was signed off before it was right.

## Aiming

- **Underneath by default.** A correction on the `mend` stage sits above the
  flats and *under* the ink, so it cannot damage the line; one on `correct` sits
  above everything and can damage anything it touches. Reach over the ink only
  when the thing being corrected is the ink.
- **You correct with the colour of the thing you are restoring** — the paper's
  own outside a contour, the flat's own inside it, the ink's own to close a hole
  in a black. Never white: on a cream ground white is lighter than anything else
  in the picture and the eye lands on it before it lands on the drawing.
- **A trim does not go on the edge you want. It goes on the waste** — centred
  halfway between the edge you have and the edge you want, and at least as wide
  as the strip between them. Aiming at the target edge cuts a pale gash through
  the middle of the mark and leaves its true edge floating above a hole.
- **Measure where the mark actually landed**, never where it was sent. Aiming and
  landing are different things, and a correction placed from an impression lands
  beside the fault and leaves two where there was one.
- **The hand is turned down.** Everywhere else in a drawing the imprecision is
  the point. Here it is the enemy, because there is no third pass to catch what
  this one misses.
- **Every correction leaves a speck** — the tip of whatever it took, marooned
  beyond the new edge. The last thing the brush does is go round and pick them
  off.
- **One fault, one mark.** When a correction falls short, widen it; do not lay a
  second one alongside. Two marks of the same colour overlapping leave a seam
  between them, and the seam is a straighter and more legible line than whatever
  they were covering — so the second attempt reads worse than the first.

## A corrective pass is not durable

Every mark in it is aimed at where the marks underneath *actually landed*, not at
where they were sent. So anything that moves them — a changed control point, a
different seed, a fix to the pen itself — invalidates the whole pass at once, and
the cuts that covered a spill are now sitting a little to one side of it. Run the
registration check again after any such change and expect to redo work. This is
the price of correcting at the pixel rather than at the decision, and it is the
reason a fault is sent back to its own stage whenever it can be.

## Prove each one, or take it out

**Render with the corrective stage hidden, and compare the two frames at 4×.**
A correction that does not survive being switched off is not a correction. Most
candidates do not survive: a fault that measures three pixels wrong can be
invisible because the subject is broken up in the same place, and then the right
answer is to take the correction out and keep the fault.

This is the only check in the skill that compares the drawing against itself
rather than against the subject, and it is the one the corrective pass cannot do
without.

## The other pass: relationships, not marks

Everything above is about marks disagreeing with each other. A finished picture
has to answer a second question that no amount of trimming reaches: **do its
parts lead in the order the subject's parts lead?** A panel can be correct part
by part and still put its furniture in front of its subject — and that, rather
than the thinness of the tier-3 objects, is what makes an economical drawing
read as an unfinished one. The furniture is not too crude. It is too loud.

`check.py --ranking parts.json` measures it: the spread of value inside each
part's own box, ranked, the drawing's order against the subject's.

**The move is zero-sum, and that is the useful half.** A ranking cannot be lifted
by working harder — add marks to every part and the order comes back unchanged.
So the only way to raise what should lead is to put down what competes with it.
That much holds.

**What does not hold is any cheap way to put it down here.** The obvious
instrument — a translucent glaze laid over the region, ink included — was built,
measured, and **rejected by the first person to look at it** [bought: drawing].
The numbers said it worked: three glazes moved a panel's rank agreement with its
subject from +0.77 to +0.80 and closed a standing describer disagreement about
which part of the picture dominates by area. The picture said otherwise. A glaze
does not push an object back a plane; it makes a **dirty copy of it in place** —
the blacks lift to brown, the lights go tan, and a veiled object beside an
unveiled neighbour of the same kind reads as a ghost rather than as distance.
This is the clearest case on record of a whole-picture number going the right way
while the drawing got worse, and it is exactly why `SKILL.md` says never to let
one stand in for the verdict.

**What actually recedes an object is losing its contour** and letting it weld
into the mass behind it — a decision belonging to the masses stage, which a
per-object ladder never offers because it has already given every object a closed
outline of its own. That is `scene.md`'s problem, not this file's.

So `--ranking` stays a **diagnostic with no pass attached to it**. Read a large
delta as a pointer to the stage that made it.

**The trap that matters** [bought: drawing]. Most large deltas are not relational
faults at all. A flat filled in the wrong colour, a background contour drawn
across the object in front of it, a form whose construction is wrong — each
arrives in this report looking exactly like a weld, because a welded junction and
a mis-filled flat have the same signature: **low spread where the subject has
high**. On the panel that bought this section the report's two worst rows were
both one fill in the wrong colour, and the right response was stage 9. **Crop the
part and look.** The report names a region; it never names a repair.

## Finding them

By eye at 1:1 you will not find these. They are two and three pixels wide, and
they are the first thing a viewer's eye lands on anyway, which is the whole
difficulty. `check.py --registration` finds them mechanically, from the drawing
alone:

```bash
python3 check.py drawing.png --registration --space x0,y0,x1,y1 --out faults.png
```

It floods the picture inward from the bare paper at its border, through anything
that is not line, and the drawing splits in two — what the line encloses and
what it does not:

- a **spill** is colour the flood reached: it lies outside the line art, so
  nothing covers its edge;
- a **gap** is paper the flood did not reach: walled in by line and colour on
  every side, so it reads as a hole;
- and if the flood pours into a region it had no business reaching, the line art
  is **open** somewhere — the most common flatting fault of all, seen from the
  other side.

The seeds are bare paper only, never every border pixel, because a shape is
supposed to run off the edge of the picture rather than stop on it.

It reports; it does not decide. **A flat mixed at the paper's own value will be
reported as a gap every time** — an eye white on cream paper, for instance — and
a trap that wanders under its own line will not be reported at all, because it
is not a fault. Look at every hit before correcting any of it.

**Its smallest hits are usually the renderer, not the drawing.** Where a hairline
crosses paper the two blend, and a blend classifies as neither ink nor paper, so
it is reported as a spill a few pixels long. Measure two or three before chasing
any of them: if the pixels run smoothly from the line's value to the paper's,
that is anti-aliasing and there is nothing to correct. List the ones you have
cleared in the drawing's own notes so the next pass does not hunt them twice.

**It is a vignette check.** It assumes bare paper surrounds the subject, which
is what makes the flood mean anything. Run it on a full-bleed scene — a room, a
landscape, anything whose colour reaches the frame on every side — and the wall
and the floor come back as the two largest spills in the drawing, because they
are colour the flood reached and nothing is covering their edge. On a panel like
that the report is still usable, but only from the small end: **sort by size and
work upward**, since a real misregistration is two and three pixels wide and
everything at the top of the list is the picture. A cast shadow drawn without an
outline will be reported forever, and correctly — the check cannot tell it from
a spill, and only you know it is meant to be there.
