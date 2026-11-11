# Hands and feet

Hands and feet are small forms with many edges, and they are easy to draw
badly. A bad hand is usually either a dark disc with a few stripes ruled across
it, at the end of a forearm that stops short of it, or two hands merged into one
egg. A bad foot is a disc where the shoe should be, because the drawing never
decided which way the foot points. Every mechanical gate can pass these, because
nothing drawn is wrong: something is missing, and a missing form has no pixels
to measure.

## Contents

- The schema is a diagnostic, never a scaffold
- The five ways a drawn hand or foot fails
- The hand is a box and a wedge [read: Bridgman, Loomis]
- The foot is a wedge with an arch [read: standard figure-drawing construction; foot-tripod literature]
- Build order

## The schema is a diagnostic, never a scaffold

Everything below describes the **average** hand and foot, which are not the ones
in front of you. **Do not build on it.** Build on landmarks measured from the
subject, and use what follows only afterwards, to ask whether a difference from
the average comes from the grip, the foreshortening, the glove or a mistake.

This matters more here than elsewhere, because a hand is almost never seen in
its textbook pose. It is wrapped round a bar, hanging off a wrist, jammed in a
pocket, or at forty-five degrees to the picture plane with three fingers hidden.
Every schema teaches the open palm with five radiating fingers, and you will
rarely draw it. If you supply that form at the stage meant for finding the
particular one, every part lands inside its correct box and the result is still
not a hand. The same holds for a foot, which in practice is a **shoe** on a
pedal, a step or the ground, at an angle.

If you could follow a passage below with the subject covered up, you are using
it wrongly. `[read: source]` marks a claim from the named book or tradition, not
yet tested here; untagged rules come from measured failures.

## The five ways a drawn hand or foot fails

The measurements come from `check.py --parts`. `ink` is the share of dark pixels
in the box. `form` is the share that differs from the box's own local ground,
which measures how much structure the box holds.

| The fault | The measurement that finds it |
|---|---|
| **The hand is not there**: a disc, a few ruled stripes, and a forearm ending in mid-air | `form` drops to about **two-thirds** of the subject's, among the worst boxes in the inventory. The fix is a back sitting **on** the handle, four fingers hanging below it and curling forward under the tube, and the forearm's two contours **ending inside it** |
| **The mitten**: two hands become one egg-shaped dark mass crossed by long concentric arcs, the finger loops a scribble that never resolves | `ink` rises about twelve points while `form` falls thirty: **darker and emptier at once**, one mass replacing several forms |
| **Fist and handle merged** into a single dark shape | `ink` again about twelve points high in that box. The subject separates them with a **band of its own ground**, or, where the whole passage is dark, a **second lighter value**. Two objects that touch still need something that shows they are two |
| **The shoes are discs** | `ink` high and `form` low together. It is fixed when a **sole running the full length of the bottom** and a **second strap slot** go in, and the outline has a **heel corner** where a disc has a curve |
| **The shoe's mass lands in the sock's box**, making the ankle boxes the worst in the inventory | Both measure far heavier than the picture's average. The sock is not at fault: the shoe is drawn too big and too high, spilling upward |

All five share one pattern: the hand or foot becomes **one dark mass where the
subject has several forms with ground between them**, and the sign is always the
same pair of numbers moving in opposite directions, ink up and structure down.
Nothing else in either inventory does that.

## The hand is a box and a wedge [read: Bridgman, Loomis]

The main source is Bridgman's *Constructive Anatomy*, with Loomis for
proportion.

- **The palm is a box**: a slab with real thickness, a front, a back and two
  narrow sides, not a flat pad. A mitten has no thickness.
- **The thumb is a separate wedge** of muscle on the thumb side of the box, and
  Bridgman puts it first: *"the mass of the thumb dominates the hand."* It is
  pyramidal at the base, narrow in the middle and pear-shaped at the end, and it
  reaches the middle joint of the first finger, a proportion you can check on
  your measured hand.
- **Everything is organised round the base joint of the thumb.** Spread, the
  fingers radiate from it; gathered, they cluster around the thumb's tip; bent
  or clenched, *"each circle of knuckles forms an arch with the same common
  centre."* This is why you draw a fist as a set of concentric arcs, not four
  sausages side by side.
- **The hand has an action side and an inaction side.** The side with the
  greater angle is the action side; the other runs straight. A hand drawn
  symmetrical about its own axis has no action in it.
- **Loomis' size check:** with the heel of the palm on the chin, the middle
  finger reaches the hairline, so **the hand is the length of the face**. One
  measurement tells you if a disc or egg is clearly too small or too large.

### Fingers are three cylinders, and they never taper to a point

Also from Bridgman. This is what most reliably separates an observed hand from
a symbol of one:

- **Three segments per finger, two for the thumb.** In profile there is *"a
  step-down from each segment to the one beyond, bridged by a wedge"*, so the
  back of a finger is **a series of wedges and squares**, not a smooth cone.
- **The middle joint is the largest**, and the middle finger is the longest and
  largest because it opposes the thumb.
- **The finger tapers from the middle joint** and ends *"embedded in a horseshoe
  form holding the nail."* It does **not** narrow steadily from knuckle to tip.
  A finger tapering to a point is the commonest sign of a symbol.
- **Seen from the back, the fingers arch toward the middle finger** as a group,
  neither parallel nor fanned.
- **Knuckles run on arcs**, the quickest way to get four finger lengths right at
  once: sweep the arc first, then cut each finger where it meets it. The second
  knuckle sits highest and is the largest.
- **Creases do not sit on the joints.** Most run across; the one opposite the
  basal joint is a single long wavy crease down the palm.

### The hand in contact

Most hands you draw are holding something. In the inventory, a hand's fingers
and thumb are each an entry, or `_absent` says why one is not;
`check.py --checklist parts.json` enforces this:

```checklist
object: hand|glove
sub-forms: finger thumb
```

A hand holding a bar, handle or tool is a **grip**, one form, and five things
decide whether it reads as one. The example below is a bicycle handlebar; the
same applies to a tool handle, a railing or a mug.

1. **The held object continues past the hand on both sides.** If hand and object
   share one silhouette, you have drawn a mitten, and the box goes about twelve
   points darker as fist and object fuse into one shape.
2. **Leave whatever the subject leaves between them.** Usually this is a strip of
   its own ground. Where the whole passage is dark, it is a second, lighter value
   instead: a handle lighter than the glove on it does the same work as a gap.
   Measure which one the subject has before assuming a gap. Without either, the
   parts check only reports a box that got darker.
3. **The fingers curl round and come back into view underneath.** Draw the back
   of the hand as one rounded plane, with **a row of four small arcs** below it:
   the finger tops curling forward under the tube, pale skin showing at the tips.
   Three long concentric arcs across a solid egg look like a beetle.
4. **A hand on a lever body holds the body, not just the bar.** On a bicycle
   brake hood, the back of the glove covers the top of the body, the fingers pass
   in front of the lever blade and wrap it, and the blade hangs from the body.
   Glove, body and blade form one connected dark shape, separated by ink and a
   lighter value, never by ground: ground between the fingers and the blade
   makes the lever float. A hand drawn beside the body instead of over it comes
   out about a quarter too small, with the fingers above the blade, and looks
   tangled.
5. **The forearm's contours end inside the hand**, not eighteen pixels above it.
   A limb that stops short of what it holds is a missing form, and only the
   parts gate against a written inventory catches it.

## The foot is a wedge with an arch [read: standard figure-drawing construction; foot-tripod literature]

This is the traditional construction as the books give it.

- **The whole foot is a wedge**: a triangular prism, thickest at the heel,
  slanting down and forward to the toes, with the ankle high at the back and the
  toes low at the front. The wedge gives a foot a **direction**, which a disc
  does not have.
- **The arch is a curve cut into the inner side of the wedge.** From the front,
  the foot is lowest along its outer edge, which sits on the ground for its
  whole length, and rises on the inner side above the big toe. If you draw both
  sides the same, you get a block.
- **Three points of contact, a tripod:** the centre of the heel, the ball behind
  the big toe (head of the first metatarsal), and the base of the little toe
  (head of the fifth), with three arches between them. In any pose, ask which of
  the three are down: that tells you where the weight is, and so which way the
  ankle leans.
- **Toes are short prisms, tapering from big to little**, with the big toe at
  its own angle to the rest, not a fringe on the front of the wedge.
- The foot's proportion check: it is about the length of the forearm, and from
  the side it is far longer than it is deep.

### A shoe is that wedge with a skin on it

The shoe covers the wedge; it does not replace it. If you draw only the
covering, you get a disc. Put these in:

- **A sole running the full length of the bottom.** This mark turns a disc into
  a shoe. It is one long, nearly straight line, the shoe's spine, and it shows
  the direction the wedge points.
- **A heel corner at the back.** The subject's outline turns a corner there. A
  drawing that rounds it into a curve stays well short on `form`, even after the
  sole and a second strap slot are in.
- **Cross-marks at the shoe's own angle**: strap slots, seams, a laced tongue.
  Draw two, running **across** the wedge, to show the form turning. One alone
  looks like decoration.
- **The shoe's mass belongs in the shoe's box.** A foot drawn slightly too large
  and too high is counted against the part above it, so the worst boxes in an
  inventory are often socks holding shoe. Treat a bad ankle box as a possible
  shoe fault before you touch the ankle.
- **A pedal, step or ground contact is a separate dark block under the sole**,
  with its own form and contour, never absorbed into the shoe.

## Build order

1. **Say in words what the hand is doing** (gripping a bar, resting on a
   forearm, hanging) and which way the foot **points**. If you do not decide,
   a generic form decides for you.
2. **Draw the palm box and the thumb wedge**, measured against the face for size
   and against each other for the action side. For feet, draw the wedge with its
   heel and toe ends at their measured heights.
3. **Draw the knuckle arc** as one sweep before any finger. For feet, draw the
   full-length sole line before any upper.
4. **Draw fingers as three-segment runs cut to the arc**, each with its
   step-down and its blunt end, and toes as short prisms off the front of the
   wedge.
5. **Draw the contact**: where the held object passes behind the hand and
   reappears, and the **band of ground** between the two. The object's contour
   must stop and restart, because a flat cannot hide ink.
6. **Set line weight last, and keep it light.** Hands and feet have many edges, so they
   attract ink, and every hand and foot fault measured so far was a box that
   ended up too dark. Draw interior marks at your finest weight and let the
   silhouette carry the form.
7. **Walk the inventory before you call it done.** A missing hand can sit next to
   marks that are all correct, and the only check that sees an absence is
   `--parts` against a list written before the first mark.
