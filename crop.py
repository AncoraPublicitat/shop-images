"""Crop a banner image. Usage: python3 crop.py URL x0 y0 x1 y1 out.jpg  (box in pixels of the source)."""
import io, sys, urllib.request
from PIL import Image
url, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
img = Image.open(io.BytesIO(urllib.request.urlopen(req).read())).convert("RGB")
print("source size", img.size)
import os; os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
img.crop((x0, y0, x1, y1)).save(out, quality=92)
print("saved", out, Image.open(out).size)
