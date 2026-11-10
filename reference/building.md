# Buildings, rooms and furniture as solids

A building goes wrong when it is drawn as a flat front with features stuck on it.
It is a box seen from one eye position, and every edge that runs away from you
points at a place on the horizon. Draw the box from that eye position and the
windows, roof and furniture fit into it. If you draw the front first and
decorate it, each later part ends up with its own perspective.

## Contents

- The ways a drawn building fails, and what each measures as
- Perspective, measured off the subject [read: Norling; Robertson]
- The building exterior
- The interior
- Furniture
- Where buildings meet other things
- Build order

Everything below describes the typical house, room and chair, and **the typical
one is not the one in front of you.** Measure the subject first, then use this
file to ask whether a difference from the typical is real or an error. If you
could follow a passage without looking at the subject, you are using it wrongly.
`[read: source]` marks a claim taken from the named book.

## The ways a drawn building fails, and what each measures as

| The fault | The measurement that finds it |
|---|---|
| **Each part has its own perspective**: the roof, the windows and the door lines aim at different points | Extend three receding edges (a roof line, a sill, a base course) on the subject and on the drawing, and note where they cross. On the subject they meet near one point; on a faulty drawing they scatter. `--overlay --box` over the facade compares each edge's angle with the subject's |
| **The horizon is in the wrong place**: the building looks seen from a ladder or from the ground when the subject was neither | On the subject, find the height where receding edges stop sloping (edges above it slope down toward the far end, edges below slope up). Check that the drawing's level edges sit on the same row |
| **Receding edges are drawn too steep**, so the side wall looks as if it bends toward you | Sight the angle of the top and bottom edge of the side wall on the subject (`measuring.md`, angles). Expect to exaggerate the slope of edges well above or below eye level |
| **Verticals lean where the subject's stand, or stand where the subject's lean** | Drop plumb lines (`--plumb`) through the corners on both images. A photo looking up at a tower converges its verticals; a drawn elevation or a level photo does not. Copy the subject, do not correct it |
| **Windows are holes punched in a flat sheet**: no reveal, no sill, no shadow on the near jamb | `--zoom` on one window, subject beside drawing. The subject shows a strip of wall thickness on one side of the opening and a shadow along the head; the faulty drawing shows a plain rectangle |
| **Wrong number of windows, or windows spaced evenly where perspective packs them** | Count them on the subject per floor and enter the count (`--counts` with `"count": N`). Then `--scan` one row through the window band: the gaps shrink toward the vanishing point on the subject, and stay equal on a drawing that spaced them by eye |
| **The building floats**: no ground line, or a ground line that runs straight past the base | `--scan` a column through the base of each corner. The subject shows a change of value where wall meets ground (a shadow, a plinth, a kerb); the drawing has paper or the same tone running through |
| **The room is a stage set**: floor, walls and ceiling meet at corners that point at different places | Extend the floor-to-wall lines on the subject to their crossing and compare with the drawing's. In a one-point room they all meet at one spot inside the back wall |
| **Furniture slides across the floor or sinks into it** | Mark where each leg meets the floor on the subject. Those points sit on the floor plane, so their heights in the picture change with depth. `--scan` a row under the chair: a leg that ends at the wrong height is in the air or under the boards |
| **A chair has the wrong number of legs showing, or four legs at four equal heights** | Count the legs visible on the subject and note which ones the seat hides. The near legs end lowest in the picture; the far legs end higher and are shorter |

A built thing is seen from one eye position. Each of these failures comes from
drawing its parts from different eye positions, or from none.

## Perspective, measured off the subject [read: Norling; Robertson]

Norling's *Perspective Made Easy* and Robertson's *How to Draw* teach the same
short list, and you can find every item on it in a picture instead of inventing
it:

- **The horizon is at the eye level of whoever took the picture.** It is a
  height in the image, not the line where land meets sky, which is often hidden
  behind buildings. Edges at eye level are horizontal on the page; edges above
  it slope down as they recede, and edges below slope up.
- **Parallel edges that recede meet at one vanishing point on the horizon.** A
  set of horizontal edges all running the same way (sills, gutters, courses of
  brick) shares one point.
- **One-point**: you face a wall square on. Its horizontals stay horizontal, its
  verticals stay vertical, and only the edges running straight away from you
  converge, to a point near the middle. A street seen down its length and a
  room seen through its open end are typical.
- **Two-point**: you face a corner. Each wall has its own vanishing point, one
  left and one right, both on the same horizon. Verticals stay vertical. Most
  house exteriors look like this.
- **Three-point**: you look up or down. The verticals converge too, to a third
  point above or below the picture, as with tall buildings seen from the street.

**Find the points on the subject before drawing a line.** Pick two or three long
receding edges per direction, extend them, and write down where they cross, even
when that is off the canvas. If they do not meet at one point, the subject is
not a strict projection (a drawn or generated image often is not). In that case
follow the subject's edges one by one, and do not force them to a point the
subject does not use.

In a two-point view a vanishing point far outside the canvas is normal. The
closer the two points sit to each other, the more distorted the box looks:
points too close together make a corner look sharper than square, and the box
reads as wrong rather than as seen from close up. If your measured points are
close, check the subject again before trusting them.

## The building exterior

**Mass first.** A house is one or two boxes with a roof on top. Before drawing
any opening, read off the subject how many boxes there are and where they join.
An extension or a porch is its own box with its own edges, and uses the main
block's vanishing points when it is square to it.

**The roof** is a prism sitting on the box. Its eaves are horizontal edges that
go to the same points as the walls below. Its sloping edges (the gable's rake, a
hip line) go to points of their own, above or below the horizon, on a vertical
line through the wall's vanishing point. The gable's ridge sits over the middle
of the gable wall, and in perspective the middle is not halfway across: find it
by crossing the wall's diagonals [read: Norling]. Check the subject's ridge
against that crossing; if it is off, ask whether the roof is asymmetric or your
wall is wrong. Eaves overhang the wall, and the shadow under them is often the
darkest line on the building.

**Openings are set into the wall's thickness.** A window is a hole with depth:
the frame sits back from the face of the wall, so a strip of jamb shows on the
side turned away from you and is hidden on the near side. A sill projects
forward and catches light on its top. Guptill's *Rendering in Pen and Ink*
renders windows mostly through the dark of the glass and the shadows of the
head and jamb, with little outline [read: Guptill]. Measure on the subject which
side the jamb shows and how wide the shadow under the head is; both change with
the view and the light.

**Count repeated windows instead of suggesting them.** Count them per floor on
the subject and write the count in the inventory. In perspective, equal spacing
on the wall becomes shrinking spacing on the page. Place the outer two from
measurement and divide between them using the wall's diagonals, or read every
edge with `--scan`. Do not fill the facade with evenly spaced rectangles, and do
not drop a window because the row looked long enough.

**The ground line.** The base of every wall sits on the ground, a plane
receding to the same horizon. Where the subject shows a plinth, a shadow, steps
or grass meeting the wall, draw it. A building with no base looks cut out and
pasted onto the picture.

## The interior

A room is the inside of a box. In a one-point view you see the back wall square
on, and the floor, ceiling and side walls are four planes running from the
picture's edges toward it. Their four meeting lines all aim at one point, which
sits on the horizon at the eye height of the viewer.

- **Read the eye height off the back wall.** If the vanishing point sits a third
  of the way up the back wall, the viewer's eyes were at a third of the room's
  height. Moving it changes how tall the viewer is and how much floor you see.
- **The floor carries the room.** Tiles, boards and rugs all obey the same
  vanishing point, and their joints show the floor's depth. Boards running away
  from you converge to it, and the cross joints get closer together as they
  recede.
- **Doors, windows and pictures on the side walls** use that wall's
  convergence: their tops and bottoms slope toward the vanishing point, their
  sides stay vertical.
- **The ceiling is often cropped out** of the subject. Then leave it out of the
  inventory too, with a reason in `_absent`.

A two-point interior (looking into a corner) works the same way with two points.
To tell which you have, check whether the back wall's top and bottom edges are
level on the subject.

## Furniture

Chairs and tables are boxes too, and Robertson and Norling both start them from
one [read: Robertson; Norling]. Draw the box that contains the piece, using the
room's vanishing points if it sits square to the room and its own if it is
turned. Then cut the piece out of the box.

- **A table** is a thin box (the top) on four posts. The top's front and back
  edges converge like the floor's. The legs stand at the top's corners, or set
  in from them; measure how far in on the subject.
- **A chair** is a seat box with four legs below and a back panel rising from
  the rear edge. The back usually leans, so measure its angle instead of
  drawing it upright.
- **Count the legs and place them in perspective.** The four feet are the
  corners of a rectangle on the floor that recedes like the floor does, so the
  near feet sit lowest in the picture. A far leg is partly or wholly hidden by
  the seat or the near leg; note which on the subject and write it in the
  overlaps table.
- **Contact with the floor** is a small dark shape, not a line: the shadow the
  foot casts, often a tiny wedge on the side away from the light. Without it the
  chair floats, however good its perspective.

A turned chair in a square room is the case most often drawn wrong. Its edges go
to points of their own, still on the same horizon. If its points are not on the
room's horizon, either the chair is tilted or your horizon is wrong.

## Where buildings meet other things

| Junction | What is in front, and what to draw |
|---|---|
| **Wall and ground** | The ground runs behind the wall's base. A shadow, a kerb or planting at the base carries the contact |
| **Figure and building** | If the viewer was standing too, a standing figure's eyes sit on the horizon at any distance on level ground. Check each figure's eye height against the horizon you measured; a figure whose head is far above it is a giant |
| **Tree or lamp-post in front of a facade** | The near object is drawn over the facade. Write the facade's ink first so its windows stop at the trunk and restart beyond it |
| **Cup, book or plate on a table** | It sits on the top plane and uses the table's vanishing points if square to it. A cup's rim ellipse lies flat in that plane, and a small shadow under its base shows the contact |
| **Chair at a table** | The table top usually hides the chair's front edge or seat; the seat hides its far legs. Each crossing is its own row in the overlaps table |
| **Person in a chair** | The body's weight sits on the seat plane. Thighs follow the seat's depth into the picture; the back meets the chair back |
| **Car in a street** | Its wheels sit on the road plane, which shares the horizon with the buildings. If the car is parallel to the kerb, it also shares their vanishing point |

## Build order

1. **The gesture first, then the horizon and the vanishing points.** Write
   every loop of a block, roof or tower in the gesture with `smooth=False`:
   smoothed, a tall block with a pitched roof renders as an oval, and the
   describer sees a row of jars or pots instead of a building. Then find the
   horizon and vanishing points on the subject and write them down as
   coordinates, even off the canvas.

2. **The main box or the room box**, as straights from measured corners, checked
   against those points.
3. **The roof, or the floor and ceiling planes**, hung on that box.
4. **Openings**, counted and spaced in perspective, each with its depth.
5. **Furniture boxes**, then legs, then the contact shadows.
6. Only then the texture (brick, boards, tiles), and only as much of it as the
   subject shows.

`check.py --checklist parts.json` reads these blocks and fails on any sub-form the
inventory neither names nor excuses in `_absent`:

```checklist
object: house|building|cottage|barn|church|shed
sub-forms: wall roof window door
```

```checklist
object: room|interior
sub-forms: floor wall ceiling
```

```checklist
object: chair|stool|armchair|bench
sub-forms: seat leg back
```

```checklist
object: table|desk
sub-forms: top leg
```
