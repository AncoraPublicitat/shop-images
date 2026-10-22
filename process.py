"""Removes the background from supplier photos and puts them on white.

Reads <supplier>_urls.txt (one photo URL per line), saves each cleaned photo
under <supplier>/<same path as the original>, skips photos already done, and
keeps <supplier>/index.txt with every finished original URL.
Usage: python3 process.py musai SHARD SHARDS
"""
import io, os, subprocess, sys, time, urllib.request
from PIL import Image
from rembg import remove, new_session

PREFIXES = {"musai": "https://static.musaibrand.com/images/models/"}
supplier, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
prefix = PREFIXES[supplier]
urls = [l.strip() for l in open(f"{supplier}_urls.txt") if l.strip()]
mine = [u for i, u in enumerate(urls) if i % shards == shard]
session = new_session("isnet-general-use")


def out_path(url):
    return os.path.join(supplier, url[len(prefix):])


def save_progress(message):
    subprocess.run(["git", "add", supplier], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return
    subprocess.run(["git", "commit", "-qm", message], check=True)
    for attempt in range(10):
        subprocess.run(["git", "pull", "-q", "--rebase", "-X", "theirs"])
        if subprocess.run(["git", "push", "-q"]).returncode == 0:
            return
        time.sleep(5 + attempt * 3)
    sys.exit("Could not push")


done_since_save = 0
for n, url in enumerate(mine, 1):
    path = out_path(url)
    if os.path.exists(path):
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://musaibrand.com/"})
        src = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=60).read())).convert("RGB")
        cut = remove(src, session=session, alpha_matting=True)
        white = Image.new("RGB", cut.size, (255, 255, 255))
        white.paste(cut, mask=cut.split()[3])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        white.save(path, quality=88, optimize=True)
        done_since_save += 1
        print(f"[{n}/{len(mine)}] {path}", flush=True)
    except Exception as error:
        print(f"[{n}/{len(mine)}] FAILED {url}: {error}", flush=True)
    if done_since_save >= 40:
        save_progress(f"{supplier}: photos (part {shard + 1}/{shards})")
        done_since_save = 0
save_progress(f"{supplier}: photos (part {shard + 1}/{shards})")
