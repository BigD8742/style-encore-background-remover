# White Background Maker (Style Encore)

A phone-friendly web app that takes product photos, removes the background, and returns clean
white-background images in **square (1:1)** and **Instagram portrait (4:5)**, ready for Instagram and the
online store. It replaces Pixelcut in the store's photo workflow.

- **Live app:** https://bigd8742.github.io/style-encore-background-remover/
- **Repository:** https://github.com/BigD8742/style-encore-background-remover (public)
- **Hosting:** GitHub Pages from the `main` branch, root folder. Every push to `main` goes live in about 1–2 minutes.
- **Cost:** free. No server, no account, no per-photo fees. Photos never leave the phone.
- **Users:** store staff on iPhone (Safari, or installed on the Home Screen as "BG Maker").

---

## The workflow

Before: take photos → Pixelcut removes the background and puts it on white → make it Instagram square or
portrait → upload to the e-commerce site.

Now:
1. Open the app and tap **Choose photos** (any number).
2. Set **Keep** (Square / Portrait / Both), output size, margin and shadow.
3. Tap **Remove backgrounds**.
4. Per photo, as needed: **Touch up**, **Position**, or tap the square/portrait previews to pick versions.
5. Tap **Save selected**, then **Save Images** to put them in Photos, and upload as before.
6. Tap **I'm finished** (or **Start over** for another batch).

---

## Features

### Processing
| Feature | Details |
|---|---|
| Batch processing | Any number of photos, processed one after another with a progress bar and "Working… 3 of 8". |
| AI background removal | On the device, in the browser: `@imgly/background-removal` 1.7.0, `isnet_fp16` model. |
| Speed | Uses the phone's graphics chip (WebGPU) when available: about 1.5 s per photo, vs about 13 s on the regular processor (desktop measurement). Falls back automatically. |
| AI kept on the phone | `sw.js` (service worker) stores the AI files after the first download (about 90 MB). Measured: 8 photos in 8 s right after a reload, vs 78–101 s when re-downloading. |
| Download progress | "Getting the AI ready: 45% downloaded" in the status line and on the photo being worked on, so a slow connection doesn't look frozen. The AI starts downloading as soon as photos are picked. |
| Clean white background | Automatic clean-up of the AI result (details under "How it works"): faint haze removed; faint pixels kept only right next to the product; separate patches smaller than 5% of the product (streaks, smudges, spare hangers) wiped. Tuned so white clothes on white backgrounds stay whole. |

### Framing and output
| Feature | Details |
|---|---|
| Product framing | Crops tight to the product and centers it on white, like Pixelcut. |
| Square and portrait | Every photo gets a 1:1 and a 4:5 preview; tap to choose which to keep. |
| Keep: Square / Portrait / Both | Sets the choice for every photo at once; individual photos can still be changed. |
| Output size | Instagram (1080 wide), Website (2000 wide, default), Large (2400 wide). Portrait height = width × 1.25. |
| Space around product | Slider, 0–25% of the image width (default 8%). |
| Soft shadow | Optional switch: a soft oval studio shadow under the product. |
| File names | `<original name>-square.jpg`, `<original name>-portrait.jpg` (JPEG, quality 0.92). |

### Editing (per photo)
| Feature | Details |
|---|---|
| Touch up | Full screen. **Erase** removes leftover background; **Restore** paints back parts the AI cut off (the original shows faintly as a guide). Brush size, pinch-zoom (or mouse wheel), −/+/Fit, Undo/Redo (15 steps), Reset to the AI result. |
| Position | Like Pixelcut: drag the product to move it, pinch to resize, snaps to center with guide lines; Smaller / Bigger / Center / Reset. Square and portrait are positioned separately, and positioning a shape also selects it. A placed product stays exactly where it was put, even after a Touch up or a margin change. |

### Saving and leaving
| Feature | Details |
|---|---|
| Saving | iPhone share sheet (Save Images → Photos); on computers the files download. Web pages can't save to Photos silently, so iOS always needs that one tap. |
| Saved / Not saved | Each photo shows "Saved ✓" or "Not saved: Portrait", tracked per shape. The bottom button saves only new or changed shapes ("Save changes (2)"), so nothing is saved twice. "Save" on a photo saves all its chosen shapes. |
| Leaving safely | Start over and I'm finished list exactly which photos aren't saved, with **Save them now** (saves just those, then continues), **Leave without saving**, or **Go back**. |
| I'm finished | Clears everything and shows an "All done" screen explaining how to leave (swipe up). Web pages can't send an iPhone to its Home Screen themselves. |

### Look and install
| Feature | Details |
|---|---|
| Branding | Style Encore logo in a white header with a red and gold stripe. The logo's red (#C62034) and gold (#D2B887) run through the app, on a warm cream background. Numbered steps 1–4, big buttons, and the main action pinned to the bottom of the screen. |
| Home Screen app | `manifest.webmanifest` + `icons/app-icon-*.png`. Added to the Home Screen, it opens full screen as "BG Maker". The icon is solid red with the logo in white and gold, so it stays bright in iPhone Dark icon mode. |

---

## How it works (technical)

The app is **`index.html`** (HTML + CSS + one JavaScript module), plus **`sw.js`** (stores the AI files),
`manifest.webmanifest` and `icons/`. There is no build step and nothing to install. The background-removal
library loads from jsDelivr, and its model files from staticimgly.com.

### Pipeline for each photo
1. **`prepareInput`**: shrinks the photo so its long side is at most 2048 px (`PROCESS_SIDE`) to keep iPhones from running out of memory.
2. **`cutout`**: runs the AI and gets a PNG with a transparent background.
   - Uses `isnet_fp16` on `device: "gpu"` when `navigator.gpu` exists.
   - If that fails it switches to `cpu`, and only then falls back to `isnet_quint8`.
   - `?cpu` in the URL forces the processor (for troubleshooting).
   - `preload()` runs when photos are added, and `onAiProgress` adds up the download progress across files.
3. **`findProduct(img, clean=true)`**:
   - **Clean** (in this order):
     - Remap alpha: ≤ 64 → 0, ≥ 208 → 255, linear in between.
     - `keepFaintOnlyNearSolid`: pixels under half solid are wiped unless they're within 0.6% of the image size of product that is at least half solid.
     - `removeStrays`: separate patches (8-connected, alpha ≥ 24) under 5% of the largest are wiped.
   - **Box:** rows and columns with a real amount of solid pixels (≥ 0.4% having alpha ≥ 128), plus 1% padding, so stray specks don't pull the framing off-center.
4. **`setCutout`**: stores the cutout PNG and box, keeps manual positions in place if the box changed (`keepPlace`), builds a small (720 px) crop for fast previews, and redraws the previews.
5. **`drawFramed`**: product box centered on white with the margin (and the shadow if on), then the photo's manual position `item.pos[shape] = { k, x, y }`.
   - k = size relative to the auto-fit; x/y = shift as a fraction of the frame's width/height.
   - Used for the previews, the Position screen and the full-size output, so all three always match.
6. **Saving (`saveJobs` → `renderFull` → `shareOrDownload`)**: jobs are `[photo, shape]` pairs. Full-size JPEGs are rendered only when saving, cached per settings and position.
   - Safari only allows the share sheet right after a tap. If rendering takes too long, the button pulses "Tap to save N", and the next tap shares the ready files.

### Per-photo data in memory
| Field | Holds |
|---|---|
| `input` | The JPEG sent to the AI (used by Restore). |
| `aiCut` | The cleaned AI cutout (used by Reset). |
| `cut` | The current cutout, after any touch-up. |
| `box` | The product's position inside the cutout. |
| `small` | A small crop of the product for fast previews. |
| `chosen` | The shapes to keep. |
| `pos` | The manual position per shape. |
| `savedV` | The shapes saved since they last changed. |
| `cache` | Rendered files. |

### Touch-up editor
- It keeps a *mask* canvas the size of `input`. Erase = `destination-out` brush on the mask; Restore = solid brush on the mask.
- The displayed product = the original photo kept only where the mask is solid (`source-in`).
- Undo stores only the mask's alpha channel (1 byte per pixel). Done → builds the new cutout, re-finds the box (no cleaning), and refreshes the previews.

### Position screen
- Draws the frame from `small` with `drawFramed`. One pointer drags; two pointers pinch (size and move); the mouse wheel zooms.
- It snaps to center within 1.5% and shows guide lines while dragging.

---

## Key decisions and why

- **Standard AI model (`isnet_fp16`), not the small one.** `isnet_quint8` left about 19% of a plain backdrop partly visible; `isnet_fp16` left 0%. The cost is a bigger download (about 90 MB vs about 40 MB), now stored on the phone.
- **Graphics chip first.** It's 8–9× faster with identical cutouts, and falls back automatically on older phones.
- **Service worker for the AI files only.** The browser's normal cache dropped the 90 MB of files between visits. The app page itself is never cached by the service worker, so updates arrive on a normal reload.
- **Clean-up thresholds came from measurements.** White-on-white garments came back only 60–75% solid, so "solid" is set at 50%: an 80% line punched holes in a white top. Streaks were mostly under 25% solid. A spare hanger was 3.3% of the product's size, so the stray-patch cut-off is 5%.
- **Positions survive box and margin changes.** `keepPlace` recomputes `{k, x, y}` so the product's pixels stay where they were, because Touch up and the margin slider used to move placed products.
- **Save tracking per shape**, so changing only a portrait doesn't force re-saving the square, and nothing is saved twice.
- **All on the device, in one HTML file.** No server costs, no uploads, private, and easy to host and change.
- **Previews from a small crop, full size only when saving**, to keep memory low with big batches on an iPhone.

---

## Test results (November 2026)

- **First stock photo test** (8 hard Unsplash photos):
  - Excellent: bags (black on white sheets, white purse in a dark shop).
  - Good: white top, floral dress, green dress on a rack.
  - Lace dress: the AI drops the **sheer tulle skirt**, and Restore fixes it.
- **Graphics chip:** 4 photos in 6 s with the same quality as the processor.
- **Stored AI:** 8 photos in 8 s after a reload (78–101 s when re-downloading).
- **Clean-up:** removes the spare hanger and the specks under the green dress. The white top and white shirts stay whole, and bags, lace and florals are unchanged.
- **Position:** the preview and the 2000×2000 saved file match. After erasing a bag's handles, the bag body's left, right and bottom edges stayed at the same pixels, and moving the margin slider didn't move a placed product.
- **Saving:** after saving everything and then repositioning two portraits, the badges showed exactly those two, the button read "Save changes (2)", and "Save them now" saved exactly those 2 files, then finished.
- Layout checked at 375 px wide throughout.
- **Store testing on iPhone:**
  - "Working great."
  - Feedback that led to the redesign: friendlier look, bigger buttons, more color, a clean exit, more speed, and drag to reposition.
  - Later feedback: unclear which photos were unsaved, a placed product moved after saving, and dirty streaks in the white. All three are fixed above.

### Known limitations

- Sheer fabric (tulle, chiffon, mesh) is often removed by the AI. Use **Restore**.
- A smudge that is solid *and* touching the product (for example, a dark floor shadow right under a hem) isn't removed automatically. Use **Erase**.
- A small separate piece that really belongs to the product (under 5% of its size, for example a detached tag) can be wiped by the clean-up. Use **Restore**.
- The first run (or after iOS clears website data) downloads about 90 MB. Use Wi-Fi, keep the app open and the screen on during a batch.
- Restore and Erase are plain round brushes. There's no "smart edge" brush yet.
- The clean-up is tuned on stock photos; the store's own photos (lighting, backdrop) haven't been used for tuning yet.

---

## Ideas for later upgrades

- Tune the clean-up on the store's own photos (ask for examples that showed streaks).
- A "smart" Restore/Erase brush that snaps to edges.
- More shapes (for example, 9:16 stories, or whatever size the online store recommends).
- A background color other than white, and straightening a tilted product.
- Uploading straight to the online store (for example, Shopify) instead of saving to Photos.
- Full offline use (cache the app page too, with an update prompt).

---

## Version history

| Date | Change |
|---|---|
| 2026-11-23 | First version: background removal on white, square option, batch. Published on GitHub Pages. |
| 2026-11-23 | Square + portrait picker, product framing, margin, Instagram/website sizes; switched to `isnet_fp16` (haze fix). |
| 2026-11-23 | Touch-up editor (erase/restore, zoom, undo) and soft shadow. Printable QR sheet. |
| 2026-11-23 | Redesign (numbered steps, big buttons, bottom bar), Position screen, graphics-chip speed-up, Home Screen app, Start over / I'm finished. |
| 2026-11-23 | Style Encore branding (logo header, red and gold); bright red app icon for Dark icon mode. |
| 2026-11-23 | Auto clean-up of streaks and stray patches, Saved/Not saved badges, save-only-changes, safe exit screen, positions kept after Touch up and margin changes, AI stored on the phone, download progress. |

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
GitHub Pages rebuilds automatically; check the live link 1–2 minutes later. On the iPhone, close and
reopen the app (or reload Safari) to get the update. Deleting and re-adding the Home Screen icon is only
needed when the icon itself changes.

### Files
| File | Purpose |
|---|---|
| `index.html` | The whole app. |
| `sw.js` | Stores the AI files on the phone. Bump `CACHE` if the imgly version changes. |
| `manifest.webmanifest` | Home Screen app settings. |
| `icons/logo.png` | Header logo. |
| `icons/app-icon-*.png` | Home Screen icons. |
| `tools/make_icons.py` | Rebuilds the logo crop and icons from the Style Encore logo (`pip install pillow`). If the icon changes, rename the files so iPhones don't show a cached icon. |
| `tools/make_qr_sheet.py` | Rebuilds the printable QR sheet (`pip install segno`). The QR code points to the permanent URL, so printed copies keep working. |
| `CLAUDE.md` | Working notes for Claude. |

`QR-code-to-print.pdf` and `app-qr-code.png` are kept locally and are not committed.
