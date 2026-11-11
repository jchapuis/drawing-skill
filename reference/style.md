# Style: making it look drawn by a person

The gates judge a clean tldraw render, which looks like vector art: flat
colour, an even ground, every line meeting exactly. A `style.json` beside
`draw.py` changes how your marks land and how the finished picture is rendered.
It never adds a mark. Without the file, nothing changes.

```json
{"medium": "watercolour+ink", "hand": 0.5, "finish": "clean",
 "handedness": "right", "paper": "cold-press", "scan": true, "seed": 11}
```

| key | values | what it changes |
|---|---|---|
| `medium` | `ink-pen`, `brush-pen`, `pencil`, `marker`, `watercolour+ink`, `gouache` | the default instrument in `pen.py` (an explicit `tool=` wins), and how `finish.py` puts colour and line on the paper |
| `hand` | 0 (tight) to 1 (loose); default 0.5 | how much the pen wanders: drift, overshoot, lines that stop 1–4px short of the line they meet, varying weight between marks, hooks at fast starts. Also lowers smoothing in the final render |
| `finish` | `clean`, `sketch` | `sketch` keeps the gesture, block-in and contour stages in the final picture as faint graphite |
| `handedness` | `right`, `left` | the direction each stroke is drawn in, so tapers and hooks fall where that hand puts them. The points do not move |
| `paper` | `none`, `smooth`, `cold-press`, `newsprint`, `sketchbook` | paper tint and grain, multiplied into everything |
| `scan` | `true`, `false` | a slight tilt, uneven light, sensor noise and a JPEG save |
| `renderer` | `tldraw` (default), `brush` | With `brush`, `brush.py` re-lays the marks of `ops.json` the way the medium would, as dabs along your points, into `brush.png`. Weight comes from pressure, edges from the paper, a fast stroke's tail goes dry, and flats are brushed inside their own outline. `finish.py` then works on `brush.png`. It adds no mark and keeps your stacking order |

With a `style.json`, `build.sh` also writes `final.png`, with the colour layer
shifted a pixel or two off the line as in a hand-coloured print. With
`"renderer": "brush"` it writes `brush.png` first. **Gates and the describer
always read `drawing.png`, never `final.png`.**

Part of a human look comes from what you draw, and no renderer can add it.
Decide these at stage 0 and write them in `reading.md`:

- **How many marks.** An experienced artist draws a contour once, with weight
  where it matters, and lets some edges get lost. A sketch restates a key
  contour two or three times along its run, slightly apart. You write both.
- **How far to drift.** A person copying a subject simplifies it and strays from
  it by a few percent. With `hand` above 0.5, an outline scan within a few
  percent of the subject passes. Do not correct it back toward a trace.
- **Colour against line.** In `finish: sketch` a flat may stop short of its
  line or run a little past it, and the rule against spill in
  `reference/colour.md` does not apply. In `clean`, it does.
- **Hatching** follows the subject's measured angle where it has one. Where you
  add hatching the subject does not dictate, slant it by `handedness`: `/`
  for right, `\` for left.
