#!/usr/bin/env python3
"""Cut one object out of the subject at a magnification it can be drawn at.

    python3 crop.py subject.png x,y,w,h SCALE parts/NAME/subject.png

The crop is the object's box plus a margin, scaled up by SCALE, so that the
smallest feature you will draw is at least ~40px on the page. The command
prints the origin and scale the scene script needs to put the part back:

    place(load("parts/NAME/ops.json"), origin=(x, y), scale=SCALE)

Pick SCALE from the feature, not the box: an eye 12px tall in the panel wants
SCALE 4; a wheel 370px tall wants 1. A part drawn at the wrong scale is a part
you could not see while you drew it.
"""
import os
import sys

from PIL import Image

subject, box, scale, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
x, y, w, h = (int(part) for part in box.split(","))
margin = max(8, round(0.15 * max(w, h)))
image = Image.open(subject).convert("RGB")
x0, y0 = max(0, x - margin), max(0, y - margin)
x1, y1 = min(image.width, x + w + margin), min(image.height, y + h + margin)
crop = image.crop((x0, y0, x1, y1))
crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
crop.save(out)
print(f"{out}: {crop.width}x{crop.height}  origin=({x0}, {y0})  scale={scale:g}")
print(f'place(load("{os.path.dirname(out)}/ops.json"), origin=({x0}, {y0}), scale={scale:g})')
