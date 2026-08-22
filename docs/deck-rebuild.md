# Deck rebuild — 22 Aug 2026

`Roshni.pptx` was rebuilt from scratch by `deck/build.mjs`. It supersedes
`deck/build.js`. 18 slides → **16**. Every figure re-derived from
`out/stats.json`, `out/curve.json` and `out/segments.geojson` rather than copied
from a doc.

## Why a rebuild rather than a patch

The old deck's defects were systemic, not per-slide. Rendering it and reading
every slide turned up:

- **Titles positioned as if always one line.** Every two-line title collided with the content under it — slides 3, 4, 7, 9, 13, 18.
- **Hero numbers in a container too narrow for number + unit.** The `%` on slide 2 and the `×` on slide 9 wrapped to a second line and landed *on top of* the body paragraph. On slide 9 the numeral also overlaid the title. That was the "buggy" you saw.
- **Containers that clipped instead of growing** — "27.7%." lost its descender on slide 7, "Approve the IUDX request." was cut by its own box on slide 16, a table column ran under an adjacent panel on slide 13.
- **Five accent colours** (amber, green, blue, pink, grey) with no semantic rule.
- **Fixed content start-Y regardless of content height**, so most slides had a dead bottom third.

The old `deck/qa.py` passed all of it, because it estimates text height against
box height and has no collision detection and no renderer. It is still worth
running for the dead-number grep; it is not sufficient on its own.

## What the new generator enforces

| | |
|---|---|
| Reserved title band | `y 0.52–1.47`, content always starts at `1.78`. A two-line title cannot reach the content. |
| Hero numbers | number and unit are **runs in one paragraph**, `wrap:false`, 6″ wide. They cannot wrap and cannot collide. |
| One accent | sodium `F2A93B`, once per slide. Green/blue/pink removed. |
| Margins | `0.7″` every side, right content edge `12.63″` on every slide. |
| Footer | source line at `y 6.86` on all 16 slides. |
| Font | **Arial** throughout, Courier New for formulas. Segoe UI was replaced because LibreOffice substitutes it with different metrics, which makes the render QA untrustworthy. Swap to Inter/Archivo only if they are installed on the presenting machine. |
| No | edge stripes, accent rules under titles, bordered card grids, icon-in-circle filler. |

Three render-and-read QA passes were run against the rasterised slides, not
against the XML.

## Storytelling changes

- **Merged old 3 + 4.** The reframe and its evidence are one slide: *Not failing. Handed the wrong order.* — closure rates left, ward concentration right.
- **Dropped the design-system appendix slide.** It was an unreadable thumbnail.
- **Slide bodies cut to roughly half.** Most of the old on-slide prose is now in speaker notes, where it belongs. Every slide has notes.
- **Slide 8 (7.7×) leads with the stress tests on the slide itself** rather than as fine print — 4.9× / 1.9× / 6.4× / 5.4× in a four-row table, so the volunteering is visible, not just spoken.

## Verified against the raw pipeline output

Recomputed from `out/segments.geojson` (all 11,029 features), not read from a doc:

| | |
|---|---|
| ρ(activity, structural) | **0.302** ✓ |
| ρ(activity, night bus) | **0.436** ✓ |
| mean P(dark) | **0.2764** ✓ |
| segments with lamp evidence | **690 · 6.3%** ✓ |
| wards / km / segments | **33 · 1,180.0 · 11,029** ✓ |

## Four things you need to decide

**1. `ppt.md` slide 7 is stale.** It says the model went from *71% of segments
dark* to *21.4%*. `21.4%` and `71%` are both on `qa.py`'s own dead list, and
`stats.json` gives mean P(dark) = **27.6%**. The slide now states 27.6% and drops
the before/after framing, because I could not find a current pre-calibration
figure anywhere in `out/`. If you still have it from the rebuild run, put the
line back — showing that you audited your own output is worth having.

**2. Lamp counts disagree between docs.** `ppt.md` slide 14 says *1,211 mapped
lamps, 1,080 labelled*. `stats.json` says `lampsInSnapshot: 1508`,
`lampsWorkingYes: 471`, `lampsWorkingNo: 657` → **1,508 / 1,128**. The deck uses
the `stats.json` figures. 1,211 was an Overpass count for the exact bbox on
21 Aug; the pipeline snapshot covers a padded area. Both are defensible; pick one
and make every doc say it.

**3. The queue screenshot contradicts itself.** It reads
**"Ranked worklist (Top 25 of 10 segments)"** and the status bar says
*Segments loaded: 10*, while the headline claims 40 repairs. It is also showing
wards from across the whole city — Yelahanka, Whitefield, RR Nagar, Hebbal —
which are **outside the locked ORR bbox** the rest of the deck is scoped to.
It is running on the fixture. Regenerate it against `out/segments.demo.geojson`
before submission; a judge who reads the screenshot will catch this. The slide's
source line currently says "running on the fixture export" so the deck is not
lying, but it is weaker than it needs to be.

**4. The scatter must be built from `segments.geojson`, never `segments.demo.geojson`.**
The demo export is a *selected* subset — every evidence-bearing segment plus the
top 2,000 by priority. Selecting on priority, which is a function of exposure,
induces a collider bias between the two exposure components: the same Spearman
computed on the demo file gives **ρ = −0.195**. Plotting that would contradict
slide 12 on slide 12's own evidence. The chart in this deck is built from all
11,029 features.

## One thing I did not build

The validation slide's **left-hand "broken run" scatter** — 1,164 points, ρ = 0.03,
55% connected. That data is not in `out/` and I will not fabricate a plot. The
slide instead carries the real corrected scatter plus a small before/after bar of
the two ρ values, which are both recorded. If you still have the first-pass ranks,
add the second panel — two plots and an arrow is a stronger object than one plot.

## Rebuilding

```
node deck/build.mjs                  # writes deck/Roshni.pptx
python deck/mkcharts.py              # regenerates deck/assets/chart-*.png
python deck/qa.py                    # dead-number grep, still useful
```

Charts are PNGs on the ink background rather than native PowerPoint charts,
because native charts fight a dark theme and lose. They are generated from the
pipeline output, so a re-run of the pipeline means a re-run of `mkcharts.py`.
