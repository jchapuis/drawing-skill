# drawing

A Claude Code skill for **drawing** — not generating. The agent chooses every mark:
it reads the subject in writing, blocks it in with straights it can measure, gates
each stage on a render it has to look at, and only then commits to curve, ink and
black. No image model is involved at any point.

## What is here

| | |
|---|---|
| `SKILL.md` | The procedure: the object ladder and, wrapped round it, the scene ladder — what each stage produces and the command that gates it |
| `reference/` | `method.md` is the full method with the measured failure behind each rule. The rest is depth loaded per task — `head`, `figure`, `scene`, `bicycle`, `quadruped`, `hands-and-feet` for subjects; `measuring`, `line`, `colour`, `tone`, `light`, `correcting` for craft; `redrawing` for a generated image as subject |
| `pen.py` | The instrument. One verb, `stroke`: you choose the control points, it supplies the hand — speed follows curvature, pressure follows speed, nothing repeats. `write` audits the ladder and refuses ink in a drawing that has no gesture, block-in and contour stage, and refuses marks the script did not write: strokes generated in another file, stamped by a loop, or whose points were loaded or computed |
| `trace.py` | The measuring instrument for a flat-cel subject: every region's outline, as straights and as a curve, in the subject's own coordinates or offset into the panel's. It measures; it never writes a mark |
| `describe.sh` | The blind describer: a fresh process that has seen no script, five fixed questions, the answer saved beside the image. The gate on the picture's event |
| `check.py` | The instruments that look back at what you drew: masses, parts, census, ranking, zoom, weights, overlay (and, over a box, the two inks in two colours), `scan` (outline and interior lines row by row, subject beside drawing), registration, unfilled, `doubled` (one edge stated twice on the page), `depth` (write order against the inventory, and overlaps nobody decided) and `ladder` (a stage that does not exist, or a mark the script did not write) |
| `crop.py` | Cuts one object's measuring crop out of the working-resolution subject, at 1:1, and stores its panel corner in the PNG so its trace comes back in panel coordinates |
| `build.sh` | Runs `draw.py`, audits it, and renders every stage's look beside the final one |
| `harness/` | A tldraw canvas driven from the command line. The document on disk *is* the drawing, and it opens in tldraw afterwards for a human to edit |

## Installing

```bash
git clone https://github.com/jchapuis/drawing-skill ~/.claude/skills/drawing
cd ~/.claude/skills/drawing/harness && npm install && npm run build && npx playwright install chromium
```

Python needs `numpy`, `scipy`, `pillow` and `opencv-python`; `describe.sh` needs
the `claude` CLI. Drop it in a project's `.claude/skills/` instead if you want it
per-repo.

## Using it

The drawing is a flat script — one mark per line, with its own literal numbers,
because a shape a function generates is identical to its siblings and reads as
plotted rather than drawn. Tools measure; only the script draws, and a scene is
one script in one coordinate space.

```bash
python3 trace.py subject.png palette.json --png regions.png   # measure the subject once
./describe.sh subject.png                                     # the event the drawing must earn
python3 crop.py subject.png 200,560,460,540 meas/bike.png      # an object's measuring crop, corner stored in it
./build.sh                                                    # draw.py -> ops.json -> gesture/blockin/contour/drawing.png
./describe.sh drawing.png                                     # the same question of the render
python3 check.py drawing.png --ref subject.png --zoom 78,150,166,95 --out eyes.png
python3 check.py drawing.png --ref subject.png --scan 78,150,166,95 --side right   # the numbers behind a look
```

## Two conventions worth knowing before you edit it

**The reference layer is diagnostics, never scaffolds.** The test is mechanical: if
a passage could be followed with the subject covered up, it is a scaffold, and it
hands the drawer a generic form at the stage whose whole job is to find the
particular one. Rewrite it as what to measure and what a departure from the average
means.

**Every claim carries its provenance.** `[bought: drawing]` marks a rule paid for by
a specific failure and the measurement that caught it; `[read: source]` marks a
hypothesis with good pedigree and nothing more. A rule leaves this layer when a
drawing shows it wrong.

## Licence

MIT — see [LICENSE](LICENSE).
