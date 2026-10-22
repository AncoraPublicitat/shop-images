# shop-images

Product photos with white backgrounds for the Ancora shop.

The dark studio backgrounds of supplier photos are removed with the free
open-source AI tool [rembg](https://github.com/danielgatis/rembg) and replaced
with white. Everything runs in GitHub Actions ("Remove backgrounds" workflow).

- `musai_urls.txt` – original Musai photo URLs to process
- `musai/` – the cleaned photos, same folder structure as Musai's
- `musai/index.txt` – originals that have a cleaned version (read by the feed builder)
