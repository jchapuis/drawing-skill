# Light, value, edges — and how line alone carries volume

## The anatomy of light on form

Lightest to darkest, on a 10-step scale:

| Zone | Value | Rule |
|---|---|---|
| **Highlight** | — | A reflection *of the source*. Only on shiny surfaces; absent on matte. Moves when the **viewer** moves |
| **Centre light** | 9–10 | The plane most perpendicular to the source. Fixed by geometry, independent of the viewer. This is the diagnostic separating it from the highlight |
| **Halftones** | 4–9 | Planes partly facing the light, lightening as they face it more directly. Most of the lit area, and most of the work |
| **Terminator** | — | Not a value: the *boundary* where a surface stops facing the light |
| **Core shadow** | 1–2 | Darkest part of the form shadow, just past the terminator, receiving least bounce |
| **Reflected light** | ~4 | Bounced light re-entering the shadow. Takes the colour of what it bounced off |
| **Occlusion / contact** | 0 | Where surfaces meet and *all* light is blocked. **The darkest note in the picture** — darker than the core shadow |
| **Cast shadow** | 2–3 | A separate overlay, not part of the form shadow |

**The hard rule on reflected light:** it must never be as light as *any* halftone.
Overstating it is the single most-cited failure — it starts reading as a
halftone, the two families collapse, and the form flattens.

**Cast shadow edges:** hard from a point source, soft from a diffuse one. Also
sharp where the shadow meets the object casting it, softening with distance.

**Model one side, flatten the other.** Rendering both the light and shadow
families fully reads as fussy. Choose which family carries the detail.

**Under diffuse light** there is no terminator and no core shadow at all — up
planes go lighter, down planes darker, and occlusion shadows become the only
sharp accents.

## Separation of the families

**The lightest value in shadow must be darker than the darkest value in light.
The two families never overlap.** This is the single most important rule in
rendering.

Work it as **notan**: before any halftone, reduce everything to two flat values
— one pale for everything lit, one dark for everything in shadow. Block the whole
shadow shape at a single flat value (~3) *before* differentiating core shadow,
reflected light and occlusion inside it.

Verify the two-value pattern still reads when squinted or shrunk. If it does not,
no internal detail will save it.

**Finding the terminator:** trace where the surface stops facing the light. On a
primitive it is a clean line or ellipse. On an organic form it is **not one smooth
curve** — it bends locally with each plane's own facing, deviating around a brow
ridge or a muscle. Resolve it plane by plane.

Its position is a decision: moving the light toward the viewer enlarges the lit
side; moving it behind does the reverse. Fix that before committing.

**Map edges before filling values.** Three edge families: terminator/core-shadow
edges (soft or hard by curvature), cast-shadow edges (usually sharper), and
silhouette edges (sharp unless deliberately lost).

## Plane-based shading

Value follows **orientation, not distance**. A plane is lighter purely as it
faces the source more directly.

Assign **one flat value per plane** by its angle to the light, before any
transition is attempted. Boxes before curves: a box has no terminator gradient at
all — each face is one flat value with a hard jump to the next.

Why flat-first beats gradient-first: the planar pass is what lets you *choose*
edge character per transition — hard at a box corner, soft at a sphere's rounding.
A gradient applied everywhere erases the plane information and reads as mush,
because it destroys the discrete decisions that make an object legible as an
assembly of surfaces.

Order: separate lights from darks, then differentiate midtones. Never start from
a blend.

## Cross-contour — the load-bearing technique for line

A contour describes a form's outer silhouette. A **cross-contour** describes the
*surface*, running across the form like a contour line on a map. In a line-only
medium this is the primary way volume is stated.

- **Curvature = surface curvature.** Flat surface → straight line. Round surface
  → curved line. The more curved the stroke, the rounder the form reads; the
  straighter, the flatter.
- **Spacing = rate of turn.** Lines clustering tightly signal a surface turning
  away fast; wide even spacing signals a flat or gently curving area.
- **Arcs tighten toward the silhouette.** A cross-contour should be shallow
  across the part of the form facing the viewer and steepen as it nears the outer
  edge, because foreshortening accelerates there. It is a gradient along the
  stroke, not a uniform arc.
- **Parallel** cross-contours on single-axis forms (limbs, branches, cylinders);
  **orthogonal** (two crossing sets, like latitude and longitude) on doubly
  curved forms (a sphere, a skull).
- **Anchor them to structure** — a ridge, a muscle boundary, a plane change — not
  to a uniform grid.
- Apply **after** the construction block-in and **before** rendering. It is a
  volume-verification pass, not a decorative finish.

No numeric spacing system exists; placement is a design decision driven by the
rules above.

## How line alone describes form

- **Weight = light.** Heavier on the side facing away from the light; thin,
  broken, or absent where light hits hardest.
- **Weight = depth.** Thicker at edges nearest the viewer; progressively lighter
  as a contour recedes.
- **Weight = contact.** Heaviest where two forms touch or overlap — the line
  equivalent of the occlusion shadow being the darkest note.
- **Weight = mass.** Taper a stroke along its length to suggest a bulge, with no
  reference to light at all.
- **Lost and found.** Draw, leave a gap, resume. Drawn segments read as a hard
  edge; the gaps read as soft. **This is the only substitute for edge-softness in
  a value-free medium** — use it where a surface rounds away, goes out of focus,
  or fades into shadow.

**Never draw a uniform unbroken outline.** Every source treats a single-weight
continuous contour as *the* flattening failure. Contour cannot be continuously
defined all the way around every form and still leave a sense of space.

A convincing line comes from having mentally realised the volume before making
the mark. The contour is the result of rich forms overlapping in the round, not a
traced silhouette.

## Edges

Four kinds, each with a physical cause rather than a stylistic one:

- **Sharp** — a sudden plane change. Reserve for the focal point.
- **Firm** — a rounded corner with slight blur.
- **Soft** — a large gently rounding form.
- **Lost** — a boundary erased by matched value or blur.

Hard edges advance and catch the eye first; soft edges recede and build depth.

**One hardest edge, at the focal point.** Grade every other edge's softness
relative to it — a continuous hierarchy from hard through soft to lost, never a
binary. Soften any edge that does not need to be sharp, but do not soften
everything uniformly.

**Deliberately lose two or three edges** per form where similar values meet. Lost
edges fuse small adjacent shapes into one larger read, let the eye travel through
non-focal areas instead of being fenced by outline everywhere, and concentrate
contrast where it belongs. Defaulting to hard edges everywhere is thinking in
line rather than in form, and is the coloring-book look.

## The primitives, and what each teaches

- **Box** — plane-to-value mapping with zero curvature. Hard edges only; no
  terminator concept needed. Learn this first.
- **Cylinder** — one axis of curvature. The terminator runs **straight, parallel
  to the axis**, curved only around the cross-section. Transfers directly to
  limbs and fingers.
- **Sphere** — curvature in every direction at once. The terminator curves on two
  axes, and **value steps compress near it**: values change slowly near the
  brightest light and darken rapidly approaching the terminator. Do not
  distribute steps evenly across the lit face — bunch them near the terminator.
- **Cone** — a straight axis-following terminator like the cylinder, converging
  and sharpening toward the apex.

**Terminator ≠ core shadow.** The terminator is fixed by the primary light. The
core shadow sits a little past it, where the surface receives least *combined*
direct and bounced light — so it shifts if the reflected light shifts, even when
the terminator does not.
