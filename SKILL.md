---
name: drawing
description: Draw something yourself, mark by mark, on a real canvas — see the subject, block it in with straights, gate each stage on a check, and only then commit to curve, ink and black. Use when asked to draw, sketch, illustrate, redraw or restyle an image by hand rather than generate it with an image model.
---

# Drawing

You place every mark. The tools measure the subject, render what you placed,
and refuse ink that has no gesture, block-in and contour under it. The judge is
a blind describer that has seen neither the subject nor your script.

Placing a mark is trivial; knowing where it goes is the work, and every
instrument here exists either to see the subject more exactly or to catch the
error you have gone blind to. `reference/method.md` holds the full method and
the measured failure behind each rule; `reference/scene.md` holds what a scene
is and why it is not a sum of objects. Load them when a gate fails and you
cannot say why — not instead of drawing.

## Setup

```bash
cd harness && npm install && npm run build && npx playwright install chromium   # once
```

Python needs `numpy`, `scipy`, `pillow`, `opencv-python`. `describe.sh` needs
the `claude` CLI. One directory per drawing holds `subject.png` and everything
below; nothing goes in `/tmp`. Copy `build.sh` in beside it and set `SKILL=` to
this directory. Your script is `draw.py`; it writes `ops.json`.

## One object or a scene

**A single object is drawn on one ladder, at one scale.** A scene is designed
first, as masses, and then every object in it that must be recognisable is
drawn as a single object in its own magnified crop and placed back. Two things
force that:

- **You can only see what is large on the page.** A render is looked at at
  roughly 1,500px whatever its size. On a single object every feature is
  judgeable; in a scene a 12px eye or a 20px hand is below what you can judge
  as a shape, and a part you could not see while drawing it is a part drawn
  badly. **Nothing drawn at panel scale by eye comes out well — a light bulb
  and a strip of tape no more than a face.** So every object that must be
  recognisable is a part, cropped small enough to see and drawn large enough
  to work on; the only other thing an object can be is welded into a mass
  with no marks of its own. There is no middle tier.
  **The box and the scale buy different things and are chosen separately: the
  box buys seeing, the scale buys drawing resolution.** A render is read at
  ~1,500px whatever it contains, so magnification is `1500 / max(box_w,
  box_h)` and no `scale` changes it — an object whose box is as wide as the
  panel cannot be magnified at all, and has to be split into boxes that can,
  cut at a seam some other form already hides. `scale` is then chosen so the
  smallest feature you must draw lands near 40px of canvas, which is a
  statement about nib headroom and not about seeing.
- **A scene is not a sum of parts.** What organises it lives above the object:
  one centre of interest, a tone plan of two to four masses, most edges lost
  into the mass behind them, and the junctions where things touch. An object
  drawn well and dropped into a panel with a closed contour of its own is what
  breaks the picture. The scene level decides these before any object exists
  and checks them after every object is placed.

Which you have is decided at stage 0, by the reading, and the answer can be
"a single object" for a picture with furniture in it.

## The object ladder

Each stage narrows one freedom and is cheap to fix while the next is expensive.
**A stage may not begin until the previous gate is true on a render you looked
at**, and no part may be more than one stage ahead of any other. `pen.write`
refuses ink that has no gesture, block-in and contour stage under it.

| # | Stage | You produce | Gate |
|---|---|---|---|
| 0 | **Read** | `palette.json`, `regions.json`, `subject.describe.md`, `reading.md`, `parts.json` | every tier-1/2 part has a shape sentence; the acceptance list exists and quotes the describer's answers 3–5 |
| 1 | **Gesture** | 3–10 strokes, `stage="gesture"`: the line of action, then each big mass as one loose loop | `describe.sh gesture.png` answers 2 and 3 the way `subject.describe.md` does. If the event does not read here, no later stage puts it in |
| 2–3 | **Block-in** | `stage="blockin"`, `smooth=False`: every tier-1/2 region as its `blockin` straights from `regions.json`, junctions as points shared by name | `check.py blockin.png --ref subject.png --overlay`: the straights sit on the subject's edges |
| 4 | **Construction** | `stage="construction"`: for each volume, its turn written down, its centre line where the turn puts it | a written turn for every tier-1 form |
| 5 | **Masses** | `stage="fill"`, `tool="flat"`: one region per surface, drawn past where the ink will go. Written in depth order, each form's fill directly before that form's ink, so a nearer form's flat covers the ink of the one behind it. Never `back("fill")`: it sends every flat behind every line and the object can then not occlude itself | `check.py drawing.png --ref subject.png --masses` — the two read as the same shape, said in words |
| 6 | **Contour** | `stage="contour"`: the real edge, curved where the subject curves, from `contour` in `regions.json` | `--overlay` again |
| 7–8 | **Ink** | `stage="ink"`, one stroke per edge, each width measured on the subject, every stroke tagged by the edge it states; `fade`/`erase` blockin and contour | `check.py drawing.png --doubled ops.json` and `--ladder ops.json` pass |
| 9 | **Fill** | flats refined; blacks massed as one value before anything is graded | `--hide ink` still separates figure from ground |
| 10 | **Correct** | `stage="correct"` marks aimed by the judges, N rounds fixed at stage 0; `refuted.md` for every item that did not survive its measurement | `describe.sh drawing.png` matches the acceptance list clause by clause; `--registration`, `--parts`, `--ranking` |

Going back up the ladder invalidates everything above it: re-run every stage
after the one you changed. The script re-renders in one call, so that is the
cheap answer.

`build.sh` draws `gesture.png` and `blockin.png` in stock stage colours on a
stock ground, with every `erase`/`fade` left out so they survive cleanup; they
are for the event and the placement, and the ground is judged on
`contour.png` and `drawing.png`, which use the palette.

## The scene ladder

The object ladder, wrapped. Stages S0–S2 draw no object: they design the
picture. Then every part runs the object ladder in `parts/<name>/` at its own
scale — the figure, the vehicle, the lamp, the picture on the wall, each one.
Then the scene is assembled, and what is drawn at panel scale is only the
junctions between parts and the blacks across them.

| # | Stage | You produce | Gate |
|---|---|---|---|
| S0 | **Read as a tone field** | everything stage 0 produces, plus in `reading.md`: **one** centre of interest; the tone plan (a dominant value, two to four masses); the **welded shapes** — five to twelve, each edge marked sharp or lost, no object with a closed contour; every object as either a **part** or **welded** — a part is an *object* (the rider, the bicycle, the lamp), never a feature of one; **an object the describer names in answers 3–4 is a part**, because the acceptance list will ask for it, unless it has no silhouette of its own against its surround, in which case write it down now as a clause the drawing will not earn; for each part its crop box (small enough that the part fills a render) and its scale (large enough to draw its smallest feature), its nested parts (a face inside a figure at a higher scale again), and its weight pitch relative to the centre of interest; the **interfaces table** with an `in front` column per crossing; the census with its zeroes | a thumbnail of the tone plan reads as a design with one dominant value and the strongest contrast at the focus; every interface has a depth decision; the part list and the acceptance list agree |
| S1 | **Armature** | `stage="gesture"`: eye level, ground plane, the main lines, the line of action, the major masses as loops | `describe.sh gesture.png`: the event and the big shape read |
| S2 | **Masses** | `stage="blockin"` straights for the welded shapes, then their flats `stage="fill"` — the middle tone over the whole, then lights, then darks, honouring sharp/lost. **Every object's mass goes in here, part or welded**: the part/welded split decides whether an object gets *marks*, never whether its *value* exists. A part left out is a hole in the tone plan, and when a whole value family lives inside parts — the darks usually do — the gate cannot pass at all until they are in. A flat is not ink, so this costs nothing at the gate. No object's *marks* yet | `--masses` against the subject at thumbnail size; **no object has an ink contour** (`--ladder` shows ink 0) |
| S3 | **Every part, each alone** | `crop.py` each part into `parts/<name>/subject.png` at its scale; run the whole object ladder there with its own `palette.json` (the scene's), `regions.json`, `parts.json`, `draw.py`, `build.sh`. A part may hold parts: a figure at 2x carries its face in `parts/<figure>/parts/face/` at 4x, placed into the figure the way the figure is placed into the scene; `build.sh` recurses. Its brief from S0: which of its edges are lost, what is in front of it, its weight pitch. A simple manufactured form — a lamp, a strip of tape, a frame — keeps the tracer's contour nearly whole and is cheap; a figure is built on the figure ladder with its three masses and every joint, and is not | each part passes its own gates before it is placed, and a describer on its crop names it. A part is a small subject again and gets a small subject's attention |
| S4 | **Place** | in `draw.py`, `place(load("parts/x/ops.json"), origin, scale, only=[...])` per **depth group**, back to front — a bicycle is not at one depth, so a part is placed in tagged groups, each with its fills then its ink. A nearer group's opaque flats cover the farther group's ink: **occlusion is order**, not cutting. `drop=[...]` removes the edges S0 marked lost. **A part's S2 mass is scaffolding and comes out as the part arrives** — leave both and every part carries a fringe wherever the stand-in and the drawn form disagree | `--ladder` and `--doubled` on the assembled `ops.json`; `--parts` shows every part present at its box |
| S5 | **Emphasis** | nothing is drawn at panel scale here. Emphasis was decided at S0 as each part's weight pitch and edge count, and the far parts were drawn lighter and with fewer edges *in their own crops*. Walk the placed panel and confirm the gradient: weight and detail decay from the centre of interest and with depth; welded objects have no marks | no part beyond the focus carries the focus's weight; a describer names every part |
| S6 | **Interfaces** | the enumerated pass over the interfaces table, in the assembled panel and nowhere else: the accent where forms touch, tangents broken by overlap or separation, lost edges confirmed lost, rails and wires only where both values are measured either side | every row of the table has a recorded decision and a look |
| S7 | **Blacks, texture, vignette** | one pass spotting the black pattern across objects; texture fields as one indicated pattern; the whole drawing's silhouette against the paper | `--ranking parts.json`: the focus leads, nothing shouts above its tier |
| S8 | **Correct from a distance** | stage 10, on the panel, with the describer run twice | the acceptance list; `--ranking` still shows one focus |

**Budget by stage.** On a scene S0 is a large share of the job, and the parts
are the rest: a figure or a vehicle costs about as much as a whole flat panel
once did, a lamp a tenth of that, and there is no cheaper tier that produces
anything usable. A self-reported budget comes back low by a factor of two; fix
the part list and the correction rounds at S0 and hold to them, and work in
checkpoints — after S2, after the first part, after the assembled panel — so a
run that is going wrong is stopped before it has spent the rest.

## Stage 0

1. **Palette.** Sample every flat and the ground off the subject into
   `palette.json` — the 13 stock names plus `background`, which is the ground
   and not a fourteenth colour. Write down where each was sampled. A subject
   with more than 13 flats merges the two closest now, in writing, not
   mid-run. **A nested part may still discover a flat the panel could not
   resolve** — a tooth, a tongue, anything smaller than the panel's own
   sampling. That is not a stage 0 failure and it cannot be prevented there;
   repoint a stock name whose own flat is expendable, and record the swap in
   `reading.md` beside the palette.
2. **Trace.** `python3 trace.py subject.png palette.json --png regions.png`,
   then look at `regions.png`. Every flat comes back as a region with its
   outline as straights and as a curve, in the subject's own coordinates. A
   region is a flat, not an object: naming them is the reading.
3. **Describe the subject.** `describe.sh subject.png`. Its answers 3 (what
   each figure is doing), 4 (what touches what) and 5 (expression) are the
   acceptance clauses, quoted, not paraphrased. A drawing that reads as a
   different event has failed whatever else it gets right.
4. **Reading** — `reading.md`: what the picture is, in one sentence; the big
   shape as one or two forms; the line of action; the deviation from the
   average, measured, because that is the likeness; the light source, fixed
   now; the two value families; what you leave out, on purpose; the budget
   and the number of correction rounds; then the acceptance list. For a
   scene, also everything S0 asks for above.
5. **Inventory** — `parts.json`: small, ranked, every entry a shape sentence
   with a box read off `regions.json`. Name the junctions as entries of their
   own — hand/bar, foot/pedal, hip/saddle, tyre/ground, and every joint —
   because that is where every scene fails. Then cut a plain image crop of
   the subject at each tier-1/2 box plus a fifth (not a part; a PIL crop is
   enough), `describe.sh` the crop, and where it does not
   answer with the part you named, fix the sentence or delete the entry. An
   answer naming a neighbour means the box is on the neighbour; "cannot tell"
   on the subject means the part reads only in context, so judge it in
   context later. An entry for a thing the subject does not have propagates
   into every stage below it, and this is the only check that can remove one.

```json
{
  "nose": {"shape": "ON the silhouette: the profile leaves the brow, runs down and OUT to the tip, then turns back under it", "box": [540, 336, 45, 50]},
  "hand/bar": {"shape": "the glove closes over the bar; the bar disappears behind the fingers and reappears 30px to the left. No gap", "box": [318, 470, 96, 70], "in_front": "hand"}
}
```

## Marks

```python
from pen import stroke, frame, fade, erase, back, write, load, place
V = {"hip": (462, 590), "knee": (445, 715), "ankle": (452, 880)}   # measured once, named once
P = lambda *names: [V[n] for n in names]
ops = [frame(0, 0, 928, 1152)]
ops.append(stroke(P("hip", "knee", "ankle"), stage="gesture", nib="fine"))
ops.append(stroke(P("hip", "knee", "ankle"), stage="blockin", smooth=False))
ops.append(stroke(P("hip", "knee", "ankle"), stage="ink", nib="medium", tag="leg.near+rider"))
ops += place(load("parts/bike/ops.json"), origin=(180, 560), scale=2, only=["rear"])
ops += place(load("parts/rider/ops.json"), origin=(300, 60), scale=2.5, drop=["jaw.left"])
ops += place(load("parts/bike/ops.json"), origin=(180, 560), scale=2, only=["front"])
write("ops.json", ops)
```

- **Every mark on its own line with its own numbers.** No function that makes
  a shape, no loop that stamps one, no `ellipse()`: a tool may not supply a
  form you did not choose after looking. A dict of measured points supplies no
  form and is the fix for an edge drawn twice — two objects that share an edge
  share the entry. `place` supplies no form either: it moves marks chosen in
  the crop.
- **Tag every ink stroke by the edge it states** (`tag="jaw.left+cowB"`,
  `+` joins several), so the scene can place a part by depth group and drop
  the edges it has decided are lost.
- **One stroke per member; a joint is a stroke boundary.** A smoothed stroke
  fits one curve through all its points, so a bent form written as a single
  `hip → knee → ankle` stroke comes back as an unbroken bow with no angle at
  the joint — and reads as the *unbent* form, however exactly the joint was
  measured. The points hold the bend and the render throws it away, silently,
  and no numeric gate reports it. Give each member its own stroke, or pass
  `smooth=False`.
- **`place` moves strokes and nothing else** — a part's own `erase`/`fade`/
  `back` decisions stay in the part's document, and its `frame` is dropped,
  since a frame is a stroke too and transferring it prints the part's crop
  rectangle across the panel.
- **The tracer's points are measurements, not marks.** They come out in
  perimeter order: keep that order. Resequencing them into what looks like a
  tidier outline folds the walk into arrowheads. Choose which to keep.
  What is drawing is which edges are stated, which are lost, what is left
  out, and what weight each takes. For an organic form that means choosing
  the few points that carry the shape; for a simple manufactured form — a
  bulb, a frame, a strip of tape, a tube — keeping the traced contour nearly
  whole *is* the choice, and the drawing is in its weight and its junctions.
  **Neither move works on a re-entrant region** — a band with shapes punched
  through it, a form whose boundary threads into its own interior. Dropping
  points breaks the walk; keeping it whole fills as spikes and holes. Abandon
  the traced path there and draw a plain polygon from measured extents.
- **A region outline is not a silhouette, and a scan run is not a contour.**
  A flat is split by ink into several objects — a shoe and the straps on it,
  an ear and the spiral inside it — and the tracer and a row scan return the
  flat, not the object. Before inking any contour taken from either, `--zoom`
  that object against the subject and say which lines are its edge and which
  are inside it. No numeric check sees this; one look does.
- **Straights are `smooth=False`**, and so is any closed quad: smoothed, four
  corners render as a lens. `closed=True` must not repeat its first
  point. A small closed form takes `tool="pen"`. A flat takes `tool="flat"`
  with `size`/`scale` pinned, or its outline renders 5px wider than you asked.
- **Draw a weight ladder first**, one *vertical* stroke per `nib=`, spaced
  apart, with the tool you will use, written with `write(..., swatch=True)`,
  and read it back with `--weights` on a row that crosses them. Each tool has
  its own ladder: `pen` is the hairline instrument and `brush` bottoms out
  near 2px at 1:1. The nibs are pitched for a ~430px subject: in a magnified
  crop call `gauge(crop_height)` before the first stroke, or the heaviest nib
  lands below the crop's median line. `weight=` is pressure, not width; width
  is `nib=` or an explicit `size=`/`scale=`. A part's ladder is drawn in the
  part's crop, at the part's scale, and `place` brings the widths back — but a
  nib is an absolute width in canvas pixels, so **divide every nib by the
  crop scale before comparing it to the subject.** At 4x the heaviest named
  nib arrives on the panel a quarter of its width, under the subject's own
  line mode: the named nibs are simply out of reach at high magnification and
  `size=`/`scale=` must be pinned by hand. A
  band wider than the heaviest nib — a strap, a tyre — is a flat: give it
  both sides as points, closed. Then measure the width of each mark on the
  subject before asking for it. Try the next rung before recording a limit.
- **Measure the ground.** Everything on it is judged by its contrast with it.
- **Never retype a coordinate from memory.** Re-measure it.

## Judges

**Describer** — `describe.sh image.png`, saved beside the image. Blind,
factual, and it excuses: ask it *what*, never *whether*. Where its answer to 3
or 4 differs from the subject's, the picture's event is wrong, and that is the
first fault, whatever the numbers say. It is noisy run to run, so at a gate run
it twice and keep only what both runs say; a clause one run states and the
other drops is not a verdict either way. **Run it twice on the subject too**:
a clause the subject's own two runs do not share is not an acceptance clause
and must not be gated on — otherwise a stage is held against a target that
does not survive its own noise. Run it on part crops as well: a face can
pass at 1:1 and carry the opposite expression at 4x.

**Critic** — a fresh agent given both images, told which is which, asked for
the N worst ways the drawing is worse *as a drawing of the same thing*: no
style, no praise, no guesses at how it was made or how to fix it. Asked for N
it returns N and about a quarter is invention, so ask for few and verify each
against the render. It finds junction faults nobody listed; it is weak on why.
Before any mark, turn each item into a measurement on subject and drawing;
an item the measurement does not reproduce gets no mark, whoever said it.
**Write the refusal down** — `refuted.md`, one line per item: the claim, the
measurement on each image, the verdict. An unrecorded refusal is re-raised
next round, and the second time it is likelier to be obeyed than measured.
The note is also where inverted faults are found: an item that does not
reproduce on the form it names is often real on the form next to it.

**Numbers** — `check.py`:

| flag | sees |
|---|---|
| `--masses` | the wrong shape, with line closed away |
| `--parts parts.json` | a part that is absent, or drifted out of its box; each sentence printed over its crop. It answers *is it there*, never *is it recognisable*, and for a small part those are different questions — an unrecognisable part passes this, `--ranking` and its own crop's describer together. Only a describer on the assembled panel answers the second |
| `--ranking parts.json` | a part shouting above its tier; two forms welded into one value. Zero-sum: the only way to lift a part is to put another down |
| `--doubled ops.json` | one edge stated twice from two guesses. A worklist: two bands meant to run together (a rim inside a tyre) are listed too, so look before you merge |
| `--ladder ops.json` | the stage that does not exist |
| `--registration` | colour and line disagreeing. Not on a full-bleed panel: every band that runs off the frame reports as a spill |
| `--zoom x,y,w,h` | whether the marks are any good, at 4x |
| `--weights rows` | the line hierarchy against the subject's |
| `--overlay` | exact drift against the subject |

Every number is a worklist, never a score. The cheap way to move a
mark-counting number is more marks, and a whole-picture pixel difference goes
*up* on a round that made the drawing better. The target is the shape sentence
and the acceptance list; a judge only says whether they are now true.

## Rules

- **Seeing is the work, and the reading is in shapes.** A sentence about shape
  is a target; a box is the only thing a box can be compared against.
- **Whole before part** in placement and stage, never in investment: how far
  each tier is built is decided once at stage 0 and is not equal. The furthest
  tier gets no marks of its own.
- **The mass is the unit; objects are named afterwards.** A dark shape is
  placed and called a rock later. Most junctions in a scene are lost, and
  losing an edge is the only cheap way to push an object back: a glaze over
  what shouts makes a dirty copy of it in place.
- **Commit late.** Gesture, straights, curve, ink, black — in that order.
- **Form before edge.** Marks answer to an implied volume; a traced silhouette
  has no way to be wrong and so no way to be corrected.
- **Two value families, never overlapping**, decided before any tone.
- **Vary execution, lock structure.** Weight and path vary; proportion,
  landmarks and identity markers do not. **Never mirror.**
- **Exaggerate along each feature's own direction**, mildly: a small mouth gets
  smaller.
- **Interfaces are objects.** They have their own inventory entries, their own
  depth decision, and they are drawn with both objects present. The accent of
  the picture is where forms touch; a tangent is a near miss and reads as
  neither.
- **A part that is absent or unrecognisable is a failed stage**, not a known
  fault. Go back and put it in.
- **Stage 10 runs before anyone sees the picture**, and a correction that
  changes nothing when switched off comes out. A fault wrong in shape or along
  its whole length goes back to its stage, not into a correction; a stage 10
  that ends with zero `correct` marks because every fault went back is a pass.
- **Where the subject itself merges two edges, draw one.** `--doubled` wins
  over `--registration` there: the spill it then reports is the subject's own,
  and restating the edge to silence it puts back the fault the other gate
  exists to catch.

## Reference

`reference/method.md` is the full method; `reference/scene.md` is the scene
level in depth — tone plan, welding, tiers as welded shapes, the interfaces
table, the named devices for what is not rendered. The rest is depth, loaded
per task: `measuring` (comparative measurement, sighting, plumb lines),
`head`, `figure`, `hands-and-feet`, `quadruped`, `bicycle`, `light`, `line`
(weight hierarchy, inking order), `tone`, `colour` (flatting, trapping),
`correcting`, `redrawing` (a generated image as subject: what it hands you
free, what must not be copied). An entry is a diagnostic, never a scaffold: if
a passage could be followed with the subject covered up, it is wrong.

An earlier attempt's notes are an input to the next attempt and a contaminant
to any test of this skill. To test the skill, give the drawer this directory
and the subject and nothing else.
