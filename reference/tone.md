# Continuous tone, as marks

`light.md` covers the physics: the zones, the two value families, where the
terminator falls, and why reflected light stays in the shadow family. This file
covers the craft: how to build a tonal step out of marks a hand could lay, on a
canvas where the only operation is `stroke`.

## Contents

- The stripe failure, and the rule that fixes it
- The instrument decides whether tone can accumulate
- Choose the value steps before the first mark
- Texture cannot be cut into a path
- Order

Knowing the zones of a sphere does not tell you how to get them onto paper. In a
test drawing with no ink line, a blind describer called the halftones
**"parallel ridges"**.

## The stripe failure, and the rule that fixes it

A translucent band laid across a form does not darken the form. It puts a band
on it.

> **A band narrow enough to show both of its edges reads as a stripe lying on
> the form, not as the form turning. Hide one of its edges inside the mass it
> runs into.**

This is why hatching works. A hatch group has a hard outer boundary where the
strokes start and a ragged inner one where they run out at different lengths, so
only one edge reads as an edge. A rectangle of translucent grey has four.

- **Start every tonal pass in an existing dark**: inside the core shadow, or
  inside the neighbouring form's shadow, and run it out into the light. The end
  that begins in the dark shows no edge.
- **Never leave both ends free.** A stroke that starts and stops inside a lit
  area is read as a mark.
- **Vary where the strokes stop.** If they all stop at the same distance, their
  ends form a second edge.

This is the best explanation so far of why tonal bands look striped, but it has
not been proved.

How to measure a subject's hatch groups, write them as single strokes, and keep
that affordable is in `line.md` § Hatching and texture.

## The instrument decides whether tone can accumulate

`pen.py` provides five instruments, and only some of them build tone:

| Instrument | Behaviour under overlap | Use for tone? |
|---|---|---|
| `marker` | translucent, overlaps darken | **Yes**, for tone built by overlapping passes (glazes, soft gradients) |
| `crayon` | broken, grainy, three offset passes per call | **Yes**, for texture and for the grainiest darks |
| `brush` | opaque, swings thin to thick, tapers both ends | **The hatching instrument**: one tapered stroke per line, at the small sizes in `line.md` § Hatching and texture, tone from spacing rather than overlap. Also contour and a deliberate single dark |
| `pen` | opaque, dead uniform | No |
| `flat` | opaque region | The mass itself, never the modelling on it |

Tone builds up only with a translucent instrument. With an opaque one you are
drawing a grey shape, and a shape has an outline, which brings back the stripe
failure.

## Choose the value steps before the first mark

The palette can hold as many named colours as you like, so no step has to be
merged away. But each step is a flat with an edge, and an opaque flat cannot
blend into its neighbour. Leave a step out (say, no flat between a surface's own
value and its highlight) and the only way left to make the gradient is to vary
how densely the marks sit, which gives a shallower falloff than the subject's.
Add a step the subject does not have and it shows as an unexplained band.

So, before the first mark:

1. Count the distinct values the *subject* needs. Squint at it. There are fewer
   than it looks, usually five or six per object.
2. Give the **shadow family** at least two steps and the **light family** at
   least two. With one each, the picture goes flat when squinted.
3. Keep one step for the **accent**: the single most saturated or extreme value,
   on one small area where the action is.
4. Add each transition you cannot make by spacing as its own named colour.

## Texture cannot be cut into a path

A jagged outline does not make texture, because `smooth=False` cannot show
detail below a certain size. In one test, a 24-point path with ±5px teeth
rendered as a smooth circle: the densifier and the hand model together smooth out
deviations smaller than about the stroke's own width.

Make texture out of marks. A granular edge is a dozen short strokes crossing the
boundary, some past it and some short of it. A woven or grained surface is its
own strokes at its own spacing. If you find yourself adding points to a contour
to make it look rough, stop: you will get a smooth line with more points.

## Order

1. **The two families first, as flats**, with a clear gap in value between them
   and no modelling. Squint: if the picture does not read now, no tone will fix
   it.
2. **The terminator**, placed as a shape on the form, not a line. Where it runs
   shows which way the form turns.
3. **The core shadow**: the darkest band, just inside the terminator on the
   shadow side, not at the form's edge.
4. **Reflected light**, kept inside the shadow family. The most common way to
   ruin a drawing here is to make it lighter than the darkest halftone in the
   light family: the families then overlap and everything goes muddy.
5. **Halftones in the light family**, each started in a dark as above.
6. **The accent**, last and once.

Cast shadows belong to the shadow family and follow the same order. A cast
shadow is hard-edged near the object casting it and soft further away. With the
same edge all round, it looks like a sticker.
