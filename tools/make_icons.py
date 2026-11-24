"""Draw the app's Home Screen icons (icons/icon-180.png, -192, -512). Needs Pillow."""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)

def icon(size):
    s = 4  # draw large, then shrink for smooth edges
    W = size * s
    img = Image.new("RGB", (W, W))
    px = img.load()
    a, b = (0x5b, 0x2a, 0x86), (0xa8, 0x32, 0x7a)   # brand purple -> berry
    for y in range(W):
        for x in range(W):
            t = (x + y) / (2 * W)
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    d = ImageDraw.Draw(img)
    # white "photo" card
    m = W * 0.17
    d.rounded_rectangle([m, m, W - m, W - m], radius=W * 0.09, fill="white")
    # hanger: hook + triangle, in brand purple
    cx = W / 2
    lw = round(W * 0.045)
    col = a
    top = W * 0.30
    d.arc([cx - W * 0.06, top - W * 0.06, cx + W * 0.06, top + W * 0.06], start=180, end=90, fill=col, width=lw)
    neck = top + W * 0.10
    d.line([cx, top + W * 0.06, cx, neck], fill=col, width=lw)
    left, right, base = (W * 0.27, W * 0.62), (W * 0.73, W * 0.62), None
    d.line([left, (cx, neck), right, left], fill=col, width=lw, joint="curve")
    # sparkle
    sx, sy, r = W * 0.70, W * 0.73, W * 0.06
    d.polygon([(sx, sy - r), (sx + r * 0.3, sy - r * 0.3), (sx + r, sy), (sx + r * 0.3, sy + r * 0.3),
               (sx, sy + r), (sx - r * 0.3, sy + r * 0.3), (sx - r, sy), (sx - r * 0.3, sy - r * 0.3)], fill=b)
    return img.resize((size, size), Image.LANCZOS)

for size in (180, 192, 512):
    icon(size).save(os.path.join(OUT, f"icon-{size}.png"), optimize=True)
    print("saved", size)
