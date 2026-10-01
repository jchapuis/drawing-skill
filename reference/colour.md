# Flat colour

Colour in cartoon work is not painting. It is **flatting**: breaking the drawing
into discrete regions of flat, unmodulated colour, then rendering on top of them.
In comics it is a separate job from colouring because it is mechanical and is
done before any decision about light.

## The pipeline

1. Closed line art.
2. **Flats**: one region per distinct surface, filled with flat colour. A face,
   a neck and a collar are three regions even when they end up the same colour.
3. **Colour assist**: the placeholder colours are nudged toward the real palette.
4. **Render**: light and shadow, using the flats as ready-made selections.

Flatting is deliberately dumb work. Its output is a labelling system, not a
preview. Professional flatters pick throwaway colours that are as different from
each other as possible, so every region stays easy to select later. Accuracy is
the next stage's job.

## Trapping: the rule that matters most

**The fill extends underneath the line, never up to it.**

The flatter's central job is to make the fills meet under the ink. If the black
plate shifts during printing, an underlapped fill only reveals more of the
correct colour, never bare paper. A fill that stops flush against the line shows
any misregistration as a white gap.

Prepress quantifies this: **spread the lighter colour underneath the darker
one**. The eye reads shape from the dark edge, so extending the light fill under
it is invisible and the dark edge stays crisp. At 150 lpi the standard trap is
**1/150–1/300 inch (about 0.08–0.16 mm)**, multiplied by 1.5–2 when one of the
two colours is black, because black hides misregistration more forgivingly.

For the same reason black line art is usually **overprinted** rather than
knocked out: the dark element covers the seam, so no knockout-and-trap step is
needed.

Applied here: draw the flat generously past where the ink will go, put it behind
the ink, and let the line cover its edge. No hand and no press cuts colour
exactly to a line.

**A trap is only hidden where a line lies on top of it.** Where the ink stops,
most often at the edge of the frame where a contour runs out of the picture, the
overhang shows as a smear of colour beside the drawing. Run those contours
*past* the frame instead of ending them on it.

The same applies wherever a line is **broken for something in front of it**: a
horizon behind a figure, a fence wire behind a post, a road edge behind a wheel.
The line is drawn in segments, and a flat cannot hide ink, so the segments have
to stop. **Each segment must run *under* the thing it breaks for**, not up to it.
A segment that ends flush leaves a three or four pixel slot. That slot is a hole
in the line art and colour pours through it; one slot at a waist band was enough
to flood five hundred pixels of field. Overlap the occluder by more than the
segment could have missed by.

**Trap against where the line landed, not where it was sent.** The trap is
proportional to the ink's width, so measure it off the render, the same way you
never retype a coordinate from memory. A flat set against the ink's intended path
will be a pixel or two out along its whole length, in whichever direction the
stroke happened to lean.

**The fill must not follow the line exactly.** Reusing the ink's own control
points, or offsetting them by a constant, is how a press behaves and not how a
hand does. The fill then inherits every wobble in the line, so a lump in the
contour becomes a lump in the colour and the two errors add instead of hiding
each other. A hand overruns in one place and falls short in another. Give the
fill **its own points**: the same shape, stated independently, wandering either
side of the line. The ink then covers the places the fill fell short, and the
places it overran read as a hand.

**How wide?** The prepress figures are absolute because a press has a fixed
misregistration. A drawing does not. What has to be hidden is the gap between a
fill's edge and the *middle* of the line covering it, so **the trap is about half
the ink's own width, and it scales with the line.** A single trap width applied
across a drawing goes wrong at both ends: it stands clear of every hairline and
vanishes under every heavy contour. A 5px trap under a 4px line is a 5px band of
colour lying beside the drawing.

## A band is not a body, and trapping one changes its width

Trapping offsets every vertex outward from the flat's own outline. On a **body**
(a form whose edge is its silhouette) that is the intent. On a **band** it is
not. A band is a strip, a rim inside a tyre, a hem, a strap, a shade along a
limb, or any joint line thick enough to be a flat rather than a stroke. A band's
two long edges face outward in opposite directions, so both move apart and **the
band gains twice the trap in width**. With a trap correctly sized to half the
ink, that adds a whole ink width to a measured quantity of the form. It happens
on every band in the drawing at once, in the direction that makes them all
fatter, and no gate reports it, because the flats are present, filled,
registered and in their boxes.

Where two bands lie **concentric or parallel**, this does more harm than an error
in either one. **The pair reads because of the ratio between the two widths**, and
trapping does not preserve it: it adds the same absolute amount to both, so the
narrower band gains the larger share and the two converge. A wide band beside a
narrow one reads as a surface with an edge. The same two at equal width read as
two stripes, and the viewer names the object differently.

So trap a band's **ends**, where they tuck under something, and never its length.
Or draw the pair as one body flat in the wider band's colour, trapped once on its
outer silhouette, with the narrower band written over it as an untrapped flat.
Then only the edge that is a silhouette is grown, and the edge that is a
measurement stays where you put it.

**The general rule: trap an edge that is a silhouette; never trap an edge that is
a measurement.** A vent, an eye, a cast shadow, a shade and a band all have edges
of the second kind. Trapping them swells the interior shapes until they eat the
form.

**The wander must never exceed the trap.** The two failures look nothing alike:

| | reads as |
|---|---|
| Fill wanders *within* the ink's own width | a hand |
| Fill falls short of the line | a white gap, always a mistake |
| Fill spills past with no line over it | a smear, always a mistake (except under `finish: sketch`, where a little loose colour is part of the look; see SKILL.md § Style) |

So the independent points are an offset *inside* a trap wide enough to absorb
them: trap generously first, then let the fill wander by less than the trap. A
fill and a contour that visibly disagree are not looseness. The drawing is coming
apart, and it is the first thing an eye lands on.

## A flat with a corner in it is not a curve

Most flats are cut to straight edges: a door, a wall, a floor, a photograph
pinned up, a panel of fabric. Sent as a smooth path, the spline through their
four corners misses every one of them by a wide margin, because no interpolating
curve turns a right angle at a single vertex whose neighbours are far away. No
trap covers this. The shape is not where its points are, and a wall's base can
bow a hundred pixels onto the floor.

Draw those flats with **straights** (the same `smooth=False` the block-in uses),
or plant a point on each side of every corner, close in. Use the smooth path only
for shapes that are curved all the way round.

## Hard edges only

Flats are **aliased, not anti-aliased**. Soft edges break clean re-selection for
the rendering stage and fringe in print. Use binary alpha and hard boundaries.

## Layer order

Flat colour sits **beneath** the black line art, on its own layer or stage. This
is the same fact as trapping seen from the layer stack: the line is on top so
that it can cover the fill's imprecise edge.

## The line-off test

A runnable check from a working colorist: **hide the line art and see whether the
page still reads.** Foreground, middle ground and background should separate, and
the important elements should stay legible, on flat colour alone. If the
composition only holds because the line is doing the work, the colour design has
failed.

Run this at the flats stage, before any rendering.

## Cel shading on top

Hard-edged flat shadow shapes are the **default** in mainstream comic colouring,
not a stylised exception. One professional describes the overwhelming majority of
their rendering as cel shading with almost no effects.

The shadow goes down as **chunky simplified shapes, not gradients, and not
following every detail**. It must still obey a single consistent light direction
and describe the underlying form. The named failure modes are shading that
flattens the drawing, ignores the light source, or wrecks the forms.

Keep every shading shape an independent re-selectable region, as with the flats,
so the rendering stage stays region-based and does not become freehand painting.

## Choosing the shadow colour

A shadow changes three things at once and is never a value drop alone: it is
darker, less saturated, and shifted in hue. Colourists' shadow colours are
consistently described that way. The hue always moves at least slightly, which
produces the warm/cool contrast that makes flat colour read as lit.

**The hue shift has a physical cause, so it has a direction.** Outdoors there are
two lights, the sun and the sky. Where the sun is blocked, the only light falling
into the shadow is skylight, which is blue, so the shadow's colour moves toward
blue. The complementary reading points the same way (warm key light, cool shadow;
orange light gives blue shadows, green light gives red ones). Shift the shadow
**toward the complement of the key light**, not automatically toward blue. It
only coincides with blue because the usual key light is warm.

A published starting point from a working comic colourist is **-30% luminosity,
+15% saturation** off the flat, applied as a correction layer. Treat it as one
studio's default worth trying first, not a standard. It moves saturation *up*,
against the usual "less saturated" advice, because the flat it starts from is
already a muted comic flat and not a pure hue.

The common shortcut is a multiply layer in the flat's own colour. It is taught
as working because "even if you set your colour to the same one you used for
flats, the multiply layer will make it darker." That is also its weakness: it
produces a pure value drop with no hue decision in it.

**Where the shadow goes matters more than what colour it is.** A shadow that
follows the outer contour at constant width is a coloured outline. It reads as a
stripe painted on the edge and describes nothing. A shadow that states a plane
starts narrow where the form still faces the light and *widens as the surface
turns away*, so its inner edge (the terminator) crosses the form instead of
running parallel to its silhouette. Mass it as one connected shape across every
part on the same side, and route the terminator around a feature instead of
cutting through it. A cel shadow that cuts an eye in half reads as damage, not
as light.

## Few colours

- **Duotone convention**: black carries the dark structure and detail; the second
  colour carries midtones and highlights. This division of labour is a good
  default for any minimal palette: one entry does structure, the other does tone.
- **Ben-Day** is the ancestor of getting more apparent colours from fewer inks.
  Sparse dot patterns mix optically: widely spaced magenta reads as pink, and
  interleaved cyan and yellow read as green. More colours came from the density
  and mixing of the same limited ink set, not from more pigments.
- Historical comics stayed near two to four colours for press economics, because
  each colour needs its own plate and press pass, not for taste. A limited
  palette was a production constraint that became a look, and it can be
  reproduced on purpose.

## Choosing the three to six

Which colours you pick matters less than **how much of each**. The areas must be
unequal. The named rule is **60 / 30 / 10**: a dominant colour holding about 60%
of the area, a secondary about 30%, an accent about 10%.

- The **dominant is usually the quietest**: a neutral, an off-white, a grey, a
  beige. It is the ground the rest is read against, not the thing you notice.
- The **secondary** carries the visual interest and should contrast with or
  complement the dominant.
- The **accent** is the only place saturation is spent. It can sit comfortably
  with the other two or compete with the dominant, and competing creates tension.
- **The paper is a palette entry.** If the paper colour is the largest area in the
  drawing, it *is* the 60%. Count it, choose it, and do not add a second large
  neutral that fights it.

Equal areas are the failure. Without a dominant colour the eye jumps around with
nowhere to settle, and repetition without dominance reads as monotony. Fix the
ratio before the hues.

## Printing loose: screenprint and riso

Assume misregistration rather than tolerate it. Studios state plainly that
registration on a multi-colour riso **will never be perfect**, and none of them
publishes a shift figure in millimetres. The instruction is comparative: **trap
by the largest amount your tool allows**, and add registration marks. The
alternative to trapping is the opposite move, *jiggle*: deliberately leave a gap
around a shape so the drift reads as intentional.

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

A **colour hold** is recolouring the ink line itself away from black in places.
It dates to the 1970s in mainstream comics and was historically rare only because
it cost an extra hand-cut separation. Once line art is its own layer it is free,
which is why it went from special-purpose to routine.

## Not established here

These could not be verified, so they are stated as open:

- **A registration tolerance in mm** for screenprint or riso. The figure "up to
  3 mm" circulates, but every studio guide reached states the problem
  qualitatively and prescribes maximum trapping instead of a number. Design for
  visible drift; do not encode a millimetre budget.
- **Whether -30% luminosity / +15% saturation generalises.** It is one
  colourist's published default, not a measured or agreed value. The *direction*
  of the shift is sourced; the magnitude is not.
- **How many colours a drawing should carry.** 60/30/10 says how to apportion
  three roles. Nothing found says three versus six, and the historical two to
  four came from press economics, not design.
