# The method

You make every mark. Nothing here generates a picture. You decide where each
stroke goes, put it on a canvas, look at what appeared, and correct it.

## Contents

- The principles
- Reading the subject
- The stages
- Checking your own work
- Failure modes
- Reference
- The canvas

Putting a mark down is easy. The hard part is knowing where it goes, and almost
everything below is a way to see the subject more accurately or to catch an
error you have stopped being able to see.

## The principles

Everything else in this file applies these. When a situation is not covered,
reason from them.

1. **Look, and describe what you see as shapes.** Write each thing as a sentence
   about its shape: *the upper lid comes down as a shallow arc that
   cuts the top off the iris; no white above the pupil.* Do not write
   `eye (524-560, 320-348)`. A check can only verify what your description
   stated, and a box can only be compared with another box. One agent described
   a body in sentences and a face in boxes: the body came out right and the face
   monstrous. Measuring confirms where a described shape sits; it cannot describe
   the shape for you.
2. **Work on the whole before any part, in placement and in stage, but do not
   spend equally on every part.** No area gets ahead of the rest. If you run
   out of time, deliver a complete drawing at an earlier stage, never one
   finished corner on a blocked-in remainder. Yet on an 81-part scene, advancing
   every part equally gave 81 equally shallow parts, with a background prop
   built as far as the figure's shoulder. Decide at stage 0 how far each part is
   built within a stage, and make it unequal (`reference/scene.md`).
3. **Commit late.** Do the cheap, reversible things first, in this order:
   gesture, straights, curve, ink, black.
4. **Measure what can be measured, and check what can be checked.** A straight
   line has an angle and a length you can verify. A curve has neither, so it can
   only be judged by eye, and your eye is what you cannot yet trust. This is why
   the block-in is made of straight lines.
5. **Form before edge.** Every mark must describe an implied volume. A traced
   silhouette records the 2D boundary from one angle; nothing in it can
   contradict anything else, so you cannot tell when it is wrong or correct it.
   Draw a tube as a solid and a ring as a band, never as outlines.
6. **Keep two value groups that never overlap.** Everything in light is lighter
   than everything in shadow. Decide the split before any tone, and keep a real
   gap between the groups.
7. **Vary how marks are made; keep the structure fixed.** Weight, curvature,
   spacing, detail density and each stroke's path should vary, because a hand
   cannot repeat itself. Proportion, landmarks and identity markers must not. If
   you randomise the structure, the drawing falls apart.
8. **Never mirror.** Mirroring doubles one half's departure from the typical
   form and erases the other's, and that asymmetry carries the likeness. Place
   each side's points separately, not as a mirrored copy with noise. Give each
   character a fixed set of asymmetries and repeat them in the same place every
   time, as model-sheet data. Prefer an off-axis view, where symmetry is
   geometrically impossible.
9. **Use ways of looking that get past your own eye, and have someone who has
   not seen the script look too.** You cannot forget the coordinates you typed.
   Asked what your drawing shows, you answer with what you meant it to show, and
   the two agree because both come from the same numbers: hundreds of lines
   about three-pixel spills and not one sentence about what the face looks like.
   No judge may have seen the script: not you, and not a coordinator scoring a
   drawing against numbers it wrote itself.
10. **Work in small increments and look after each one.** "Write the stage, then
    render" is still a batch: a stage written without looking bakes in a dozen
    errors that then have to be unpicked together. Never retype a coordinate
    from memory; measure it again. A contour retyped from memory lands about
    10px off, and every fill that met it now shows a gap. That is how a
    correctly measured brow ended up inverted.

## Reading the subject

Do this in writing, before touching the canvas. `Read` the reference image
first, and measure it rather than relying on your impression.

1. **What is this a picture of?** Answer in one sentence: what should the viewer
   notice first? Everything below is ranked against that answer.
2. **The big shape**, as one or two simple forms. If you cannot say it in a
   sentence, you have not looked yet.
3. **The line of action**: the single curve that carries the movement.
4. **How this subject differs from the typical one.** That difference is the
   likeness. Measure it (`reference/measuring.md`). If you set up the typical
   form first, you will draw the typical form and then decorate it. Exaggerate
   each feature in its own direction: a big nose gets bigger, a small mouth gets
   smaller, and pushing everything cancels the contrast. Mild exaggeration works
   better than extreme, and overshooting harms the likeness as much as
   undershooting.
5. **The light source.** Decide it now and never move it.
6. **The two value groups**, then the three-value plan. Two objects on
   different depth planes must never share a value, or they merge into one
   plane.
7. **What you will leave out.** An omission you chose is economy; one you did
   not notice is a failure. Economy applies to texture, detail and variation
   inside a form. It never removes an object a viewer would name: a small figure
   can be drawn with few marks, but it must be drawn.
8. **The inventory**, below.

### The inventory: name the parts, then look for them

Write the inventory before the first mark. Every check that measures marks is
blind to marks that are not there: a missing nose has no pixels, so a face
without one passes them all. In earlier tests, a rider with no nose and no ear
and a herd of cows with heads and no bodies shipped with every mechanical gate
passing.

Each entry is a **shape note** with a box derived from it, taken from the
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

Write the note first and read the box off the shape it describes, never the
reverse. A bare `"nose": [540, 336, 45, 50]` still loads, because five drawings
on disk use it, but do not write new entries like it: it says where a part is
and not what it is, so the check passes anything of the right size in the right
place.

**Validate your reading before you place anything.** Every target in this skill
(these boxes, the zoom crops, the colour count for the masses) is a number you
typed with the same eye the check exists to test, so it catches slips but never
misreadings: a moustache boxed 30px short passed the absence check on the wrong
region. So crop the subject to each box, show the crop to a reader who has not
seen your reading, ask what it is, and correct the note and box against the
answer. Do this for every tier-1 and tier-2 entry, not a sample, and treat "I
can't tell what this is" as the most useful answer it can give. Then write the acceptance list for the finished
drawing from the reading, and do not change it afterwards.

This is also the only check that can remove a part. Wherever the subject lacks
something its category normally has, you will write an entry for it anyway,
because your idea of the typical thing fills the gap. That entry carries through
the block-in, the flats, the overlaps table and the depth order, and reaches the
critic as a drawn object. No mechanical check catches it: `--parts` reports the box as present and busy, the masses see a few dark pixels
inside a dark region, overlay sees an object inside the union of its
neighbours, and registration sees it trapped and closed. A critic invents the
same object for the same reason.

**The box exists for the check to crop with. Never draw to it.** The note is
the target, but the box is the only number in the entry, and a hand placing a
mark reaches for the number. A flat drawn to its box shows up as two faults that
look unrelated: a departure from its own mode near 0.00 at the masses gate
("uniform inside its own box"), and later a large ink excess in the same box.
It survives correction rounds because the corrections aim at the box too.

Then at every gate run:

```bash
python3 check.py drawing.png --ref subject.png --parts parts.json --out parts.png
```

It shows the subject above and the drawing below, with the note printed over
each pair. For each part, ask whether the note is true of the drawing. Where it
is not, write one line on what the subject does and one on what the drawing
does. If you cannot name a difference, you have not looked.

**Name the junctions as well as the things**, as ordinary entries with their
own notes. Every scene tested here has failed at its junctions. An inventory of
nouns produces a drawing of nouns stuck together, and a junction is the gap or
overlap between two boxes, where no check looks unless it is named. Examples are hand/handlebar, foot/pedal, hip/saddle and tyre/floor
(`reference/scene.md`), and, within a body, the shoulder, elbow, hip, knee,
wrist, ankle and the segments between them. An 81-part inventory that named no
joint, splitting surfaces finer instead, produced a figure with no shoulder, no
elbow, and an arm that widened toward the wrist. A 74-part list for a similar
picture named `R upper arm` and `L elbow`, and had the better arms. Naming more
joints helps more than splitting surfaces finer.

**Keep the inventory small and ranked** against the sentence from step 1. A
flat list gives a wall clock and a face equal standing, which principle 2 rules
out.

A part that is absent, or not recognisable as itself, is a failed stage, not a
known fault. Go back and put it in.

## The stages

Each stage settles a different decision, cheap to fix then and expensive at
the next. A stage may not begin until the previous gate is met, verified by
looking at a render, and no part may be more than one stage ahead of any other.
Walk the inventory to check, because the tools pull you towards neglecting the
rest of the picture: `--parts` hands you a box per feature,
`--zoom` at 4x reads best on a face, and a describer offers opinions about
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
| 8 | **Ink** | Weight, permanence, hierarchy | No edge drawn twice and no stage skipped (`--doubled`, `--stages`); no line stopping just short of what it meets (`--joins`); the line weights match the subject's (`--linework`). This is the last line stage |
| 9 | **Fill** | The masses refined: shadow, blacks, flats | Structure already fixed; value cannot rescue wrong proportion |
| 10 | **Correct** | Where colour and line disagree | Ink and flats both final; every correction survives being switched off |

Registration, weights and ink share belong to stage 9 and later. Earlier they
are a distraction that looks like rigour, and they use up looking time at the
stages whose whole job is to look at a shape and say what it is.

Going back to an earlier stage invalidates everything after it: a restated
contour strands the flats that met it and the corrections aimed at its marks, so
re-run every later stage. It is also cheaper, since the script re-renders in one
call and a pixel correction would have to be redone anyway.

### Straights (stages 2-3)

This is the step most often skipped, and the one that most decides whether the
result looks amateur.

- Plot the four extremity points and connect them into the smallest polygon
  that contains everything. A chord across a convex run cuts inside the form.
  Any part of the subject outside the envelope fails the gate; it is not a
  simplification.
- Subdivide in passes, each adding shorter straights at the next-largest
  change of direction. Landmarks are the block-in's vertices. Place every new
  landmark relative to one already fixed, never independently by eye.
- Draw no curve until the straights have been checked against the subject. Then
  round the transitions. A curve is only as good as the straight it replaced.
- Straights must reach the canvas densified, as many close points rather than
  two endpoints. Otherwise the freehand renderer smooths every corner off and
  hands back the soft blob the block-in exists to prevent. `smooth=False` does
  this for you: it selects the densifying branch of `stroke`, which does more
  than switch the curve off.

### Fill (stage 9)

Lay flat colour down as flatting: one region per distinct surface (face, neck
and collar are three regions even if they end up the same colour), with hard
aliased edges, drawn generously past where the ink will go and placed behind
it, so the line covers the fill's edge. Neither a hand nor a printing press cuts
colour exactly to a line. With the colour running under the line, any
misregistration shows more of the right colour instead of bare paper.

Then hide the ink and look. If the flats alone no longer separate foreground
from background, the colour design has failed and no rendering will rescue it.

For value rather than colour, mass the whole shadow as one flat value first and
check that the shape reads. Then grade inside it. Never blend first. Erase
construction before filling blacks. Details are in `reference/colour.md`.

### Correct (stage 10)

Correcting is not more drawing. It fixes the two- and three-pixel disagreements
between marks that were each aimed correctly. They are invisible at 1:1 and are
the first thing a viewer's eye lands on. `check.py --registration` finds them
from the drawing alone. Anything wrong along its whole length, or wrong in
shape, goes back to its own stage instead. See `reference/correcting.md`.

Stage 10 runs before anyone sees the picture. Do not drop it when the budget is
thin: without it, the faults a viewer names first are almost exactly the ones
this stage exists to catch.

Correcting is a fixed number of rounds, each aimed by the critic's list: not
open-ended polishing, and not zero rounds. Fix the number of rounds at stage 0,
alongside the acceptance list, and score every round against that list and
nothing else. A round that invents a new measurement to score itself by has
already failed: each new number detects the last fault and is blind to the
next, so the picture gets worse while the newest metric passes.

Then ask one question correcting cannot answer: does the picture lead the eye
where the subject does? A picture can be right part by part and still put its
furniture ahead of its subject, because the furniture is too prominent, not too
crude. `--ranking` measures this, and there is no cheap repair at this point. A
translucent glaze over the prominent object was tried and rejected on sight: it
makes a dirty copy in place instead of pushing the object back. An object
recedes when it loses its contour and merges into the mass behind it, a
decision that belongs to the masses stage (see `scene.md`). Read a large delta
in this report as a pointer to the stage that caused it, not a repair to make
now.

## Checking your own work

Each check catches a kind of error the others miss, so skipping one means
shipping that kind of error.

| Check | Catches |
|---|---|
| **Masses** | The wrong shape. Both pictures are reduced to flat areas with the lines removed (`--masses`, as `--only fill,frame`), leaving what the eye reads first. A wedge and an oval share a bounding rectangle, and this is the one check that tells them apart |
| **Blind description** | Your own anchoring, which nothing else here reaches. Hand only the render to someone who has not seen the script and ask: what shape is it, what does it express, what is the biggest thing in it. Ask the same of the subject and compare. Never ask "is anything wrong": a describer looking at a cartoon excuses everything as style. Use two describers and keep what they agree on. Ask about a part crop too, since a form with the right outline can still be the wrong shape |
| **Critic** | Quality, fused and missing parts, and the list a client would produce. Give it both images, say which is which, and ask for every way the drawing is worse as a drawing of the same thing, worst first, naming the feature and what each image does. Forbid style comments, praise and the word "fine", and forbid guessing how the drawing was made or how to fix it. It reliably finds the faults a viewer would name (a limb ending without its extremity, a part simply absent) and junction faults nobody listed (no contact where the weight goes, an object its support does not touch, a frame that does not close). It is weaker on causes: it calls a form unidentifiable when two forms have fused, and misplaced when one is shapeless. Asked for N items, it returns N, and the tail is invented: expect roughly a quarter to be false, typically a part named as missing that is drawn and filled, or a crossing the geometry rules out. So ask for fewer items than you think and verify each against the render before acting. If you cannot find a fault it names, the error is the critic's. The number of items is not evidence |
| **Parts** | Whether each shape note is true, and two things no other check can see: a part that is not there at all, and a part that has drifted out of its own box (`--parts parts.json`). Before the masses stage, read MISSING? as "behind the rest"; from the masses stage on, as "absent". An entry with no note is reported in red, because for that part this is a box compared to a box |
| **Verdict** | Your own failure to look. Naming a difference in words is what turns looking into seeing |
| **Detail** | Whether the marks are any good. Every other check measures placement, and at 1:1 a well-placed bad shape and a good one occupy the same box. Magnify one feature 4x with the subject above it (`--zoom x,y,w,h`) |
| **Weight** | A line hierarchy that has drifted from the subject's (`--weights`). Meaningless on tone |
| **Linework** | Missing hatching, and a flattened weight hierarchy (`--linework parts.json`). It reads the line marks in each box whose entry carries a `hatch` measurement and fails where the drawing has no group at that angle, then compares the span from finest to heaviest line. `--hatch BOX` prints the groups themselves. A drawing of flats with one even outline passes every other check here against a hatched subject |
| **Ranking** | An object standing out more than its tier allows, and a junction where two forms have merged into one value (`--ranking parts.json`). It ranks the spread of value inside each part's own box and compares the drawing's order with the subject's. Unlike the other numbers here it is zero-sum: adding marks everywhere leaves the order where it was, so the only way to lift a part is to tone another down, which is the only move a whole-picture pass may make. Most large deltas are earlier-stage faults in disguise: a flat in the wrong colour and a merged junction share one signature, low spread where the subject has high. Crop the part and look before believing a row |
| **Stage audit** | A drawing that skipped stages, read off the script rather than the picture: which stages exist and how many marks each holds, how many strokes carry their own `lead=`/`tail=`, the mix of instruments, and the number of distinct weights against the measured span. `--stages` covers the first of these. A drawing inked straight off its block-in has no contour pass, and every curve in it is a first attempt. One whose marks are nearly all `flat` has drawn its lines as filled shapes. Either passes every placement check here and reads as a diagram |
| **Doubled edge** | One boundary drawn twice, from two guesses: the commonest mark-level fault in a scene, and invisible to everything above, because two contours 2px apart look like two correct contours (`--doubled ops.json`). It reads the script for two ink strokes whose centrelines run together for a large fraction of their length. On the page it looks like a field of crossing loops and is often misdiagnosed for rounds as poor curve control. Two strokes meeting at one shared point are a junction and are excluded, since counting them would penalise the construction that fixes the fault |
| **Registration** | Colour and line disagreeing: a fill short of its contour, a fill past it with nothing over it, a contour that does not close (`--registration`). It cannot work on a full-bleed picture |
| **Switch off** | Whether a correction really is one. Render with the corrective stage hidden and compare at 4x. Most candidates change nothing, and then the right answer is to take the correction out and keep the fault |
| **Defeat your own eye** | Habituation, attacked from several directions, none expensive. Use **mirror** for proportion drift, **squint** for value and mass, **silhouette** for fused forms and tangents, **negative space** for errors in relationships (largest gap first), **plumb** for diagonals you have pulled toward vertical, **overlay** for exact drift against a reference, **line off** (`--hide ink`) for whether the flats carry the composition, and **big-to-small** ("am I still working at the big-shape scale?") |

Never compare against memory. You will silently fall back to the symbol you
already believed in.

**Ask a describer to describe, never to judge; ask a critic to compare; and
never treat either one's words as the target.** A describer is a recognition
test: blind, one image. It is good at shape, expression, what leads, and whether
the action is present, and more reliable on matters of fact, because it reports
what it sees; but it excuses faults as "stylised". A critic is a comparison test
and the only thing here that judges quality. It attends to features, so it is
worse at silhouette, and because it is asked for faults it supplies the number
requested. So the describer excuses but does not invent, and the critic invents
but does not excuse. Run both: in one test two describers, asked only what shape the picture
was, said an arch for the subject and a wedge for the drawing. That was the line
of action, which a critic had listed fifteen items down.

Where the two agree independently, believe them. Run both on a part crop at 4x
as well: a face can pass at 1:1 and carry the opposite expression at 4x, which
inverts the picture's action, a fault no placement check can reach.

The target is the shape note from the reading; a judge only says whether that
note is now true. Drawing towards a describer's vocabulary is drawing symbols at
one remove: "closed eyes" once became "wide-eyed" through a bulging cartoon eye,
and the fix that worked was aimed at the subject's measured lid.

**`form` is a to-do list, never a gate.** It measures how much is going on
inside a box, so adding marks raises it whether or not they are right. An
agent told that two cow chests were the worst-structured boxes added thirteen
contours: the ratios rose from 0.42 to 0.53 and from 0.57 to 0.75, and the
picture got worse. The subject's brisket samples cow-white, so nothing belonged
there; what was missing was the body's dark barrel, not carried far enough
across, and four points fixed it. So sample the subject inside the box before
adding a mark; if it is flat, the deficit belongs to something next to it. Read `form`
in both directions. Above 1.0 it says to take marks out, which `ink` cannot
say, and it is the only check that sees a duplicated mark (a handlebar drawn
twice 12px apart, misdiagnosed for rounds as a badly drawn fist).

The same hazard applies to every number in this file. A measure you can act on
becomes a target, and the cheapest way to move a target that counts marks is to
make more marks.

**Never let a whole-picture number stand in for the verdict.** The tempting one
is mean pixel difference from the subject, and it misleads. In one round that
made a fan's cage read as a cage and a shoe's sole as a sole, the fan region went
from 43.5 to 45.1 and the shoe region from 56.2 to 62.7. Correct marks land
where the subject has marks but never at identical coordinates, so closer
agreement can measure as worse, and scoring by that number would have reverted
every good change.

## Failure modes

These are the three with a measurement behind them. A principle restated as a
symptom is not a new finding, so do not add a row each round.

| Symptom | Name | Fix |
|---|---|---|
| A feature of the subject is simply not in the drawing: no nose, no ear, a body under a head | **Omission**, which every mark-measuring check is blind to | Run `--parts` against the inventory at every gate, then draw it. It is a failed stage, never a known fault. A face that reads as monstrous usually has two or three omissions plus one feature at the wrong scale. A face is its parts in relation, and with one part missing the rest cannot compensate |
| The outline tracks the subject at every row and the form still reads as the wrong shape, for example a slab where the subject is a wedge | **The interior is ranked wrong**: right features, right boxes, wrong order of size, so the eye and mouth lead where the subject leads with the jaw plane | No pixel check can see it: enlarging a head's irises 2.4x with every outline point untouched moved the silhouette 0.45% and the masses 0.16 points, and `--parts` only reported a darker box. Ask a blind describer the three questions about that part's crop alone, and compare what each of you ranks first. On that enlarged drawing two describers ranked the eyes below the helmet and read the expression as "deadpan": the eye got bigger and blacker and ranked lower, because a feature leads by the expression it carries, not its area. Fix by weight before size |
| Accurate, but reads as a sketch rather than a finished drawing | **You only ever looked at it at 1:1.** Placement was checked and the marks never were | Magnify one feature 4x beside the subject. Blunt-ended marks, a weight range that does not match the subject's, and lumpy silhouettes are all invisible at full size |

## Reference

The detail lives in the files beside this one, the reference layer. Load what
the task needs.

**A reference entry says what to look for; it never hands you a form to copy.**
The test is mechanical: a passage that could be followed with the subject
covered up is a recipe. Rewrite it as what to measure and what a difference
from the typical form means. A tutorial is dangerous for the same reason as
`ellipse()`: it hands you a finished generic form at the stage whose job is to
find the particular one. `[read: source]` marks a claim taken from a book, a
well-sourced hypothesis not yet tested here. Every unmarked rule comes from a
failure measured on a drawing. Remove a rule when a drawing shows it wrong;
otherwise the reference layer only shrinks when someone deliberately decides to
shrink it.

An earlier attempt's measurements help the next attempt and spoil any test of
this skill. To make a picture, read the previous attempt's notes and reading
sheet before placing a mark: the reference layer holds what generalises, a
subject's notes hold what is true of that subject, and the first does not
replace the second. To test the skill, give the agent the reference layer and
the subject and nothing else. An agent handed the last fault list proves only
that it can follow a hint, and hides every gap the hint covers.

Before reacting to a failure, note what it tells you. A fault already measured
in the previous attempt's notes argues for reading them. A fault the reference
already names, shipped anyway, shows that naming a failure is not the same as
saying what to draw instead.

**Where the reference has no entry, do not fall back to outlining.** While
`head.md` was the only entry teaching how to build anything, two agents
independently spent their whole budget on the face and outlined everything
else: the face was the only thing the skill knew how to construct. Still
missing: perspective and receding planes, manufactured form, water and
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
- `colour.md`: flatting, trapping under the line, hiding the ink to test the
  flats, cel shading, limited palettes
- `correcting.md`: what a corrective pass may not do, aiming a trim, proving one
  by switching it off, finding faults with the registration flood
- `redrawing.md`: redrawing a generated image rather than a photograph or a
  life subject: the exact palette and posterised reading it gives you for free,
  why its edges invert `scene.md`'s rule, the measuring traps its flat regions
  set, and the parts of it that must not be copied

## The canvas

`harness/` is a tldraw canvas driven from the command line. The document on disk
is the drawing. It persists between calls, and a person can open it in tldraw to
edit by hand afterwards.

```bash
node harness/cli.mjs DOC.json --ops OPS.json --png LOOK.png [--scale 2] [--flip] [--squint 6]
python3 check.py LOOK.png --ref SUBJECT.png --out CHECK.png   # one look, four panels
```

Set it up once with `cd harness && npm install && npm run build && npx playwright install chromium`.
Rebuild after editing `harness/src/main.jsx`, because the CLI serves the built
bundle.

Write every render and check beside the drawing, never into `/tmp`: two
drawings worked on at once would share it, and one can overwrite the other's
check between writing and reading it back. For the same reason, prefix the bare
file names in this file with the drawing's own directory.

`pen.py` renders your decisions. You choose the control points, which is the
drawing; it interpolates and varies pressure, which is the hand. Its docstrings
list the traps: corners need `smooth=False`, `closed=True` must not repeat its
first point, `fill="solid"` is a tint, and flats need `tool="flat"`. The header
of `cli.mjs` lists the flag traps: `--only` needs `frame` in the list,
`--padding 0` clips as well as pins, and `--palette` changes the ground colour.

**Measure the ground.** It is a palette entry with a right answer, and
everything on it is judged by its contrast with it. In one picture the ground
was eleven levels too light for six rounds: nothing looked wrong, but an object
failed to separate from the wall it hung on. One line fixed it without touching
any mark (structure 0.39 to 1.01). A wrong ground flattens every
relationship at once and is invisible to every check that compares marks.

**Draw a weight swatch before you trust a weight.** Draw one stroke per `nib=`,
render it, and read it back with `--weights`. Use the instrument you will draw
with, because each `tool=` has its own weights and nothing in the numbers says
so. In one test a swatch measured with `brush` and applied with `flat` came out
at 0.42x: a top tube 5px wide where 12px was asked for, and a bicycle that ended
up with `bicycle.md`'s "reads as wire" failure.

**Then measure on the subject the width you are about to ask for, mark by
mark.** A calibrated swatch only guarantees you get the number you asked for;
the number itself is what gets guessed. On one small head, two marks were placed
exactly where measured. A silhouette asked for at 9px, where the subject's
outline measures 4-5px, turned the horns into solid black hooks. An eyelid bar
asked for at 7.5px, where the subject's measures 4px, covered the white of the
eye and took the expression with it. Every placement check passed both. Skipping
this measurement is the same error as guessing a landmark.

**Try the next weight up before you record a limit.** A mark that will not reach
its measured width is a real constraint, but write it down only after trying the
heavier weights. One script recorded that the instrument could not draw a band
wider than a few pixels, so a wire-thin tyre was a limit of the tool; the next
size up drew the tyre at the measured width first time. An assumed limit is
worse than an assumed number, because it is recorded as a fact about the tool
and nobody measures it again.

### The drawing is a script, not a program

Write every mark on its own line, with its own numbers. Use no function that
generates a shape, no loop that stamps one seven times, and no geometry
computed from an angle.

The principle behind this is that no tool may supply a form you did not choose
after looking. A supplied form arrives free at exactly the stage whose job is to
find the particular one: a head built on a computed ball with a centre line down
the middle came out with every feature inside its correct box, and was not a
face. The test is whether the call could produce a shape the subject does not
have. An `ellipse()` can, so there is no `ellipse()`. A fill bounded by a
contour you drew by hand cannot, so deriving a fill that way is fine where a
function for it exists.

A flat script also forces you to look at every mark. Where it does not, as with
a coordinate retyped from a box, it is pure cost.

**A measuring program is fine; a drawing program is not.** Scans, traces and
row chains see the subject exactly and return numbers you read. Once a program's
output becomes the op list (ink skeletonised off the subject one stroke per
segment, or flats emitted a region at a time), nothing in the drawing was
chosen, so nothing can be sent back to its stage. A picture built that way
passed every gate and was a vectorised copy, tracer's artefacts included. `pen.write` refuses strokes called from
another file, stamped out by one call site, or whose points are not written as
numbers in the script.

**Keep one geometry and evolve it.** Measure every point once, name it once, and
keep it in one dict. Strokes then refer to points by name and never retype a
coordinate. Where two objects share an edge, they share the entry.

This looks like the computed geometry forbidden above, but apply the test, not
the rule: a dict of measured points supplies no form. It only removes a
contradictory second copy of a point you chose, so it cannot produce a shape the
subject does not have. Say so in the script, because the next reader will reach
for the rule and not the test.

The dict fixes the doubled edge structurally: with one entry per adjacency the
fault cannot recur, whereas a rule against it can only be remembered. It removes
the second guess but not the overshoot. A hand runs on past an open stroke's
endpoints, so two strokes meeting at one named point each run on into the other
and rebuild a dozen pixels of doubled edge. Reduce `hand=` on the strokes that
meet.

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

A correction is not a special kind of mark, and no function makes one. It is the
same `stroke`, with a different pigment and a different stage.
