# Roshni reimagined — the plan

Branch `reimagined`. Written 22 Aug 2026 after a reviewer read the working
prototype and concluded the substance is fine and the presentation is not.

> **The current prototype makes the judge understand the implementation before
> they understand the product.**

That is the whole diagnosis and it is correct. Nothing in `data/` changes. The
pipeline, the posterior, the counterfactual, the routing graph all stay exactly
as measured. **We rebuild what the judge sees, not what the system does.**

## The product in one line

> People report dark streets → Roshni estimates darkness → exposure changes what
> gets repaired and what gets recommended for walking.

Three nouns the audience has to remember: **dark**, **busy**, **decide**.
Everything else is supporting evidence, available on demand, invisible by
default.

---

## 1. What is wrong, precisely

Not polish. Four structural mistakes.

**Everything has equal visual weight.** The map draws 11,029 segments at
comparable width and opacity, so there is no dominant object and nothing to look
at. A sidebar of equal density competes with it.

**The machinery is on the surface.** Segment counts, corridor kilometres,
posterior variance, confidence-as-texture legends, stress-test ratios, three
weight sliders and a budget slider all appear before the product has said
anything. A judge reads complexity where they should read one sentence.

**The map is unrecognisable.** Bare GeoJSON linework, no labels, no place
context, no city outline. It reads as `roads.json`, not Bengaluru, and that
quietly undermines every number placed beside it.

**The one deliverable the problem statement names first does not exist as a
surface.** PS 17 asks for *"a public dark-zone risk map."* We built a municipal
console that happens to contain a map. The public map was never its own screen.

---

## 2. Screens

Four tabs and one panel. The nav names the product, not the features.

```
● ROSHNI      Map    Walk    Report    City          Coverage    11:30 PM
```

| Surface | The 3-second understanding | Dominant object |
|---|---|---|
| **Map** | these are the dark, busy streets | the map, then one card |
| **Walk** | slightly longer, better lit | two cards |
| **Report** | one tap improves the data | one button |
| **City** | repair this street before that one | a ranked list |
| **Coverage** | a road network is all it needs | an input ladder |

### Map — the public dark-zone risk map

The PS deliverable, finally first-class. Map dominates; the panel is gone.
Clicking a street produces a floating card:

```
4TH MAIN ROAD
Madiwala

Likely dark          82%
Night footfall       among the busiest
How sure we are      estimated only
Repair priority      #3

[ Report darkness ]
```

Nothing else on screen but the nav, the city, and a single primary action.
`See how reports change this ▸` opens the before/after sequence (§4).

### Walk — two routes, one decision

Kept conceptually; simplified visually. Two cards side by side, the map below as
proof the routes exist, one honest sentence underneath. **"Better lit" is a
choice, not an alarm** — the shortest route is always shown next to it, never
hidden or warned against.

```
+3 min · 846 m less street we can't vouch for
```

### Report — one question

```
IS THIS STREET DARK?
4th Main Road · Madiwala · 11:23 PM

[      YES — REPORT IT      ]

Your location is attached automatically.
```

Then the result, which is the entire point:

```
4th Main Road    #24 → #18
Your report changed the repair queue.
```

The suggestion list ("streets worth checking tonight") survives as **three rows
below the fold**, because directed reporting is a real differentiator. UCB,
variance and targeting language do not appear — they are the answer to *"how do
you decide where to ask?"*, not a label.

### City — a list, not a console

Not a full-screen map; this is a table task at a desk on a Monday morning.

```
REPAIR QUEUE                    [ Roshni order | Complaint order ]
Where darkness affects the most people

                      7.7×
        more pedestrian exposure restored than complaint order

01  Service Road       Bellanduru  2,281 m / 13 stretches  ████████ 100
02  Outer Ring Road    Bellanduru  1,707 m / 10 stretches  ██████    78
...                                          footfall index, relative

[ Export work order ]        Tune scoring ▾
```

The budget slider and the three weight sliders move **behind `Tune scoring`**.
They are an excellent answer to a judge's question and a terrible first
impression.

### Coverage — the generality panel

A header link, **not a fifth workflow**, and explicitly not a city dropdown.
Roughly 5–10% of the visual real estate, which is the right budget for proving
generality.

```
BUILT FOR BENGALURU. DESIGNED FOR ANY CITY.

✓ Road network          required     OpenStreetMap
✓ Ward boundaries       optional     225 BBMP wards
✓ Complaint history     optional     126,974 records, Jan–Jun 2025
✓ Transit departures    optional     101,367 in the demo area
○ Lamp inventory        optional     1,128 citizen-labelled, no municipal feed
○ Live telemetry        gated        we speak the IUDX record shape

More local data → narrower uncertainty. None of it unlocks a feature.
```

Closing line, said plainly because it is the defensible version:

> Built and measured in Bengaluru. The architecture is city-agnostic. Transfer
> to a second city is validation work we have not done.

**No "Select city" dropdown.** A judge would say "show me Mumbai," and we cannot.

---

## 3. The full Bengaluru map

The reviewer's largest visual complaint and the user's explicit ask. Fixed with
data already downloaded — `data/raw/bbmp_wards_2023.kml`, which turns out to
carry **225 ward polygons with population per ward.**

Measured: **8,449,004 people city-wide; about 765,000 across 24 wards inside the
locked demo bbox (9.1%)**, by clipping each ward polygon to the bbox and
area-weighting its population. A first pass used ward centroids and got 788,462
across 21 — close, but not defensible, because the rectangle is about the size of
one ward and a centroid test misclassifies edge wards both ways.

So the city-wide layer is not decoration — it states the honest scope:

> We measured this rectangle deeply — about 765,000 people, 24 wards. The same
> architecture covers the other 7.7 million.

Four z-ordered layers, each with one job:

| Layer | Treatment | Job |
|---|---|---|
| City wards (225) | 0.5px `#1B232E` outline, no fill | this is Bengaluru, and it is big |
| Demo subsection | 1px brand outline, 4% brand fill | this is what we measured |
| Roads outside scope | 0.35px `#161D26` | texture, never read |
| Scored roads | **colour = darkness, width = exposure** | the product |
| Selected road | 6px pale brand + blur | the one thing you are looking at |

Labels, all from data on disk, all offline:

All labels are **DOM spans positioned with `map.project()`**, not a MapLibre
`symbol` layer — the style declares no `glyphs` URL and the page makes no network
requests, so `text-field` would render nothing at all. See the review-round notes
at the end.

- **ward names** — from KML centroids, capped and culled by zoom; outside the
  measured area they drop away as you zoom in.
- **street names** — only for segments the model calls dark, capped at 22.
  1,550 of 2,117 demo segments carry a name.
- **on the Walk screen** — labelled `START` / `HOME` pins, because the routing
  graph spans the whole snapshot while names only exist for the scored subset.
- **no BENGALURU wordmark** — the ward names and the city silhouette say it, and
  the panel says it in words.

Density collapses: roughly 80–90% of linework drops to near-invisible so the
scored network can be the only thing with contrast.

---

## 4. The simulation becomes a sequence, not a tab

The Live feed's diagnosis was: *correct and illegible* — a percentage, a street
count, a swap count and ninety words all moving together in a 350px column.

It stops being a tab. It becomes a **full-bleed overlay in three states**,
launched from Map, and it is the demo's opening beat.

**State 1 — before.** Two lists side by side, complaint order against Roshni
order, and one button: `Simulate reports`.

**State 2 — running.** Reports pulse on the map. One number, large, falling:

```
63%  →  6%
of the shortest way home crosses street we can't vouch for
```

**State 3 — the reveal.** One sentence, nothing else:

> **The complaint queue fixed whoever complained first.
> Roshni fixes whoever is actually walking.**
>
> The top 40 barely moved — most reports came from streets we already knew about.
> That is the bias, and it is why the app asks.

Speed controls, the reset button, the arriving-now ticker and the four
paragraphs are deleted. Play and scrub survive.

---

## 5. Visual system

**Three colours, total.** Yellow `#FFC107` = attention, dark, fix. Teal
`#26C6A6` = better, safe, improved. Grey = ground and unknown. Blue and indigo
are removed; the shortest route draws in `#8C97A6` so teal is the only
route colour that means anything. No red — nothing here is an alarm.

**One dominant number per screen**, at 56–84px, with a small label beneath.
Hero numbers: `7.7×`, `+3 min`, `#24 → #18`, `63% → 6%`.

**Cards become flat surfaces with one hairline.** No nested boxes. Fewer
borders, more whitespace, fewer words.

**Confidence has three registers.** Citizen: *"we don't know this street well."*
Municipal: a `● ◐ ○` glyph. Technical: the posterior, behind Methodology. The
legend explaining texture leaves the screen.

### Deleted from the UI

`11,029 segments` · `1,180 km` · `0 network calls` · speed controls · reset ·
visible weight sliders · visible budget slider · stress-test ratios · the
confidence-texture legend · "Municipal Engineer Console" · the arriving-now
ticker · every explanatory paragraph over one sentence · most map dots.

They stay in the deck, `docs/`, and the Methodology sheet. **Deleted from the
app, not from the argument.**

---

## 6. Problem-statement adherence

The reduction has to not cost us a deliverable. It does the opposite.

| PS text | Before | After |
|---|---|---|
| "pedestrian-centric streetlight reporting" | Report tab | Report, simplified |
| "…and routing system" | Walk tab | Walk, simplified |
| **"a public dark-zone risk map"** | **no such surface** | **Map, first-class** |
| "weights repairs by pedestrian exposure" | City queue | City, list-first |
| "recommends well-lit safer alternate routes" | Walk tab | unchanged |
| Challenge: validate footfall with no data | docs only | Coverage + Methodology |

**5 of 6 improve; none regress.** The map deliverable goes from absent to the
default screen.

### The challenge question, answered properly

Not *"beta-binomial posterior with UCB targeting."* That answers a question
nobody asked. The answer is a procedure:

1. **Estimate** from observable proxies — road class, connectivity, night-active
   land use, transit access.
2. **Validate** by counting a sample: 10–20 streets spanning the predicted
   range, counted by hand or camera, prediction against observation.
3. **Calibrate** and report the residual.

Then the line that makes it a product thesis rather than a science claim:

> Roshni does not need a correct footfall number. It needs an **ordering** good
> enough to beat complaint order.

**Quote the ablations here, not the headline.** The gap is 7.7× at the measured
configuration, but that figure is computed against our own objective, so on its
own it shows the model outscoring a naive baseline on a metric the model also
defines. The numbers that answer the challenge question are the ones that hold
when the evidence is taken away: **5.42×** with every lamp label deleted,
**6.4×** holding geography and evidence coverage constant, **1.89×** against a
steelman that picks the worst street in every ward it visits. Those say the
ordering is not a coverage artefact. Criterion validation against the BTP crash
PDFs is still the only independent leg, and it is still unmined — say so.

---

## 7. Build order, and what gets abandoned first

One file still: `web/index.html`. No backend, no new dependency, offline.
New data prep is one script pass, reusing `data/pipeline.py` outputs untouched.

| # | Work | Why it is first |
|---|---|---|
| 1 | `out/city.geojson` — 225 ward outlines + centroids + population | unblocks the map |
| 2 | Map layer hierarchy, labels, density collapse | the largest visual defect |
| 3 | Map screen: decision card, nav rename, panel removed | the missing PS deliverable |
| 4 | City: list-first, sliders behind disclosure | worst overbuild |
| 5 | Report: one question, one button, one result | cheapest win |
| 6 | Walk: two cards, prose cut | already closest |
| 7 | Simulation overlay, three states | biggest legibility gain |
| 8 | Coverage panel | generality, 5% of the pixels |
| 9 | Colour reduction, type scale, whitespace | global pass |

**Order of abandonment**, if time runs out: drop 9, then 8, then 7. Never drop
1–3 — an unrecognisable map is the defect that makes a judge distrust the
numbers, and the public map is the PS deliverable.

## Definition of done

- Every screen passes the 3-second test in the table in §2.
- The map is recognisable as Bengaluru without a caption.
- No screen shows a number the deck cannot source.
- The generality claim is stated with its limit attached, in the app.
- Runs offline from `file://` and at 414px.
- Every deleted claim still exists in `docs/` — nothing is destroyed, only hidden.

---

## What the review round changed

Three reviewers read this plan before it was built — one on how the demo lands
in the room, one on whether every number survives contact with
`measured-2026-08-22.md`, one on whether it could be built in the time left.
What they changed, and what they got wrong.

### Adopted

**The map has to encode exposure, not just darkness.** The largest single
finding. As first written, line width rose with darkness alone, which draws a
broken-lamp map — and a broken-lamp map is neither novel nor the differentiator
the problem statement names. Now **colour carries darkness and width carries
exposure**, so a thick bright line is a street that is both unlit and heavily
walked. That is the only thing on the map worth acting on, and it is legible in
the first ten seconds without reading anything.

**The colour ramp contradicted its own legend.** Found by looking at the render,
not by reasoning: the old ramp ran cream → deep blue, so well-lit streets were
the *brightest* thing on screen while the panel said brighter meant more likely
unlit. Replaced with a ramp monotonic in brightness, dim grey → full amber.

**Confidence is relocated, not deleted.** 93.7% of segments run on the ward
prior alone. Showing "82% likely dark" with no register attached would give a
prior-only estimate the same visual authority as a lamp-evidenced one. The map
card now carries *measured / partly known / estimated only* in words, and the
texture legend lives behind "How sure are we?" on the City screen.

**The complaint-history label was wrong.** It read "126,974 grievances,
2020–2025". The 126,974 rows are **1 Jan – 19 Jun 2025** — a five-and-a-half
month window. Two older docs carry the same error; the app no longer does.

**The population figure needed a real method.** The first pass tested ward
membership by asking whether a ward's *centroid* fell inside the demo bbox. The
rectangle is comparable in size to a single ward, so that misclassifies edge
wards in both directions. Replaced with Sutherland-Hodgman clipping and
area-weighted population: **about 765,000 people across 24 wards**, down from the
centroid estimate of 788,462 across 21. Centroids are now label anchors only,
and the number is quoted as "about", to two significant figures, because it
assumes even population density inside a ward.

**Absolute footfall counts are gone.** An earlier draft of this rebuild printed
"237 people on foot / night" per street, derived from the exposure index by an
arbitrary scale factor. That invents precisely the quantity the challenge
question says has to be validated. The screens now show a **relative footfall
index** and the map card says it in words.

**One street per row.** OSM splits a road into many short ways, so the raw
ranking put four separate 170 m pieces of the same service road in the top five.
Correct, and useless to read or dispatch against. Lists now group by street and
total the metres — "Service Road, Bellanduru, 2,281 m across 13 stretches" — which
is what a work order should have said in the first place.

### Corrected — where a reviewer was wrong

**The Walk figures are not stale.** Two reviewers flagged `+3 min · 846 m` and
`63% → 6%` as copied from an old deck. They are computed live, per render, from
the current belief state — which is why they stay true after reports arrive. The
stale artefact is the **route table in `measured-2026-08-22.md` §6b**, which
predates the full-bbox pipeline rebuild and still describes a two-query
`routes.json` on the old sub-bbox. That table needs regenerating; the app does
not.

**Out-of-scope roads needed no new source.** The build reviewer costed a second
fetch of the 7.7 MB `segments.geojson` to draw roads outside the scored area.
`basemap.geojson` was already loaded and already covers the whole snapshot. The
step was free.

**Glyphs were the real blocker, and the fix is not glyphs.** Both the earlier
brief and the build reviewer proposed a MapLibre `symbol` layer for street
labels. The style declares no `glyphs` URL, so `text-field` renders nothing —
MapLibre rasterises text from glyph PBFs over the network, and this page makes no
requests. Rather than vendor font ranges, labels are **DOM spans projected with
`map.project()`**: offline by construction, capped and culled by zoom, and with
real CSS typography. Street labels on the Walk screen fall back to labelled
endpoints, because the routing graph spans the whole snapshot while `PROPS` only
covers the scored subset, so most segments on a given walk have no name at all.

### Known, and deliberately left

**The app renders 7.8× where the pipeline computes 7.73×.** Same method, same
300 draws, different RNG — mulberry32 in the browser against numpy in the
pipeline. It is ~1% sampling noise. **Quote 7.7× everywhere off-screen**; if a
judge spots the difference, that sentence is the answer. Raising the browser from
60 to 300 draws already closed most of the gap.

**`docs/ps-adherence.md` is stale** where it records the reporting screen as "not
built — mockup exists". It has been built since. That file is an audit dated
before the citizen surfaces landed, and it should be re-run rather than patched.
