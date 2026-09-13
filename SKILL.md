---
name: drawing
description: Draw something yourself, mark by mark, on a real canvas — see the subject, block it in with straights, gate each stage on a check, and only then commit to curve, ink and black. Use when asked to draw, sketch, illustrate, redraw or restyle an image by hand rather than generate it with an image model.
---

# Drawing

You make every mark. Nothing here generates a picture — you decide where each
stroke goes, put it on a canvas, look at what appeared, and correct it.

Placing a mark is trivial; knowing *where* it goes is the entire discipline, and
almost everything below is a device either for seeing the subject more accurately
or for catching the error you have gone blind to.

## The principles

Everything else here is an application of these. When a situation is not covered,
reason from here.

1. **Seeing is the work, and the reading is in shapes.** Say what a thing is as a
   *sentence about its shape* — *the upper lid comes down as a shallow arc that
   cuts the top off the iris; no white above the pupil.* Not `eye (524–560,
   320–348)`. **A check can only verify what the reading stated**, and a box is
   the only thing a box can be compared against: the same drawer in one session
   produced a body read in sentences that is structurally right and a face read
   in boxes that is monstrous. Measurement verifies the placement of a shape you
   have already stated; it cannot state one.
2. **Whole before part** — in placement and stage, **never in investment.** No
   area gets ahead of the rest; if you run out of time the deliverable is a
   complete drawing at an earlier stage, never a finished corner on a blocked-in
   rest. But "everything advances *equally*" on an 81-part scene gave 81 equally
   shallow parts — a background prop given as much construction as the figure's
   shoulder, and nothing in the panel a mistake because nothing was built. How far each part
   is built inside a stage is decided once, at stage 0, and is not equal
   (`reference/scene.md`).
3. **Commit late.** Cheap reversible things first: gesture, straights, curve,
   ink, black.
4. **Measure what can be measured; never guess what can be checked.** A straight
   has an angle and a length you can verify. A curve has neither — it can only be
   judged by whether it "looks right", which is the judgement not yet
   trustworthy. This is why the block-in is straight.
5. **Form before edge.** Marks must answer to an implied volume. A traced
   silhouette records the 2D boundary from one angle, contradicts nothing, and so
   has no way to be wrong — which is the same as no way to be corrected. A tube
   is a solid and a ring is a band, not an outline.
6. **Two families, never overlapping.** Everything in light lighter than
   everything in shadow. Decide the split before any tone; keep a real gap.
7. **Vary execution; lock structure.** Weight, curvature, spacing, detail density
   and the path of every stroke vary — a hand cannot repeat itself. Proportion,
   landmarks and identity markers do not. Randomise the wrong layer and the
   drawing falls apart.
8. **Never mirror.** Mirroring doubles one half's real deviation and erases the
   other's, and the asymmetry is what carries the likeness. Place each side's
   points separately — not mirrored-with-noise. Fix an identity asymmetry
   signature per character and repeat it in the *same* place every time; that is
   model-sheet data, not noise. Prefer an off-axis view, which makes symmetry
   geometrically unavailable.
9. **Look in ways that defeat your own eye, and let someone who has not seen the
   script look too.** You cannot un-know the coordinates you typed: asked what
   your drawing shows you answer with what you meant it to show, and the two
   agree because they are the same numbers. That is how a drawing gets three
   hundred lines of forensics about three-pixel spills and not one sentence about
   what the face looks like. **No judge may have seen the script** — including
   you, and including any coordinator scoring a drawing against numbers it wrote
   itself.
10. **Small increments, and look after every one.** "Write the stage, then
    render" is still a batch. A stage written blind bakes in a dozen errors that
    then have to be unpicked together. And **never retype a coordinate from
    memory** — re-measure it. A contour reissued from recollection lands 10px off
    and every fill that met it now gapes; that is how a correctly measured brow
    became an inverted one.

## Reading the subject

In writing, before touching the canvas. `Read` the reference image first, and
measure it rather than impressing yourself with it.

1. **What is this a picture of?** One sentence — what should the viewer notice
   first. Everything below is ranked against that answer.
2. **The big shape**, as one or two simple forms. If you cannot say it in a
   sentence you have not looked yet.
3. **The line of action** — the single curve carrying the thrust.
4. **The deviation.** How does *this* subject differ from the average one? That
   difference is the likeness. **Measure it** (`reference/measuring.md`) —
   establish the average first and you will draw the average, then decorate it.
   Exaggeration follows each feature's *own* direction: a big nose gets bigger
   but a **small mouth gets smaller**, and pushing everything cancels the
   contrast. Mild beats extreme; overshoot degrades likeness as surely as
   undershoot.
5. **Light source.** Decide it now and never move it.
6. **The two value families**, then the three-value plan. Two objects on
   different depth planes must never share a value or they weld into one plane.
7. **What you will leave out.** An omission you chose is economy; one you did not
   notice is a failure.
8. **The inventory** — below.

### The inventory: name the parts, then look for them

**Write it before the first mark.** Every check that measures marks is blind to
marks that are not there: a face with no nose passes all of them, because nothing
is *wrong* — something is missing, and missing has no pixels. Two panels shipped
from this skill with a rider who had no nose and no ear, and a herd of cows with
heads and no bodies, every mechanical gate green.

Every entry is a **shape sentence** with a box *derived from* it, taken off the
subject, saved as `parts.json`:

```json
{
  "nose": {
    "shape": "ON the silhouette, not a mark inside the cheek: the profile leaves the brow, runs down and OUT to the tip, then turns back under it",
    "box": [540, 336, 45, 50],
    "front_of": "face"
  },
  "hand/bar": {
    "shape": "the glove closes over the bar; the bar disappears behind the fingers and reappears 30px to the left. No gap",
    "box": [318, 470, 96, 70]
  }
}
```

The sentence comes first and the box is read off the shape it describes, never
the reverse. A bare `"nose": [540, 336, 45, 50]` still loads, because five
drawings on disk are written that way, and it is not what to write: it states
where a part is and nothing about what it is, so a box becomes the only thing any
check can compare against and the check then passes anything of the right size in
the right place.

**Validate the reading before you place anything.** Every aim in this skill —
these boxes, the zoom crops, the masses colour count — is a number you typed,
produced by the same seeing the instrument exists to check, so a self-aimed check
catches slips and never misreadings. A moustache boxed 30px short passed the
absence check on the wrong region. So crop the *subject* to each box, show it to
a reader who has not seen your reading, ask what it is, and correct the sentence
and the box against the answer. Then write the acceptance list for the finished
drawing, from the reading, and do not change it afterwards.

**It is also the only check that can delete a part.** Every other
gate asks whether what you drew is right; this is the only one pointed at the
reading, and the inventory is upstream of all of them — so an entry for an object
that **is not in the subject** propagates into the block-in, the flats, the
interfaces table and the depth order, and arrives at the critic as a drawn object
with a provenance. You will write such entries wherever the subject omits
something its category normally has, because that is where the symbol fills in.
No mechanical check reaches it: `--parts` reports the box as present and busy,
the masses see a few dark pixels inside a dark region, overlay sees an object
inside the union of its neighbours, registration sees it trapped and closed. A
critic invents the same object for the same reason.

So run the validation on **every** tier-1 and tier-2 entry, not a sample, and
treat *"I can't tell what this is"* as the strongest result it can return, not a
failed answer.

**The box exists for the check to crop with. Never draw to it.** The sentence is
the target; the box is the only *number* in the entry, and a hand placing a mark
reaches for the number. A flat drawn to its box reads as two unrelated faults —
departure-from-own-mode near 0.00 at the masses gate ("uniform inside its own
box"), a large ink excess in the same box later — and survives correction rounds,
because the corrections are aimed at the box too.

Then at every gate:

```bash
python3 check.py drawing.png --ref subject.png --parts parts.json --out parts.png
```

Subject above, drawing below, **with the sentence printed over each pair** — so
the verdict is written against what the reading claimed, not against a bare
picture. For each part: is the sentence true of the drawing? Where it is not, one
line on what the subject does and one on what the drawing does. If you cannot
name a difference you have not looked. A part with no sentence is reported in
red, because for that part this check is comparing a box to a box.

**Name the junctions, not only the things**, as ordinary entries with sentences
of their own — they need no machinery, and they are where every scene here has
failed. An inventory of nouns produces a drawing of nouns stuck together. A
junction is the *gap* or the *order* between two boxes, so no check looks there
unless it is named — hand/handlebar,
foot/pedal, hip/saddle, tyre/floor (`reference/scene.md`), and within a body
shoulder, elbow, hip, knee, wrist, ankle and the segments that span them. The
finest inventory built here — 81 parts — named **not one joint**, went finer on
surfaces instead, and produced a figure with no shoulder, no elbow, and an arm
widening toward the wrist. The 74-part list on the sibling panel named `R upper
arm` and `L elbow`, and that panel's arms are the better ones. **Finer is not
better; more joints is.**

**Small and ranked**, against the sentence from step 1 — a flat list gives a wall
clock and a face equal standing, which principle 2 says is wrong.

**A part that is absent, or unrecognisable as itself, is a failed stage, not a
known fault.** Go back and put it in.

## The stages

Each narrows a different freedom, and each is cheap to fix while the next is
expensive. **A stage may not begin until the previous gate is true, verified by
looking at a render.** And **no part may be more than one stage ahead of any
other** — walk the inventory and check, because the instruments reward neglecting
the rest of the panel: `--parts` hands you a box per feature, `--zoom` at 4x is
most legible on a face, and a describer volunteers an opinion about expression
unasked.

| # | Stage | Decides | Gate |
|---|---|---|---|
| 0 | **Read** | What the picture is | The sentence, the big shape, the deviation, the light source — and `parts.json`: ranked, joints named, every entry a shape sentence, validated against a fresh reader before anything is placed |
| 1 | **Gesture** | Rhythm, action, thrust | One continuous force reads. Proportion explicitly *not* checked yet |
| 2 | **Envelope** | Outer extent | Four extremity points plotted; polygon (≤6 sides to start, one vertex per real direction change) **contains** the subject |
| 3 | **Block-in** | Structure and proportion, in straights | Landmarks placed relative to already-fixed landmarks; angles checked against the subject by overlay |
| 4 | **Construction** | 3D volume under the shape | Every form's turn stated in writing first, its centre line placed where that turn puts it — not down the middle of its box |
| 5 | **Masses** | The picture as filled areas, no line at all | `check.py --masses` beside the subject's: the two read as the same shape, said in words. Nothing drawn on top will fix them if they do not |
| 6 | **Contour** | The real edge — *break the straights into curve* | Curves depart from the primitives where the subject does |
| 7 | **Cleanup** | Which line is *the* line | Every line intended for ink exists and is right; construction faded or erased |
| 8 | **Ink** | Weight, permanence, hierarchy | — terminal line stage |
| 9 | **Fill** | The masses refined — shadow, blacks, flats | Structure already fixed; value cannot rescue wrong proportion |
| 10 | **Correct** | Where colour and line disagree | Ink and flats both final; every correction survives being switched off |

**Registration, weights and ink-share belong to stage 9 and later.** Earlier they
are a distraction with the appearance of rigour, and they eat the looking budget
at the stages whose whole job is to look at a shape and say what it is.

**Going back up the ladder invalidates what sits above it** — a restated contour
orphans the flats that met it and the corrections aimed at where its marks
landed. Re-run every stage after the one you changed. This is also the *cheap*
answer: the script re-renders in one call, so sending a fault back to its own
stage costs less than a pixel correction that then has to be redone anyway.

### Straights (stages 2–3)

The part most likely to be skipped, and the part that most determines whether the
result looks amateur.

- Plot the **four extremity points** and connect them into the smallest polygon
  containing everything. A chord across a convex run cuts *inside* the form, and
  part of the subject outside the envelope is a failed gate, not a simplification.
- Subdivide in passes, each adding shorter straights at the next-largest
  direction change. **Landmarks are the block-in's vertices.** Every new landmark
  is placed **relative to one already fixed**, never independently by eye.
- **No curve exists until the straights have been checked against the subject.**
  Then round the transitions. A curve is only as good as the straight it replaced.
- Straights must reach the canvas **densified** — many close points, not two
  endpoints — or the freehand renderer smooths every corner off and hands back
  the soft blob the block-in exists to prevent. `smooth=False` does this for you;
  it is the densifying branch of `stroke`, not merely a curve switched off.

### Fill (stage 9)

Flat colour goes down as **flatting**: one region per distinct surface — face,
neck and collar are three regions even if they end up the same colour — hard
aliased edges, drawn **generously past where the ink will go** and placed
*behind* it, so the line covers the fill's edge. Cutting colour exactly to a line
is what neither a hand nor a press does; underlapping means any misregistration
reveals more of the correct colour instead of bare paper.

Then **hide the ink and look.** If the flats alone no longer separate foreground
from background, the colour design has failed and no rendering will rescue it.

For value rather than colour: mass the whole shadow as **one flat value** first,
verify that shape reads, *then* grade inside it. Never blend first. Erase
construction before filling blacks. Detail in `reference/colour.md`.

### Correct (stage 10)

Not more drawing — the two- and three-pixel disagreements between marks that were
each aimed correctly, invisible at 1:1 and the first thing a viewer's eye lands
on. `check.py --registration` finds them from the drawing alone. Anything wrong
along its whole length, or wrong in shape, goes back to its stage instead.
`reference/correcting.md`.

**Stage 10 runs before anyone sees the picture**, and it is not the stage you
drop when the budget is thin. Ship without it and the faults a viewer names first
are, almost exactly, the ones this stage exists to catch.

**Correcting is N rounds, each aimed by the critic's list — not an open-ended
polish and not zero.** Write the acceptance list at stage 0 from the reading, fix
the number of rounds then, and score every round against that list and nothing
else. A round that invents a new measurement to score itself by has already
failed: each new number is a detector for the last fault and blind to the next by
construction, so the picture regresses while the newest metric goes green.

**Then one question correcting cannot reach: does the picture lead where the
subject leads?** This stage works mark against mark. A panel can be right part by
part and still put its furniture in front of its subject — and the furniture is
not too crude, it is too *loud*. `--ranking` measures that. What it does **not**
buy is a cheap repair here: a translucent glaze over what shouts was built and
rejected on sight, because it makes a dirty copy of an object in place instead of
pushing it back. What recedes an object is **losing its contour and letting it
weld into the mass behind it** — a decision belonging to the masses stage, and
one a per-object ladder never offers. See `scene.md`. Read a large delta in this
report as a pointer to the stage that made it, not as a repair to attempt now.

## Checking your own work

Each catches a class the others hide, so a check you skip is a class of error you
ship.

| Check | Catches |
|---|---|
| **Masses** | The wrong *shape*. Both pictures reduced to flat areas with line closed away (`--masses`, as `--only fill,frame`), so what is left is what the eye reads first. A wedge and an oval share a bounding rectangle and differ in the only way that matters; this is the one check that tells them apart |
| **Blind description** | Your own anchoring, which nothing else here reaches. Hand the render — **only** the render, to someone who has not seen the script — and ask: *what shape is it, what does it express, what is the biggest thing in it.* Ask the same three of the subject; compare. Never ask "is anything wrong": a describer looking at a cartoon excuses everything as style. Two describers, keep what they agree on. Ask it of a **part crop** too — a form whose outline is right can still be the wrong shape |
| **Critic** | Quality, fused and missing parts, and the list a client produces — the half of the atelier the ladder otherwise leaves out. Both images, told which is which, asked for every way the drawing is worse *as a drawing of the same thing*, worst first, naming the feature and what each image does. Forbid style comments, praise, and the word "fine"; forbid guessing how it was made or how to fix it. It reliably reaches the faults a viewer would name, and names them at the right altitude — a limb ending without its extremity, a part that is simply absent. It is weaker on *why*: it reports a form as unidentifiable where the cause is that two forms have fused, and as misplaced where the cause is that one is shapeless. Its own contribution is junction faults nobody listed — no contact where the weight goes, an object its support does not touch, a frame that does not close. **Asked for N items it returns N items, and the tail is invention** — expect roughly a quarter to be false about the drawing, typically naming as missing a part that is drawn and filled, or asserting a crossing the geometry rules out. So ask for fewer items than you think, and verify each against the render before acting: a fault you cannot find is the critic's, not yours. Its item count is not evidence |
| **Parts** | Whether each shape sentence is true, and the two things no other check can see: the part that is not there at all, and the part that has drifted out of its own box (`--parts parts.json`). Read MISSING? as "behind the rest" before the masses, and as "absent" from the masses on. An entry with no sentence is reported in red — for that part this is a box compared to a box |
| **Verdict** | Your own failure to look. Naming a difference in words is what turns looking into seeing |
| **Detail** | Whether the marks are any good. Every other check measures *placement*; at 1:1 a well-placed bad shape and a good one occupy the same box. Magnify one feature 4x with the subject above it (`--zoom x,y,w,h`) |
| **Weight** | A line hierarchy drifted from the subject's (`--weights`). Meaningless on tone |
| **Ranking** | An object shouting above its tier, and a junction where two forms have **welded** into one value (`--ranking parts.json`) — the spread of value inside each part's own box, ranked, the drawing's order against the subject's. Alone among the numbers here it is **zero-sum**: adding marks everywhere leaves the order exactly where it was, so the only way to lift a part is to put another one down, which is the only move a whole-picture pass may make. Most large deltas are still upstream faults in relational costume — a flat filled in the wrong colour and a weld have the same signature, low spread where the subject has high. Crop the part and look before believing a row |
| **Ladder audit** | A drawing that skipped the ladder, read off the *script* rather than the picture: which stages exist and how many marks each holds, how many strokes carry their own `lead=`/`tail=`, the instrument mix, the count of distinct weights against the measured span. A drawing inked straight off its block-in has no contour pass and every curve in it is a first attempt; one whose marks are nearly all `flat` has drawn its lines as filled shapes. Either passes every placement check here and reads as a diagram |
| **Registration** | Colour and line disagreeing — a fill short of its contour, a fill past it with nothing over it, a contour that does not close (`--registration`). Cannot work on a full-bleed panel |
| **Switch off** | Whether a correction is one. Render with the corrective stage hidden, compare at 4×. Most candidates change nothing, and then the right answer is to take the correction out and keep the fault |
| **Defeat your own eye** | Habituation, in several directions, none expensive: **mirror** for proportion drift; **squint** for value and mass; **silhouette** for fused forms and tangents; **negative space** for relational error, largest gap first; **plumb** for diagonals you squared toward vertical; **overlay** for exact drift against a reference; **line off** (`--hide ink`) for whether the flats carry the composition; **big-to-small** — "am I still at big-shape scale?" |

**Never compare against memory.** You will silently revert to the symbol you
already believed.

**Never ask a describer to judge; ask a critic to compare; and let neither's
words be the target.** They are two instruments with two jobs. A describer is a
recognition test — blind, one image — and it is good at shape, expression, what
leads, and whether the picture's event is present; it *excuses*, so asking it
whether anything is wrong returns "it's stylised". A critic is a comparison test,
and it is the only thing here that sees quality; it attends to features, so it is
worse at silhouette. Measured on the same panel: the two describers, asked only
what shape it is, returned an **arch** for the subject and a **wedge** for the
drawing — the line of action, missed by a critic fifteen items deep. Run both.

**On matters of fact the describer is the more reliable of the two.** The
asymmetry is in the task: a describer reports what it sees, a critic is *asked
for faults* and supplies the number requested. The describer excuses and does not
invent; the critic invents and does not excuse. Weigh their words accordingly.

**Where the two agree independently, believe them, and run both on a part crop at
4x.** A face can pass at 1:1 and carry the opposite expression at 4x — which
inverts the picture's event, the one fault no placement check can reach.

The target is the shape sentence from the reading; a judge's job is only to say
whether that sentence is now true. Optimise to a describer's vocabulary and you
are symbol-drawing by proxy: "closed eyes" became "wide-eyed" by way of a bulging
cartoon eye, and the fix that worked was aimed at the subject's measured lid.

**`form` is a worklist, never a gate.** It measures how much is *going on* inside
a box, and marks are what is going on, so **adding marks raises it whether or not
the marks are right.** Told two cow chests were the worst-structured boxes in the
inventory, a drawer put thirteen more contours in; the ratios rose 0.42→0.53 and
0.57→0.75 **and the picture got worse.** The deficit was not inside those boxes:
the subject's brisket samples cow-white, so there was nothing to add there, and
what was missing was the body's dark barrel not carried far enough across. Four
points fixed what thirteen had broken. So **sample the subject inside the box**
before adding a mark — flat means the deficit belongs to something adjacent. Read
it in both directions: above 1.0 it says take marks out, which `ink` cannot say,
and it is the only thing here that sees a **duplicated mark** (a handlebar drawn
twice 12px apart, diagnosed for rounds as a badly-drawn fist).

This is the general hazard of every number in this file. A measure a drawer can
act on becomes a target, and the cheapest way to move any mark-counting target is
to make more marks.

**And never let a whole-picture number stand in for the verdict.** Mean pixel
difference from the subject is the tempting one and it is actively wrong: across
a round that made a fan's cage read as a cage and a shoe's sole read as a sole,
the fan region went 43.5 to 45.1 and the shoe region 56.2 to 62.7 — worse on the
number, better as a drawing. Correct marks land where the subject has marks but
never at identical coordinates, so agreeing more can measure as agreeing less.
Had that number been the score, every good change in that round would have been
reverted.

## Failure modes

The three with a measurement behind them. A principle restated as a symptom is
not a second finding, and this table is not the place to collect one per round.

| Symptom | Name | Fix |
|---|---|---|
| A feature of the subject is simply **not in the drawing** — no nose, no ear, a body under a head | **Omission**, and every mark-measuring check is blind to it | `--parts` against the inventory, at every gate; then draw it. A failed stage, never a known fault. A face reading as monstrous is usually two or three of these at once plus one feature at the wrong scale — a face is *its parts in relation*, and take one away and the rest cannot compensate |
| The outline tracks the subject at every row and the form still reads as the wrong shape — a slab where the subject is a wedge | **The interior is ranked wrong** — right features, right boxes, wrong order of size, so the eye and mouth lead where the subject leads with the jaw plane | No pixel check can see it: inflating a head's irises 2.4x with every outline point untouched moved the silhouette 0.45% and the masses 0.16 points, and `--parts` could only report that a box got darker. Ask a blind describer the three questions **of that part's crop alone** and compare what each of you ranks first — on the degraded drawing two describers dropped the eyes behind the helmet and read the expression as "deadpan". The eye got **bigger, blacker, and ranked lower**: what makes a feature lead is the expression it carries, not its area. Fix by weight before size |
| Accurate, and reads as a sketch rather than a finished drawing | **You only ever looked at it at 1:1.** Placement was checked; the marks never were | Magnify one feature 4x beside the subject. Blunt-ended marks, a weight range that does not match the subject's, and lumpy silhouettes are all invisible at full size |

## Reference

Depth lives alongside this file; load what the task needs.

**An entry is a diagnostic, never a scaffold**, and the test is mechanical: *if a
passage could be followed with the subject covered up, it is a scaffold.* Rewrite
it as what to measure and what a difference from the average means. A tutorial is
dangerous here in exactly the way `ellipse()` is: it hands you a finished generic
form at the stage whose whole job is to find the particular one. **Mark the
provenance of every claim** — `[bought: drawing]` names the failure and the
measurement that paid for it; `[read: source]` is a hypothesis with good pedigree
and nothing more. **A rule leaves this layer when a drawing shows it wrong**, and
this layer only shrinks by someone deciding to shrink it.

**An earlier attempt's measurements are an input to the next attempt** — and a
contaminant to any test of this skill. Keep the two purposes apart. To *make a
picture*, read the previous go's notes and reading sheet before placing a mark:
this layer holds what generalises, a subject's own notes hold what is true about
that subject, and no amount of the first substitutes for the second. To find out
whether the skill *works*, give the drawer this layer and the subject and nothing
else — a drawer handed the last attempt's fault list proves it can follow a hint,
not that the skill prevents the fault, and every gap it papers over stays hidden.

Note which way a failure points before reacting to it. A fault that sat measured
in the previous attempt's notes is an argument for reading them; a fault this
layer already names in writing and a drawer shipped anyway is an argument that
naming a failure is not the same as saying what to draw instead.

**A gap here is not a licence to outline.** For a long time `head.md` was the only
entry teaching how to *build* anything, and two drawers independently spent their
whole budget on the face and outlined everything else — not because they were
drawn to faces, but because the face was the only thing the skill knew how to
construct. Still missing: perspective and receding planes, manufactured form,
water and reflections, architecture and interiors, foliage.

- `measuring.md` — comparative measurement, sighting, plumb lines, units,
  sight-size vs comparative, negative shape
- `head.md` — skull, planes, the canon to measure a departure from, features as
  constructed forms
- `figure.md` — the three masses and the spine between them, the shoulder girdle
  riding on the ribcage, where the thigh actually leaves the pelvis,
  foreshortening, the cyclist, and cloth as folds with a cause
- `scene.md` — how a scene differs from a subject: ranking objects into tiers,
  budgeting construction before the first mark, and the interfaces between
  objects, which is where every scene here has failed
- `bicycle.md` — frame geometry, the tube weight ladder, wheels in perspective,
  the three rider contacts, drawing occlusion in a lattice
- `quadruped.md` — the animal as one mass, the ribcage barrel and the
  clavicle-less scapula, the ungulate leg and why its backwards knee is an ankle,
  head and horn insertion, keeping a herd from twinning
- `hands-and-feet.md` — the palm box and the thumb mass, the knuckle arcs,
  fingers as three-segment cylinders that never taper to a point, the foot as a
  wedge on a tripod, the shoe as a form over it
- `tone.md` — continuous tone as marks: the stripe failure, anchoring a tonal
  pass, which instruments accumulate, why texture cannot be cut into a path
- `light.md` — light anatomy, the two families, planes, edges, cross-contour, how
  line alone describes volume
- `line.md` — weight hierarchy, what decides weight, inking order, blacks
- `colour.md` — flatting, trapping under the line, the line-off test, cel
  shading, limited palettes
- `correcting.md` — what a corrective pass may not do, aiming a trim, proving one
  by switching it off, finding faults with the registration flood

## The canvas

`harness/` is a tldraw canvas driven from the command line. The document on disk
*is* the drawing; it persists between calls and opens in tldraw for a human to
edit by hand afterwards.

```bash
node harness/cli.mjs DOC.json --ops OPS.json --png LOOK.png [--scale 2] [--flip] [--squint 6]
python3 check.py LOOK.png --ref SUBJECT.png --out CHECK.png   # one look, four panels
```

Setup once: `cd harness && npm install && npm run build && npx playwright install chromium`.
**Rebuild after editing `harness/src/main.jsx`** — the CLI serves the built bundle.

**Write every render and every check beside the drawing, never into `/tmp`.** Two
drawings worked on at once share that directory, and a check is written and read
back a moment later: one overwrote the other's in between. The file names here are
deliberately unqualified for the same reason — qualify them with the drawing's
own directory.

`pen.py` renders your decisions. You choose the control points — that is the
drawing; it interpolates and varies pressure — that is the hand. **Its docstrings
carry the traps**: corners need `smooth=False`, `closed=True` must not repeat its
first point, `fill="solid"` is a tint, flats need `tool="flat"`. `cli.mjs`'s
header carries the flag traps: `--only` needs `frame` in the list, `--padding 0`
clips as well as pins, `--palette` repoints the ground.

**Measure the ground.** It is a palette entry with a right answer, and everything
sitting on it is judged by its contrast *with* it. One panel carried a ground
eleven levels too light for six rounds; nothing looked wrong, a whole object
failed to separate from the wall it hung on, and one line fixed it with no marks
touched — structure 0.39 to 1.01. A wrong ground flattens every relationship at
once and is invisible to every check that compares marks.

**Draw a weight ladder before you trust a weight** — one stroke per `nib=`,
rendered and read back with `--weights` — and draw it **with the instrument you
will use**, because each `tool=` has its own ladder and nothing in the numbers
says so. One measured with `brush` and applied with `flat` came out at 0.42x: a
top tube 5px wide where 12px was asked for, and a whole bicycle arriving at
`bicycle.md`'s "reads as wire" failure.

### The drawing is a script, not a program

**Write every mark on its own line, with its own numbers.** No function that
generates a shape, no loop that stamps one seven times, no geometry computed from
an angle.

The principle under it: **no tool may supply a form you did not choose after
looking.** A supplied form arrives free of charge at exactly the stage whose job
is to find the particular one — a head built on a computed ball with a centre
line down the middle came out with every feature inside its correct box and was
not a face. The test is *could this call produce a shape the subject does not
have?* An `ellipse()` can, so there is no `ellipse()`. A fill bounded by a
contour you drew by hand cannot, and derivation of that kind is fair where a verb
for it exists.

The second thing a flat script buys is a forced look per mark. Where it does not
force one — a coordinate retyped from a box — it is pure cost.

```python
from pen import stroke, frame, fade, erase, write
write("ops.json", [
    frame(0, 0, 900, 1160),                                  # the edge of the picture
    stroke([(300,60),(420,90),(440,300),(300,520)], stage="blockin",
           smooth=False, closed=True),                       # straights, block-in
    stroke([(340,280),(360,275),(385,284)], stage="ink", weight=1.2),
])
```

Marks carry a `stage` (`gesture`, `blockin`, `construction`, `contour`, `ink`,
`fill`, `mend`, `correct`, `frame`), which lets a later stage `fade` or `erase`
the pencil under the ink, and lets `--hide` switch a stage off to see what it is
really doing. `tool=` picks how the mark is made — `pen` (dead uniform), `brush`
(swings thin to thick), `marker` (translucent, overlaps darken), `crayon` (broken
grainy passes), `flat` (opaque regions), `gouache` (opaque body colour, the only
instrument that goes on top of dry ink). `nib=` picks the weight: `hairline fine
medium bold heavy`.

A correction is not a special kind of mark and there is no function that makes
one. It is the same `stroke`, with a different pigment and a different stage.
