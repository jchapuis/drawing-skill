# The figure as masses

A figure is usually the largest object in the picture and the one most often
drawn badly. The inventory, the form ratio, the describer and a zoom all look at
it, and all of them will pass a figure with no shoulder and no hip, because a
figure goes wrong at the joints between its parts and every check measures the
parts.

## Contents

- The seven ways a drawn figure fails
- The schema is a diagnostic, never a scaffold
- Three masses and a spine [read: Bridgman, Loomis]
- The shoulder girdle rides on the ribcage [read: Bridgman, Goldfinger]
- A turned torso, and a look back over the shoulder [read: Bridgman, Goldfinger]
- Where the thigh leaves the pelvis [read: Bridgman]
- Proportion: the unit is the head, and what you measure is a segment [read: Loomis]
- A limb's contour is the masses under it [read: Bridgman]
- Foreshortening: do not reason about length [read: Loomis, Hogarth]
- A seated, braced figure [read: bike-fit literature]
- Cloth on the figure
- A small figure is still a whole figure
- Build order

## The seven ways a drawn figure fails

To find these faults, classify each pixel as ink, garment, skin or ground, and
measure the runs of each class across named rows. None of the faults is visible
at 1:1, so each one is listed with the measurement that catches it.

| The fault | The measurement that finds it |
|---|---|
| **The body encloses no space.** Where a limb hangs forward from the shoulder, the subject shows a wedge of ground between the dark of the garment and the pale of the limb | Measure that gap on ten rows. A subject keeps it for hundreds of px in total. A drawing with this fault often has **zero on every row**, its dark running unbroken across the whole torso |
| **The garment over the hips is a kidney shape**: no buttock corner, no seat contact, no leg opening, one smooth boundary at top and bottom | Its forward edge overshoots the subject's by a large fraction of the torso's width, which also closes the gap in the row above. Measure the forward edge against the subject's on the same row |
| **The arm has no elbow**: one tube from shoulder to hand | Trace the back contour. A subject's stays near vertical, then **breaks 20-30 px sideways within 30 rows**, a corner of about 40°. A drawing without an elbow drifts a few px and never breaks |
| **A third pale limb**: an unexplained contour that splits one arm lengthwise into two thin ones | Count skin runs across the arm on a dozen rows: three where the subject has two (§ A limb's contour) |
| **The legs are straws**: no calf, no ankle | Measure the shin at the calf and the ankle. The subject's swells by half at the calf and narrows at the ankle; the drawn leg keeps one width |
| **One sleeve line for two arms** | A subject's two hems sit at *different heights*, because the two arms are at different depths. A single straight ink line across both flattens them onto one plane |
| **A limb that ends in no hand or foot**, and a folded forearm drawn as a slab of constant width with a squared end | See `hands-and-feet.md`. A wrist-worn object drawn as a disc laid on top, instead of a band that runs round the wrist, is the same fault at a smaller scale |

**The bounding box can be right while the figure is wrong.** A garment's box
can match the subject's to within two pixels on a shape with no shoulder in it,
and the parts check will report a median form ratio near 1.0 with nothing
missing, because no box contains a joint. If the inventory has no shoulder, hip,
elbow or knee (and often no upper arm, because one box runs from sleeve to
hand), the check cannot report them missing.

So fix the inventory, not the marks. What makes an inventory better is more
joints, not finer division. If you split surfaces further but drop `upper arm`
and `elbow` from the list, the drawing gets worse and the parts check will not
say so.

## The schema is a diagnostic, never a scaffold

Everything below describes the **average** figure, which is not the one in front
of you. **Do not build on it.** Build on landmarks measured from the subject,
and use what follows only afterwards, to ask whether a difference from the
average comes from the pose, the person, the clothing or a mistake.

This matters most for the figure because its canon is arithmetic: "eight heads,
crotch at the halfway point, elbow at the navel" can be met with a ruler, and a
figure that meets every number can still look like nobody. Loomis, who wrote the
canon most artists use, says so in the same book:

> *"If you are accustomed to measuring off so many heads, you must discard the
> method in drawing the reclining figure… **Measurements are not standard and
> apply only to the subject before you.**"* And, of his own block forms,
> *"Never fit a box around anything that is an interpretation of life."*

If you could follow a passage below with the subject covered up, you are using
it wrongly. `[read: source]` marks a claim from the named book or paper, not yet
tested here; untagged rules come from measured failures.

## Three masses and a spine [read: Bridgman, Loomis]

Only three parts of the body are rigid: the **head**, the **ribcage** and the
**pelvis**. The pose is the three relations between them, so state it as three
measured angles, not one outline. A hunched figure bends in one short place
between ribcage and pelvis, not evenly along a curve. Two masses of different
proportion **wedge into each other** instead of sitting end to end.

**What to measure.** Measure the long axes of the ribcage and of the pelvis as
two separate angles on the subject, then their difference. If you cannot name
two different angles, you have not looked at two masses, and you will draw one
bag.

## The shoulder girdle rides on the ribcage [read: Bridgman, Goldfinger]

A missing shoulder is more than a missing bump on an outline: the drawing has
merged two structures, shoulder and ribcage, that are not attached to each
other.

- **The collarbone is the arm's only bony connection to the trunk.** Bridgman:
  the clavicle *"expresses an important spring function, it being the only bony
  union of arm and shoulder with the trunk."* The shoulder blade, the shoulder
  mass and the arm hang in muscle against the **outside** of the ribcage and
  slide on it.
- **The shoulder blade is a plate on a barrel**, *"a flat plaque of bone fitting
  snugly against the cage of the thorax"*. Its outer corner is the
  **acromion**, the hard point at the top of a shoulder (Goldfinger's *Human
  Anatomy for Artists* shows how these appear on the surface). The arm hangs
  from that point, above and outside the ribcage, never from the ribcage's own
  silhouette.
- **The deltoid is a wedge**: a block *"with its long diameter
  sloping down and out, beveled off at the end"*, which *"lies diagonally across
  and overlaps the mass of the arm"*, its *"apex sink[ing] into the outer groove
  of the arm half way down."* Because it overlaps the arm, a shoulder reads as a
  **corner**, and a sleeve has to turn one too.
- `quadruped.md` says the opposite for the same reason: a cow has **no**
  clavicle, so its front end hangs between two shoulder blades with nothing
  bracing them apart, and its shoulders are narrow. The clavicle is what pushes
  a human's shoulders out wide.

**What to measure.** Find where the arm's silhouette *leaves* the torso's, and
measure the ground between them as a negative shape (see `measuring.md`); you
have no preconceived idea of a gap's shape, so you see it accurately. It is
usually a wedge, widest near the shoulder and closing to nothing at the wrist.
**Zero ground between torso and arm is the mitten failure at figure scale**,
diagnosed as `hands-and-feet.md` diagnoses a fist merged with a bar.

## A turned torso, and a look back over the shoulder [read: Bridgman, Goldfinger]

A turned pose depends on a few angles, and a few degrees change how the
describer reads it: with every shape close, a figure looking back over its
shoulder can still be described as "torso facing forward, head turned". A turned
torso shows on the surface like this:

- **The shoulder line foreshortens.** When the ribcage turns away, the far half
  of the shoulder line (pit of the neck to the far acromion) is shorter than the
  near half. Seen from about shoulder height, the far shoulder usually also sits
  lower, partly hidden by the neck, the hair or the near shoulder.
- **The centre-front line moves toward the far edge**, as on a turned head
  (`head.md` § The schema is a diagnostic): the pit of the neck, the breastbone
  and a garment's front opening run close to the far contour. A collar drawn
  symmetric about the neck says the torso faces you.
- **The sternomastoid shows on the neck.** This muscle runs from the knob behind
  the ear (the mastoid) to the pit of the neck. When the head turns, the one on
  the side away from the turn stands out as a diagonal cord, which Bridgman and
  Goldfinger both use to show the head turning on the neck instead of the whole
  figure turning.
- **The chin comes over the near shoulder**, so in the picture the chin, the
  pit of the neck and the near half of the shoulder line fall close to one line.

**What to measure: the angles that show "looking back over the shoulder".**
Enter two points for each with `look.py axis` (`--seg NAME:subject/render`):

1. **The near half of the shoulder line**, from the pit of the neck to the top
   of the near shoulder: its angle, and its length against the eye spacing.
2. **The eye line against the shoulder line** (`--pair eyes,shoulder`): the
   head's turn and tilt against the torso's.
3. **The sternomastoid**, from earlobe to the pit of the neck.
4. **The chin line**, from chin to the pit of the neck, against the near
   shoulder line (`--pair chin,shoulder`). It is near 0° when the chin is over
   the shoulder.

When the turn is large, add the torso's centre-front line (pit of the neck to
the waist or a garment's front opening). For example, in a painted portrait of
a woman looking back over her shoulder, the subject's chin line lay within 1° of
the near shoulder line. A drawing with every shape close put the chin line 10°
above it and the near half-shoulder at 1.52 eye spacings against 1.35, and was
described as facing forward, though its other three angles were within 2°.

**When to measure.** At stage 0, measure these angles on the subject and write
them in `reading.md`. At stage 4 and at the final gate, run `look.py axis` again
with the render's points after the slash, and match them. If the describer
misses part of the pose, measure and correct an angle; do not redraw a shape.

## Where the thigh leaves the pelvis [read: Bridgman]

The pelvis is a **bucket** with a rim, a front, a back and a closed bottom. In a
seated figure it is the only mass carrying weight. The leg does not leave from
the bottom of it:

> *"[The femur] is joined to the bones of the pelvis at the hip socket by a long
> neck, which carries the shaft itself out beyond the widest part of the crest.
> From there the femora converge as they approach the knees, bringing the knee
> under the hip socket."*

The thigh leaves from the **side**, swings out past the widest point, and comes
back in. The surface landmark is the **great trochanter**, *"the upper tip of
the shaft which reaches up slightly beyond where the neck joins."* That knob
makes a hip; a smooth arc from waist to thigh says there is none.

- **A leg opening is a cross-contour** (a line that wraps the form), not the
  edge of the dark mass. It follows the thigh's perspective like a band around
  a barrel (see "Cloth on the figure"). The near opening is a diagonal hem
  across the thigh; the far one sits higher and at a different angle, because
  the legs are at different phases and depths. **Always draw two openings.**
- **A seat is a contact, so draw it**: its own dark wedge, its own contour, and
  a break between it and the body.
- Bridgman on the thigh's mass: *"inclined inward from hip to knee, and…
  slightly beveled toward the knee from front, back and outside."* It is widest
  at the root and tapers into the joint. A thigh of constant width, or one that
  widens toward the knee, is wrong.

**What to measure.** Measure each leg opening's height and angle separately,
and where the forward edge of the dark mass sits against the landmarks of the
seat. An overshooting forward edge shows up as a missing gap elsewhere in the
figure, often far from the garment.

## Proportion: the unit is the head, and what you measure is a segment [read: Loomis]

A canon based on total height stops applying when the figure stops standing,
as it does in most pictures. Three of Loomis's statements still hold, because
they concern a limb's *own* length and can be checked on a folded figure by
asking where the joint would fall if the limb hung down: the elbow at the navel,
the wrist at the crotch, the knee just above the lower quarter. The rest
describes nobody in particular.

So the unit is the **head**, and you measure a **segment** against it, never the
whole figure: crown to sole on a figure bent double gives something like 3.2
heads, which means nothing. Two further limits apply. **Headgear is not part of the head**, so measure the
unit both with and without it, or every proportion shifts. And **a cartoon has
its own canon**, so measure how far the subject departs from *its own internal
ratios*: head against torso, and torso against whatever it rides or holds.

## A limb's contour is the masses under it [read: Bridgman]

A limb is a stack of forms inside a sleeve of skin, and its width at any height
reflects what is inside it there. If you only trace the edge, you record where
the edge was but not why, so when it is wrong you cannot tell what to correct.
Bridgman on how the segments meet:

> *"The masses of the shoulder, arm, forearm and hand do not join directly end to
> end with each other, but overlap and lie at various angles. They are joined by
> wedges and wedging movements."*

Taken literally, that rules out the tube. Two segments that overlap at an angle
produce a **break in the contour** at every joint, and that break is the joint.
`hands-and-feet.md` says the same of a finger (*"a step-down from each segment to
the one beyond, bridged by a wedge"*); a limb is the same rule at a larger size.

| Symptom | What it is | What to look for |
|---|---|---|
| Constant width | **The straw**: no muscle stated anywhere along it | A drawn shin well under half the subject's width at the calf (in one case 19-25 px against 59), and still narrower than the subject at the ankle (34 px there) |
| Widening toward the far end | **Backwards.** A limb is widest at its root and narrowest at the joint it runs into | A drawn forearm wider at the wrist than at the sleeve (in one case 42 px at the sleeve, 55 at the wrist), where the subject narrows toward the elbow (42 narrowing to 36) |
| No change of direction | **No joint** | A break of about 40° in the subject's contour at the elbow or knee, which is 20-30 px sideways within 30 rows, against a few px of drift in the drawing |
| A contour down the middle | **The tramline**: a duplicate line that makes one limb look like two thin ones | Three pale runs where the subject has two, on most rows (in one case 9 of 12). `ink` cannot see it; `form` can |
| Two limbs at one angle | **Twinning** (the rule against twinning, in `SKILL.md`) | Loomis: *"drop one hip, get the elbows at different levels… do anything that keeps your drawing from looking like a wooden dummy"* |
| Drawn dead straight | Stiffness with a bony cause | Loomis: *"no bone is perfectly straight. An arm or a leg drawn with a perfectly straight bone will lie rigid and stiff-looking"* |

**An interior line on a limb must fade out.** A subject may have one inside the
near arm, such as an elbow crease: narrow, lasting two rows, then gone. A line
running the full length of the limb at full weight is a tramline. As with cloth
(below), point at the mark and name what causes it; a tramline has no cause.

## Foreshortening: do not reason about length [read: Loomis, Hogarth]

A limb pointing at the viewer keeps its width and loses its length, and you
cannot work out the lost length by reasoning, because you are looking down it
like a gun barrel. Think of the form as sections lined up one behind the other.
For a drawing this means:

- **Show depth with overlap, not size.** Once the length is gone, the only thing
  left to show a limb coming forward is which contour crosses in front of which.
  The far contour **stops and restarts**; do not rely on a flat to hide ink
  underneath it (see the occlusion rule in `bicycle.md` for the same idea on a
  lattice).
- **Draw the joint's ellipse even where it will be covered.** A knee seen
  edge-on is a line; coming at you it is a wide ellipse, whose opening measures
  the turn.
- **Measure the foreshortened segment against something in the picture plane**
  (the head, the other limb, a frame tube). You cannot check it against itself.
- **The symbol-drawing mistake:** a foreshortened arm drawn at full length and
  then "shortened" by making it *thinner*. A forearm pointing toward you is
  fatter than one seen from the side.

## A seated, braced figure [read: bike-fit literature]

A standing canon cannot draw a figure that sits and leans on something. A
cyclist is the clearest case; the same reasoning applies to a rider, a driver,
or anyone at a desk.

**Five contacts, each a place where two forms meet.** For a cyclist: two hands
on the bar, two feet on the pedals, the pelvis on the saddle. `bicycle.md`
covers the first three; the saddle is the fourth. At each, the object continues
past the body on both sides, and a band of the subject's own ground (or, where
the whole passage is dark, a second lighter value) separates the two.

**The fold is at the hip first and the lower back second.** Bike-fit sources put
a road rider's torso at 40-50° from horizontal and the closed hip angle at
44-58°, tighter for a fitter rider. A flexible rider tips the pelvis forward and
keeps the lower back long; a stiff one rounds it. Use this to know what to look
for, not what to draw: **a long shallow arc means a forward-tipped pelvis, a
short sharp one a rounded lower back, and they make different characters.**
Measure it as rise over run, tailbone to shoulder; a rise of about half the run
is a shallow dome, not a hunch. It is usually the only long curve in a picture
of straight lines, so exaggerate it.

**The arms are struts** carrying weight from the shoulder girdle into the bars:
nearly straight, never locked, never parallel. Loomis on braced limbs: *"limbs become props or braces rather than complete
supports. The spine has a tendency to relax in a concave manner toward such
bracing."* The elbow's small bend separates an arm from a stick: expect **a break of
around 40° in the subject against under 10° in a first drawing.**

**The legs are never at the same phase.** The cranks are 180° apart, so one knee
is always up and one down, and the thighs leave the pelvis at different angles.
Plot the bottom bracket, then both pedals against it: one falls **below and
behind**, the other **above and in front**, and the knees sit roughly a third of
a head unit apart vertically. **Level knees show a figure standing on two
pedals**, not pedalling.

**Everything comes in pairs, and no pair is identical.** Shoulders, arms, hips,
legs and shoes: in each pair the two sit on different depth planes, and the far
one is narrower, shorter, and (per the depth rule in `quadruped.md`) takes a
**lighter line weight and a duller value**, because depth is settled before
light. A far thigh drawn at a third of the subject's width is not one plane
back; it is simply too small. The **neck is extended**: a rider looking up the
road holds the head against the line of the spine, the one place where the back
compresses and the throat opens. If the head sits straight on the jersey with
neck and cheek as one pale mass, the neck is missing.

## Cloth on the figure

Cloth tends to be drawn as a flat coloured region with straight lines ruled
across it, as happens to any object you have no construction for.

| Where | The fault | What the measurement says |
|---|---|---|
| a top | One closed silhouette whose interior is all seams: lines across the full torso, a vertical down the centre, a hem line | **No folds at all.** No interior mark responds to a tension point (the shoulder bearing weight, a forearm folded across the body, the hip) |
| a waist band | Both edges nearly straight and parallel, running from silhouette to silhouette | A band goes *around a barrel* and is interrupted by anything in front of it. A flat strip measures at about **half the structure** of a formed one: nothing is missing from the box, it just carries less |
| a chin strap | Two bands into a buckle, lying on the jaw like a ribbon | A chin strap exists *because* it is in tension over a jaw, and the drawing leaves the tension out |
| trousers or shorts | A flat with a hem line | The same failure, with fewer marks |

**A seam and a fold are different kinds of interior mark, and neither is a
straight line.** Drawings often get both wrong at once:

- A **fold** is a line *of* the cloth. It starts at a tension point, where the
  force is applied, and fades out. A fold drawn at full weight from silhouette
  to silhouette looks like a wire.
- A **seam, band, zip or printed stripe** is a line *on* the cloth, which makes
  it a **cross-contour**: it wraps the form and follows its perspective. A band
  around a torso is an ellipse around a barrel, not a straight line across a
  rectangle, and its depth changes as the barrel turns away. A seam is often
  *also* a support, so folds may radiate from it because it is a support.

**What to plot before drawing any cloth.** Plot every support and tension point,
and the lowest point of contact, which divides cloth lying on the form from
cloth hanging free. Below it, cloth hangs vertically whatever the body does.
Above it, every mark must have a cause you can point at.

## A small figure is still a whole figure

Viewers find a human figure in a picture before almost anything else and read
what it is doing, so a recognisable figure is never a minor part however few
pixels it covers. Its tier sets its line weight and contrast, never which parts
of the body exist.

The usual failure is a small figure drawn as one closed outline, like a
gingerbread cut-out: a round head on an armless body and two straight tubes for
legs. Next to a subject whose small figures have hats, shoulders, bent knees and
something in their hands, it is the first thing a viewer sees as wrong.

At any size, a figure is built from:

- the **head**, with its hat or the mass of its hair, and the **neck** under it;
- the **shoulder line**, set at its own angle, and the **torso** under it;
- **both arms**, each with an elbow and a hand. The hands hold whatever the
  subject shows (a stick, a basket, a bag, a rein), and the held object is an
  inventory entry of its own with its junctions (`figure.hand/stick`,
  `stick/figure.shoulder`);
- the **hips**, and **both legs**, each with a knee;
- **both feet**, each pointing its own direction on the ground.

It also has a **pose taken from the gesture**: which leg is forward, how far the
knees bend, how the body leans over the feet, where the weight sits. A walking
figure has one leg straight and one bent, and its feet at different heights. A
figure standing on two straight legs side by side is not walking, whatever the
road under it suggests.

Build it like any other part: its own `--zoom` box, a working resolution where
its head is around 40px (so a 10px head is drawn four times larger), the same
stages, joints in the inventory and describer run on its crop as a large figure.
Only its weight and contrast follow its tier. Budget the strokes its joints need
at stage 0, not from whatever is left at the end.

```checklist
object: person|people|figure|figures|man|men|woman|women|child|children|walker|walkers|rider|riders
sub-forms: head torso|body arm leg foot|feet
```

## Build order

Draw the figure and any object it rides or holds **together, keeping both at the
same stage throughout** (`bicycle.md` says the same from the other side). Keep
cloth one stage behind the body, because a finished fold over a blocked-in torso
has to be bent to fit whatever the torso becomes.

1. **Write the joints and the gaps into the inventory**: shoulder, hip, elbow,
   knee, upper arm, and the negative shape between torso and arm, each boxed like
   any other part. A joint that is not listed cannot be reported missing.
2. **State the pose as three masses**: the ribcage's tilt, the pelvis's tilt,
   and the head against both, as three angles measured separately and written
   down. Then draw **the line of action**, one exaggerated curve (in a cyclist,
   pelvis to crown). For a turn or a look over the shoulder, add the angles in
   § A turned torso, measured with `look.py axis`.
3. **Draw the ribcage and the pelvis as two measured boxes**, with the flexible
   waist between them, never as one bag.
4. **Lay the shoulder girdle on the ribcage**: the acromion outside and above
   the barrel, the deltoid as a wedge pointing down the arm. Plot the **ground
   under the arm** as a shape at the same time.
5. **Draw the pelvis's contacts and openings**: the trochanter as a landmark,
   any seat as a separate form with its own contour, and each leg opening as its
   own cross-contour at its own height and angle.
6. **Draw limbs as stacked segments between measured joints**, every joint a
   break in the contour, every segment widest at its root. Draw the two arms at
   different angles and the two legs at different phases (for a cyclist, read
   them off the cranks).
7. **Draw foreshortened segments last**, measured against something in the
   picture plane, with overlaps drawn as stops and restarts, not painted over.
8. **Walk the inventory, joints included, before passing any stage**, since a
   median form ratio near 1.0 says nothing about missing joints.
9. **A garment drawn as one closed mass looks like furniture** (a bag, a
   cushion, a bundle the figure rests against), however right its width and
   placement. Cloth looks worn when the **hem interrupts the limb it covers**
   and the limb continues out of it. Give every garment its openings (the two
   arcs where the thighs leave shorts, the cuff, the collar) as contours of the
   garment, not of the limb. A mass that *ends* where a limb begins looks like
   something the limb is behind; a mass the limb *comes out of* looks like
   clothing. Numeric gates miss this and the describer names it plainly, so give
   each garment a describer run of its own.
