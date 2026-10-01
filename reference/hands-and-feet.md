# Hands and feet

Hands and feet are small forms that carry many edges, and they are easy to draw
badly. A badly drawn hand is usually one of two things: a dark disc with a few
stripes ruled across it, sitting at the end of a forearm that stops short of it,
or two hands merged into one egg. A badly drawn foot is a disc where the shoe
should be, because the drawing never decided which way the foot points. Every
mechanical gate can pass in these cases. Nothing in the drawing is wrong;
something is missing, and a missing form has no pixels.

## The schema is a diagnostic, never a scaffold

Everything below describes the **average** hand and the average foot, and the
average one is not the one in front of you. **Do not build on it.** Build on
landmarks measured off the subject. Use what follows afterwards, to ask why your
measured hand differs from the average and whether the difference is the grip,
the foreshortening, the glove or a mistake.

This matters more here than elsewhere, because a hand is almost never seen as a
hand. It is seen wrapped round a bar, hanging off a wrist, jammed in a pocket,
or at forty-five degrees to the picture plane with three fingers hidden. The
canonical open palm with its five radiating tubes is the arrangement you will
rarely draw, and it is the one every schema teaches. If you supply that form at
the stage whose job is to find the particular one, every part ends up inside its
correct box and the result is still not a hand. The same holds for a foot, which
in practice is a **shoe**, on a pedal, a step or the ground, at an angle.

If a passage below could be followed with the subject covered up, you are using
it wrongly. `[read: source]` marks a claim taken from the named book or tradition: it comes from
the literature and has not been tested here. Rules without the tag come from
measured failures.

## The five ways a drawn hand or foot fails

The measurements come from `check.py --parts`: `ink` is the share of dark pixels
in the box, and `form` is the share departing from the box's own local ground,
that is, how much is going on in there.

| The fault | The measurement that finds it |
|---|---|
| **The hand is not there**: a disc, a few ruled stripes, and a forearm ending in mid-air | `form` drops to about **two-thirds** of the subject's, putting the box among the worst in the inventory. The fix is a back sitting **on** the handle, four fingers hanging below it and curling forward under the tube, and the forearm's two contours **ending inside it** |
| **The mitten**: two hands become one egg-shaped dark mass crossed by long concentric arcs, the finger loops a scribble that never resolves | `ink` rises about twelve points while `form` falls thirty: **darker and emptier at once**, which is what a mitten is, one mass replacing several forms |
| **Fist and handle merged** into a single dark shape | `ink` again about twelve points high in that box. The subject separates them with a **band of its own ground**, or, where the whole passage is dark, a **second lighter value**. Two objects that touch still need something that says they are two |
| **The shoes are discs** | `ink` runs high and `form` low together. It resolves when a **sole running the full length of the bottom** and a **second strap slot** go in, and the outline has a **heel corner** where a disc has a curve |
| **The shoe's mass lands in the sock's box**, making the ankle boxes the worst in the inventory | Both read far heavier than the picture's average. The sock is not at fault: the shoe is drawn too big and too high, spilling upward |

The pattern across all five: a hand or foot fails by becoming **one dark mass
where the subject holds several forms with ground between them**, and the
signature is always the same pair of numbers moving in opposite directions, ink
up and structure down. Nothing else in either inventory does that.

## The hand is a box and a wedge [read: Bridgman, Loomis]

Bridgman's *Constructive Anatomy* is the main source here, with Loomis for
proportion.

- **The palm is a box**: a slab with real thickness, a front, a back and two
  narrow sides, not a flat pad. A mitten has no thickness.
- **The thumb is a separate wedge** of muscle on the box's thumb side, and
  Bridgman puts it first: *"the mass of the thumb dominates the hand."* It is
  pyramidal at the base, narrow in the middle, pear-shaped at the end, and it
  reaches to the middle joint of the first finger, a proportion you can check
  against your measured hand rather than guess.
- **Everything is organised round the thumb's basal joint.** Spread, the fingers
  radiate from it; gathered, they form a corona around the thumb's tip; bent or
  clenched, *"each circle of knuckles forms an arch with the same common
  centre."* This is why a fist is drawn as a set of concentric arcs and not as
  four sausages side by side.
- **The hand has an action side and an inaction side.** The side carrying the
  greater angle is the action side; the other runs straight. A hand drawn
  symmetrical about its own axis has no action in it.
- **Loomis' size check:** put the heel of the palm on your chin and the middle
  finger reaches the hairline. **The hand is the length of the face.** A disc or
  an egg that is clearly smaller or larger than that fails the check, and it is
  one measurement.

### Fingers are three cylinders, and they never taper to a point

Bridgman again, and this is the part that most reliably separates a drawn hand
from a symbol:

- **Three segments per finger, two for the thumb.** In profile there is *"a
  step-down from each segment to the one beyond, bridged by a wedge"*, so the
  back of a finger is **a series of wedges and squares**, not a smooth cone.
- **The middle joint is the largest**, and the middle finger is the longest and
  largest because it opposes the thumb.
- **The finger tapers from the middle joint** and ends *"embedded in a horseshoe
  form holding the nail."* It does **not** narrow continuously from knuckle to
  tip. A finger drawn as a taper to a point is the single commonest symbol tell.
- **In back view the fingers arch toward the middle finger** as a group. They are
  not parallel and they are not a fan.
- **Knuckles run on arcs**, and the arcs are the quickest way to get four finger
  lengths right at once: sweep the arc first, then cut each finger to where it
  meets it. The second knuckle sits highest and largest.
- **Creases do not sit on the joints.** Most run across; the one opposite the
  basal joint is a single long wavy crease down the palm.

### The hand in contact

Most hands you draw are holding something. In the inventory a hand is its
fingers and its thumb, each an entry, or `_absent` says why not;
`check.py --checklist parts.json` holds it to that:

```checklist
object: hand|glove
sub-forms: finger thumb
```

A hand holding a bar, handle or tool is not a hand plus an object. It is a
**grip**, and five things decide whether it reads. A bicycle's handlebar is the
example used below; the same applies to a tool handle, a railing or a mug.

1. **The held object continues past the hand on both sides.** If hand and object
   share one silhouette you have drawn a mitten, and the box goes about twelve points darker as the
   fist and the object fuse into one shape.
2. **Leave whatever the subject leaves between them.** Usually this is a strip of
   its own ground. Where the whole passage is dark, it is a second lighter value
   instead: a handle lighter than the glove on it does the same work as a gap.
   Measure which before assuming a gap. Without it the parts check reports a box
   that got darker and can tell you nothing more.
3. **The fingers curl round and come back into view underneath.** Draw the back
   of the hand as one rounded plane, with **a row of four small arcs** below it:
   the finger tops curling forward under the tube, pale skin showing at the tips.
   Three long concentric arcs across a solid egg is a beetle, not a hand.
4. **A hand on a lever body holds the body, not just the bar.** On a
   bicycle brake hood, the glove's back covers the body's top, the fingers pass in
   front of the lever blade and wrap it, and the blade hangs from the body.
   Glove, body and blade are one connected dark shape told apart by ink and a
   lighter value, never by ground: ground between the fingers and the blade says
   the lever floats. A hand drawn beside the body instead of over it comes out about a quarter too
   small, with the fingers above the blade, and reads as tangled.
5. **The forearm's contours end inside the hand**, not eighteen pixels above it. A limb that
   stops short of what it holds is the absence failure, and only the parts gate
   against a written inventory catches it.

## The foot is a wedge with an arch [read: standard figure-drawing construction; foot-tripod literature]

This is the traditional construction, stated as the books give it and untested
here.

- **The whole foot is a wedge**: a triangular prism, thickest at the heel,
  slanting down and forward to the toes. Ankle in at the back and high; toes out
  at the front and low. The wedge gives a foot a **direction**, which a disc
  does not have.
- **The arch is a curve cut into the side of the wedge**, on the inside. From the
  front the foot is narrowest along its outer edge, which sits on the ground for
  its whole length, and rises on the inner side above the big toe. Draw both
  sides the same and you have a block, not a foot.
- **Three points of contact, a tripod:** the centre of the heel, the ball behind
  the big toe (head of the first metatarsal), and the base of the little toe
  (head of the fifth). Three arches span between them. Whatever the pose, ask
  which of the three are down; that answers where the weight is and therefore
  which way the ankle leans.
- **Toes are short prisms, tapering big to little**, with the big toe set at its
  own angle to the rest. They are not a fringe on the front of the wedge.
- The foot's own proportion check: it is about the length of the forearm, and
  seen from the side it is far longer than it is deep.

### A shoe is that wedge with a skin on it

The shoe does not replace the wedge, it clothes it. Draw only the skin and you
get a disc. Put these in:

- **A sole running the full length of the bottom.** This is the mark that turns a
  disc into a shoe. It is a single long near-straight line and the shoe's spine:
  it states the direction the wedge points, which a disc cannot.
- **A heel corner at the back.** The subject's outline turns a corner there. A
  drawing that runs through it as a curve stays well short on `form`, even after
  the sole and a second strap slot have gone in.
- **Cross-marks at the shoe's own pitch**: strap slots, seams, a laced tongue.
  Two are enough, and they must run **across** the wedge; they are what says the
  form turns. One is a decoration.
- **The shoe's mass belongs in the shoe's box.** A foot drawn a little too large
  and a little too high gets reported against the part above it, so the worst
  boxes in an inventory are often socks holding shoe. Read a bad ankle box as a
  possible shoe fault before you touch the ankle.
- **A pedal, step or ground contact is a separate dark block under the sole**,
  with its own form and contour, never absorbed into the shoe.

## Build order

1. **Say what the hand is doing, in words**: gripping a bar, resting on a
   forearm, hanging. And say which way the foot **points**. Both are decisions,
   and a generic form quietly makes both for you.
2. **The palm box and the thumb wedge**, measured, against the face for size,
   against each other for the action side. Feet: the wedge, with its heel end and
   its toe end at their measured heights.
3. **The knuckle arc**, as one sweep, before any finger exists. Feet: the sole
   line, full length, before any upper exists.
4. **Fingers as three-segment runs cut to the arc**, each with its step-down and
   its blunt end. Toes as short prisms off the front of the wedge.
5. **The contact**: where the held object passes behind the hand and reappears,
   and the **band of ground** between the two. The contour of the object must
   stop and restart, because a flat cannot hide ink.
6. **Weight last, and downward.** A hand and a foot are small forms that carry
   many edges, so they attract ink, and every hand and foot fault measured so far was a box that ended up too
   dark. Draw the interior marks at the finest weight you have and let the
   silhouette carry the form.
7. **Walk the inventory before you call it done.** A missing hand can sit next to
   marks that are all correct. The only check that sees an absence is `--parts`
   against a list written before the first mark.
