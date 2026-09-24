#!/usr/bin/env python3
"""Cut one object's measuring crop out of the working-resolution subject.

    python3 crop.py subject.png x,y,w,h meas/NAME.png

The crop is the object's box plus a margin, at 1:1. It is never rescaled: the
subject is already at working resolution, and a rescaled crop puts a second
coordinate space between the measurement and `draw.py`.

**The crop's corner is not your box's corner**: the margin moves it up and left
by `max(8, 0.15 * max(w, h))`. Passing the box corner as the offset put every
traced region of one panel 8px off, with nothing to say so. So the corner is
written INTO the PNG, and `trace.py` reads it back by itself:

    python3 trace.py meas/NAME.png palette.json --out meas/NAME.json

comes back in panel coordinates with no `--offset` at all, and an `--offset`
that disagrees with the one in the file is refused.

The crop is for measuring and for looking. Nothing is drawn in it.
"""
import os
import sys

from PIL import Image
from PIL.PngImagePlugin import PngInfo

Image.MAX_IMAGE_PIXELS = None

if len(sys.argv) != 4 or not sys.argv[3].lower().endswith(".png"):
    sys.exit("usage: crop.py subject.png x,y,w,h meas/NAME.png  (the crop must be a PNG: "
             "its panel offset is stored in it)")
subject, box, out = sys.argv[1], sys.argv[2], sys.argv[3]
x, y, w, h = (int(part) for part in box.split(","))
margin = max(8, round(0.15 * max(w, h)))
image = Image.open(subject).convert("RGB")
x0, y0 = max(0, x - margin), max(0, y - margin)
x1, y1 = min(image.width, x + w + margin), min(image.height, y + h + margin)
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
info = PngInfo()
info.add_text("offset", f"{x0},{y0}")
image.crop((x0, y0, x1, y1)).save(out, pnginfo=info)
print(f"{out}: {x1 - x0}x{y1 - y0}, its corner at {x0},{y0} in the panel "
      f"(your box's corner {x},{y} less the {margin}px margin); stored in the PNG")
print(f"python3 trace.py {out} palette.json --out {os.path.splitext(out)[0]}.json")
