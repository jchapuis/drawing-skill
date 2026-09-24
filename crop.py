#!/usr/bin/env python3
"""Cut one object's measuring crop out of the working-resolution subject.

    python3 crop.py subject.png x,y,w,h meas/NAME.png

The crop is the object's box plus a margin, at 1:1. It is never rescaled: the
subject is already at working resolution, and a rescaled crop puts a second
coordinate space between the measurement and `draw.py`. It prints the offset
to hand to `trace.py`, so the object's regions come back in panel coordinates:

    python3 trace.py meas/NAME.png palette.json --offset X,Y --out meas/NAME.json

The crop is for measuring and for looking. Nothing is drawn in it.
"""
import os
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

subject, box, out = sys.argv[1], sys.argv[2], sys.argv[3]
x, y, w, h = (int(part) for part in box.split(","))
margin = max(8, round(0.15 * max(w, h)))
image = Image.open(subject).convert("RGB")
x0, y0 = max(0, x - margin), max(0, y - margin)
x1, y1 = min(image.width, x + w + margin), min(image.height, y + h + margin)
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
image.crop((x0, y0, x1, y1)).save(out)
print(f"{out}: {x1 - x0}x{y1 - y0}  offset={x0},{y0}")
print(f"python3 trace.py {out} palette.json --offset {x0},{y0} "
      f"--out {os.path.splitext(out)[0]}.json")
