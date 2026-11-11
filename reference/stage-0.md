# Stage 0: reading the subject

Everything stage 0 produces before the first mark: the working space, the
palette, the trace, the describer's answers, `reading.md` and `parts.json`.
SKILL.md lists the stages; this file details stage 0.

## Contents

- The working space
- Measure per object, even though you draw in one document
- A trace does not say what the objects are
- Stage 0 (palette, trace, describe, reading, inventory)

## The working space

**A scene's working space is the delivered size times four.** A single object
gets the same 4x space when its smallest feature needs it (under about 40px at
delivered size, as in most objects). Every mark, measurement and render lives
in this space. Make it once: `subject.png` is the delivered image
upscaled 4x with `Image.BILINEAR`, and the delivered image is kept beside it as
`subject_1x.png`, for the describer and for reading the whole picture.
Points you trace on `subject_1x.png` can be typed as traced after `pen.unit(4)`
(and `unit(1)` to go back); it scales them and adds no shape. Widths are still
measured at 4x, not multiplied (below).

Do not upscale with LANCZOS or BICUBIC. Both overshoot into a pale halo beside
every dark line, and the halo classifies as ground (in one test LANCZOS did this
to 0.12% of the pixels and BILINEAR to none). Even with BILINEAR, the soft ramp
beside each line traces as a ring region round every outlined form, so trace an
upscaled subject with `--fringe 60`, which assigns the ramp to the line. A pale
form bounded by ink then traces 3–5px inside its visible edge on every side, so
take the edges of small pale forms from a scan or `--zoom`, not the trace.

The harness exports at device pixel ratio 2, so render with
`./build.sh --scale 0.5` to get renders 1:1 with `subject.png`. **macOS has no
`timeout`**; use `gtimeout`, or `perl -e 'alarm N; exec @ARGV' --`.

**Measure `--line` in the space you trace in.** `trace.py subject.png
palette.json --ink NAMES --measure-line` prints the per-pixel min(row, column)
run width of the line; pass its p90. Runs wider than twice the median run are
left out as flats. (A fixed fraction of the image once let a mouth count as line
and cut under a small object's own lines.) Never
multiply the delivered-size figure. For example, one line was 6px at 1x and
20px, not 24, at 4x, because the upscale's ramp thins the core that classifies
as ink. Give `--ink` every palette name that is line: the darkest near-black, a
line that reads brown over one flat and black over another, and a line drawn in
a colour of its own (a horizon, grass), which gets its own palette name.

## Measure per object, even though you draw in one document

A trace of the whole picture resolves every object at picture scale. A small
object comes back with a handful of points per form, and no care at the drawing
stage recovers them. Tracing the delivered-size image and scaling it
up puts every boundary on a grid as coarse as the scale factor. So **crop each
object out of the working-resolution subject and trace that**: `crop.py
subject.png x,y,w,h meas/NAME.png` cuts it at 1:1 and stores its corner in the
PNG, so `trace.py meas/NAME.png palette.json` returns whole-picture coordinates
with no flag. The stored corner is not your box's corner, because the crop has a
margin. Passing a box corner as `--offset` once shifted every region 8px, and
the tool now refuses it.

Marks stay in one `draw.py` in one coordinate space; only the measuring is per
object. For example, one object gave 77 regions and 872 contour points in a
whole-picture trace, and 156 regions and 3878 points from its own crop. That is
the difference between an object a viewer can name and a shapeless blob. Forms
with three to nine points each are the symptom to watch for.

**Masses are the one thing measured on the whole picture.** Trace
`subject_1x.png` (segment it, for a photograph or a painted subject) and read
their outlines off that. Masses carry no ink, so the 1px grid at delivered size
costs nothing. There are five to twelve of them, and you type them into
`draw.py` like every other mark, from the trace, with as many points as their
silhouettes need. A mass layer of hundreds of flats, one per traced region, is
just the generated drawing again.

Where two ink-less masses meet, the edge is one shared entry in the dict. The
far mass runs past it, under the nearer mass written after it, so no hairline
of ground opens along the join. A mass is usually several traced regions split
by ink, and its outline is their union with the ink closed over, using a kernel
the width of `--line`. That kernel is the only setting, and it is measured, not
chosen. Masses read off different regions do not meet exactly,
and a simplified outline cuts corners, so extend each far mass by hand under
the one in front. Otherwise the first render shows ground along every join.

## A trace does not say what the objects are

Deciding which regions make up an object, and which single form a viewer reads
as that object, is part of the reading. It costs the same on a detailed trace as
on a sparse one. Taking the largest region per object is tempting and fails in
predictable ways. A limb comes back as two ribbons: its lit strip
beside a separate shade band. A garment comes back as the two patches either
side of its zip, with no shoulders. An object with no dominant region (a sock, a
sole, a neck) is never drawn, and nothing reports it as missing.

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

A lit strip and its shade band are one form with two values. Never draw them as
two flats side by side.

A form cut in two by a nearer one is still one form, and each cut end is the
nearer form's edge: it ends on that form's ink, never in mid-surface. The tracer
returns the pieces as unrelated regions, and a scan confirming the gap does not
ask what made it. A flat that stops inside another flat with
nothing drawn across its end looks like a patch stuck on. For example, a dark
band broken by a sleeve became two dark patches on a torso, each within 10px of
the subject, because the sleeve's own edge was never drawn. Name the occluder of
every cut end and run `--overlay --box` on it. A blue line across the end with no
red beside it is the occluder's contour, missing from the drawing. Count the
pieces on the subject: a band wrapping a body is cut by every limb in front of
it, and the piece that shows only below an arm is the one most often left out.

The same holds from the far side. A form that passes behind another continues
under it, and its own outline does not close at the occluder's edge. For
example, an arm whose outline closed just above a bar read as a bare hand
resting on it. Check the part list against the canvas before calling the picture
done.

## Stage 0

1. **Palette.** Sample every flat and the ground off the subject into
   `palette.json`: one entry per flat, as many as the subject has. Each entry is
   a name you choose and a `#rrggbb` value (`"coat.lit": "#c8934a"`, `"roof"`,
   `"sky"`; letters, digits, `.`, `_` and `-`), plus `background`, the ground.
   Name each flat for what it is, so `color=` says what it paints. A mark
   may not use `background`, so where the ground shows through a hole in a
   form, give the ground's colour a name of its own. Write down where you
   sampled each colour. Then trace, and read the unmatched-colour line that
   `trace.py` prints: a flat missing from the palette comes back as a clumped
   patch of pixels far from every entry.

   - **Sample each value step of an object at its most saturated representative
     patch**: inside the form, away from its edges, its highlights and any
     colour the ground reflects into it, and on a patch large enough to be the
     step and not one hair or speck. Never take a step's colour from an
     average. A k-means centre, a blur over the whole object, or a posterised
     copy mixes the step with its highlight, its shadow and the ground's spill,
     and the mix is greyer than any patch on the subject. A gold coat sampled
     that way comes back beige in the light and brown in the shade.
   - **Keep the hue ramp.** Read it off the subject from light to shadow: each
     step is darker, and on most warm or translucent materials (fur, skin, wood,
     fruit) also warmer or more saturated, never greyer. Shadow steps greyer
     than the subject's mean the palette has lost the ramp.
   - **Compare the palette's chroma with the subject's** before drawing. For each
     of an object's steps, put the palette entry's saturation beside the
     saturation of the subject's most saturated tenth of pixels at that value.
     An entry well below it is an average, so sample it again. Once there is a
     drawing, `check.py drawing.png --ref subject.png --colour parts.json`
     compares each part (`reference/judging.md`).
   - A flat within about ten levels of the ground (an eye's white, teeth) cannot
     be separated from it by colour, and the tracer gives it bare ground. Draw
     it from measured extents inside its ink, and trace with `--exclude NAME`,
     or the ground itself comes back as that flat.
   - In the same way, a dark flat a few levels off the ink takes over the ink's
     ramp, so leave it out of `--ink`. Fill it with a near-black name of its
     own, never the ink's black. Vents, brows and a strap drawn in the line's
     black look like holes punched through the form and pull the eye away from
     the centre of interest.
   - Ramp pixels classified as a real name come back as long thin regions
     hugging the ink, with a `median` far from their entry. That is not a
     missing flat.
   - A nested part may reveal a flat the full picture could not resolve: a
     tooth, a tongue, anything smaller than the picture's own sampling. That is
     not a stage 0 failure and stage 0 cannot prevent it. Sample it, add a name,
     and record it in `reading.md` beside the palette.
   - An older `palette.json` uses tldraw's 13 stock names (`black grey
     light-violet violet blue light-blue yellow orange green light-green
     light-red red white`) repointed to the subject's values. It still renders
     unchanged. A new palette uses its own names: a stock name suggests a hue
     the flat lacks and is easy to type for the wrong flat.
2. **Trace.** Choose the tool by the subject. Both write `regions.json` in the
   same format, and both read the corner `crop.py` stores in a crop.
   - **A flat-cel or printed subject** (flats and ink):
     `python3 trace.py subject.png palette.json --png regions.png`. It
     classifies every pixel to its nearest palette entry. A printed or textured
     subject (halftone dots, lithograph grain, paper texture in a scan) traces
     as a tangle of specks. Trace it with `--smooth PX`, which smooths the
     texture out before classifying. Set PX near the size of the texture's
     repeat, and check that the unmatched-colour figure falls.
   - **A photograph or a painted subject** (continuous tone, brushwork, fur,
     foliage, no ink to bound the flats): `python3 segment.py subject.png
     --palette palette.json --png regions.png`. Classifying each pixel of such
     a subject gives hundreds of noise regions, even with `--smooth`.
     `segment.py` smooths the texture with an edge-preserving filter and merges
     similar neighbours into about `--regions` (default 40) regions that follow
     the forms. `--box x,y,w,h` measures one part at a finer scale; `--silhouette
     x,y --box ...` prints one object's outline. Read `reference/photograph.md`
     before measuring a photograph.

   Check `regions.png`. On a scene, use `subject_1x.png` for the reading and
   the masses, and each part's own crop when you reach it. A region is a flat
   or a patch of similar colour, not an object; naming the regions is the
   reading.
3. **Describe the subject.** Run `describe.sh subject.png A` and again with `B`
   (the run name keeps both files apart; on a scene, describe `subject_1x.png`).
   Its answers 3 (what each figure is doing), 4 (what touches what) and 5
   (expression) are the acceptance clauses. Quote them; do not paraphrase. A
   drawing that reads as a different action has failed, whatever else it gets
   right.
4. **Reading.** Write `reading.md` with:
   - what the picture is, in one sentence;
   - the big shape as one or two forms;
   - the line of action;
   - when the action lives in a turn or a tilt (a look over the shoulder, a
     head thrown back), the 3–4 angles that carry it, measured with `look.py
     axis` (`reference/figure.md`, `head.md`, `bird.md`) and checked again at
     stage 4 and at the final gate;
   - how this subject differs from the typical one, measured, because that
     difference is the likeness;
   - the light source, fixed now;
   - the two value groups;
   - **the line character**, measured. Give the outline's weight range, finest
     to heaviest in px (`check.py subject.png --linework parts.json --ref
     subject.png` prints the subject's span, compared with itself; `--weights`
     on a few rows gives single lines), and where the heaviest lines sit (the
     silhouette, under forms, at contacts). Say whether the line is uniform or
     varied. Then list every hatched or textured region: its box, and from
     `--hatch BOX` its direction, spacing, mark length and value. When a
     subject's look is mostly hatched ink (an engraving, a pen drawing, an old
     print), this paragraph describes that look, and a drawing that leaves it
     out looks like a colouring-book copy however well its flats are placed;
   - what you leave out on purpose. That may be texture, small detail and
     variation inside a form, never an object. Every object a viewer of the
     subject names (the describer's answers 1, 3 and 4) is drawn, as a part or
     as a mass, however small it is and however tight the budget. If the budget
     cannot cover every named object, say so and ask for more budget or a split
     across agents. Never drop the object and mark its clause as not earned;
   - the budget and the number of correction rounds;
   - then the acceptance list.

   For a scene, also include everything S0 asks for above.
5. **Inventory.** Write `parts.json`: small and ranked, every entry a shape note
   with a box read off `regions.json`.

   - **An entry descends to the sub-forms that make the object what it is**,
     each with its own box and note. A wheel is a tyre, a rim, spokes and a hub,
     not "a wheel". A glove is its fingers, its thumb and its cuff. A single
     note for a whole object gets one silhouette, which a viewer often names as
     a different object. The count of repeated small forms already includes
     these sub-forms; this is where they become marks.
   - **A reference's ```checklist block is enforced.** `build.sh` runs `check.py
     --checklist parts.json` and will not build until each sub-form the
     checklist lists for an object in the inventory has an entry, or a reason in
     `"_absent": "name: reason; ..."`. A name is either the sub-form as the
     checklist lists it (`"hole: ..."` excuses it for every object) or a dotted
     path ending in it (`"tree.hole: ..."`, that object only). A sub-form listed
     only in prose gets read and then skipped, which is why an inventory can
     still stop at the first level. A checklist applies only when a key names
     one of its `object:` words. When none does, `--checklist` warns that no
     reference object matched, and its PASS then checks nothing. Use a listed
     name in the keys, or add the subject's name to the reference's `object:`
     line.
   - Stop descending where the next level down would not survive at the scale
     you will draw it. That scale is the part's working resolution, with its
     smallest feature near 40px, not the picture's. A human figure always
     descends at least to head, torso, arms, legs and feet, whatever its tier
     (the person checklist in `reference/figure.md` enforces this).
   - **Two instances of one object class get the same sub-form list.** The
     second of two wheels, hands or shoes gets less attention and fewer
     entries, and its missing sub-form is then missing from every gate.
     Reconcile the pair before leaving stage 0, or write down what the second
     really lacks.
   - Name the junctions as entries of their own (hand/handle, foot/pedal,
     hip/seat, tyre/ground, and every joint), because that is where scenes
     fail. **Name the specific crossing forms in overlap rows**:
     `chair.frame.leg/person.leg.near`, not `chair.frame/person.leg.near`.
     `--depth` matches by prefix, so if one member of a frame sits in another
     depth group, a whole object-level row fails even though the drawing
     honours it.
   - Then cut a plain image crop of the subject (a PIL crop is enough) at each
     tier-1/2 box, grown by a fifth so the part's edges and neighbours are in
     view. On a scene, cut from `subject_1x.png` at the box divided by four,
     since a 4x crop of a large part runs to thousands of pixels. Cut a box
     under about 150px at 1x from `subject.png` instead, since at 1x a 14px
     sweat drop comes back as "a low-resolution crop". Run `describe.sh` on each
     crop. The calls are independent, but run at most four at once (`xargs
     -P4`): many at once can hit the CLI's usage limit, and then every call
     fails. `describe.sh` exits 3 when the CLI reports a usage or rate limit;
     wait and rerun only those crops.
 Where the answer does not name your
     part, fix the note or delete the entry.
   - An answer that names a neighbour means the box is on the neighbour. If a
     tightened box still names it, or the answer is "cannot tell", the part has
     no silhouette of its own. Keep such a part when the acceptance list names
     it, and judge it in context later.
   - An entry for something the subject lacks carries into every later stage,
     and only this check can remove it.
   - **Count each group of repeated small forms** (vents, fingers, teeth,
     spokes, droplets). Count on the object's own working-resolution crop, by
     a component scan of its pixels. A count read by eye off a magnified view took

     a parallel edge for a third motion arc. Use a box that stops short of every
     neighbour: a box reaching into a pile or cutting a forearm counts their
     fragments as forms. Count a group running parallel to a heavier line
     together with that line, and say so in the count. Never count with a
     describer on a picture-scale crop, which counts blobs and under-counts.
     Cross-check against the closed regions the object's trace returns; a
     mismatch usually means forms left open where a surface curves away.
   - **Write the count into the entry** (`"count": 7, "value": "black+grey"`) and
     run `--counts parts.json` after S2 and after the object. It is the only gate
     that fails on something missing, and only where it can count the subject:
     separate forms of one value in a tight box. Crossing or touching forms
     (spokes, slots bounded by their own ink, a wing's feathers) come back
     UNCHECKED; count those on `--zoom`, on both images, into `notes.md`. The
     tracer drops forms under `--min-area` and gives dark forms narrower than
     `--line` to their neighbours, and `--masses` passes even when a spray of
     droplets is missing. A count put off until later never gets taken.
   - **Write each hatched region's measurement into its entry**, from `check.py
     subject.png --hatch BOX`: `"hatch": {"angle": 127, "spacing": 33, "length":
     38}`, in degrees on the page (0 horizontal, 90 vertical, 45 a `/`) and px.
     A region with two groups (cross-hatching, or two planes in one box) gets
     two entries, one per group. For pale lines cut into a dark, measured with
     `--hatch BOX --light`, add `"light": true` inside the `hatch` dict
     (`"hatch": {"angle": 73, "spacing": 39, "length": 39, "light": true}`).
     Placed beside `hatch` instead, it is ignored and dark lines are checked;
     every check warns about an entry key it does not read.

     `--linework` fails a drawing that has no group at that angle in that box,
     or whose group there is heavier than the subject's (its mark width over
     1.6x, or its share of the outline's weight over 1.6x). Note the group's
     `width` too: it sets the hatch's weight, not the outline
     (`reference/line.md`). If `--hatch` warns that the marks are grain, they
     are texture fragments (a photograph, fur); write no entry for them
     (`reference/photograph.md`).

```json
{
  "nose": {"shape": "ON the silhouette: the profile leaves the brow, runs down and OUT to the tip, then turns back under it", "box": [540, 336, 45, 50]},
  "mug.handle.top/hand.near": {"shape": "the fingers close over the handle; the handle disappears behind them and reappears 30px to the left. No gap", "box": [318, 470, 96, 70], "in_front": "hand.near"},
  "radiator.slots": {"shape": "seven slots radiating from the top edge, each tapering to both ends", "box": [380, 100, 330, 200], "count": 7, "value": "black"},
  "rock.face": {"shape": "short horizontal dashes along the front face, densest under the overhang", "box": [400, 3330, 1600, 150], "hatch": {"angle": 2, "spacing": 33, "length": 39}}
}
```
