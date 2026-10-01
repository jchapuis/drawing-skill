# Trees and plants as solids

A tree goes wrong in two opposite ways. It becomes a symbol (a brown column
with a green ball on top), or it becomes a pile of leaves drawn one at a time
until the form disappears under them. Both come from drawing what a tree is
supposed to be instead of the large shapes the subject shows. A plant is the same
problem at a smaller size, and a flower adds one more: its petals get drawn as a
decorative star with whatever number of points the hand happens to make.

Everything below describes the typical tree, plant or flower, and **the typical
one is not the one in front of you.** Do not build on it. Measure the subject
first, then use this to ask why your measured tree differs from the usual one and
whether the difference is the species, the light, the season or a mistake. If a
passage below could be followed with the subject covered up, you are using it
wrongly. `[read: source]` marks a claim taken from the named book.

## The ways a drawn tree or plant fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **The trunk is a column**: the same width from the ground to the first fork | `check.py --scan` on a box across the trunk with `--step` set to give a reading every tenth of its height. The subject's width falls as you go up and widens again at the root flare; the drawing's stays flat |
| **A branch is as thick as the limb it leaves**, or thicker than it | Scan across the parent just below a fork and across each child just above it. The children are each narrower than the parent. A child wider than its parent is an error unless the subject shows it |
| **The canopy is one ball**, round and even, with a smooth outline | `--masses` on the canopy box: the subject reads as a few separate masses with notches between them, the drawing as one blob. Sight the outline's direction changes (`measuring.md`, the envelope) and count them on both |
| **The canopy is one value**, with no lit side and no shadow side | `--masses --colours 3` on the canopy box. The subject splits into two or three levels, usually lit on the side facing the light and on top. If the drawing returns one level, the masses carry no light |
| **Leaves drawn everywhere**, so the interior is busy and the form is lost | `--masses` at thumbnail size, then `--ranking parts.json`: a canopy drawn leaf by leaf ranks above its tier and pulls the eye off the centre of interest |
| **No sky holes**, or holes that are too few, too regular, or as light as the open sky | Count the holes on `--zoom` of the canopy, on subject and drawing. Read the value inside a hole and the value of the open sky beside the canopy (`measuring.md`, reading a value off the subject); the hole is usually darker |
| **The edge is smooth and the interior textured**, the reverse of what the subject shows | `--overlay --box` on a stretch of the canopy's edge. The subject's texture sits at the silhouette and where a mass turns from light to shadow; the inside of each mass is quieter |
| **The species reads wrong**: an oak drawn with a pine's habit, or a generic tree | Run `describe.sh` on the tree's crop. If it names a different kind of tree, or only "a tree" when the subject's describer named one, compare silhouettes with `--masses` and the branch angles with a sighting at each fork |
| **The pot's rim is a flat line or a lemon**: an ellipse with pointed ends, or the base drawn as flat as the rim | `--scan` with `--side top` on a one-column box through the centre of the rim, then the same through the base. Write down the minor-to-major ratio of each. Below eye level the base ellipse is rounder than the rim |
| **A flower has the wrong number of petals** | Count on the flower's own crop. Separate petals of one value can go in the entry as `"count"` for `--counts`; overlapping petals come back UNCHECKED, so count them on `--zoom` on both images and write both numbers into `notes.md` |
| **Stems and leaves float**, touching nothing, or join the stalk at a point with no thickness | `--zoom` on each junction: the subject shows where the leaf stalk leaves the stem and on which side. A leaf that ends at the stem's contour line with no join has been drawn after the stem as a separate object |

The pattern across all of these: a tree is a few big solids, a trunk and a handful
of masses, that the light falls across. The failures come from drawing a symbol
for the whole, or from drawing many small parts in place of the solids.

## The trunk and branches

**The trunk tapers.** It is widest at the ground, where the roots flare out into
it, and narrows upward. Each time a branch leaves, the trunk above that fork is
thinner than below it. Leonardo noted that the branches at any height of a tree,
taken together, are about as thick as the trunk below them [read: Leonardo,
*Notebooks*]. Use that to check a fork you have measured: if both children are
drawn as thick as the parent, one of them is wrong.

**Branches leave at the angles the species uses.** Some grow upward in a narrow
V, some leave nearly level, some droop. Sight the angle of each main limb where
it leaves the trunk (`measuring.md`, angles and plumb lines) and write it down.
The angle at the fork is where species shows most clearly, and drawn branches
tend to drift toward one comfortable angle on every tree.

**Branches come toward you and go away.** In a three-quarter or frontal view,
some limbs point at the viewer and are foreshortened to short thick stubs; others
pass behind the trunk. A tree whose branches all spread flat to the left and right,
like a diagram, has lost its depth. Look for limbs that overlap the trunk and
mark each crossing as an overlap row.

**The bark is texture, and texture belongs at the edges.** Guptill's advice on
pen drawing of trees is to suggest bark with a few marks that follow the form,
concentrated where the trunk turns from light into shadow, and to leave the lit
side mostly bare [read: Guptill, *Rendering in Pen and Ink*]. Marks spread evenly
across the trunk flatten it.

How the trunk fails: drawn as a parallel-sided column; cut off flat where it meets
the ground; branches that join the trunk at a point instead of growing out of it
with a widening at the joint.

## The canopy

**The canopy is a few large masses, not leaves.** Carlson treats foliage as
masses with planes, like any other solid, lit on the side facing the sky and the
sun and darker underneath and on the far side [read: Carlson, *Guide to
Landscape Painting*]. A large tree
usually shows somewhere between a few and a dozen of these masses. Count them on
the subject's crop at the size you will draw and write the count in the reading.

**Each mass has a lit side and a shadow side.** The value change between them is
what makes the canopy round. Under the masses, where the canopy overhangs the
trunk, there is usually a dark band, and the trunk often passes into that shadow
and comes out lighter below it.

**Sky holes.** Where the sky shows through the canopy, the hole is a shape like
any other negative shape. Carlson notes that sky seen through foliage looks
darker than open sky, because the surrounding leaves crowd it and the eye reads
it against them [read: Carlson]. If the drawing makes the holes as bright as
the open sky, they look cut out of the paper. The holes are also irregular:
grouped, different in size, more of them near the thinner outer branches. A
regular scatter of round holes reads as a pattern printed on the tree. Holes need
their own palette name if their value differs from the open sky's, since a mark
may not use `background`.

**Texture at the edges only.** Indicate leaves where the silhouette meets the sky
and where a mass's lit side turns into its shadow. Elsewhere the mass is a flat
or a gradation. A few leaf shapes at the edge are enough to say what the leaves
are; the eye fills in the rest. Guptill makes the same point for foliage in pen:
suggest, do not enumerate [read: Guptill].

**Species by silhouette and branching habit.** A tree is recognised from a
distance by its overall shape and how its limbs divide: a conifer's narrow cone
with level or drooping tiers, a broad spreading crown, a column, a weeping
curtain. Look at the silhouette and the main limbs before anything inside them.
The subject's describer answer names the kind; check that the drawing's does too.

How the canopy fails: a single round ball; even texture everywhere; holes as a
regular sprinkle; the outline drawn as a continuous scalloped cloud line, which
reads as a cartoon tree.

## Potted plants

**The pot is a cylinder or a cone, and its rim and base are ellipses.** Norling
and Robertson both teach that a circle seen at an angle is an ellipse whose
minor axis lies along the cylinder's axis, and that ellipses get rounder the
further they sit from eye level [read: Norling, *Perspective Made Easy*;
Robertson, *How to Draw*]. So the base of a pot seen from above is rounder than
its rim. Measure both rather than assuming the rule; a picture can break it.

The rim is a band with a thickness, so it is two ellipses, outer and inner, and
the inner one is cut off at the back by the soil or the plant. The ends of an
ellipse are round. A rim drawn with pointed ends is the most common pot error.

**The plant grows out of the soil, not off the rim.** Find where each stem leaves
the soil inside the rim. Leaves that hang over the rim pass in front of the front
edge and behind the back edge; note which.

## Flowers

**A flower is a simple form before it is petals.** Many flowers fit one of a few
solids: a cup (tulip, rose bud), a trumpet or cone (daffodil, lily), a flat disc
(daisy, sunflower), a ball (a cluster head). Decide which solid the subject's
flower is, and its axis, before any petal. A disc seen at an angle is an ellipse
with the centre pushed toward the near side, like a wheel.

**The petal number is counted, not drawn freehand.** Write the count into the
entry. The petals of one flower are evenly spaced round the centre, so on a disc
seen at an angle the near petals look short and wide and the far ones narrow, or
hidden. If your count is right but the petals are all the same shape, the turn of
the flower is missing.

**Stems and leaves attach.** A stem enters the flower at its back, through the
green sepals; on a cup or trumpet it meets the base, not the side. A leaf leaves
the stem at a node, often with a short stalk, and the leaves usually alternate or
pair up along the stem in a regular way. Look at which pattern the subject uses
and keep it. A stem has width and tapers slightly toward the flower.

How a flower fails: a star of identical petals with no centre; the petal count off
by one or two; the head stuck on the side of the stem; leaves pasted against the
stem with no join.

## Where trees and plants meet other things

Occlusion is write order: the far form's fill and ink go in first, then the near
form's fill covers that ink. Write each crossing as an overlap row, at the grain of
the forms that cross.

- **Trunk and ground.** The trunk is in front of the ground behind it, and the
  root flare spreads onto the ground plane. A cast shadow anchors the trunk; look
  for it and measure its direction against the light.
- **A bird on a branch.** The toes wrap round the branch. On the near side the toes
  are in front of it and the branch passes behind them; on the far side the branch
  is in front of the toes. Split the rows: `tree.branch/bird.foot.near` with the
  foot in front, and `bird.foot.far/tree.branch` with the branch in front. A
  bird with its feet resting on top of a branch line looks pasted on.
- **A figure against a trunk.** Decide whether the shoulder or hand is in front of
  the trunk or behind it, and where the trunk's contour breaks.
- **Near foliage against far foliage.** The near tree is in front, and the edge
  between them is often lost where their values meet. Two trees of one value in
  one plane read as one tree; their separation is a value difference or a sky gap.
- **Canopy against a building or the sky.** Leaves at the edge break the
  building's straight line; they are in front of it. Do not draw the building's
  edge through the leaves.
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
object: tree
sub-forms: trunk branch|branches canopy|foliage hole|gap
```

```checklist
object: flower
sub-forms: petal stem leaf|leaves
```

```checklist
object: pot|planter
sub-forms: rim body soil|earth|water
```

## Build order

1. **The silhouette of the whole tree or plant**, from measured extremes. It
   carries the species and is the first thing a viewer reads.
2. **The trunk and main limbs** as straights between measured forks, with each
   width scanned, and the fork angles written down.
3. **The canopy masses**, counted, each blocked as one shape, with its lit side and
   shadow side decided from the subject.
4. **The sky holes**, as negative shapes with their own value.
5. **For a pot, the rim and base ellipses**, each with its measured ratio, before
   the plant. For a flower, its solid and axis before any petal.
6. **Texture last**, at the silhouette and the turn of each mass only.
