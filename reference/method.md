# The method

You make every mark. Nothing here generates a picture. You decide where each
stroke goes, put it on a canvas, look at what appeared, and correct it.

Placing a mark is trivial. Knowing where it goes is the whole discipline, and
almost everything below is a device for seeing the subject more accurately or
for catching an error you have stopped being able to see.

## The principles

Everything else here applies these. When a situation is not covered, reason
from them.

1. **Seeing is the work, and the reading is in shapes.** Say what a thing is as a
   sentence about its shape: *the upper lid comes down as a shallow arc that
   cuts the top off the iris; no white above the pupil.* Do not write
   `eye (524-560, 320-348)`. A check can only verify what the reading stated,
   and a box can only be compared against a box. An agent in one session read a
   body in sentences and a face in boxes, and the body came out structurally
   right while the face was monstrous. Measurement verifies the placement of a
   shape you have already stated. It cannot state one.
2. **Whole before part, in placement and stage, but not in investment.** No
   area gets ahead of the rest. If you run out of time, deliver a complete
   drawing at an earlier stage, never a finished corner on a blocked-in
   remainder. But advancing every part equally on an 81-part scene gave 81
   equally shallow parts: a background prop got as much construction as the
   figure's shoulder, and nothing in the picture was a mistake because nothing
   was built. How far each part is built inside a stage is decided once, at
   stage 0, and it is not equal (`reference/scene.md`).
3. **Commit late.** Do the cheap, reversible things first: gesture, straights,
   curve, ink, black.
4. **Measure what can be measured, and check what can be checked.** A straight
   has an angle and a length you can verify. A curve has neither. It can only be
   judged by whether it looks right, and that judgement is the one you cannot
   yet trust. This is why the block-in is straight.
5. **Form before edge.** Marks must answer to an implied volume. A traced
   silhouette records the 2D boundary from one angle and contradicts nothing,
   so it cannot be wrong, which also means it cannot be corrected. Treat a tube
   as a solid and a ring as a band, not as outlines.
6. **Two value groups that never overlap.** Everything in light is lighter than
   everything in shadow. Decide the split before any tone and keep a real gap
   between the groups.
7. **Vary execution, lock structure.** Weight, curvature, spacing, detail density
   and the path of every stroke vary, because a hand cannot repeat itself.
   Proportion, landmarks and identity markers do not vary. If you randomise the
   structure, the drawing falls apart.
8. **Never mirror.** Mirroring doubles one half's real deviation from the
   typical form and erases the other's, and the asymmetry is what carries the
   likeness. Place each side's points separately, not mirrored with noise. Fix
   an asymmetry signature for each character and repeat it in the same place
   every time; that is model-sheet data, not noise. Prefer an off-axis view,
   which makes symmetry geometrically unavailable.
9. **Look in ways that defeat your own eye, and have someone who has not seen the
   script look too.** You cannot un-know the coordinates you typed. Asked what
   your drawing shows, you answer with what you meant it to show, and the two
   agree because they come from the same numbers. The result is hundreds of
   lines of forensics about three-pixel spills and not one sentence about what
   the face looks like. No judge may have seen the script. That includes you,
   and it includes any coordinator scoring a drawing against numbers it wrote
   itself.
10. **Work in small increments and look after every one.** "Write the stage, then
    render" is still a batch. A stage written blind bakes in a dozen errors that
    then have to be unpicked together. Never retype a coordinate from memory;
    re-measure it. A contour reissued from recollection lands about 10px off, and
    every fill that met it now gapes. That is how a correctly measured brow
    became an inverted one.

## Reading the subject

Do this in writing, before touching the canvas. `Read` the reference image
first, and measure it rather than going on your impression of it.

1. **What is this a picture of?** Answer in one sentence: what should the viewer
   notice first? Everything below is ranked against that answer.
2. **The big shape**, as one or two simple forms. If you cannot say it in a
   sentence, you have not looked yet.
3. **The line of action**: the single curve carrying the thrust.
4. **How this subject differs from the typical one.** That difference is the
   likeness. Measure it (`reference/measuring.md`). If you establish the
   typical form first, you will draw the typical form and then decorate it.
   Exaggeration follows each feature's own direction: a big nose gets bigger
   but a small mouth gets smaller, and pushing everything cancels the contrast.
   Mild exaggeration beats extreme, and overshoot degrades likeness as much as
   undershoot.
5. **Light source.** Decide it now and never move it.
6. **The two value groups**, then the three-value plan. Two objects on different
   depth planes must never share a value, or they merge into one plane.
7. **What you will leave out.** An omission you chose is economy. One you did
   not notice is a failure. Economy applies to texture, detail and variation
   inside a form. It never removes an object that a viewer of the subject
   names: a small figure can be drawn with few marks, but it is drawn.
8. **The inventory**, below.

### The inventory: name the parts, then look for them

Write it before the first mark. Every check that measures marks is blind to
marks that are not there. A face with no nose passes all of them, because
nothing is wrong, only missing, and a missing part has no pixels. In earlier
tests, one picture shipped with a rider who had no nose and no ear, and another
with a herd of cows that had heads and no bodies, with every mechanical gate
green.

Every entry is a **shape note** with a box derived from it, taken off the
subject and saved as `parts.json`:

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

The note comes first, and the box is read off the shape it describes, never the
reverse. A bare `"nose": [540, 336, 45, 50]` still loads, because five drawings
on disk are written that way, but do not write new entries like it. It states
where a part is and nothing about what it is, so the box becomes the only thing
a check can compare against, and the check then passes anything of the right
size in the right place.

**Validate the reading before you place anything.** Every aim in this skill
(these boxes, the zoom crops, the colour count for the masses) is a number you
typed, produced by the same seeing the instrument exists to check. A self-aimed
check catches slips and never misreadings. A moustache boxed 30px short passed
the absence check on the wrong region. So crop the subject to each box, show it
to a reader who has not seen your reading, ask what it is, and correct the note
and the box against the answer. Then write the acceptance list for the finished
drawing, from the reading, and do not change it afterwards.

This is also the only check that can delete a part. Every other gate asks
whether what you drew is right. This one is pointed at the reading, and the
inventory is upstream of all the others. An entry for an object that is not in
the subject propagates into the block-in, the flats, the overlaps table and the
depth order, and arrives at the critic as a drawn object with a provenance. You
will write such entries wherever the subject omits something its category
normally has, because that is where the symbol fills in. No mechanical check
reaches it: `--parts` reports the box as present and busy, the masses see a few
dark pixels inside a dark region, overlay sees an object inside the union of
its neighbours, and registration sees it trapped and closed. A critic invents
the same object for the same reason.

So run the validation on every tier-1 and tier-2 entry, not a sample. Treat
"I can't tell what this is" as the strongest result it can return, not as a
failed answer.

**The box exists for the check to crop with. Never draw to it.** The note is the
target. The box is the only number in the entry, and a hand placing a mark
reaches for the number. A flat drawn to its box shows up as two apparently
unrelated faults: a departure from its own mode near 0.00 at the masses gate
("uniform inside its own box"), and a large ink excess in the same box later.
It survives correction rounds because the corrections are aimed at the box too.

Then at every gate run:

```bash
python3 check.py drawing.png --ref subject.png --parts parts.json --out parts.png
```

It shows the subject above and the drawing below, with the note printed over
each pair, so the verdict is written against what the reading claimed and not
against a bare picture. For each part, ask whether the note is true of the
drawing. Where it is not, write one line on what the subject does and one on
what the drawing does. If you cannot name a difference, you have not looked. A
part with no note is reported in red, because for that part the check is
comparing a box to a box.

**Name the junctions as well as the things.** Give them ordinary entries with
notes of their own; they need no special machinery. They are where every scene
tested here has failed. An inventory of nouns produces a drawing of nouns stuck
together. A junction is the gap or the order between two boxes, so no check
looks there unless it is named. Examples are hand/handlebar, foot/pedal,
hip/saddle and tyre/floor (`reference/scene.md`), and within a body the
shoulder, elbow, hip, knee, wrist, ankle and the segments that span them. The
finest inventory tried, with 81 parts, named no joint. It went finer on
surfaces instead, and produced a figure with no shoulder, no elbow, and an arm
widening toward the wrist. A 74-part list on a sibling picture named `R upper
arm` and `L elbow`, and that picture's arms were the better ones. Naming more
joints helps more than splitting surfaces finer.

**Keep the inventory small and ranked**, against the sentence from step 1. A
flat list gives a wall clock and a face equal standing, which principle 2 says
is wrong.

A part that is absent, or not recognisable as itself, is a failed stage, not a
known fault. Go back and put it in.

## The stages

Each stage narrows a different freedom, and each is cheap to fix while the next
is expensive. A stage may not begin until the previous gate is true, verified
by looking at a render. And no part may be more than one stage ahead of any
other. Walk the inventory and check, because the instruments reward neglecting
the rest of the picture: `--parts` hands you a box per feature, `--zoom` at 4x
is most legible on a face, and a describer volunteers an opinion about
expression unasked.

| # | Stage | Decides | Gate |
|---|---|---|---|
| 0 | **Read** | What the picture is | The sentence, the big shape, how the subject differs from the typical one, the light source, and `parts.json`: ranked, joints named, every entry a shape note, validated against a reader who has not seen the reading before anything is placed |
| 1 | **Gesture** | Rhythm, action, thrust | One continuous force reads. Proportion is explicitly not checked yet |
| 2 | **Envelope** | Outer extent | Four extremity points plotted; polygon (6 sides or fewer to start, one vertex per real direction change) **contains** the subject |
| 3 | **Block-in** | Structure and proportion, in straights | Landmarks placed relative to already-fixed landmarks; angles checked against the subject by overlay |
| 4 | **Construction** | 3D volume under the shape | Every form's turn stated in writing first, its centre line placed where that turn puts it, not down the middle of its box |
| 5 | **Masses** | The picture as filled areas, no line at all | `check.py --masses` beside the subject's: the two read as the same shape, said in words. Nothing drawn on top will fix them if they do not |
| 6 | **Contour** | The real edge: break the straights into curve | Curves depart from the primitives where the subject does |
| 7 | **Cleanup** | Which line is the line | Every line intended for ink exists and is right; construction is out of the final render (`build.sh` hides it) |
| 8 | **Ink** | Weight, permanence, hierarchy | None. This is the last line stage |
| 9 | **Fill** | The masses refined: shadow, blacks, flats | Structure already fixed; value cannot rescue wrong proportion |
| 10 | **Correct** | Where colour and line disagree | Ink and flats both final; every correction survives being switched off |

Registration, weights and ink-share belong to stage 9 and later. Earlier they
are a distraction that looks like rigour, and they use up the looking budget at
the stages whose whole job is to look at a shape and say what it is.

Going back to an earlier stage invalidates everything above it. A restated
contour orphans the flats that met it and the corrections aimed at where its
marks landed, so re-run every stage after the one you changed. This is also the
cheap option: the script re-renders in one call, so sending a fault back to its
own stage costs less than a pixel correction that would have to be redone
anyway.

### Straights (stages 2-3)

This is the part most likely to be skipped, and the part that most determines
whether the result looks amateur.

- Plot the four extremity points and connect them into the smallest polygon
  containing everything. A chord across a convex run cuts inside the form, and
  part of the subject outside the envelope is a failed gate, not a
  simplification.
- Subdivide in passes, each adding shorter straights at the next-largest
  direction change. Landmarks are the block-in's vertices. Place every new
  landmark relative to one already fixed, never independently by eye.
- No curve exists until the straights have been checked against the subject.
  Then round the transitions. A curve is only as good as the straight it
  replaced.
- Straights must reach the canvas densified: many close points, not two
  endpoints. Otherwise the freehand renderer smooths every corner off and hands
  back the soft blob the block-in exists to prevent. `smooth=False` does this
  for you. It selects the densifying branch of `stroke`, and does more than
  switch the curve off.

### Fill (stage 9)

Flat colour goes down as flatting: one region per distinct surface (face, neck
and collar are three regions even if they end up the same colour), with hard
aliased edges, drawn generously past where the ink will go and placed behind
it, so the line covers the fill's edge. Cutting colour exactly to a line is
something neither a hand nor a press does. Underlapping means that any
misregistration reveals more of the correct colour instead of bare paper.

Then hide the ink and look. If the flats alone no longer separate foreground
from background, the colour design has failed and no rendering will rescue it.

For value rather than colour, mass the whole shadow as one flat value first and
verify that the shape reads. Then grade inside it. Never blend first. Erase
construction before filling blacks. Detail is in `reference/colour.md`.

### Correct (stage 10)

Correcting is not more drawing. It fixes the two- and three-pixel
disagreements between marks that were each aimed correctly. They are invisible
at 1:1 and are the first thing a viewer's eye lands on. `check.py
--registration` finds them from the drawing alone. Anything wrong along its
whole length, or wrong in shape, goes back to its own stage instead. See
`reference/correcting.md`.

Stage 10 runs before anyone sees the picture, and it is not the stage to drop
when the budget is thin. If you ship without it, the faults a viewer names
first are almost exactly the ones this stage exists to catch.

Correcting is a fixed number of rounds, each aimed by the critic's list. It is
not an open-ended polish, and it is not zero rounds. Write the acceptance list
at stage 0 from the reading, fix the number of rounds then, and score every
round against that list and nothing else. A round that invents a new
measurement to score itself by has already failed. Each new number detects the
last fault and is blind to the next, so the picture regresses while the newest
metric goes green.

After that, ask one question that correcting cannot reach: does the picture
lead where the subject leads? Correcting works mark against mark. A picture can
be right part by part and still put its furniture in front of its subject, and
the furniture is not too crude, it is too loud. `--ranking` measures that. It
does not give a cheap repair here. A translucent glaze over what shouts was
tried and rejected on sight, because it makes a dirty copy of the object in
place instead of pushing it back. An object recedes when it loses its contour
and merges into the mass behind it. That decision belongs to the masses stage,
and the per-object stages never offer it. See `scene.md`. Read a large delta in
this report as a pointer to the stage that caused it, not as a repair to
attempt now.

## Checking your own work

Each check catches a class of error the others hide, so skipping one means
shipping that class.

| Check | Catches |
|---|---|
| **Masses** | The wrong shape. Both pictures are reduced to flat areas with line closed away (`--masses`, as `--only fill,frame`), so what is left is what the eye reads first. A wedge and an oval share a bounding rectangle and differ in the only way that matters, and this is the one check that tells them apart |
| **Blind description** | Your own anchoring, which nothing else here reaches. Hand the render, and only the render, to someone who has not seen the script, and ask: what shape is it, what does it express, what is the biggest thing in it. Ask the same three of the subject and compare. Never ask "is anything wrong", because a describer looking at a cartoon excuses everything as style. Use two describers and keep what they agree on. Ask it of a part crop too, since a form whose outline is right can still be the wrong shape |
| **Critic** | Quality, fused and missing parts, and the list a client would produce. Give it both images, say which is which, and ask for every way the drawing is worse as a drawing of the same thing, worst first, naming the feature and what each image does. Forbid style comments, praise, and the word "fine", and forbid guessing how the drawing was made or how to fix it. It reliably reaches the faults a viewer would name, at the right altitude: a limb ending without its extremity, a part that is simply absent. It is weaker on why. It reports a form as unidentifiable where the cause is that two forms have fused, and as misplaced where the cause is that one is shapeless. Its own contribution is junction faults nobody listed: no contact where the weight goes, an object its support does not touch, a frame that does not close. Asked for N items, it returns N items, and the tail is invention. Expect roughly a quarter to be false about the drawing, typically naming as missing a part that is drawn and filled, or asserting a crossing the geometry rules out. So ask for fewer items than you think, and verify each against the render before acting. A fault you cannot find is the critic's, not yours. The item count is not evidence |
| **Parts** | Whether each shape note is true, and the two things no other check can see: a part that is not there at all, and a part that has drifted out of its own box (`--parts parts.json`). Read MISSING? as "behind the rest" before the masses stage, and as "absent" from the masses stage on. An entry with no note is reported in red, because for that part this is a box compared to a box |
| **Verdict** | Your own failure to look. Naming a difference in words is what turns looking into seeing |
| **Detail** | Whether the marks are any good. Every other check measures placement, and at 1:1 a well-placed bad shape and a good one occupy the same box. Magnify one feature 4x with the subject above it (`--zoom x,y,w,h`) |
| **Weight** | A line hierarchy drifted from the subject's (`--weights`). Meaningless on tone |
| **Linework** | Hatching left out, and a flattened weight hierarchy (`--linework parts.json`). It reads the line marks in each box whose entry carries a `hatch` measurement and fails where the drawing has no group at that angle, then compares the span from finest to heaviest line. `--hatch BOX` prints the groups themselves. A drawing of flats with one even outline passes every other check here against a hatched subject |
| **Ranking** | An object shouting above its tier, and a junction where two forms have merged into one value (`--ranking parts.json`). It ranks the spread of value inside each part's own box and compares the drawing's order with the subject's. Alone among the numbers here it is zero-sum: adding marks everywhere leaves the order exactly where it was, so the only way to lift a part is to put another one down, which is the only move a whole-picture pass may make. Most large deltas are still upstream faults in disguise. A flat filled in the wrong colour and a merged junction have the same signature, low spread where the subject has high. Crop the part and look before believing a row |
| **Stage audit** | A drawing that skipped stages, read off the script rather than the picture: which stages exist and how many marks each holds, how many strokes carry their own `lead=`/`tail=`, the instrument mix, and the count of distinct weights against the measured span. `--stages` covers the first of these, which stages exist and how many marks each holds. A drawing inked straight off its block-in has no contour pass and every curve in it is a first attempt. One whose marks are nearly all `flat` has drawn its lines as filled shapes. Either passes every placement check here and reads as a diagram |
| **Doubled edge** | One boundary stated twice, from two guesses. It is the commonest mark-level fault in a scene and invisible to everything above, because two contours 2px apart are two correct-looking contours (`--doubled ops.json`). It reads the script: two ink strokes whose centrelines run together for a large fraction of their own length. On the page the fault reads as a field of crossing loops and tends to be diagnosed for rounds as bad curve control, which it is not. Two strokes that meet at one shared point are a junction, not a doubling, and are excluded. Counting those would punish the very construction that fixes the fault |
| **Registration** | Colour and line disagreeing: a fill short of its contour, a fill past it with nothing over it, a contour that does not close (`--registration`). It cannot work on a full-bleed picture |
| **Switch off** | Whether a correction is one. Render with the corrective stage hidden and compare at 4x. Most candidates change nothing, and then the right answer is to take the correction out and keep the fault |
| **Defeat your own eye** | Habituation, in several directions, none expensive. Use **mirror** for proportion drift, **squint** for value and mass, **silhouette** for fused forms and tangents, **negative space** for relational error (largest gap first), **plumb** for diagonals you squared toward vertical, **overlay** for exact drift against a reference, **line off** (`--hide ink`) for whether the flats carry the composition, and **big-to-small** ("am I still at big-shape scale?") |

Never compare against memory. You will silently revert to the symbol you
already believed.

**Never ask a describer to judge; ask a critic to compare; and let neither's
words be the target.** They are two instruments with two jobs. A
describer is a recognition test (blind, one image). It is good at shape,
expression, what leads, and whether the action is present. It excuses, so
asking it whether anything is wrong returns "it's stylised". A critic is a
comparison test, and it is the only thing here that sees quality. It attends to
features, so it is worse at silhouette. In one test, two describers asked only
what shape the picture is returned an arch for the subject and a wedge for the
drawing. That was the line of action, which a critic had missed fifteen items
deep. Run both.

On matters of fact the describer is the more reliable of the two. The
asymmetry is in the task: a describer reports what it sees, while a critic is
asked for faults and supplies the number requested. The describer excuses and
does not invent. The critic invents and does not excuse. Weigh their words
accordingly.

Where the two agree independently, believe them, and run both on a part crop at
4x. A face can pass at 1:1 and carry the opposite expression at 4x, which
inverts the picture's action, the one fault no placement check can reach.

The target is the shape note from the reading, and a judge's job is only to say
whether that note is now true. If you optimise to a describer's vocabulary, you
are symbol-drawing by proxy. In one case "closed eyes" became "wide-eyed" by
way of a bulging cartoon eye, and the fix that worked was aimed at the
subject's measured lid.

**`form` is a list to work through, never a gate.** It measures how much is
going on inside a box, and marks are what is going on, so adding marks raises it
whether or not the marks are right. In one test, an agent was told two cow
chests were the worst-structured boxes in the inventory and put thirteen more
contours in. The ratios rose from 0.42 to 0.53 and from 0.57 to 0.75, and the
picture got worse. The deficit was not inside those boxes. The subject's
brisket samples cow-white, so there was nothing to add there, and what was
missing was the body's dark barrel not carried far enough across. Four points
fixed what thirteen had broken. So sample the subject inside the box before
adding a mark: if it is flat, the deficit belongs to something adjacent. Read
`form` in both directions. Above 1.0 it says to take marks out, which `ink`
cannot say, and it is the only check that sees a duplicated mark (a handlebar
drawn twice 12px apart, diagnosed for rounds as a badly drawn fist).

The same hazard applies to every number in this file. A measure you can act on
becomes a target, and the cheapest way to move any mark-counting target is to
make more marks.

**Never let a whole-picture number stand in for the verdict.** Mean pixel
difference from the subject is the tempting one, and it is actively wrong.
Across one round that made a fan's cage read as a cage and a shoe's sole read
as a sole, the fan region went from 43.5 to 45.1 and the shoe region from 56.2
to 62.7. Both were worse on the number and better as a drawing. Correct marks
land where the subject has marks but never at identical coordinates, so
agreeing more can measure as agreeing less. If that number had been the score,
every good change in that round would have been reverted.

## Failure modes

These are the three with a measurement behind them. A principle restated as a
symptom is not a second finding, so do not add a row per round.

| Symptom | Name | Fix |
|---|---|---|
| A feature of the subject is simply not in the drawing: no nose, no ear, a body under a head | **Omission**, which every mark-measuring check is blind to | Run `--parts` against the inventory at every gate, then draw it. It is a failed stage, never a known fault. A face reading as monstrous is usually two or three omissions at once plus one feature at the wrong scale. A face is its parts in relation, and with one part missing the rest cannot compensate |
| The outline tracks the subject at every row and the form still reads as the wrong shape, for example a slab where the subject is a wedge | **The interior is ranked wrong**: right features, right boxes, wrong order of size, so the eye and mouth lead where the subject leads with the jaw plane | No pixel check can see it. Inflating a head's irises 2.4x with every outline point untouched moved the silhouette 0.45% and the masses 0.16 points, and `--parts` could only report that a box got darker. Ask a blind describer the three questions of that part's crop alone and compare what each of you ranks first. On the degraded drawing two describers dropped the eyes behind the helmet and read the expression as "deadpan". The eye got bigger, blacker and ranked lower: what makes a feature lead is the expression it carries, not its area. Fix by weight before size |
| Accurate, and reads as a sketch rather than a finished drawing | **You only ever looked at it at 1:1.** Placement was checked and the marks never were | Magnify one feature 4x beside the subject. Blunt-ended marks, a weight range that does not match the subject's, and lumpy silhouettes are all invisible at full size |

## Reference

The depth lives alongside this file. Load what the task needs.

**An entry is a diagnostic, never a scaffold.** The test is mechanical: if a
passage could be followed with the subject covered up, it is a scaffold.
Rewrite it as what to measure and what a difference from the typical form
means. A tutorial is dangerous here in the same way `ellipse()` is. It hands
you a finished generic form at the stage whose whole job is to find the
particular one. `[read: source]` marks a claim taken from a book: a
hypothesis with good pedigree and nothing more, from the literature and not yet
tested here. Every unmarked rule comes from
a failure that was measured on a drawing. A rule leaves this layer when a
drawing shows it wrong, and this layer only shrinks when someone decides to
shrink it.

An earlier attempt's measurements are an input to the next attempt, and a
contaminant to any test of this skill. Keep the two purposes apart. To make a
picture, read the previous attempt's notes and reading sheet before placing a
mark. This layer holds what generalises, a subject's own notes hold what is
true about that subject, and the first does not substitute for the second. To
find out whether the skill works, give the agent this layer and the subject and
nothing else. An agent handed the last attempt's fault list proves only that it
can follow a hint, not that the skill prevents the fault, and every gap the
hint covers stays hidden.

Note which way a failure points before reacting to it. A fault that sat
measured in the previous attempt's notes is an argument for reading them. A
fault that this layer already names in writing, and that an agent shipped
anyway, is an argument that naming a failure is not the same as saying what to
draw instead.

**A gap here is not a licence to outline.** For a long time `head.md` was the
only entry teaching how to build anything, and two agents independently spent
their whole budget on the face and outlined everything else. They were not
drawn to faces. The face was the only thing the skill knew how to construct.
Still missing: perspective and receding planes, manufactured form, water and
reflections, architecture and interiors, foliage.

- `measuring.md`: comparative measurement, sighting, plumb lines, units,
  sight-size vs comparative, negative shape
- `head.md`: skull, planes, the canon to measure a departure from, features as
  constructed forms
- `figure.md`: the three masses and the spine between them, the shoulder girdle
  riding on the ribcage, where the thigh actually leaves the pelvis,
  foreshortening, the cyclist, and cloth as folds with a cause
- `scene.md`: how a scene differs from a single subject: ranking objects into
  tiers, budgeting construction before the first mark, and the overlaps between
  objects, which is where every scene tested here has failed
- `bicycle.md`: frame geometry, the tube weight swatch, wheels in perspective,
  the three rider contacts, drawing occlusion in a lattice
- `quadruped.md`: the animal as one mass, the ribcage barrel and the
  clavicle-less scapula, the ungulate leg and why its backwards knee is an ankle,
  head and horn insertion, keeping a herd from twinning
- `hands-and-feet.md`: the palm box and the thumb mass, the knuckle arcs,
  fingers as three-segment cylinders that never taper to a point, the foot as a
  wedge on a tripod, the shoe as a form over it
- `tone.md`: continuous tone as marks: the stripe failure, anchoring a tonal
  pass, which instruments accumulate, why texture cannot be cut into a path
- `light.md`: light anatomy, the two value groups, planes, edges, cross-contour,
  how line alone describes volume
- `line.md`: weight hierarchy, what decides weight, inking order, blacks
- `colour.md`: flatting, trapping under the line, the line-off test, cel
  shading, limited palettes
- `correcting.md`: what a corrective pass may not do, aiming a trim, proving one
  by switching it off, finding faults with the registration flood
- `redrawing.md`: redrawing a generated image rather than a photograph or a
  life subject: the exact palette and posterised read it hands you for free, why
  its edges invert `scene.md`'s rule, the measuring traps its flat regions set,
  and the parts of it that must not be copied

## The canvas

`harness/` is a tldraw canvas driven from the command line. The document on disk
is the drawing. It persists between calls and opens in tldraw for a person to
edit by hand afterwards.

```bash
node harness/cli.mjs DOC.json --ops OPS.json --png LOOK.png [--scale 2] [--flip] [--squint 6]
python3 check.py LOOK.png --ref SUBJECT.png --out CHECK.png   # one look, four panels
```

Set it up once with `cd harness && npm install && npm run build && npx playwright install chromium`.
Rebuild after editing `harness/src/main.jsx`, because the CLI serves the built
bundle.

Write every render and every check beside the drawing, never into `/tmp`. When
two drawings are worked on at once they share that directory, and a check is
written and read back a moment later, so one drawing can overwrite the other's
in between. The file names here are unqualified for the same reason: qualify
them with the drawing's own directory.

`pen.py` renders your decisions. You choose the control points, which is the
drawing. It interpolates and varies pressure, which is the hand. Its
docstrings carry the traps: corners need `smooth=False`, `closed=True` must not
repeat its first point, `fill="solid"` is a tint, and flats need `tool="flat"`.
The header of `cli.mjs` carries the flag traps: `--only` needs `frame` in the
list, `--padding 0` clips as well as pins, and `--palette` repoints the ground.

**Measure the ground.** It is a palette entry with a right answer, and
everything sitting on it is judged by its contrast with it. In one picture the
ground was eleven levels too light for six rounds. Nothing looked wrong, but a
whole object failed to separate from the wall it hung on, and one line fixed it
with no marks touched (structure 0.39 to 1.01). A wrong ground flattens every
relationship at once and is invisible to every check that compares marks.

**Draw a weight swatch before you trust a weight.** Draw one stroke per `nib=`,
render it, and read it back with `--weights`. Draw it with the instrument you
will use, because each `tool=` has its own weights and nothing in the numbers
says so. In one test a swatch measured with `brush` and applied with `flat`
came out at 0.42x: a top tube 5px wide where 12px was asked for, and a whole
bicycle that arrived at `bicycle.md`'s "reads as wire" failure.

**Then measure the width you are about to ask for, on the subject, mark by
mark.** A calibrated swatch only guarantees that you get the number you asked
for, and the number is the half that gets guessed. For example, on one small
head two marks were each placed exactly where they were measured to belong. A
silhouette asked for at 9px, where the subject's outline measures 4-5px,
rendered its horns as solid black hooks. An eyelid bar asked for at 7.5px,
where the subject's measures 4px, covered the white of the eye beneath it and
took the expression with it. Every placement check passed both. The swatch is
calibration, and the width of this mark is a measurement. Skipping it is the
same error as guessing a landmark.

**Try the next step up before you record a limit.** A mark that will not reach
its measured width is a real constraint worth writing down, but only after the
heavier weights have actually been asked for. One drawing recorded in its own
script that the instrument could not draw a band wider than a few pixels, and
that a wire-thin tyre was therefore a limit of the tool. The next size up
rendered the tyre at the measured width on the first try. An assumed limit is
worse than an assumed number, because it gets written down as a fact about the
tool and nobody measures it again.

### The drawing is a script, not a program

Write every mark on its own line, with its own numbers. Use no function that
generates a shape, no loop that stamps one seven times, and no geometry
computed from an angle.

The principle under this is that no tool may supply a form you did not choose
after looking. A supplied form arrives free of charge at exactly the stage
whose job is to find the particular one. A head built on a computed ball with a
centre line down the middle came out with every feature inside its correct box
and was not a face. The test is whether the call could produce a shape the
subject does not have. An `ellipse()` can, so there is no `ellipse()`. A fill
bounded by a contour you drew by hand cannot, so derivation of that kind is
fair where a verb for it exists.

A flat script also forces a look at every mark. Where it does not force one,
as with a coordinate retyped from a box, it is pure cost.

**A measuring program is fair, and a drawing program is not.** Scans, traces
and row chains are how the subject is seen exactly, and what they hand back is
numbers you read. Once a program's output is the op list, with ink skeletonised
off the subject and emitted a stroke per segment, or flats emitted a region at
a time, nothing in the drawing was chosen, and so nothing in it can be sent
back to its stage. A picture built that way passed every gate and was a
vectorised copy with the tracer's artefacts in it.
`pen.write` refuses strokes called from another file, stamped by one call site,
or whose points are not written as numbers in the script.

**One geometry, evolved.** Measure every point once, name it once, and keep it
in one dict. Strokes then name points and never retype a coordinate. Where two
objects share an edge, they share the entry.

That looks like the computed geometry this rule forbids, but it is not. Apply
the test, not the rule. A dict of measured points supplies no form. It can only
remove a contradictory second copy of a point you already chose, so it cannot
produce a shape the subject does not have. Say as much in the script, because
the next reader will reach for the rule and not the test.

It fixes the doubled edge, and it does so structurally: with one entry per
adjacency the fault cannot recur, where a rule against it can only be
remembered. What it removes is the second guess, not the overshoot. A hand runs
on past an open stroke's endpoints, so two strokes meeting at one named point
each run on into the other and rebuild a dozen pixels of the doubled edge. Damp
`hand=` on the strokes that meet.

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
`fill`, `mend`, `correct`, `frame`), which lets `--hide` switch a stage off to
see what it is really doing. `build.sh` renders `drawing.png` with gesture,
construction, block-in and contour hidden, so the pencil never reaches the
final render and nothing needs erasing. `tool=` picks how the mark is made:
`pen` (dead uniform), `brush` (swings thin to thick), `marker` (translucent,
overlaps darken), `crayon` (broken grainy passes), `flat` (opaque regions), and
`gouache` (opaque body colour, the only instrument that goes on top of dry
ink). `nib=` picks the weight: `hairline fine medium bold heavy`.

A correction is not a special kind of mark, and there is no function that makes
one. It is the same `stroke`, with a different pigment and a different stage.
