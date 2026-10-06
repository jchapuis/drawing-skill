# The bird as a solid

A bird goes wrong when it is drawn as a circle for the body, a smaller circle
for the head, a neck between them, and a leaf-shaped wing stuck on the side.
None of those shapes is in the subject. The body is an egg, the neck is hidden
inside it, and the wing is a stack of feather groups lying on the body and
tucked into it.

Everything below describes the typical bird, and **the typical bird is not the
one in front of you.** Measure the subject first. Use this file afterwards, to
ask why your measured bird differs from the typical one and whether the
difference is the species, the pose or a mistake. If a passage could be
followed with the subject covered up, you are using it wrongly. `[read: source]`
marks a claim taken from the named book.

## The ways a drawn bird fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **A neck appears** between head and body, with a waist the subject does not have | `check.py --scan` on a box across the head-to-body junction: the subject's outline widths change smoothly from head to breast; the drawing's dip and rise again |
| **The body sits at the wrong tilt**, usually too upright on a perched bird or too level on a wader | Sight the long axis of the body (crown to tail tip, or breast to rump) as an angle on the subject and on the drawing. Measure angles, do not judge them |
| **The head is too big**, a cartoon proportion | Comparative measurement: head length (beak base to back of head) against body length, both off the subject. The head almost always comes out larger than measured |
| **The beak is stuck on** at an angle that does not run through the head | Sight a line along the gape (the line where the two halves of the beak meet) and see where it ends against the eye. `check.py --zoom` on the head box, subject above and drawing below |
| **The eye floats in the middle of the head** | Measure the eye's distance from the beak base and from the crown in eye widths, on both. Most drawn eyes sit too far back and too high |
| **The wing is a leaf pasted on**, outlined all round | `check.py --overlay --box` on the wing: the subject's front edge of the folded wing is lost under the breast and flank feathers; the drawing has an unbroken contour there |
| **The wingtip stops in the wrong place** against the tail | Measure where the tip of the primaries falls as a fraction of the visible tail length, on both. This is one of the most informative numbers on a perched bird |
| **Legs as sticks from the belly**, with the joint bending the wrong way or the bird floating over its perch | `check.py --zoom` on the feet: count the toes in front of the perch and behind it, and measure the gap between belly and perch |
| **A head thrown back reads as a head turned sideways** | `look.py axis` on the beak axis, the nape line and the throat line, subject and drawing; a few degrees decide it (see § Chickens and other galliform birds) |
| **Feathers drawn one by one everywhere**, so the body reads as scales | `check.py --masses`: the subject reads as a few large values, the drawing as noise. Pattern belongs where the subject has it (wing bars, scapulars) and nowhere else |

Most of these come from drawing what a bird is known to have (a neck, a knee,
a wing) instead of what this one shows.

## The body is an egg, and the egg tilts

The body is one smooth egg, broad at the breast and narrowing to the tail. Its
tilt carries the pose: a perched songbird holds it steeply, a thrush on a lawn
nearer level, a heron at rest folds it under a hunched neck. Sibley's guides
draw each species in a standard posture so that body shape and tilt can be
compared at a glance [read: Sibley, *The Sibley Guide to Birds*]. Laws builds
every bird on a tilted egg for the body and a ball for the head, and judges the
pose by the angle of that egg [read: Laws, *The Laws Guide to Drawing Birds*].

Measure the tilt as an angle off the subject. Then check what moves it: a bird
alarmed or singing stands up; a bird feeding or about to fly leans forward. A
drawn tilt that matches no reason in the subject is an error.

The outline of the egg is not uniform. Breast feathers fluff out on a cold or
resting bird and sleek down on an alert one, so the same species can measure
round or slim. Take the subject's widths, not the species'.

## The neck is inside the feathers

A bird's neck is long and S-shaped, and on most birds at rest it is folded
down into the body and hidden by feathers [read: Laws; Sibley]. What shows is a
smooth run from the back of the head into the back, and from the throat into
the breast. A drawn waist below the head is the commonest single error on a
small bird.

The neck shows only when the bird stretches it: a heron striking, a bird
reaching for food, a duck alert on water. When the subject shows a neck,
measure its width against the head's. When it does not, do not add one.

## The head and the beak

The head is a ball, and the beak comes out of its front along one axis. Two
things fix that axis on the subject:

- **The gape line**, where upper and lower beak meet, usually runs back
  toward the eye and ends below or just in front of it. Its angle tells you
  where the beak points, and it is often a different angle from the beak's
  upper edge (the culmen) [read: Sibley, bird topography].
- **The forehead** runs into the culmen with a step, a smooth slope, or almost
  no break at all, depending on the species. Measure that profile with
  `--zoom` before choosing.

Beak length is best measured against head length, not body length. A beak
drawn too long for the head is often a head drawn too small.

**The eye** sits on the side of the head, and on most small birds it is well
forward, close to the beak base. Measured in eye widths, the gap between eye
and beak base is short. Its highlight and the dark of the iris often merge into
one dark dot at small scale: draw the value the subject shows, not the eye
you know is there. Facial marks (an eye ring, an eye stripe, a dark mask) are
often what makes the species read, so measure their position against the eye
rather than placing them by memory.

## The folded wing is layered feathers on the body

A folded wing is not a separate shape outlined on the side. Its parts overlap
in a fixed order, front to back and top to bottom [read: Sibley]:

| Group | What it does on a perched bird |
|---|---|
| **Scapulars** | Shoulder feathers on the back that cover the top of the folded wing. They often hide where the wing joins |
| **Coverts** | Rows of small feathers over the base of the flight feathers. Their pale tips make wing bars when the species has them |
| **Tertials** | The innermost long feathers, lying on top of the folded secondaries near the back |
| **Secondaries** | Mostly hidden under the tertials when folded |
| **Primaries** | The long outer feathers. Folded, they stack into one narrow point that runs back over the rump and tail |

The front of the folded wing tucks under the breast and side feathers, so its
leading edge is lost there. Drawing that edge as a firm line separates wing
from body.

**The primaries cross over the tail.** On many birds the two wingtips meet or
cross above the rump and lie along the tail; on others they stop at the base of
the tail. How far the primaries reach past the tertials (the primary
projection) varies by species and is used to tell similar species apart
[read: Sibley]. Measure the wingtip's position against the tail on the subject.
If your drawing differs, it is almost always the drawing.

## The tail

Folded, the tail is a narrow stack of feathers, so it reads as one shape with a
few edges, not as many feathers. Its length against the body changes the whole
character of the bird; measure it. Below it, the undertail coverts form a
separate pale or dark wedge on many species. Spread in flight or display, the
same feathers fan out from a single point at the rump, and the fan's outline
(square, rounded, notched or forked) is a measured shape like any other.

## Legs and feet

The joint halfway down a bird's leg that seems to bend backwards is the ankle.
The knee and thigh are inside the body, under the belly feathers [read: Laws].
So the visible leg leaves the body at the belly feathers as a thin lower leg
(the tarsus) and goes straight down to the toes. Nothing on it bends forward.

- **Where the leg leaves the feathers** is a landmark. Measure it against the
  body egg: on a perched bird it is usually under the body's widest point, so
  the bird balances over its feet. A drawn bird that would tip over has its
  legs in the wrong place.
- **Most perching birds have three toes forward and one back**, the back toe
  (hallux) opposing them to grip [read: Sibley]. Owls, woodpeckers and parrots
  show two forward and two back. Count the toes on the subject; do not supply
  the number.
- **Toes wrap the perch.** They curve round it and the claws reach its far
  side. A foot drawn flat on top of a round branch reads as standing on a pipe.
- On a fluffed or resting bird the belly feathers can hide the legs
  completely. If the subject shows no legs, draw none.

## The wing in flight is a hand

The open wing has the same bones as an arm: upper arm and forearm near the
body, then a wrist and a hand [read: Laws; Sibley]. The feathers follow the
bones:

- **Secondaries** run along the forearm and make the broad inner wing.
- **Primaries** grow from the hand and make the outer wing, narrower, and on
  many birds with gaps between the tips (the "fingers" of a soaring hawk).
- **The alula** is a small group of feathers on the thumb, on the leading edge
  at the wrist. It lifts in slow flight and on landing.

The leading edge is thick, because it carries the bones and muscle. The
trailing edge is thin feather tips. So the leading edge takes a firmer line or
a harder value edge than the trailing one. A wing drawn with equal edges on
both sides reads as a flat paper shape.

**Foreshortening.** The two wings of a flying bird are almost never the same
length on the page. One is turned toward you or away, and the bend at the
wrist turns the hand at a different angle from the arm. Measure each wing's
length from the body to the tip, and the position of each wrist, separately.
A drawing with two equal wings when the subject has unequal ones has been made
symmetrical from memory. On the upstroke the wing folds at the wrist and the
primaries can point back, so the outline changes more than the bones do;
read the bones' positions (shoulder, wrist, tip) off the subject first and
hang the feathers on them.

## A spread wing at rest, seen from the side

A bird standing with a wing held out (drying, displaying, about to flap) shows
the open wing nearly flat to the viewer. Read it as three bands stacked from
the leading edge down, in the order the feather groups lie [read: Sibley, bird
topography]:

| Band | What it looks like |
|---|---|
| **Coverts** | The top band, along the leading edge: short feathers in overlapping rows, whose lower edge is a scalloped line of rounded tips. Drawn as a straight bar, it reads as a stick |
| **Secondaries** | The middle band, along the forearm: broad feathers of about equal length, their tips a row of shallow curves. The separations run from under the coverts to the tips |
| **Primaries** | The outer band, from the wrist: longer, narrower feathers that fan out, their tips pointed and the notches between them deep. Stubby primaries with shallow notches read as a paddle |

Each band has its own value and its own edge shape, and the band edges are the
lines that make the wing read. Measure each band's width at the wrist and at
the body, and the angle of the fan, on the subject.

**Count the feathers on `--zoom`, not with `--counts`.** Wing feathers touch
and are bounded by their own ink, so `--counts` usually returns UNCHECKED for
primaries and secondaries, or counts merged groups. Count each band on the
`--zoom` of the subject and of the drawing, and write both counts into
`notes.md`.

## Chickens and other galliform birds

Chickens, pheasants, turkeys and grouse are galliform birds: a heavy body, a
small head, a short rounded wing, and strong legs for walking and scratching.
A domestic cock (rooster) reads by its head and tail far more than by its body,
so an inventory that stops at the songbird list loses it. Its parts, named as
in poultry handbooks [read: Damerow, *The Chicken Encyclopedia*]:

- **Comb**: the fleshy crest on top of the head, from the beak base back over
  the crown. A single comb is a row of points; other breeds have rose, pea or
  other combs. Count the points and measure the comb's height against the head.
- **Wattles**: the two fleshy lobes hanging under the beak. Their length
  against the head is a measured number; they swing with the head.
- **Earlobe**: a bare patch of skin below and behind the eye, often white or
  red, separate from the wattle.
- **Hackles**: long narrow neck feathers that hang over the shoulders like a
  cape. They hide the neck's join to the body and carry the head's tilt into
  the back.
- **Saddle**: long narrow feathers on the lower back, in front of the tail,
  hanging down over the sides.
- **Sickles**: the long curved tail feathers of the cock, arching up and over
  the rest of the tail. Each one is a separate stroke with its own curve;
  drawn as one mass, the tail reads as a blob.

A hen has a smaller comb and wattles, short hackles and saddle, and no sickles.

**The crowing pose.** A crowing cock stands upright, stretches the neck, throws
the head back and opens the beak with the beak pointing up. "Head thrown back"
is carried by a few angles, each two points typed into `look.py axis`
(`--seg NAME:subject/render`):

1. **The beak axis against horizontal**: the upper edge (culmen) from the
   forehead to the tip, and the lower mandible from the gape's corner to its
   tip. Their difference is how wide the beak is open.
2. **The nape**, in two pieces, since it curves: the back of the skull to the
   top of the hackles, then down the hackles to the shoulders. The lower piece's
   lean from vertical says how far the neck is stretched back.
3. **The throat line**, from under the lower mandible down the front of the
   neck to the breast.
4. **The beak against the nape** (`--pair beak,nape`): the head's angle on the
   neck, the number that says "thrown back" rather than "looking ahead".

A lift a few degrees short of the subject's on any of these reads as a head
turned sideways with the beak open, and no other numeric gate sees the
difference. As an example, on a printed crowing cock and a drawing of it
described as "in profile, looking left", these angles all came within about 7°
of the subject's (beak against nape 98° on the subject, 105° on the drawing;
the beak's upper edge 2° below horizontal against 3° above). Match them to a
couple of degrees. When they already match and the clause still fails, measure
the angles of what sits on the head next: the comb's lean, the wattle's swing,
the eye's long axis. At stage 0, write the angles in `reading.md`, measured.
At stage 4 and at the final gate, measure them again on the render and match
them; a describer run on the head crop says whether the pose now reads. A pose
clause that fails is an angle to measure, not a shape to redraw.

On that same crowing cock, what moved the reading from "in profile, looking
left" to "head raised, looking up, as if crowing" was not the head's angles but
three features on it: the eye (a narrowed almond tilted along the beak, about
−57°, where the drawing had a round upright eye at −88° that read as alert), the
wattle (thrown forward and out by the raised head, its fold at +30°, where the
drawing's hung straight down), and the open lower beak (two pointed spikes, not
a blunt box). The expression of the features carries the effort of the pose:
measure each one's long axis with `look.py axis` before redrawing anything.

```checklist
object: bird|rooster|cockerel|hen|chicken|pheasant|turkey|duck|goose|swan|owl|eagle|hawk|falcon|parrot|pigeon|dove|gull|heron|sparrow|finch|robin|crow|raven|magpie|songbird
sub-forms: beak|bill eye head body wing primaries|primary tail leg foot|feet
```

```checklist
object: rooster|cockerel|hen|chicken
sub-forms: comb wattle
```

## Where a bird meets other things

| Contact | What is in front |
|---|---|
| **Foot on a branch** | The near foot's front toes pass in front of the branch; the hallux passes behind it or under it. The far foot sits behind the branch and is often hidden. Write the branch before the near toes and after the far foot |
| **Belly over the perch** | On a fluffed bird the belly feathers hang in front of the perch and hide the legs. The perch's line stops at the feathers and restarts beyond them |
| **Tail and perch** | The tail can hang in front of the branch or behind it. Read it off the subject; it decides which line is broken |
| **Bird in foliage** | Leaves and twigs in front cut the bird's outline. Each cut is a row in the overlaps table, or the bird gets drawn whole and the leaves pasted on top |
| **Bird on water** | The waterline cuts the body flat, and the part below is either hidden or seen as a reflection, which is a separate shape with its own values |
| **Bird on the ground** | A small cast shadow under the feet ties it to the ground. Without it, a standing bird floats |
| **The far wing in flight** | Passes behind the body; the body's outline is drawn over it. Write the far wing first |

The canvas paints in the order marks are written, so a nearer form hides a far
one only when the far one is written first. Record each crossing in the
overlaps table with its `in_front` entry, and `check.py --depth` will check the
write order against it.

## Build order

1. **The body egg**, as a measured length, width and tilt. It is the largest
   form and everything else is placed against it.
2. **The head**, measured against the body, placed where the subject puts it,
   with no neck unless the subject shows one.
3. **The beak axis and the eye**, off the gape line, at the same stage as the
   head. A head that is tilted or thrown back gets its angles (§ Chickens and
   other galliform birds) measured with `look.py axis` here.
4. **The folded wing as one mass on the body**, with the wingtip placed by its
   measured position on the tail. In flight, the shoulder, wrist and tip of
   each wing first.
5. **The tail**, measured against the body.
6. **Legs and feet**, from where they leave the feathers to the toes around
   the perch, with the perch drawn at the same stage.
7. Feather groups, wing bars and facial marks last, only where the subject
   has them. A galliform's comb and wattles go in with the head (step 3) and
   its sickles with the tail (step 5): they are what makes it read.
