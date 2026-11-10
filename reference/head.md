# The head as a solid

An oval with features on it fails because an oval has no side plane, no back and
no thickness at its edge. The head's outline is the edge of a volume that
continues out of sight, so draw the volume and let the contour follow from it.

## Contents

- Two masses and a hinge
- Bony landmarks and what they do on the surface
- The schema is a diagnostic, never a scaffold
- The Loomis construction
- Planes
- Features are solids
- Build order for any angle

## Two masses and a hinge

Before any feature, the head is three pieces:

- **Cranium**: a large, round, thin-shelled ball, the top and back of the head.
- **Facial mass**: a smaller *wedge* hung on the lower front quarter of that
  ball, carrying the eye sockets, nose and upper jaw.
- **Mandible** (lower jaw): hung underneath from a hinge near the ear. It is a
  separate tapered piece, which is why it opens.

Do not merge these into one oval. Decide, in order: the cranial ball's size and
tilt → where the facial wedge attaches and at what angle → the width of the
zygomatic arch (this sets the face's width, *not* the cranium) → the mandible's
hinge and its gonial angle.

## Bony landmarks and what they do on the surface

| Landmark | What it governs |
|---|---|
| **Brow ridge** | The shelf the eyebrows sit on and the ceiling over the eye, which is why the upper lid sits back in shadow. The two arches look like a stretched M |
| **Temporal line** | The plane break where the side of the skull stops being a wall and becomes a roof |
| **Zygomatic arch** | The face's width. It stands clear of the skull with a gap behind it; the cheekbone is this arch pushing the skin out |
| **Orbital socket** | A **rhombus with rounded corners**, not a circle: frontal bone on top, maxilla at the inner lower side, zygomatic at the outer lower side. This is why an eye looks diamond-like, its inner corner pulled down and pointed, its outer corner rounder |
| **Nasal spine / maxilla** | How far the nose root stands off the face, and how far the mouth pushes forward |
| **Gonial angle** | The rear corner of the jaw: square or tapered |
| **Mastoid process** | The knob behind the earlobe that the neck's front muscle runs to. Without it, nothing visible attaches the neck |
| **Occiput** | The bulge at the back of the skull. Leaving it out makes 3/4 heads look front-heavy and cut off |

## The schema is a diagnostic, never a scaffold

Everything in this section describes the average head, which is not the one in
front of you. **Do not build on it.** Build on landmarks measured from the
subject, and use what follows only afterwards, to ask whether a difference from
the average is the character or a mistake.

The order matters. A head built on a ready-made ball, with a centre line down
the middle and equal thirds hung off it, comes out as a competent generic head
at the subject's size: every feature inside its correct box, every box within a
few pixels, and no likeness. The checks miss this because they compare marks,
and the marks are where you meant them to be.

**State the turn first.** How far is the head rotated, and which way? That
decides where the centre line goes, and it is not down the middle of the box: on
a three-quarter head it runs down the nose, close to the far edge of the face.
If you default to a frontal head, you get a face seen front-on with the nose
stuck to one side. Write the rotation down, place the centre line where the
rotation puts it, and only then hang anything on it.

## The Loomis construction

1. **Cranial sphere**: the brain case only. Draw it **bigger than feels
   natural**. Making it too small is the commonest error, and it stretches the
   jaw later.
2. **Cross it** with a centre line and a brow line, both drawn as bands
   *wrapped around the ball*, never as straight bisectors of a flat circle.
3. **Cut the side plane**: a flattened patch on each side, about **2/3 of the
   ball's diameter**, at the **temple**. Putting this cut at the eye makes a
   3/4 head look like a flat disc.
4. **Hang the tapered jaw block** below, measured against the sphere's radius.
5. **Four guides**: hairline, brow, nose base, chin.
6. Features last.

### The average head, for comparison only

Compare these numbers with the ones you measured, so you can name how the
subject differs. None of them describes anyone in particular.

- Vertical thirds, **equal**: hairline→brow, brow→nose base, nose base→chin.
- Hairline sits halfway between brow and the top of the sphere.
- Eye line = vertical midpoint of the whole head; eye-line-to-chin = half the
  head height.
- **Five eye-widths across the brow line**: margin, eye, one-eye gap, eye, margin.
- Nose width ≈ distance between the inner eye corners.
- Bottom of the lower lip sits halfway between nose base and chin.
  Mouth slightly wider than the nose, roughly to the inner iris positions.
- Ear top on the brow line, ear bottom on the nose base, behind the jaw.

A specific character is defined by how it *differs* from these. Measure the
difference instead of judging it by eye, and exaggerate it instead of inventing
something else. See `measuring.md`.

### Under turn and tilt

- Rotate the sphere **in your head first**, then redraw every guide as a line
  wrapped around the rotated ball.
- **3/4 turn**: the centre line bulges toward the side turning away; the brow
  line curves the opposite way, like an equator on a tilted globe.
- **The far side compresses.** The near half shows more width; the far eye is
  narrower, closer to the centre line, and partly hidden behind the nose bridge
  and the side-plane edge.
- **Yaw and pitch behave differently**: on a horizontal turn the centre line keeps
  its length and slides sideways while the eye line narrows; on a vertical tilt
  the centre line foreshortens while the eye line keeps its width.
- **Ear-base / nose-base rule**: at eye level they sit on one horizontal. With
  the head tilted back, the nose base rises above the ear base; tilted forward,
  it drops below. The gap grows with the angle.

### The head against the shoulders

Whether a head turns on the shoulders or with them shows in a few angles, not
in the head's own shapes: a face with every feature in place can still be read
as "head turned, torso facing forward" when the subject looks back over its
shoulder. Measure with `look.py axis` (two points per line, subject then
render):

- **The eye line against the shoulder line**: the head's turn and tilt against
  the torso's.
- **The centre line** (between the eyes to the chin) against the torso's
  centre-front line.
- **The sternomastoid**, from behind the earlobe to the pit of the neck, the
  cord that shows the head turning on the neck (§ Bony landmarks, mastoid).
- **The chin line**, chin to the pit of the neck, against the near half of the
  shoulder line; the two are close to one line when the chin is over the near
  shoulder.

`figure.md` § A turned torso covers the torso's side (the foreshortened
shoulder line, the far shoulder lower and narrower). Write these angles in
`reading.md` at stage 0 and check them at stage 4 and at the final gate. When
the describer misses the pose, correct the angle that is off before redrawing
any shape.

## Planes

There are four broad planes: **front** (forehead, eyes, nose front, mouth,
chin), **side** (temple through cheek to jaw), **top** (crown) and **bottom**
(under chin, nostrils, brow, lower lip, usually in shadow). Every plane edge is
a value break.

The plane breaks to draw:

1. **Temple/side plane**: anchored by hairline, nose base, temple corner and back
   of skull; visible where the pointed end of the brow turns the corner.
2. **Zygomatic plane**: a strip from the jaw joint forward to the nasal base.
3. **Forehead front-to-side**: S-curves up from the cheekbone's side plane to
   the socket edge, angling in to a **keystone** at the glabella.
4. **Nose**: top, two sides, bottom.
5. **Under the jaw**: the bottom plane.

**The nose-to-chin staircase.** In profile, the front of the face from nose base
to chin is a run of alternating steps: nose bottom (down) → philtrum (down) →
upper lip edge (up) → lower lip (up) → chin groove (down) → chin boss
(forward/up). From the front, these show as alternating dark and light bands. A
mouth drawn as one flat line misses them.

## Features are solids

### Eye
A **sphere in a socket**, with the lids as **two bands of real thickness wrapped
over it like caps**. The upper lid has 3 planes, the lower 2. Because the lids
have thickness, the upper shows a shadowed under-plane and the lower a lit top
plane.

Build: brow-ridge box tilted back → a second box below, sloping to the
cheekbone → drop the eyeball in → block the socket opening as one shape → treat
lids, sclera and iris as one shape to fix placement → only then separate the lid
bands.

*Symbol signs* (marks of an eye drawn from a remembered symbol instead of the
subject): a flat almond outline;
lids as a single line with no thickness; upper and lower lids mirror-symmetric,
when **the upper lid's peak sits toward the nose and the lower lid's toward the
ear**; the iris a perfect circle at any angle instead of a perspective ellipse;
the white of the eye flat with no gradient.

**Measure every face's eyes, not only the main one.** Expression depends on the
eye's height over its width and on where the pupil sits inside it (centred,
low, looking aside), on a secondary face, an animal or a cartoon character too:
a cat drawn with round eyes and pupils pushed to the side looks startled or
comic, whatever the subject's expression. For each face in the inventory,
measure both on the subject with `look.py grid` or `probe` (the pupil as a
fraction of the eye's width and height), write them down, and check them on the
drawing before leaving the part.

### Nose
A wedge with **four planes** (top, two sides, bottom) carrying a **ball**
(two cartilage halves hooking under at the septum) and two **wings** curling
under and around.

Build: bridge (bone above, cartilage below, meeting the glabella keystone) →
the major box → the ball with its own top/front/bottom → the wings → minor plane
breaks last.

*Symbol signs:* a flat silhouette outline; nostrils as two dots with no wing
volume; septum and wings not tucked under, so the nose sits on the face instead
of growing out of it.

### Mouth
Lips are stretched over a **cylinder standing in for the dental arch**, like a
short wide can, and its curvature pushes the lip surface out.

Build: fix the tooth cylinder's tilt and diameter → upper lip as **three
pillows** (central lobe with the philtrum, two side lobes) → lower lip as **two
pillows** with a shadowed pillar between → the **tubercle** (the central wedge
pushing down between them, not a flat cupid's-bow line) → pinch the corners as
bean-shaped nodes, never line-ends → check for overlaps between lip forms, which
make the mouth recede.

*Symbol signs:* one curved line with two humps sitting flat on the face; no wrap
around the cylinder; no difference between the upper lip's downward-facing plane
and the lower lip's upward-facing one, which take light in opposite ways.

### Ear
A **bowl**. Helix (the rim, a "?" with the lobe as its dot),
antihelix (an interior "Y"), tragus and antitragus (two beads across a U-notch),
concha (the deep central bowl), lobule (soft, about **1/3 of ear height**).

Use a heavier line on the outer helix (real cartilage bulk) and a thinner one on
the interior folds. When the head tilts, the ear moves to keep perspective:
higher on a down-tilt, lower on an up-tilt.

*Symbol signs:* a comma or backwards 6 with no interior; no depth in the concha,
so the ear lies flat instead of standing off as a bowl.

## Build order for any angle

1. Decide eye level, and the head's yaw (turn) and pitch (tilt) against it.
2. Build the cranial ball or skull box **already rotated** to that angle.
3. Wrap the centre and brow lines around it as curves, never as straight lines.
4. Put the side-plane cut at the **temple**.
5. Fix the tilt of the eye, nose and mouth lines with the ear-base/nose-base
   rule *before* drawing any feature.
6. Draw features last, each with its own foreshortening: eyes thin toward a
   line in profile; the nose hides more of the far eye as the head turns (how
   much is a direct measure of the turn); lips come *forward off* the face in
   profile, never flattened onto the cheek plane.
