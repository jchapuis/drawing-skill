# Hands and feet

Every drawing this skill has made has hands and feet in it, and in every one of
them they were among the worst things in the picture. In one panel a rider's
hand was **absent entirely** — a black disc with five stripes ruled across it and
a forearm stopping eighteen pixels above it, touching neither the hand nor the
bar. Three marks that each landed exactly where they were sent, and no hand. Every
mechanical gate was green, because nothing in the drawing was wrong; something was
missing, and missing has no pixels.

In the sibling panel the two hands merged into **one egg**, and both shoes were
drawn as **discs**. A disc is what you draw when you have not decided which way
the foot points.

## The schema is a diagnostic, never a scaffold

Everything below is knowledge about the **average** hand and the average foot,
and the average one is not the one in front of you. **Do not build on it.** Build
on landmarks measured off the subject, and use what follows only afterwards, to
ask why your measured hand differs from the average and whether the difference is
the grip, the foreshortening, the glove — or a mistake.

This warning bites harder here than anywhere else in the repertoire, for a
reason worth stating plainly: **a hand is almost never seen as a hand.** It is
seen wrapped round a bar, hanging off a wrist, jammed in a pocket, at forty-five
degrees to the picture plane with three of its fingers hidden. The canonical
open palm with its five radiating tubes is the one arrangement you will hardly
ever draw, and it is the one every schema teaches. Supply that form for free at
the stage whose job is to find the particular one and you get what this skill's
most expensive failure got: every part inside its correct box, and not a hand.
The same holds for a foot, which in practice is a **shoe**, on a pedal, at an
angle.

If a passage below could be followed with the subject covered up, you are using
it wrongly.

**Provenance is marked throughout.** *Bought* means a drawing paid for the claim
and the measurement is given. *Read* means it comes from the instruction
literature, is named to its source, and **has not been tested here.**

## The five ways a drawn hand or foot fails

Numbers are `check.py --parts`: `ink` is dark-pixel share in the box, `form` is
the share departing from the box's own local ground — how much is actually *going
on* in there.

| The fault | The measurement that finds it |
|---|---|
| **The hand is not there** — a disc, a few ruled stripes, and a forearm ending in mid-air | `form` drops to about **two-thirds** of the subject's, putting it among the worst boxes in the inventory. The fix is a back sitting **on** the handle, four fingers hanging below it and curling forward under the tube, and the forearm's two contours **ending inside it** |
| **The mitten** — two hands become one egg-shaped dark mass crossed by long concentric arcs, the finger loops a scribble that never resolves | `ink` rises about twelve points while `form` falls thirty: **darker and emptier at once**, which is the definition of a mitten — one mass replacing several forms |
| **Fist and handle welded** into a single dark shape | `ink` again about twelve points high in that box. The subject separates them with a **band of its own ground** — or, where the whole passage is dark, a **second lighter value**. Two objects that touch still need what says they are two |
| **The shoes are discs** | `ink` runs high and `form` low together. It resolves only when a **sole running the full length of the bottom** and a **second strap slot** go in, and the outline is still a curve where the subject's has a **heel corner** |
| **The shoe's mass lands in the sock's box**, making the ankle boxes the worst in the inventory | Both read far heavier than the panel's average, and neither is a fault of a sock: it is a shoe drawn too big and too high, spilling upward |

Read the pattern rather than the rows. A hand or foot fails by becoming **one
dark mass where the subject holds several forms with ground between them**, and
the signature is always the same pair of numbers moving in opposite directions:
ink up, structure down. Nothing else in either inventory does that.

## The hand is a box and a wedge [read: Bridgman, Loomis]

Bridgman's *Constructive Anatomy* is the tradition here, with Loomis for
proportion. None of it has been tested here.

- **The palm is a box** — a slab with real thickness, a front, a back and two
  narrow sides. Not a flat pad. Its thickness is what a mitten has none of.
- **The thumb is a separate wedge** of muscle on the box's thumb side, and
  Bridgman puts it first: *"the mass of the thumb dominates the hand."* It is
  pyramidal at the base, narrow in the middle, pear-shaped at the end, and it
  reaches to the middle joint of the first finger — a proportion you can check
  against your measured hand rather than guess.
- **Everything organises round the thumb's basal joint.** Spread, the fingers
  radiate from it; gathered, they form a corona around the thumb's tip; bent or
  clenched, *"each circle of knuckles forms an arch with the same common
  centre."* This is why a fist is drawn as a set of concentric arcs and not as
  four sausages side by side.
- **The hand has an action side and an inaction side.** The side carrying the
  greater angle is the action side; the other runs straight. A hand drawn
  symmetrical about its own axis has no action in it.
- **Loomis' size check:** put the heel of the palm on your chin and the middle
  finger reaches the hairline. **The hand is the length of the face.** Ours came
  out as a disc smaller than that and as an egg larger than it; either way the
  check is one measurement.

### Fingers are three cylinders, and they never taper to a point

Bridgman again, and this is the part that most reliably separates a drawn hand
from a symbol:

- **Three segments per finger, two for the thumb.** In profile there is *"a
  step-down from each segment to the one beyond, bridged by a wedge"* — so the
  back of a finger is **a series of wedges and squares**, not a smooth cone.
- **The middle joint is the largest**, and the middle finger is the longest and
  largest because it opposes the thumb.
- **The finger tapers from the middle joint** and ends *"embedded in a horseshoe
  form holding the nail."* It does **not** narrow continuously from knuckle to
  tip. A finger drawn as a taper to a point is the single commonest symbol tell.
- **In back view the fingers arch toward the middle finger** as a group. They are
  not parallel and they are not a fan.
- **Knuckles run on arcs**, and the arcs are the fastest way to get four finger
  lengths right at once: sweep the arc first, then cut each finger to where it
  meets it. The second knuckle sits highest and largest.
- **Creases do not sit on the joints.** Most run across; the one opposite the
  basal joint is a single long wavy crease down the palm.

### The hand in contact, which is the only one you will draw [bought]

A hand in the inventory is its fingers and its thumb, each an entry, or
`_absent` says why not; `check.py --checklist parts.json` holds it to that:

```checklist
object: hand|glove
sub-forms: finger thumb
```

A hand on a bar is not a hand plus a bar. It is a **grip**, and five things
decide whether it reads:

1. **The bar continues past the hand on both sides.** If hand and bar share one
   silhouette you have drawn a mitten, and the box goes about twelve points
   darker as the fist and the bar top fuse into one shape.
2. **Leave whatever the subject leaves between them** — usually a strip of its
   own ground, and where the whole passage is dark, a second lighter value
   instead: a handle lighter than the glove on it does the same work as a gap.
   Measure which before assuming a gap. Two forms that touch still need what says
   they are two; without it the parts check reports a box that got darker and can
   tell you nothing more.
3. **The fingers curl round and come back into view underneath.** In the subject
   the near glove shows the back as one rounded plane with **a row of four small
   arcs** below it — the finger tops curling forward under the tube, pale skin
   showing at the tips. That is the shape to draw: a back, four fingers hanging
   below it curling forward under the tube. Three long concentric arcs across a
   solid egg is what a beetle looks like.
4. **A hand on a lever body holds the body, not a tube.** The glove's back
   covers the body's top, the fingers pass in front of the lever blade and wrap
   it, and the blade hangs from the body. Glove, body and blade are one
   connected dark shape told apart by ink and a lighter value, never by
   ground: ground between the fingers and the blade says the lever floats. A
   hand drawn beside the body instead of over it came out a quarter too small,
   with the fingers above the blade, and read as tangled.
5. **The forearm's contours end inside the hand**, not eighteen pixels above it.
   A limb that stops short of what it holds is the absence failure, and only the
   parts gate against a written inventory catches it.

## The foot is a wedge with an arch [read: standard figure-drawing construction; foot-tripod literature]

Untested here, and stated as the traditional construction gives it.

- **The whole foot is a wedge** — a triangular prism, thickest at the heel,
  slanting down and forward to the toes. Ankle in at the back and high; toes out
  at the front and low. The wedge is what gives a foot a **direction**, and a
  direction is precisely what a disc has none of.
- **The arch is a curve cut into the side of the wedge**, on the inside. From the
  front the foot is narrowest along its outer edge, which sits on the ground for
  its whole length, and rises on the inner side above the big toe. Draw both
  sides the same and you have a block, not a foot.
- **Three points of contact — a tripod:** the centre of the heel, the ball behind
  the big toe (head of the first metatarsal), and the base of the little toe
  (head of the fifth). Three arches span between them. Whatever the pose, ask
  which of the three are down; that answers where the weight is and therefore
  which way the ankle leans.
- **Toes are short prisms, tapering big to little**, with the big toe set at its
  own angle to the rest. They are not a fringe on the front of the wedge.
- The foot's own proportion check: it is about the length of the forearm, and
  seen from the side it is far longer than it is deep.

### A shoe is that wedge with a skin on it [bought]

The shoe does not replace the wedge, it clothes it. Draw only the skin and this
is what happens:

- **A sole running the full length of the bottom.** This is the mark that
  converted both discs into shoes. It is a single long near-straight line and it
  is the shoe's spine — it states the direction the wedge points, which is the
  one thing a disc cannot say.
- **A heel corner at the back.** The subject's outline turns a corner there. A
  drawing runs through it as a curve, and the box stays well short on `form` even
  after the sole and a second strap slot have gone in.
- **Cross-marks at the shoe's own pitch** — strap slots, seams, a laced tongue.
  Two are enough, and they must run **across** the wedge; they are what says the
  form turns. One is a decoration.
- **The shoe's mass belongs in the shoe's box.** The worst boxes in an inventory
  are routinely socks holding shoe. Whenever a foot is drawn a little too
  large and a little too high, the error is reported against the part above it,
  so read a bad ankle box as a possible shoe fault before you touch the ankle.
- **The pedal, the step, the ground is a separate dark block under the sole** —
  its own form with its own contour, never absorbed into the shoe.

## Build order

1. **Say what the hand is doing, in words** — gripping a bar, resting on a
   forearm, hanging. And say which way the foot **points**. Both are decisions,
   and both are the thing a generic form quietly makes for you.
2. **The palm box and the thumb wedge**, measured — against the face for size,
   against each other for the action side. Feet: the wedge, with its heel end and
   its toe end at their measured heights.
3. **The knuckle arc**, as one sweep, before any finger exists. Feet: the sole
   line, full length, before any upper exists.
4. **Fingers as three-segment runs cut to the arc**, each with its step-down and
   its blunt end. Toes as short prisms off the front of the wedge.
5. **The contact**: where the held object passes behind the hand and reappears,
   and the **band of ground** between the two. The contour of the object must
   stop and restart — a flat cannot hide ink.
6. **Weight last, and downward.** A hand and a foot are small forms that carry
   many edges, so they attract ink; every hand and foot fault measured in these
   two panels was a box that ended up too dark. Take the interior marks to the
   finest weight the ladder has and leave the silhouette to carry the form.
7. **Walk the inventory before you call it done.** The hand that was missing was
   missing beside three marks that were all correct. The only check that sees an
   absence is `--parts` against a list written before the first mark.
