#!/usr/bin/env python
"""Repaint the placeholder numbers on the two UI mockups with the real ones.

The mockups were generated before the pipeline finished, so they carry
illustrative figures. A deck whose headline slide says 7.7x and whose very next
screenshot says 3.47x loses the room -- that inconsistency is exactly what a
judge notices. These are our own mockups and these are our own measured
numbers, so the honest fix is to put the real ones on the image.

Reads out/stats.json and out/routes.json, so it cannot drift from the pipeline.

    .venv/Scripts/python.exe assets/fix_mockup_numbers.py
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "assets"
FONT = "C:/Windows/Fonts/arial.ttf"
FONT_B = "C:/Windows/Fonts/arialbd.ttf"
BRAND = (255, 193, 7)
WHITE = (230, 234, 240)
MUTED = (150, 160, 173)
GREEN = (38, 198, 166)
BLUE = (64, 163, 255)
GREY = (122, 134, 150)

stats = json.loads((ROOT/"out"/"stats.json").read_text())
routes = json.loads((ROOT/"out"/"routes.json").read_text())
cf = stats["counterfactual"]["40"]
RATIO = f'{cf["ratioMean"]:.1f}'
q1 = routes["queries"][0]
safer, short = q1["routes"][0], q1["routes"][1]

f = lambda p, s: ImageFont.truetype(p, s)


def fill(d, box, img):
    """Paint over a region using a pixel sampled just inside it, so the patch
    matches whatever surface the mockup used."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=img.getpixel((x0 + 2, y0 + 2)))


# ---------------------------------------------------------------- queue banner
im = Image.open(A/"screen-queue-raw.png").convert("RGB")
d = ImageDraw.Draw(im)
band = (118, 96, 1514, 166)
d.rectangle(band, fill=im.getpixel((1500, 100)))

x = 190
d.text((x, 112), "These ", font=f(FONT, 34), fill=WHITE)
x += d.textlength("These ", font=f(FONT, 34))
d.text((x, 112), "40", font=f(FONT_B, 34), fill=BRAND)
x += d.textlength("40", font=f(FONT_B, 34))
d.text((x, 112), " repairs restore", font=f(FONT, 34), fill=WHITE)

d.text((596, 92), RATIO, font=f(FONT_B, 74), fill=BRAND)
w = d.textlength(RATIO, font=f(FONT_B, 74))
d.text((596 + w + 6, 120), "x", font=f(FONT_B, 40), fill=BRAND)
tail = "the exposed pedestrian-km the complaint queue's first 40 would have."
tx = 596 + w + 46
size = 25
while d.textlength(tail, font=f(FONT, size)) > (1506 - tx) and size > 15:
    size -= 1
assert d.textlength(tail, font=f(FONT, size)) <= 1506 - tx, "banner text overflows"
d.text((tx, 124), tail, font=f(FONT, size), fill=WHITE)
im.save(A/"screen-queue.png")
print(f"queue banner -> {RATIO}x, budget 40")

# ---------------------------------------------------------------- route cards
im = Image.open(A/"screen-route-raw.png").convert("RGB")
d = ImageDraw.Draw(im)

def card(x0, x1, r, num_col):
    km = r["distanceM"]/1000
    fill(d, (x0, 424, x1, 470), im)
    d.text((x0 + 8, 424), f"{km:.2f}", font=f(FONT_B, 38), fill=WHITE)
    w = d.textlength(f"{km:.2f}", font=f(FONT_B, 38))
    d.text((x0 + 14 + w, 440), "km", font=f(FONT, 22), fill=MUTED)
    d.text((x0 + 150, 437), f"{r['walkMinutes']:.0f} min", font=f(FONT, 24), fill=WHITE)

    lit = r["litShare"]; dark = r["darkShare"]; unk = r["unknownShare"]
    bx0, bx1, by0, by1 = x0 + 8, x1 - 10, 516, 528
    fill(d, (bx0 - 2, by0 - 4, bx1 + 4, by1 + 4), im)
    span = bx1 - bx0
    cx = bx0
    for share, col in ((lit, GREEN), (dark, BLUE), (unk, GREY)):
        wpx = span * share
        if wpx > 1:
            d.rounded_rectangle((cx, by0, cx + wpx, by1), radius=6, fill=col)
        cx += wpx

    fill(d, (x0 + 6, 536, x1 - 6, 566), im)
    d.text((x0 + 8, 540), f"{lit*100:.0f}%", font=f(FONT_B, 22), fill=GREEN)
    d.text((x0 + 150, 540), f"{dark*100:.0f}%", font=f(FONT_B, 22), fill=BLUE)
    d.text((x1 - 70, 540), f"{unk*100:.0f}%", font=f(FONT_B, 22), fill=GREY)

card(26, 412, safer, GREEN)
card(437, 828, short, BLUE)

# route insight strip further down quotes km figures too
fill(d, (30, 1440, 823, 1478), im)
d.text((34, 1442), f"Shortest route has {short['distanceM']/1000:.2f} km",
       font=f(FONT, 21), fill=WHITE)
d.text((34, 1466), "of dark segments." if short["darkShare"] else "of unlit or unknown ground.",
       font=f(FONT, 21), fill=WHITE)
d.text((305, 1442), f"{short['unknownShare']*short['distanceM']/1000:.2f} km on shortest route",
       font=f(FONT, 21), fill=WHITE)
d.text((305, 1466), "have no reliable data.", font=f(FONT, 21), fill=WHITE)
im.save(A/"screen-route.png")
print(f"route cards -> safer {safer['distanceM']/1000:.2f}km "
      f"{safer['litShare']*100:.0f}/{safer['darkShare']*100:.0f}/{safer['unknownShare']*100:.0f}, "
      f"shortest {short['distanceM']/1000:.2f}km "
      f"{short['litShare']*100:.0f}/{short['darkShare']*100:.0f}/{short['unknownShare']*100:.0f}")
