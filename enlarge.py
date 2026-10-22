"""Trims the empty white border around each product and re-centres it on a
3:4 portrait canvas, so the product fills about 90% of the frame.
Reads <supplier>/..., writes <supplier>_v2/... (new paths, so Shopify
downloads them as new images) and <supplier>_v2/index.txt."""
import os, sys
from PIL import Image, ImageChops

supplier = sys.argv[1]
FILL, RATIO, SIZE = 0.90, (3, 4), (900, 1200)
src_root, dst_root = supplier, supplier + "_v2"
done = 0
for folder, _, files in os.walk(src_root):
    for name in files:
        if not name.lower().endswith(".jpg"):
            continue
        src = os.path.join(folder, name)
        dst = os.path.join(dst_root, os.path.relpath(src, src_root))
        if os.path.exists(dst):
            continue
        im = Image.open(src).convert("RGB")
        mask = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L")
        box = mask.point(lambda p: 255 if p > 18 else 0).getbbox()
        if box:
            obj = im.crop(box)
            w, h = obj.size
            cw = max(w / FILL, h / FILL * RATIO[0] / RATIO[1])
            ch = cw * RATIO[1] / RATIO[0]
            canvas = Image.new("RGB", (int(cw), int(ch)), (255, 255, 255))
            canvas.paste(obj, ((int(cw) - w) // 2, (int(ch) - h) // 2))
            im = canvas.resize(SIZE, Image.LANCZOS)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im.save(dst, quality=88, optimize=True)
        done += 1
print(f"{done} photos enlarged")
prefix = {"musai": "https://static.musaibrand.com/images/models/"}[supplier]
originals = [l.strip() for l in open(f"{supplier}_urls.txt") if l.strip()]
ready = [u for u in originals if os.path.exists(os.path.join(dst_root, u[len(prefix):]))]
open(os.path.join(dst_root, "index.txt"), "w").write("\n".join(ready) + "\n")
print(f"{len(ready)} of {len(originals)} in {dst_root}/index.txt")
