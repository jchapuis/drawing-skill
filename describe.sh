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
# A usage or rate limit ("hit your session limit", "rate limit", 429) is not
# retried, since a retry hits the same limit: the script says so and exits 3,
# with no .describe file. Run at most 4 describes in parallel (xargs -P4); 19
# at once hit the session limit and every call failed.
#
# The describer is shown a copy of the image under a random name in a temp
# directory, never the image's own path: a crop named head_comb.png told it
# "by its filename it may be a rooster's comb". The copy is removed afterwards,
# and the answer still lands beside the original. The CLI also runs from that
# directory, since it tells the model its working directory.
#
# To describe a part, crop it to its own PNG first and describe that. Never
# hand it a sheet that also shows the subject: then it is not blind.
#
# It runs with the Read tool only and no MCP servers (--strict-mcp-config):
# otherwise the CLI appends notes about connected services to the answer, and
# those notes pass the five-answer check and land in the saved file.
#
# The describer normally answers in about 20s. When it hangs it gives no sign
# and blocks the whole run, so every call is capped and retried once. `timeout`
# is not on macOS, so the cap uses perl's alarm. Override it with
# DESCRIBE_TIMEOUT.
set -e
IMAGE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="${IMAGE%.*}.describe${2:+.$2}.md"
TIMEOUT="${DESCRIBE_TIMEOUT:-180}"
BLIND="$(mktemp -d)"
trap 'rm -rf "$BLIND"' EXIT
EXT="${IMAGE##*.}"
SHOWN="$BLIND/$(LC_ALL=C tr -dc a-z0-9 < /dev/urandom | head -c 12).$EXT"
cp "$IMAGE" "$SHOWN"
PROMPT="Use the Read tool to look at exactly one file: $SHOWN. Do not read anything else.
You are describing a picture to someone who cannot see it. Report only what is visible.
Do not judge quality, do not say whether anything is wrong, do not comment on style,
do not guess how it was made. If you cannot tell, say 'cannot tell'.
Answer each in one to three plain sentences:
1. What is this a picture of, and what does the eye land on first?
2. What is the big shape of the main subject — one or two simple forms?
3. What is every figure or animal physically doing? Standing, seated, riding, leaning, looking where, hands on what, feet on what.
4. What touches what? Name each contact between the main subject and the things around it.
5. What does the main face express?"

# run from the temp directory: the CLI tells the model its working directory,
# and a run directory's name (drw-runs/rooster) leaks the subject as well
ask() (
  cd "$BLIND" && perl -e 'alarm shift; exec @ARGV or exit 127' "$TIMEOUT" \
    claude -p "$PROMPT" --model sonnet --tools Read --allowedTools Read --strict-mcp-config
)

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
  if grep -qiE "hit your [a-z ]*limit|usage limit|rate.?limit|\b429\b" "$OUT.err"; then
    echo "describe.sh: the CLI hit a usage or rate limit (kept in $OUT.err), so it is not" >&2
    echo "retried. Wait for the limit to reset, then rerun. Run at most 4 describes in" >&2
    echo "parallel (e.g. xargs -P4)." >&2
    head -3 "$OUT.err" >&2
    rm -f "$OUT"
    exit 3
  fi
  echo "describe.sh: attempt $attempt gave no five answers (kept in $OUT.err):" >&2
  head -3 "$OUT.err" >&2
done
rm -f "$OUT"
exit 1
