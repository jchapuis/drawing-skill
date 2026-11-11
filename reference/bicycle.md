# The bicycle as a solid

A bicycle is a lattice of thin dark tubes. Drawn as outlines, each tube two
lines around a lighter interior, it becomes a tangle of wire that does not read
as a machine. It also needs its own construction: without one, you will end up
outlining the bike, and outlining is the worst error you can make.

## Contents

- The five ways a drawn bicycle fails, and what each measures as
- The frame is two triangles, one of them open
- Wheels
- The sub-forms an inventory descends to
- Where the machine and the rider meet
- Occlusion is write order
- Build order

Everything below describes the average bicycle, and **the average bicycle is not
the one in front of you.** Build on landmarks measured off the subject, and use
this file afterwards to ask whether a difference from the average is real or an
error.

## The five ways a drawn bicycle fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| The frame reads as a **thicket**: every tube drawn as two heavy contours with the tube colour between them | Sight across a tube. In the subject most of its width is its own colour; if yours holds **zero** between two outlines, it is nothing but outline |
| The bike **does not read as an object at all**: blind describers of the subject name it by its mass, and no describer of the drawing mentions a bicycle | Tubes drawn as two open lines measure a few px of dark, against 12–25px in the subject. Draw each tube as one closed shape with a solid fill |
| The bar top and the fist merge into **one dark mass** | Measure what the subject puts between them: a band of its own ground or, where the whole passage is dark, a second lighter value. Touching objects still need something that separates them |
| A tube's ink runs **straight over the limb in front of it** | Sight down the tube in the subject: it stops at the limb and starts again beyond it. The limb's flat hides the tube's ink only if the limb is written **after** the tube, so write the far tube first |
| A wheel is judged "much too large" by eye when it is within a few percent | Wheels are the easiest part to measure and the easiest to misjudge. **Measure them** instead of judging them |

All five come from drawing **thin dark solids** as **outlines of thin light
shapes**. Draw a tube as a dark bar with an edge, never as a line with a colour
inside it.

## The frame is two triangles, one of them open

| Part | What it does |
|---|---|
| **Head tube** | The short tube at the front. Its angle sets the bike's attitude, typically 72–74° from horizontal, near-parallel to the seat tube |
| **Top tube** | Head tube to seat tube. Horizontal on a classic frame, sloping down to the rear on a modern one. The most legible line on the machine |
| **Down tube** | Head tube to bottom bracket. **The fattest tube on the bike**. If all your tubes have one weight, this is the one that is wrong |
| **Seat tube** | Bottom bracket up to the saddle, near-parallel to the head tube |
| **Chainstays** | Bottom bracket back to the rear hub, near-horizontal |
| **Seatstays** | Seat tube down to the rear hub. **The thinnest tubes on the bike** |

The front triangle (head, top, seat and down tubes) is closed and carries the
weight. The rear is a flattened triangle on either side of the wheel; in a side
view its two stays read as one narrow wedge, so do not draw them as two bars.

**Give the tubes their own weight order:** down tube heaviest, then top tube and
seat tube, then chainstays, then seatstays. Every tube at one weight does to a
frame what a uniform outline does to a figure: the bike reads as wire.

## Wheels

- **Both wheels are the same diameter**, always on a road bike. Unequal wheels
  make a bicycle look like a toy.
- **The wheelbase is roughly 1.5 wheel diameters** on a road bike. Check it
  against your measured wheel before you place the second one.
- A wheel seen at an angle is an ellipse. Its **minor axis lies along the
  axle (the cylinder's axis), which points at the vanishing point**, not down
  the page. In a true projection the **hub does not
  sit at the ellipse's centre**: it is pushed toward the near side, and centred
  hubs make a three-quarter bicycle look bent. A drawn or generated subject does
  not always obey this, though. In one case the front hub sat within 12px of its
  ellipse's centre and the rear hub 130px off. Measure each hub instead of
  imposing the offset.
- **Draw spokes as a tone, not as thirty-two lines.** Draw enough to show the
  radial direction and let the rest be the value they average to. A wheel with
  every spoke drawn reads as a dinner plate.
- A wheel is **two concentric bands, not one circle**: a dark tread outside and
  a lighter rim inside it. Which is wider varies: a deep-section rim is far
  wider than its tread, a balloon tyre the reverse. **Measure both along a
  radius** instead of assuming. Run `check.py --scan` on a one-row box through
  the hub, with `--value` naming the tyre's and the rim's palette names, and
  read the run of each value from the hub outward. That one scan gives the
  radii, both widths and the ink between them, and it is the only reliable way
  to read a curved band.
- **The ratio between the two bands is what makes a wheel read as a wheel.** One
  clearly dominant band plus a narrow one reads as a surface with an edge. At
  *equal* width they read as two ribbons with a stripe between them. That error
  passes every numeric gate, because each band is present and inside its box,
  so preserve the ratio as well as the bands. Growing both bands by the same
  absolute amount pulls the ratio toward 1; `colour.md` has the trapping case.

## The sub-forms an inventory descends to

"Bar" and "drivetrain" are not parts. Each is a cluster of small dark forms in
contact, and an inventory entry that stops at the cluster leaves the count
(`--counts`), `--depth` and the part-crop describer nothing below it to check.
Write an entry for each of these that the subject shows:

- **Bar:** the taped top, each drop's curl, and on each side a **lever body**
  (the hood) sitting on the bend, taller than the bar, with the **blade**
  hanging from its front. Without the body the blade floats.
- **Drivetrain:** the chainring and its cut-outs, the crank, the pedal, the
  **chain** (both runs, and its wrap round the cogs), the **cassette** as a disc
  with a toothed edge, and the **rear derailleur** below it: body, knuckle, and
  a cage whose two small wheels the chain threads through. It reads through the
  light gaps between those members; filled solid, it is a block with holes.

  The chain is one closed loop: upper run, wrap round the cassette, through the
  derailleur's two wheels, lower run, wrap round the chainring, back to the
  upper run. Each run meets the next at a tangent point both share by name, so
  the loop has no gap (`line.md` § Continuous paths). Where the subject shows
  links, draw the chain as a beaded line. Count the chainring's and cassette's
  teeth and write each tooth as its own mark. `--joins` lists any run that stops
  short.

`check.py --checklist parts.json` reads this block and fails on any of these
sub-forms that the inventory neither names nor excuses in `_absent`:

```checklist
object: bike|bicycle
sub-forms: tyre|tire rim spoke hub frame|tube fork bar|handlebar hood lever brake saddle chainring crank pedal chain cassette derailleur frontmech|frontderailleur
```

## Where the machine and the rider meet

A rider touches the machine in three places. Draw each contact deliberately:

- **Hands on the bar.** The hand wraps the bar and the bar continues past it.
  If hand and bar share one silhouette, you have drawn a mitten. Leave the band
  of ground the subject leaves. On the hoods the hand holds the lever body, not
  the bar; `hands-and-feet.md` covers that grip.
- **Foot on the pedal.** The shoe is a wedge with a sole, and the pedal is a
  small dark block under it. Until you add the sole and the strap slot, both
  come out as discs, which is what you draw when you have not decided which way
  the foot points.
- **Seat under the rider.** The saddle is a long narrow wedge seen nearly
  edge-on. Its nose fixes the rider's fore-aft position.

## Occlusion is write order

In a bicycle the rider's legs, the far side of the frame and the spokes keep
passing behind and in front of each other. The canvas paints marks in the order
they are written, so a nearer form's flat hides a far form's ink only when the
far form (fill and ink) is written first. Otherwise the far contour runs
straight across the nearer form. A lattice has more crossings than most things
in a scene, so write it tube by tube in depth order and record each crossing as
its own row in the overlaps table.

## Build order

1. **Both wheels first**, as measured circles. They fix the scale and the
   wheelbase, and every other landmark hangs off their hubs.
2. **The bottom bracket**, the one point that fixes the whole frame.
3. **The four tubes of the front triangle**, as single straight lines between
   fixed points, as in any block-in.
4. **The rear stays**, to the rear hub.
5. **Bar, saddle and cranks**, the three contact points, placed against the
   rider, not against the frame.
6. Only then add thickness, the weight order of the tubes, and the occlusions
   where the rider crosses the machine.

Draw the bicycle **with** the rider and at the same stage, never after. It is
usually the largest dark mass in the picture, and the rider's proportions depend
on it as much as its proportions depend on the rider.
