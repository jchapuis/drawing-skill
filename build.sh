#!/bin/bash
# Build one drawing: run draw.py, audit the stages and the authorship, and
# render every stage's look beside the final one. One document, one script.
# Copy this next to the drawing and set SKILL.
#
#   ./build.sh            # writes gesture.png blockin.png contour.png drawing.png
#   ./build.sh --flip     # extra flags go to every render
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
render() { rm -f "$DOC"; node "$SKILL/harness/cli.mjs" "$DOC" --ops "$1" --png "$2" --padding 0 "${@:3}"; }
# the stage looks are drawn from the ops with every erase/fade taken out, so
# cleanup does not change them. They use stock colours, because a palette sampled
# off the subject can map a stage's default colour to the ground and blank it
python3 -c "import json; json.dump([o for o in json.load(open('ops.json')) if o.get('op') not in ('erase', 'fade')], open('stages.json', 'w'))"
render stages.json gesture.png --only gesture,frame "$@"
render stages.json blockin.png --only gesture,blockin,frame "$@"
render stages.json contour.png --only blockin,contour,fill,frame --palette palette.json "$@"
# drawing.png never shows the scaffolding. The stages do not say to erase
# construction or contour, and left-over gesture loops would read as mass
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
