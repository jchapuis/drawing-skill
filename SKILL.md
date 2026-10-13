---
name: drawing
description: Draw a subject by hand on a real canvas, one mark at a time. You look at the subject, block it in with straight lines, check each stage with a tool before the next, and only then draw curves, ink and blacks. Use when asked to draw, sketch, illustrate, redraw or restyle an image by hand rather than generate it with an image model.
---

# Drawing

You place every mark. The tools measure the subject, render what you placed,
and refuse ink in a drawing that has no gesture, block-in or contour stage. The
judge is a blind describer, an agent that has seen neither the subject nor your
script.

Placing a mark is easy; knowing where it goes is the work. Every instrument here
either helps you see the subject more exactly or catches an error you have
stopped noticing. `reference/method.md` holds the full method and the failure
behind each rule. `reference/scene.md` explains what a scene is and why it is
more than a sum of objects. Load them when a gate fails and you cannot say why,
not instead of drawing.

## Terms

- **Gesture**: a few loose strokes that capture the action of the whole figure or object before any detail.
- **Line of action**: the main curve the gesture follows, the direction of the movement or pose.
- **Armature**: the skeleton of main lines (eye level, ground, axes) the masses hang on.
- **Block-in**: the subject's regions drawn as straight-edged shapes, to fix placement and proportion before curves.
- **Value**: how light or dark something is, apart from its colour.
- **Value group**: the set of values that belong together (the lit and shaded versions of one surface). A drawing has two groups that must not overlap.
- **Flats**: areas of one uniform colour, filled in without shading.
- **Trapping**: drawing a flat slightly past where its ink will go, so no gap shows between fill and line.
- **Lost and found edges**: a lost edge fades into what is behind it; a found edge is crisp. Losing most edges is how a form is pushed back.
- **Massing**: treating forms as simple shapes of one value. A **mass** is a form drawn only as a flat shape with no ink or marks of its own. A **part** is an object drawn with its own marks.
- **Centre of interest**: the one place in the picture that carries the strongest contrast and the most detail.
- **Tier**: a part's rank in `parts.json`. Tier 1 is the focus. A tier sets how heavy and how contrasted a part is drawn, never which of its sub-forms exist.
- **Gate**: a check a stage must pass before the next stage begins.
- **Describer** and **critic**: the two judges, described under Judges.
- **Emphasis**: how heavy and how detailed a part is drawn relative to the centre of interest.

## You write the marks; tools only measure

The drawing is `draw.py`. You type every point of every stroke there, from a
measurement you read. A measuring tool may tell you where things are: a
landmark, a width, an extent, the rows a slot occupies, a traced contour to
read positions off. It may not write the op list. A tool that prints `slot 3:
rows 212-260, left 118->131, right 140->139` is measuring. A tool whose output
is `stroke([...])`, or a list you hand to `stroke` in a loop, is drawing, and
then you are not the one drawing.

It is forbidden to skeletonise or vectorise the subject's own ink or flats into
strokes or fills. It is also forbidden to turn a trace into lines of `draw.py`
by any route: a generated section module, a loop over regions, a generator whose
output you import or paste.

A drawing made that way can pass every gate and the blind describer on every
crop. It is still a vectorised copy that carries the tracer's artefacts: a bead
at every junction, halos from upscaling, small parts lost, thin lines dropped.
None of these is a decision you can send back to a stage, and the script is just
concatenation with nothing in it to revise.

**Where reading ends and pasting begins.** A measuring tool may print an
outline. You then type the points where the silhouette turns, in perimeter
order. Copying every printed point in order is pasting, however it got into the
file. A script that edits `draw.py` is a text editor, and is fine when each line
it writes is one mark you decided. A script that computes a coordinate is a
generator.

`pen.write` refuses, and `--stages` fails, in three cases: strokes called from
another file; a call site reached more than once (a loop, a comprehension, an
import that draws); control points mostly not written as numbers in `draw.py`.
On six hand-written drawings none of these fired, and on a generated one all
three did.

**What the checks cannot see.** They read the finished `draw.py`, not how its
numbers got there. Numbers written into it by a script look the same as numbers
you typed: a script that adds a fixed offset to centres you chose to make a row
of ticks, or that copies a list shifted, passes every check. There is no sound
check for this. Hand-typed parallel hatching often repeats one offset exactly
(finished hand-written drawings hold groups of three to six strokes that are
exact translations of each other), so a check on repeated offsets would refuse
honest work. The rule is the only guard: a script may write a line into
`draw.py` only when you decided every number in it. If a script computed a
coordinate, by offset, by copy or by formula, the mark was generated, whatever
the checks say. Type each tick, and vary its length and spacing the way a hand
does (`reference/line.md`).

A scene stays affordable through its economy (five to twelve
masses, a part list fixed at S0, marks spent near the centre of interest), never
through a generator. Hatching is the same: each hatch line is its own stroke with
its own points, and a hatched region costing a hundred lines of `draw.py` is
expected. It is kept affordable by indicating it, not by a loop (see
`reference/line.md` § Hatching and texture).

## Setup

```bash
cd harness && npm install && npm run build && npx playwright install chromium   # once
```

Python needs `numpy`, `scipy`, `pillow`, `opencv-python`. `describe.sh` needs
the `claude` CLI. One directory per drawing holds `subject.png` and everything
below; nothing goes in `/tmp`. Copy `build.sh` into it and point it at this
directory with `export SKILL=…`, or write the path into its `SKILL=` line (a
copy cannot find the skill on its own, and says so). Your script is `draw.py`;
it writes `ops.json`. Copy `gates.sh` in beside it the same way: `./gates.sh`
runs every gate whose files are there (`--checklist`, `--stages`, `--doubled`,
`--joins`, `--depth`, `--colour`, `--linework`, `--counts`, `--ranking`,
`--parts`, `--masses`), prints one verdict line per gate (PASS, FAIL,
UNCHECKED, LOOK for a sheet or ranking you read yourself, SKIP), keeps each
gate's full output in `gates/`, and exits 1 on any FAIL. A LOOK line still
needs looking at; `--zoom`, `--hatch`, `--unfilled` and the describer are run
by hand.

**The shell may be zsh** (the macOS default). zsh does not split a variable
into words, so a flag and its argument held in one variable (`G="--stages
ops.json"; python3 check.py drawing.png $G`) reach `check.py` as one argument
and it stops with its usage text. Write each flag out, or use an array
(`G=(--stages ops.json); python3 check.py drawing.png "${G[@]}"`).

**A scene's working space is the delivered size times four.** A single object
gets the same 4x space when its smallest feature needs it (under about 40px at
delivered size, which is most objects). Every mark,
measurement and render lives in it. Make it once: `subject.png` is the
delivered image upscaled 4x with `Image.BILINEAR`, and the delivered image is
kept beside it as `subject_1x.png`, for the describer and for reading the whole
picture. Do not use LANCZOS or BICUBIC: both overshoot into a pale halo beside
every dark line, and the halo classifies as ground (in one test LANCZOS did this
to 0.12% of the pixels and BILINEAR to none). The soft ramp beside each line
still traces as a ring region round every outlined form, so trace an upscaled
subject with `--fringe 60`. That hands the ramp to the line, so a pale form
bounded by ink traces 3–5px inside its visible edge on every side, and small
pale forms drawn from the trace come back small: take their edges from a scan
or `--zoom`. The harness exports at device pixel ratio 2, so render with
`./build.sh --scale 0.5` to get renders 1:1 with `subject.png`. **macOS has no
`timeout`**; use `gtimeout`, or `perl -e 'alarm N; exec @ARGV' --`.

**Measure `--line` in the space you trace in.** `trace.py subject.png
palette.json --ink NAMES --measure-line` prints the per-pixel min(row, column)
run width of the line; pass its p90. Runs wider than twice the median run are
left out as flats. (A fixed fraction of the image once let a mouth count as line
and cut under a small object's own lines.) Never multiply the delivered-size
figure: one line was 6px at 1x and 20px, not 24, at 4x, because the upscale's
ramp thins the core that classifies as ink. `--ink` takes every palette name
that is line. That means the darkest near-black, a line that reads brown over
one flat and black over another, and a line drawn in a colour of its own (a
horizon, grass), which gets its own palette name.

### Measure per object, even though you draw in one document

A trace of the whole picture resolves every object at picture scale. A small
object comes back with a handful of points per form, and no care at the drawing
stage recovers them. Tracing the delivered-size image and scaling it up puts
every boundary on a lattice the size of the factor. So **crop each object out of
the working-resolution subject and trace that**: `crop.py subject.png x,y,w,h
meas/NAME.png` cuts it at 1:1 and stores its corner in the PNG, so `trace.py
meas/NAME.png palette.json` returns whole-picture coordinates with no flag. The
stored corner is not your box's corner, because the crop has a margin. Passing a
box corner as `--offset` once shifted every region 8px, and is now refused.
Marks stay in one `draw.py` in one coordinate space; only the measuring is per
object. For example, one object gave 77 regions and 872 contour points in a
whole-picture trace, and 156 regions and 3878 points from its own crop. That is
the difference between an object a viewer names and a shapeless blob. The
symptom to watch for is forms with three to nine points each.

**Masses are the one thing measured on the whole picture.** Trace
`subject_1x.png` (segment it, for a photograph or a painted subject) and read
their outlines off that. They carry no ink, so its
lattice of 1px at delivered size costs nothing. There are five to twelve of
them, and you type them into `draw.py` like every other mark, from the trace,
with as many points as their silhouettes need. A mass layer of hundreds of
flats, one per traced region, is the generated drawing again.

Where two ink-less masses meet, the edge is one shared entry in the dict. The
far mass runs past it, under the nearer one written after, so no hairline of
ground opens along the join. A mass is usually several traced regions split by
ink, and its outline is their union with the ink closed over, by a kernel the
width of `--line`. That kernel is the one knob, and it is measured, not chosen.
Masses read off different regions meet at nothing, and a simplified outline cuts
corners. So extend each far mass by hand under the one in front, or the first
render shows ground along every join.

### A trace does not say what the objects are

Deciding which regions make up an object, and which single form a viewer reads
as that object, is part of the reading. It costs the same on a detailed trace as
on a sparse one. The tempting shortcut is to take the largest region per object.
That fails in predictable ways. A limb comes back as its lit strip beside a
separate shade band, two ribbons. A garment comes back as the two patches either
side of its zip, with no shoulders. An object with no dominant region (a sock, a
sole, a neck) is never drawn, and nothing counts it as missing.

So before any mark, write down three things for each object:

1. **Which traced regions make it up**, by box, and what each one is: the lit
   strip, the shade band, a cast shadow, the ink, a hole punched through it by
   something in front.
2. **Which single form a viewer reads as this object**, its silhouette. This is
   what has to be right; the internal flats sit inside it.
3. **Where the traced contour is the right measurement and where it is not.** It
   is right for a silhouette, wrong for a slot or a hole, and wrong for a
   re-entrant region (one whose boundary folds back into its own interior).

If you cannot write those three, you are not ready to draw it.

A lit strip and its shade band are one form with two values, never two flats
side by side.

A form cut in two by a nearer one is still one form, and each cut end is the
nearer form's edge: it ends on that form's ink, never in mid-surface. The tracer
returns the pieces as unrelated regions, and a scan that confirms the gap is
real can close the item without anyone asking what made the gap. A flat that
stops inside another flat with nothing drawn across its end reads as a patch
stuck on. For example, a dark band broken by a sleeve became two dark patches on
a torso, each within 10px of the subject, because the sleeve's own edge was
never drawn. Name the occluder of every cut end and run `--overlay --box` on it.
A blue line across the end with no red beside it is that occluder's contour,
missing. Count the pieces on the subject: a band that wraps a body is cut by
every limb in front of it, and the piece that survives only below an arm is the
one most often left out.

The same holds from the far side. A form that passes behind another runs on
under it, and its own outline does not close at the occluder's edge. For
example, an arm whose outline closed just above a bar read as a bare hand
resting on it. Check the part list against the canvas before calling the picture
done.

## One object or a scene

A single object is drawn through the object stages, at one scale. A scene is
designed first, as masses. Then every object in it that must be recognisable is
drawn through the same stages, in the same document, in whole-picture
coordinates, at a working resolution high enough for its smallest feature. Two
reasons force this:

- **You can only judge what is large on the page.** A render is looked at at
  roughly 1,500px whatever its size, so in a scene a 12px eye or a 20px hand is
  too small to judge as a shape, and a part you could not see while drawing it
  is drawn badly. Nothing drawn at picture scale by eye comes out well, whether
  it is a face, a light bulb or a strip of tape. So every object that must be
  recognisable is a part. You look at it magnified with `--zoom` (the
  magnification is `1500 / max(box_w, box_h)`; a box as wide as the picture
  cannot be magnified, so split it at a seam some other form already hides), and
  you draw it at a working resolution that puts its smallest feature near 40px.
  The only other thing an object can be is a mass, with no marks of its own.
  There is no middle tier.
- **A scene is not a sum of parts.** What organises it lives above the object:
  one centre of interest, a tone plan of two to four masses, most edges lost
  into the mass behind them, and the junctions where things touch. An object
  drawn well with a closed contour of its own can break the picture. The scene
  level decides these before any object exists and checks them after every
  object is drawn.

Which case you have is decided at stage 0, from the reading. A picture with
furniture in it can still be "a single object".

## The object stages

Each stage narrows one freedom and is cheap to fix while the next is expensive.
**A stage may not begin until the previous gate is true on a render you looked
at**, and no part may be more than one stage ahead of any other. `pen.write`
refuses ink in a drawing with no gesture, block-in or contour stage. It checks
that those stages exist, not that each ink mark has a contour under it.

One `draw.py` holds every stage, and `build.sh` renders all of it, so the easy
path is to type every stage at once and gate them afterwards. Do not. Write one
stage, render it alone with `STAGE=<name> ./build.sh --scale 0.5` (`gesture`,
`blockin`, `construction`, `fill`, `contour`, `ink`, `correct`: it renders
that stage and the ones before it), pass its gate, and only then write the next.

| # | Stage | You produce | Gate |
|---|---|---|---|
| 0 | **Read** | `palette.json`, `regions.json`, `subject.describe.md`, `reading.md`, `parts.json` | every tier-1/2 part has a shape note; the acceptance list exists and quotes the describer's answers 3–5; `reading.md` records the line character, and every hatched region you will draw has a `hatch` entry measured with `--hatch` |
| 1 | **Gesture** | 3–10 strokes, `stage="gesture"`: the line of action, then each big mass as one loose loop. A built or faceted mass (a building, a box, a machine, a rock) is a loop with `smooth=False`: smoothed, a building's blocks render as ovals and the describer names jars or pots. An organic mass keeps the default smoothing | `describe.sh gesture.png` answers 2 and 3 the way `subject.describe.md` does. If the action does not read here, no later stage puts it in. There are two exceptions. One is an action carried by value rather than silhouette (a hand that reads only as pale fingers against a dark glove): record the describer runs that show it and gate the action at stage 5. The other is an action carried by a small feature that no loop can state (an open beak, a tilted head, a glance): record the runs and gate the action at the stage that draws that feature |
| 2–3 | **Block-in** | `stage="blockin"`, `smooth=False`: every tier-1/2 region as its `blockin` straights from `regions.json`, junctions as points shared by name | `check.py blockin.png --ref subject.png --overlay`: the straights sit on the subject's edges |
| 4 | **Construction** | `stage="construction"`: for each volume, its turn written down, its centre line where the turn puts it | a written turn for every tier-1 form |
| 5 | **Masses** | `stage="fill"`, `tool="flat"`: one region per surface, drawn past where the ink will go (see the trapping notes below). Written in depth order, each form's fill directly before that form's ink, so a nearer form's flat covers the ink of the one behind it. Never `back("fill")`: it sends every flat behind every line, and the object can then no longer occlude itself | `check.py drawing.png --ref subject.png --masses`: the two read as the same shape, said in words. Stages 5–8 interleave per form, so on a subject with heavy line, judge it once each form's ink is in. Its flats alone never match a subject whose line carries mass |
| 6 | **Contour** | `stage="contour"`: the real edge, curved where the subject curves, from `contour` in `regions.json` | `--overlay` again |
| 7–8 | **Ink** | `stage="ink"`, one stroke per edge, each width measured on the subject, every stroke tagged by the edge it states; then the hatching, group by group, each line its own stroke | `check.py drawing.png --doubled ops.json` and `--stages ops.json` pass; `check.py --joins ops.json --parts parts.json` lists no line stopping just short of the mark it runs at; `--linework parts.json --ref subject.png` passes: every measured hatch group is there at its angle and no heavier than the subject's, and the weight span is at least half the subject's |
| 9 | **Fill** | flats refined; blacks massed as one value before anything is graded | `--hide ink` still separates figure from ground |
| 10 | **Correct** | `stage="correct"` marks aimed by the judges, with the number of rounds fixed at stage 0; `refuted.md` for every item that did not survive its measurement | `describe.sh drawing.png` matches the acceptance list clause by clause; `--registration`, `--parts`, `--ranking` |

**Trapping at stage 5.** `trap=<px>` on a body flat grows it outward by that
amount, so the contour covers its edge. A fill outline taken from the tracer
sits at the colour transition, which is inside the ink. Used as is, it falls
short by half a line width, and the ground shows through wherever the contour
bulges.

- Trap an edge that is a silhouette. Never trap an edge that is a measurement.
  A flat that is a mark in its own right (a vent, an eye, a cast shadow, a
  shade) is ruined by trapping, and trapping every closed flat swells the
  interior shapes until they eat the form.
- A band (a strip, a rim, a hem, a strap) is the silent case. Its two long edges
  face opposite ways, so trapping moves both, and the band gains twice the trap
  in width, on every band at once, with every gate still passing. Where two
  bands run concentric or parallel, their ratio is what makes the pair read, and
  trapping converges it. Trap a band's ends, never its length.

**Stages 5 to 8 interleave per form; they are not four passes over the whole
drawing.** As soon as two forms overlap, write them depth-major: the far form's
fill, its ink, then the near form's fill over that ink, then the near form's
ink. Written stage-major, the far outline lands after the near flat and draws
straight across it, making a crease or seam that is not there. Occlusion comes
from the order you write in and from nothing else, and `--depth ops.json
parts.json` is its only gate. That gate works only if stroke tags and inventory
names use one vocabulary:

- The key of an overlap is written `far/near` in tag names
  (`mug.body/table.top`, not `body.mug/top.table`): the side behind first, so
  `in_front` names the second side (`"mug.handle.top/hand.near"` with
  `"in_front": "hand.near"`). The order is easy to get backwards; `--depth` warns on a key whose first side is the one `in_front`
  names. `in_front` still decides the check, so fix the key to match it.
- `in_front` sits only on overlap entries.
- A part with no ink makes its rows UNRESOLVED, which is as serious as FAIL.
- Matching is by prefix, so a parent's rows clear only when every sub-form is
  ordered.
- Two sub-forms of one surface (a neck ruff and the chest, a muzzle and the
  head) have no front: each one's ink crosses the other's flat. Write their row
  with `"in_front": "same"`. `--depth` then checks no order for it, still wants
  both names tagged on the page, and drops the pair from UNLISTED.

A hole (a vent, a window, an eyelet) is an absence in its form, so its flat is
written after the ink of the surface it pierces. Otherwise that contour runs
across the opening.

**A subject with no outline** (flat vector art, a poster, a cel without line)
goes through the same stages. Its contour is the edges between flats, written
as the flats' shared points: what the flats are cut to, with no weight of its
own. The ink stage holds only what the subject draws as a dark line (spokes,
cables, a chain, a seam), and nothing where it has none. Do not add an outline
the subject lacks.

Going back to an earlier stage invalidates everything after it, so re-run every
stage after the one you changed. The script re-renders in one call, which makes
that cheap.

`build.sh` draws `gesture.png` and `blockin.png` in stock stage colours on a
stock ground (`--palette palette.json --stock`), to check the action and the
placement. The ground is judged on
`contour.png` and `drawing.png`, which use the palette. `drawing.png` never
shows gesture, construction, block-in or contour, so nothing needs erasing.

## The scene stages

These are the object stages, wrapped. Stages S0–S2 draw no object; they design
the picture. Then every object is drawn into that same document, in
whole-picture coordinates, at 4x the delivered size (see Setup). There is one
`draw.py`, one `ops.json` and no second coordinate space.

Objects drawn in their own crop and composited back came out as blobs, and the
same objects drawn whole came out well. What a crop gave was a forced look at
the object magnified, so that survives as a gate: **`--zoom` every object before
you call it done.** An object never zoomed comes back as fat lozenges and
scratches that pass at full-picture size. Crops are for measuring and looking
only.

| # | Stage | You produce | Gate |
|---|---|---|---|
| S0 | **Read as a tone field** | everything stage 0 produces, plus the items listed below under S0, in `reading.md` | a thumbnail of the tone plan reads as a design with one dominant value and the strongest contrast at the centre of interest; every overlap has a depth decision; the part list and the acceptance list agree |
| S1 | **Armature** | `stage="gesture"`: eye level, ground plane, the main lines, the line of action, the major masses as loops (`smooth=False` for a built or faceted mass, as at stage 1). The object stages' "3–10 strokes" is a single object's budget and does not apply here. A scene needs one stroke per mass plus the ground and eye lines, which runs to fifteen or twenty. With too few, the describer reads one object's parts as another's | `describe.sh gesture.png`: the action and the big shape read. See the note on S1 below |
| S2 | **Masses** | `stage="blockin"` straights for the masses, then their flats `stage="fill"`: the middle tone over the whole, then lights, then darks, honouring sharp and lost edges. Every object's mass goes in here, part or mass. The part/mass split decides whether an object gets marks, never whether its value exists. A part left out is a hole in the tone plan, and when a whole value group lives inside parts (the darks usually do) the gate cannot pass until they are in. A flat is not ink, so this costs nothing at the gate. No object's marks yet | `--masses` against the subject at thumbnail size; no object has an ink contour (`--stages` shows ink 0) |
| S3 | **Every object, in place** | run stages 2 to 9 of the object stages on each object. Block-in straights first, in the one `draw.py`, in whole-picture coordinates, writing from the furthest object forward. This is write order, not work order: work the centre of interest first if the budget says so, and insert it at its depth. Its brief from S0: which of its edges are lost, what is in front of it, its emphasis. **Refine the object's S2 mass into its stage-5 fill.** They are the same line of `draw.py`: edit its points in place from the object's own trace and never stack a second fill over it, so there is no stand-in to remove and no fringe. A simple manufactured form is written from its traced contour nearly point for point and is cheap. A figure is built from its three masses and every joint, and is not cheap | `--zoom` on the object, beside the subject, before you leave it. This is not optional. Then its own stage gates, `--faces` and `--unfilled` |
| S4 | **Junctions** | nothing to assemble. Every object was drawn where it belongs, with its neighbours already on the page, so the overlaps table was satisfied as you went. Walk it once and confirm each row: the accent where forms touch, the joint line that breaks at the leg in front of it, the lost edge still lost | `--doubled`; `--depth ops.json parts.json` clean, with no UNRESOLVED row; every row of the overlaps table has a recorded decision and a look |
| S5 | **Emphasis** | nothing is drawn at whole-picture scale here. Emphasis was decided at S0 as each part's weight and edge count, and the far parts were drawn lighter and with fewer edges as you went. Fewer edges means edges lost into the mass behind, never sub-forms left out: a far figure keeps its arms, legs and feet. Walk the picture and confirm the gradient: weight and detail fall off with distance from the centre of interest and with depth, and masses have no marks | no part beyond the centre of interest carries its weight; a describer names every part |
| S6 | **Overlaps** | the pass over the overlaps table, row by row, on the whole picture: the accent where forms touch, tangents broken by overlap or separation, lost edges confirmed lost, rails and wires only where both values are measured either side | every row of the table has a recorded decision and a look |
| S7 | **Blacks, hatching, texture, vignette** | one pass spotting the black pattern across objects; each hatched region recorded at S0 drawn as its measured groups, one stroke per hatch line, dense at the edges, turns and centre of interest and thinning out into the light; texture elsewhere indicated (a few marks that suggest it without drawing all of it); the whole drawing's silhouette against the paper | `--ranking parts.json`: the centre of interest leads, nothing shouts above its tier; `--linework parts.json --ref subject.png`: no measured group missing, at the wrong angle or heavier than the subject's, and the weight span at least half the subject's |
| S8 | **Correct from a distance** | stage 10, on the whole picture, with the describer run twice. A blind viewer on each part's crop ranks the round: parts that are misnamed get the budget first, then parts whose shape notes are untrue | the acceptance list; `--ranking` still shows one centre of interest; no part misnamed. An item that returns after a round that addressed it is the stopping rule |

**S0 items for `reading.md`:**

- **One** centre of interest.
- The tone plan: a dominant value and two to four masses.
- The masses: five to twelve, each edge marked sharp or lost, no object with a closed contour.
- Every object marked as a **part** or a **mass**. A part is an object (the lamp, the chair, the figure), never a feature of one. An object the describer names in answers 3–4 is a part, because the acceptance list will ask for it. The exception is an object with no silhouette of its own against its surround: it is still drawn, as part of the mass it sits in, and its clause is the only one the drawing may leave unearned. Write that down now. Budget is never a reason for an unearned clause.
- For each part: its box (the `--zoom` and measuring crop), its smallest feature at working resolution, its nested parts (a face inside a figure), and its emphasis relative to the centre of interest.
- The overlaps table, with an `in front` column per crossing, masses included. A road cut into a hillside is in front of it, and S2 needs that order to run each far mass under the near one. Rows that name a mass stay UNRESOLVED until its one line is written, so check them at S4.
- The counts of repeated small forms, including the zeroes.

**S1, when the action cannot be stated yet.** Some actions cannot be stated at
this stage. One is a pose carried by value rather than silhouette (a seated
figure with fully foreshortened thighs has a standing figure's outline). Another
is an action the describer's category prior outvotes, such as a figure above a
bicycle, which reads as riding whatever the lines say. In those cases, record
that the action is gated at S2 instead, with the describer runs that show it,
rather than redrawing an armature that cannot carry it. A third is an action
carried by a small feature (an open beak, a head tilted back, a glance): loops
cannot state it, and the masses at S2 cannot either. Record the describer runs
and gate the action at the stage in S3 that draws that feature.

**Every part gets its whole run of stages; budget never shortens one.** S0 is a
large share of a scene, and a figure or a vehicle costs as much as a whole flat
picture. Rationing a scene by percentages fails in a known way. The centre of
interest goes through all the object stages, and every other part stays at its
S2 mass with an outline. The hands become slabs and a small mechanism becomes
two blocks, though the inventory names their fingers or levers. The same part,
drawn alone with no budget limit, matches the subject piece for piece. So a part
that must be recognisable is either drawn through stages 2–10 with its own
correction rounds, or it is a mass. Never leave one half-drawn.

A small human figure is the part most often cut down this way, to a round head
on an outline with no arms and two tubes for legs. People draw the eye at any
size, so a figure is never a minor part and never a mass with an outline. However
small, it has a head (with its hat or hair), neck, shoulders, torso, two arms
with elbows and hands holding what the subject shows, hips, two legs with knees,
and feet, in the stride or pose of the gesture, and it gets its own `--zoom` and a
working resolution where its head is around 40px. Its tier lightens its line,
not its anatomy (`reference/figure.md` § A small figure is still a whole figure).

When one agent cannot carry every part, split the scene: one agent per part,
each writing its own section of the one `draw.py` in its depth position, with
the S0 reading shared. Sections, copies, the merge and the final pass are in
`reference/scene.md` § The mechanics. Checkpoint after S2, after the first part
and after the last.

## Stage 0

1. **Palette.** Sample every flat and the ground off the subject into
   `palette.json`: one entry per flat, as many as the subject has, each a name
   you choose and a `#rrggbb` value (`"coat.lit": "#c8934a"`, `"roof"`,
   `"sky"`; letters, digits, `.`, `_` and `-`), plus `background`, the ground.
   Name a flat for what it is, so `color=` says which colour it paints. A mark
   may not use `background`, so where the ground shows through a hole in a
   form, give the ground's colour a name of its own. Write down where each
   colour was sampled. Then
   trace and read the unmatched-colour line that `trace.py` prints: a flat the
   palette lacks comes back as a clumped patch of pixels far from every entry.

   - **Sample each value step of an object at its most saturated representative
     patch**: inside the form, away from its edges, its highlights and any
     colour the ground reflects into it, and on a patch large enough to be the
     step rather than one hair or one speck. Never take a step's colour from an
     average: a k-means centre, a blur over the whole object, or a posterised
     copy mixes the step with its highlight, its shadow and the ground's spill,
     and the mix is greyer than any patch on the subject. A gold coat sampled
     that way comes back beige in the light and brown in the shade.
   - **Keep the hue ramp.** Read it off the subject from light to shadow: each
     step is darker, and on most warm or translucent materials (fur, skin, wood,
     fruit) also warmer or more saturated, not greyer. A palette whose shadow
     steps are greyer than the subject's has lost the ramp.
   - **Compare the palette's chroma with the subject's** before drawing: for each
     of an object's steps, put the palette entry's saturation beside the
     saturation of the subject's most saturated tenth of pixels at that value.
     An entry well below it is an average; sample it again. Once there is a
     drawing, `check.py drawing.png --ref subject.png --colour parts.json`
     compares each part (§ Judges).

   - A flat within about ten levels of the ground (an eye's white, teeth) cannot
     be separated from it by colour, and the tracer hands it bare ground. Draw
     it from measured extents inside its ink, and trace with `--exclude NAME`,
     or the ground itself comes back as that flat.
   - A dark flat a few levels off the ink steals the ink's ramp in the same way,
     so leave it out of `--ink`. Fill it with a near-black name of its own,
     never the ink's black. Vents, brows and a strap drawn in the line's black
     read as holes punched through the form and pull the eye off the centre of
     interest.
   - Ramp classified as a real name comes back as long thin regions hugging the
     ink, with a `median` far from their entry. That is not a missing flat.
   - A nested part may discover a flat the full picture could not resolve: a
     tooth, a tongue, anything smaller than the picture's own sampling. That is
     not a stage 0 failure and it cannot be prevented there. Sample it and add
     a name; record it in `reading.md` beside the palette.
   - An older `palette.json` uses tldraw's 13 stock names (`black grey
     light-violet violet blue light-blue yellow orange green light-green
     light-red red white`) repointed to the subject's values. It still renders
     unchanged. A new palette uses names of its own: a stock name says a hue
     the flat does not have, and is easy to type for the wrong flat.
2. **Trace.** Choose the tool by the subject. Both write `regions.json` in the
   same form, and both read the corner `crop.py` stores in a crop.
   - **A flat-cel or printed subject** (flats and ink):
     `python3 trace.py subject.png palette.json --png regions.png`. It
     classifies every pixel to its nearest palette entry. A printed or textured
     subject (halftone dots, lithograph grain, paper texture in a scan) traces
     as a tangle of specks. Trace it with `--smooth PX`, which smooths the
     texture out before classifying; take PX near the size of the texture's
     repeat and check that the unmatched-colour figure falls.
   - **A photograph or a painted subject** (continuous tone, brushwork, fur,
     foliage, no ink to bound the flats): `python3 segment.py subject.png
     --palette palette.json --png regions.png`. Classifying each pixel there
     returns hundreds of regions of noise, even with `--smooth`. `segment.py`
     smooths the texture with an edge-preserving filter and merges like
     neighbours into about `--regions` (default 40) regions that follow the
     forms. `--box x,y,w,h` measures one part at a finer scale; `--silhouette
     x,y --box ...` prints one object's outline. Read
     `reference/photograph.md` before measuring a photograph.

   Look at `regions.png`. On a scene, use `subject_1x.png` for the reading and
   the masses, and each part's own crop when you reach it. A region is a flat
   or a patch of like colour, not an object; naming the regions is the reading.
3. **Describe the subject.** Run `describe.sh subject.png A` and again with `B`
   (the run name keeps both files; on a scene, describe `subject_1x.png`). Its
   answers 3 (what each figure is doing), 4 (what touches what) and 5
   (expression) are the acceptance clauses, quoted, not paraphrased. A drawing
   that reads as a different action has failed whatever else it gets right.
4. **Reading.** Write `reading.md`:
   - what the picture is, in one sentence;
   - the big shape as one or two forms;
   - the line of action;
   - when the action lives in a turn or a tilt (a look over the shoulder, a
     head thrown back), the 3–4 angles that carry it, measured with `look.py
     axis` (`reference/figure.md`, `head.md`, `bird.md`), and checked again at
     stage 4 and at the final gate;
   - how this subject differs from the typical one, measured, because that
     difference is the likeness;
   - the light source, fixed now;
   - the two value groups;
   - **the line character**, measured. The outline's weight range, finest to
     heaviest in px (`check.py subject.png --linework parts.json --ref
     subject.png` prints the subject's span, compared with itself; `--weights` on
     a few rows gives single lines), and where
     the heaviest lines sit (the silhouette, under forms, at contacts). Whether
     the line is uniform or varied. Then every hatched or textured region: its
     box, and from `--hatch BOX` its direction, spacing, mark length and value.
     A subject whose look is mostly hatched ink (an engraving, a pen drawing, an
     old print) has its look in this paragraph, and a drawing that leaves it out
     reads as a colouring-book copy however well its flats are placed;
   - what you leave out, on purpose. That may be texture, small detail and
     variation inside a form, never an object. Every object a viewer of the
     subject names (the describer's answers 1, 3 and 4) is drawn, as a part or
     as a mass, however small and however tight the budget. If the budget
     cannot carry every named object, say so and ask for more budget or a split
     across agents; never drop the object and mark its clause as not earned;
   - the budget and the number of correction rounds;
   - then the acceptance list.

   For a scene, also include everything S0 asks for above.
5. **Inventory.** Write `parts.json`: small, ranked, every entry a shape note
   with a box read off `regions.json`.

   - **An entry descends to the sub-forms that make the object what it is**,
     each with its own box and its own note. A wheel is a tyre, a rim, spokes and
     a hub, not "a wheel". A glove is its fingers, its thumb and its cuff. A
     single note for a whole object buys one silhouette, and a silhouette is
     what a viewer calls a different object. The count of repeated small forms
     already includes these sub-forms, and this is where they become marks.
   - **A reference's ```checklist block is enforced.** `build.sh` runs `check.py
     --checklist parts.json` and will not build until each sub-form the
     checklist lists for an object in the inventory has an entry, or a reason in
     `"_absent": "name: reason; ..."`. A name is the sub-form as the checklist
     lists it (`"hole: ..."` excuses it for every object) or a dotted path
     ending in it (`"tree.hole: ..."`, that object only). A sub-form listed only in prose gets read
     and then skipped: an inventory can still stop at the first level.
     A checklist applies only when a key names one of its `object:` words.
     When none does, `--checklist` warns that no reference object matched, and
     its PASS then checks nothing. Use a listed name in the keys, or add the
     subject's name to the reference's `object:` line.
   - Stop descending where the next level down would not survive at the scale
     you will draw it. That scale is the part's working resolution, with its
     smallest feature near 40px, not the picture's. A human figure always
     descends at least to head, torso, arms, legs and feet, whatever its tier
     (the person checklist in `reference/figure.md` enforces it).
   - **Two instances of one object class get the same sub-form list.** The
     second of two wheels, hands or shoes is read with less attention and comes
     back with fewer entries, and its missing sub-form is missing from every
     gate. Reconcile the pair before leaving stage 0, or write down what the
     second genuinely lacks.
   - Name the junctions as entries of their own (hand/handle, foot/pedal,
     hip/seat, tyre/ground, and every joint), because that is where scenes fail.
     **Write overlap rows at the grain of the forms that cross**:
     `chair.frame.leg/person.leg.near`, not `chair.frame/person.leg.near`.
     `--depth` matches by prefix, so one member of a frame written in another
     depth group fails a whole object-level row that the drawing honours.
   - Then cut a plain image crop of the subject (a PIL crop is enough) at each
     tier-1/2 box, grown by a fifth so the part's edges and neighbours are in
     view. On a scene, cut from
     `subject_1x.png` at the box over four, since a 4x crop of a large part runs
     to thousands of pixels. A box under about 150px at 1x is cut from
     `subject.png` instead, since a 14px sweat drop comes back as "a
     low-resolution crop". Run `describe.sh` on each crop. The calls are
     independent, but run at most four at once (`xargs -P4`): many at once can hit
     the CLI's usage limit, and then every call fails. `describe.sh` exits 3 when the
     CLI reports a usage or rate limit; wait, then rerun only those crops.
     Where it does not answer with the part you named, fix the note or delete
     the entry.
   - An answer that names a neighbour means the box is on the neighbour. If a
     tightened box still names it, the part has no silhouette of its own, and so
     does an answer of "cannot tell". Keep such a part when the acceptance list
     names it, and judge it in context later.
   - An entry for a thing the subject does not have propagates into every stage
     below it, and this is the only check that can remove one.
   - **Count each group of repeated small forms** (vents, fingers, teeth,
     spokes, droplets). Count on the object's own working-resolution crop, by
     component scan on its pixels. A count read off a magnified look once took a
     parallel edge for a third motion arc. Use a box that stops short of every
     neighbour: a box reaching into a pile or cutting a forearm counts their
     fragments as forms. A group running parallel to a heavier line is counted
     with it, and the count says so. Never count with a describer on a
     picture-scale crop, which counts blobs and under-counts. Cross-check
     against the closed regions the object's trace returns; a mismatch is
     usually forms left open by a surface curving away.
   - **Write the count into the entry** (`"count": 7, "value": "black+grey"`) and
     run `--counts parts.json` after S2 and after the object. It is the only gate
     that fails on an absence, and only where it counts the subject: separate
     forms of one value in a tight box. Crossing or touching forms (spokes, slots
     bounded by their own ink, a wing's feathers) come back UNCHECKED; count those on `--zoom`, on
     both images, into `notes.md`. The tracer drops forms under `--min-area` and
     hands dark forms narrower than `--line` to their neighbours, and `--masses`
     passes without a spray of droplets. A count deferred to "later" is never
     taken.
   - **Write each hatched region's measurement into its entry**, from `check.py
     subject.png --hatch BOX`: `"hatch": {"angle": 127, "spacing": 33, "length":
     38}`, in degrees on the page (0 horizontal, 90 vertical, 45 a `/`) and px.
     A region with two groups (cross-hatching, or two planes in one box) gets
     two entries, one per group. For pale lines cut into a dark, measured with
     `--hatch BOX --light`, add `"light": true` inside the `hatch` dict
     (`"hatch": {"angle": 73, "spacing": 39, "length": 39, "light": true}`).
     Placed beside `hatch` it is ignored and dark lines are checked; every check
     warns on a key in an entry that it does not read. `--linework` fails a
     drawing that has no group at that angle in that box, or whose group there is
     heavier than the subject's (its mark width over 1.6x, or its share of the
     outline's weight over 1.6x). Note the group's `width` too: it, not the
     outline, sets the hatch's weight (`reference/line.md`). If `--hatch` warns
     that the marks are grain, they are texture fragments (a photograph, fur):
     write no entry for them (`reference/photograph.md`).

```json
{
  "nose": {"shape": "ON the silhouette: the profile leaves the brow, runs down and OUT to the tip, then turns back under it", "box": [540, 336, 45, 50]},
  "mug.handle.top/hand.near": {"shape": "the fingers close over the handle; the handle disappears behind them and reappears 30px to the left. No gap", "box": [318, 470, 96, 70], "in_front": "hand.near"},
  "radiator.slots": {"shape": "seven slots radiating from the top edge, each tapering to both ends", "box": [380, 100, 330, 200], "count": 7, "value": "black"},
  "rock.face": {"shape": "short horizontal dashes along the front face, densest under the overhang", "box": [400, 3330, 1600, 150], "hatch": {"angle": 2, "spacing": 33, "length": 39}}
}
```

## Reading coordinates

Every point in `draw.py` is read off the subject. `look.py` is the tool for it.
It measures and writes no mark. Coordinates are the working space's; `--scale 4`
reads `subject_1x.png` in the 4x space, and a render is read at the first
image's size, so `drawing.png` from `--scale 0.5` lines up with `subject.png`.

```bash
python3 look.py grid subject.png drawing.png --box 400,1500,600,500 --out look.png
python3 look.py probe subject.png drawing.png --at 640,1850 1000,600
python3 look.py edge subject.png drawing.png --ray 700,100,0,1 --ray 640,1850,1,0
```

- `grid` crops the box from each image, magnifies it to about 1000px and rules
  it every `--step` (about ten lines by default), each line labelled in picture
  coordinates and every fifth one stronger. **Use it to place points.** On a
  photograph with hundreds of points it is often the only practical way.
- `probe` prints, per point and per image, the median colour of a small patch,
  its hue, saturation, value and grey, and the nearest `palette.json` name.
- `edge` walks a ray from `x,y` along `dx,dy` and prints where the colour first
  changes sharply (`--contrast`, Lab units), with the colour and palette name
  on either side, then the next few edges. From a point inside a form, four
  rays give its extents.

**The grid places; a probe or an edge confirms.** A position read by eye off a
grid or a zoom's ticks is a placement, and a fault is never judged by one
(§ The correction cycle). Before you move a mark for a fault, or trust a point
your shape depends on (a corner, a contact, an eye), check it with `probe`,
`edge` or `check.py --scan`. For an outline row by row, `--scan` is still the
instrument; for a silhouette, `segment.py --silhouette`.

## Marks

```python
from pen import stroke, frame, fade, erase, back, write
V = {"hip": (462, 590), "knee": (445, 715), "ankle": (452, 880)}   # measured once, named once
P = lambda *names: [V[n] for n in names]
ops = [frame(0, 0, 3712, 4608)]   # the working space: 4x the delivered 928x1152
ops.append(stroke(P("hip", "knee", "ankle"), stage="gesture", nib="fine"))
ops.append(stroke(P("hip", "knee", "ankle"), stage="blockin", smooth=False))
ops.append(stroke(P("hip", "knee"), stage="ink", nib="medium", tag="figure.leg.near.thigh"))
ops.append(stroke(P("knee", "ankle"), stage="ink", nib="medium", tag="figure.leg.near.shin"))
ops.append(stroke([(430, 600), (470, 598), (468, 880), (440, 882)], stage="fill", tool="flat",
                  closed=True, color="leg.shade", size="s", scale=0.5, tag="figure.leg.near"))
write("ops.json", ops)   # color= takes a palette.json name; a name it lacks is refused
```

- **Only `tool="flat"` fills.** Every other tool (`brush`, `pen`, `marker`,
  `crayon`, `gouache`, `pencil`) draws a closed path as its outline, so a solid
  eye drawn with `tool="pen"` comes out as a ring. `stroke` refuses a closed
  `stage="fill"` mark with any other tool unless it passes `fill=` itself
  (`fill="none"` when the outline is meant).
- **Keep `stage` out of a dict of shared settings.** `stroke(..., stage="ink",
  **C)` where `C` also holds `stage` stops with a duplicate-keyword error. Share
  `color`, `size`, `scale` and `tool` in the dict and write `stage=` on each call.

- **Every mark goes on its own line with its own numbers.** No function that
  makes a shape, no loop that stamps one, no `ellipse()`: a tool may not supply
  a form you did not choose after looking. A dict of measured points supplies no
  form, and it is the fix for an edge drawn twice: two objects that share an
  edge share the entry. Your own points may serve two marks (a flat and its ink,
  or one edge of two faces). The rule is about where the numbers come from, not
  how often they are used. Reference them from one named list and never paste a
  copy, because two copies drift apart on the next edit and become one edge from
  two guesses. A slice of a named list (`GLOVE[3:] + GLOVE[:2]`, to ink one edge
  of a closed form open) is a reference, not a computation. What stays forbidden
  is a program computing points, whatever carries them into the file.
- **Tag every ink stroke by the edge it states** (`tag="jaw.left+neck"`; `+`
  joins several), so `--depth` can read the write order against the inventory
  and `--only` and `--hide` can show one object. Ink is per edge. A mass's closed
  outline inked as it stands states every shared edge twice (one band's outline
  ran 298px along its neighbour's), so where a neighbour states an edge, ink the
  mass with open strokes.
- **One stroke per member; a joint is a stroke boundary.** A smoothed stroke fits
  one curve through all its points. A bent form written as a single
  `hip → knee → ankle` stroke therefore comes back as an unbroken bow with no
  angle at the joint, and reads as the unbent form however exactly the joint was
  measured. The points hold the bend, the render throws it away, and no numeric
  gate reports it. Give each member its own stroke, or pass `smooth=False`.
- **A chain, belt, rope, cable, hose or wire is one continuous path.** Write it
  as consecutive strokes that share their end points by name, each meeting the
  wheel or anchor it wraps at the tangent point, with no gap. Carry its texture
  (a beaded or linked line) when the subject shows it, and count and write the
  teeth of a gear. `--joins` lists a run that stops short. See
  `reference/line.md` § Continuous paths.
- **The tracer's points are measurements, not marks.** You read positions off a
  contour and type the ones that carry the shape into `draw.py`. The region list
  is never iterated into strokes. Keep perimeter order. Resequencing folds the
  walk into arrowheads, and a point added to a traced outline (a run-on under a
  nearer form) goes in at its place round the outline. Typed at the head of the
  list, it once made the outline double back, and the face rendered with ground
  showing across it. `--stages` lists every such HOLE.

  How many points to type depends on the form. For an organic form, type the few
  that carry it. For a simple manufactured form (a bulb, a frame, a strip of
  tape), type most of the contour, and the drawing is then in its weight and its
  junctions. A straight is the exception: a tube's edge read every 75px wanders
  ±5px, and typed through every reading it inks wavy. Measure many points, type
  its ends and any real bend, and use `smooth=False`.

  Neither approach works on a re-entrant region, such as a band with shapes
  punched through it or a boundary threading into its own interior. Draw a plain
  polygon from measured extents instead.

  A ring is not a disc. A region with `holes` is a band, drawn as a stroke along
  its centre line, or as a flat with what shows through the hole written after
  it. Where what shows through is a scene, one closed polygon (outer edge, seam,
  inner edge) renders a hairline of ground along its seam. Put the seam where a
  nearer form covers it, and write it `smooth=False`. Smoothed, the path through
  the seam's doubled-back points bulges past the ink. A flat pierced by several
  openings (a chainring's cut-outs) is the same polygon with a slit from a
  covered point out to each opening and round it the other way.
- **To draw a group of repeated small forms, chain rows to measure it and then
  write each form yourself. The measuring is a gate, not advice.** This covers
  vents, fingers, teeth, slots, louvres, treads and droplets: wherever one
  object carries several of one small form. Skipping the measuring is a failed
  stage. Those classes are the ones most often skipped, and a viewer then names
  the object something else, such as a helmet read as a beetle or a glove as a
  shoe.

  Scan each row for runs of the target value inside the eroded silhouette
  (`check.py --scan BOX --value NAMES`), chain the runs across rows, and print,
  per form, its end rows and its two edges every few rows. This counts the forms
  (a morphological opening merges two narrow ones and silently lowers your
  count). It shows where each form tapers, because the chain ends there and not
  because you chose a nice shape. It also shows a structure running the wrong
  way, such as a groove narrowing where you drew it widening. Then author each
  form from it: end rows, widest row, and enough of both edges to carry every
  turn, typically twelve to twenty points for a slot.

  The point count tells you how it went. Five to eight points means the shape
  was chosen by eye, or read off a sparse trace (re-trace the object's crop).
  Forms chosen by eye also come back identical. Emitting the chain itself, one
  point per row, is the generated mark described above.

  Where a form curves back so that one row holds two of its runs (a tadpole's
  tail, a bent streak), chain along its own long axis (scan columns) and still
  write one outline. A piece per chain abuts along a row, and `--doubled`
  reports it as one edge stated twice. Where a form sits in front of a form of
  the same value, no value mask separates them. The ink between carries the
  edge, so read it off `--zoom` and say in the script where those points came
  from.
- **Never probe a region at its `centre`.** That field is a centroid, and a
  centroid is not necessarily a point inside the region. On a crescent, ring,
  bent or C-shaped form it lands in a neighbour, whose colour looks like proof
  that the region is an artefact. (In one crop, 11 of the 14 largest regions had
  a centroid outside themselves, all genuine.) Probe `inside`, or compare the
  region's `median` with its palette entry. Culling a region is a decision and
  needs the same measurement as a mark, because nothing downstream will say it
  was wrong.
- **A region-growing measurement needs a bound that is not a colour.** Seeding a
  silhouette on a palette name runs it into every other object carrying that
  flat. A garment seeded on its two colours once swallowed a nearby object that
  shared one of them. The object's box is already written down in the inventory;
  pass it as the bound. `segment.py --silhouette` will not run without one.
- **A traced contour measures a silhouette; it does not measure a slot.** The
  tracer stops at the colour transition. For a vent, an eyelet, a gap between
  fingers or any other dark opening, it therefore returns the opening's pale
  interior, a short fat blob. What a viewer reads as a slot is the dark shape
  including the ink that bounds it, and the thin rib between two slots carries a
  dark line of its own. Draw the interiors and you get spots on a dome: a helmet
  becomes a beetle. A better measurement does not fix this. A group of vents
  built from detailed traced contours at twenty points each came back worse than
  the same vents built from a sparse trace, because a precise measurement of the
  wrong thing is still the wrong thing. For any dark opening, chain the dark
  inside the eroded silhouette, read where each rib between two openings runs off
  the same scan, and write both yourself.
- **A dark mechanism reads by its light gaps.** This is the inverse of the slot.
  A derailleur, a lever on its body, a hinge or a buckle is one connected dark
  shape, and what says it is an assembly is the light openings between its
  members and the ink joins where they meet. Fill a gap solid and it becomes a
  block with holes. Leave a join open and one assembly becomes islands on the
  ground, a lever floating beside the hand that holds it. On `--zoom`, count both
  images' dark pieces and enclosed light gaps inside the part's box, and write
  each gap and each join as a mark of its own.
- **A region outline is not a silhouette, and a scan run is not a contour.** Ink
  splits a flat into several objects (a shoe and the straps on it, an ear and
  the spiral inside it), and the tracer and a row scan return the flat, not the
  object. The ink class merges forms the same way: a nostril hook touching a
  moustache came back as a hump on the moustache's outline. Where `--line` sits
  below the heaviest ink, those lines come back as rings named after the nearest
  dark flat (a garment's name round every silhouette); read them as ink. Before
  inking any contour taken from either source, `--zoom` that object against the
  subject and say which lines are its edge and which are inside it. No numeric
  check sees this; one look does.

  The two sources also put an edge in different places. A traced boundary is the
  ink's centre line, while a class mask or a scan run stops at its inner edge.
  That holds only for a line narrower than `--line`, which the tracer hands to
  its neighbours. A heavier line stays a black flat of its own, and the
  neighbour's boundary is then its inner edge too (in one measured case about
  24px inboard of the centre, on a chin). The silhouette lines are the heavy
  ones, so place those from a scan across the ink.

  An open line inside a form (a crease, a fold, a ridge) is narrower than
  `--line` and is handed to the flat around it, so the trace has nothing to read
  it from. `check.py subject.png --ref subject.png --scan BOX --side S` prints
  each row's dark runs on the subject alone. Place ink from the scan, not the
  trace: strokes placed from the trace came out half a line inboard, and tubes
  read thin.
- **Straights are `smooth=False`.** Fills are smoothed by default, so any flat
  with a corner on the frame (sky, sea, a field, a cliff running off the edge)
  needs `smooth=False` too, or it bulges into a round hump at every corner. So
  is any closed quad (smoothed, four
  corners render as a lens), any organic form's one named corner (a glove's
  cuff, a heel: smoothed through the right points, a glove lost its cuff and was
  named "the hood"), and every stroke of a faceted form such as a rock, crystal
  or folded paper (rendered smooth, a rock field became river stones and every
  gate passed), including its gesture loop. `closed=True` must not repeat its
  first point. Smoothing is per
  call, not per point list: a quad's list reused from its `smooth=False` fill
  for its ink, without restating it, came back as an ellipse. A small closed form
  takes `tool="pen"`. A flat takes `tool="flat"` with `size` and `scale` pinned,
  or its outline renders 5px wider than you asked. Everything else that is
  organic (fur, a coat, a petal, a cloud) keeps the default smoothing: a soft
  form typed as a `smooth=False` polygon renders faceted, and reads as cut
  paper rather than as the form.
- **Draw a weight swatch first.** Draw one vertical stroke per width, spaced
  apart, with the tool you will use, written with `write(..., swatch=True)`. Read
  it back with `--weights` on a row that crosses the strokes. Then read it again
  on the drawing after its first ink: the same weight once ran 1–3px heavier on
  curves. A hard-edged pen matched to `--measure-line`'s p90 reads heavier than
  the subject's soft line, so match it to the dark core that `--weights` reads.
  Then look at the swatch, and later the first ink, downsampled to the delivered
  size. Weights matched in the 4x space can vanish there: a 3px line at 4x is
  under 1px when the picture is viewed, and the drawing reads as flat colour.
  Raise the finest weight until it shows at delivered size, and keep the span.

  Each tool has its own range. `pen` is the hairline instrument, and `brush`
  bottoms out near 2px at 1:1. At the same `size` and `scale` a brush runs about
  twice a pen's width. A long straight (a pole, a tube, a frame edge) wanders
  several px off its points under the default hand, so pass `hand=0` there. A
  flat (`tool="flat"`) never drifts: it lands on its points at any `hand`, so
  the ratio of two bands set side by side holds. The named nibs are pitched for a ~430px subject. On a single object of another size
  call `gauge(subject_height)`. On a 4x scene the named nibs are unusable, so pin
  `size` and `scale` from the swatch by hand, once for the whole document.
  `weight=` is pressure, not width.

  A band wider than the heaviest weight in the swatch (a strap, a tyre) is a flat
  with both sides as points, closed. So is a small form dark all through, such as
  a droplet whose ink is wider than its interior, with the interior written over
  it. Measure each mark's width on the subject before asking for it, and try the
  next weight up before recording a limit.
- **Measure the ground.** Everything on it is judged by its contrast with it.
- **Never retype a coordinate from memory.** Re-measure it.
- **A filter that matches the palette exactly measures the wrong thing on a
  shaded subject.** A limb is its lit value plus a shade band, so a skin-only run
  stops at the shade and reports the limb short, or missing. Every measure taken
  this way made the subject too narrow, and the drawing then looked too wide.
  Measure a form by its whole value group, or between the ink lines either side.
  The same trap counts a dark fill as a line. Look at what a run-based measure
  actually classified.

## Judges

**Describer.** `describe.sh image.png [RUN]` saves its answer beside the image as
`image.describe[.RUN].md`. A reply without five numbered answers (the CLI's own
error) is refused with exit 1 and nothing written; a usage or rate limit exits 3.
It shows the describer a copy under a neutral name, so a crop named after its
part does not hand over the answer. The describer is
blind and factual, and it excuses what it sees, so ask it what a thing is, never
whether it is good. Where its answer to 3 or 4 differs from the subject's, the
picture's action is wrong, and that is the first fault whatever the numbers say.

The describer is noisy from run to run, so at a gate run it twice and keep only
what both runs say, by meaning rather than wording. A clause that one run states
and the other drops is not a verdict either way. Describe the drawing at the
subject's size: downsample `drawing.png` to `subject_1x.png`'s dimensions first,
so both are read at one scale. Run it twice on the subject too. A clause that the
subject's own two runs do not share is not an acceptance clause and must not be
gated on, otherwise a stage is held against a target that does not survive its
own noise. Run it on part crops as well: a face can pass at 1:1 and carry the
opposite expression at 4x. A crop also holds its neighbours, and a neighbour
still at an earlier stage gets misnamed (an unbuilt helmet was read as a slab of
hair). A clause about a part that is not yet drawn is not a verdict on the part
you are judging.

**Naming a part.** Crop a part's box out of the subject and out of the drawing
(a plain PIL crop), run `describe.sh` on each, and read the two paragraphs side
by side. This is the only instrument that asks what a thing is. Every other one
measures presence, placement, value or design, and an object can pass all of them
while reading as a different object: present, in its box, at the right weight,
inside a matching design, and a viewer still calls it a plate of food.

Ask for a paragraph, never a single name. Shown a crude mask, a viewer says
"face", matching "a laughing woman's face" on its head word. A paragraph has to
commit to kind, proportions, parts and angle, so a loss shows.

The describer detects problems and does not measure quality. A wrong name ("animal
paw", "a plate of food") is a true diagnosis. A right name proves nothing:
scored against itself, a subject does not come back at 1.00, a visibly wrong
drawing scores like a faithful copy, and two blind viewers disagree by more than
any such score resolves. Never build a score, a bar or a ranking out of it.

Even a correct name only reaches recognition, never likeness. A face can be named
correctly and still be the wrong shape for the person in the subject. Likeness is
answered by the shape note, checked by two instruments on the centre of interest:

- an **outline scan** (`--scan` on the side the silhouette faces), the only thing
  that sees a wrong turn between two measured landmarks;
- the **two inks** (`--overlay --box`), because the outline is not all of a
  likeness.

For example, a face matched its subject's edge within 10px row by row and still
read wrong: the nose's ridge line ran diagonally from brow to nostril in the
subject, a wide wedge, and near-vertically down the far edge in the drawing. For
every blue line inside the form, say which red line is meant to be it and how far
it runs off, then measure it with `--scan`. There is no threshold. Which line
answers which is a reading, and any distance between two inks shrinks as ink is
added. `reference/measuring.md` has the detail.

**Critic.** A fresh agent is given both images, told which is which, and asked
for the N worst ways the drawing is worse as a drawing of the same thing. It is
told to give no style comments, no praise, and no guesses at how the drawing was
made or how to fix it. Asked for N, it returns N, and about a quarter is
invention, so ask for few and verify each against the render. The critic finds
junction faults nobody listed; it is weak on why.

Before any mark, turn each item into a measurement on subject and drawing. An
item the measurement does not reproduce gets no mark, whoever raised it. Measure
a claim with an instrument that can see it. A claim about shape ("the pad is a
rounded oval") is measured on `--zoom` or `--overlay --box`, never refuted by row
widths: a pad with the right width on every row and the wrong shape was cleared
by a width scan and came back real a round later. Give each round's critic
`refuted.md` along with the images, so it does not re-raise what was measured and
refused.

Write each refusal down in `refuted.md`, one line per item: the claim, the
measurement on each image, the verdict. An unrecorded refusal is re-raised next
round, and the second time it is more likely to be obeyed than measured. The note
is also where inverted faults turn up: an item that does not reproduce on the
form it names is often real on the form next to it.

**Numbers.** These are the `check.py` flags.

| flag | sees |
|---|---|
| `--masses` | the wrong shape: line closed away (dark runs thinner than the subject's line), both cut on the subject's value levels, `--colours` 3 by default. **A design gate, not a proportion gate**: a head half again too wide is still a pale blob above a dark torso at thumbnail size, and passes |
| `--scan x,y,w,h --side S` (needs `--ref`) | per row, subject beside drawing (`--value NAMES` scans runs of those palette names instead of dark ones): the first non-ground pixel from that side, and the dark runs inward from it. The instrument for a coordinate and for a proportion. `<<` marks an edge off by over 2% of the box, and `runs a|b` marks a row whose line count differs: a thick line drawn as two, or an interior line drawn somewhere else |
| `--overlay` | the drawing blended over the subject. With `--box x,y,w,h`, the two inks over that box (`--value black` reads only the line; without it every dark flat, such as a glove or bar tape, shows as ink): the subject's blue, the drawing's red, black where they coincide. On `blockin.png`, whose stock lines are too pale to read as line, pass `--dark 200`. The only view of interior lines (see above). It gives no number, on purpose |
| `--parts parts.json` (needs `--ref`) | a part that is absent, or drifted out of its box; each shape note is printed over its crop. `form` is the share of the box off its own median grey, `off-ground` the share unlike every colour round the box (a fence on a road beside a field stands on two grounds, both read off the picture); MISSING? needs both low. It answers whether the part is there, never whether it is recognisable. Only a describer on the assembled picture answers that. At S2 every feature whose marks wait for S3 reads MISSING?, which is the staging and not a fault |
| `--checklist parts.json` | a sub-form that a reference's checklist names for an object in the inventory, with no entry and no reason in `_absent`. Run by `build.sh`, and blocks it. Warns when no reference object matched any key, which makes its PASS empty |
| `--counts parts.json` (needs `--ref`) | a group of repeated forms culled, merged or added, where the subject itself counts; exit 1 is FAIL, exit 2 is UNCHECKED rows |
| `--colour parts.json` or `--colour x,y,w,h` (needs `--ref`) | a part whose colour has drifted: per box, at the subject's size, the median hue, saturation and value of the object's own pixels (line left out: a run darker than `--ink`, default 60, and no wider than `--line`, default the subject's longer side / 200 and at least 6, so a dark flat such as a roof, a timber band or a black coat is read as colour however dark; `INK=` and `LINE=` set both for `gates.sh`; in the drawing, the ground is `--ground`, default palette.json's `background`; in the subject, the object is the colour clusters nearer, in hue and chroma, the drawn object's colours than that ground, so the shade and grass round a photographed part are left out), and `mid`, the saturation of the most saturated tenth of its mid-tones. `<<` on hue more than 15° off, median saturation a third or more lower, `mid` a fifth or more lower (a starting figure), or value more than 0.15 off. A low `mid` with matching medians is a palette sampled as an average: the light and the shadow match and the saturated step between them has gone beige. Small or mostly dark boxes (an eye, a nose, a tag) give noisy rows; read the large ones. **The stage 0 sample wins over a value flag.** The subject's median takes in the dark between hairs or leaves and the side in shade, while an entry is sampled at the saturated mid-tone patch, so on fur or foliage the subject reads darker than a correctly sampled flat. Answer a value flag with the ramp's darker step (a shade flat, strands, hatching) where the subject is darker; re-sample an entry only when the flagged box holds the patch it was sampled from. A row saying no subject colour is nearer the drawn object's than the ground is a flat drawn in a colour the subject does not have there. A box with too few colour pixels (line on bare ground) is shown and not counted. Run it on `drawing.png`; a `style.json` finish lowers saturation again in `final.png`. Exit 1 when a row is flagged |
| `--ranking parts.json` (needs `--ref`) | a part shouting above its `tier` (named when it outranks the whole focus tier), and two forms merged into one value. Zero-sum: the only way to lift a part is to put another down |
| `--doubled ops.json` | one edge stated twice on the page. Write order, `erase` and `back` are replayed, and an edge a later flat buries is not listed. Two lines that cross in an X, or meet in a V or a T, at 5° or more (crossing spokes, a chain over a spoke) are not listed. Two lines that run side by side (two bands, parallel cables) are, and so is a contact between two objects' edges, so look before you merge |
| `--joins ops.json [--parts parts.json]` | a line that stops just short of the mark it runs at, in the same object (the tag up to its first `.`): a gap of one to eight line widths, edge to edge, which reads as neither a join nor a separation. A chain short of its sprocket, a spoke short of its rim, a ring left open. Ends that some mark touches pass, and so does a styled hand's 1–4px fall-short. Marks beside the end (a hatch group's next line), a hairline under half the end's width, and marks with the end's own tag are not join targets. A pair meant to stop short goes in parts.json's `"_gaps": ["tagA/tagB", ...]`, matched by tag prefix. Exit 1 when anything is listed |
| `--depth ops.json parts.json` | an occlusion the inventory decided on that the write order does not deliver: the far form's ink after the near form's fill, drawn across it. **UNRESOLVED** is not a pass; it means tags and inventory are not one vocabulary. **UNLISTED** is a list to work through: one part's ink shown across another's flat where no row decides which is in front. Warns on a key written `near/far`. A row with `"in_front": "same"` (sub-forms of one surface) has no order to check |
| `--stages ops.json` | a stage that does not exist, and a mark the script did not write: called from another file, stamped by a loop or an import, points loaded or computed. It does not check that each ink has a contour under it. Pasted generated literals pass it |
| `--faces ops.json` | a flat simpler than the traced region it overlaps: a shade drawn as a quad on a form of twenty-five corners reads as a patch stuck on. Pass the object's own trace as `--regions`. On an upscaled or generated subject, also pass `--grain` of three times the upscale factor, or the serration reads as corners (in one case 150 false rows, and 4 with it). A deliberately straight form cut by intruding objects still fails it, and so does a silhouette flat whose region is punched by holes (vents written over a shell). More corners would be the wrong fix in both cases |
| `--unfilled --paper C` (needs `--ref`) | bare paper where the subject carries the object: a flat short of its own ink, most often along an open edge that `--registration` cannot see. The object is read off the subject's ground (`palette.json`) and bareness off `--paper`. Render a check copy with `background` repointed to a colour nothing uses, and pass that |
| `--registration` | colour and line disagreeing. Not usable on a full-bleed picture, where every band that runs off the frame reports as a spill |
| `--zoom x,y,w,h` | whether the marks are any good, at 4x, ticked in whole-picture coordinates. **The primary gate on any object**: three versions of one object passed every numeric gate and ranged from a beetle to something a blind viewer named at once, and only the magnified pair told them apart. Ticks orient you; they are not a coordinate (`look.py grid` places a point, `look.py probe` and `edge` confirm it) |
| a blind viewer on a part's crop | what the part is. The only gate that fails a blob. A detector, not a meter |
| `--weights rows` | the line hierarchy against the subject's, each run as `width@centre` |
| `subject.png --hatch x,y,w,h [--ref drawing.png]` | the line marks in a box, flats left out: coverage, and per group of parallel marks its angle, spacing, length and width. With `--ref`, the drawing's box beside it, `<<` on a group missing, an angle more than 20° off, spacing off by more than half, or coverage under half; FAIL (exit 1) on a group whose marks are over 1.6× the subject's width, or over 1.6× its share of the outline's weight (outline = 95th-percentile line over the picture). Widths are read at half each mark's darkness, in the subject's pixels whatever the render's size. `--light` reads pale lines on a dark. **WARN grain** when the marks are short (median under 3 × `--line`) and fade under a light blur: photo grain, fur or a dot screen, not hatching. Numbers only: where the hatching is, never strokes |
| `--linework parts.json` (needs `--ref`) | hatching left out: FAIL where an entry's `hatch` angle has no line group within 20° in the drawing's box. Hatching too heavy: FAIL where that group's marks are over 1.6× the subject's width, or its hatch/outline ratio over 1.6× the subject's (both printed per entry; outline = 95th-percentile line over the inventory's boxes). And a flattened weight hierarchy: FAIL where the drawing's span (heaviest over finest line, 95th over 10th percentile on the marks' centre lines) is under half the subject's. A FAIL in a box whose lines run wider than `--line` adds a hint: an edge heavier than `--line` reads as a flat, so a narrow part between two of them loses its hatching; thin the edge first. Exit 1 FAIL, 2 UNCHECKED (the written angle does not reproduce on the subject) |

Treat every number as a list to work through, never as a score. The cheap way to
move a mark-counting number is to add marks, and a whole-picture pixel difference
goes up on a round that made the drawing better. The target is the shape note and
the acceptance list; a judge only says whether they are now true.

## The correction cycle

Corrections are where a drawing is won or abandoned, so the loop is fixed rather
than left to judgement.

**Iterate one part, never the whole picture.** A full-picture round costs an
order of magnitude more and tells you less. Its faults are per-part anyway, and a
round spent re-working everything is a round not spent drawing. Take one part,
work it through its own stages, and leave it when it passes.

**There is no score, so the acceptance list drives the loop.** Order the parts by
the clauses they break, worst first. A part a blind viewer misnames outranks one
whose shape note is merely inexact, which outranks a part that is only absent.

```
per part: --zoom beside the subject, and a blind viewer on its crop
  the crop is misnamed        -> the worst fault there is. Its stage failed;
                                 go back to that stage, not to a correction mark
  named, note untrue          -> measure the clause on subject AND drawing
                              -> name the stage it belongs to, fix it there
  named, every note true      -> pass; take the next part
  the same item returns after
  a round that addressed it,
  and still measures true     -> plateau: stop, and report what it plateaued on
  a clause flips run to run
  with no mark changed        -> describe the subject's own pair again: a clause
                                 the subject's runs do not share is noise, not a
                                 plateau of the drawing
  it returns, and is already
  in refuted.md               -> not a plateau: the critic never saw the refusal.
                                 Re-measure once with a different instrument;
                                 still refuted, note it and go on
  budget spent                -> hand the remaining parts to another agent;
                                 never leave one half-drawn
```

**Fix a contradiction before an omission.** A contradiction is a fault; an
omission is often a choice. An item that no measurement reproduces gets no mark
and goes to `refuted.md`. A fault that is wrong in shape or along a whole length
goes back to its stage. Only a local, bounded fault earns a `correct` mark.

**Log every cycle in `notes.md` beside the drawing**: the cycle, what was changed,
what the viewer called each crop, which clauses became true. Keep this trail
because a plateau looks like progress from inside, and with no curve to plot the
trail is all there is.

**A person is the gate, and a person grades against the wrong thing.** Someone
reading each render compares it to the previous render, and after a few rounds
signs off on work that has improved and is still bad. No number can be trusted to
replace the person, so fix the procedure. Make every judgement beside the
subject, at the same scale, in one image. The question is never "is this better"
but "is this clause true". Look at the render itself; a viewer's words or a
gate's number reported as the verdict is not a look.

A look finds problems, and a number decides whether a mark moves. Proportion
judged by eye from a side-by-side was wrong in both directions on one picture (a
head that looked 10% large was 3% wide; a chin that looked 70px low was 6px off).
A person reading the same thumbnails was half right on every item, and a scan or
an overlay settled each case. A downsampled side-by-side also makes every small
drawn form look bigger and blockier beside the subject's soft edges. So an item
raised by eye, whether by you, a critic or a person, is measured on subject and
drawing before any mark, exactly like a critic's.

To judge a fault, never read a coordinate off a zoom's tick labels or a resized
grid crop. Both produced faults that did not exist (a small opening read as 50px
high, two thin lines read as 20–40px off) and a probe of the render refuted
them. Probe or scan the pixels (`look.py probe`, `look.py edge`, `--scan`).
Placing marks is different: on a subject with hundreds of points, reading them
off `look.py grid` is often the only practical way, and it is allowed, provided
the placed points are then checked by probing or scanning the pixels of subject
and render (§ Reading coordinates). A number has a
converse too: a row run through a dark form misreads
wherever a nearer pale form sits inside it, so check by eye what the run crossed.

## Rules

- **Seeing is the work, and the reading is in shapes.** A sentence about shape is
  a target, and a box is the only thing a box can be compared against.
- **Whole before part** in placement and stage, never in investment. How far each
  tier is built is decided once at stage 0 and is not equal. The furthest tier
  gets no marks of its own.
- **The mass is the unit; objects are named afterwards.** A dark shape is placed
  first and called a rock later. Most junctions in a scene are lost. Losing an
  edge is the only cheap way to push an object back, because a glaze over what
  shouts makes a dirty copy of it in place.
- **Commit late.** Gesture, straights, curve, ink, black, in that order.
- **Form before edge.** Marks answer to an implied volume. A traced silhouette
  cannot be wrong, so it cannot be corrected.
- **Two value groups, never overlapping**, decided before any tone.
- **Vary execution, lock structure.** Weight and path vary; proportion, landmarks
  and identity markers do not. Never mirror, and avoid twinning: two limbs or
  two figures in the same pose read as a copy.
- **Exaggerate along each feature's own direction**, mildly: a small mouth gets
  smaller.
- **Overlaps are objects.** They have their own inventory entries and their own
  depth decision, and they are drawn with both objects present. The accent of the
  picture is where forms touch. A tangent is a near miss and reads as neither
  touching nor separate.
- **A part that is absent or unrecognisable is a failed stage**, not a known
  fault. `--parts` catches the first, and a blind viewer on its crop catches the
  second.
- **Stage 10 runs before anyone sees the picture.** A correction that changes
  nothing when switched off comes out. Zero `correct` marks, because every fault
  went back to its stage, is a pass.
- **Where the subject itself merges two edges, draw one.** `--doubled` wins over
  `--registration` there. The spill it then reports is the subject's own, and
  restating the edge to silence it puts back the fault the other gate exists to
  catch.

## Style: making it look drawn by a person

The gates judge a clean tldraw render, and that render looks like vector art:
flat colour, even ground, every line meeting exactly. A `style.json` beside
`draw.py` changes how your marks land and how the finished picture is
rendered. It never adds a mark. Without the file nothing changes.

```json
{"medium": "watercolour+ink", "hand": 0.5, "finish": "clean",
 "handedness": "right", "paper": "cold-press", "scan": true, "seed": 11}
```

| key | values | what it changes |
|---|---|---|
| `medium` | `ink-pen`, `brush-pen`, `pencil`, `marker`, `watercolour+ink`, `gouache` | the default instrument in `pen.py` (an explicit `tool=` wins), and how `finish.py` puts colour and line on the paper |
| `hand` | 0 (tight) to 1 (loose); 0.5 is the default hand | drift, overshoot, lines that stop 1–4px short of the line they meet, weight variance between marks, hooks at fast starts; lower smoothing in the final render |
| `finish` | `clean`, `sketch` | `sketch` keeps gesture, block-in and contour in the final picture as faint graphite |
| `handedness` | `right`, `left` | the direction each stroke is drawn in, so tapers and hooks fall where that hand puts them. The points do not move |
| `paper` | `none`, `smooth`, `cold-press`, `newsprint`, `sketchbook` | paper tint and grain, multiplied into everything |
| `scan` | `true`, `false` | a slight tilt, uneven light, sensor noise and a JPEG save |
| `renderer` | `tldraw` (default), `brush` | `brush`: `brush.py` lays the marks of `ops.json` again as the medium would, with dabs along your points (weight from pressure, edges the paper gives, dry brush on a fast tail, brush passes inside each flat's own outline), into `brush.png`, and `finish.py` works on that. It adds no mark and keeps your stacking order |

`build.sh` then also writes `final.png`, with the colour layer shifted a pixel
or two off the line as hand-coloured prints are (and `brush.png` first, with
`"renderer": "brush"`). **Gates and the describer
always read `drawing.png`, never `final.png`.**

Some of a human look is in what you draw, and no renderer supplies it. Decide
these at stage 0 and write them in `reading.md`:

- **How many marks.** An experienced hand states a contour once, with weight
  where it matters, and lets edges get lost. A sketch restates a key contour
  two or three times along its run, slightly apart. Both are marks you write.
- **How far to drift.** A person copying a subject simplifies it and moves off
  it by a few percent. With `hand` above 0.5, an outline scan within a few
  percent of the subject is a pass. Do not correct it back toward a trace.
- **Colour against line.** In `finish: sketch` a flat may stop short of its
  line or run a little past it, and the rule against spill in
  `reference/colour.md` does not apply. In `clean`, it does.
- **Hatching** follows the subject's measured angle where it has one. Where you
  add hatching the subject does not dictate, it follows the hand: strokes slant
  `/` for a right hand and `\` for a left.

## Reference

`reference/method.md` is the full method. `reference/scene.md` covers the scene
level in depth: tone plan, masses, tiers as masses, the overlaps table, and the
named devices for what is not rendered. The rest is detail, loaded per task.

- Subjects: `head`, `figure`, `hands-and-feet`, `quadruped` (dogs, cats, horses,
  cattle), `bird`, `bicycle`, `vehicle` (cars, boats, aircraft, trains),
  `building` (perspective, exteriors, interiors, furniture), `landscape` (sky,
  water, mountains, distance), `tree-and-plant` (trees, foliage, flowers, pots),
  `still-life` (ellipses, containers, glass, fruit, food, everyday objects).
- Photographs: `photograph` (simplifying the values before tracing, finding the
  silhouette, which edges to keep, fur and grass as directional strokes, and
  why `--hatch` misreads grain).
- Craft: `measuring` (comparative measurement, sighting, plumb lines), `light`,
  `line` (weight hierarchy, hatching and texture by hand, inking order), `tone`, `colour` (flatting,
  trapping), `correcting`, and `redrawing` (a generated image as subject: what
  it hands you free, what must not be copied).

Load every subject file whose subject appears in the picture: its checklist
blocks are enforced on `parts.json` whether you read the file or not. Use an entry to diagnose a problem, never as a template to follow. If
a passage could be followed with the subject covered up, it is wrong.

Notes from an earlier attempt are an input to the next attempt, and they
contaminate any test of this skill. To test the skill, give the agent this
directory and the subject and nothing else.
