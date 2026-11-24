# Context for Claude: White Background Maker

Read `README.md` first. It has the features, the pipeline, key decisions, test results, known limitations,
and the upgrade ideas list.

## Who uses it and how
- A retail store owner (not a developer) and staff, using **iPhone Safari**. The app replaced Pixelcut in the
  photo workflow: remove background → white → square or Instagram portrait (4:5) → upload to the online store.
- Explain changes in plain, non-technical language. Phone-first: every UI change must work at 375 px wide
  with touch.
- When adding features, match what Pixelcut offers where sensible. The owner asked for Pixelcut parity.

## Project facts
- The whole app is one file: `index.html`. No build step, no package manager. The AI library loads from the CDN
  (`@imgly/background-removal@1.7.0`, model `isnet_fp16`; don't switch back to `isnet_quint8`, which leaves background haze).
- Live: https://bigd8742.github.io/style-encore-background-remover/ (GitHub Pages, `main` branch, root).
  Deploying = commit and push to `main`. Confirm it's live by curling the URL for a string from the change.
- Repo: `BigD8742/style-encore-background-remover` (public). The `gh` CLI is logged in as BigD8742.
- Git identity is set **locally in this repo** to GitHub's no-reply address. Never put the owner's personal
  email in commits or files. The repo is public.
- `.gitignore` keeps `.claude/`, `app-qr-code.png` and `QR-code-to-print.pdf` out of the repo.
- `tools/make_qr_sheet.py` rebuilds the printable QR sheet (`pip install segno`). The URL never changes, so
  existing printed QR codes keep working.

## Testing changes
- Serve locally: the `.claude/launch.json` preview `app` (`python -m http.server 8765`).
- Batch test: build `File` objects in the page and set them on `#file` with a `DataTransfer`, then click `#start`.
  Real photos can be fetched in the page from `images.unsplash.com/photo-<id>?w=1800&fm=jpg` (free license, CORS OK).
  Don't commit test photos.
- The first run downloads about 90 MB. After that, about 13 s per photo on desktop.
- `sw.js` caches the AI files (staticimgly.com, cdn.jsdelivr.net). If the imgly version in the import changes, bump `CACHE` in sw.js. Test speed after a reload, not just on first load.
- Clean-up changes: always re-test a white garment on a white background (Unsplash photo-1578747522731-9e5a179b02f7) for holes, plus a photo with a spare hanger (photo-1519554318711-aaf73ece6ff9).
- Saving is tracked per shape (`item.savedV`). Anything that changes how a shape looks must clear it from `savedV`.
- The AI runs on the graphics chip (`device: "gpu"`) when available, with CPU fallback; `?cpu` in the URL forces the CPU. Check both paths after AI changes.
- `window.close()` in "I'm finished" really closes script-opened test tabs; stub it when testing that flow.
- Look and feel: Style Encore branding. The logo (`icons/logo.png`) sits in a white header with a red and gold stripe. Brand red `#C62034` (`--brand`), gold `#D2B887` (`--gold`, darker `--gold-dark` for text), warm cream background. Green = save/selected, coral = start over/erase, red-soft = Position, gold-soft = Touch up. Keep buttons big (46–58 px), labels on one line at 375 px, and the main action in the bottom bar.
- Icons (`icons/app-icon-*.png`: solid red with white and gold logo, so they stay bright in iPhone Dark icon mode) are rebuilt with `python tools/make_icons.py <logo on white>` (`icons/logo.png` works as the source). If they change, rename the files so iPhones do not show a cached old icon.
- The Touch up and Position editors use pointer events. Synthetic touches need distinct `pointerId`s; `setPointerCapture` is wrapped in try/catch.
- Check memory-heavy changes with iPhone limits in mind (photos are processed at a max of 2048 px; full-size renders only on save).
