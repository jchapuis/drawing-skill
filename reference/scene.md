# Drawing a scene

A scene is not a bigger subject. It is a different problem, and the difference is
arithmetic: **quality falls off with the number of things in the picture, because
the budget divides by the part count.**

Same method, same instrument, a fixed budget. A single subject of about twenty
named parts gets a few tens of thousands of tokens per part and comes out
coherent first time. A scene of seventy or eighty parts gets a quarter of that
per part, and every part arrives thin — a garment that is a balloon, a hip with
no joint in it, a tyre that never closes. **Nothing there is a *mistake*.** It is
what happens when nothing is built, and no amount of correction reaches it,
because there is no error to find.

**So the part count, not the difficulty, is what makes a scene hard**, and the
only variable you control is how unevenly you spend. Everything below is about
spending unevenly on purpose.

## Whole before part governs placement, never investment

The second law's structural form — *no part may be more than one stage ahead of
any other* — is right. Applied to an eighty-part scene as a rule about *effort*
it guarantees eighty **equally shallow** parts, with a background prop carrying
as much construction as the figure's shoulder.

No illustrator works that way, and a reference panel almost never does either:
look at one and the figure and its machine are fully built while the furniture
behind them is three or four confident lines each.

> Every object reaches every **stage** together. How far each object is **built**
> inside that stage is a decision you make once, before the first mark, and it is
> not equal.

## Rank the objects before you draw one

At stage 0, after the inventory and before anything else:

1. **Say in one sentence what the picture is about.** Not what is in it — what it
   is *about*. Not "a cyclist in a cellar" but "a man going nowhere, with the
   ride he is not having pinned to the wall in front of him."
2. **Put every named part in a tier.**

| tier | what it is | treatment |
|---|---|---|
| **1 — carries the picture** | The thing the sentence is about. Usually one or two objects | Fully constructed. Volume under every contour, interfaces resolved, the detail pass at 4x |
| **2 — supports it** | Objects that make tier 1 legible or place it in the world | Constructed in the large forms; no interior modelling that is not doing work |
| **3 — furnishes it** | Everything else, and it is most of the list | **Stated** in the fewest confident marks that read as the thing |

For a figure among furniture: tier 1 is the figure and whatever it is doing
something with. Tier 2 is the few objects that make that legible or place it in
the world. Tier 3 is everything else — routinely nine-tenths of the panel's area
and a twentieth of its work.

**A tier is not permission to draw something badly.** Tier 3 gets *fewer* marks,
each of which must be *right* — a clock stated in four correct lines beats a
clock built badly out of forty. The skill already knows this and never applied it
hierarchically: *it takes more skill to render a form in fewer lines than in
more.* Economy is what pays for the figure.

## Budget it, in advance and in writing

You will not build eighty parts. Decide which twenty before you start, rather
than discovering at stage 8 that you have spread everything evenly and nothing is
finished. Write the tier list into the working notes with the inventory, and when
the budget runs short, **cut depth from tier 3, never from tier 1** — the failure
mode is a panel in which everything is equally unbuilt, and the deliverable that
beats it is a panel whose subject is built and whose furniture is stated.

## Interfaces are objects, and they are where scenes fail

Scene faults concentrate at the junctions between things:

| interface | how it fails |
|---|---|
| hand / handle | one fused dark mass, where the subject separates them with a band of its own ground or a second lighter value |
| foot / pedal | two discs, until a sole and a strap slot go in |
| hip / seat | no joint at all — supports leaving the bottom of a black shape |
| limb / tube behind it | the tube's ink runs straight over the limb in front |
| wheel / floor | the ring never closes, so nothing bears weight |
| shoulder / arm | no upper arm; the forearm starts at the garment's edge |

A single subject has almost none of these. A scene is mostly these. So:

- **Put the interfaces in `parts.json` as named parts with their own boxes.** They
  are not covered by the boxes either side of them, they are exactly the gap
  between those boxes, and no check looks there unless you name it.
- **Draw the interface at the same time as both objects it joins**, not after
  either one is finished. A hand drawn onto a finished bar is a hand stuck on.
- **Occlusion is drawn, not filled over.** The contour of the far object stops
  where the near one crosses and restarts beyond it — a flat cannot hide ink,
  because the ink sits above the fill.
- **Decide the depth order per crossing in writing, at stage 0, beside the
  interface itself.** Which of the two is in front is a *decision*, and no mark
  records it: a stroke has no z, `back("fill")` moves a whole stage and not one
  object, and the checks have no way to ask. So the interfaces list carries a
  third column — `in front` — and it is complete before anything is inked.
  Without it the order is settled by whichever mark happened to be written last,
  which is how a chainring came to be drawn across the shoe standing on it.

**What that costs when it is skipped.** Two objects that cross come out as one
black mass, and the cause is usually not value — measure both and they are often
the same colour in the subject too. The cause is that the far object's marks were
drawn over the near one and nothing had decided they were behind it. The fix is
arithmetic once the decision exists: take the near object's silhouette as a
polygon, test the far object's points against it, and re-emit the far contour as
the runs that fall outside. **Compute that, never judge it** — at 1:1 a crossing
that is a few pixels wrong and one that is right look identical.

## What makes a scene hard, so you can see it coming

- **Many depth planes.** Two objects on different planes must never share a value
  or they weld into one plane, and in a scene there are five or six planes, not
  two.
- **One light, many forms.** Every object must answer to the same source. A scene
  drawn object-by-object drifts, and the giveaway is shadows that disagree.
- **A fixed budget over a growing part count.** The only variable you control is
  the tier list.
- **The interfaces multiply faster than the objects.** Ten objects have far more
  than ten junctions, and each one is a place to fail.

## Studies, and how they buy back the budget [read: comics and atelier practice]

The arithmetic at the top of this file says a scene cannot afford to build
eighty parts. Studies are how the profession has always got round it, and they
are not a workaround — they are the standard pipeline. Thumbnails settle the
composition before anything is drawn at size. Elements get worked on a separate
sheet, traced through a lightbox and dropped in. Pencils are preserved by inking
on a fresh sheet over them. Roughs are scanned, scaled, printed as **bluelines**
on the final sheet and drawn over, never redrawn from memory. The oldest version
is the Renaissance *cartone*: a full-size preparatory drawing worked until it is
right, then pricked and pounced onto the wall.

The reason it works here is the arithmetic: **an object drawn on its own is a
small subject again**, and gets a small subject's attention however many parts
the panel has. A single subject drawn alone comes out coherent by this method; the
same method spread over eighty parts does not.

### A study builds the capacity to draw the thing, not one copy of it

This is what separates a study from a careful copy, and getting it wrong wastes
the whole device. A study is **the same form drawn several times, off the panel,
from different angles and in different positions** — a bicycle three-quarter from
the left, then head-on, then leaning, then with a leg across it — until the form
is *understood as a solid*. Only then is the panel's instance drawn, from that
understanding rather than from the reference's outline.

Draw it once, in place, at the angle the panel needs, and you have a traced
silhouette: principle 5 says such a mark records the 2D boundary from one angle,
contradicts nothing, and therefore has no way to be wrong — which is the same as
no way to be corrected. Repetition from varied angles is what turns it into a
volume, because a form you can only draw from one angle is a shape you have
memorised, not a thing you understand. The test is mechanical: **if you cannot
draw the object at an angle the reference does not show, you have not studied
it — you have copied it**, and it will come apart at the first junction that
needs it to be solid.

That is also why a study is cheap despite being repetition. Three attempts at one
object are three small subjects, and the understanding transfers to every
instance afterwards; one thin pass inside an eighty-part panel transfers nothing.

### Where a study lives, and how the panel gets it

Studies go in **their own document** — the repetition and the odd angles have no
place in the panel, and the panel is the drawing. Give `pen.write` a separate ops
file and render it separately.

The panel's instance is then drawn in the panel, tagged, and worked with the
object filtered into view:

```bash
# the object, every stage, over the composition rough beneath it
node harness/cli.mjs DOC.json --only bike --only blockin --only frame --png bike.png

# the detail pass: that object magnified, subject above, drawing below
python3 check.py drawing.png --ref subject.png --zoom 340,600,420,400 --out crop-bike.png
```

`stroke` takes `tag=` for the object alongside `stage=` for the ladder phase, and
both `--only` and `--hide` match either. Tag every mark of a tier-1 object as you
place it; the ladder machinery is untouched, so `erase("contour")`, `--hide ink`
and `back("fill")` all still reach a tagged mark. Filtering keeps the object's
marks in the panel's own coordinates, so nothing has to be fitted afterwards —
which matters because the junctions between objects are already the worst thing
in every scene.

Run the 4x detail pass per tier-1 object after every few marks. It reaches faults
no whole-panel check can: a feature swallowing its neighbour, a closed form
rendering open, a strap drawn through an ear.

**Order the depth per tube, not per object.** "Draw the bike, then the figure" is
the wrong grain: the top tube passes in front of the far leg and the seat tube
passes behind the near one. An object is not at one depth, and treating it as if
it were silently paints a thigh over a tube.

**The interfaces need both objects present**, so they are drawn in the assembled
panel and nowhere else — hand-on-bar and foot-on-pedal cannot be resolved by
looking at either object alone. Give them the budget the tier list saved.

Which objects get the 4x detail pass: tier 1, and nothing else. Spending one on a
wall clock is the same mistake as building it in the first place.

## Splitting a scene across drawers [bought: drawing]

A panel divides badly by area and well by object: two drawers each taking half a
picture meet at a seam nobody owns, while one drawer per tier-1 object meets at the
interfaces, which the panel has to name anyway. The split is worth making — the
arithmetic at the top of this file is about a budget divided by part count, and an
object drawn on its own is a small subject again. What follows is what survives
being handed between drawers and what does not.

**Studying and painting can be different drawers. Reading and drawing cannot.** The
drawer who paints must look at the subject itself; a handoff aims that looking and
never replaces it. Treat a handoff as a hypothesis with good pedigree: every
statement in one that proves wrong is caught by the painter re-measuring, and none
of it is catchable by trusting the page — including an asymmetry stated backwards,
which inverts a likeness while every box stays correct.

**What transfers**

- **Decisions**, expensive to reach and cheap to state: the light — including
  *there is none*, which is a measurement, not an omission — the value families and
  the empty gap between them, the depth order at every junction, what to leave out.
  These are the handoff's real value; reaching them cold costs rounds, and a drawer
  without them invents a shadow the subject does not have.
- **Numbers**: landmarks, the measured weight span, the palette with where each
  value was sampled, and the departure from the canon with the direction each
  feature is to be pushed — including which features are canonical and must *not* be
  pushed, or the contrast the departures carry is spent.
- **The census** (below).

**What does not transfer**

- **Boxes.** An inventory of bounding boxes cannot become a mark, and a box must
  never be drawn to. A drawer handed only boxes still traces every contour itself,
  which is most of the work the study was supposed to save. Hand over measured
  contours — the runs of points — or expect the outline to be measured twice.
- **Procedures.** A handoff passage that could be followed with the subject covered
  up is a scaffold, and it arrives precisely at the stage whose job is to find the
  particular form. Test every line of a handoff that way before sending it.
- **A weight ladder as numbers.** Each instrument has its own ladder and nothing in
  the numbers says so. A span stated in pixels is not a setting: the painting
  drawer draws and measures its own ladder with the instrument it will use.

### The census — the check that catches an extra part

Every other instrument here asks whether what was drawn is right. The census asks
how many there are. Before drawing, state the count of every countable thing, and
state the zeroes: no nostrils, no lips as shapes, no shadow on a face that carries
none. A missing part is caught by walking the inventory; a part drawn twice, a
third limb, a second shadow, a second near ear — nothing else catches those,
because an extra part has no box to be absent from. Count them in the render and
compare against the list.

The census is also where a blind reader pays for itself twice over: shown numbered
crops with no sight of the writing, it names parts the inventory does not have. A
part the drawer never knew was there cannot be found by any scan the drawer writes,
because the mask excludes the region it never suspected.

### Accept a delegated drawing by its script, before looking at it

Run the ladder audit from `SKILL.md` on what comes back. A drawing that measured
honestly and skipped stages 6 and 8 comes back with its lines as filled shapes and
not one mark carrying its own taper, and it will pass every placement check in this
file. The script says so in four numbers; the picture takes a 4x crop and an
argument.

### Budget, and why a self-reported one is not a budget

Studying one object to this depth and then painting it can cost more than an entire
panel has ever cost, which is the whole reason tiers exist: study tier 1 only, and
let tier 3 arrive in the panel's own pass with the few confident marks it is owed.
Enforce the cap from outside the drawer, too — a drawer's own estimate of what it
has spent has come back low by more than a factor of two, and pacing by that
estimate silently spends the panel's budget on one object.

## Order of work

1. **Read the scene**: the sentence, the big shape of the whole composition, the
   depth planes and their three values, the light.
2. **Inventory, with tiers and interfaces named**, boxes off the subject.
3. **Gesture and envelope for the whole panel**, composition first — where the
   masses sit relative to each other and to the frame, before any object is a
   thing rather than a mass.
4. **Block-in every object together**, in straights, tier-blind: placement is
   equal work for everyone.
5. **Masses for the whole panel**, and check they read as the subject's do.
6. **Freeze the rough.** It does not move again; everything later is drawn over
   it.
7. **Construction, tiered.** Here the budget divides. Tier 1 is worked until it
   would stand as its own drawing, checked at 4x against the subject with
   `--zoom` after every few marks. Tier 3 gets the marks it needs and no more.
8. **Draw the interfaces**, with both objects present, which is the only state
   in which they can be drawn at all.
9. Contour, cleanup, ink, fill, correct — each sweeping the whole panel, each
   spending at the tier's rate.

**The stage gate means "no part has been SKIPPED at this stage" — not "every part
has had equal work".** Those are different, and taking it as
work-parity makes it unusable the moment tiers exist: at the masses gate a tier-3
background band is *finished* by its single flat while a tier-1 cow head is only
*begun* by its flats. Both are at stage 5. Walk the inventory for omissions, not
for equal depth — being *at* a stage means something different for a rider than
for a clock, and you decided which at stage 0.

**Budget by stage, not only by part.** The tier list divides the
work between objects; it says nothing about where the run's time actually goes,
and a drawer who has planned tiers is still surprised. Measured on a 12-object,
84-part panel, to the end of the masses gate: **stage 0 — reading, measuring, the
inventory and its blind validation — 55%**; gesture/envelope/block-in 15%;
construction 3%; masses plus one correction round 27%. Stage 0 on a scene is more
than half the job and should be, but plan it rather than discover it. Add to that
a fixed cost the tier list also cannot see: **loading this skill is itself a
material fraction of a scene's budget** — a scene with a figure, a machine,
animals, hands, faces, line and colour needs nearly every reference entry, and
both drawers spent roughly a third of their run reading before a mark existed.
