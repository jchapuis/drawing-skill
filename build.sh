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
