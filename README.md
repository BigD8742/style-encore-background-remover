# White Background Maker

A phone-friendly web app that takes product photos, removes the background, and returns clean
white-background images in **square (1:1)** and **Instagram portrait (4:5)**, ready for Instagram and the
online store. It replaces the Pixelcut steps in the store's photo workflow.

- **Live app:** https://bigd8742.github.io/style-encore-background-remover/
- **Repository:** https://github.com/BigD8742/style-encore-background-remover
- **Hosting:** GitHub Pages, served from the `main` branch, root folder. Every push to `main` goes live in about 1–2 minutes.
- **Cost:** free. No server, no account, no per-photo fees. Photos never leave the phone.

---

## The workflow it replaces

Before: take photos → Pixelcut removes the background and puts it on white → make it Instagram square or
portrait → upload to the e-commerce site.

Now: open the app → pick a batch of photos → **Remove backgrounds** → pick Square / Portrait / Both for each
photo → **Touch up** any bad edges → **Save selected** → Save Images to Photos → upload as before.

---

## Features

| Feature | Details |
|---|---|
| Batch processing | Pick any number of photos at once; they run one after another with a progress bar. |
| AI background removal | Runs on the device in the browser (`@imgly/background-removal` 1.7.0, `isnet_fp16` model). |
| Clean white background | Faint leftovers of the old background are wiped so the white stays pure. |
| Product framing | Crops tight to the product and centers it on white, like Pixelcut. |
| Space around product | Slider, 0–25% of the image width (default 8%). |
| Square and portrait | Every photo gets both a 1:1 and a 4:5 preview. Tap to choose which to keep. |
| Keep: Square / Portrait / Both | Sets the choice for every photo at once; individual photos can still be changed. |
| Output size | Instagram (1080 wide), Website (2000 wide, default), Large (2400 wide). Portrait height = width × 1.25. |
| Soft shadow | Optional switch: a soft oval studio shadow under the product. |
| Position (per photo) | Like Pixelcut: drag the product with one finger to move it, pinch to resize. Snaps to center with pink guide lines. Buttons: Smaller, Bigger, Center, Reset. Square and portrait are positioned separately; positioning a shape also selects it. |
| Speed | Uses the phone's graphics chip (WebGPU) when available: about 1.5 s per photo vs about 13 s on the regular processor (desktop test). Falls back automatically. The AI starts downloading as soon as photos are picked. |
| Home Screen app | Manifest + icon (`manifest.webmanifest`, `icons/`). Added to the Home Screen, it opens full screen like an app named "BG Maker", with the Style Encore logo as its icon. |
| Branding | Style Encore logo in the header; the app uses the logo's red (#C62034) and gold (#D2B887) on a warm cream background. |
| Start over / I'm finished | Start over clears the batch (warns if photos aren't saved). I'm finished clears everything and shows an "All done" screen explaining how to leave (swipe up). Web pages can't send an iPhone to its Home Screen themselves. |
| Touch up editor | Full screen. **Erase** removes leftover background; **Restore** paints back parts the AI cut off (the original shows faintly as a guide). Brush size, pinch-zoom (or mouse wheel), −/+/Fit buttons, Undo/Redo (15 steps), Reset to the AI result. |
| Saving | iPhone share sheet (Save Images → Photos). On computers it downloads the files. |
| File names | `<original name>-square.jpg`, `<original name>-portrait.jpg` (JPEG, quality 0.92). |

---

## How it works (technical)

Everything lives in one file: **`index.html`** (HTML + CSS + one JavaScript module). There is no build step
and no dependencies to install. The background-removal library loads from the jsDelivr CDN.

Processing pipeline for each photo:

1. **`prepareInput`**: shrinks the photo so its long side is at most 2048 px (`PROCESS_SIDE`) to keep iPhones from running out of memory.
2. **`cutout`**: runs the AI and gets a PNG with a transparent background. It uses `isnet_fp16` on `device: "gpu"` when `navigator.gpu` exists; if that fails it switches to `cpu`, and only then falls back to `isnet_quint8`. Add `?cpu` to the URL to force the processor (for troubleshooting). `preload()` is called when photos are added.
3. **`findProduct(img, clean=true)`**:
   - **Clean:** alpha ≤ 48 → 0, alpha ≥ 208 → 255, linear in between. This wipes haze but keeps soft edges.
   - **Box:** the product box covers rows and columns with a real amount of solid pixels (≥ 0.4% of the width/height having alpha ≥ 128), plus 1% padding, so stray specks don't pull the framing off-center.
4. **`setCutout`**: stores the cutout PNG and the box, builds a small (720 px) crop for fast previews, and draws the previews.
5. **`drawFramed`**: draws the product box centered on white with the chosen margin (and the shadow if on), then applies the photo's manual position `item.pos[shape] = { k, x, y }` (k = size relative to the auto-fit; x/y = shift as a fraction of frame width/height). It's used for previews, the Position screen and the full-size output, so all three always match.
6. **Saving (`renderFull` → `shareOrDownload`)**: renders full-size JPEGs only when saving, cached per settings.
   - Safari only allows the share sheet right after a tap. If rendering takes too long, the button turns green: "Tap again to save N", and the second tap shares the ready files.

Per-photo data kept in memory: `input` (the JPEG sent to the AI, used by Restore), `aiCut` (the AI's cutout, used
by Reset), `cut` (the current cutout, after any touch-up), `box`, `small`, `chosen`, and `cache`.

**Touch-up editor:** keeps a *mask* canvas the size of `input`.
- Erase = `destination-out` brush on the mask; Restore = solid brush on the mask.
- The displayed product = original photo kept only where the mask is solid (`source-in`).
- Undo stores only the mask's alpha channel (1 byte per pixel) to save memory.
- Done → builds the new cutout, re-finds the box (no cleaning), and refreshes the previews.

---

## Key decisions and why

- **Standard AI model (`isnet_fp16`), not the small one.** In testing, `isnet_quint8` left about 19% of a plain backdrop partly visible (gray-beige haze). `isnet_fp16` left 0%. The cost is a one-time download of about 90 MB instead of about 40 MB, cached by the browser after the first run.
- **All on the device.** No server costs, no uploads, works with any number of photos, and keeps photos private.
- **Single HTML file.** It's easy to host on GitHub Pages and easy to change.
- **The product box ignores sparse specks**, so the auto-centering isn't thrown off by tiny leftovers.
- **Previews from a small crop, full size only when saving**, to keep memory low with big batches on an iPhone.

---

## Test results (November 2026)

- Simulated product photos: clean cutouts, correct square/portrait framing, the right file count and sizes on save (for example, 1080×1080 and 1080×1350).
- 8 real stock photos (Unsplash, free license; tested locally, not stored in the repo):
  - **Excellent:** black handbag on white sheets, white purse in a dark shop.
  - **Good:** white top with necklace, floral dress, green dress on a cluttered rack.
  - **Needs touch-up:** black top in a wardrobe (an empty hanger beside it was kept; fix with Erase). Lace dress with a **sheer tulle skirt**: the AI itself drops sheer fabric. Fixed with Restore, and the framing updated correctly.
  - Speed: about 13 seconds per photo on a desktop computer. An iPhone is slower.
- The store owner tested on iPhone: "working great."
- Redesign (purple/berry theme, numbered steps, bottom action bar, Touch up / Position / Save per photo) checked at 375 px wide.
- Graphics chip: 4 real photos in 6 seconds with the same cutout quality as the processor. Position: the preview and the 2000×2000 saved file put the product in the same spot.
- Feedback that drove the redesign: the user wanted it friendlier, with more prominent buttons, more color, a clean way to exit, more speed, and Pixelcut-style drag to reposition.

### Known limitations

- Sheer fabric (tulle, chiffon, mesh) is often removed by the AI. Use **Restore**.
- Separate objects next to the product (spare hangers, tags, props) are kept. Use **Erase**.
- The first run needs about 90 MB (use Wi-Fi). Keep Safari open and the screen on during a batch.
- Restore and Erase are plain round brushes. There's no "smart edge" brush yet.

---

## Ideas for later upgrades

- A "smart" Restore/Erase brush that snaps to edges.
- An option to keep only the largest object (auto-removes spare hangers).
- More shapes (for example, 9:16 stories, or whatever size the online store recommends).
- A background color other than white, and straightening a tilted product.
- Uploading straight to the online store (for example, Shopify) instead of saving to Photos.
- Offline use (a service worker that caches the app and the AI model).

---

## Working on the app

### Run it locally
Opening `index.html` directly from disk won't load the module. Serve the folder instead:

```
python -m http.server 8765
```

Then open http://localhost:8765. (`.claude/launch.json` has this set up as the `app` preview.)

### Publish a change
```
git add index.html
git commit -m "Describe the change"
git push
```
GitHub Pages rebuilds automatically. Check the live link 1–2 minutes later.

### QR code for the iPhone
The QR code points to the permanent live URL, so it never needs changing after updates.
To regenerate the printable sheet, run `python tools/make_qr_sheet.py qr-sheet.html` (needs `pip install segno`),
then print it or save it as a PDF from any browser. `QR-code-to-print.pdf` and `app-qr-code.png` are kept
locally and are not committed.
