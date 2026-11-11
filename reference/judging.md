# Judging a drawing

How to use the judges (the blind describer, naming a part, the critic), and
what each `check.py` flag catches.

## Contents

- Judges
- Judging by eye

## Judges

**Describer.** `describe.sh image.png [RUN]` saves its answer beside the image as
`image.describe[.RUN].md`. If the reply lacks five numbered answers (the CLI's own
error), it is refused with exit 1 and nothing is written. A usage or rate limit
exits 3. The describer sees a copy under a neutral name, so a crop's file name
does not give away the answer. It is blind and factual, and it excuses what it
sees, so ask it what a thing is, never whether it is good. If its answer to 3 or
4 differs from the subject's, the picture's action is wrong: fix that first,
whatever the numbers say.

The describer varies from run to run. At a gate, run it twice and keep only what
both runs say (by meaning, not wording); a clause only one run states counts
neither way. Describe the drawing at the subject's size: downsample
`drawing.png` to `subject_1x.png`'s dimensions first. Run it twice on the subject
too, and never gate on a clause the subject's two runs do not share.

Run it on part crops as well: a face can pass at 1:1 and show the opposite
expression at 4x. A crop also includes neighbouring parts, and a neighbour still
at an earlier stage gets misnamed (an unbuilt helmet was read as a slab of hair).
A clause about a part not yet drawn says nothing about the part you are judging.

**Naming a part.** Crop a part's box out of the subject and out of the drawing
(a plain PIL crop), run `describe.sh` on each, and read the two paragraphs side
by side. This is the only tool that asks what a thing is. The others measure
presence, placement, value or design, and an object can pass them all (present,
in its box, at the right weight, in a matching design) while a viewer still
calls it a plate of food.

Ask for a paragraph, never a single name. Shown a crude mask, a viewer says
"face", which matches "a laughing woman's face" on its head word. A paragraph has
to commit to kind, proportions, parts and angle, so a loss shows.

The describer finds problems; it does not measure quality. A wrong name ("animal
paw", "a plate of food") is a true diagnosis. A right name proves nothing: a
subject scored against itself does not come back at 1.00, a visibly wrong
drawing scores like a faithful copy, and two blind viewers disagree by more than
any such score resolves. Never build a score, a threshold or a ranking from it.

A correct name shows the object is recognisable, not that it is a likeness: a
face can be named correctly and still be the wrong shape for the person.
Likeness is defined by the shape note and checked with two tools on the centre
of interest:

- an **outline scan** (`--scan` on the side the silhouette faces), the only thing
  that sees a wrong turn between two measured landmarks;
- the **two inks** (`--overlay --box`), because the outline is not all of a
  likeness.

For example, a face matched its subject's edge within 10px row by row and still
read wrong: the nose's ridge ran diagonally from brow to nostril in the subject,
and nearly vertically down the far edge in the drawing. For every blue line inside the form, say which red line is meant to match
it and how far it strays, then measure it with `--scan`. There is no threshold.
Deciding which line matches which is a judgement, and any distance between the
two inks shrinks as ink is added. `reference/measuring.md` has the detail.

**Critic.** A fresh agent is given both images, told which is which, and asked
for the N worst ways the drawing falls short as a drawing of the same thing. It
is told to give no style comments, no praise, and no guesses at how the drawing
was made or how to fix it. Asked for N, it returns N, and about a quarter are
invented, so ask for few and verify each against the render. It finds
junction faults nobody listed, but rarely explains them well.

Before any mark, turn each item into a measurement on subject and drawing. An
item the measurement does not reproduce gets no mark, whoever raised it. Use a
tool that can see the claim. Measure a claim about shape ("the pad
is a rounded oval") on `--zoom` or `--overlay --box`, and never refute it with
row widths. For example, a pad with the right width on every row and the wrong
shape was cleared by a width scan and came back as a real fault a round later.
Write each refusal in `refuted.md`, one line per item: the claim, the
measurement on each image, the verdict. Give each round's critic `refuted.md`
with the images. An unrecorded refusal is raised again next round, and the
second time you are more likely to obey it than measure it. The
note also reveals misplaced faults: an item that does not reproduce on the form
it names is often real on the form next to it.

**Numbers.** These are the `check.py` flags.

| flag | sees |
|---|---|
| `--masses` | The wrong shape. It closes the line away (dark runs thinner than the subject's line), cuts both images at the subject's value levels, and uses `--colours` 3 by default. **It checks the overall design, not proportion.** A head half again too wide is still a pale blob above a dark torso at thumbnail size, and passes |
| `--scan x,y,w,h --side S` (needs `--ref`) | Per row, subject beside drawing: the first non-ground pixel from that side, and the dark runs inward from it. `--value NAMES` scans runs of those palette names instead of dark ones. Use it to measure a coordinate or a proportion. `<<` marks an edge off by more than 2% of the box. `runs a|b` marks a row whose line count differs: a thick line drawn as two, or an interior line drawn somewhere else |
| `--overlay` | The drawing blended over the subject. With `--box x,y,w,h`, it shows the two inks over that box: the subject's in blue, the drawing's in red, black where they coincide. `--value black` reads only the line; without it every dark flat, such as a glove or bar tape, shows as ink. On `blockin.png`, whose stock lines are too pale to read as line, pass `--dark 200`. It is the only view of interior lines (see above). It gives no number, on purpose |
| `--parts parts.json` (needs `--ref`) | A part that is absent, or has drifted out of its box. Each shape note is printed over its crop. `form` is the share of the box that differs from its own median grey. `off-ground` is the share unlike every colour round the box (a fence on a road beside a field stands on two grounds, both read off the picture). MISSING? needs both to be low. It says whether the part is there, never whether it is recognisable (only a describer on the assembled picture says that). At S2, every feature whose marks wait for S3 reads MISSING?, which is expected at that stage and not a fault |
| `--checklist parts.json` | A sub-form that a reference's checklist names for an object in the inventory, with no entry and no reason in `_absent`. `build.sh` runs it, and a failure blocks the build. It warns when no reference object matched any key, which means its PASS checked nothing |
| `--counts parts.json` (needs `--ref`) | A group of repeated forms that was culled, merged or added to, where the subject itself can be counted. Exit 1 is FAIL; exit 2 means UNCHECKED rows |
| `--colour parts.json` or `--colour x,y,w,h` (needs `--ref`) | A part whose colour has drifted. Per box, at the subject's size:  the median hue, saturation and value of the object's own pixels, and `mid`, the saturation of the most saturated tenth of its mid-tones. **What counts as the object's pixels:** line is left out, meaning a run darker than `--ink` (default 60) and no wider than `--line` (default the subject's longer side / 200, at least 6). So a dark flat such as a roof, a timber band or a black coat is read as colour however dark it is. `INK=` and `LINE=` set both for `gates.sh`. In the drawing, the ground is `--ground` (default palette.json's `background`). In the subject, the object is the colour clusters that are nearer, in hue and chroma, to the drawn object's colours than to that ground, so the shade and grass round a photographed part are left out. **Flags:** `<<` when hue is more than 15° off, median saturation a third or more lower, `mid` a fifth or more lower (a starting figure), or value more than 0.15 off. A low `mid` with matching medians means the palette was sampled as an average: the light and the shadow match, and the saturated step between them has gone beige. Small or mostly dark boxes (an eye, a nose, a tag) give noisy rows; read the large ones. **The stage 0 sample wins over a value flag.** The subject's median includes the dark between hairs or leaves and the side in shade, while an entry is sampled at the saturated mid-tone patch, so on fur or foliage the subject reads darker than a correctly sampled flat. Answer a value flag with the ramp's darker step (a shade flat, strands, hatching) where the subject is darker. Re-sample an entry only when the flagged box holds the patch it was sampled from. A row saying no subject colour is nearer the drawn object's than the ground means a flat drawn in a colour the subject does not have there. A box with too few colour pixels (line on bare ground) is shown and not counted. Run it on `drawing.png`; a `style.json` finish lowers saturation again in `final.png`. Exit 1 when a row is flagged |
| `--ranking parts.json` (needs `--ref`) | A part that stands out more than its `tier` allows (named when it outranks the whole focus tier), and two forms merged into one value. The only way to lift a part is to tone another down |
| `--doubled ops.json` | One edge stated twice on the page. It replays write order, `erase` and `back`. It does not list an edge a later flat buries, nor two lines that cross in an X, or meet in a V or a T, at 5° or more (crossing spokes, a chain over a spoke). It does list two lines that run side by side (two bands, parallel cables), and a contact between two objects' edges, so look before you merge |
| `--joins ops.json [--parts parts.json]` | A line that stops just short of the mark it runs towards, in the same object (the tag up to its first `.`). The gap is one to eight line widths, edge to edge, which reads as neither a join nor a separation: a chain short of its sprocket, a spoke short of its rim, a ring left open. Ends that some mark touches pass, and so does a styled hand's 1–4px fall-short. These are not join targets: marks beside the end (a hatch group's next line), a hairline under half the end's width, and marks with the end's own tag. List a pair meant to stop short in parts.json's `"_gaps": ["tagA/tagB", ...]`, matched by tag prefix. Exit 1 when anything is listed |
| `--depth ops.json parts.json` | An occlusion the inventory decided that the write order does not deliver: the far form's ink written after the near form's fill, so it is drawn across it. **UNRESOLVED** is not a pass; it means the tags and the inventory do not use the same names. **UNLISTED** is a list to work through: one part's ink shown across another's flat where no row decides which is in front. It warns on a key written `near/far`. A row with `"in_front": "same"` (sub-forms of one surface) has no order to check |
| `--stages ops.json` | A stage that does not exist, and a mark the script did not write itself: called from another file, stamped by a loop or an import, or with points loaded or computed. It does not check that each ink mark has a contour under it. Pasted generated literals pass it |
| `--faces ops.json` | A flat simpler than the traced region it overlaps: a shade drawn as a four-sided shape on a form with twenty-five corners looks like a patch stuck on. Pass the object's own trace as `--regions`. On an upscaled or generated subject, also pass `--grain` of three times the upscale factor, or the jagged edge reads as corners (in one case 150 false rows without it, 4 with it). It still fails a deliberately straight form cut by intruding objects, and a silhouette flat whose region is punched by holes (vents written over a shell). Adding corners is the wrong fix in both cases |
| `--unfilled --paper C` (needs `--ref`) | Bare paper where the subject has the object: a flat that stops short of its own ink, most often along an open edge that `--registration` cannot see. The object is read off the subject's ground (`palette.json`), and bare paper off `--paper`. Render a check copy with `background` set to a colour nothing else uses, and pass that |
| `--registration` | Colour and line disagreeing. Not usable on a full-bleed picture, where every band that runs off the frame is reported as a spill |
| `--zoom x,y,w,h` | Whether the marks are any good, at 4x, with ticks in whole-picture coordinates. **The primary gate on any object.** Three versions of one object passed every numeric gate yet ranged from a beetle to something a blind viewer named at once; only the magnified pair told them apart. The ticks are for orientation, not for reading coordinates (`look.py grid` places a point; `look.py probe` and `edge` confirm it) |
| a blind viewer on a part's crop | What the part is. The only gate that fails a shapeless blob. It detects a problem but does not measure how good the part is |
| `--weights rows` | The line hierarchy against the subject's, each run as `width@centre` |
| `subject.png --hatch x,y,w,h [--ref drawing.png]` | The line marks in a box, flats left out. It reports coverage, and for each group of parallel marks its angle, spacing, length and width. With `--ref`, it shows the drawing's box beside it and marks `<<` on a missing group, an angle more than 20° off, spacing off by more than half, or coverage under half. It FAILs (exit 1) on a group whose marks are over 1.6× the subject's width, or over 1.6× its share of the outline's weight (outline = 95th-percentile line over the picture). Widths are read at half each mark's darkness, in the subject's pixels whatever the render's size. `--light` reads pale lines on a dark ground. **WARN grain** when the marks are short (median under 3 × `--line`) and fade under a light blur: that is photo grain, fur or a dot screen, not hatching. It reports numbers and where the hatching is; it never supplies strokes |
| `--linework parts.json` (needs `--ref`) | Three faults. Hatching left out: FAIL where an entry's `hatch` angle has no line group within 20° in the drawing's box. Hatching too heavy: FAIL where that group's marks are over 1.6× the subject's width, or its hatch/outline ratio is over 1.6× the subject's (both printed per entry; outline = 95th-percentile line over the inventory's boxes). A flattened weight hierarchy: FAIL where the drawing's span (heaviest over finest line, 95th over 10th percentile on the marks' centre lines) is under half the subject's. A FAIL in a box whose lines run wider than `--line` adds a hint: an edge heavier than `--line` reads as a flat, so a narrow part between two such edges loses its hatching; thin the edge first. Exit 1 is FAIL; 2 is UNCHECKED (the written angle does not reproduce on the subject) |

Treat every number as a list of things to check, never as a score. Adding marks
moves a mark-counting number cheaply, and a whole-picture pixel difference can
rise on a round that improved the drawing. The target is the
shape note and the acceptance list; a judge only says whether they are now true.

## Judging by eye

Use your eye to find problems, and a measurement to decide whether a mark moves.
For example, on one picture a head that looked 10% too large was 3% too wide,
and a chin that looked 70px low was 6px off. A person reading the same
thumbnails was right on half the items; a scan or an overlay settled each one.
A downsampled side-by-side also makes small drawn forms look bigger and blockier
than the subject's soft edges. So measure any complaint raised by eye (yours, a
critic's or a person's) on subject and drawing before any mark moves.

To judge a fault, never read a coordinate off a zoom's tick labels or a resized
grid crop. Both have produced faults that probing then refuted (a small opening
read as 50px high, two thin lines read as 20–40px off). Probe or scan the pixels instead (`look.py probe`, `look.py edge`,
`--scan`). Placing marks off `look.py grid` is allowed, as long as you then
confirm the points by probing or scanning (`reference/marks.md` § Reading
coordinates).

Measurements can mislead too: a row scan through a dark form misreads wherever a
paler form sits inside it, so look at what the scan actually crossed.
