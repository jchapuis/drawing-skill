# Continuous tone, as marks

`light.md` covers the physics: the zones, the two families, where the terminator
falls, and why reflected light stays inside the shadow family. This file covers
the craft: how to make a tonal step out of marks a hand can lay, on a canvas
whose only verb is `stroke`.

It is needed because naming every zone on a sphere does not tell you how to get
one onto paper. In a test drawing with no ink line, the halftones came back,
in a blind describer's words, as **"parallel ridges"**.

## The stripe failure, and the rule that fixes it

Laying a translucent band across a form to darken it does not darken the form.
It puts a band on it.

> **A band narrow enough to show both of its own edges reads as a stripe lying
> on the form, not as the form turning. One of its edges must be hidden inside
> the mass it runs into.**

That is the difference between shading and striping, and it is why hatching
works. A hatch group has a hard outer boundary where it starts and a ragged inner
one where the strokes run out at different lengths, so only one edge is ever
visible as an edge. A rectangle of translucent grey has four.

What to do:

- **Anchor every tonal pass in an existing dark.** Start the stroke inside the
  core shadow, or inside the neighbouring form's shadow, and run it out into the
  light. The end that begins in darkness has no edge.
- **Never leave both ends free.** A stroke that starts and stops in the middle of
  a lit passage is a mark, and it will be read as one.
- **Vary the run-out.** If every stroke in a group stops at the same distance,
  the stroke ends rebuild the second edge.

This rule is a working explanation of why tonal bands look striped. It is the
best account so far and has not been proved.

How to measure a subject's hatch groups and write them as single strokes, and
how to keep that affordable, is in `line.md` § Hatching and texture.

## The instrument decides whether tone can accumulate

`pen.py` provides five instruments, and only some of them build tone:

| Instrument | Behaviour under overlap | Use for tone? |
|---|---|---|
| `marker` | translucent, overlaps darken | **Yes**: this is the hatching instrument |
| `crayon` | broken, grainy, three offset passes per call | **Yes**, for texture and for the grainiest darks |
| `brush` | opaque, swings thin to thick | For contour and for a deliberate single dark, not for building |
| `pen` | opaque, dead uniform | No |
| `flat` | opaque region | The mass itself, never the modelling on it |

Tone accumulates only where the instrument is translucent. With an opaque one
you are not shading. You are drawing a shape whose colour happens to be grey, and
a shape needs an outline, which brings back the stripe failure.

## Choose the value steps before the first mark

The palette holds as many named colours as you give it, so no step has to be
merged away. But every step is a flat with an edge, and an opaque flat cannot
blend into its neighbour. **A step left out becomes a spacing problem**: with no
flat between a surface's own value and its highlight, the only way left to make
a gradient is to change how densely the marks sit. That works, but badly: the
falloff comes out shallower than the subject's. A step added that the subject
does not have is a band no one can explain.

So decide the steps deliberately, before the first mark:

1. Count the distinct values the *subject* needs. Squint at it. The count is
   smaller than it looks, usually five or six per object.
2. Give the **shadow family** at least two steps and the **light family** at
   least two. With one each, the picture goes flat when squinted.
3. Keep one step for the **accent**: the single saturated or extreme value the
   picture turns on, used on one small area that carries the action.
4. Add the transitions you cannot make by spacing, each as its own name.

## Texture cannot be cut into a path

A jagged outline is not texture. `smooth=False` has an **amplitude floor**. In one
test, a 24-point path with ±5px teeth came back from the renderer as a smooth
circle, because the densifier and the hand model together iron out deviations
below roughly the stroke's own width. The teeth were smaller than the pen.

**Texture is made of marks, not of a wiggly boundary.** A granular edge is a
dozen short strokes crossing the boundary, some over it and some short of it. A
woven or grained surface is its own strokes at its own spacing. If you find
yourself adding points to a contour to make something look rough, stop. You will
get a smooth line with more points in it.

## Order

1. **Two families first, as flats**, with a real gap between them and no
   modelling at all. Squint: if the picture does not read at this stage, no
   amount of tone will fix it.
2. **The terminator**, placed as a shape. It is a *shape* on the form and not a
   line, and where it runs says which way the form turns.
3. **The core shadow**: the darkest band, sitting just inside the terminator on
   the shadow side, not at the form's edge.
4. **Reflected light**, kept inside the shadow family. The most common way to
   ruin a drawing at this stage is to make it lighter than the darkest halftone
   in the light family. The two families then overlap and everything goes muddy.
5. **Halftones in the light family**, anchored per the rule above.
6. **The accent** last, and once.

Cast shadows belong to the shadow family and follow the same order. A cast shadow
has a hard edge near the object casting it and a soft one far away. Drawing it at
one edge character throughout makes it read as a sticker.
