# Still life as solids

Knowing what a mug is, you tend to draw the mug you remember: a flat-bottomed
box with an ear stuck on the side. Nearly every object on a table is a cylinder,
a sphere or a box in perspective, and most errors come from drawing the symbol
for the object instead of that solid.

## Contents

- The schema is a diagnostic, never a scaffold
- The ways a drawn still life fails, and what each measures as
- Ellipses [read: Norling; Robertson]
- Cylinders and containers [read: Loomis; Robertson]
- Handles
- Glass and metal [read: Guptill; Gurney, Color and Light]
- Fruit and round forms [read: Gurney, Color and Light; Loomis]
- Books, boxes, clocks and screens [read: Norling; Robertson]
- Food: plates and stacked layers
- The sub-forms an inventory descends to
- Where the still life meets the rest of the picture
- Build order

## The schema is a diagnostic, never a scaffold

Everything below describes the typical object, which is not the one in front
of you. **Do not build the drawing from it.** Measure the subject first, then use
this file to ask whether each difference between your measured cup and a typical
one is real or an error. If you are following a passage without
looking at the subject, you are using it wrongly. `[read: source]` marks a claim
taken from the named book.

## The ways a drawn still life fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **Pointed ellipses**: a rim drawn as two arcs meeting in a point at each end, like a lemon | `check.py --zoom` on each end of the rim. The subject's ellipse is rounded at the ends of its long axis; no ellipse has a corner |
| **A flat-bottomed cylinder**: the base of a cup, vase or bottle drawn as a straight line | A one-column `--scan` with `--side bottom` down the centre line, and two more near the sides. On the subject the base is lowest at the centre line and rises toward the sides |
| **Every ellipse at one degree** (how open it is, height over width): the base of a cup as narrow as its rim | Measure height against width of each ellipse with `--scan` (one row through the long axis, one column through the short). Below eye level, the base is rounder than the rim. Equal ratios on the drawing mean you drew the symbol |
| **A leaning object**: the centre line not at right angles to the ellipses | `--plumb` through the centre of the rim and the centre of the base. On an upright object both centres sit on one vertical, and that vertical meets each ellipse's long axis at a right angle |
| **The handle stuck on flat**, in profile, while the cup is turned | Measure the horizontal distance from the centre line to each of the handle's two joins, and their heights, on the subject. A turned cup brings the handle in toward the centre line and foreshortens its loop |
| **The object floats** above the table | `--zoom` on the base. The subject has a dark accent where the object meets the surface, darker than the cast shadow beside it. If the drawing has no accent there, or a gap showing the ground, the object floats |
| **Glass drawn as a grey shape**, filled with one mid value | `--masses` on the glass's box. The subject shows a few sharp lights and darks over the background seen through it; the faulty drawing shows a solid grey object |
| **Metal shaded like clay**: a smooth gradient from light to dark | `--scan` with `--value` across the body. The subject's runs jump from near white to near black within a few px; a gradient on the drawing has no such jump |
| **Reflected light as bright as the lit side** on a fruit or bowl | Sample both values off the subject. Reflected light in the shadow belongs to the shadow group and stays darker than any value in the light |
| **Box edges that spread apart** as they recede | Sight the angle of each receding edge on the subject (`measuring.md`, angles) and on the drawing. Parallel edges going away converge or stay parallel; they never diverge |
| **Clock numerals spaced evenly** round a tilted face | Measure the gaps between numerals along the ellipse. On a tilted face the ones near the ends of the long axis crowd together |
| **Cake or burger layers as flat stripes** | `--scan` with `--side top` across the front of the stack. On the subject each band's edges curve the same way the plate's ellipse does |

## Ellipses [read: Norling; Robertson]

A circle seen at an angle is an ellipse. Norling builds every round object in
*Perspective Made Easy* from this, and Robertson's *How to Draw* gives the same
rules with more care over the degree.

- **The short axis is the cylinder's axis.** On a cup standing upright, the
  rim's short axis is vertical. On a bottle lying on its side, the short axis
  of its base runs along the bottle. If the short axis of an ellipse is not on
  the centre line of the object it belongs to, the object looks twisted.
- **The degree changes with distance from eye level.** An ellipse at eye level
  is a straight line. The further above or below eye level it sits, the
  rounder it gets. So on a cup below your eye the base is rounder than the rim,
  and in a stack of plates the lowest is rounder than the top one. Find the eye
  level on the subject from where the ellipses flatten, and check every ellipse
  in the picture against it.
- **The ends are round**: tightest at the ends of the long axis, never pointed.
- **The centre of the circle is not the centre of the ellipse.** In a true
  projection the circle's centre sits a little toward the near side. That
  matters for where a stem leaves a plate or where a clock's hands pivot. A
  drawn or generated subject does not always follow this, so measure the centre
  instead of imposing the offset.

## Cylinders and containers [read: Loomis; Robertson]

Cups, mugs, bottles, bowls, vases and jars are all built the same way: a
**centre line**, then an ellipse across it wherever the profile changes, then
the profile drawn as two lines that touch each ellipse at its widest point.
Loomis teaches still-life objects this way in *Successful Drawing*, as cylinders
and cones before any surface.

- **The centre line goes in first**, through the measured centres of the rim
  and the base, with every ellipse square to it. Plumb it on the subject.
- **The two sides are mirror images about the centre line.** Measure the width
  at each ellipse on the subject and put half on each side. A bottle drawn by
  eye comes out with one shoulder higher than the other.
- **The profile touches the ellipses.** The sides of a cylinder meet the rim and
  the base at the ends of their long axes, and the front half of the base
  ellipse is the bottom edge. The back half is hidden on an opaque object and
  visible through a glass one.
- **Thickness shows at the rim** as two nearly concentric ellipses, with the
  gap wider at the front. A single ellipse looks like a tube cut from paper.
- **Bottles and vases are cylinders and cones joined**: base, body, shoulder,
  neck, lip. Each junction is an ellipse, even where the profile has no corner.
- **Bowls** are half a sphere hung under a rim ellipse. From above you see the
  far inside wall, which takes its own value from the light.

## Handles

A handle is a loop in a plane through the cup's centre line, and it turns with
the cup. Seen side on it is a full ear. Seen three-quarter it narrows, and its
far edge passes behind its near edge. Seen from the front it is a thin bar down
the centre line.

Each of its two joins lies on an ellipse round the body at its own height, and
both move toward the centre line as the cup turns. If the joins stay at the edge
of the silhouette on a turned cup, you have drawn the profile mug from memory.

## Glass and metal [read: Guptill; Gurney, Color and Light]

- **Glass is read by its edges.** Guptill's *Rendering in Pen and Ink* draws
  glass almost entirely with the dark and light lines at its rim, base and
  sides, and a few sharp highlights. Through it you see the background, shifted
  and squeezed where the curved wall bends it. Draw that displaced background,
  and let it make up most of the glass.
- **Liquid in a glass has its own surface ellipse**, rounder than the rim when
  below eye level. Its front edge is often the strongest dark in the glass.
- **Metal is a distorted mirror.** Gurney describes polished surfaces as
  showing the environment, with the darkest darks and the brightest lights side
  by side. On a cylinder those reflections stretch into bands along the axis;
  on a sphere they curve round it. Measure where each band starts and stops
  instead of smoothing them into a gradient.
- Both depend on the highlight's **shape**, which follows the form: a vertical
  streak on a bottle, a window-shaped patch on a sphere. A round white dot on a
  cylinder makes the surface look flat.

## Fruit and round forms [read: Gurney, Color and Light; Loomis]

Fruit is a sphere with a dent, and a sphere in light has a fixed order of
values (Gurney lays it out; Loomis teaches it on a ball): light, halftone, the
**terminator** where the form turns away from the light, the core shadow just
past it, **reflected light** inside the shadow, and the **cast shadow** on the
table.

- **The terminator shows the shape.** Its curve follows the form, so a dent or
  a lobe bends it. A terminator drawn as a smooth arc turns a lumpy apple into a
  ball. Trace its path on the subject.
- **Reflected light stays in the shadow group.** Making it too bright is the
  commonest way two value groups end up overlapping. Sample it and compare it
  with the darkest halftone in the light.
- **Fruit is not a sphere.** An apple dents at the stem; a pear is a small round
  on a larger one. Measure width against height before drawing the round.
- **The cast shadow starts at the contact point**, darkest there, and is
  flatter than the fruit because it lies on the table in perspective.

## Books, boxes, clocks and screens [read: Norling; Robertson]

- **A box is three sets of parallel edges.** In perspective each set converges
  toward its own vanishing point or stays parallel. Sight each receding edge on
  the subject and check that its partners match.
- **A book is a box with a cover round it**, overhanging the pages on three
  sides, with the pages showing as fine lines. Drawn as one block, it looks like
  a brick.
- **A clock face is an ellipse with a scale on it.** On a tilted face the 12-6
  and 3-9 lines are not the ellipse's axes, and the numerals bunch up near the
  ends of the long axis. Place each numeral by measurement. The hands pivot at
  the circle's centre, which (as above) is not the ellipse's centre.
- **A screen is a rectangle inside a bezel**, in the device's perspective. Draw
  its image as a pattern of values, as much as the subject shows at that scale. A
  laptop's lid and base share one straight hinge line.

## Food: plates and stacked layers

- **A plate is concentric ellipses**: the rim, the edge of the well, and the
  foot underneath. Their degrees are close but not equal. The rim band is wider
  at the front than at the back; measure both.
- **A cake or burger is a stack of short cylinders**, each layer a band. Each
  band's top and bottom edges are ellipse arcs of nearly the same degree, so
  below eye level each band's front edge curves down. Overhanging layers
  (lettuce, cheese, icing) break the edge of the band below.
- **The ratio of band widths is what makes it recognisable.** As with a wheel's
  two bands (`bicycle.md`), a burger whose bun, patty and fillings come out
  equal in height looks like a striped cylinder. Measure every band's height on
  one column through the front of the stack.

## The sub-forms an inventory descends to

Write an entry for each sub-form the subject has. `check.py --checklist
parts.json` reads the blocks below, one object per block, and fails on any
sub-form the inventory neither names nor lists in `_absent`.

```checklist
object: cup|mug
sub-forms: rim body handle
```

```checklist
object: bottle|vase
sub-forms: neck shoulder body base
```

```checklist
object: wineglass|goblet
sub-forms: rim bowl stem foot
```

```checklist
object: book
sub-forms: cover spine page
```

```checklist
object: clock
sub-forms: face rim hand
```

```checklist
object: burger|hamburger
sub-forms: bun patty
```

## Where the still life meets the rest of the picture

- **Object on table.** The table is behind and under every object on it. Write
  the table first, then the cast shadow, then the contact shadow, then the
  object. The contact shadow is the junction; give it its own entry
  (`cup/table`).
- **Object in front of object.** In a group, the nearer object's base ellipse
  sits lower on the page. If two bases are at the same height, the objects are
  side by side, whatever the overlap suggests. Check each pair against the
  overlaps table.
- **Something through glass.** Write the far object first, displaced where the
  glass bends it, then the glass's lights and darks over it.
- **Hand on cup.** The cup's ellipses run on behind the fingers;
  `hands-and-feet.md` covers the grip.
- **Food on plate, plate on table.** Each has its own contact shadow; the
  plate's is the one usually forgotten.

## Build order

1. **Eye level**, read off the subject from where its ellipses flatten, and
   the table plane with each object's footprint on it.
2. **Each object's centre line**, measured and plumbed, and the ellipses on it,
   each with its measured width and degree.
3. **The profiles** joining the ellipses, then handles, spouts and lids.
4. **Shadows and contacts**: cast shadows and the dark accent where each object
   meets the table.
5. Only then reflections, highlights, labels and surface detail.
