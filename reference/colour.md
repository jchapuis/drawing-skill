# Flat colour

Colour in cartoon work is not painting. It is **flatting**: breaking the drawing
into discrete regions of flat, unmodulated colour, then rendering on top of them.
In comics it is a separate job from colouring for exactly that reason — it is
mechanical, and it is done before any judgement about light.

## The pipeline

1. Closed line art.
2. **Flats** — one region per distinct surface, filled with flat colour. A face,
   a neck and a collar are three regions even when they end up the same colour.
3. **Colour assist** — the placeholder colours are nudged toward the real palette.
4. **Render** — light and shadow, using the flats as ready-made selections.

Flatting is deliberately dumb work. Its output is a *labelling system*, not a
preview: professional flatters pick throwaway colours chosen for maximum mutual
distinguishability so every region stays independently re-selectable later.
Accuracy is the next stage's problem.

## Trapping — the rule that matters most

**The fill extends underneath the line, never up to it.**

The flatter's central job is making the fills meet *under* the ink. If the black
plate shifts during printing, an underlapped fill only ever reveals more of the
correct colour — never bare paper. Stop the fill flush against the line and any
misregistration shows as a white gap.

From prepress, where this is quantified: **spread the lighter colour underneath
the darker one**. The eye reads shape from the dark edge, so extending the light
fill under it is invisible while the dark edge stays crisp. At 150 lpi the
standard trap is **1/150–1/300 inch (≈0.08–0.16 mm)**, and that width is
**multiplied by 1.5–2 when one of the two colours is black**, because black hides
misregistration more forgivingly.

The same structure is why black line art is usually **overprinted** rather than
knocked out: the dark element covers the seam, so no knockout-and-trap step is
needed at all.

Applied here: draw the flat generously past where the ink will go, put it behind
the ink, and let the line cover its edge. Cutting colour exactly to a line is
what no hand and no press does.

**A trap is only invisible where there is a line on top of it.** Wherever the ink
stops — most often at the edge of the frame, where a contour runs out of the
picture — the overhang stops being hidden and shows as a smear of colour beside
the drawing. Run those contours *past* the frame rather than ending them on it.

The same fact bites again wherever a line is **broken for something in front of
it**. A horizon behind a rider, a fence wire behind a post, a road edge behind a
wheel: the line is drawn in segments, and a flat cannot hide ink, so the segments
have to stop. **Each one must run *under* the thing it breaks for**, not up to
it. Ending a segment flush leaves a three or four pixel slot, and a slot is a
hole in the line art — colour pours through it, and one at a waist band was
enough to flood five hundred pixels of field. Overlap the occluder by more than
the segment could have missed by.

**And trap against where the line landed, not where it was sent.** The rule above
is proportional to the ink's width, which means it is measured off the render:
the same law as never retyping a coordinate from memory, applied to colour. A
flat set against the ink's intended path will be a pixel or two out along its
whole length, in whichever direction the stroke happened to lean.

**And the fill must not follow the line exactly.** Reusing the ink's own control
points, or offsetting them by a constant, is a press's behaviour, not a hand's:
it inherits every wobble the line has, so a lump in the contour becomes a lump in
the colour and the two errors reinforce instead of hiding each other. A hand
overruns here and falls short there. Give the fill **its own points** — the same
shape, stated independently, wandering either side of the line — and the ink then
covers the places it fell short while the places it overran read as a hand.

**How wide?** The prepress figures above are absolute because a press has a
fixed misregistration. A drawing does not: what has to be hidden is the gap
between a fill's edge and the *middle* of the line covering it, so **the trap is
about half the ink's own width, and it scales with the line.** A single trap
width applied across a drawing goes wrong at both ends — it stands clear of
every hairline and vanishes under every heavy contour. A 5px trap under a 4px
line is not a trap, it is a 5px band of colour lying beside the drawing.

## A band is not a body, and trapping one edits its width

Trapping offsets every vertex outward from the flat's own outline. On a **body**
— a form whose edge is its silhouette — that is exactly the intent. On a
**band** it is not: a strip, a rim inside a tyre, a hem, a strap, a shade along
a limb, any joint line thick enough to be a flat rather than a stroke. A band's
two long edges face outward in *opposite* directions, so both move apart and
**the band gains twice the trap in width** — and at a trap correctly sized to
half the ink, that is a whole ink width added to a measured quantity of the
form. It happens on every band in the drawing at once, in the direction that
makes them all fatter, and no gate reports it: the flats are present, filled,
registered and in their boxes.

Where two bands lie **concentric or parallel**, this is worse than an error in
either one, because **what makes the pair read is the ratio between them**, and
trapping does not preserve it — it adds the same absolute amount to both, so
the narrower band gains the larger share and the two converge. A wide band
beside a narrow one is a surface with an edge. The same two at equal width are
two stripes, and a viewer names the object differently.

So: trap a band's **ends**, where they tuck under something, and never its
length. Or draw the pair as one body flat in the wider band's colour, trapped
once on its outer silhouette, with the narrower band written over it as an
untrapped flat — then only the edge that is a silhouette is grown, and the edge
that is a *measurement* is left where you put it.

**The general form of the rule: trap an edge that is a silhouette; never trap
an edge that is a measurement.** A vent, an eye, a cast shadow, a shade and a
band all have edges of the second kind, and trapping them swells the interior
shapes until they eat the form.

**But the wander must never exceed the trap.** There is a hard line between the
two failures, and they look nothing alike:

| | reads as |
|---|---|
| Fill wanders *within* the ink's own width | a hand |
| Fill falls short of the line | a white gap — a mistake, every time |
| Fill spills past with no line over it | a smear — a mistake, every time |

So the independent points are an offset *inside* a trap wide enough to absorb
them: trap generously first, then let the fill wander by less than the trap. A
fill and a contour that visibly disagree is not looseness, it is the drawing
coming apart, and it is the first thing an eye lands on.

## A flat with a corner in it is not a curve

Most flats are cut to straight edges — a door, a wall, a floor, a photograph
pinned up, a panel of jersey. Sent as a smooth path, the spline through their
four corners leaves every one of them by a wide margin, because no interpolating
curve turns a right angle at a single vertex whose neighbours are far away. It is
not a trapping error and no trap covers it: the shape is simply not where its
points are, and a wall's base can bow a hundred pixels onto the floor.

Draw those flats with **straights** — the same `smooth=False` the block-in uses —
or plant a point on each side of every corner, close in. Reserve the smooth path
for shapes that really are curved all the way round.

## Hard edges only

Flats are **aliased, not anti-aliased**. Soft edges break clean re-selection for
the rendering stage and fringe in print. Binary alpha, hard boundaries.

## Layer order

Flat colour sits **beneath** the black line art, on its own layer or stage. This
is the same fact as trapping, seen from the layer stack rather than from the
fill — the line is on top precisely so it can cover the fill's imprecise edge.

## The line-off test

A concrete, runnable check from a working colorist: **hide the line art and see
whether the page still reads.** Foreground, middle ground and background should
separate, and the important elements should stay legible, on flat colour alone.
If the composition only holds because the line is doing the work, the colour
design has failed.

Run this at the flats stage, before any rendering.

## Cel shading on top

Hard-edged flat shadow shapes are the **default** in mainstream comic colouring,
not a stylised exception — one professional describes the overwhelming majority
of their rendering as cel shading with almost no effects.

The shadow goes down as **chunky simplified shapes, not gradients, and not
detail-following**. It must still obey a single consistent light direction and
describe the underlying form. The named failure modes are shading that flattens
the drawing, ignores the light source, or wrecks the forms.

Keep every shading shape an independent re-selectable region, the same way the
flats are — the rendering stage stays region-based rather than becoming freehand
painting.

## Choosing the shadow colour

A shadow is **three changes at once**, never a value drop alone: darker, less
saturated, and shifted in hue. Colourists' shadow colours are consistently
described that way — the hue always moves at least slightly, which is what
produces the warm/cool dynamic that makes flat colour read as lit.

**The hue shift has a physical cause, so it has a direction.** Outdoors there are
two lights: the sun, and the sky. Where the sun is blocked, the only light left
falling into the shadow is skylight, which is blue — so the shadow's chromaticity
moves toward blue. The complementary reading points the same way (warm key light
→ cool shadow; orange light gives blue shadows, green light gives red ones), so
the two reinforce each other. Shift the shadow **toward the complement of the key
light**, not reflexively toward blue: that only coincides with blue because the
usual key is warm.

A published starting point from a working comic colourist is **−30% luminosity,
+15% saturation** off the flat, applied as a correction layer. Treat it as one
studio's default worth trying first, not a standard — and note it moves
saturation *up*, against the usual "less saturated" advice, because the flat it
starts from is already a muted comic flat rather than a pure hue.

The common shortcut — a multiply layer in the flat's own colour — is explicitly
taught as working because "even if you set your colour to the same one you used
for flats, the multiply layer will make it darker." That is exactly its weakness:
it produces a pure value drop with no hue decision in it.

**Where the shadow goes matters more than what colour it is.** A shadow that
follows the outer contour at constant width is a coloured outline: it reads as a
stripe painted on the edge and it describes nothing. A shadow that states a plane
starts narrow where the form is still facing the light and *widens as the surface
turns away*, so its inner edge — the terminator — crosses the form rather than
paralleling its silhouette. Mass it as one connected shape across every part on
the same side, and route the terminator around a feature rather than bisecting
it: a cel shadow cutting an eye in half reads as damage, not as light.

## Few colours

- **Duotone convention**: black carries the dark structure and detail; the second
  colour carries midtones and highlights. That is a real division of labour and a
  good default for any minimal palette — one entry does structure, one does tone.
- **Ben-Day** is the ancestor of getting more apparent colours out of fewer inks:
  sparse dot patterns optically mixing (widely spaced magenta reads as pink,
  interleaved cyan and yellow read as green). More colours came from *density and
  mixing of the same limited ink set*, not more pigments.
- Historical comics stayed near two to four colours for press economics — each
  colour needs its own plate and press pass — not for taste. Which means a
  limited palette is a production constraint that turned into a look, and it is
  reproducible on purpose.

## Choosing the three to six

Picking which colours is a smaller decision than deciding **how much of each**.
The areas must be unequal. The named rule is **60 / 30 / 10**: a dominant colour
holding about 60% of the area, a secondary about 30%, an accent about 10%.

- The **dominant is usually the quietest** — a neutral, an off-white, a grey, a
  beige. It is the ground the rest is read against, not the thing you notice.
- The **secondary** carries the visual interest and should contrast or complement
  the dominant.
- The **accent** is the only place saturation is spent. It can sit sympathetically
  with the other two or compete with the dominant, and competing is what buys
  tension.
- **The paper is a palette entry.** If the paper colour is the largest area in the
  drawing, it *is* the 60% — count it, choose it, and do not then add a second
  large neutral that fights it.

Equal areas are the failure: without dominance the eye jumps around with nowhere
to settle, and repetition without dominance reads as monotony. Push the ratio
before you push the hues.

## Printing loose: screenprint and riso

Assume misregistration rather than tolerate it. Studios state plainly that
registration on a multi-colour riso **will never be perfect**, and none of them
publishes a shift figure in millimetres — the instruction is comparative:
**trap by the largest amount your tool allows**, and add registration marks.
The alternative to trapping is the opposite move: *jiggle*, deliberately leaving
a gap around a shape so the drift reads as intentional.

What is quantified, and worth designing to:

| Constraint | Figure |
|---|---|
| Minimum line weight | ~0.5 pt |
| Minimum text size | ~7 pt |
| Ink coverage on a large solid | 75–85%, never 100% — it floods and leaves tide marks |
| Best-reading combination | line work printed **over** a solid block of colour |

## Mistakes

| Mistake | Why it matters |
|---|---|
| **Merging unrelated regions** into one flat — two figures, or wall + floor + window | Destroys the point of flatting: the renderer can no longer select them independently |
| **Anti-aliased edges** | Fringing, and broken re-selection |
| **Stray pixels** — pinholes, unflatted specks | Show up as holes once rendered |
| **Gaps in the line art** | The single most recurring flatting problem; fills leak through. Close the line or use gap-tolerant filling |
| Shading that ignores the light source or follows detail instead of form | Flattens the drawing rather than modelling it |

## Colour holds

A **colour hold** is recolouring the ink line itself away from black in places.
It dates to the 1970s in mainstream comics and was historically rare only because
it cost an extra hand-cut separation. Once line art is its own layer it is free,
which is why it went from special-purpose to routine.

## Not established here

Kept explicit rather than guessed, because the research could not verify them:

- **A registration tolerance in mm** for screenprint or riso. The figure "up to
  3 mm" circulates, but every studio guide reached states the problem
  qualitatively and prescribes maximum trapping instead of a number. Design for
  visible drift; do not encode a millimetre budget.
- **Whether −30% luminosity / +15% saturation generalises.** It is one colourist's
  published default, not a measured or agreed value. The *direction* of the shift
  is sourced; the magnitude is not.
- **How many colours a drawing should carry.** 60/30/10 says how to apportion
  three roles; nothing found says three versus six, and the historical two-to-four
  was press economics, not design.
