# Continuous tone, as marks

`light.md` is the physics — the zones, the two families, where the terminator
falls, why reflected light stays inside the shadow family. This is the craft:
how to *make* a tonal step out of marks a hand can lay, on a canvas whose only
verb is `stroke`.

It exists because the first drawing with no ink line in it found the gap
immediately. The skill could name every zone on a sphere and said nothing about
how to get one onto paper, and the halftones came back reading — a blind
describer's words — as **"parallel ridges"**.

## The stripe failure, and the rule that fixes it

Laying a translucent band across a form to darken it does not darken the form.
It puts a band on it.

> **A band narrow enough to show both of its own edges reads as a stripe lying
> on the form, not as the form turning. One of its edges must be hidden inside
> the mass it runs into.**

That is the whole difference between shading and striping, and it is why
hatching works: a hatch group has a hard outer boundary where it starts and a
ragged inner one where the strokes run out at different lengths, so only one
edge is ever visible as an edge. A rectangle of translucent grey has four.

Consequences:

- **Anchor every tonal pass in an existing dark.** Start the stroke inside the
  core shadow, or inside the neighbouring form's shadow, and run it out into the
  light. The end that begins in darkness has no edge.
- **Never both ends free.** A stroke that starts and stops in the middle of a lit
  passage is a mark, and it will be read as one.
- **Vary the run-out.** If every stroke in a group stops at the same distance,
  you have rebuilt the second edge out of stroke ends.

This rule was invented against a wall, on the third attempt, and the drawing it
came from **still shows the fault**. It is stated here because it is the best
account so far of why, not because it has been proved.

## The instrument decides whether tone can accumulate

`pen.py` gives five, and only some of them build tone at all:

| Instrument | Behaviour under overlap | Use for tone? |
|---|---|---|
| `marker` | translucent, overlaps darken | **Yes** — this is the hatching instrument |
| `crayon` | broken, grainy, three offset passes per call | **Yes** — for texture and for the grainiest darks |
| `brush` | opaque, swings thin to thick | For contour and for a deliberate single dark, not for building |
| `pen` | opaque, dead uniform | No |
| `flat` | opaque region | The mass itself, never the modelling on it |

Tone accumulates only where the instrument is translucent. With an opaque one
you are not shading, you are drawing a shape whose colour happens to be grey —
and a shape needs an outline, which is the stripe failure again.

## Value count is a hard constraint, and it is thirteen

The palette has thirteen slots and the ground is not one of them. On a subject
with real continuous tone that runs out fast, and when it does, **the missing
step becomes a spacing problem**: with no slot between a surface's own value and
its highlight, the only way left to make a gradient is to change how densely the
marks sit. That works, badly — the falloff comes out shallower than the
subject's, which is exactly what happened to the mat.

So spend the slots deliberately, before the first mark:

1. Count the distinct values the *subject* actually needs. Squint at it: the
   count is smaller than it looks, usually five or six.
2. Give the **shadow family** at least two slots and the **light family** at
   least two. One each and the picture goes flat the moment it is squinted.
3. Reserve one slot for the **accent** — the single saturated or extreme value
   the picture turns on — one small area of it, carrying the whole event.
4. Whatever is left goes to the transitions you cannot make by spacing.

## Texture cannot be cut into a path

A jagged outline is not texture. `smooth=False` has an **amplitude floor**: a
24-point path with ±5px teeth came back from the renderer as a smooth circle,
because the densifier and the hand model between them iron out deviations below
roughly the stroke's own width. The teeth were smaller than the pen.

**Texture is made of marks, not of a wiggly boundary.** A granular edge is a
dozen short strokes crossing the boundary, some over and some short of it. A
woven or grained surface is its own strokes at its own pitch. If you find
yourself adding points to a contour to make something look rough, stop — you are
about to get a smooth line with more points in it.

## Order

1. **Two families first, as flats**, with a real gap between them and no
   modelling at all. Squint: if the picture does not read at this stage, no
   amount of tone will save it.
2. **The terminator**, placed as a shape. It is a *shape* on the form, not a
   line, and where it runs is what says which way the form turns.
3. **The core shadow** — the darkest band, sitting just inside the terminator on
   the shadow side, not at the form's edge.
4. **Reflected light**, and it stays inside the shadow family. The most common
   way to destroy a drawing at this stage is to make it lighter than the darkest
   halftone in the light family; then the two families overlap and everything
   goes muddy.
5. **Halftones in the light family**, anchored per the rule above.
6. **The accent** last, and once.

Cast shadows belong to the shadow family and follow the same order — but a cast
shadow has a hard edge near the object casting it and a soft one far away, and
drawing it at one edge character throughout is what makes it read as a sticker.
