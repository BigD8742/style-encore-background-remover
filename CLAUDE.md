# Context for Claude: White Background Maker (Style Encore)

Read `README.md` first. It has the features, the pipeline, key decisions with their measurements, test
results, known limitations, upgrade ideas and the version history. Keep both files current after every change.

## Who uses it and how
- The owner (not a developer) relays feedback from a staff member who does the store's product photos on an
  **iPhone** (Safari, and installed on the Home Screen as "BG Maker"). She is detail-oriented: she notices
  smudges, things moving, and unclear states. The app replaced **Pixelcut**: remove background → white →
  square or Instagram portrait (4:5) → upload to the online store.
- Explain changes in plain, non-technical language. Phone-first: every UI change must work at 375 px wide
  with touch, with labels on one line.
- Match what Pixelcut offers where sensible; the owner asked for Pixelcut parity.
- Be upfront about platform limits instead of faking them: a web page can't save to Photos without the
  Save Images tap, can't send the phone to its Home Screen, and iPhones keep an old Home Screen icon until it's re-added.
- After publishing, tell the owner how she gets the update (close and reopen the app; re-add only if the icon changed).

## Project facts
- App: `index.html` (one file, no build step) + `sw.js` + `manifest.webmanifest` + `icons/`.
  AI: `@imgly/background-removal@1.7.0` from jsDelivr, model `isnet_fp16`, device `gpu` with CPU fallback.
  Don't switch to `isnet_quint8`, which leaves background haze.
- Live: https://bigd8742.github.io/style-encore-background-remover/ (GitHub Pages, `main` branch, root).
  Deploying = commit and push to `main`, then confirm it's live by curling the URL for a string from the change.
- Repo: `BigD8742/style-encore-background-remover` (public). The `gh` CLI is logged in as BigD8742.
- Git identity is set **locally in this repo** to GitHub's no-reply address. Never put the owner's personal
  email in commits or files. The repo is public, and the Style Encore logo is in it (the owner's own brand).
- `.gitignore` keeps `.claude/`, `app-qr-code.png` and `QR-code-to-print.pdf` out of the repo.
- The original logo file isn't in the repo; `icons/logo.png` (a crop on white) works as the source for `tools/make_icons.py`.

## Rules that protect earlier fixes
- **Clean-up** (`findProduct` → `removeBackdropChunks` → `keepFaintOnlyNearSolid` → `removeStrays`): after any change, re-test
  - the store's real photos in `her-photos/` (gitignored, never commit): IMG_9023 front and IMG_9026 back (no table pieces), IMG_9024 label close-up; `pixelcut_*.JPG` are the target look;
  - a white garment on white: Unsplash photo-1578747522731-9e5a179b02f7 (no holes; it's only 60–75% solid);
  - a spare hanger: photo-1519554318711-aaf73ece6ff9 (should disappear);
  - the green dress on a rack: photo-1724891793770-49b41a5c9731 (no specks);
  - the lace dress: photo-1591221662157-6f62de5508eb;
  - bags: photo-1614179689702-355944cd0918 and photo-1682745230951-8a5aa9a474a0.
  - the lace dress hanger must stay (thin backdrop-colored parts are protected unless the backdrop is near-white).
  Touch-up results are never auto-cleaned (`findProduct(out, false)`).
- **Tap area** limits were measured on her photos: Restore seed 100 / step 60, Erase seed 50 / step 28 (× Range factor). Erase must never spill from the white table into light jeans.
- BiRefNet was tried and doesn't run in the browser here (WebGPU errors, out of memory on CPU). Don't retry without a new reason. `her-photos/compare.html` is the side-by-side test page.
- **Saving** is tracked per shape in `item.savedV`. Anything that changes how a shape looks must remove that
  shape from `savedV`. Margin, shadow, size and Touch up clear all shapes; Position clears the shapes it changed.
- **Positions** (`item.pos[shape] = {k, x, y}`) are relative to the auto-fit. Anything that changes the box or
  the margin must call `keepPlace` so placed products don't move.
- **`drawFramed`** is the single drawing path for previews, the Position screen and saved files. Keep it that way so they always match.
- **`sw.js`** caches only the AI hosts (staticimgly.com, cdn.jsdelivr.net), never the app page. Bump `CACHE` if the imgly version changes.
- **Icons:** if they change, use new file names (and update `index.html` and the manifest) so iPhones don't show a cached icon.
  Keep the solid-color background, because white-background icons turn dull in iPhone Dark icon mode.

## Look and feel
- Style Encore branding: logo (`icons/logo.png`) in a white header with a red and gold stripe; warm cream background.
- Colors: brand red `#C62034` (`--brand`), gold `#D2B887` (`--gold`; `--gold-dark` for text).
  - Green = save/selected/"Saved ✓".
  - Coral = start over, erase, "Not saved".
  - Red-soft = Position; gold-soft = Touch up.
- Big buttons (46–58 px); the main action sits in the bottom bar.

## Testing changes
- Serve locally with the `.claude/launch.json` preview `app` (`python -m http.server 8765`). Test at the mobile viewport (375×812).
- Batch test: build `File` objects in the page and set them on `#file` with a `DataTransfer`, then click `#start`.
  Fetch real photos in the page from `images.unsplash.com/photo-<id>?w=1800&q=85&fm=jpg` (free license, CORS OK). Don't commit test photos.
- Stub `navigator.share` / `navigator.canShare` to capture saved files, `window.confirm` for prompts, and
  `window.close` when testing "I'm finished" (it really closes script-opened tabs).
- The editors use pointer events. Synthetic touches need distinct `pointerId`s; `setPointerCapture` is wrapped in try/catch.
- The first load (or after the cache is cleared) downloads about 90 MB and can take 1–2 minutes. Measure speed after a reload, when `sw.js` is serving the files.
- Keep iPhone memory in mind: photos are processed at a max of 2048 px; full-size renders happen only on save.
- Contact sheet for reviewing many results: overlay a grid of `.thumb` originals next to each `.variant canvas` preview.
