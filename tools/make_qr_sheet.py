import sys
import segno

URL = "https://bigd8742.github.io/style-encore-background-remover/"
out = sys.argv[1]

svg = segno.make(URL, error="m").svg_inline(scale=1, border=2, dark="#000", omitsize=True)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>White Background Maker - QR code</title>
<style>
  @page {{ size: letter; margin: 0.6in; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: "Segoe UI", -apple-system, Roboto, Arial, sans-serif; color: #1d1d1f; }}
  .sheet {{ text-align: center; padding-top: 0.2in; }}
  h1 {{ font-size: 30pt; margin: 0 0 4pt; }}
  .sub {{ font-size: 14pt; color: #444; margin: 0 0 22pt; }}
  .qr svg {{ width: 4.6in; height: 4.6in; display: block; margin: 0 auto; }}
  .url {{ font-size: 10.5pt; color: #444; margin: 12pt 0 26pt; word-break: break-all; }}
  ol {{ text-align: left; display: inline-block; font-size: 13pt; line-height: 1.55; margin: 0; padding-left: 1.3em; max-width: 6in; }}
  li {{ margin-bottom: 4pt; }}
  .tip {{ font-size: 11pt; color: #555; margin-top: 18pt; }}
  @media screen {{ body {{ background: #e9e9ee; padding: 24px; }} .sheet {{ background: #fff; width: 8.5in; min-height: 11in; margin: 0 auto; padding: 0.8in 0.6in; box-shadow: 0 2px 12px rgba(0,0,0,.15); }} }}
</style>
</head>
<body>
<div class="sheet">
  <h1>White Background Maker</h1>
  <p class="sub">Scan with your iPhone camera to open the app</p>
  <div class="qr">{svg}</div>
  <p class="url">{URL}</p>
  <ol>
    <li>Open the <b>Camera</b> app and point it at the code. Tap the link that appears.</li>
    <li>In Safari, tap <b>Share</b> &rarr; <b>Add to Home Screen</b> so it opens like an app.</li>
    <li>The first time, use <b>Wi-Fi</b>. The app downloads its AI once (about 90 MB).</li>
    <li>Choose photos, tap <b>Remove backgrounds</b>, then <b>Save selected</b> &rarr; <b>Save Images</b>.</li>
  </ol>
  <p class="tip">Keep the screen on and Safari open while a batch is working.</p>
</div>
</body>
</html>
"""
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", out)
