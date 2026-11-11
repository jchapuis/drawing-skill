# Marks and coordinates

How to read a coordinate off the subject and how to write a mark in `draw.py`:
the pen's API, smoothing, weights, and the measurements that most often go
wrong.

## Contents

- Reading coordinates
- Marks
- Overlap order

## Reading coordinates

Every point in `draw.py` is read off the subject, with `look.py`. It measures
and writes no mark. Coordinates are in the working space: `--scale 4` reads
`subject_1x.png` in the 4x space, and a render is read at the first image's
size, so `drawing.png` from `--scale 0.5` lines up with `subject.png`.

```bash
python3 look.py grid subject.png drawing.png --box 400,1500,600,500 --out look.png
python3 look.py probe subject.png drawing.png --at 640,1850 1000,600
python3 look.py edge subject.png drawing.png --ray 700,100,0,1 --ray 640,1850,1,0
```

- `grid` crops the box from each image, magnifies it to about 1000px and rules
  it every `--step` (about ten lines by default). Each line is labelled in
  picture coordinates and every fifth one is stronger. **Use it to place
  points.** On a photograph with hundreds of points it is often the only
  practical way.
- `probe` prints, per point and per image, the median colour of a small patch,
  its hue, saturation, value and grey, and the nearest `palette.json` name.
- `edge` walks a ray from `x,y` along `dx,dy` and prints where the colour first
  changes sharply (`--contrast`, Lab units), with the colour and palette name
  on either side, then the next few edges. From a point inside a form, four
  rays give its extents.

**Use the grid to place points and a probe or an edge to confirm them.** A
position read by eye off a grid or a zoom's tick marks is only a placement, and
you never judge a fault by one (SKILL.md § The correction cycle). Before you move a mark
for a fault, or trust a point your shape depends on (a corner, a contact, an
eye), check it with `probe`, `edge` or `check.py --scan`. For an outline row by
row, use `--scan`; for a silhouette, `segment.py --silhouette`.

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
- **Write every mark on its own line with its own numbers.** Use no function
  that makes a shape, no loop that stamps one, no `ellipse()`: a tool must not
  supply a form you did not choose after looking. A dict of measured points
  supplies no form, and it fixes an edge drawn twice: two objects that share
  an edge share the entry. Your own points may serve two
  marks (a flat and its ink, or one edge of two faces); the rule is about where
  the numbers come from, not how often they are used. Reference them from one
  named list and never paste a copy, because two copies drift apart on the next
  edit and become one edge drawn from two guesses. A slice of a named list
  (`GLOVE[3:] + GLOVE[:2]`, to ink one edge of a closed form open) counts as a
  reference, not a computation. What stays forbidden is a program computing
  points, however they reach the file.
- **Tag every ink stroke with the edge it draws** (`tag="jaw.left+neck"`; `+`
  joins several), so `--depth` can check the write order against the inventory
  and `--only` and `--hide` can show one object. Ink is per edge. A mass's
  closed outline inked as is draws every shared edge twice (one band's outline
  ran 298px along its neighbour's), so where a neighbour already draws an edge,
  ink the mass with open strokes.
- **One stroke per member; a joint ends a stroke.** A smoothed stroke fits one
  curve through all its points. So a bent form written as a single
  `hip → knee → ankle` stroke comes back as an unbroken bow with no angle at the
  joint, and reads as unbent however exactly you measured the joint. The points
  hold the bend, the render loses it, and no numeric gate reports it. Give each
  member its own stroke, or pass `smooth=False`.
- **A chain, belt, rope, cable, hose or wire is one continuous path.** Write it
  as consecutive strokes that share their end points by name, each meeting the
  wheel or anchor it wraps at the tangent point, with no gap. Draw its texture
  (a beaded or linked line) when the subject shows it, and count and write the
  teeth of a gear. `--joins` lists a run that stops short. See
  `reference/line.md` § Continuous paths.
- **The tracer's points are measurements, not marks.** You read positions off a
  contour and type the ones that carry the shape into `draw.py`. Never iterate
  the region list into strokes. Keep the points in perimeter order: reordering
  folds the outline into arrowheads. A point added to a traced outline (a
  continuation under a nearer form) goes in at its place round the outline. For
  example, one typed at the head of the list made the outline double back, and
  the face rendered with ground showing across it. `--stages` lists every such
  HOLE.

  How many points to type depends on the form. For an organic form, type the few
  that carry it. For a simple manufactured form (a bulb, a frame, a strip of
  tape), type most of the contour; the drawing's quality then lies in its weight
  and its junctions. Straight lines are the exception: a tube's edge read every
  75px wanders ±5px, and typed through every reading it inks wavy. Measure many
  points, type its ends and any real bend, and use `smooth=False`.

  Neither approach works on a re-entrant region, such as a band with shapes
  punched through it or a boundary threading into its own interior. Draw a plain
  polygon from measured extents instead.

  A ring is not a disc. A region with `holes` is a band: draw it as a stroke
  along its centre line, or as a flat with what shows through the hole written
  after it. Where a scene shows through, one closed polygon (outer edge, seam,
  inner edge) renders a hairline of ground along its seam. Put the seam where a
  nearer form covers it, and write it `smooth=False`; smoothed, the path through
  the seam's doubled-back points bulges past the ink. A flat pierced by several
  openings (a chainring's cut-outs) is the same polygon, with a slit from a
  covered point out to each opening and round it the other way.
- **To draw a group of repeated small forms, measure it by chaining row scans,
  then write each form yourself. This measuring is a gate: skipping it fails the
  stage.** It applies to vents, fingers, teeth, slots, louvres, treads and
  droplets, wherever one object carries several of one small form. These are the
  forms most often skipped, and a viewer then names the object as something
  else, such as a helmet read as a beetle or a glove as a shoe.

  Scan each row for runs of the target value inside the eroded silhouette
  (`check.py --scan BOX --value NAMES`), chain the runs across rows, and print,
  per form, its end rows and its two edges every few rows. This counts the forms
  (a morphological opening merges two narrow ones and silently lowers your
  count). It shows where each form tapers, because the chain ends there. It also shows a structure running the wrong
  way, such as a groove narrowing where you drew it widening. Then write each
  form from the scan: end rows, widest row, and enough of both edges to carry
  every turn, typically twelve to twenty points for a slot.

  The point count is a check. Five to eight points means you chose
  the shape by eye, or read it off a sparse trace (re-trace the object's crop).
  Forms chosen by eye also come back identical. Emitting the chain itself, one
  point per row, is a generated mark, which the rule above forbids.

  Where a form curves back so that one row holds two of its runs (a tadpole's
  tail, a bent streak), chain along its own long axis (scan columns) and still
  write one outline. Writing a piece per chain makes the pieces abut along a
  row, and `--doubled` reports that as one edge drawn twice. Where a form sits
  in front of a form of the same value, no value mask separates them. The ink
  between them carries the edge, so read it off `--zoom` and note in the script
  where those points came from.
- **Never probe a region at its `centre`.** That field is a centroid, which is
  not necessarily inside the region. On a crescent, ring, bent or C-shaped form
  it lands in a neighbour, whose colour then seems to prove that the region is
  an artefact. (In one crop, 11 of the 14 largest regions had a centroid outside
  themselves, and all were genuine.) Probe `inside`, or compare the region's
  `median` with its palette entry. Culling a region needs the same measurement
  as a mark, because nothing later will tell you it was wrong.

- **A region-growing measurement needs a bound that is not a colour.** Seeding a
  silhouette on a palette name runs it into every other object with that flat.
  For example, a garment seeded on its two colours swallowed a nearby object
  that shared one of them. The object's box is already in the inventory; pass it
  as the bound. `segment.py --silhouette` will not run without one.
- **A traced contour measures a silhouette, never a slot.** The tracer stops at
  the colour transition, so for a vent, an eyelet, a gap between fingers or any
  other dark opening it returns the opening's pale interior, a short fat blob.
  What a viewer reads as a slot is the dark shape including the ink that bounds
  it, and the thin rib between two slots has a dark line of its own. Draw the
  interiors and you get spots on a dome: a helmet becomes a beetle. A more
  detailed trace does not fix this. For example, vents built from detailed
  traced contours at twenty points each came out worse than the same vents built
  from a sparse trace, because they measured the wrong thing more precisely. For
  any dark opening, chain the dark inside the eroded silhouette, read where each
  rib between two openings runs off the same scan, and write both yourself.
- **A dark mechanism reads by its light gaps**, the inverse of the slot. A
  derailleur, a lever on its body, a hinge or a buckle is one connected dark
  shape, and the light openings between its members and the ink joins where
  they meet are what show it is an assembly. Fill a gap solid and it becomes a
  block with holes. Leave a join open and the assembly breaks into islands on
  the ground, such as a lever floating beside the hand that holds it. On
  `--zoom`, count the dark pieces and enclosed light gaps inside the part's box
  in both images, and write each gap and each join as a mark of its own.
- **A region outline is not a silhouette, and a scan run is not a contour.** Ink
  splits a flat into several objects (a shoe and the straps on it, an ear and
  the spiral inside it), and the tracer and a row scan return the flat, not the
  object. The ink class merges forms the same way: a nostril hook touching a
  moustache came back as a hump on the moustache's outline. Where `--line` is
  below the heaviest ink, those lines come back as rings named after the nearest
  dark flat (a garment's name round every silhouette); read them as ink. Before
  inking any contour taken from either source, `--zoom` that object against the
  subject and decide which lines are its edge and which are inside it. No
  numeric check catches this, so you have to look.

  The two sources also put an edge in different places. A traced boundary is the
  ink's centre line, while a class mask or a scan run stops at the ink's inner
  edge. That holds only for a line narrower than `--line`, which the tracer
  assigns to its neighbours. A heavier line stays a black flat of its own, and
  the neighbour's boundary is then its inner edge too (in one measured case
  about 24px inside the centre, on a chin). The silhouette lines are the heavy
  ones, so place those from a scan across the ink.

  An open line inside a form (a crease, a fold, a ridge) is narrower than
  `--line` and is assigned to the flat around it, so the trace has nothing to
  read it from. `check.py subject.png --ref subject.png --scan BOX --side S`
  prints each row's dark runs on the subject alone. Place ink from the scan, not
  the trace: strokes placed from the trace came out half a line inside, and
  tubes looked thin.
- **Straight lines take `smooth=False`.** Fills are smoothed by default, so these
  also need `smooth=False`:
  - any flat with a corner on the frame (sky, sea, a field, a cliff running off
    the edge), or it bulges into a round hump at every corner;
  - any closed quad, whose four corners otherwise render as a lens;
  - an organic form's one named corner (a glove's cuff, a heel). Smoothed
    through the right points, a glove lost its cuff and was named "the hood";
  - every stroke of a faceted form such as a rock, crystal or folded paper,
    including its gesture loop. Rendered smooth, a rock field became river
    stones and every gate passed.

  `closed=True` must not repeat its first point. Smoothing is set per call, not
  per point list: a quad's list reused from its `smooth=False` fill for its ink,
  without restating the flag, came back as an ellipse. A small closed form takes
  `tool="pen"`. A flat takes `tool="flat"` with `size` and `scale` pinned, or its
  outline renders 5px wider than you asked. Everything else that is organic
  (fur, a coat, a petal, a cloud) keeps the default smoothing: a soft form typed
  as a `smooth=False` polygon renders faceted and looks like cut paper.
- **Draw a weight swatch first.** Draw one vertical stroke per width, spaced
  apart, with the tool you will use, written with `write(..., swatch=True)`.
  Read it back with `--weights` on a row that crosses the strokes. Read it again
  on the drawing after its first ink, because the same weight once ran 1–3px
  heavier on curves. A hard-edged pen matched to `--measure-line`'s p90 looks
  heavier than the subject's soft line, so match it to the dark core that
  `--weights` reads. Then look at the swatch, and later the first ink,
  downsampled to the delivered size. Weights matched in the 4x space can vanish
  there: a 3px line at 4x is under 1px when the picture is viewed, and the
  drawing reads as flat colour. Raise the finest weight until it shows at
  delivered size, and keep the span.

  Each tool has its own range. `pen` is the hairline tool, and `brush` bottoms
  out near 2px at 1:1. At the same `size` and `scale` a brush runs about twice a
  pen's width. A long straight line (a pole, a tube, a frame edge) wanders
  several px off its points under the default hand, so pass `hand=0` there. A
  flat (`tool="flat"`) never drifts: it lands on its points at any `hand`, so
  the ratio of two bands set side by side holds. The named nibs are set for a
  ~430px subject. On a single object of another size, call
  `gauge(subject_height)`. On a 4x scene the named nibs are unusable, so pin
  `size` and `scale` from the swatch by hand, once for the whole document.
  `weight=` is pressure, not width.

  A band wider than the heaviest weight in the swatch (a strap, a tyre) is a
  closed flat with both sides as points. So is a small form dark all through,
  such as a droplet whose ink is wider than its interior, with the interior
  written over it. Measure each mark's width on the subject before asking for
  it, and try the next weight up before recording a limit.
- **Measure the ground.** Everything on it is judged by its contrast with it.
- **Never retype a coordinate from memory.** Re-measure it.
- **A filter that matches the palette exactly measures the wrong thing on a
  shaded subject.** A limb is its lit value plus a shade band, so a skin-only
  run stops at the shade and reports the limb short, or missing. Every measure
  taken this way made the subject too narrow, so the drawing then looked too
  wide. Measure a form by its whole value group, or between the ink lines on
  either side. The same mistake counts a dark fill as a line. Look at what a
  run-based measure actually classified.

## Overlap order

Overlap comes only from the order you write marks in, and `check.py --depth
ops.json parts.json` is its only check. It works only when stroke tags and
inventory names use the same words:

- Write an overlap key as `far/near` in tag names (`mug.body/table.top`, not
  `body.mug/top.table`). The side behind comes first, so `in_front` names the
  second side (`"mug.handle.top/hand.near"` with `"in_front": "hand.near"`).
  This is easy to get backwards. `--depth` warns when the first side is the one
  `in_front` names, but `in_front` still decides the check, so fix the key to
  match it.
- Put `in_front` only on overlap entries.
- A part with no ink leaves its rows UNRESOLVED, which is as serious as FAIL.
- Matching is by prefix, so a parent's rows clear only when every sub-form is
  ordered.
- Two sub-forms of one surface (a neck ruff and the chest, a muzzle and the
  head) have no front: each one's ink crosses the other's flat. Write their row
  with `"in_front": "same"`. `--depth` then checks no order for it, still wants
  both names tagged on the page, and drops the pair from UNLISTED.
- Write overlap rows at the level of the forms that actually cross:
  `chair.frame.leg/person.leg.near`, not `chair.frame/person.leg.near`. Because
  matching is by prefix, if one member of a frame is written at another depth,
  a whole object-level row fails even though the drawing honours it.
