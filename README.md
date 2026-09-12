# drawing

A Claude Code skill for **drawing** — not generating. The agent chooses every mark:
it reads the subject in writing, blocks it in with straights it can measure, gates
each stage on a render it has to look at, and only then commits to curve, ink and
black. No image model is involved at any point.

## What is here

| | |
|---|---|
| `SKILL.md` | The method: the principles, the ten stages and their gates, the checks, and the failure modes each one catches |
| `reference/` | Depth loaded per task — `head`, `figure`, `scene`, `bicycle`, `quadruped`, `hands-and-feet` for subjects; `measuring`, `line`, `colour`, `tone`, `light`, `correcting` for craft |
| `pen.py` | The instrument. One verb, `stroke`: you choose the control points, it supplies the hand — speed follows curvature, pressure follows speed, nothing repeats |
| `check.py` | The instruments that look back at what you drew: masses, parts, zoom, weights, overlay, registration |
| `harness/` | A tldraw canvas driven from the command line. The document on disk *is* the drawing, and it opens in tldraw afterwards for a human to edit |

## Installing

```bash
git clone https://github.com/jchapuis/drawing-skill ~/.claude/skills/drawing
cd ~/.claude/skills/drawing/harness && npm install && npm run build && npx playwright install chromium
```

Python needs `numpy`, `scipy` and `pillow`. Drop it in a project's
`.claude/skills/` instead if you want it per-repo.

## Using it

The drawing is a flat script — one mark per line, with its own literal numbers,
because a shape a function generates is identical to its siblings and reads as
plotted rather than drawn.

```bash
python3 paint.py contour                         # your script writes ops.json
node harness/cli.mjs doc.json --ops ops.json --png look.png --padding 0
python3 check.py look.png --ref subject.png --zoom 78,150,166,95 --out eyes.png
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
