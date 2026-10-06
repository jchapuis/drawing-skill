# The bicycle as a solid

A bicycle goes wrong when it is drawn as outlines. It is a lattice of thin dark
tubes, and drawing each tube as two lines around a lighter interior gives a
tangle of wire that does not read as a machine. A bicycle also needs a
construction: if you have a way to build the figure but none for the bike, the
bike gets outlined, and outlining is the cardinal error.

Everything below describes the average bicycle, and **the average bicycle is not
the one in front of you.** Do not build on it. Build on landmarks measured off
the subject. Use this afterwards, to ask why your measured bike differs and
whether the difference is real or an error.

## The five ways a drawn bicycle fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| The frame reads as a **thicket**: every tube drawn as two heavy contours with the tube colour between them | Sight across a tube: if it holds **zero** of its own colour between two outlines, the tube is entirely its own outline. A subject's tube holds most of its width in colour |
| The bike **does not read as an object at all**: blind describers of the subject name it by mass; no describer of the drawing mentions a bicycle | Tubes drawn as two open lines measure a few px of dark against a subject's 12–25px. Each tube must be one closed shape with a solid fill |
| The bar top and the fist are **one dark mass** | Measure what the subject puts between them: a band of its own ground, or where the whole passage is dark, a second lighter value. Two objects that touch still need what says they are two |
| A tube's ink runs **straight over the limb in front of it** | Sight down the tube in the subject: it stops at the limb and restarts beyond it. The limb's flat hides the tube's ink only if it is written **after** it, so write the far tube first |
| A wheel is judged "much too large" by eye when it is within a few percent | Wheels are the easiest part to measure and the easiest to misjudge. **Measure them** rather than judging them |

The pattern across all five: a bicycle is made of **thin dark solids**, and each
failure comes from drawing them as **outlines of thin light shapes**. A tube is a
dark bar with an edge, not a line with a colour inside it.

## The frame is two triangles, one of them open

| Part | What it does |
|---|---|
| **Head tube** | The short one at the front. Its angle sets the bike's attitude, typically 72–74° from horizontal, and near-parallel to the seat tube |
| **Top tube** | Head tube to seat tube. Horizontal on a classic frame, sloping down to the rear on a modern one. The most legible line on the machine |
| **Down tube** | Head tube to bottom bracket. **The fattest tube on the bike**. If all your tubes are one weight, this is the one that is wrong |
| **Seat tube** | Bottom bracket up to the saddle, near-parallel to the head tube |
| **Chainstays** | Bottom bracket back to the rear hub, near-horizontal |
| **Seatstays** | Seat tube down to the rear hub. **The thinnest tubes on the bike** |

The front triangle (head, top, seat, down) is closed and carries the weight. The
rear is a flattened triangle either side of the wheel, and in a side view the
two stays read as one narrow wedge, not as two separate bars.

**The tubes have a weight order of their own.** Down tube heaviest, then top
tube and seat tube, then chainstays, then seatstays. Drawing every tube at one
weight is the frame equivalent of a uniform outline, and it makes a bike read as
wire.

## Wheels

- **Both wheels are the same diameter.** On a road bike, always. Unequal wheels
  are the fastest way to make a bicycle look like a toy.
- **Wheelbase is roughly 1.5 wheel diameters** on a road bike, a proportion
  worth checking against your measured wheel before you place the second one.
- A wheel seen at an angle is an ellipse. Its **minor axis points at the
  vanishing point**, not down the page, and the **hub does not sit at the centre
  of that ellipse**: a circle in perspective projects with its centre pushed
  toward the near side. Placing the hub at the ellipse's centre makes a
  three-quarter bicycle look bent. That is the geometry of a true projection,
  but a drawn or generated subject does not always obey it (in one case the front hub
  sat at its ellipse's centre within 12px and the rear 130px off), so measure each
  hub rather than imposing the offset.
- **Spokes are a tone, not thirty-two lines.** Draw enough to establish the
  radial direction and let the rest be the value they average to. A wheel with
  every spoke drawn reads as a dinner plate.
- A wheel is **two concentric bands, not one circle**: a dark tread outside and
  a lighter rim inside it. Which of the two is wider depends on the wheel in
  front of you: a deep-section rim is far wider than its tread, a balloon tyre
  the reverse. **Measure both along a radius** rather than assuming either. Cut
  from the hub outward and record the run of each value with `check.py --scan` on
  a one-row box through the hub, with `--value` naming the tyre's and the rim's
  palette names. That one scan settles the radii, both widths and the ink between
  them, and it is the only reliable way to read a band that curves.
- **The ratio between those two bands makes a wheel read as a wheel.** One band
  clearly dominant plus a narrow one reads as a surface with an edge. The same
  two at *equal* width read as two ribbons with a stripe between them, and the
  wheel stops being a wheel. This survives correct radii, placement and colours
  and every numeric gate, because each band is present and in its box. Preserve
  the ratio, not just the presence. Anything that grows both bands by the same
  absolute amount converges the ratio; `colour.md` has the trapping case.

## The sub-forms an inventory descends to

"Bar" and "drivetrain" are not parts; each is a cluster of small dark forms in
contact, and an entry that stops at the cluster gives the count (`--counts`),
`--depth` and the part-crop describer nothing below it to check. Look for these on the
subject, and write an entry for each that is there:

- **Bar:** the taped top, each drop's curl, and on each side a **lever body**
  (the hood) sitting on the bend, taller than the bar, with the **blade**
  hanging from its front. Without the body the blade has nothing to hang from
  and floats.
- **Drivetrain:** chainring and its cut-outs, crank, pedal, the **chain** (both
  runs, and its wrap round the cogs), the **cassette** as a disc with a toothed
  edge, and the **rear derailleur** below it: body, knuckle, and a cage whose
  two small wheels the chain threads. It reads by the light gaps between those
  members; filled solid it is a block with holes.

  The chain is one closed loop: upper run, wrap round the cassette, through the
  derailleur's two wheels, lower run, wrap round the chainring, back to the
  upper run. Each run meets the next at a tangent point shared by name, so the
  loop has no gap (`line.md` § Continuous paths). Where the subject shows links,
  the chain is a beaded line, not a plain one. The chainring's and the
  cassette's teeth are counted and written, each as its own mark. `--joins`
  lists a run that stops short.

`check.py --checklist parts.json` reads this block and fails on any of these
the inventory neither names nor excuses in `_absent`:

```checklist
object: bike|bicycle
sub-forms: tyre|tire rim spoke hub frame|tube fork bar|handlebar hood lever brake saddle chainring crank pedal chain cassette derailleur frontmech|frontderailleur
```

## Where the machine and the rider meet

A rider touches the machine in three places, and each is a contact to draw
deliberately:

- **Hands on the bar.** The hand wraps the bar and the bar continues past it.
  If hand and bar share one silhouette you have drawn a mitten. Leave the band
  of ground the subject leaves. On the hoods the hand holds the lever body, not
  the bar; `hands-and-feet.md` covers that grip.
- **Foot on the pedal.** The shoe is a wedge with a sole; the pedal is a small
  dark block under it. Both come out as discs until the sole and the strap slot
  go in, and a disc is what you draw when you have not decided which way the foot
  points.
- **Seat under the rider.** The saddle is a long narrow wedge seen nearly
  edge-on, and its nose is the landmark that fixes the rider's fore-aft position.

## Occlusion is write order

A bicycle is a lattice, so the rider's legs, the far side of the frame and the
spokes pass behind and in front of each other constantly. The canvas paints in
the order marks are written, so a nearer form's flat hides the far form's ink
only when the far form (fill and ink) is written first. Written the other way,
the far contour runs straight across the nearer form. A lattice has more
crossings than most things in a scene, so write it tube by tube in depth order
and record each crossing as its own row in the overlaps table.

## Build order

1. **Both wheels first**, as measured circles, which fix the scale and the
   wheelbase, and every other landmark hangs off their hubs.
2. **The bottom bracket**, which is the one point that fixes the whole frame.
3. **The four tubes of the front triangle**, as single straights between fixed
   points, in the block-in's straight-line discipline.
4. **The rear stays** to the rear hub.
5. **Bar, saddle, cranks**, the three contact points, placed against the rider,
   not against the frame.
6. Only then thickness, the weight order of the tubes, and the occlusions where
   the rider crosses the machine.

Draw the bicycle **with** the rider and at the same stage, never after. It is
usually the largest dark mass in the picture, and the rider's proportions answer
to it as much as it answers to them.
