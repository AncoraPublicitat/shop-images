"""Writes <supplier>/index.txt listing the original URLs whose white version exists."""
import os, sys
PREFIXES = {"musai": "https://static.musaibrand.com/images/models/"}
supplier = sys.argv[1]
urls = [l.strip() for l in open(f"{supplier}_urls.txt") if l.strip()]
done = [u for u in urls if os.path.exists(os.path.join(supplier, u[len(PREFIXES[supplier]):]))]
open(os.path.join(supplier, "index.txt"), "w").write("\n".join(done) + "\n")
print(f"{len(done)} of {len(urls)} photos done")
