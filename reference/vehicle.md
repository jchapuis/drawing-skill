# The vehicle as a solid

A car goes wrong when it is drawn as a side-view outline with wheels stuck on.
It is a box in perspective that sits on four wheels, and each wheel is a circle
seen at an angle. Drawn as a silhouette, the box has no top or front plane, the
wheels turn into upright ovals, and the body floats off the road. This file
covers cars first, then boats, aircraft and trains. Bicycles and motorbike
wheels are in `bicycle.md`.

Everything below describes the typical vehicle, and **the typical vehicle is not
the one in front of you.** Build on landmarks measured off the subject. Use what
follows afterwards, to ask why your measured vehicle differs and whether the
difference is real or an error. If a passage could be followed with the subject
covered up, you are using it wrongly. `[read: source]` marks a claim taken from
the named book.

## The seven ways a drawn car fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **Wheels drawn as upright ovals** whatever the car's turn, so the car looks as if its wheels are steering or wobbling | Sight the tilt of each wheel's long axis on the subject as a clock-face angle (`measuring.md`, Angles) and check the drawing at the same tilt. `check.py --overlay --box` on one wheel shows both ellipses together |
| **Wheels too small or set too far in**, so the car reads as a toy or a bus | Take the subject's wheel diameter as the unit and count units along the wheelbase and the overhangs front and back. Wheels are easy to misjudge by eye; measure them |
| **The body floats**: a band of ground between tyre and road, or no dark under the car | `--zoom` on the contact box. On the subject the tyre meets its own shadow with no light between them, and the darkest value under the car is right where the tyre touches |
| **The box does not converge**: roof line and sill line drawn parallel when the subject's close toward a vanishing point, or closing the wrong way | Sight the angle of the roof line, the waist line and the sill line separately and compare them. `--overlay` on the block-in shows which straight is off |
| **The glass is too tall** and the body below it too thin, or the reverse | `--scan` one column through the B-pillar (the post behind the front door) and read off where glass stops and painted body starts. The ratio of glass height to body-side height is the car's character, and drawings push it toward a default |
| **Near and far sides drawn the same width** on a three-quarter view: two equal headlights, two equal wheels | Measure the near and far headlight widths, and the near and far front wheel ellipses. The far one is narrower on most subjects; if the drawing's are equal, the drawing has gone front-on |
| **Reflections drawn as soft streaks or scattered highlights** | `--masses --box` on a door panel: the subject's reflections come back as a few hard-edged shapes of flat value. A drawing whose panel comes back as one blurred value has lost them |

The common thread: a car is a few large planes and four ellipses, and most of
these failures come from drawing its outline instead of its planes.

## The body is a box before it is anything else [read: Robertson, How to Draw; Norling]

Block the whole car as one box in perspective before any curve. Its three
visible faces (side, front or rear, top) are what later carry the light, and
each edge of the box is a straight you can sight against the subject. Scott
Robertson's *How to Draw* builds vehicles this way: a box sized to the car's
length, width and height, set into a perspective grid, then the wheels placed
in it, then the body carved out of it. Norling's *Perspective Made Easy* gives
the same box-first approach for any manufactured object.

- **Length, width and height come first.** Measure them off the subject as
  ratios to the wheel diameter. A small hatchback and an estate car can have
  similar heights and very different lengths.
- **The waist line** (the crease or edge under the side windows) runs the length
  of the car and is usually the most legible line on it. It follows the box's
  perspective like the roof and sill do. Sight its angle on the subject.
- **Plan view tapers.** Most car bodies are narrower at the roof than at the
  sill, and many narrow toward the nose. Seen from the front, the side of the
  car leans in toward the roof. Drawn straight up, the car looks like a van.
  Measure the lean on the subject rather than assuming it.

## Wheels and arches [read: Robertson, How to Draw; Norling]

- **The minor axis of a wheel ellipse lies along the axle.** The axle runs
  across the car, so the ellipse's short axis points along that line in
  perspective, and its long axis is at right angles to it. This is the
  standard rule for any circle in perspective and both Robertson and Norling
  teach it. It is also why an upright oval on a turned car reads as wrong:
  its short axis points nowhere the axle goes.
- **Each wheel is its own ellipse.** The front and rear wheels on one side are
  at different distances and different angles to your eye, so their widths
  differ. Measure each one.
- **The hub is not at the centre of the ellipse** in a true perspective
  projection; it sits a little toward the near side. A generated or drawn
  subject does not always obey this, so measure each hub. `bicycle.md` has the
  same point for bicycle wheels.
- **A wheel is several bands**: the dark tyre, the rim, the spokes or disc, the
  hub. Their widths along a radius are what make it read as a wheel. Measure
  them with `--scan` on a one-row box through the hub and `--value` naming the
  tyre's and rim's palette names, as in `bicycle.md`.
- **The arch is a cut in the body around the top of the wheel**, with a gap
  between tyre and arch edge. The gap varies a great deal between cars (a
  lowered sports car has almost none, an off-road car a wide one), so it is
  one of the measurements that gives a car its stance. Measure it at the top of
  each wheel with a one-column `--scan`.
- **The inside of the arch is dark.** The far edge of the arch opening shows as
  a dark crescent behind the tyre. Without it the wheel looks pasted onto the
  side.

## The glass and the body

The car splits horizontally at the waist line into the **glass area** above and
the **body** below. Car designers call the upper part the glasshouse or
greenhouse. The two read differently and should be decided separately.

- **Glass is usually darker than the paint and carries the sky.** A windscreen
  tilted back reflects the sky and is often the lightest glass on the car; side
  windows facing you show the interior and are darker. Sample both off the
  subject, never one value for all the glass.
- **Pillars** (the posts between windows) set the rhythm of the side view.
  Count them on the subject and measure the slope of the front pillar, which
  follows the windscreen's rake.
- **The glass sits in from the body side** on most cars, so there is a ledge
  along the waist. Seen from above or at three-quarter, that ledge is a thin
  light band.

## Reflections are shapes [read: Gurney, Color and Light; Robertson, How to Render]

A glossy panel shows what is around it, not its own colour shaded. On a car
side the usual pattern is the ground reflected low on the door (dark) and the
sky reflected high (light), with a fairly sharp line between them where the
horizon reflects. That line follows the curve of the panel, so it bends where
the body bends and helps say which way each panel faces. Robertson's *How to
Render* works through this; Gurney's *Color and Light* covers reflections and
specular light on shiny surfaces in general.

For drawing: each reflection is a flat with a hard edge, drawn as its own
region in `regions.json`. Trace the subject's reflection shapes and count them.
Do not invent a reflection pattern from this paragraph: the subject's
surroundings decide what is reflected, and a studio shot looks nothing like a
street.

## Lights, grille, mirrors, doors

- **Headlights and tail lights** sit on the corners where the front or rear
  plane turns into the side. On a three-quarter view the far light is
  compressed and partly hidden by the nose. Measure both.
- **The grille** is centred on the front plane. On a turned car its centre is
  not the middle of the front's bounding box; find it the way you find a head's
  centre line in `head.md`.
- **Mirrors** stick out from the base of the front pillar, past the body side.
  They are often the only thing that breaks the silhouette above the waist.
- **Door shut lines** are thin dark lines that follow the body's surface. Drawn
  at full ink weight they cut the car into pieces. Measure their width with
  `--weights` against the outline's.

## Where the car meets other things

| Where | What to look for | In front |
|---|---|---|
| **Tyre on road** | The tyre flattens slightly at the bottom; the shadow under it is the darkest value under the car. No light gap | Tyre in front of its own shadow |
| **Body over road** | A band of shadow under the sill, sharp near the wheels and softer between them on most subjects. Measure its height | Body in front of shadow |
| **Driver behind glass** | Seen through glass, the figure takes the glass's value over it; its edges are softer and lower in contrast than anything outside | Glass in front of figure |
| **Car behind car, or behind a figure** | Write the far car first, fill and ink, so the near form covers its lines | The nearer form, by write order |
| **Car on a reflective ground** (wet road) | The reflection is the car turned upside down below the contact line, darker and softer | Car in front of its reflection |

Each row goes in the overlaps table with its `in_front`, and `--depth ops.json
parts.json` checks the write order.

## Boats [read: Carlson; Gurney, Color and Light]

- **The hull is a curved wedge**, widest near the middle and narrowing to the
  bow. The **sheer line** (the top edge of the hull from bow to stern) usually
  rises toward the bow. Sight its curve on the subject; drawn flat, the boat
  looks like a tray.
- **The waterline is where hull meets water** and it is a curve in perspective,
  not a straight. It is often the line that seats the boat; if it is wrong, the
  boat floats above the water or sinks into it. `--zoom` on it and compare.
- **The reflection is the boat mirrored about the water's surface**, measured
  from where the hull meets the water, not from the bottom of the drawn hull.
  Ripples break it into horizontal pieces and pull it longer downward. Carlson
  and Gurney both describe reflections in water as differing in value from the
  thing reflected; read the value off the subject rather than reusing the
  hull's.

## Aircraft and trains

- **An aircraft is a cylinder with flat planes through it.** The fuselage is a
  long tube that tapers at both ends; the wings are thin slabs that cross it.
  The usual errors are wings drawn at the wrong angle to the fuselage in
  perspective, and the far wing drawn as long as the near one. Sight both wing
  tips against the fuselage and measure each.
- **A train is a box repeated along a line.** The cars share one set of
  vanishing points, so their roof lines all close toward the same point. Count
  the windows and wheels on the subject (`--counts` with a count on the entry)
  rather than drawing a pattern that looks about right. The rails are two
  converging lines that the wheels sit on; check that each wheel touches its
  rail.

## The sub-forms an inventory descends to

"Car" is not one part. An inventory entry that stops at the car gives the
count, `--depth` and the part-crop describer nothing to check. Look for these on
the subject, and write an entry for each that is there:

```checklist
object: car|automobile
sub-forms: wheel|tyre|tire window|windscreen|windshield headlight door mirror arch
```

```checklist
object: boat|ship
sub-forms: hull deck reflection
```

`check.py --checklist parts.json` reads these blocks and fails on any sub-form
the inventory neither names nor excuses in `_absent`.

## Build order

1. **The box**, from measured length, width and height, with its roof, waist
   and sill lines sighted against the subject.
2. **The wheels** as ellipses with their minor axes on the axle lines, each
   measured; then the arches around them, with the measured gap.
3. **The split between glass and body** at the waist line, and the pillars.
4. **The contact with the ground** and the shadow under the car, at the same
   stage as the wheels, never after.
5. Lights, grille, mirrors and door lines, each placed on the plane it belongs
   to.
6. Reflections last, as flats with hard edges, traced from the subject.

Draw the car whole and at one stage throughout. A finished front end over a
blocked-in rear is the same fault as a finished head over a blocked-in chest.
