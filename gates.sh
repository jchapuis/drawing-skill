#!/bin/bash
# Run every gate that applies to this drawing, and print one verdict line per
# gate. Copy this next to the drawing and set SKILL, like build.sh.
#
#   ./gates.sh            # after ./build.sh --scale 0.5
#   INK=40 LINE=10 ./gates.sh   # --colour's line: runs darker than INK (default
#                               # 60) and no wider than LINE px (default the
#                               # subject's longer side / 200, at least 6)
#
# It reads drawing.png, subject.png, parts.json, ops.json and palette.json from
# this directory and runs a gate only when the files it needs are there. Each
# gate's full output goes to gates/<gate>.txt (and an image gate's sheet to
# gates/<gate>.png); the verdict line quotes the first line that failed.
#
#   PASS       the gate passed
#   FAIL       the gate failed; exit 1
#   UNCHECKED  the gate could not measure some rows (--linework, --counts)
#   LOOK       an image or a ranking to read yourself; no verdict of its own
#   SKIP       a file the gate needs is missing, or nothing in parts.json asks for it
#
# Flags are written out one by one, never held in one string: zsh does not
# split a variable into words, so "--stages ops.json" in a variable reaches
# check.py as one argument.
cd "$(dirname "$0")"
SKILL="${SKILL:-$(dirname "$(readlink -f "$0")")}"
[ -f "$SKILL/check.py" ] || { echo "gates.sh: no check.py in $SKILL -- a copied gates.sh must have SKILL= set to the skill directory" >&2; exit 1; }
export PYTHONPATH="$SKILL${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p gates
FAILED=0

have() { for file in "$@"; do [ -f "$file" ] || return 1; done; }

# gate NAME FILE... -- CHECK-ARGS...: run check.py when every FILE exists
gate() {
  local name=$1; shift
  local needs=()
  while [ "$1" != "--" ]; do needs+=("$1"); shift; done
  shift
  if ! have "${needs[@]}"; then
    printf '  %-10s %-11s needs %s\n' SKIP "$name" "${needs[*]}"
    return
  fi
  python3 "$SKILL/check.py" "$@" > "gates/$name.txt" 2>&1
  local code=$? verdict first
  case "$name:$code" in
    parts:*|masses:*|ranking:*) verdict=LOOK ;;
    *:0) verdict=PASS ;;
    linework:2|counts:2) verdict=UNCHECKED ;;
    *) verdict=FAIL; FAILED=1 ;;
  esac
  # the lines that carry a finding: a row flagged by the gate, never its help text
  local found='^ *(FAIL|UNRESOLVED|NEAR MISS|HOLE|WARN)|[0-9-] +<< [a-z]| UNCHECKED'
  case "$name" in
    parts) first="$(grep -c 'MISSING?$' "gates/$name.txt") MISSING?; sheet in gates/parts*.png" ;;
    ranking) first="$(grep -c 'ABOVE ITS TIER:' "gates/$name.txt") ABOVE ITS TIER" ;;
    masses) first="gates/masses.png: say both shapes in words" ;;
    *) if [ "$name" = counts ] && grep -q "no entry carries a count" "gates/$name.txt"; then
         printf '  %-10s %-11s no entry in parts.json carries a count\n' SKIP "$name"; return
       fi
       if [ "$verdict" = PASS ]; then
         first=$(grep -m1 -E "PASSES|no ink yet|^ *WARN" "gates/$name.txt")
       else
         first="$(grep -cE "$found" "gates/$name.txt") flagged; first: $(grep -m1 -E "$found" "gates/$name.txt" | tr -s ' ' | sed 's/^ //')"
       fi ;;
  esac
  printf '  %-10s %-11s %s\n' "$verdict" "$name" "$(echo "$first" | sed 's/^ *//' | cut -c1-110)"
}

echo "gates on $(pwd) -- full output in gates/"
gate checklist parts.json -- drawing.png --checklist parts.json
gate stages    ops.json -- drawing.png --stages ops.json
gate doubled   ops.json -- drawing.png --doubled ops.json
if have parts.json; then
  gate joins   ops.json parts.json -- drawing.png --joins ops.json --parts parts.json
else
  gate joins   ops.json -- drawing.png --joins ops.json
fi
gate depth     ops.json parts.json -- drawing.png --depth ops.json parts.json
# unquoted on purpose: each expands to two words (flag, value) or to nothing
gate colour    drawing.png subject.png parts.json -- drawing.png --ref subject.png --colour parts.json ${INK:+--ink "$INK"} ${LINE:+--line "$LINE"}
gate linework  drawing.png subject.png parts.json -- drawing.png --ref subject.png --linework parts.json
gate counts    drawing.png subject.png parts.json palette.json -- drawing.png --ref subject.png --counts parts.json
gate ranking   drawing.png subject.png parts.json -- drawing.png --ref subject.png --ranking parts.json
gate parts     drawing.png subject.png parts.json -- drawing.png --ref subject.png --parts parts.json --out gates/parts.png
gate masses    drawing.png subject.png -- drawing.png --ref subject.png --masses --out gates/masses.png
exit $FAILED
