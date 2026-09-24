---
name: drawing
description: Draw something yourself, mark by mark, on a real canvas — see the subject, block it in with straights, gate each stage on a check, and only then commit to curve, ink and black. Use when asked to draw, sketch, illustrate, redraw or restyle an image by hand rather than generate it with an image model.
---

# Drawing

You place every mark. The tools measure the subject, render what you placed,
and refuse ink in a drawing with no gesture, block-in and contour stage. The judge is
a blind describer that has seen neither the subject nor your script.

Placing a mark is trivial; knowing where it goes is the work, and every
instrument here exists either to see the subject more exactly or to catch the
error you have gone blind to. `reference/method.md` holds the full method and
the measured failure behind each rule; `reference/scene.md` holds what a scene
is and why it is not a sum of objects. Load them when a gate fails and you
cannot say why — not instead of drawing.

## You write the marks; tools only measure

The drawing is `draw.py`, and every point of every stroke is typed there by
you, from a measurement you read. A measuring tool may tell you **where things
are** — a landmark, a width, an extent, the rows a slot occupies, a traced
contour to read positions off. It may not **write the op list**. The line is
the point list: a tool that prints `slot 3: rows 212-260, left 118->131, right
140->139` is measuring; a tool whose output is `stroke([...])`, or a list you
hand to `stroke` in a loop, is drawing, and it is not you drawing.
**Skeletonising or vectorising the subject's own ink or flats into strokes or
fills is forbidden**, and so is anything that turns a trace into lines of
`draw.py`: a generated section module, a loop over regions, a generator whose
output you import or paste.

Measured: a panel whose ink was skeletonised off the subject and emitted one
stroke per segment, its flats emitted from the trace, passed every gate here
and the blind describer on every crop. It was a vectorised copy carrying the
tracer's artefacts — a bead at every junction, upscale halos, lost vent tabs,
dropped spokes — and none was a decision that could be sent back to a stage;
the script was seventy lines of concatenation with nothing in it to revise.

`pen.write` refuses, and `--ladder` fails, strokes called from another file, a
call site reached more than once (a loop, a comprehension, an import that
draws), or control points mostly not written as numbers in `draw.py`: silent on
six hand-written drawings, all three signals on the generated one. **Generated
output pasted in as literal lines passes it and is still forbidden.** What makes
a scene affordable is the scene ladder's economy — five to twelve welded
shapes, a part list fixed at S0, marks spent near the focus — never a generator.

## Setup

```bash
cd harness && npm install && npm run build && npx playwright install chromium   # once
```

Python needs `numpy`, `scipy`, `pillow`, `opencv-python`. `describe.sh` needs
the `claude` CLI. One directory per drawing holds `subject.png` and everything
below; nothing goes in `/tmp`. Copy `build.sh` in beside it and set `SKILL=` to
this directory. Your script is `draw.py`; it writes `ops.json`.

**A scene's working space is the delivered size times four**, and every mark,
measurement and render lives in it. Make it once: `subject.png` is the
delivered image upscaled 4x with `Image.BILINEAR`, and the delivered image is
kept beside it as `subject_1x.png` for the describer and the panel-level
reading. Not LANCZOS or BICUBIC: both overshoot into a pale halo beside every
dark line that classifies as the ground (LANCZOS on 0.12% of a panel's pixels,
BILINEAR on none). The ramp beside each line still traces as a ring region
round every outlined form, so trace an upscaled subject with `--fringe 60`. The harness exports at device pixel ratio 2, so render with
`./build.sh --scale 0.5` to get renders 1:1 with `subject.png`. **macOS has no
`timeout`** — it is `gtimeout`, or `perl -e 'alarm N; exec @ARGV' --`.

**Measure `--line` in the space you trace in**: `trace.py subject.png
palette.json --ink NAMES --measure-line` prints the per-pixel min(row, column)
run width of the line; pass its p90. Never multiply the delivered figure: one
panel's line was 6 at 1x and 20, not 24, at 4x, because the upscale's ramp thins
the core that classifies as ink. `--ink` takes every palette name that is line:
not only the darkest near-black, but a line that reads brown over one flat and
black over another, and a line drawn in a colour of its own (a horizon, grass),
which gets its own palette name.

### Measure per object, even though you draw in one document

A panel-wide trace resolves every object at *panel* scale, and a small object
comes back with a handful of points per form that no care at the drawing stage
recovers; tracing the delivered-size image and scaling it up puts every boundary
on a lattice the size of the factor. **Crop each object out of the
working-resolution subject and trace that** — `crop.py subject.png x,y,w,h
meas/NAME.png` cuts it at 1:1 and stores its panel corner in the PNG, so
`trace.py meas/NAME.png palette.json` returns panel coordinates with no flag.
The corner is not your box's corner (the crop has a margin): a box corner
passed as `--offset` put a whole panel's regions 8px off, and is now refused. Marks stay in one `draw.py`, in
one coordinate space; only the measuring is per object. Measured on one object:
77 regions and 872 contour points panel-wide, 156 and 3878 from its own crop
— the difference between a helmet a viewer names and a striped loaf. The
silent symptom is forms with three to nine points each.

**The welded masses are the one thing measured panel-wide**: trace
`subject_1x.png` and read their outlines off that. They carry no ink, so its
1px-at-delivered-size lattice costs nothing, and there are five to twelve of
them — typed into `draw.py` like every other mark, from the trace, at the point
count their silhouettes need. A mass layer of hundreds of flats, one per traced
region, is the generated drawing again. Where two ink-less masses meet, the
edge is one shared entry in the dict, and the far mass runs past it under the
nearer one written after, so no hairline of ground opens along the join.

**And then: a rich trace does not name anything.** Which regions compose an
object, and which single form a viewer reads as it, is the reading, and it
costs the same on a rich trace as on a poor one. Taking the largest region per
object is the failure this invites: a limb comes back as its lit strip beside
a separate shade band, two ribbons; a garment as the two patches either side
of its zip, with no shoulders; an object with no dominant region — a sock, a
sole, a neck — is never drawn, and nothing counts it.

So before any mark, for each object, write down three things:

1. **Which traced regions compose it**, by box, and **what each one is** — the
   lit strip, the shade band, a cast shadow, the ink, a hole punched through it
   by something in front.
2. **Which single form a viewer reads as this object** — its silhouette. That
   is what has to be right; the internal flats sit inside it.
3. **Where the traced contour is the right measurement and where it is not** —
   right for a silhouette, wrong for a slot or a hole, wrong for a re-entrant
   region.

If you cannot write those three, you are not ready to draw it. **A lit strip
and its shade band are one form with two values**, never two flats side by
side. **A form cut in two by a nearer one is still one form, and each cut end
is the nearer form's edge**: it ends on that form's ink, never in mid-surface.
The tracer returns the pieces as unrelated regions, and a scan confirming the
gap is real closes the item without asking what made it. A flat that stops
inside another flat with nothing drawn across its end reads as a patch stuck
on: a band broken by a sleeve became two dark patches on a torso, placed within
10px of the subject, because the sleeve's own edge was never drawn. Name the
occluder of every cut end and `--overlay --box` it; a blue line across the end
with no red beside it is that occluder's contour, missing. Check the part list
against the canvas before calling a panel done.

## One object or a scene

**A single object is drawn on one ladder, at one scale.** A scene is designed
first, as masses, and then every object in it that must be recognisable is
drawn on that ladder too — in the same document, in panel coordinates, at a
working resolution high enough for its smallest feature. Two things force that:

- **You can only see what is large on the page.** A render is looked at at
  roughly 1,500px whatever its size, so in a scene a 12px eye or a 20px hand is
  below what you can judge as a shape, and a part you could not see while
  drawing it is a part drawn badly. **Nothing drawn at panel scale by eye comes
  out well — a light bulb and a strip of tape no more than a face.** So every
  object that must be recognisable is a part, looked at magnified with `--zoom`
  (magnification is `1500 / max(box_w, box_h)`; a box as wide as the panel
  cannot be magnified and is split at a seam some other form already hides),
  and drawn at a working resolution that puts its smallest feature near 40px.
  The only other thing an object can be is welded into a mass with no marks of
  its own. There is no middle tier.
- **A scene is not a sum of parts.** What organises it lives above the object:
  one centre of interest, a tone plan of two to four masses, most edges lost
  into the mass behind them, and the junctions where things touch. An object
  drawn well with a closed contour of its own is what breaks the picture. The
  scene level decides these before any object exists and checks them after
  every object is drawn.

Which you have is decided at stage 0, by the reading, and the answer can be
"a single object" for a picture with furniture in it.

## The object ladder

Each stage narrows one freedom and is cheap to fix while the next is expensive.
**A stage may not begin until the previous gate is true on a render you looked
at**, and no part may be more than one stage ahead of any other. `pen.write`
refuses ink in a drawing with no gesture, block-in and contour stage — it checks
that the stages exist, not that each ink mark has a contour under it.

| # | Stage | You produce | Gate |
|---|---|---|---|
| 0 | **Read** | `palette.json`, `regions.json`, `subject.describe.md`, `reading.md`, `parts.json` | every tier-1/2 part has a shape sentence; the acceptance list exists and quotes the describer's answers 3–5 |
| 1 | **Gesture** | 3–10 strokes, `stage="gesture"`: the line of action, then each big mass as one loose loop | `describe.sh gesture.png` answers 2 and 3 the way `subject.describe.md` does. If the event does not read here, no later stage puts it in |
| 2–3 | **Block-in** | `stage="blockin"`, `smooth=False`: every tier-1/2 region as its `blockin` straights from `regions.json`, junctions as points shared by name | `check.py blockin.png --ref subject.png --overlay`: the straights sit on the subject's edges |
| 4 | **Construction** | `stage="construction"`: for each volume, its turn written down, its centre line where the turn puts it | a written turn for every tier-1 form |
| 5 | **Masses** | `stage="fill"`, `tool="flat"`: one region per surface, **drawn past where the ink will go** — `trap=<px>` on a BODY flat grows it outward by that much, so the contour covers its edge. **Trap an edge that is a silhouette; never trap an edge that is a measurement.** A flat that is a mark in its own right — a vent, an eye, a cast shadow, a shade — is ruined by it, and trapping every closed flat swells the interior shapes until they eat the form. A **band** is the silent case: a strip, a rim inside a tyre, a hem, a strap — its two long edges face opposite ways, so trapping moves both and **the band gains twice the trap in width**, on every band at once, with every gate still passing. Where two bands run concentric or parallel it is their *ratio* that makes the pair read, and trapping converges it. Trap a band's ends, never its length. A fill outline taken from the tracer sits at the colour transition, which is INSIDE the ink, so used verbatim it falls short by half a line width and the ground shows through wherever the contour bulges. Written in depth order, each form's fill directly before that form's ink, so a nearer form's flat covers the ink of the one behind it. Never `back("fill")`: it sends every flat behind every line and the object can then not occlude itself | `check.py drawing.png --ref subject.png --masses` — the two read as the same shape, said in words |
| 6 | **Contour** | `stage="contour"`: the real edge, curved where the subject curves, from `contour` in `regions.json` | `--overlay` again |
| 7–8 | **Ink** | `stage="ink"`, one stroke per edge, each width measured on the subject, every stroke tagged by the edge it states | `check.py drawing.png --doubled ops.json` and `--ladder ops.json` pass |
| 9 | **Fill** | flats refined; blacks massed as one value before anything is graded | `--hide ink` still separates figure from ground |
| 10 | **Correct** | `stage="correct"` marks aimed by the judges, N rounds fixed at stage 0; `refuted.md` for every item that did not survive its measurement | `describe.sh drawing.png` matches the acceptance list clause by clause; `--registration`, `--parts`, `--ranking` |

**Stages 5 to 8 interleave per form; they are not four passes over the whole
drawing.** As soon as two forms overlap, write them depth-major — the far
form's fill, its ink, then the near form's fill *over that ink*, then the near
form's ink. Written stage-major, the far outline lands after the near flat and
draws straight across it: a crease or seam that is not there. **Occlusion is
the order you write in, and nothing else provides it**, and `--depth ops.json
parts.json` is its only gate — which works only if stroke tags and inventory
names are one vocabulary: the interface **key** is written `far/near` in tag
names (`wheel.front.tyre/ground.landing`, not `tyre.front/ground`), `in_front`
sits only on interface entries, and a part with no ink makes its rows
UNRESOLVED, which reads as loudly as FAIL. Matching is by prefix, so a parent's
rows clear only when every sub-form is ordered. A **hole** — a vent, a window,
an eyelet — is an absence in this form, so its flat is written *after* the ink
of the surface it pierces, or that contour runs across the opening.

Going back up the ladder invalidates everything above it: re-run every stage
after the one you changed. The script re-renders in one call, so that is the
cheap answer.

`build.sh` draws `gesture.png` and `blockin.png` in stock stage colours on a
stock ground, for the event and the placement; the ground is judged on
`contour.png` and `drawing.png`, which use the palette. `drawing.png` never
shows gesture, construction, block-in or contour, so nothing needs erasing.

## The scene ladder

The object ladder, wrapped. Stages S0–S2 draw no object: they design the
picture. Then every object is drawn into that same document, in panel
coordinates, at 4x the delivered size (see Setup). One `draw.py`, one
`ops.json`, no second coordinate space.

**Objects drawn in their own crop and composited back came out as blobs; the
same objects drawn whole came out well.** What a crop bought was a forced look
at the object magnified, so that survives as a gate: **`--zoom` every object
before you call it done, always** — an object never zoomed comes back as fat
lozenges and scratches that pass at panel size. Crops survive only for
measuring and for looking.

| # | Stage | You produce | Gate |
|---|---|---|---|
| S0 | **Read as a tone field** | everything stage 0 produces, plus in `reading.md`: **one** centre of interest; the tone plan (a dominant value, two to four masses); the **welded shapes** — five to twelve, each edge marked sharp or lost, no object with a closed contour; every object as either a **part** or **welded** — a part is an *object* (the rider, the bicycle, the lamp), never a feature of one; **an object the describer names in answers 3–4 is a part**, because the acceptance list will ask for it, unless it has no silhouette of its own against its surround, in which case write it down now as a clause the drawing will not earn; for each part its box (the `--zoom` and measuring crop), its smallest feature at working resolution, its nested parts (a face inside a figure), and its weight pitch relative to the centre of interest; the **interfaces table** with an `in front` column per crossing; the census with its zeroes | a thumbnail of the tone plan reads as a design with one dominant value and the strongest contrast at the focus; every interface has a depth decision; the part list and the acceptance list agree |
| S1 | **Armature** | `stage="gesture"`: eye level, ground plane, the main lines, the line of action, the major masses as loops. **The object ladder's "3–10 strokes" is a single object's budget and does not apply here** — a scene needs one per mass plus the ground and eye lines, which runs to fifteen or twenty. Too few and the describer reads one object's parts as another's: a bicycle's bar becomes the figure's outstretched arms | `describe.sh gesture.png`: the event and the big shape read. **Some events cannot be stated here**: a pose carried by value rather than by silhouette — a seated figure with fully foreshortened thighs has a standing figure's outline — or one the describer's category prior outvotes, as a figure above a bicycle reads as riding whatever the lines say. Then the honest move is to record that the event is gated at S2 instead, with the describer runs that show it, rather than to keep redrawing an armature that cannot carry it |
| S2 | **Masses** | `stage="blockin"` straights for the welded shapes, then their flats `stage="fill"` — the middle tone over the whole, then lights, then darks, honouring sharp/lost. **Every object's mass goes in here, part or welded**: the part/welded split decides whether an object gets *marks*, never whether its *value* exists. A part left out is a hole in the tone plan, and when a whole value family lives inside parts — the darks usually do — the gate cannot pass at all until they are in. A flat is not ink, so this costs nothing at the gate. No object's *marks* yet | `--masses` against the subject at thumbnail size; **no object has an ink contour** (`--ladder` shows ink 0) |
| S3 | **Every object, in place** | run stages 2 to 9 of the object ladder on each object — its block-in straights first, in the one `draw.py`, in panel coordinates, working from the furthest object forward. Its brief from S0: which of its edges are lost, what is in front of it, its weight pitch. **Refine the object's S2 mass into its stage-5 fill** — they are the same line of `draw.py`: edit its points in place from the object's own trace, never stack a second fill over it, so there is no stand-in to remove and no fringe. A simple manufactured form is written from its traced contour nearly point for point and is cheap; a figure is built on the figure ladder with its three masses and every joint, and is not | **`--zoom` on the object, beside the subject, before you leave it** — not optional. Then its own ladder gates, `--faces` and `--unfilled` |
| S4 | **Junctions** | nothing to assemble: every object was drawn where it belongs, with its neighbours already on the page, so the interfaces table was satisfied as you went rather than afterwards. Walk it once and confirm each row — the accent where forms touch, the joint line that breaks at the leg in front of it, the lost edge still lost | `--doubled`; `--depth ops.json parts.json` clean, with no UNRESOLVED row; every row of the interfaces table has a recorded decision and a look |
| S5 | **Emphasis** | nothing is drawn at panel scale here. Emphasis was decided at S0 as each part's weight pitch and edge count, and the far parts were drawn lighter and with fewer edges as they were drawn. Walk the panel and confirm the gradient: weight and detail decay from the centre of interest and with depth; welded objects have no marks | no part beyond the focus carries the focus's weight; a describer names every part |
| S6 | **Interfaces** | the enumerated pass over the interfaces table, on the whole panel: the accent where forms touch, tangents broken by overlap or separation, lost edges confirmed lost, rails and wires only where both values are measured either side | every row of the table has a recorded decision and a look |
| S7 | **Blacks, texture, vignette** | one pass spotting the black pattern across objects; texture fields as one indicated pattern; the whole drawing's silhouette against the paper | `--ranking parts.json`: the focus leads, nothing shouts above its tier |
| S8 | **Correct from a distance** | stage 10, on the panel, with the describer run twice. A blind viewer on each part's crop ranks the round: the **misnamed** parts get the budget first, then the parts whose shape sentences are untrue | the acceptance list; `--ranking` still shows one focus; no part misnamed. An item that returns after a round that addressed it is the stopping rule |

**Budget by stage.** S0 is a large share of a scene; a figure or a vehicle
costs a whole flat panel, a lamp a tenth of that. A self-reported budget comes
back low by a factor of two: fix the part list and correction rounds at S0, and
checkpoint after S2, after the first part and after the last.

## Stage 0

1. **Palette.** Sample every flat and the ground off the subject into
   `palette.json` — the 13 stock names (`black grey light-violet violet blue
   light-blue yellow orange green light-green light-red red white`) plus
   `background`, which is the ground and not a fourteenth colour: a mark may
   not use it, so where the ground shows through a hole in a form, spend a
   name on the ground's colour. Write down where each was sampled, then trace
   and read the misfit line `trace.py` prints: a flat the palette lacks comes
   back as a clumped patch of pixels far from every entry. A subject
   with more than 13 flats merges the two closest now, in writing, not
   mid-run. **A nested part may still discover a flat the panel could not
   resolve** — a tooth, a tongue, anything smaller than the panel's own
   sampling. That is not a stage 0 failure and it cannot be prevented there;
   repoint a stock name whose own flat is expendable, and record the swap in
   `reading.md` beside the palette.
2. **Trace.** `python3 trace.py subject.png palette.json --png regions.png`,
   and look at `regions.png` — on a scene, `subject_1x.png` for the reading and
   the welded masses, each part's own crop when you reach it. A region is a
   flat, not an object: naming them is the reading.
3. **Describe the subject.** `describe.sh subject.png A` and again with `B`
   (the run name keeps both files; on a scene, describe `subject_1x.png`). Its answers 3 (what
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
   with a box read off `regions.json`. **An entry descends to the sub-forms
   that make the object what it is**, each with its own box and its own
   sentence: a wheel is a tyre, a rim, its spokes and a hub, not "a wheel"; a
   glove is its fingers, its thumb and its cuff. One sentence for a whole
   object buys one silhouette, and a silhouette is what a viewer calls a
   different object — the census counts these sub-forms already, and this is
   where they become marks. Stop descending where the next level down would
   not survive at the scale you will draw it.
   **Two instances of one object class get the same sub-form list**: the
   second of two wheels, hands or shoes is read with less attention and comes
   back with fewer entries, and its missing sub-form is missing from every gate.
   Reconcile the twins before leaving stage 0, or write down what the second
   genuinely lacks. Name the junctions as entries of
   their own — hand/bar, foot/pedal, hip/saddle, tyre/ground, and every joint —
   because that is where every scene fails. Then cut a plain image crop of
   the subject at each tier-1/2 box plus a fifth (not a part; a PIL crop is
   enough), `describe.sh` the crop, and where it does not
   answer with the part you named, fix the sentence or delete the entry. An
   answer naming a neighbour means the box is on the neighbour — and if a
   tightened box still names it, the part has no silhouette of its own; so
   does "cannot tell". Keep such a part when the acceptance list names it,
   and judge it in context later. An entry for a thing the subject does not have propagates
   into every stage below it, and this is the only check that can remove one.
   **The census of a group of repeated small forms** — vents, fingers, teeth,
   spokes, droplets — is counted on the object's own working-resolution crop,
   never by a describer on a panel-scale crop, which counts blobs and
   under-counts; cross-check it against the **closed** regions the object's
   trace returns (a mismatch is usually forms left open by a surface curving
   away). **Write it into the entry** — `"count": 7, "value": "black+grey"` —
   and run `--census parts.json` after S2 and after the object: it is the only
   gate that fails on an absence, and only where it counts the subject to the
   census — separate forms of one value in a tight box. Crossing or touching
   forms (spokes, slots bounded by their own ink) come back UNCHECKED; count
   those on `--zoom`, both images, into `notes.md`. The tracer drops forms
   under `--min-area` and hands dark forms narrower than `--line` to their
   neighbours, and `--masses` passes without a spray of droplets; a count
   deferred to "later" was never taken.

```json
{
  "nose": {"shape": "ON the silhouette: the profile leaves the brow, runs down and OUT to the tip, then turns back under it", "box": [540, 336, 45, 50]},
  "bike.bar/rider.hand": {"shape": "the glove closes over the bar; the bar disappears behind the fingers and reappears 30px to the left. No gap", "box": [318, 470, 96, 70], "in_front": "rider.hand"},
  "helmet.vents": {"shape": "seven slots radiating from the brow, each tapering to both ends", "box": [380, 100, 330, 200], "count": 7, "value": "black"}
}
```

## Marks

```python
from pen import stroke, frame, fade, erase, back, write
V = {"hip": (462, 590), "knee": (445, 715), "ankle": (452, 880)}   # measured once, named once
P = lambda *names: [V[n] for n in names]
ops = [frame(0, 0, 928, 1152)]
ops.append(stroke(P("hip", "knee", "ankle"), stage="gesture", nib="fine"))
ops.append(stroke(P("hip", "knee", "ankle"), stage="blockin", smooth=False))
ops.append(stroke(P("hip", "knee"), stage="ink", nib="medium", tag="rider.leg.near.thigh"))
ops.append(stroke(P("knee", "ankle"), stage="ink", nib="medium", tag="rider.leg.near.shin"))
write("ops.json", ops)
```

- **Every mark on its own line with its own numbers.** No function that makes
  a shape, no loop that stamps one, no `ellipse()`: a tool may not supply a
  form you did not choose after looking. A dict of measured points supplies no
  form and is the fix for an edge drawn twice — two objects that share an edge
  share the entry. **Your own points may serve two marks** — a flat and its
  ink, one edge of two faces: the rule is about where numbers come from, not
  how often they are used. Reference them from one named list, never paste a
  copy: two copies drift apart on the next edit and become one edge from two
  guesses. What stays forbidden is a program computing points, whatever
  carries them into the file.
- **Tag every ink stroke by the edge it states** (`tag="jaw.left+cowB"`,
  `+` joins several), so `--depth` can read the write order against the
  inventory and `--only`/`--hide` can show one object.
- **One stroke per member; a joint is a stroke boundary.** A smoothed stroke
  fits one curve through all its points, so a bent form written as a single
  `hip → knee → ankle` stroke comes back as an unbroken bow with no angle at
  the joint — and reads as the *unbent* form, however exactly the joint was
  measured. The points hold the bend and the render throws it away, silently,
  and no numeric gate reports it. Give each member its own stroke, or pass
  `smooth=False`.
- **The tracer's points are measurements, not marks.** You read positions off
  a contour and type the ones that carry the shape into `draw.py`; the region
  list is never iterated into strokes. Keep perimeter order — resequencing
  folds the walk into arrowheads. For an organic form that means the few points
  that carry it; for a simple manufactured form — a bulb, a frame, a strip of
  tape, a tube — most of the contour, and the drawing is then in its weight and
  its junctions. **Neither works on a re-entrant region** — a band with shapes
  punched through it, a boundary threading into its own interior: draw a plain
  polygon from measured extents. **A ring is not a disc**: a region with
  `holes` is a band, drawn as a stroke along its centre line or as a flat with
  what shows through the hole written after it. Where what shows through is a
  scene, one closed polygon (outer edge, seam, inner edge) renders a hairline
  of ground along its seam: put the seam where a nearer form covers it.
- **Chain rows to measure a group of repeated small forms, then write each
  form yourself. The measuring is a GATE, not advice.** Vents, fingers, teeth,
  slots, louvres, treads, droplets: wherever one object carries several of one
  small form, skipping it is a failed stage — it has been skipped on exactly
  those classes run after run, and a viewer then names the object something
  else: a helmet becomes a beetle, a glove a shoe. Scan each row for runs of the
  target value *inside the eroded silhouette*, chain the runs across rows, and
  print per form its end rows and its two edges every few rows. That counts the
  forms (a morphological opening merges two narrow ones and silently corrects
  your census downward), says where each tapers — because the chain ends, not
  because you chose a nice shape — and shows a structure running the wrong way,
  a groove narrowing where you drew it widening. Then **author** each form from
  it: end rows, widest row, and enough of both edges to carry every turn,
  typically twelve to twenty points for a slot. **The count is the tell**: five
  to eight points means the shape was chosen by eye, or read off a starved
  trace (re-trace the object's crop); chosen forms also come back identical. Emitting the chain
  itself, one point per row, is the generated mark above.
  Where a form curves back so one row holds two of its runs — a tadpole's tail,
  a bent streak — chain along its own long axis (scan columns) and still write
  one outline; a piece per chain abuts along a row and `--doubled` reports it as
  one edge stated twice. Where a form sits in front of a same-valued form, no
  value mask separates them: the ink between carries the edge, so read it off
  `--zoom` and say in the script where those points came from.
- **Never probe a region at its `centre`.** That field is a centroid, and a
  centroid is not a point inside the region: on any crescent, ring, bent or
  C-shaped form it lands in a *neighbour*, whose colour looks like proof that
  the region is an artefact: eleven of one crop's fourteen largest regions had
  a centroid outside themselves, all genuine. Probe `inside`, or compare the
  region's `median` with its palette entry. **A cull is a decision and needs
  the same measurement as a mark**; nothing downstream will say it was wrong.
- **A region-growing measurement needs a bound that is not a colour.** Seeding
  a silhouette on a palette name runs it into every other object carrying that
  flat — a garment seeded on its two colours swallowed a bicycle that shared
  one of them. The object's box is already written down in the inventory; pass
  it as the bound.
- **A traced contour measures a silhouette; it does not measure a slot.** The
  tracer stops at the colour transition, so what it returns for a vent, an
  eyelet, a gap between fingers or any other dark opening is that opening's
  *pale interior* — a short fat blob. What a viewer reads as a slot is the dark
  shape **including the ink that bounds it**, and the thin rib between two
  slots carries a dark line of its own. Draw the interiors and you get spots on
  a dome: a helmet becomes a beetle. **This is independent of how good the
  measurement is** — a group of vents built from rich traced contours at twenty
  points each came back *worse* than the same vents built from a starved trace,
  because a rich measurement of the wrong thing is still the wrong thing. For
  any dark opening, chain the dark inside the eroded silhouette, read where each
  rib between two openings runs off the same scan, and write both yourself.
- **A dark mechanism reads by its light gaps.** The inverse of the slot: a
  derailleur, a lever on its body, a hinge, a buckle is one connected dark
  shape, and what says it is an assembly is the light openings between its
  members and the ink joins where they meet. Fill a gap solid and it becomes a
  block with holes; leave a join open and one assembly becomes islands on the
  ground, a lever floating beside the hand that holds it. On `--zoom`, count
  both images' dark pieces and enclosed light gaps inside the part's box, and
  write each gap and each join as a mark of its own.
- **A region outline is not a silhouette, and a scan run is not a contour.**
  A flat is split by ink into several objects — a shoe and the straps on it,
  an ear and the spiral inside it — and the tracer and a row scan return the
  flat, not the object. Before inking any contour taken from either, `--zoom`
  that object against the subject and say which lines are its edge and which
  are inside it. No numeric check sees this; one look does. And the two put
  an edge in different places: a traced boundary is the ink's CENTRE line, a
  class mask or a scan run stops at its INNER edge. Ink belongs on the first;
  strokes placed on the second came out half a line inboard, and tubes read
  thin.
- **Straights are `smooth=False`**, and so is any closed quad (smoothed, four
  corners render as a lens) and every stroke of a faceted form — rock, crystal,
  folded paper: rendered smooth, a rock field became river stones and every
  gate passed. `closed=True` must not repeat its first
  point. A small closed form takes `tool="pen"`. A flat takes `tool="flat"`
  with `size`/`scale` pinned, or its outline renders 5px wider than you asked.
- **Draw a weight ladder first**, one *vertical* stroke per width, spaced
  apart, with the tool you will use, written with `write(..., swatch=True)`,
  and read it back with `--weights` on a row that crosses them. Each tool has
  its own ladder: `pen` is the hairline instrument and `brush` bottoms out near
  2px at 1:1. The named nibs are pitched for a ~430px subject: on a single
  object of another size call `gauge(subject_height)`; on a 4x scene they are
  unusable, so pin `size`/`scale` from the ladder by hand, once for the whole
  document. `weight=` is pressure, not width. A band wider than the heaviest
  rung — a strap, a tyre — is a flat with both sides as points, closed; so is a
  small form dark all through, a droplet whose ink is wider than its interior,
  with the interior written over it. Measure each mark's width on the subject
  before asking for it, and try the next rung before recording a limit.
- **Measure the ground.** Everything on it is judged by its contrast with it.
- **Never retype a coordinate from memory.** Re-measure it.
- **A palette-exact filter measures the wrong thing on a shaded subject.**
  A limb is its lit value *plus a shade band*, so a skin-only run stops at the
  shade and reports the limb short, or missing; every measure taken this way
  made the subject too narrow and the drawing falsely too wide. Measure a form
  by its value **family**, or between the ink lines either side. The same trap
  counts a dark *fill* as a line. Look at what a run-based measure classified.

## Judges

**Describer** — `describe.sh image.png [RUN]`, saved beside the image as
`image.describe[.RUN].md`; a reply without five numbered answers (a rate limit,
the CLI's own error) is refused, exit 1, nothing written. Blind,
factual, and it excuses: ask it *what*, never *whether*. Where its answer to 3
or 4 differs from the subject's, the picture's event is wrong, and that is the
first fault, whatever the numbers say. It is noisy run to run, so at a gate run
it twice and keep only what both runs say; a clause one run states and the
other drops is not a verdict either way. **Run it twice on the subject too**:
a clause the subject's own two runs do not share is not an acceptance clause
and must not be gated on — otherwise a stage is held against a target that
does not survive its own noise. Run it on part crops as well: a face can
pass at 1:1 and carry the opposite expression at 4x.

**Naming a part** — crop a part's box out of the subject and out of the
drawing (a plain PIL crop), `describe.sh` each, and read the two paragraphs
side by side. **This is the only instrument that asks what a thing IS.** Every
other one measures presence, placement, value or design, and an object passes
all of them while reading as a different object: present, in its box, at the
right weight, inside a design that matches — and a viewer calls it a plate of
food.

**Ask for a paragraph, never a name**: shown a crude mask a viewer says
"face", matching "a laughing woman's face" on its head word; a paragraph must
commit to kind, proportions, parts and angle, so a loss shows.

**It is a detector, never a meter.** A wrong name — "animal paw", "a plate of
food" — is a true diagnosis. A *right* name proves nothing: scored against
**itself** a subject does not come back at 1.00, a visibly wrong drawing scores
like a faithful copy, and two blind viewers disagree by more than any such
score resolves. Never build a score, a bar or a ranking out of it.

Even the name only reaches recognition, never likeness — a face can be named
correctly and still be the wrong shape for the person in the subject. What
answers likeness is the shape sentence, checked by two instruments on the
focus: an **outline scan** (`--scan` on the side the silhouette faces), the only
thing that sees a wrong turn between two measured landmarks, and the **two
inks** (`--overlay --box`), because the outline is not all of a likeness. A face
matched its subject's edge within 10px row by row and still read wrong: the
nose's ridge line ran diagonally from brow to nostril in the subject, a wide
wedge, and near-vertically down the far edge in the drawing. For every blue
line inside the form, say which red line is meant to be it and how far it runs
off, then measure it with `--scan`. No threshold: which line answers which is
a reading, and any distance between two inks falls as ink is added.
`reference/measuring.md` has the detail.

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
| `--masses` | the wrong shape: line closed away (dark runs thinner than the subject's line), both cut on the subject's value levels, `--colours` 3 by default. **A design gate, not a proportion gate** — a head half again too wide is still a pale blob above a dark torso at thumbnail size, and passes |
| `--scan x,y,w,h --side S` (needs `--ref`) | per row, subject beside drawing: the first non-ground pixel from that side, and the dark runs inward from it. **The instrument for a coordinate and for a proportion**; `<<` marks an edge off by over 2% of the box, `runs a|b` a row whose line count differs — a thick line drawn as two, an interior line drawn somewhere else |
| `--overlay` | the drawing blended over the subject; with `--box x,y,w,h`, the two inks over that box: the subject's blue, the drawing's red, black where they coincide. The only view of **interior lines** (see below). No number, on purpose |
| `--parts parts.json` (needs `--ref`) | a part that is absent, or drifted out of its box; each sentence printed over its crop. It answers *is it there*, never *is it recognisable* — only a describer on the assembled panel answers that |
| `--census parts.json` (needs `--ref`) | a group of repeated forms culled, merged or added, where the subject itself counts to the census; exit 1 FAIL, exit 2 UNCHECKED rows |
| `--ranking parts.json` (needs `--ref`) | a part shouting above its `tier` — named when it outranks the whole focus tier; two forms welded into one value. Zero-sum: the only way to lift a part is to put another down |
| `--doubled ops.json` | one edge stated twice **on the page**: write order, `erase` and `back` are replayed, and an edge a later flat buries is not listed. Two bands meant to run together are listed too, so look before you merge |
| `--depth ops.json parts.json` | an occlusion the inventory decided on that the write order does not deliver — the far form's ink after the near form's fill, drawn across it. **UNRESOLVED** is not a pass: tags and inventory are not one vocabulary. **UNLISTED** is a worklist: one part's ink shown across another's flat where no row decides which is in front |
| `--ladder ops.json` | a stage that does not exist, and a mark the script did not write: called from another file, stamped by a loop or an import, points loaded or computed. It does not check that each ink has a contour under it. Pasted generated literals pass it |
| `--faces ops.json` | a flat simpler than the traced region it overlaps: a shade drawn as a quad on a form of twenty-five corners reads as a patch stuck on. Pass the object's own trace as `--regions`, and on an upscaled or generated subject `--grain` of three times the upscale factor, or its serration reads as corners (150 false rows on one panel, 4 with it). A deliberately straight form cut by intruding objects still fails it |
| `--unfilled --paper C` (needs `--ref`) | bare paper where the subject carries the object — a flat short of its own ink, most often along an open edge `--registration` cannot see. The object is read off the subject's ground (`palette.json`), bareness off `--paper`: render a check copy with `background` repointed to a colour nothing uses, and pass that |
| `--registration` | colour and line disagreeing. Not on a full-bleed panel: every band that runs off the frame reports as a spill |
| `--zoom x,y,w,h` | whether the marks are any good, at 4x, ticked in panel coordinates. **The primary gate on any object**: three versions of one object passed every numeric gate and ranged from a beetle to a thing a blind viewer named at once; only the magnified pair told them apart. Ticks orient; they are not a coordinate |
| a blind viewer on a part's crop | what the part **is**. The only gate that fails a blob — a detector, not a meter |
| `--weights rows` | the line hierarchy against the subject's, each run as `width@x` |

Every number is a worklist, never a score. The cheap way to move a
mark-counting number is more marks, and a whole-picture pixel difference goes
*up* on a round that made the drawing better. The target is the shape sentence
and the acceptance list; a judge only says whether they are now true.

## The correction cycle

Corrections are where a drawing is won or abandoned, so the loop is fixed
rather than left to judgement.

**Iterate one part, never the panel.** A panel costs an order of magnitude more
per round and tells you less: its faults are per-part anyway, and a round spent
re-working everything is a round not spent drawing. Take one part, work it in
its own ladder, and leave it when it passes.

**There is no score, so the loop is driven by the acceptance list.** Order the
parts by the clauses they break, worst first: a part a blind viewer **misnames**
outranks one whose shape sentence is merely inexact, which outranks a part that
is only absent.

```
per part: --zoom beside the subject, and a blind viewer on its crop
  the crop is misnamed        -> the worst fault there is. Its stage failed;
                                 go back to that stage, not to a correction mark
  named, sentence untrue      -> measure the clause on subject AND drawing
                              -> name the stage it belongs to, fix it there
  named, every sentence true  -> pass; take the next part
  the same item returns after
  a round that addressed it   -> plateau: stop, and report what it plateaued on
  budget spent                -> stop
```

**WRONG before MISSING**: a contradiction is a fault, an omission is often a
choice. An item no measurement reproduces gets no mark and goes to
`refuted.md`. A fault wrong in shape or along a whole length goes back to its
stage; only a local, bounded fault earns a `correct` mark.

**Log every cycle in `notes.md` beside the drawing** — cycle, what was changed,
what the viewer called each crop, which clauses went true. A campaign has to
leave a trail, because the one thing a plateau looks like from inside is
progress, and with no curve to plot the trail is all there is.

**A person is the gate, and a person grades against the wrong thing.** Someone
reading each render compares it to the *previous* render, and after a few
rounds signs off on work that has improved and is still bad. There is no number
that can be trusted to replace them, so fix the procedure instead: every
judgement is made **beside the subject, at the same scale, in one image**, and
the question is never "is this better" but "is this clause true". Look at the
render itself — a viewer's words or a gate's number reported as the verdict is
not a look. And **a look finds, a number moves a mark**: proportion judged by
eye from a side-by-side was wrong in both directions on one panel (a head that
looked 10% large was 3% wide; a chin that looked 70px low was 6px off), a
person reading the same thumbnails was half right on every item, and a scan or
an overlay settled each case. So an item raised by eye — yours, a critic's or
a person's — is measured on subject and drawing before any mark, exactly like
a critic's.

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
  fault: `--parts` answers the first, a blind viewer on its crop the second.
- **Stage 10 runs before anyone sees the picture**; a correction that changes
  nothing when switched off comes out, and zero `correct` marks because every
  fault went back to its stage is a pass.
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
