#!/usr/bin/env python
"""Deck diagrams, drawn from the product's own palette.

Two of them:
  assets/diagram-connection.png  input -> one estimate -> two decisions
  assets/diagram-inputs.png      the input ladder, and what each source buys

Numbers come from out/stats.json, so a rerun of the pipeline updates the
diagrams rather than leaving them to drift.

    .venv/Scripts/python.exe assets/diagrams.py
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
S = json.loads((ROOT / "out" / "stats.json").read_text())
CF = S["counterfactual"]["40"]

BG, SURF, HAIR = (11, 15, 20), (18, 24, 32), (35, 43, 54)
TEXT, MUTE, DIM = (230, 234, 240), (177, 186, 198), (122, 134, 150)
BRAND, TEAL, BLUE, INDIGO = (255, 193, 7), (38, 198, 166), (64, 163, 255), (124, 155, 255)
R = "C:/Windows/Fonts/arial.ttf"
B = "C:/Windows/Fonts/arialbd.ttf"
f = lambda p, s: ImageFont.truetype(p, s)


def card(d, box, stroke=HAIR, fill=SURF, r=14, w=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=stroke, width=w)


def label(d, xy, text, font, fill, anchor="la", spacing=8):
    d.multiline_text(xy, text, font=font, fill=fill, anchor=anchor, spacing=spacing)


def arrow(d, x0, y, x1, col=DIM, w=3, head=13):
    d.line((x0, y, x1 - head, y), fill=col, width=w)
    d.polygon([(x1, y), (x1 - head, y - head // 2), (x1 - head, y + head // 2)], fill=col)


def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return "\n".join(lines)


# ------------------------------------------------------- 1. the connection
W, H = 2400, 1250
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

d.text((90, 74), "One estimate. Two decisions.", font=f(B, 62), fill=TEXT)
d.text((92, 152), "Everything on this diagram runs from a single darkness estimate "
                  "per 150 m of street.", font=f(R, 30), fill=DIM)

COL1, COL2, COL3 = 90, 900, 1620
TOP = 250

# inputs
card(d, (COL1, TOP, COL1 + 660, TOP + 430))
d.text((COL1 + 34, TOP + 30), "THE CITY GIVES", font=f(B, 23), fill=DIM)
rows = [("Road network", "the only hard requirement", TEAL),
        ("Ward boundaries", "optional", DIM),
        ("Lamp counts per ward", "optional", DIM),
        ("Complaint log", "optional", DIM),
        ("Transit feed", "optional", DIM)]
y = TOP + 82
for name, note, col in rows:
    d.ellipse((COL1 + 34, y + 9, COL1 + 46, y + 21), fill=col)
    d.text((COL1 + 62, y), name, font=f(R, 30), fill=TEXT)
    d.text((COL1 + 62 + d.textlength(name, font=f(R, 30)) + 18, y + 6), note,
           font=f(R, 22), fill=col if col is TEAL else DIM)
    y += 66

card(d, (COL1, TOP + 470, COL1 + 660, TOP + 700), stroke=BRAND)
d.text((COL1 + 34, TOP + 500), "A CITIZEN GIVES", font=f(B, 23), fill=BRAND)
d.text((COL1 + 34, TOP + 546), "One tap: “this stretch is dark”", font=f(B, 34), fill=TEXT)
d.text((COL1 + 34, TOP + 600), "GPS and a timestamp. No account, and no\n"
                               "lamp number to hunt for in the dark.",
       font=f(R, 26), fill=MUTE, spacing=8)

# the model
card(d, (COL2, TOP + 90, COL2 + 560, TOP + 560), stroke=INDIGO)
d.text((COL2 + 40, TOP + 126), "ROSHNI", font=f(B, 34), fill=INDIGO)
d.text((COL2 + 40, TOP + 182),
       "One darkness estimate per\n150 m of street, each with\na confidence band.",
       font=f(R, 31), fill=TEXT, spacing=12)
d.line((COL2 + 40, TOP + 330, COL2 + 520, TOP + 330), fill=HAIR, width=2)
for i, (k, v) in enumerate([
        ("segments scored", f'{S["segments"]:,}'),
        ("of them running on priors alone", f'{round(S["priorOnlyShare"]*100)}%'),
        ("corridor", f'{S["totalCorridorKm"]:,.0f} km')]):
    yy = TOP + 358 + i * 58
    d.text((COL2 + 40, yy), k, font=f(R, 25), fill=DIM)
    d.text((COL2 + 520, yy - 3), v, font=f(B, 28), fill=TEXT, anchor="ra")

arrow(d, COL1 + 690, TOP + 215, COL2 - 20)
arrow(d, COL1 + 690, TOP + 585, COL2 - 20)
arrow(d, COL2 + 590, TOP + 210, COL3 - 20, col=TEAL)
arrow(d, COL2 + 590, TOP + 440, COL3 - 20, col=BRAND)

# outputs
card(d, (COL3, TOP + 60, COL3 + 690, TOP + 320), stroke=TEAL)
d.text((COL3 + 34, TOP + 92), "SOMEONE WALKING HOME", font=f(B, 23), fill=TEAL)
d.text((COL3 + 34, TOP + 138), "A better-lit way back", font=f(B, 36), fill=TEXT)
d.text((COL3 + 34, TOP + 194),
       wrap(d, "Two routes side by side, and an honest line about how much of "
                "each one we cannot vouch for.", f(R, 26), 620),
       font=f(R, 26), fill=MUTE, spacing=8)

card(d, (COL3, TOP + 360, COL3 + 690, TOP + 700), stroke=BRAND)
d.text((COL3 + 34, TOP + 392), "THE CITY", font=f(B, 23), fill=BRAND)
d.text((COL3 + 34, TOP + 438), "This week’s work order", font=f(B, 36), fill=TEXT)
d.text((COL3 + 34, TOP + 494),
       wrap(d, "Forty streets, ranked by how many people actually walk them "
                "after dark. Exported as a CSV a crew can be sent against.",
            f(R, 26), 620), font=f(R, 26), fill=MUTE, spacing=8)
d.text((COL3 + 34, TOP + 620), f'{CF["ratioMean"]:.1f}×', font=f(B, 54), fill=BRAND)
d.text((COL3 + 34 + 150, TOP + 636),
       "the exposed pedestrian-km that\nthe complaint queue’s first 40 restore",
       font=f(R, 23), fill=DIM, spacing=6)

# the loop
ly = TOP + 760
card(d, (COL1, ly, COL3 + 690, ly + 150), fill=(16, 21, 28))
d.text((COL1 + 34, ly + 28), "WHEN IT IS FIXED", font=f(B, 23), fill=DIM)
seq = [("The person who reported it finds out.", TEXT, R),
       ("The city finds out whether “closed” meant fixed —", TEXT, R),
       ("nobody asks that today.", BRAND, B)]
lx = COL1 + 34
for txt, col, face in seq:
    d.text((lx, ly + 72), txt, font=f(face, 30), fill=col)
    lx += d.textlength(txt, font=f(face, 30)) + 26

d.text((90, H - 74), "Bengaluru, ORR corridor. Every figure recomputed from open data; "
                     "no lamp inventory used.", font=f(R, 24), fill=DIM)
im.save(OUT / "diagram-connection.png")
print("diagram-connection.png")

# ------------------------------------------------------- 2. the input ladder
W2, H2 = 2400, 1180
im = Image.new("RGB", (W2, H2), BG)
d = ImageDraw.Draw(im)
d.text((90, 74), "A road network is the only hard requirement.", font=f(B, 62), fill=TEXT)
d.text((92, 152), "Every other source narrows the confidence bands. None of them "
                  "unlocks a feature.", font=f(R, 30), fill=DIM)

ladder = [
    ("OpenStreetMap road network", "mandatory", "Ranks every street by structural "
     "night exposure. Darkness is a class-weighted prior.", 0.26, TEAL),
    ("+ ward boundaries", "optional", "The prior gets spatial resolution — density "
     "varies ward by ward instead of city-wide.", 0.40, BLUE),
    ("+ lamp counts per ward", "optional", "Coverage becomes measurable: lamps per km "
     "against 30 m standard pole spacing.", 0.58, BLUE),
    ("+ complaint log", "optional", "The counterfactual can be computed against the "
     "city’s own queue, in its own numbers.", 0.72, BLUE),
    ("+ transit feed with departure times", "optional", "Night service becomes "
     "countable. Where buses stop, people walk.", 0.84, INDIGO),
    ("+ smart-lighting telemetry", "gated", "Estimate becomes measurement. The bands "
     "collapse. Nothing else changes.", 1.0, BRAND),
]
y = 268
BARX, BARW = 1310, 960
for name, tag, what, frac, col in ladder:
    d.text((90, y), name, font=f(B, 33), fill=TEXT)
    tw = d.textlength(name, font=f(B, 33))
    d.text((90 + tw + 20, y + 7), tag, font=f(R, 23),
           fill=TEAL if tag == "mandatory" else BRAND if tag == "gated" else DIM)
    d.text((90, y + 48), wrap(d, what, f(R, 25), 1130), font=f(R, 25), fill=MUTE, spacing=7)
    d.rounded_rectangle((BARX, y + 12, BARX + BARW, y + 44), radius=16, fill=(24, 32, 42))
    d.rounded_rectangle((BARX, y + 12, BARX + int(BARW * frac), y + 44), radius=16, fill=col)

    y += 138

d.text((BARX, 214), "HOW MUCH THE MODEL CAN SAY", font=f(B, 21), fill=DIM)
d.text((BARX, 244), "relative, illustrative — not a measured score", font=f(R, 20), fill=(90, 100, 114))
d.text((90, H2 - 96), "We ran it on Bengaluru because Bengaluru publishes unusually "
                      "good open data. Bengaluru is not the product — it is the deepest "
                      "proof we could get.", font=f(R, 26), fill=MUTE)
d.text((90, H2 - 54), "We have not yet run a second city, so portability is an argument "
                      "from architecture rather than a demonstration.",
       font=f(R, 24), fill=DIM)
im.save(OUT / "diagram-inputs.png")
print("diagram-inputs.png")
