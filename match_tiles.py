"""Recreate small cropped tiles at full resolution.
For each tile in tiles_src/, find where it sits inside its full-size original (multi-scale
template matching) and cut that same area out of the original. Output: tiles_hd/<name>.jpg"""
import io, os, urllib.request
import cv2, numpy as np

B = "https://d8j0ntlcm91z4.cloudfront.net/user_3GWbTxF6tkpedliNQazaF3xHNVM/hf_20261023_"
CANDIDATES = {
    "1-d97d6feb": ["091048_ddafd738-f034-46d4-8823-9fc1d3e4c396", "084144_655b50f8-54ae-4853-9cf3-505970f92e5c"],
    "2-526e13c0": ["112049_3d0a37d6-8852-4e83-8bae-ffd5a3d13ab2"],
    "3-056f2aa2": ["112050_08356c35-1de3-4235-94a0-51d9a4a4b673"],
    "4-da002303": ["112049_1f14b721-8bda-4193-8111-54d748c78905"],
    "5-95c3829b": ["112049_2cdf6ec8-5f06-4942-bbab-6618b7750766"],
    "6-ad4095ad": ["084142_56784c66-650b-4924-8dd0-8b58c5b2db8e"],
    "7-e2d7717e": ["112050_682aa2e1-822f-488e-9772-e0798fcc9f02"],
    "8-cb422528": ["112049_3d0a37d6-8852-4e83-8bae-ffd5a3d13ab2", "111034_17c3571a-b60e-44b8-bb73-25724bd36b1e",
                   "111251_08db1493-168b-4c18-bd52-d930afa95337"],
}
cache = {}
def fetch(key):
    if key not in cache:
        req = urllib.request.Request(B + key + ".png", headers={"User-Agent": "Mozilla/5.0"})
        data = np.frombuffer(urllib.request.urlopen(req, timeout=60).read(), np.uint8)
        cache[key] = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return cache[key]

def best_match(tile, orig):
    t = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY); o = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    th, tw = t.shape; oh, ow = o.shape
    lo = max(tw / ow, th / oh)              # tile can't be bigger than the whole original
    best = (-1, None)
    def try_scale(f):
        nonlocal best
        small = cv2.resize(o, (max(tw, round(ow * f)), max(th, round(oh * f))), interpolation=cv2.INTER_AREA)
        if small.shape[0] < th or small.shape[1] < tw: return
        r = cv2.matchTemplate(small, t, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(r)
        if score > best[0]: best = (score, (f, loc))
    for f in np.geomspace(lo, 1.0, 50): try_scale(f)
    f0 = best[1][0]
    for f in np.linspace(f0 * 0.96, min(1.0, f0 * 1.04), 21): try_scale(f)
    score, (f, (x, y)) = best
    return score, (round(x / f), round(y / f), round((x + tw) / f), round((y + th) / f))

os.makedirs("tiles_hd", exist_ok=True)
log = []
for name, keys in CANDIDATES.items():
    tile = cv2.imread(f"tiles_src/{name}.jpg")
    results = []
    for k in keys:
        try:
            orig = fetch(k)
            s, box = best_match(tile, orig)
            results.append((s, k, box)); log.append(f"{name} vs {k}: score {s:.3f} box {box} orig {orig.shape[1]}x{orig.shape[0]}")
        except Exception as e:
            log.append(f"{name} vs {k}: ERROR {e}")
    if not results: continue
    s, k, (x0, y0, x1, y1) = max(results)
    orig = fetch(k)
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(orig.shape[1], x1), min(orig.shape[0], y1)
    crop = orig[y0:y1, x0:x1]
    cv2.imwrite(f"tiles_hd/{name}.jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 93])
    log.append(f"==> {name}: using {k} score {s:.3f}, saved {crop.shape[1]}x{crop.shape[0]}")
open("tiles_log.txt", "w").write("\n".join(log) + "\n")
print("\n".join(log))
