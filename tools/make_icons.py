"""Build the header logo and Home Screen icons from the Style Encore logo. Needs Pillow.

Usage: python tools/make_icons.py <logo image with white background>
Writes icons/logo.png (tight crop for the header) and icons/icon-180.png, -192, -512.
"""
import os
import sys
from PIL import Image, ImageChops

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)

src = Image.open(sys.argv[1]).convert("RGB")
white = Image.new("RGB", src.size, (255, 255, 255))
mask = ImageChops.difference(src, white).convert("L").point(lambda v: 255 if v > 18 else 0)
logo = src.crop(mask.getbbox())

# header logo: tight crop, 900 px wide
w = 900
logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS).save(os.path.join(OUT, "logo.png"), optimize=True)

# app icons: logo centered on white with a thin red band at the bottom
RED = (0xC6, 0x20, 0x34)
GOLD = (0xD2, 0xB8, 0x87)
for size in (180, 192, 512):
    S = size * 4
    icon = Image.new("RGB", (S, S), "white")
    lw = round(S * 0.84)
    lh = round(logo.height * lw / logo.width)
    icon.paste(logo.resize((lw, lh), Image.LANCZOS), ((S - lw) // 2, round(S * 0.46 - lh / 2)))
    band = round(S * 0.07)
    icon.paste(Image.new("RGB", (S, band), RED), (0, S - band))
    icon.paste(Image.new("RGB", (S, round(band * 0.35)), GOLD), (0, S - band - round(band * 0.35)))
    icon.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, f"icon-{size}.png"), optimize=True)
    print("saved", size)
