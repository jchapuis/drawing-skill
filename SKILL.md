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

On a panel-sized subject three things bite immediately. **Trace each object's
own crop, never the whole panel**: `trace.py` on a 17-megapixel subject does
not finish, and the obvious escape — tracing the delivered-size image and
projecting the coordinates up with `--space` — is a trap that costs more than
it saves. See below. **Set `Image.MAX_IMAGE_PIXELS=None`** before opening a
comparison: `--masses` writes an image past PIL's decompression-bomb limit and
the gate dies on its own output. And **macOS has no `timeout`** — it is
`gtimeout`, or `perl -e 'alarm N; exec @ARGV' --`.

### Where your measurements come from is an architectural decision

Drawing in one document does not mean **measuring** in one pass, and conflating
the two is the most expensive mistake available here. A panel-wide trace
resolves every object at *panel* scale: a small object comes back with a
handful of points per form, and no amount of care at the drawing stage recovers
what was never measured. Tracing the delivered-size image and multiplying the
coordinates is worse still — it quantises every region boundary to the
projection factor, so a 4x working space gets boundaries on a 4px lattice.

**Crop each object out of the working-resolution subject, trace that, and
offset the coordinates into panel space.** It is not a compromise with the
one-document rule: you still draw every mark in panel coordinates, in one
`draw.py`, with no second coordinate space for marks and no placement step.
Only the *measuring* is per object. Measured on one object: a panel-wide 1:1
trace gave it 77 regions and 872 contour points, while its own crop at working
resolution gave 156 regions and 3878 points — **4.4× the detail, in 1.5
seconds.** The same object drawn from the rich trace and from the starved one
is the difference between a helmet a viewer names and a striped loaf.

The symptom to watch for, because it is silent: forms arriving with three to
nine points each where the object plainly has more structure than that.

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
| 5 | **Masses** | `stage="fill"`, `tool="flat"`: one region per surface, **drawn past where the ink will go** — `trap=<px>` on a BODY flat grows it outward by that much, so the contour covers its edge. **Trap an edge that is a silhouette; never trap an edge that is a measurement.** A flat that is a mark in its own right — a vent, an eye, a cast shadow, a shade — is ruined by it, and trapping every closed flat swells the interior shapes until they eat the form. A **band** is the silent case: a strip, a rim inside a tyre, a hem, a strap — its two long edges face opposite ways, so trapping moves both and **the band gains twice the trap in width**, on every band at once, with every gate still passing. Where two bands run concentric or parallel it is their *ratio* that makes the pair read, and trapping converges it. Trap a band's ends, never its length A fill outline taken from the tracer sits at the colour transition, which is INSIDE the ink, so used verbatim it falls short by half a line width and the ground shows through wherever the contour bulges. Written in depth order, each form's fill directly before that form's ink, so a nearer form's flat covers the ink of the one behind it. Never `back("fill")`: it sends every flat behind every line and the object can then not occlude itself | `check.py drawing.png --ref subject.png --masses` — the two read as the same shape, said in words |
| 6 | **Contour** | `stage="contour"`: the real edge, curved where the subject curves, from `contour` in `regions.json` | `--overlay` again |
| 7–8 | **Ink** | `stage="ink"`, one stroke per edge, each width measured on the subject, every stroke tagged by the edge it states; `fade`/`erase` blockin and contour | `check.py drawing.png --doubled ops.json` and `--ladder ops.json` pass |
| 9 | **Fill** | flats refined; blacks massed as one value before anything is graded | `--hide ink` still separates figure from ground |
| 10 | **Correct** | `stage="correct"` marks aimed by the judges, N rounds fixed at stage 0; `refuted.md` for every item that did not survive its measurement | `describe.sh drawing.png` matches the acceptance list clause by clause; `--registration`, `--parts`, `--ranking` |

**Stages 5 to 8 interleave per form; they are not four passes over the whole
drawing.** The table numbers them because each one commits less than the next,
not because you finish one everywhere before starting the next. As soon as two
forms overlap, write them depth-major — the far form's fill, the far form's
ink, then the near form's fill *over that ink*, then the near form's ink. Group
them stage-major, every fill and then every ink, and the far form's outline is
laid down after the near form's flat and draws straight across it: a stray edge
through the middle of the nearer object, which reads as a crease or a seam that
is not there. **Occlusion is the order you write in, and nothing else provides
it** — and `--depth ops.json parts.json` is the only gate on it, which works
only if your stroke tags and your inventory names are the same vocabulary. Tag
by the inventory's names, never a private shorthand, or the gate resolves
nothing and reports a clean bill over an unchecked drawing. Three things it
needs that are easy to get wrong: the interface **key** must itself be written
`far/near` **in the tag vocabulary** (`wheel.front.tyre/ground.landing`, not
`tyre.front/ground`); `in_front` belongs only on interface entries, never on a
plain object; and a part carrying **no ink at all** makes its rows
unresolvable, which is why UNRESOLVED has to be read as loudly as FAIL.
Matching is by prefix, so a sub-form's ink counts as its parent's — which also
means a parent's rows do not clear until every one of its sub-forms is ordered.
A **hole** — a vent, a window, an eyelet — is the same rule seen from the
other side: it is not a nearer form but an absence in this one, so its flat is
written *after* the ink of the surface it pierces, or that surface's own
contour runs across the opening.

Going back up the ladder invalidates everything above it: re-run every stage
after the one you changed. The script re-renders in one call, so that is the
cheap answer.

`build.sh` draws `gesture.png` and `blockin.png` in stock stage colours on a
stock ground, with every `erase`/`fade` left out so they survive cleanup; they
are for the event and the placement, and the ground is judged on
`contour.png` and `drawing.png`, which use the palette.

## The scene ladder

The object ladder, wrapped. Stages S0–S2 draw no object: they design the
picture. Then every object is drawn **into that same document, in the panel's
own coordinates**, at a working resolution high enough to draw its smallest
feature — 4x the delivered size is a reasonable default, and the whole panel at
4x renders in seconds. There is one `draw.py` and one `ops.json`. Nothing is
cropped out, nothing is placed back, and there is no second coordinate space
anywhere.

**Objects drawn in their own crop and composited back came out as blobs; the
same objects drawn whole came out well.** What a crop really buys is that it
forces you to look at the object magnified, and that service is worth having —
so take it as a gate instead of as an architecture: **`--zoom` every object
before you call it done, always.** An object built from numbers and never
zoomed comes back as fat lozenges and scratches and looks passable at panel
size. Everything else a crop costs — a second coordinate space, nibs divided by
a crop scale, scaffolding masses to remove, interfaces deferred to an assembly
stage, a palette and a weight ladder per part — goes away, and the junctions
become write-order rather than a plan.

| # | Stage | You produce | Gate |
|---|---|---|---|
| S0 | **Read as a tone field** | everything stage 0 produces, plus in `reading.md`: **one** centre of interest; the tone plan (a dominant value, two to four masses); the **welded shapes** — five to twelve, each edge marked sharp or lost, no object with a closed contour; every object as either a **part** or **welded** — a part is an *object* (the rider, the bicycle, the lamp), never a feature of one; **an object the describer names in answers 3–4 is a part**, because the acceptance list will ask for it, unless it has no silhouette of its own against its surround, in which case write it down now as a clause the drawing will not earn; for each part its crop box (small enough that the part fills a render) and its scale (large enough to draw its smallest feature), its nested parts (a face inside a figure at a higher scale again), and its weight pitch relative to the centre of interest; the **interfaces table** with an `in front` column per crossing; the census with its zeroes | a thumbnail of the tone plan reads as a design with one dominant value and the strongest contrast at the focus; every interface has a depth decision; the part list and the acceptance list agree |
| S1 | **Armature** | `stage="gesture"`: eye level, ground plane, the main lines, the line of action, the major masses as loops. **The object ladder's "3–10 strokes" is a single object's budget and does not apply here** — a scene needs one per mass plus the ground and eye lines, which runs to fifteen or twenty. Too few and the describer reads one object's parts as another's: a bicycle's bar becomes the figure's outstretched arms | `describe.sh gesture.png`: the event and the big shape read. **A pose carried by value rather than by silhouette may not be statable here** — a seated figure with fully foreshortened thighs has a standing figure's outline — and then the honest move is to record that the event is gated at S2 instead, with the describer runs that show it, rather than to keep redrawing an armature that cannot carry it |
| S2 | **Masses** | `stage="blockin"` straights for the welded shapes, then their flats `stage="fill"` — the middle tone over the whole, then lights, then darks, honouring sharp/lost. **Every object's mass goes in here, part or welded**: the part/welded split decides whether an object gets *marks*, never whether its *value* exists. A part left out is a hole in the tone plan, and when a whole value family lives inside parts — the darks usually do — the gate cannot pass at all until they are in. A flat is not ink, so this costs nothing at the gate. No object's *marks* yet | `--masses` against the subject at thumbnail size; **no object has an ink contour** (`--ladder` shows ink 0) |
| S3 | **Every object, in place** | run stages 4 to 9 of the object ladder on each object, in the one `draw.py`, in panel coordinates, working from the furthest object forward. Its brief from S0: which of its edges are lost, what is in front of it, its weight pitch. **Refine the object's S2 mass into its stage-5 fill** — they are the same flat, so there is no stand-in to remove and no fringe. A simple manufactured form keeps the tracer's contour nearly whole and is cheap; a figure is built on the figure ladder with its three masses and every joint, and is not | **`--zoom` on the object, beside the subject, before you leave it** — this is the gate the crop used to enforce and it is not optional. Then its own ladder gates, `--faces` and `--unfilled` |
| S4 | **Junctions** | nothing to assemble: every object was drawn where it belongs, with its neighbours already on the page, so the interfaces table was satisfied as you went rather than afterwards. Walk it once and confirm each row — the accent where forms touch, the joint line that breaks at the leg in front of it, the lost edge still lost | `--doubled`; `--depth ops.json parts.json` clean, with no UNRESOLVED row; every row of the interfaces table has a recorded decision and a look |
| S5 | **Emphasis** | nothing is drawn at panel scale here. Emphasis was decided at S0 as each part's weight pitch and edge count, and the far parts were drawn lighter and with fewer edges *in their own crops*. Walk the placed panel and confirm the gradient: weight and detail decay from the centre of interest and with depth; welded objects have no marks | no part beyond the focus carries the focus's weight; a describer names every part |
| S6 | **Interfaces** | the enumerated pass over the interfaces table, in the assembled panel and nowhere else: the accent where forms touch, tangents broken by overlap or separation, lost edges confirmed lost, rails and wires only where both values are measured either side | every row of the table has a recorded decision and a look |
| S7 | **Blacks, texture, vignette** | one pass spotting the black pattern across objects; texture fields as one indicated pattern; the whole drawing's silhouette against the paper | `--ranking parts.json`: the focus leads, nothing shouts above its tier |
| S8 | **Correct from a distance** | stage 10, on the panel, with the describer run twice. A blind viewer on each part's crop ranks the round: the **misnamed** parts get the budget first, then the parts whose shape sentences are untrue | the acceptance list; `--ranking` still shows one focus; no part misnamed. An item that returns after a round that addressed it is the stopping rule |

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
   with a box read off `regions.json`. **An entry descends to the sub-forms
   that make the object what it is**, each with its own box and its own
   sentence: a wheel is a tyre, a rim, its spokes and a hub, not "a wheel"; a
   glove is its fingers, its thumb and its cuff. One sentence for a whole
   object buys one silhouette, and a silhouette is what a viewer calls a
   different object — the census counts these sub-forms already, and this is
   where they become marks. Stop descending where the next level down would
   not survive at the scale you will draw it.
   **Two instances of one object class get the same sub-form list.** Where the
   subject shows the same kind of thing twice — two wheels, two hands, two
   shoes — the second is read with less attention than the first and comes back
   with fewer entries, and the missing sub-form is then missing from every gate
   that works off the inventory. The asymmetry is the tell: if one entry
   descends and its twin does not, the twin was under-read, not simpler. Line
   them up and reconcile before leaving stage 0 — or write down, as a clause,
   what the second one genuinely lacks that the first has. Name the junctions as entries of
   their own — hand/bar, foot/pedal, hip/saddle, tyre/ground, and every joint —
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
- **Chain rows to find a form, rather than choosing its shape. This is a
  GATE on any group of repeated small forms, not advice.** Vents, fingers,
  teeth, slots, louvres, treads: wherever one object carries several of the
  same small form, chaining is required and skipping it is a failed stage.
  It has been stated as advice and skipped on exactly the object classes it
  names by example, in run after run, because nothing ever asked where a
  form's points came from. **The count is the tell you can read off your own
  script**: a form whose outline was chosen by eye arrives with five to eight
  points; the same form chained arrives with sixteen to eighteen, because the
  chain emits one point per row per side. Before inking any such group, look at
  the point counts in `draw.py`. If they are single-digit, a viewer will name
  the object something else — a helmet becomes a beetle, a glove becomes a
  shoe. **A single-digit count has two causes and they need different fixes:**
  you chose the shape by eye, or the trace you took it from was starved and
  never offered more. Check the region's own point count before blaming
  yourself; if the trace is thin, re-trace that object's crop at working
  resolution rather than chaining against a measurement that is not there.
  The other tell is that chosen forms come back near-identical to each other
  and chained ones do not.
  For any flat
  subject: scan each row for the runs of the target value *inside the eroded
  silhouette*, chain those runs across rows into forms, and emit each form as
  its **left chain going down and its right chain coming back up**. Both ends
  taper to a point because the chain ends, not because you chose a nice shape,
  and choosing the shape is exactly how a slot becomes a lozenge and a finger
  becomes a lobe. It also counts the forms for you — a morphological opening
  merges two narrow ones into a fat one and silently corrects your census
  downward — and it is the only thing that shows a structure running the wrong
  way, a groove that narrows where you drew it widening. Use it before you
  decide what a group of marks is; looking at the whole object does not reveal
  it.
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
- **On a scene, `gauge` does not apply and the named nibs are unusable.** At a
  4x working resolution a named nib arrives at a width that has nothing to do
  with the subject's line. Draw the ladder with the tool you will use, read it
  back with `--weights`, and pin `size`/`scale` by hand — once, for the whole
  document, since there is only one.
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
- **A palette-exact filter measures the wrong thing on a shaded subject.**
  Scanning for one flat's colour looks precise and is a trap: a subject draws
  a limb as its lit value *plus a shade band along one edge*, so a skin-only
  run stops at the shade and reports the limb short — or, where the whole limb
  sits inside its shade, reports it missing. Every width, extent or proportion
  measured this way came back wrong in the same direction: the subject too
  narrow, and therefore the drawing falsely too wide. Measure a form with its
  value **family** — the lit value and its shade together — or measure the
  silhouette between the ink lines either side. The same trap counts a dark
  *fill* as a line when measuring line weight. Before trusting any run-based
  measurement, look at what it classified.

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

**Naming a part** — crop a part's box out of the subject and out of the
drawing (a plain PIL crop), `describe.sh` each, and read the two paragraphs
side by side. **This is the only instrument that asks what a thing IS.** Every
other one measures presence, placement, value or design, and an object passes
all of them while reading as a different object: present, in its box, at the
right weight, inside a design that matches — and a viewer calls it a plate of
food.

**Ask for a paragraph, never a name.** Shown a crude mask a viewer says "face",
which matches the subject's "a laughing woman's face" on its head word and
tells you nothing. A paragraph has to commit to the kind of thing, its
proportions, its parts and its angle, so anything lost shows up as a
difference you can point at.

**It is a detector, never a meter.** A wrong name — "animal paw", "a plate of
food" — is a true and useful diagnosis, and the losing concept is the
diagnosis. A *right* name proves nothing at all, and the confidence attached to
it measures nothing: scoring a subject against **itself** does not come back at
1.00, and a visibly wrong drawing scores the same as a faithful copy. The
spread between two blind viewers on one image is as large as the difference any
such score would need to resolve, so a number built on it cannot rank parts,
cannot detect a plateau, and cannot decide a pass. Use the name; never build a
score, a bar or a ranking out of it, and do not rebuild the scorer.

Even the name only reaches recognition, never likeness — a face can be named
correctly and still be the wrong shape for the person in the subject. What
answers likeness is the shape sentence, read beside the subject at the same
scale.

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
| `--masses` | the wrong shape, with line closed away. **A design gate, not a proportion gate** — it posterises to two values and asks whether the panel reads as the same design, so at thumbnail size a head half again too wide is still a pale blob above a dark torso in the right place and it passes. Nothing in the kit checks a part's proportion automatically; what catches it is a bounding box and a per-row width scan against the subject |
| `--parts parts.json` (needs `--ref`) | a part that is absent, or drifted out of its box; each sentence printed over its crop. It answers *is it there*, never *is it recognisable*, and for a small part those are different questions — an unrecognisable part passes this, `--ranking` and its own crop's describer together. Only a describer on the assembled panel answers the second |
| `--ranking parts.json` (needs `--ref`) | a part shouting above its tier; two forms welded into one value. Zero-sum: the only way to lift a part is to put another down |
| `--doubled ops.json` | one edge stated twice from two guesses. A worklist: two bands meant to run together (a rim inside a tyre) are listed too, so look before you merge |
| `--depth ops.json parts.json` | an occlusion the inventory decided on that the write order does not deliver: the far form's ink written after the near form's fill, which draws that edge straight across the nearer object. The only gate on depth order, and it reads the script, since the pixels are all correct. An **UNRESOLVED** row is not a pass — it means the stroke tags and the inventory names are not one vocabulary and the pair went unchecked |
| `--ladder ops.json` | the stage that does not exist |
| `--faces ops.json` | a flat simpler than the form it lies on. A shade drawn as a quad on a form the tracer gives twenty-five points reads as a patch stuck to the object, not as its surface turning away. It compares against the traced region, so a form that is *deliberately* straight — a ground band, a step riser — fails it whenever objects intrude into that region and drive its point count up; read those as false and move on. It counts corners, never where they fall: a flat whose corners bunch at two ends passes with a long straight boundary running where the form curves, and `--masses` is what sees that |
| `--unfilled` (needs `--ref`) | bare ground where the subject carries the object — a flat that stopped short of its own ink. **Pass a `--paper` the drawing never paints with**: if the ground is a colour you also fill with, every such flat reads as bare and the gate is pure noise. `--registration` sees only paper the line walls in completely; a flat short along an OPEN edge leaves a bay the flood reaches, and that is the commoner fault |
| `--registration` | colour and line disagreeing. Not on a full-bleed panel: every band that runs off the frame reports as a spill |
| `--zoom x,y,w,h` | whether the marks are any good, at 4x |
| a blind viewer on a part's crop | what the part **is**. The only gate that fails a blob — and a detector, not a meter: act on a wrong name, read nothing into a right one |
| `--weights rows` | the line hierarchy against the subject's |
| `--overlay` | exact drift against the subject |

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
not a look.

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
  fault. Go back and put it in. `--parts` answers the first half and
  a blind viewer on its crop the second; a part can sit exactly in its box, at exactly its
  weight, and be a different object.
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
