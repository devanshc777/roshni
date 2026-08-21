#!/usr/bin/env python
"""QA the generated deck without a renderer.

There is no LibreOffice on this machine, so slides cannot be rasterised and
eyeballed. This does the two checks that catch most of what an eyeball would:

  1. Text-fit estimate. For every text frame, estimate how many lines the text
     needs at its own font size and box width, and flag frames where the text
     probably will not fit. Segoe UI averages about 0.5 em per character, which
     is close enough to catch real overflow and ignore near-misses.
  2. Content checks. Dead numbers from superseded pipeline runs, leftover
     placeholder words, missing speaker notes, missing images.

Run: .venv/Scripts/python.exe deck/qa.py
"""
import math
import re
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu

DECK = Path(__file__).resolve().parent / "Roshni.pptx"

# numbers and phrases that were true in an earlier pipeline run and must not
# survive into the deck
DEAD = [
    "5.2×", "5.2x", "1.58×", "1.58x", "5.16", "3.47", "1,164 segments",
    "160.9", "85% of", "ρ = 0.03 between", "225 a day", "Horamavu 3,128",
    "~800", "half a million", "303 bus stops", "VIIRS raster",
    "71% of segments", "21.4%", "0.73", "73%",
]
PLACEHOLDER = ["lorem", "ipsum", "xxxx", "TODO", "TBD", "placeholder", "Lorem"]

EM_PER_CHAR = 0.5     # Segoe UI average advance width
TOLERANCE = 1.18      # allow 18% over before flagging; PowerPoint wraps tighter


def frame_runs(tf):
    out = []
    for para in tf.paragraphs:
        size = None
        text = "".join(r.text for r in para.runs)
        for r in para.runs:
            if r.font.size:
                size = r.font.size.pt
                break
        out.append((text, size or 18.0))
    return out


def estimate_height_in(tf, width_in):
    """Inches of vertical space the text probably needs."""
    total = 0.0
    for text, size in frame_runs(tf):
        if not text.strip():
            total += size * 0.6 / 72
            continue
        chars_per_line = max(1, (width_in * 72) / (size * EM_PER_CHAR))
        lines = max(1, math.ceil(len(text) / chars_per_line))
        total += lines * size * 1.28 / 72
    return total


def main():
    if not DECK.exists():
        sys.exit(f"missing {DECK} — run `node deck/build.js` first")
    prs = Presentation(DECK)
    sw, sh = prs.slide_width / 914400, prs.slide_height / 914400
    print(f"{DECK.name}: {len(prs.slides)} slides, {sw:.2f} x {sh:.2f} in\n")

    overflow, dead, missing_notes, images, charts, tables = [], [], [], 0, 0, 0
    all_text = []

    for i, slide in enumerate(prs.slides, 1):
        notes = (slide.notes_slide.notes_text_frame.text.strip()
                 if slide.has_notes_slide else "")
        if not notes:
            missing_notes.append(i)
        for sh_ in slide.shapes:
            if sh_.shape_type == 13 or sh_.__class__.__name__ == "Picture":
                images += 1
            if sh_.has_chart if hasattr(sh_, "has_chart") else False:
                charts += 1
            if getattr(sh_, "has_table", False):
                tables += 1
            if not sh_.has_text_frame:
                continue
            text = sh_.text_frame.text
            if not text.strip():
                continue
            all_text.append((i, text))
            w_in = Emu(sh_.width).inches
            h_in = Emu(sh_.height).inches
            need = estimate_height_in(sh_.text_frame, w_in)
            if need > h_in * TOLERANCE:
                overflow.append((i, text[:58].replace("\n", " ⏎ "),
                                 round(need, 2), round(h_in, 2)))

    joined = "\n".join(t for _, t in all_text)
    for token in DEAD:
        for i, t in all_text:
            if token in t:
                dead.append((i, token, t[:60].replace("\n", " ")))
    ph = [(i, p) for p in PLACEHOLDER for i, t in all_text if p in t]

    print(f"images embedded: {images}   charts: {charts}   tables: {tables}")
    print(f"text frames checked: {len(all_text)}\n")

    ok = True
    if overflow:
        ok = False
        print(f"LIKELY TEXT OVERFLOW ({len(overflow)}):")
        for i, t, need, have in sorted(overflow, key=lambda r: -(r[2] / r[3])):
            print(f"  slide {i:>2}  needs ~{need}in in {have}in  |  {t}")
        print()
    if dead:
        ok = False
        print(f"SUPERSEDED NUMBERS PRESENT ({len(dead)}):")
        for i, tok, ctx in dead:
            print(f"  slide {i:>2}  '{tok}'  |  {ctx}")
        print()
    if ph:
        ok = False
        print(f"PLACEHOLDER TEXT: {ph}\n")
    if missing_notes:
        print(f"slides without speaker notes: {missing_notes}\n")

    for want, label in [("7.7", "headline ratio"), ("96.4", "closure rate"),
                        ("31.4", "complaint share"), ("0.30", "corrected rho"),
                        ("0.03", "the null we report"), ("17.9", "median bypass"),
                        ("5.4", "labels-deleted ratio")]:
        if want not in joined:
            ok = False
            print(f"MISSING expected figure: {want} ({label})")

    print("\nPASS — nothing flagged." if ok else "\nFIX THE ABOVE.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
