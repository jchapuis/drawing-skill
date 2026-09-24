#!/bin/bash
# Build one drawing: run draw.py, audit the ladder and the authorship, and
# render every stage's look beside the final one. One document, one script.
# Copy this next to the drawing and set SKILL.
#
#   ./build.sh            # writes gesture.png blockin.png contour.png drawing.png
#   ./build.sh --flip     # extra flags go to every render
set -e
cd "$(dirname "$0")"
SKILL="${SKILL:-$(dirname "$(readlink -f "$0")")}"
export PYTHONPATH="$SKILL${PYTHONPATH:+:$PYTHONPATH}"   # so draw.py can `from pen import ...`
DOC=doc.json

python3 draw.py                                    # your script; writes ops.json
python3 "$SKILL/check.py" drawing.png --ladder ops.json 2>/dev/null || true
render() { rm -f "$DOC"; node "$SKILL/harness/cli.mjs" "$DOC" --ops "$1" --png "$2" --padding 0 "${@:3}"; }
# the stage looks are drawn from the ops with every erase/fade taken out, so
# they survive cleanup; and in stock colours, because a palette sampled off the
# subject can repoint a stage's default colour to the ground and blank the look
python3 -c "import json; json.dump([o for o in json.load(open('ops.json')) if o.get('op') not in ('erase', 'fade')], open('stages.json', 'w'))"
render stages.json gesture.png --only gesture,frame "$@"
render stages.json blockin.png --only gesture,blockin,frame "$@"
render stages.json contour.png --only blockin,contour,fill,frame --palette palette.json "$@"
# drawing.png never shows the scaffolding: nothing in the ladder said to erase
# construction or contour, and a masses gate read left-over gesture loops as mass
render ops.json drawing.png --hide gesture,construction,blockin,contour --palette palette.json "$@"
