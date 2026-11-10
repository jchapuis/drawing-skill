# Line weight, inking, and blacks


## Contents

- The weight hierarchy
- What decides the weight
- Line quality
- Spotting blacks
- Continuous paths: chains, belts, ropes, cables
- Hatching and texture, by hand
- The inking pass
## The weight hierarchy

There are three tiers, and the finest line is roughly **8–10×** thinner than the
heaviest:

1. **Heaviest**: the outer silhouette of the figure or object.
2. **Medium**: plane breaks, where two interior forms meet (sleeve against arm,
   jaw against neck).
3. **Finest**: surface detail inside a single plane. Even these should not be
   dead uniform: thicker in the middle, tapering to a point at open ends.

With four stroke sizes, that maps to `xl`/`l` for the silhouette, `m` for plane
breaks and `s` for detail.

> **The ratio depends on the style.** 8–10× is a heavily inked comic. A flat cel
> or *ligne claire* design runs nearer 2–3×, and its finest line is not fine at
> all. When you have a subject, **measure its own span** (the width of its
> lightest interior mark and of its heaviest silhouette) and match that instead
> of using the number above.
>
> **Also match how much of the drawing sits at each weight.** Even with the
> heaviest nib matched to the subject's heaviest silhouette, the drawing comes
> out far too heavy if the two lower weights are used freely, because a flat
> design drops to its finest line as soon as it is inside a form. The drawing
> then measures correctly feature by feature and still looks crude: invisible at
> full size, obvious at 4×, and visible to the tools only in `check.py --parts`,
> as ten to twenty points more ink than the subject in *every* box. For example, a 22px band round a jaw whose subject uses 11px, with
> 2px threads inside a face whose subject never goes below 3px, looks unfinished
> however well every mark is placed. `check.py --weights` reports both figures,
> in pixels.

### Measuring the hierarchy

Read the subject's span before choosing any weight, and the drawing's after its
first ink. `check.py drawing.png --linework parts.json --ref subject.png`
prints the finest, middle and heaviest line width of each picture over the
inventory's boxes, read on each mark's centre line, and fails when the drawing's
span is under half the subject's. `--weights` on a few rows names single lines
(`width@centre`), so you can say which line is the heaviest and where it is.

The common failure is one even, fairly heavy outline round every form, with
interior lines nearly as heavy. It measures as a finest line two or three times
the subject's, with the heaviest line about right. Fix it from the bottom up:

- **Thin the interior lines.** Surface detail and lines inside a form go down to
  the subject's finest width, usually a third or less of the silhouette.
- **Make the silhouette heavier**, unevenly: heavier on the shadow side and where
  the form turns away, thinner on the lit side.
- **Make the contacts heaviest**: under a form resting on another, where a foot
  meets the ground, under an overhang, where a limb crosses the body. A heavy
  line there stands in for the cast shadow.

Each is a `size` or pressure on a stroke you write; read it back on the swatch
and the drawing with `--weights`.

### How wide a span

Where line weight is quantified at all, it is in technical pens, sold from
**0.03 mm to 0.8 mm**. Panel frames and backgrounds use the top of that range,
0.5–0.8 mm, so a whole page spans roughly **20×**, wider than the **8–10×** of a
single figure's contours.

There is **no rule about how many weights**, and some artists ink a whole page
with one. But the weight always *varies*, even in *ligne claire*, which is
defined by flatness and the absence of hatching.

## What decides the weight

**Decide the light source first.** Every later weight decision depends on it.

- **Shadow side heavy, light side thin**, on the same form. This works on
  anything solid, not on smoke, fire or cloud.
- **Depth**: foreground heavy, middle ground medium, background fine. This alone
  separates the planes without any shading.
- **Contact**: an edge touching another surface gets no extra weight, and an
  edge pulled away into open air gets a thicker line. This is how "in front"
  reads.
- **Distance from the light**: the further away, the thicker. Under an overhead
  light the feet carry more weight than the head.
- **Anatomy**: thicker around fat and muscle, thinner around bone.
- **Curves**: thinnest at the apex of a curve. A motion swoosh is the exception
  and thickens at its apex.
- **Junctions**: thicker where structures meet, like jaw into neck.

**A top-lit face** gets heavier line under the top eyelid, the nose, the top lip,
the bottom lip and the jaw, where the heavy line stands in for cast shadow.
**Invert every weight** for lighting from below, which is why underlighting looks
sinister.

**Keep it consistent**: all light-side lines roughly equal to each other, and
all shadow-side lines roughly equal. Weight varies for a *reason*, never at
random.

**Never give two adjacent objects on different depth planes the same weight.**
It merges them onto one plane, and a small distant figure starts to look as if
it is standing on the near figure's shoulder.

## Line quality

- **Draw from the shoulder or elbow**, not the wrist, for anything longer than a
  few centimetres. That gives smooth, even arcs instead of jittery segments
  pivoting at the wrist.
- **Taper**: thick through the middle, pointed at both ends. A hand gets this by
  speeding up into the stroke and easing off out of it, like a car reaching speed
  and then coasting instead of braking.
- **Ghost the stroke** two or three times before touching down, then make it in
  one confident pass.
- **Never correct by drawing over**: a second, bolder mark makes the error *more*
  visible. Redraw the whole segment.
- **A drawn line does not shake.** Watch anyone ink: the stroke is smooth. What
  varies from one mark to the next is where it landed, how hard the hand leaned,
  and a slight bow across the whole arc, never a wobble along it. Real hand
  tremor is tens of microns, invisible at viewing scale. Rendering tremor is the
  quickest way to make a line look like a beginner's.
- **One contour, one stroke.** Short segments chained end to end leave a step at
  every join, because each has its own placement error. A long contour is
  really laid in several passes, but they overlap and retrace *along the whole
  run* instead of butting together. **Lift the pen only to change weight**, and
  then make the two strokes meet where both are thinnest, so the taper hides the
  join.
- **Do not add weight by doubling.** With an opaque ink, a second pass beside the
  first makes two parallel lines, not a heavier one. Weight comes from the nib
  and the pressure profile.
- **A closed form is one closed contour.** An eye, a nostril, a vent slot: one
  continuous loop of varying weight, not two arcs meeting at the corners. Arcs
  that meet leave a knuckle at each corner, and the corners of an eye are where
  the subject's line is finest.
- **A heavy line must be more precise than a fine one.** Weight magnifies error:
  a kink invisible at 3px is a lump at 10px. The pressure model makes it worse,
  because a hand leans into a tight turn and lays more ink exactly at the
  unintended corner. So give a heavy contour *fewer* control points, further
  apart, with no change of direction you did not mean. If a thick stroke looks
  jagged, take points out.
- A uniform-width mechanical line looks **dead** however accurate it is. Vary the
  width along each stroke.
- For a small enclosed detail such as a nostril, **outline it and fill it**. A
  single stroke distorts the shape.
- **A ring is a stroke, not a filled shape.** A tyre, a rim, a chainring, a clock
  bezel and a washer are rings, and filling a closed circle fills the hole too.
  Draw the band as a single wide stroke along its centre line, so the stroke's
  width is the band's width. The same goes for any outline whose inside must
  stay open.
- **A band drawn as a stroke sits on its CENTRE line, but a scan of the subject
  gives you its EDGE.** The two coincide only for a hairline; otherwise the band
  is off by half its width on every side at once. For example, a tyre whose
  points were taken off the subject's outer silhouette and drawn as a 24px stroke
  came out 14 to 55px too wide, worst at the bottom of the wheel, where the whole
  band lands outside the form, although every point was measured correctly. So
  after
  measuring where a band ends, **move the path half a weight inward** before
  drawing it. Anything that meets that band (spokes, hatching, a joint) stops at
  the new path, not at the old silhouette.
- **A mark that bounds a small pale shape eats into it**, and past a certain
  width it has eaten all of it. An eye is the lid *and* the white beneath it, so
  a thicker lid deletes the white, and the expression with it, while the lid
  stays exactly where it was measured.
  The same applies to a nostril, a highlight, a gap between two tubes, or the
  slot inside a vent. **Where a form is defined by the gap between two marks,
  the gap is what you measure.** Take it off the subject and let the marks fall
  where it puts them, instead of choosing a weight and hoping the space
  survives. Halving one such mark often brings a feature back.

Leave out every line you can: *"the secret to drawing is not the making of
lines, but the elimination of unnecessary lines."* Rendering a form in fewer
lines takes more skill, and over-rendering usually hides weak construction.

## Spotting blacks

Solid blacks are **placed**, not shaded. They separate figure from ground, set
depth, lead the eye, set mood, and tie scattered shapes together into one.

**Spread them unevenly on purpose**: a little black on most things, a lot on
some, a little on the objects of interest. An even scatter looks like noise.

**Three values across three planes.** Give black, mid-tone and white one each to
foreground, middle ground and background, and change which gets which from
panel to panel to shift where the weight falls. As with line weight, never give
two objects on different depth planes the same value.

**Contrast inside a mass**: leave small islands of white in a black mass, or drop
small black accents into a large empty area. The local break pulls the eye
harder than a large uniform black does.

If a finished panel looks flat and grey when squinted, add a real black anchor
**and** a real white space to rest the eye. More mid-tone detail will not fix
it.

## Continuous paths: chains, belts, ropes, cables

A chain, belt, rope, cable, hose or wire is one continuous path, even when
written as several strokes. The eye follows it end to end, and any break reads
as a broken object: a chain whose run stops short of the sprocket
is an open loop, and a cable that stops before its end stop hangs loose. Draw a
path like this:

- **Every piece meets the next with no gap.** Write the path as consecutive
  strokes (a straight run, the wrap round a wheel, the next run) that share their
  end points by name: the end of one and the start of the next come from the
  same entry in the dict of measured points. Two numbers typed separately for one
  junction drift apart.
- **A run meets a wheel at its tangent point**, where the straight line touches
  the circle without cutting it and the radius is square to the run. Measure
  that point on the subject's `--zoom` and name it. The wrap round the wheel
  starts and ends at those named points. Stopping at the wheel's outline
  anywhere else leaves a kink or a gap.
- **An anchor is a point the path reaches.** A rope ends at the hand or ring that
  holds it, and a cable at its stop or housing. The stroke's last point is that
  anchor's named point.
- **Give each run its own tag** (`bike.chain.upper`, `bike.chain.wrap.rear`).
  `--joins` does not compare strokes that share a tag, since a hatch group shares
  one, so runs under one tag are never checked against each other.
- **Draw the path's texture when the subject shows it.** A chain's links, a
  rope's twist and a beaded cable read as a textured line, and a plain line in
  their place reads as a wire. Look at the subject's `--zoom`: if the line is
  beaded or linked, draw it that way. `dash="dotted"` or `dash="dashed"` gives a
  beaded or broken line along your own path, at a spacing the renderer sets.
  Compare that with the subject's link pitch on `--zoom`; where it does not
  match, draw each link as its own small stroke at the measured pitch. Either
  way the path's points are yours.
- **Teeth are a repeated small form.** Count a gear's or sprocket's teeth
  (`--counts`, or on `--zoom` into `notes.md`) and write each tooth with its own
  points, like any other group of repeated forms. A plain circle in their place
  reads as a ring, not a gear.

`check.py --joins ops.json --parts parts.json` lists every ink end that stops
one to eight line widths short of a mark of its own object that it is heading
for: too far to read as a join, too near to read as a separation. A gap the
subject really has goes in parts.json as `"_gaps": ["tagA/tagB"]`.

## Hatching and texture, by hand

On a subject drawn in fine ink (an engraving, a pen drawing, an old printed
illustration), the hatching carries the shading, the texture of each material
and most of what makes it look drawn. Flats with an outline and no hatching look
like a colouring-book copy of it, however well they are placed.

**Measure, then write.** For each hatched region:

1. Box it and run `check.py subject.png --hatch x,y,w,h`. For the box, it prints
   the share covered by line marks, and for each group of parallel marks, its
   angle (0 horizontal, 90 vertical, 45 a `/`), the spacing between neighbours,
   the typical length and width, and the middle half of each range. Read pale
   lines cut into a dark (feather shafts on a black wing, light grain on a dark
   rock) with `--light`. If it warns of grain, the marks are texture fragments,
   not hatching (a photograph, fur): see `photograph.md`.
2. Write each group into the part's `parts.json` entry as `"hatch": {"angle",
   "spacing", "length"}`, one entry per group, so `--linework` can check it.
   For pale lines add `"light": true` inside the same dict.
3. Read the actual lines off a `--zoom` or a `--scan` across the group: where
   each line starts and ends. Then write each hatch line as its own `stroke`, on
   its own line of `draw.py`, with its own two or three measured points. Vary
   length and spacing within the measured ranges, as a hand does: no two lines
   the same length, no two gaps equal.
4. Re-run `--hatch` with `--ref drawing.png`. It flags (`<<`) a missing group,
   an angle more than 20° off, spacing off by more than half, or coverage under
   half the subject's. It FAILs (exit 1) a group whose marks are over 1.6× the
   subject's width, or whose width as a share of the drawing's outline weight is
   over 1.6× the subject's share. Both numbers print either way, in the
   subject's pixels whatever size the render is.

**Fix the outline weight first.** Before writing any hatch mark, run
`--weights` on a few rows across the outline, on subject and drawing. Hatching
is read against the outline: hatching at the subject's pixel width still looks
heavy against an outline drawn too thin.

**Hatch weight: the lightest in the swatch, set from the measured width.** Take
the hatch weight from the group's `width` in `--hatch`, never from the outline.
A hatch drawn "a step under the contour" ends up at the contour's weight, and a
field of marks as heavy as the outline looks like heavy brush strokes however
right their angles are. The match is relative too: if the subject's hatch is a
third of its outline's weight, the drawing's is a third of its own. `--hatch`
reads the subject's width at half each mark's darkness, so a soft upscaled line
is not read wider than it is; match your swatch to that number.

**Hatch character: tapered, and in the line's colour.** A hand-drawn hatch mark
tapers at both ends, thin where the nib lands and lifts, and more at the end
that runs out into the light. It is drawn in the subject's line colour. Measure
that colour: sample the centre of a few marks on the subject at the magnified
view and put the value in `palette.json`, under the name you ink with. Old prints
and pen drawings are often a warm dark brown. Uniform, square-ended marks in pure
black look heavier than their width, so a group at the subject's width can still
look like heavy brush strokes. Use `tool="brush"`,
whose default `lead` and `tail` taper both ends, at the small sizes below (or
`lead=` and `tail=` on a `marker`). `tool="pen"` has no taper: keep it for a
subject whose hatching is a technical pen's even hairline.

A swatch rendered at 4x with `--scale 0.5`
(1:1 with `subject.png`), widths at half darkness, and each line's contrast
against a paper of 250 once downsampled 4x to the delivered size:

| instrument | width at 4x | contrast at 1x |
|---|---|---|
| `pen`, `size="s"`, `scale=0.25` | 2px, never full black | 25: gone |
| `pen`, `size="s"`, `scale=0.5` | 2px | 53: faint |
| `pen`, `size="s"`, `scale=0.75` | 2px | 117: hairline, visible |
| `pen`, `size="s"`, `scale=1.0` | 3px | 111 |
| `pen`, `size="s"`, `scale=1.5` | 5px | 203: a solid 1px line |
| `brush`, `size="s"`, `scale=0.35` | 3px | 150 |
| `brush`, `size="m"`, `scale=0.6` | 7px | 226 |
| `brush`, `size="m"`, `scale=1.0` | 11px | 236 |

So the hairline at 4x is `pen` `size="s"` at `scale` 0.75–1.0: 2–3px, still a
visible grey line at the delivered size. Below `scale` 0.5 it fades out there.
For a mark that ends in a point at both ends, `brush` `size="s"` at `scale`
0.35–0.5 gives 3–5px, tapered by its `lead` and `tail`. A `brush` at `size="m"`
starts at 7px, which on most subjects is an outline weight, not a hatching one.
Render your own swatch before trusting these: the numbers move with the palette,
the ground and the renderer.

The instrument only prints numbers. Nothing turns a group into strokes, and a
loop or comprehension that does is a generated mark, which `pen.write` refuses.
Expect a hatched region to cost fifty or a hundred lines of `draw.py`.

**Indicate; do not fill.** Do not hatch a whole surface evenly. Keep hatching
affordable the way illustrators do:

- **At the edges and the turns.** Put the texture where the form turns away and
  along the shadow edge, and let it thin out and stop as the surface comes into
  the light. A few marks at the edge of a roof or a field of grass say the whole
  surface is tiled or grassy [read: Guptill, *Rendering in Pen and Ink*].
- **Near the centre of interest.** Put the densest groups there and thin them
  out with distance from it, as with every other kind of detail.
- **One group per plane.** Each plane of the form gets its own group at its own
  angle. Where the plane turns, the group changes direction or curves round the
  form. A single angle across several planes flattens them into one.
- **Start each line in a dark.** Begin it at the shadow edge or the contour and
  run it out into the light (`tone.md`), so the group has one hard edge and one
  ragged one.

**Line quality inside a group:**

- **Bad**: all hatch lines the same length, crossing at right angles. This looks
  like a mechanical pattern.
- **Also bad**: two layers at nearly the same angle, which produces a moiré.
- **Good**: varied lengths, some short and broken, getting heavier as they merge
  toward a black, and lines curving *around* the form to show volume.

Texture that is not hatching (a rock's cracks, bark, the dashes of a stone wall)
follows the same rules: measure the marks' direction, length and spacing with
`--hatch`, write each mark, indicate at the edges and let it thin out.

## The inking pass

1. **Fix the light source.** Everything else depends on it.
2. **Ink the contours of the big shapes first**, thin on the light side and heavy
   on the shadow side. Every later decision is placed relative to these.
3. **Set up depth** with contour weight per plane (heavy foreground, medium
   middle, fine background) before adding anything else.
4. **Plan the blacks while inking the contours**: mark every area that will be
   solid, but do **not** fill it yet.
5. **Inking is not tracing.** Correct obvious errors in the underdrawing instead
   of copying them. Viewing the page mirrored shows proportion errors you have
   stopped noticing.
6. **Feather and hatch** to soften hard black edges and add volume. Know what
   each mark is for; do not copy the pencil's rough marks literally.
7. **Erase all pencil, then fill the blacks.** Filling after erasing keeps them
   dense; filling first muddies them.
8. **Background, texture and effects last**, on top of the settled contours and
   blacks, so they follow the hierarchy instead of competing with it.
9. **Final pass**: remove stray marks. Neatness counts even on a rush job.
