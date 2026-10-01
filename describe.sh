#!/bin/bash
# The blind describer. It takes one image and answers five fixed questions in a
# fresh process that has seen no script, no subject and no notes. The answer is
# saved beside the image as <image>.describe.md, so the gate leaves a file.
#
#   describe.sh subject.png      # at stage 0: the answers the drawing must earn
#   describe.sh gesture.png      # gate on stage 1: does the same action read?
#   describe.sh drawing.png      # gate on stage 10: same question, final render
#   describe.sh drawing.png B    # a second run, kept as drawing.describe.B.md
#
# A gate runs the describer twice and keeps what both runs say. Name the second
# run (the B above), because each image has one output file and an unnamed
# second run would overwrite the first.
#
# An answer is accepted only if it answers all five questions. The CLI can exit
# 0 with its own error text (a session limit, a refusal), and that text must not
# be saved as the image's description. A rejected answer is kept as <out>.err,
# the call is retried once, and the script exits 1 with no .describe file.
#
# To describe a part, crop it to its own PNG first and describe that. Never
# hand it a sheet that also shows the subject: then it is not blind.
#
# The describer normally answers in about 20s. When it hangs it gives no sign
# and blocks the whole run, so every call is capped and retried once. `timeout`
# is not on macOS, so the cap uses perl's alarm. Override it with
# DESCRIBE_TIMEOUT.
set -e
IMAGE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="${IMAGE%.*}.describe${2:+.$2}.md"
TIMEOUT="${DESCRIBE_TIMEOUT:-180}"
PROMPT="Use the Read tool to look at exactly one file: $IMAGE. Do not read anything else.
You are describing a picture to someone who cannot see it. Report only what is visible.
Do not judge quality, do not say whether anything is wrong, do not comment on style,
do not guess how it was made. If you cannot tell, say 'cannot tell'.
Answer each in one to three plain sentences:
1. What is this a picture of, and what does the eye land on first?
2. What is the big shape of the main subject — one or two simple forms?
3. What is every figure or animal physically doing? Standing, seated, riding, leaning, looking where, hands on what, feet on what.
4. What touches what? Name each contact between the main subject and the things around it.
5. What does the main face express?"

ask() {
  perl -e 'alarm shift; exec @ARGV or exit 127' "$TIMEOUT" \
    claude -p "$PROMPT" --model sonnet --allowedTools Read
}

# an answer has all five numbered answers; anything else is the CLI talking
answered() { [ "$(grep -cE '^[[:space:]*#]*(\*\*)?[1-5][.)]' "$1")" -ge 5 ]; }

TMP="$OUT.tmp"
for attempt in 1 2; do
  # the CLI's warnings go to stderr and stay out of the answer file
  if ask > "$TMP" 2>"$TMP.stderr" && answered "$TMP"; then
    rm -f "$TMP.stderr"
    mv "$TMP" "$OUT"
    cat "$OUT"
    exit 0
  fi
  cat "$TMP.stderr" >> "$TMP" 2>/dev/null; rm -f "$TMP.stderr"
  mv "$TMP" "$OUT.err"
  echo "describe.sh: attempt $attempt gave no five answers (kept in $OUT.err):" >&2
  head -3 "$OUT.err" >&2
done
rm -f "$OUT"
exit 1
