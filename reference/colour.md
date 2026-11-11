# Flat colour

Colour in cartoon work starts with **flatting**: splitting the drawing into
separate regions of flat, unmodulated colour, to be rendered on top of later. In
comics it is a separate job from colouring, because it is mechanical and comes
before any decision about light.

## Contents

- The pipeline
- Trapping: the rule that matters most
- A band is not a body, and trapping one changes its width
- A flat with a corner in it is not a curve
- Hard edges only
- Layer order
- The line-off test
- Cel shading on top
- Choosing the shadow colour
- Few colours
- Choosing the three to six
- Printing loose: screenprint and riso
- Mistakes
- Colour holds
- Not established here

## The pipeline

1. Closed line art.
2. **Flats**: one region per distinct surface, filled with flat colour. A face,
   a neck and a collar are three regions even if they end up the same colour.
3. **Colour assist**: the placeholder colours are nudged toward the real palette.
4. **Render**: light and shadow, using the flats as ready-made selections.

The output of flatting is a set of labelled regions, not a preview.
Professional flatters pick throwaway colours as different from each other as
possible, so every region stays easy to select. Getting the colours right is the
next stage's job.

## Trapping: the rule that matters most

**The fill extends underneath the line, never just up to it.**

If the black plate shifts in printing, a fill that runs under the line only
reveals more of the right colour. A fill that stops flush against the line shows
any misregistration as a white gap.

Prepress puts it as **spread the lighter colour underneath the darker one**. The
eye reads shape from the dark edge, so the light fill running under it is
invisible and the dark edge stays crisp. At 150 lpi the standard trap is
**1/150–1/300 inch (about 0.08–0.16 mm)**, multiplied by 1.5–2 when one of the
two colours is black, because black hides misregistration better.

For the same reason, black line art is usually **overprinted** on the colour
instead of knocked out of it: the black covers the seam, so no separate trap is
needed.

Here, draw the flat generously past where the ink will go, behind the ink, and
let the line cover its edge. Neither a hand nor a press cuts colour exactly to a
line.

**A trap is hidden only where a line lies on top of it.** Where the ink stops,
most often where a contour runs out of the picture at the frame, the overhang
shows as a smear of colour beside the drawing. Run those contours *past* the
frame instead of ending them on it.

The same applies wherever a line is **broken for something in front of it**: a
horizon behind a figure, a fence wire behind a post, a road edge behind a wheel.
The line is drawn in segments, and since a flat cannot hide ink, the segments
have to stop. **Run each segment *under* the thing it breaks for**, not up to
it. A segment that ends flush leaves a three or four pixel slot in the line art
that colour pours through: one slot at a waist band flooded five hundred pixels
of field. Overlap the object in front by more than the segment could miss by.

**Trap against where the line actually landed, not where it was aimed.** The trap
depends on the ink's width, so measure it off the render, as you would any
coordinate. A flat set against the ink's intended path is a pixel or two out
along its whole length, in whichever direction the stroke leaned.

**The fill must not follow the line exactly.** Reusing the ink's control points,
or offsetting them by a constant, is how a press behaves, not a hand. The fill
then copies every wobble, so a lump in the contour becomes a lump in the colour
and the two errors add up. Give the fill **its own points**: the same shape,
stated independently, wandering either side of the line as a hand overruns in
one place and falls short in another. The ink covers where it fell short, and
where it overran reads as a hand.

**How wide?** The prepress figures are absolute because a press has a fixed
misregistration. A drawing does not. What has to be hidden is the gap between a
fill's edge and the *middle* of the line covering it, so **the trap is about half
the ink's own width, and it scales with the line.** A single trap width across a
whole drawing sticks out from every hairline and disappears under every heavy
contour: a 5px trap under a 4px line is a 5px band of colour beside it.

## A band is not a body, and trapping one changes its width

Trapping pushes every vertex outward from the flat's outline. On a **body** (a
form whose edge is its silhouette) that is what you want. On a **band** it is
not. A band is a strip: a rim inside a tyre, a hem, a strap, a shade along a
limb, or any joint line thick enough to be a flat. Its two long edges face
opposite ways, so both move out and **the band gains twice the trap in width**:
with the trap at half the ink width, a whole ink width added to a measured
dimension. It fattens every band in the drawing at once, and no gate reports it,
because the flats are present, filled, registered and in their boxes.

Where two bands lie **concentric or parallel**, the damage is worse than an
error in either one. **The pair reads through the ratio between their widths**,
and trapping adds the same amount to both, so the narrower one grows
proportionally more and the widths converge. A wide band beside a narrow one
reads as a surface with an edge; at equal widths they read as two stripes, and
the viewer names the object differently.

So trap a band only at its **ends**, where they tuck under something, and never
along its length. Or draw the pair as one body flat in the wider band's colour,
trapped once on its outer silhouette, with the narrower band drawn over it as an
untrapped flat. Then only the silhouette edge grows, and the measured edge stays
where you put it.

**The general rule: trap an edge that is a silhouette; never trap an edge that is
a measurement.** A vent, an eye, a cast shadow, a shade and a band all have
measured edges. Trapping them swells the interior shapes until they eat the
form.

**The fill's wander must stay inside the trap.** The failures look nothing alike:

| | reads as |
|---|---|
| Fill wanders *within* the ink's own width | a hand |
| Fill falls short of the line | a white gap, always a mistake |
| Fill spills past with no line over it | a smear, always a mistake (except under `finish: sketch`, where a little loose colour is part of the look; see `reference/style.md`) |

So trap generously first, then let the fill's own points wander by less than the
trap. A fill and contour that visibly disagree read as the drawing coming apart,
not as looseness, and the eye lands on it first.

## A flat with a corner in it is not a curve

Most flats have straight edges: a door, a wall, a floor, a pinned-up photograph,
a panel of fabric. Sent as a smooth path, the spline through their four corners
misses every corner by a wide margin, because no interpolating curve can turn a
right angle at one vertex whose neighbours are far away. No trap covers this:
the shape is not where its points are, and a wall's base can bow a hundred
pixels onto the floor.

Draw such flats with **straights** (the same `smooth=False` the block-in uses),
or put a point close in on each side of every corner. Use a smooth path only
for shapes that are curved all the way round.

## Hard edges only

Flats are **aliased, not anti-aliased**. Soft edges stop the rendering stage
from re-selecting regions cleanly, and fringe in print. Use binary alpha and
hard boundaries.

## Layer order

Flat colour sits **beneath** the black line art, on its own layer or stage, so
the line can cover the fill's imprecise edge.

## The line-off test

A check you can run, from a working colourist: **hide the line art and see
whether the picture still reads** on flat colour alone. Foreground, middle
ground and background should separate, and the important elements should stay
legible. If the composition holds only because the line is doing the work, the
colour design has failed.

Run this at the flats stage, before any rendering.

## Cel shading on top

Hard-edged flat shadow shapes are the **default** in mainstream comic colouring,
not a stylised exception. One professional describes nearly all of their
rendering as cel shading with almost no effects.

Lay the shadow down as **chunky simplified shapes, not gradients, and not
following every detail**. It must still keep to one consistent light direction
and describe the form underneath. The failures colourists name are shading that
flattens the drawing, ignores the light source, or wrecks the forms.

Keep every shading shape a separate region you can re-select, as with the flats,
so rendering stays region-based and does not turn into freehand painting.

## Choosing the shadow colour

Colourists consistently describe a shadow as darker, less saturated and shifted
in hue, never just darker. The hue always moves at least slightly, and that
warm/cool contrast is what makes flat colour look lit.

**The hue shift has a physical cause, so it has a direction.** Outdoors there
are two lights, the sun and the sky. Where the sun is blocked only blue
skylight reaches, so the shadow moves toward blue. The
complementary-colour rule points the same way (warm key light, cool shadow;
orange light gives blue shadows, green light gives red ones). Shift the shadow
**toward the complement of the key light**, not automatically toward blue. It
only matches blue because the usual key light is warm.

A published starting point from a working comic colourist is **-30% luminosity,
+15% saturation** off the flat, applied as a correction layer. Treat it as one
studio's default worth trying first, not a standard. It raises saturation,
against the usual "less saturated" advice, because the flat it starts from is
already a muted comic flat, not a pure hue.

When there is a subject to copy, read the shadow colour off it instead of
using either rule. Warm, translucent materials (fur, skin, wood, fruit) often
get warmer and more saturated toward the shadow core, and a shadow sampled as an
average of the shade, its edges and the ground's spill comes out greyer than the
subject (`reference/stage-0.md`, step 1).

The common shortcut is a multiply layer in the flat's own colour, taught because
"even if you set your colour to the same one you used for flats, the multiply
layer will make it darker." That is its weakness too: a pure drop in value with
no choice of hue.

**Where the shadow goes matters more than its colour.** A shadow that follows
the outer contour at constant width is a coloured outline: it reads as a stripe
painted on the edge and describes nothing. A shadow that states a plane starts
narrow where the form still faces the light and *widens as the surface turns
away*, so its inner edge (the terminator) crosses the form instead of running
parallel to the silhouette. Mass it as one connected shape across every part on
the same side, and route the terminator around a feature instead of through it.
A cel shadow that cuts an eye in half reads as damage, not light.

## Few colours

- **Duotone convention**: black carries the dark structure and detail, and the
  second colour carries midtones and highlights. This split is a good default
  for any minimal palette: one entry for structure, one for tone.
- **Ben-Day dots** are the ancestor of getting more apparent colours from fewer
  inks. Sparse dot patterns mix in the eye: widely spaced magenta reads as pink,
  and interleaved cyan and yellow read as green. The extra colours came from the
  density and mixing of the same few inks, not from more pigments.
- Historical comics kept to about two to four colours because each colour needed
  its own plate and press pass. That production limit became a look you can
  reproduce on purpose.

## Choosing the three to six

How much of each colour you use matters more than which colours. The areas must
be unequal. The usual rule is **60 / 30 / 10**: a dominant colour over about 60%
of the area, a secondary about 30%, an accent about 10%.

- The **dominant is usually the quietest**: a neutral, an off-white, a grey, a
  beige. It is the ground the rest is read against, not the thing you notice.
- The **secondary** carries the visual interest and should contrast with or
  complement the dominant.
- The **accent** is the only place you spend saturation. It can sit comfortably
  with the other two or compete with the dominant, which creates tension.
- **The paper counts as a colour.** If the paper is the largest area in the
  drawing, it *is* the 60%. Count it, choose it, and do not add a second large
  neutral that fights it.

Equal areas are the failure. With no dominant colour the eye jumps around with
nowhere to settle, and repetition without a dominant reads as monotony. Fix the
proportions before the hues.

## Printing loose: screenprint and riso

Plan for misregistration instead of merely tolerating it. Studios say plainly
that registration on a multi-colour riso **will never be perfect**, and none of
them publishes a shift figure in millimetres. Their advice is relative: **trap
by the largest amount your tool allows**, and add registration marks. The
opposite approach is *jiggle*: leave a deliberate gap around a shape so the
drift looks intentional.

What is quantified, and worth designing to:

| Constraint | Figure |
|---|---|
| Minimum line weight | ~0.5 pt |
| Minimum text size | ~7 pt |
| Ink coverage on a large solid | 75–85%, never 100%, because it floods and leaves tide marks |
| Best-reading combination | line work printed **over** a solid block of colour |

## Mistakes

| Mistake | Why it matters |
|---|---|
| **Merging unrelated regions** into one flat, such as two figures, or wall + floor + window | Destroys the point of flatting: the renderer can no longer select them independently |
| **Anti-aliased edges** | Fringing, and broken re-selection |
| **Stray pixels**: pinholes, unflatted specks | Show up as holes once rendered |
| **Gaps in the line art** | The most common flatting problem; fills leak through. Close the line or use gap-tolerant filling |
| Shading that ignores the light source or follows detail instead of form | Flattens the drawing instead of modelling it |

## Colour holds

A **colour hold** means recolouring parts of the ink line away from black. It
dates from the 1970s in mainstream comics and was rare then only because it
cost an extra hand-cut separation. Once the line art is its own layer it costs
nothing, which is why it went from special to routine.

## Not established here

These could not be verified, so they are left open:

- **A registration tolerance in mm** for screenprint or riso. The figure "up to
  3 mm" circulates, but every studio guide found describes the problem in words
  and prescribes maximum trapping instead of a number. Design for visible drift;
  do not build in a millimetre budget.
- **Whether -30% luminosity / +15% saturation generalises.** It is one
  colourist's published default, not a measured or agreed value. The *direction*
  of the shift is sourced; the size is not.
- **How many colours a drawing should carry.** 60/30/10 says how to share area
  between three roles. Nothing found says three versus six, and the historical
  two to four came from press economics, not design.
