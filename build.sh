#!/bin/bash
# Build one drawing: run draw.py, audit the stages and the authorship, and
# render every stage's look beside the final one. One document, one script.
# Copy this next to the drawing and set SKILL.
#
#   ./build.sh            # writes gesture.png blockin.png contour.png drawing.png
#   ./build.sh --flip     # extra flags go to every render
#   STAGE=blockin ./build.sh   # only the stages up to block-in
#
# STAGE=<name> cuts the build at that stage, so one draw.py can be gated stage
# by stage: every mark of a later stage is dropped from ops.json before any
# render, and only the renders that stage reaches are made (the rest are
# removed, so a stale one is never judged). The order is gesture, blockin,
# construction, fill, contour, ink, correct. The authorship audit still reads
# the whole script. Unset, everything is drawn.
set -e
cd "$(dirname "$0")"
SKILL="${SKILL:-$(dirname "$(readlink -f "$0")")}"
[ -f "$SKILL/check.py" ] || { echo "build.sh: no check.py in $SKILL -- a copied build.sh must have SKILL= set to the skill directory" >&2; exit 1; }
export PYTHONPATH="$SKILL${PYTHONPATH:+:$PYTHONPATH}"   # so draw.py can `from pen import ...`
DOC=doc.json

# the inventory must name every sub-form its references' checklist lists, or say
# why not. The build stops until it does
[ ! -f parts.json ] || python3 "$SKILL/check.py" drawing.png --checklist parts.json
python3 draw.py                                    # your script; writes ops.json
python3 "$SKILL/check.py" drawing.png --stages ops.json 2>/dev/null || true
# the reach of the build: how far along the stage order STAGE is, 6 when unset
REACH=$(python3 - "${STAGE:-}" <<'PY'
import json, sys
order = ("gesture", "blockin", "construction", "fill", "contour", "ink", "correct")
cut = sys.argv[1]
if not cut:
    print(len(order) - 1)
    sys.exit()
if cut not in order:
    sys.exit(f"build.sh: STAGE={cut} is not a stage. The stages are: {', '.join(order)}")
reach = order.index(cut)
ops = json.load(open("ops.json"))
unknown = sorted({op.get("stage", "ink") for op in ops} - set(order) - {"frame"})
if unknown:
    sys.exit(f"build.sh: ops carry stage {', '.join(unknown)}, which STAGE= cannot place")
# a stroke without a stage is ink, as pen.audit reads it; a fade, erase or
# back acts on the stage it names and goes with it
kept = [op for op in ops if op.get("stage", "ink") == "frame"
        or order.index(op.get("stage", "ink")) <= reach]
json.dump(kept, open("ops.json", "w"))
print(f"build.sh: STAGE={cut} kept {len(kept)} of {len(ops)} ops in ops.json", file=sys.stderr)
print(reach)
PY
)
# reach: 0 gesture, 1 blockin, 3 fill, 5 ink
stale() { rm -f "$@"; echo "build.sh: STAGE=$STAGE does not reach $*; removed" >&2; }
render() { rm -f "$DOC"; node "$SKILL/harness/cli.mjs" "$DOC" --ops "$1" --png "$2" --padding 0 "${@:3}"; }
# the stage looks are drawn from the ops with every erase/fade taken out, so
# cleanup does not change them. They use stock colours (`--stock`), because an
# older palette that repoints stock names can map a stage's default colour to
# the ground and blank it. The palette is still read, for the names the later
# stages' marks carry
python3 -c "import json; json.dump([o for o in json.load(open('ops.json')) if o.get('op') not in ('erase', 'fade')], open('stages.json', 'w'))"
STOCK_LOOK=()
[ ! -f palette.json ] || STOCK_LOOK=(--palette palette.json --stock)
render stages.json gesture.png --only gesture,frame "${STOCK_LOOK[@]}" "$@"
if [ "$REACH" -ge 1 ]; then render stages.json blockin.png --only gesture,blockin,frame "${STOCK_LOOK[@]}" "$@"; else stale blockin.png; fi
if [ "$REACH" -ge 3 ]; then
  render stages.json contour.png --only blockin,contour,fill,frame --palette palette.json "$@"
else stale contour.png; fi
# drawing.png never shows the scaffolding. The stages do not say to erase
# construction or contour, and left-over gesture loops would read as mass
if [ "$REACH" -lt 5 ]; then
  stale drawing.png colour-offset.png construction.png final.png
  exit 0
fi
render ops.json drawing.png --hide gesture,construction,blockin,contour --palette palette.json "$@"

# With a style.json beside draw.py, also make final.png: the drawing as a medium
# on paper, scanned. It is for looking at, never for a gate. The renders above
# are untouched by it. Two more renders feed it: the colour put a hand's slip
# off the line (`--offset`), and, for a sketch finish, the construction alone,
# which finish.py lays under the picture as faint graphite
if [ -f style.json ]; then
  # read with python, because jq may be missing; finish.read_style stops on a bad value
  SETTINGS=$(python3 - <<'PY'
import random
from finish import read_style
style = read_style("style.json")
hand = float(style.get("hand", 0.5))
pick = random.Random(style["seed"])
# a 1-3px slip, larger for a looser hand, in a direction fixed by the seed
dx, dy = (pick.choice((-1, 1)) * round(1 + 2 * hand * pick.uniform(0.5, 1), 1) for _ in range(2))
# a looser hand keeps more of the stroke's small movements
print(dx, dy, round(0.62 - 0.4 * hand, 2), int(style["finish"] == "sketch"))
PY
)
  read -r DX DY STREAMLINE SKETCH <<< "$SETTINGS"
  render ops.json colour-offset.png --hide gesture,construction,blockin,contour --palette palette.json \
    --offset "fill:$DX,$DY" --streamline "$STREAMLINE" "$@"
  CONSTRUCTION=()
  if [ "$SKETCH" = 1 ]; then
    render stages.json construction.png --only gesture,blockin,construction,contour,frame \
      --palette palette.json --streamline "$STREAMLINE" "$@"
    CONSTRUCTION=(--construction construction.png)
  fi
  python3 "$SKILL/finish.py" --style style.json --drawing colour-offset.png "${CONSTRUCTION[@]}" --out final.png
fi
