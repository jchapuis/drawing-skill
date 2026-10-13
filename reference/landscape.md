# The landscape as planes and air

A landscape goes wrong when its parts are drawn as objects laid side by side: a
hill, a tree, a cloud, a lake, each outlined and each at full strength. What
makes a landscape read is depth, and depth is carried by a few measurable
changes: value and contrast falling with distance, bands of ground getting
thinner toward the horizon, and edges softening as they recede. A landscape is
almost always a scene of masses, so the scene stages and `scene.md` apply.

Everything below describes the typical landscape, and **the typical landscape is
not the one in front of you.** Measure the subject first. Use this afterwards, to
ask why your measured subject differs and whether the difference is real (fog,
backlight, a stylised poster, a camera tilted down) or an error. If a passage
below could be followed with the subject covered up, you are using it wrongly.
`[read: source]` marks a claim taken from the named book.

## The ways a drawn landscape fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **The far hills are as dark and as sharp as the near ones**, so the picture reads as a flat backdrop | Sample the mode of a clean interior patch in each band, near to far, on both images (`measuring.md` § Reading a value off the subject). Write the two value sequences side by side. The subject's usually climbs toward the sky's value; the drawing's often stays flat |
| **The darkest dark sits in the distance** | The same samples, and `--weights` on a row through a near and a far band. The far band should carry the lighter line, or none |
| **The horizon tilts**, or sits at a height chosen by eye | `--scan` a narrow box at the left end and at the right end of the horizon; the row where the value changes should match on each image. Measure its height as a fraction of the frame |
| **The ground bands are evenly spaced**, so the land stands up like a wall | `--scan` one column from the bottom of the frame to the horizon, with `--value` naming the band colours. List each band's height in rows. On the subject the heights shrink toward the horizon |
| **The sky is one flat value**, or darker at the horizon than overhead | Sample the sky's mode near the top of the frame and just above the horizon, on both images |
| **Clouds are cotton balls**: round all over, lit at the bottom or not at all, the same size right down to the horizon | `--zoom` on a near cloud and a far one. Sample the value at the top and at the base of each. Measure each cloud's height in rows and compare it with its height above the horizon |
| **A reflection drifts sideways, leans, or is as long as the object measured from the shore** | Drop a plumb line (`measuring.md` § Sighting and measurement) through the object's top on the subject and see where it lands in the water. Then do the same on the drawing. Measure the reflection's length from the point where the object would meet the water, not from the visible bank |
| **A reflection is the same value as its object** | Sample both on the subject. A light object usually reflects a little darker, a dark one a little lighter. Check which the subject does before drawing either |
| **Ripples are wavy lines drawn over the reflection** | `--scan` a column down through the reflection. The subject's runs break into short horizontal pieces with gaps of water value between them. `--overlay --box` on the water shows whether the drawn breaks are horizontal |
| **A road stays wide into the distance**, or its edges meet somewhere other than the horizon | `--scan` the road on five or six rows and write its width per row. Extend both edges with a ruler line; on flat ground they meet on the horizon, and the width at each row is in proportion to that row's distance below it |
| **Distant edges are crisp** | `--zoom` on a near edge and a far edge and compare the width of the soft ramp across each. A far edge that is as hard as a near one pulls forward |

The pattern across all of these: a landscape is a stack of planes going away
from you, and each failure comes from drawing every plane at the same distance.

## Aerial perspective [read: Gurney, Color and Light; Carlson]

Air between you and a form adds its own light. The result, in typical daylight:

- **Darks lighten more than lights darken.** A far forest is mid-grey, not black;
  a far white cliff is still nearly white. So contrast falls with distance, and
  the far band's lightest and darkest values sit close together. Sample both on
  each band; the gap between them is what to compare.
- **Colour shifts toward the colour of the air**, usually toward blue, and
  saturation drops. At sunset or in dust the shift can go warm. Read the shift off
  the subject; do not cool a distance the subject has warmed.
- **Edges soften and detail drops.** Texture is drawn in the near ground and
  stated as a flat in the far.
- **The base of a far range is often lighter than its top**, because haze and mist
  sit in the valleys. A ridge then reads as a band that fades downward into the
  one in front.

What breaks the rule: backlight (far ridges against a bright sky read as dark
silhouettes, though still lighter than near ones), night, thick fog that erases
everything past one plane, and flat graphic styles that set each band's value by
design. If the subject reverses the usual order, the drawing reverses it too.

## The horizon and the ground

- **The horizon is at the eye level of the picture.** Every horizontal line that
  recedes on flat ground meets it. On flat ground a standing figure's head sits
  on it at any distance, if the viewer is also standing [read: Norling; Robertson,
  How to Draw]. That is a check, not a placement: measure where the subject's
  heads fall and ask why if they do not.
- **The true horizon may be hidden** by hills or trees, and the visible skyline
  then sits above it. Find the eye level from the convergence of roads, fields or
  rooftops rather than from the skyline. `redrawing.md` has the case of a
  horizon visible over only a few short runs.
- **Ground recedes in overlapping bands.** Each nearer band overlaps the one
  behind it, and its top edge is the line where the far band disappears. Equal
  steps of real distance take up less and less height on the page as they near
  the horizon. A field drawn as evenly spaced strips is the most common sign
  that this was skipped.
- **Texture shrinks and packs with distance.** Grass blades, stones and furrows get
  smaller and closer together toward the horizon, and past some band they merge
  into a flat. Draw the near ones as marks and stop where the subject stops
  resolving them.
- **The planes have a value order of their own** [read: Carlson]. Under an open
  sky the sky is the lightest plane, flat ground next, slopes darker, and upright
  forms such as trees darkest, because each faces the sky less. A hillside lit
  by low sun can break this. Use the order to ask why a measured band is lighter
  or darker than expected.

## Mountains and hills

- **A range is a silhouette first.** Its skyline carries almost all its character:
  where the peaks fall, how steep each side is, where a shoulder breaks the run.
  Read the skyline with `--scan` from the top of the box (`--side top`) at
  intervals across the range. A guessed skyline comes out as even zigzags, and
  a measured one rarely is.
- **Each range has a lit side and a shaded side.** Fix the light once at stage 0
  and check that every range takes it from the same side. The lit side is one
  value and the shaded side another; ridges and gullies are drawn as the edge
  between the two, not as outlines.
- **Ranges overlap like the ground bands.** The nearer range cuts the base of the
  one behind it, and the far one is lighter and lower in contrast. Two ranges at
  one value merge into a single wall.
- **Hills are softer and rounder**, and their form shows in the shapes of fields,
  hedges and roads that wrap over them. A field boundary running across a hill
  curves with the hill's surface; drawn straight, it flattens the hill.

## Skies and clouds

- **A clear sky is a gradient.** It is usually deepest overhead and lightest and
  warmest near the horizon, and lightest of all toward the sun [read: Gurney,
  Color and Light; Carlson]. Measure the subject at two or three heights before
  deciding how many steps the drawing gives it.
- **A cumulus cloud is a volume with a lit top and a flatter, darker base.** The
  base is flat because clouds of one kind tend to form at one height, so in a
  field of them the bases lie on one plane [read: Gurney, Color and Light].
- **That plane follows perspective.** Clouds near the horizon are further away,
  so they come out smaller, flatter and closer together, and they overlap more.
  Their bases appear to converge toward the horizon, the same as a ceiling seen
  from below. A sky with full-size round clouds down to the horizon stands up
  like a wall.
- **A cloud's edges vary.** Sharp where it turns against blue sky in the light,
  soft where it thins or where one cloud sinks into another. Outlining a cloud
  turns it into a cut-out. Treat it as a mass with lost and found edges.

## Water

- **A reflection lies directly below what it reflects**, on a vertical, whatever
  the angle of view. On still water the reflection of a vertical is vertical
  [read: Norling; Robertson, How to Draw].
- **Measure its length from where the object would meet the water plane**, which
  may be hidden behind a bank. A tree set back from the shore shows only part of
  its reflection, or none.
- **The reflection is the object seen from below the water line**, so it can show
  undersides the object hides, such as the underside of a bridge's arch or a
  boat's hull. Do not mirror the visible object; read the reflection itself.
- **Values in a reflection shift.** A light object usually reflects slightly darker
  and a dark one slightly lighter [read: Carlson]. Rough water shows more of the
  sky's value and less of the reflection.
- **Ripples break a reflection into horizontal pieces.** Each ripple tilts a strip
  of the surface toward the sky, which puts a band of sky value across the
  reflection. The pieces get thinner and closer together with distance, like any
  ground texture. Wind on part of a lake shows as a lighter band with no
  reflection in it.
- **Water is a ground plane.** Its far shore is a band like any other, and the
  water line is a horizontal that recedes with the rest of the ground.

## Roads, paths and rivers

- **On flat ground a straight road's edges meet on the horizon.** Going uphill the
  edges meet above it, going downhill below it [read: Norling; Robertson, How to
  Draw]. Where the measured edges meet tells you which the subject is doing.
- **A road's width on the page falls with distance in a steady way.** On flat
  ground the width at a row is proportional to that row's distance below the
  horizon, so a road at half the depth below the horizon is half as wide. Use
  that to check the scan, not to place the road.
- **A winding road's curves tighten and flatten with distance.** A bend near you is
  wide and open; the same bend far off is a short S lying almost flat. A road
  that drops behind a rise and comes back is two pieces with a gap, and the gap's
  position is where the rise's top edge crosses the road.
- **Ruts, fence posts and road markings are repeated forms** that shrink and pack
  toward the vanishing point. Count them on the subject per band (SKILL.md § Stage 0,
  Inventory), since an even spacing is the usual error.

## Where a landscape meets other subjects

| Overlap | What goes wrong, and which is in front |
|---|---|
| a figure or animal standing on the ground | Feet float when the cast shadow and the contact accent are missing. A nearer figure stands lower on the page; check its feet against the band it stands in. The figure is in front of every band behind its feet |
| a tree / the sky and the hills behind it | The trunk meets the ground in its own band; its crown overlaps the sky and any range behind. The tree is in front. Write sky and ranges first so the crown's flat covers them |
| a vehicle's tyres / the road | The tyre sits on the road surface, with a dark contact line and a shadow running back toward the light's far side. `bicycle.md` covers the wheel itself. The tyre is in front of the road |
| a boat, post or bank / the water | The object, its water line, then its reflection below. The reflection is a flat on the water, written after the water's flat and before any ripple breaks that cross it |
| a road / the hillside it climbs | A road cut into a hill is in front of it (SKILL.md § S0). Where the road passes over a crest, the near slope is in front of the far part of the road |
| a building or fence / the ground | Its base line follows the ground's perspective, converging on the same eye level as the road |
| the near band / the far band | The near band is always in front. Run each far band under the one in front so no hairline of ground opens along the join (SKILL.md § Measure per object) |

The write order follows from the table: sky, then clouds, then far ranges, then
nearer ranges, then ground bands from far to near, then water and its
reflections, then objects from far to near. Record each row in the overlaps table
with its `in front` decision at stage 0.

## No checklist

A landscape has no fixed sub-forms, so this file carries no checklist block. List
the bands, ranges, clouds and water the subject actually has in `parts.json`
from the reading.
