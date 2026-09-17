#!/bin/bash
# The blind describer. One image, a fresh process that has seen no script, no
# subject and no notes, five fixed questions; the answer is saved beside the
# image as <image>.describe.md so the gate leaves a file.
#
#   describe.sh subject.png      # at stage 0: the answers the drawing must earn
#   describe.sh gesture.png      # gate on stage 1: does the same event read?
#   describe.sh drawing.png      # gate on stage 10: same question, final render
#
# To describe a part, crop it to its own PNG first and describe that. Never
# hand it a sheet that also shows the subject: then it is not blind.
set -e
IMAGE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="${IMAGE%.*}.describe.md"
claude -p "Use the Read tool to look at exactly one file: $IMAGE. Do not read anything else.
You are describing a picture to someone who cannot see it. Report only what is visible.
Do not judge quality, do not say whether anything is wrong, do not comment on style,
do not guess how it was made. If you cannot tell, say 'cannot tell'.
Answer each in one to three plain sentences:
1. What is this a picture of, and what does the eye land on first?
2. What is the big shape of the main subject — one or two simple forms?
3. What is every figure or animal physically doing? Standing, seated, riding, leaning, looking where, hands on what, feet on what.
4. What touches what? Name each contact between the main subject and the things around it.
5. What does the main face express?" --model sonnet --allowedTools Read > "$OUT"
cat "$OUT"
