# Trees and plants as solids

A tree goes wrong in two opposite ways. It becomes a symbol (a brown column
with a green ball on top), or a pile of leaves drawn one at a time until the
form disappears under them. Both come from drawing what a tree is supposed to be
instead of the large shapes the subject shows. A plant has the same problem at
a smaller size. A flower adds one more: its petals get drawn as a decorative
star with whatever number of points the hand happens to make.

## Contents

- The ways a drawn tree or plant fails, and what each measures as
- The trunk and branches
- The canopy
- Potted plants
- Flowers
- Where trees and plants meet other things
- Checklist
- Build order

Everything below describes the typical tree, plant or flower, and **the typical
one is not the one in front of you.** Measure the subject first, then use this
file to ask whether a difference comes from the species, the light, the season
or a mistake. If you could follow a passage without looking at the subject, you
are using it wrongly. `[read: source]` marks a claim taken from the named book.

## The ways a drawn tree or plant fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **The trunk is a column**: the same width from the ground to the first fork | `check.py --scan` on a box across the trunk with `--step` set to give a reading every tenth of its height. The subject's width narrows going up and widens at the root flare; a faulty drawing's stays constant |
| **A branch is as thick as the limb it leaves**, or thicker than it | Scan across the parent just below a fork and across each child just above it. Each child should be narrower than the parent, unless the subject shows otherwise |
| **The canopy is one ball**, round and even, with a smooth outline | `--masses` on the canopy box: the subject reads as a few separate masses with notches between them, a faulty drawing as one blob. Sight the outline's changes of direction (`measuring.md`, the envelope) and count them on both |
| **The canopy is one value**, with no lit side and no shadow side | `--masses --colours 3` on the canopy box. The subject splits into two or three levels, usually lit on top and on the side facing the light. If the drawing returns one level, its masses show no light |
| **Leaves drawn everywhere**, so the interior is busy and the form is lost | `--masses` at thumbnail size, then `--ranking parts.json`: a canopy drawn leaf by leaf ranks above its tier and pulls the eye away from the centre of interest |
| **No sky holes**, or holes that are too few, too regular, or as light as the open sky | Count the holes on a `--zoom` of the canopy, on subject and drawing. Read the value inside a hole and of the open sky beside the canopy (`measuring.md`, reading a value off the subject); the hole is usually darker |
| **The edge is smooth and the interior textured**, the reverse of what the subject shows | `--overlay --box` on a stretch of the canopy's edge. In the subject the texture sits at the silhouette and where a mass turns from light to shadow, and the inside of each mass is quieter |
| **The species reads wrong**: an oak drawn with a pine's habit (its typical growth shape), or a generic tree | Run `describe.sh` on the tree's crop. If it names a different kind of tree, or only "a tree" when the subject's describer named one, compare silhouettes with `--masses` and sight the branch angle at each fork |
| **The pot's rim is a flat line or a lemon**: an ellipse with pointed ends, or the base drawn as flat as the rim | `--scan` with `--side top` on a one-column box through the centre of the rim, then the same through the base. Write down the minor-to-major ratio of each. Below eye level the base ellipse is rounder than the rim |
| **A flower has the wrong number of petals** | Count on the flower's own crop. Separate petals of one value can go in the entry as `"count"` for `--counts`; overlapping petals come back UNCHECKED, so count them on `--zoom` on both images and write both numbers into `notes.md` |
| **Stems and leaves float**, touching nothing, or join the stalk at a point with no thickness | `--zoom` on each junction: the subject shows where the leaf stalk leaves the stem and on which side. A leaf that ends at the stem's contour with no join was drawn after the stem as a separate object |

A tree is a few big solids, a trunk and a handful of masses, with light falling
across them. These failures come from drawing a symbol for the whole, or many
small parts in place of the solids.

## The trunk and branches

**The trunk tapers.** It is widest at the ground, where the roots flare out into
it, and narrows upward. Above each fork the trunk is thinner than below it.
Leonardo noted that the branches at any height of a tree, taken together, are
about as thick as the trunk below them [read: Leonardo, *Notebooks*]. Use that
to check a fork you have measured: if both children are as thick as the parent,
one of them is wrong.

**Branches leave at the angles the species uses.** Some grow upward in a narrow
V, some leave nearly level, some droop. Sight the angle of each main limb where
it leaves the trunk (`measuring.md`, angles and plumb lines) and write it down.
The fork angle shows the species most clearly, and drawn branches tend to drift
toward one comfortable angle on every tree.

**Branches come toward you and go away.** In a three-quarter or frontal view,
some limbs point at the viewer and are foreshortened to short thick stubs, and
others pass behind the trunk. A tree whose branches all spread flat to left and
right, like a diagram, has lost its depth. Look for limbs that overlap the trunk
and record each crossing as an overlap row.

**Bark is texture, and texture belongs at the edges.** Guptill's advice for pen
drawings of trees is to suggest bark with a few marks that follow the form,
concentrated where the trunk turns from light into shadow, and to leave the lit
side mostly bare [read: Guptill, *Rendering in Pen and Ink*]. Marks spread evenly
across the trunk flatten it.

The trunk usually fails in one of three ways: it is drawn as a parallel-sided
column, it is cut off flat where it meets the ground, or its branches join it at
a point instead of growing out of it with a widening at the joint.

## The canopy

**The canopy is a few large masses, not leaves.** Carlson treats foliage as
masses with planes, like any other solid, lit on the side facing the sky and the
sun and darker underneath and on the far side [read: Carlson, *Guide to
Landscape Painting*]. A large tree usually shows between a few and a dozen of
these masses. Count them on the subject's crop at the size you will draw, and
write the count in the reading.

**Each mass has a lit side and a shadow side.** The value change between them
makes the canopy look round. Where the canopy overhangs the trunk there is
usually a dark band under the masses, and the trunk often passes into that
shadow and comes out lighter below it.

**Sky holes.** Where the sky shows through the canopy, treat the hole as a
negative shape like any other. Carlson notes that sky seen through foliage looks
darker than open sky, because the surrounding leaves crowd it and the eye reads
it against them [read: Carlson]. Holes as bright as the open sky look cut out
of the paper. The holes are also irregular: grouped, different in size, and more
numerous near the thinner outer branches. A regular scatter of round holes looks
like a pattern printed on the tree. Give holes their own palette name if their
value differs from the open sky's, since a mark may not use `background`.

**Texture at the edges only.** Indicate leaves where the silhouette meets the sky
and where a mass's lit side turns into its shadow. Elsewhere draw the mass as a
flat or a gradation. A few leaf shapes at the edge are enough to show what the
leaves are; the eye fills in the rest. Guptill makes the same point for foliage
in pen: suggest the leaves instead of drawing each one [read: Guptill].

**Species by silhouette and branching habit.** From a distance, a tree is
recognised by its overall shape and how its limbs divide: a conifer's narrow
cone with level or drooping tiers, a broad spreading crown, a column, a weeping
curtain. Look at the silhouette and the main limbs before anything inside them.
The describer's answer for the subject names the kind of tree; check that its
answer for the drawing does too.

The canopy usually fails as a single round ball, as even texture everywhere, as
holes in a regular sprinkle, or as an outline drawn as one continuous scalloped
cloud line, which looks like a cartoon tree.

## Potted plants

**The pot is a cylinder or a cone, and its rim and base are ellipses.** Norling
and Robertson both teach that a circle seen at an angle is an ellipse whose
minor axis lies along the axle (the cylinder's axis), and that ellipses get rounder the
further they sit from eye level [read: Norling, *Perspective Made Easy*;
Robertson, *How to Draw*]. So the base of a pot seen from above is rounder than
its rim. Measure both instead of assuming the rule, because a picture can break
it.

The rim is a band with a thickness, so it is two ellipses, outer and inner, and
the soil or the plant cuts off the back of the inner one. The ends of an ellipse
are round; a rim drawn with pointed ends is the most common pot error.

**The plant grows out of the soil, not off the rim.** Find where each stem leaves
the soil inside the rim. Leaves that hang over the rim pass in front of the front
edge or behind the back edge; note which.

## Flowers

**A flower is a simple form before it is petals.** Many flowers fit one of a few
solids: a cup (tulip, rose bud), a trumpet or cone (daffodil, lily), a flat disc
(daisy, sunflower), a ball (a cluster head). Before drawing any petal, decide
which solid the subject's flower is and where its axis points. A disc seen at an
angle is an ellipse with the centre pushed toward the near side, like a wheel.

**Count the petals instead of drawing them freehand.** Write the count into the
entry. The petals of one flower are evenly spaced round the centre, so on a disc
seen at an angle the near petals look short and wide and the far ones narrow, or
hidden. If your count is right but the petals all have the same shape, you have
lost the turn of the flower.

**Stems and leaves attach.** A stem enters the flower at its back, through the
green sepals; on a cup or trumpet it meets the base, not the side. A leaf leaves
the stem at a node, often with a short stalk, and the leaves usually alternate or
pair up along the stem in a regular pattern. Find the subject's pattern and keep
it. A stem has width and tapers slightly toward the flower.

A flower usually fails as a star of identical petals with no centre, a petal
count off by one or two, a head stuck on the side of the stem, or leaves pasted
against the stem with no join.

## Where trees and plants meet other things

Occlusion is write order: the far form's fill and ink go in first, then the near
form's fill covers that ink. Write each crossing as an overlap row naming the
specific sub-forms that cross (the near foot, not the whole bird).

- **Trunk and ground.** The trunk is in front of the ground behind it, and the
  root flare spreads onto the ground plane. A cast shadow anchors the trunk; look
  for it and measure its direction against the light.
- **A bird on a branch.** The toes wrap round the branch. The near foot's toes
  are in front of the branch, and the branch is in front of the far foot's toes.
  Split the rows: `tree.branch/bird.foot.near` with the foot in front, and
  `bird.foot.far/tree.branch` with the branch in front. A bird with its feet
  resting on top of a branch line looks pasted on.
- **A figure against a trunk.** Decide whether the shoulder or hand is in front of
  the trunk or behind it, and where the trunk's contour breaks.
- **Near foliage against far foliage.** The near tree is in front, and the edge
  between them is often lost where their values meet. Two trees of one value in
  one plane read as one tree; separate them with a value difference or a sky gap.
- **Canopy against a building or the sky.** Leaves at the edge are in front of
  the building and break its straight line. Do not draw the building's edge
  through the leaves.
- **A pot on a table, a plant in a vase.** The pot is in front of the table top,
  and its base ellipse sits on the table plane with a contact shadow along the
  near curve. In a vase, the front of the rim is in front of the stems and the
  back of the rim is behind them, so each stem crosses the rim twice.

## Checklist

`check.py --checklist parts.json` reads these blocks. A sub-form is matched as
the word or the word plus "s", so irregular plurals (`branches`, `leaves`) are
listed as alternatives. Where the subject lacks one (a conifer may show no sky
holes), write the reason in `_absent`.

```checklist
object: tree|oak|pine|fir|palm|birch|willow|maple
sub-forms: trunk branch|branches canopy|foliage hole|gap
```

```checklist
object: flower|rose|tulip|daisy|sunflower|lily|poppy
sub-forms: petal stem leaf|leaves
```

```checklist
object: pot|planter
sub-forms: rim body soil|earth|water
```

## Build order

1. **The silhouette of the whole tree or plant**, from measured extremes. It
   shows the species and is the first thing a viewer reads.
2. **The trunk and main limbs** as straight lines between measured forks, with
   each width scanned and the fork angles written down.

3. **The canopy masses**, counted, each blocked as one shape, with its lit side and
   shadow side decided from the subject.
4. **The sky holes**, as negative shapes with their own value.
5. **For a pot, the rim and base ellipses**, each with its measured ratio, before
   the plant. For a flower, its solid and axis before any petal.
6. **Texture last**, at the silhouette and the turn of each mass only.
