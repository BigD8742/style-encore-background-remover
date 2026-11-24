"""Build the header logo and Home Screen icons from the Style Encore logo. Needs Pillow.

Usage: python tools/make_icons.py <logo image with white background>
Writes:
  icons/logo.png              tight crop on white, for the header
  icons/app-icon-<size>.png   Home Screen icons: solid brand red, logo in white and gold

The icon has a solid colored background on purpose: iPhones in Dark icon mode turn white-background
icons into dull dark squares, while a full red icon stays bright.
If the icon changes again, change the file names (and the links in index.html / manifest.webmanifest)
so iPhones do not keep a cached old icon.
"""
import os
import sys
from PIL import Image, ImageChops

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)

RED = (0xC6, 0x20, 0x34)
GOLD = (0xD2, 0xB8, 0x87)
DEEP = (0x9C, 0x17, 0x28)

src = Image.open(sys.argv[1]).convert("RGB")
white = Image.new("RGB", src.size, (255, 255, 255))
mask = ImageChops.difference(src, white).convert("L").point(lambda v: 255 if v > 18 else 0)
logo = src.crop(mask.getbbox())

# header logo: tight crop, 900 px wide
w = 900
logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS).save(os.path.join(OUT, "logo.png"), optimize=True)

# Recolor the logo for a red background: red ink -> white, gold ink -> gold, white -> see-through.
# Each pixel is a blend of white and one ink color; work out which ink and how much.
def recolor(img):
    out = Image.new("RGBA", img.size)
    src_px, out_px = img.load(), out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = src_px[x, y]
            a_red = max(0.0, min(1.0, (255 - g) / (255 - RED[1])))
            pred_b = a_red * RED[2] + (1 - a_red) * 255
            if abs(pred_b - b) <= 30 and r > g + 20 * a_red - 5:
                out_px[x, y] = (255, 255, 255, round(a_red * 255))
            else:
                a_gold = max(0.0, min(1.0, (255 - b) / (255 - GOLD[2])))
                out_px[x, y] = (*GOLD, round(a_gold * 255))
    return out

big = logo.resize((1600, round(logo.height * 1600 / logo.width)), Image.LANCZOS)
light_logo = recolor(big)

for size in (180, 192, 512):
    S = size * 4
    icon = Image.new("RGB", (S, S), RED)
    # soft diagonal shading so it does not look flat
    shade = Image.new("L", (64, 64))
    shade.putdata([round((x + y) / 126 * 255 * 0.6) for y in range(64) for x in range(64)])
    icon = Image.composite(Image.new("RGB", (S, S), DEEP), icon, shade.resize((S, S), Image.BILINEAR))
    lw = round(S * 0.82)
    lh = round(light_logo.height * lw / light_logo.width)
    lg = light_logo.resize((lw, lh), Image.LANCZOS)
    icon.paste(lg, ((S - lw) // 2, round(S * 0.47 - lh / 2)), lg)
    # thin gold line under the logo
    lw2 = round(S * 0.34)
    icon.paste(Image.new("RGB", (lw2, max(2, round(S * 0.012))), GOLD), ((S - lw2) // 2, round(S * 0.47 + lh / 2 + S * 0.06)))
    icon.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, f"app-icon-{size}.png"), optimize=True)
    print("saved", size)
