# PPT — build spec

**This file is the deck.** Every slide's title, body copy, visual, source line
and speaker note is written out verbatim below. Copy the text, don't rewrite it —
the wording is load-bearing in places and the numbers are all measured.

Who this is for: whoever is building the deck, working alone, while the
developers make the MVP real. You should not need to ask a developer anything to
finish it.

- **Numbers**: all measured 22 Aug 2026, **after the rebuild** — authority is `docs/measured-2026-08-22.md` §10, which supersedes §5 and §6 of that same file. If any other doc in this repo disagrees with a number here, this file and that one win.
- **UI screenshots**: prompts to generate the screens are in `docs/prompts.md`. Feed them `out/segments.fixture.geojson`.
- **Deck-generator prompts**: Part 7 of this file. Paste-ready for Gamma / Claude / Copilot.
- **Longer rationale** per slide, if you want the reasoning: `docs/deck-outline.md`.

**16 slides. 16:9. Dark throughout.** Judges skim. One idea per slide, one number
per slide, and the number is the biggest object on the page.

---

## Part 1 — The seven rules

Read these before you open PowerPoint. They are what separate this deck from the
other forty in the room.

1. **One number per slide, and it is huge.** 120pt minimum on the two hero slides. A slide with two competing numbers has none.
2. **One accent colour, used once per slide.** Sodium amber `#F2A93B`. Used four times it stops being an accent and becomes decoration.
3. **Uncertainty is a texture, never a colour.** Low confidence = 45° hatch, ~35% opacity, no solid fill. This is the single most important visual decision in the deck. Every honesty claim in the pitch rests on it being visible. If a generated screen flattens it into a pale colour, fix the screen before you screenshot it.
4. **Never red/green for darkness.** The light→dark comparison is exactly the one deuteranopia breaks. Use the ramp in Part 2.
5. **Real screenshots only.** No phone-bezel mockup frames, no Lorem, no invented street names. Every street name on a slide is a real Bengaluru street from `out/segments.geojson`.
6. **Every source cited, 13pt muted, bottom edge.** A number without a source reads as invented, even when it isn't.
7. **Say the limitation before the judge finds it.** Three slides do this deliberately (13, 15, and the fine print on 9). Volunteering costs a sentence and buys the whole room.

### Global do-not list

- **No accent line under the title.** Instant AI-slide tell. Use whitespace.
- **No stock skyline photo.** Not on the title slide, not anywhere.
- **No VIIRS nightlights raster.** Half the teams in this track will have one. It is 500 m per pixel — five to ten city blocks — so it physically cannot tell you a street is dark. We say so on slide 15 as a differentiator. Putting one on a slide destroys that.
- **No neon-on-black, glowing hexagons, wireframe globes, or dashboard gauges.** "Smart city" visual cliché. The reference is a well-printed infrastructure report that happens to be on a black page.
- **No donut charts. No 3D anything. No gradients on text.**
- **No word "leverage", "revolutionise", "AI-powered", or "one-stop solution."** There is no LLM in this project and claiming one invites a question you lose.
- **No centred body text.** Titles centre. Paragraphs and lists left-align.
- **No slide that is title + bullets with no visual.**
- **Do not put 24 hours / hackathon / "we only had one night" anywhere.** Judges know. It reads as pre-apologising.
- **Do not say BBMP is failing.** Slide 3 exists specifically to not say that.

---

## Part 2 — Visual system

### Palette

| Role | Hex | Where |
|---|---|---|
| Ink | `#0B0E14` | every slide background |
| Surface | `#141A24` | cards, table fills, code blocks |
| Hairline | `#252C3A` | 1px rules, table borders |
| Text | `#E8EBF0` | headings, body |
| Muted | `#8A94A6` | captions, sources, axis labels |
| **Sodium** | `#F2A93B` | the accent — hero numbers, one highlight per slide |
| Sodium dim | `#8A6224` | secondary marks on the same scale |
| Cool dark | `#3B4A7A` | the "dark street" end of the map ramp |

Sodium amber is the colour of a working streetlight. That is why it is the
accent — it is the colour of the thing the project is about.

**Darkness ramp** (sequential, lit → dark):
`#FDE9C4` → `#F2A93B` → `#A85D2B` → `#5C3A5E` → `#2B2F6B`

**Uncertainty**: 45° hatch, `#8A94A6` at 35% opacity, no fill. In PowerPoint:
Shape Fill → Pattern Fill → wide upward diagonal, foreground muted, background none.

### Type

| Element | Font | Size |
|---|---|---|
| Slide title | Archivo / Inter Tight 600, tracking −2% | 40pt |
| Subhead | same, 600 | 24pt |
| Body | Inter 400 | 18pt |
| Caption / source | Inter 400, muted | 13pt |
| **Hero number** | same family, 700, tabular figures | **120pt+** |

PowerPoint-safe fallback: **Segoe UI Semibold** headings, **Segoe UI** body. If
Archivo and Inter aren't installed on the presenting machine, use the fallback —
a missing font substitution mid-pitch looks worse than a plain one.

Nothing a judge is meant to read goes below 18pt.

### Layout

12-column grid, 64px (0.67") margins. Two templates only:

- **Number slide** — hero number centred, one sentence beneath, source at the bottom edge, nothing else on the page. Slides 2, 3, 9.
- **Split slide** — 5 columns text left, 7 columns visual right. Everything else.

Alternate them. Three split slides in a row and the deck goes flat.

---

## Part 3 — The slides

Copy the blockquoted text verbatim. `[VISUAL]` tells you what to put on the
right. `[SOURCE]` is the 13pt muted line. `[SAY]` is the speaker note — it does
not go on the slide.

---

### Slide 1 · Title

**Title:** Roshni

**Subtitle:**
> The streetlight repair queue, reordered by who is actually walking.

**Footer line, muted:**
> Problem Statement 17 · Smart Cities: Night-Safety Dark-Zone Mapper · Bengaluru

`[VISUAL]` Plain ink. If — and only if — someone on the team took a photograph of
a dark Bengaluru street, use it at 25% opacity behind the ink. A photo you took
yourselves is worth a lot here. A stock photo is worth less than nothing.

`[SAY]` Read the subtitle out loud as your first sentence. Don't introduce
yourselves first — lead with the idea.

**DO NOT** put team names, college name, or a logo wall on this slide. Put those
on the last slide if the submission format demands them.

---

### Slide 2 · The problem, in their own number

**Title:** Bengaluru's most-filed complaint

**Hero number:** `31.4%`

**Body:**
> Of the **126,974** civic complaints Bengaluru filed between 1 January and
> 19 June 2025, **39,847 — 31.4%, about 236 a day — were "Street Light Not
> Working."**
>
> The single largest complaint category in the city. Garbage is second, at 16,137.

`[VISUAL]` Horizontal bar chart, top 5 sub-categories, descending. Bar 1 amber,
bars 2–5 sodium dim. Values: Street Light Not Working 39,847 · Garbage dump
16,137 · Garbage vehicle not arrived 12,135 · Sweeping not done 3,641 · Road side
drains 3,269.

`[SOURCE]` BBMP grievance register, 1 Jan – 19 Jun 2025, via OpenCity. Recomputed
from the raw CSV, 22 Aug 2026. n = 126,974.

`[SAY]` "This is their number, not ours — and we recomputed it from the raw
register rather than citing an analysis of it."

**DO NOT** round to "about a third" — the precision is the point.

---

### Slide 3 · The reframe

**Title:** They are not failing. They are being handed the wrong order.

**Hero number:** `96.4%`

**Body:**
> BBMP closes **96.4%** of electrical complaints — 40,632 of 42,138. Road
> maintenance closes 58%.
>
> They are not slow, not under-resourced, and not failing at execution.
>
> **The queue is sorted by who complained first.**

`[VISUAL]` Two bars, same axis: Electrical 96.4% (amber) · Road Maintenance 58.0%
(sodium dim). Nothing else. The contrast is the visual.

`[SOURCE]` Same register, `Grievance Status` field.

`[SAY]` This is the most important slide in the deck for a government judge.
Never open by criticising the municipality — they will resent it and the data
does not support it. The move is: *an efficient execution machine is being handed
the wrong order.* Say that phrase.

**DO NOT** use the words "broken", "failure", "apathy", or "negligence" anywhere
on this slide.

---

### Slide 4 · Who complains is not who is exposed

**Title:** Complaining correlates with app-literacy, not exposure

**Body:**
> Streetlight complaints concentrate in **Jnanabharathi 1,345 · Ullalu 1,026 ·
> Hemmigepura 983 · Dodda Bidarkallu 967 · Rajarajeshwari Nagar 964** — newer,
> peripheral, more car-owning, more app-literate wards.
>
> Older, denser, more-walked inner wards file fewer. Not because their lights
> work.
>
> **A first-come queue is sorted by who complains, not by who is exposed.**

`[VISUAL]` Ward map of Bengaluru, complaint volume as circle area, amber circles
on ink, ward hairlines in `#252C3A`. Boundary file: `data/raw/bbmp_wards_2015.kml`
(198-ward vintage). Label only the five named wards. If you cannot build a map,
use a horizontal bar chart of the same five — a bad map is worse than a good bar
chart.

`[SOURCE]` Same register, filtered `Sub Category = "Street Light Not Working"`,
grouped by `Ward Name`. 198 wards present.

`[SAY]` "Peripheral, newer, more app-literate. The person on a dark arterial at
eleven at night is not the person filing the ticket."

**TWO TRAPS ON THIS SLIDE.** Both will get you caught.

1. **Use the streetlight-only counts above.** Earlier drafts of our own docs quoted Horamavu 3,128 / Jnanabharathi 2,842 / Thanisandra 2,480 — those are **all-category** complaint counts, a different measurement. Do not mix the two bases on one slide. If you want the all-category framing, label it explicitly.
2. **Do not claim complaint timestamps prove people file in the morning.** We tried to verify it and the field cannot support it: `Grievance Date` is a **12-hour clock with AM/PM stripped**, so all 126,974 rows fall in hours 1–12 and 7am is indistinguishable from 7pm. The ward pattern carries the argument on its own. If a judge asks about timing, say exactly that — "the field is 12-hour, we checked, we can't claim it."

---

### Slide 5 · What we build

**Title:** Three surfaces, one atom

**Body — three cards, icon in an amber circle each:**

| | |
|---|---|
| **Queue** · municipal | A ranked worklist under a repair budget. **The hero.** |
| **Route** · citizen | Safer and shortest walking route, side by side, always both. |
| **Report** · citizen | One tap: "this stretch is dark." |

**Pull quote, below the cards:**
> The atom is the **road segment**, not the lamp. A pedestrian at 23:00 does not
> care whether a street has eleven lamps or fourteen — they care whether the next
> 200 metres is lit.
>
> Darkness per segment is a quantity you can **estimate**. Lamp inventory is an
> enumeration you cannot **obtain**. Choosing the estimable quantity is why the
> missing inventory stops being fatal.

`[VISUAL]` The three cards are the visual. Keep them equal width, 0.4" gaps.

`[SAY]` "One modelling decision does most of the work here, and it's this one."

---

### Slide 6 · Architecture

**Title:** How it works

`[VISUAL]` Full-page diagram, redrawn cleanly. Hairline boxes on ink. Amber only
on the two output arrows and on the word DARKNESS. The IUDX arrow is **dashed**.

```
   OSM walk graph ─────┐
   BMTC GTFS ──────────┤                          ┌──► TRIAGE  ──► municipal queue
   (night departures)  ├──► EXPOSURE  E(seg) ─────┤    knapsack under budget
   night-active POIs ──┤         │                │    + counterfactual
   edge betweenness ───┘         │ opposite signs └──► ROUTING ──► safer route
                                 │                     weighted walk graph
   ward lamp density ──┐         │
   OSM working=yes/no ─┼──► DARKNESS  Beta(α,β) ──────► confidence band
   lit=yes / lit=no ───┤     mean = P(dark)                    │
   citizen reports ────┤     var  = uncertainty                ▼
   IUDX telemetry ┄┄┄┄┄┘                            REPORT TARGETING
    (gated)                                         exposure × variance
```

Three things to say over it, in this order:

1. **Two models, four products.** Darkness and exposure are estimated separately; four different outputs consume them.
2. **Uncertainty is a first-class output**, not a footnote. Posterior variance drives the routing refusal and the report targeting.
3. **The dashed arrow is gated.** Everything works without it, and nothing needs rewriting when it opens — slide 14.

`[SAY]` Ten seconds per numbered point. Do not walk the boxes left to right; a
judge reads the diagram faster than you can narrate it.

**DO NOT** add boxes for things we did not build. No "ML model", no "cloud", no
"blockchain layer", no user-auth box. Every box on this diagram exists in
`data/pipeline.py`.

---

### Slide 7 · The darkness model is calibrated, not asserted

**Title:** We didn't pick these numbers. We measured them.

**Body — left column, the transition matrix:**

Vasanthanagar citizen lamp audit, 469 individually coded lamps, two dates
15 days apart, June–July 2019:

```
                     2 July
   17 June      DEAD   OK
   DEAD           33    28    →  45.9% of dead lamps repaired in 15 days
   OK             15   360    →   4.0% of working lamps died in 15 days
```

> Equilibrium dead share = 0.040 / (0.040 + 0.459) = **8.0%**

**Right column, the prior:**

```
P(lit)  = coverage × 0.920
          coverage = ward lamps per km ÷ 33.3
          33.3 lamps/km  = 30 m standard pole spacing
          0.920          = measured working rate, left
Beta(α₀, β₀) = (K·P(lit), K·(1−P(lit)))     K = 2, deliberately weak
```

**The line that earns the slide, in amber:**
> Before calibration the model called **71% of segments dark**. After: **21.4%**.

`[SOURCE]` OpenCity — Vasanthanagar streetlights database 2019, citizen audit,
469 rows.

`[SAY]` "We caught our own model producing an indefensible number and fixed it
against a measured failure rate. Both numbers are on the slide on purpose."

Then, if there is time: evidence updates α and β — `working=yes/no` at weight
1.0, `lit=no` at 0.8, corroborated citizen report at 1.0, IUDX zero-current-after-dusk
at 2.0 — each decayed with a 30-day half-life, so the model stays live and a
confirmed repair genuinely clears a segment.

**DO NOT** cut the "71% → 21.4%" line to save space. Showing that you audited
your own output is worth more than the corrected number alone.

---

### Slide 8 · The duality

**Title:** One variable, opposite signs

**Body:**
```
repair_priority = E · P(dark) · confidence               E multiplies  → exposure
route_penalty   = L · (1 + λd·P(dark) + λe/E + λu·var)   E divides     → protection
```

> Footfall is **exposure** in the repair queue — more people at risk on a dark
> street, so fix it first. It is **protection** in the router — eyes on the
> street, so prefer it.
>
> Same variable, opposite sign, depending on which surface consumes it.
>
> Use it with one sign in both and your router confidently sends a woman down an
> empty, brightly lit industrial road at 01:00.

`[VISUAL]` Two small side-by-side illustrations: left, a dark busy street marked
"repair first"; right, a lit empty street marked "do not call this safe". Amber
on the labels only.

`[SOURCE]` Jane Jacobs, *The Death and Life of Great American Cities*, 1961 —
eyes on the street.

`[SAY]` This is the strongest intellectual slide in the deck and it costs nothing
but clear thinking. Most teams will use footfall with one sign in both places and
won't notice. Cite Jacobs by name — it lands.

---

### Slide 9 · The counterfactual — the number the deck lands on

**Title:** Same crew. Same budget. Different order.

**Hero number:** `7.7×`

**Body:**
> A crew can complete 40 repairs this week. Roshni's 40 restore **7.7× the
> exposed pedestrian-kilometres** that the complaint queue's first 40 restore.

**Fine print beneath, muted — volunteered, not extracted:**
> The grievance file has no coordinates and no pole IDs. A complaint names a
> **ward**, never a street. So the baseline is Monte-Carlo'd over 300 draws:
> wards in complaint order, target inside the ward unknown. 7.7× is the mean.
> Against the luckiest of the 300 draws: **4.9×**. Against a steelman BBMP that
> somehow picks the single worst segment in every ward it visits — which a
> coordinate-free complaint log cannot do — **still 1.9×**.
>
> And the robustness check, volunteered: restricted to the wards where we
> actually hold lamp labels, **6.4×**. With every lamp label deleted and the
> ranking built on the ward prior and exposure alone, **5.4×**. The win survives
> throwing away our own best data.
>
> **The gain is not from being cleverer inside a ward. It is from visiting the
> right wards.**

`[VISUAL]` Two stacked horizontal bars, same axis: "Roshni's 40" = 4,544 (amber),
"Complaint order's 40" = 588 (sodium dim), with a thin P5–P95 whisker on the
second bar (461 → 735) and a hairline tick at the steelman value 2,410, labelled.
The whisker is what makes it look measured rather than asserted.

`[SOURCE]` 11,029 segments, 1,180 km, 33 wards, the locked ORR demo bbox.
Objective Σ exposure × P(dark) × length. 300 Monte-Carlo draws. `out/stats.json`.

`[SAY]` Land on the number, pause, then give the fine print **before anyone asks
for it**. The last sentence is the thesis of the whole project — say it slowly.

**THIS SLIDE IS THE PRODUCT.** If you have to cut slides for a time limit, cut
around this one. Never cut this one.

**DO NOT** quote 7.7× on its own without the steelman. A sharp judge will say
"you're just beating random", and if you have already said 1.9× — and then the
5.4× with our own labels deleted — you win that exchange instead of losing it.

---

### Slide 10 · Prototype — the queue

**Title:** The municipal queue

`[VISUAL]` Full-bleed screenshot, three amber callouts.

Must be visible in the shot:
- the hero ratio in large type
- the budget slider
- the ranked worklist with **real Bengaluru street names**
- **at least one hatched low-confidence row**

Callouts: (1) the ratio · (2) "municipal priorities" sliders — *the municipality
owns these weights, not us* · (3) the hatched row — *we do not know this street,
and we say so*.

**Caption:** Live in the browser. The sliders recompute the knapsack client-side
— no network call on the demo path.

`[SAY]` "This is the screen a BBMP executive engineer would open on a Monday."

**DO NOT** screenshot a version whose sliders are decorative. If they don't
recompute, don't claim they do.

---

### Slide 11 · Prototype — the route

**Title:** Both routes. Always.

`[VISUAL]` Screenshot with both polylines and the comparison strip visible.

Must be visible:
- two visibly different routes
- distance and time for each
- the lit/dark proportion bar
- a hatched segment that the safer route **goes around**

**Caption:** Advisory, never a guarantee. The safer route refuses to path through
segments we are not confident about.

**The measured numbers for the demo route** (`out/routes.json`, query 1):
> Shortest: 1,575 m, **63% of it across ground we are not confident about.**
> Safer: 2,021 m, **7% unknown** — it routes around 18 low-confidence segments.
> Cost of the choice: **+446 m, about six minutes.**

"Six minutes to walk on ground we actually have data for" is the sentence.

**Then the finding that reframes the whole product — say this one slowly.**
We ran a bypass test on the 25 worst segments in the corridor: delete the
segment, look for another way between its endpoints.
> **Six of them have no walkable alternative at all.** Nineteen have a bypass
> more than three times the segment's length. Median **17.9×**. One 167 m dark
> service road on the Outer Ring Road has exactly one alternative and it is
> **23 kilometres.**
>
> On the streets that most need fixing, **there is nowhere else to walk.
> Routing cannot solve them. Only repair can.**

That is the measured answer to "why not just build a safer-route app", and it is
why the queue is the hero screen and this one is secondary.

`[SAY]` Say the duality out loud here on real geography: **Haralur Road in
Bellandur** carries the widest confidence band in our whole corridor — no mapped
lamps, almost no night bus service, and zero streetlight complaints in the ward
file. The router will not send you down it. The report screen sends you *to* it.

**DO NOT** auto-select the safer route or hide the shortest one. The product
position on liability is that the choice is the user's, and the screenshot has to
show that.

---

### Slide 12 · Prototype — the report, and the cold start

**Title:** The empty state is the feature

`[VISUAL]` Screenshot of the report screen's empty state.

**Body:**
> The empty state is not "no reports yet." It is **"streets worth checking
> tonight"** — ranked by exposure × uncertainty. The app **directs** reporting
> instead of waiting for it.
>
> **94% of our 11,029 segments have no lamp evidence at all** and run on the ward
> prior alone. That is not a flaw we are hiding — it is why every segment carries
> a variance, and it is what this screen is for. A report is worth most exactly
> where we are least sure and most people walk.

**Caption:** Day zero. No inventory, no reports — and the map is already useful,
and already honest about where it isn't.

**The learning curve, measured** (`out/curve.json`, simulation — label it as one):
> With **zero reports**, the prior-only ranking already captures **56%** of what a
> perfectly-informed ranking would restore. **400 targeted reports takes it to 76%.
> 400 random reports only reach 63%.**
>
> And say how we got there, because it is a better story than the curve. Our
> first targeting rule asked about the streets we knew *least* — highest
> uncertainty. Measured, it **lost to picking streets at random.** Those streets
> are mostly ones no repair crew would ever be sent to. The rule that works asks
> about streets whose *optimistic* darkness estimate would put them in the repair
> queue if it turned out true. Same screen, different question, and it beats
> random from ten reports on.

`[SOURCE]` 690 of 11,029 segments carry any OSM lamp evidence. `out/stats.json`,
`out/curve.json`.

`[SAY]` This slide pre-answers the hardest question we get — "what does it do on
day one with no data" — before it is asked.

---

### Slide 13 · Validation — the challenge question

**Title:** How would you validate a footfall estimate with no official data?

**Two structural points first, and they matter more than the table:**
> **One.** Validation needs a signal you did **not** use to build the estimate.
> Build an index from POI density and "validate" it against POI density and the
> circularity is visible in ten seconds.
>
> **Two.** You are validating an **ordering**, not a magnitude. "412 pedestrians
> per hour" is unfalsifiable. "These streets rank above those" is checkable.

**Then the four layers:**

| Layer | Method | Result |
|---|---|---|
| **Convergent** | activity estimate vs structural estimate, Spearman ρ | **ρ = +0.30**, and +0.44 vs night bus departures. Passes — but read the story below |
| **Criterion** | risk score vs night pedestrian crashes — never enters the model | **not yet measured** |
| **Ground truth** | 8 stratified segments, 5-min counts at 21:30, rank correlation | **not yet measured** |
| **Transfer** | fit where data exists, apply where it doesn't, report degradation | designed; degradation not quantified |

**The line to say — and it is a sequence, not a number. Rehearse it.**
> We ran convergent validation and the first answer was **ρ = 0.03. A null.**
> Two proxies that should have agreed didn't.
>
> So instead of publishing it we went looking for why — and found the bug. We
> were keying our walk graph on rounded coordinates, so junctions where two
> roads genuinely meet weren't merging. Our network had shattered into
> disconnected fragments and the betweenness centrality we were feeding the
> model was computed over **55%** of the city. Half our structural signal was
> noise.
>
> Fixed it — keyed the graph on OSM node ids instead — and re-ran over eight
> times the area. **98.4% of the network now connects, and the two disjoint
> proxies converge at ρ = 0.30, and 0.44 against night bus departures.**
>
> Two proxies built from completely unrelated inputs — one from night commerce,
> one from pure network topology plus bus service — do not agree at 0.30 by
> accident. That is real convergent evidence. It is also a number we only
> deserve because we didn't ship the first one.

**One honesty note to carry, in case you are asked about the weights.** The
exposure blend leans structural at 0.75. On the broken numbers that looked like
a *finding*. On the corrected numbers it is a **choice**, made because the
problem statement names late-night commuters. Call it a choice. It is still the
right one, and it is a slider.

**Then the two cheap things nobody else does:**
- **Negative controls.** An industrial cul-de-sac at 01:00 must score near zero. A stretch outside a bus terminus at 22:00 must score high. A gated-layout internal road must score low on through-movement and moderate on residential. Fifteen minutes, and they catch the class of bug a correlation coefficient hides.
- **Uncertainty as a control signal.** Every other team renders one confident number per street. We render a band, and the band *does* something: the router refuses wide bands, the report screen targets them.

**One number on this slide nobody else will have:**
> BMTC's GTFS export carries every departure time, so night service is directly
> countable. In our bbox: **405 stops, 6,187 departures at or after 21:00 — 6.1%
> of daily service — and 119 of those 405 stops have no night service at all.**
> Where the night buses stop, people walk, and nobody is counting them.

`[VISUAL]` **Two scatter plots side by side, both from real data.** Left: the
broken run — activity rank vs structural rank, 1,164 points, flat, "ρ = 0.03",
labelled *55% of the network connected*. Right: the corrected run — 11,029
points, visible positive slope, "ρ = 0.30", labelled *98.4% connected*.

Two plots and an arrow between them is the most persuasive object in this deck.
It is the only slide that shows the team debugging itself.

`[SOURCE]` `out/stats.json`; `data/pipeline.py`; BMTC GTFS via Vonter/bmtc-gtfs.

`[SAY]` This is the slide the problem author cares about — the challenge
question is about validation, not features, and that is them telling you where
the marks are. Lead with the null, then the bug, then the corrected number. A
team that gets a null, distrusts it, finds its own bug and re-runs is doing
science. A team that just shows you a good correlation is asking to be trusted.

**DO NOT** hide the first number. The 0.03 is the point of the slide — it is
what makes the 0.30 believable. Showing only the good number throws away the
whole argument and reads like every other deck.

**DO NOT** claim the criterion or ground-truth rows are done if they aren't. Say
"not yet measured" on the slide. If someone gets the crash PDFs mined or the
field count done before submission, replace the row and say so.

---

### Slide 14 · The data — what we have, what is gated

**Title:** The data exists. It's one approval away.

**Left column — have, open, in hand:**
- 126,974 grievances for 2025, six years available
- **1,211 mapped lamps** in the demo bbox; **1,080 of them labelled `working=yes/no`**
- per-lamp KML for the ORR corridor and Bellandur/HSR
- lamp counts for all 198 wards — **421,113 lamps**
- BMTC GTFS with per-stop departure times
- a two-date citizen lamp audit
- night pedestrian crash reports

**Right column — gated, catalogued, one approval away:**

IUDX dataset `9b27c09f-1ec6-4acd-89f0-a27f23184017`, published by the Electronics
City Industrial Township Authority: *"Streetlights Location Info in Electronic
City, Bengaluru"*, with an hourly current-and-voltage companion resource. Marked
**Private**. The sample record is public:

```json
{"deviceID": "L0302",
 "location": {"type": "Point", "coordinates": [77.666046, 12.841758]}}
```

**The positioning, verbatim:**
> Ninety-three Indian cities publish streetlight **counts** through MoHUA's Smart
> Cities portal. **Zero publish coordinates** — the D24 template is a KPI return,
> not an asset register. The pole-level geometry is on IUDX, for our city,
> published by the local authority, marked private.
>
> So Roshni's internal lamp record **is** `{deviceID, location: GeoJSON Point}`
> and its telemetry record **is** `{deviceID, observationDateTime, current,
> voltage}` — copied verbatim from IUDX. "We plug into the municipal feed the day
> access is granted" is not a promise, it is a schema fact. When it opens, the
> darkness prior is replaced by measurement and the bands collapse. The queue,
> the exposure model, the knapsack and all three screens are unchanged.

**One line worth saying, because it is the fragmentation story in miniature:**
> The IUDX feed covers Electronic City, which has **4** lamps mapped in OSM. OSM
> covers the ORR corridor, which has **1,211**. The two datasets cover adjacent,
> non-overlapping ground.

`[VISUAL]` Screenshot of the IUDX resource page, cropped to show the
`Request Resource` button on the left and the sample record on the right. If you
cannot get a clean screenshot, set the JSON in a `#141A24` code block and put the
dataset ID above it in muted grey.

`[SAY]` End this slide on "our ask is that someone approves the request." It
reframes the missing data from a weakness into a call to action, and it is true.

---

### Slide 15 · What we know we get wrong

**Title:** Four things we get wrong, on purpose, out loud

> **94% of our 11,029 segments have no lamp evidence** and run on a ward-level
> prior alone. Every one of them carries a confidence band that says so, the
> router avoids the least-certain fifth of the network, and the report screen
> targets them. But it means most of the map is an estimate, and we would rather
> say that than have you find it.
>
> **Our labelled lamps are geographically concentrated.** OSM's
> working/not-working tags come from citizen surveys, and those surveys walked
> some wards and not others — which is why our top forty repairs cluster. We
> tested whether that flatters the result: restricted to the surveyed wards it
> is 6.4×, and with every lamp label deleted it is 5.4×. It survives. But the
> concentration is real and it shapes which streets we can be confident about.
>
> **OSM records `opening_hours` for 6.7% of POIs** in our corridor — 78 of 1,157.
> So we cannot filter night activity by closing hour as designed; we weight by POI
> class instead. And Google's review counts, which we do not have, undercount
> thelas and tea stalls — exactly the population most exposed to dark streets.
>
> **The `working` tags are survey-biased.** 657 broken to 471 working in our
> snapshot is a property of who went out mapping, not the outage rate of
> Bengaluru. We use them as labels, never as a base rate.
>
> **Tree canopy** is a large effect on how lit a Bengaluru street feels and we
> have no data for it at all. **Footpath existence** is the same story — a lit road
> with no walkable footpath is not a safe pedestrian route, and OSM `sidewalk`
> coverage here is thin.

**And one line that buys a lot:**
> VIIRS nighttime lights are 500 m per pixel — five to ten city blocks — so they
> cannot tell you a street is dark. We do not use them that way.

`[VISUAL]` Four numbered rows, each with its number in an amber circle. No chart.
This slide is text and it is allowed to be.

`[SAY]` Volunteering a limitation is worth more than defending one. Say all four
briskly — thirty seconds total — and do not dwell. The tone is command of the
material, not confession.

---

### Slide 16 · What's next, and the ask

**Title:** What another week buys

Answer this with what you would try to **learn**, not with features.

> - Mine the Bengaluru Traffic Police crash reports and close the criterion-validation leg.
> - Field pedestrian counts on stratified segments — is the ordering right?
> - Fit the transfer model across wards of genuinely different urban form and report the degradation honestly. Where it does not transfer, the system should refuse to guess and ask for a report instead — that behaviour is already built.
> - Instrument the resolution loop. **BBMP closes 96.4% of electrical complaints, and Roshni is the first thing that can ask *closed, or fixed?*** A ward line reading "11% of closures were not verified by anyone on the ground" is a metric a commissioner does not have today and would want immediately. One table and a notification.

**The ask, last thing on the screen, amber:**
> The data exists, for our city, one approval away, and we already speak its
> schema. **Approve the IUDX request.**

**Then the number, one more time:** `7.7×`

`[SAY]` First number they hear and the last. Close on it and stop talking.

**DO NOT** answer "what's next" with a feature list. Every team does. Answering
with what you'd try to *learn* is the differentiator, and it is the last thing
they hear before scoring.

---

## Part 4 — Asset checklist

Tick these off. The deck is not finished until every row is done or deliberately
dropped.

| # | Asset | Slide | Where it comes from | Status |
|---|---|---|---|---|
| 1 | Top-5 complaint bar chart | 2 | numbers in this file | — |
| 2 | Closure-rate two-bar chart | 3 | numbers in this file | — |
| 3 | Ward complaint map or bar chart | 4 | `data/raw/bbmp_wards_2015.kml` + counts here | — |
| 4 | Architecture diagram, redrawn | 6 | ASCII in slide 6 | — |
| 5 | Transition matrix table | 7 | numbers in this file | — |
| 6 | Duality illustration, two panels | 8 | draw it | — |
| 7 | Counterfactual bar + whisker | 9 | `out/stats.json` | — |
| 8 | **Queue screenshot** | 10 | `docs/prompts.md` Prompt 1 + `out/segments.fixture.geojson` | — |
| 9 | **Route screenshot** | 11 | `docs/prompts.md` Prompt 3 | — |
| 10 | **Report empty-state screenshot** | 12 | `docs/prompts.md` Prompt 2 | — |
| 11 | ρ scatter plot | 13 | `out/segments.geojson`, activity vs structural | — |
| 11b | Learning curve, two lines | 12 or 13 | `out/curve.json` — targeted vs random, annotate the ~50-report crossover | — |
| 12 | IUDX page screenshot | 14 | iudx.org.in catalogue, dataset ID in slide 14 | — |
| 13 | Night-street photograph, ours | 1 | someone's phone | optional |
| 14 | Photo of the team counting pedestrians | 13 | one evening | optional, high value |

Rows 8–10 are the prototype glimpses and they are the ones judges remember.
Rows 13–14 are optional but a real photograph beats any graphic on the slide it
sits on.

---

## Part 5 — Where every number came from

If a judge asks "where did that come from", these are the answers.

| Number | Source | Command |
|---|---|---|
| 126,974 · 39,847 · 31.38% · 236/day | `data/raw/bbmp_grievances_2025.csv` | filter `Sub Category == "Street Light Not Working"` |
| 96.4% · 58.0% | same file | `groupby("Category")["Grievance Status"]` |
| Ward counts | same file | streetlight rows only, `groupby("Ward Name")` |
| 1,211 · 5,874 · 1,173 · 1,080 · 303 · 630 · 1,885 · 4 | OpenStreetMap via Overpass | `data/overpass.md` |
| 421,113 lamps, 198 wards | `data/raw/streetlights_by_ward.csv` | sum the count column |
| 469 lamps · 4.0% · 45.9% · 8.0% | `data/raw/streetlights_vasanthanagar_2019.csv` | crosstab the two condition columns |
| 405 stops · 101,367 · 6,187 · 6.1% · 119 | `data/raw/bmtc_stops.geojson`, `trip_list` | `data/derived_stops_bbox.json` |
| 7.73× · 4.88× · 1.89× | same | `out/stats.json` → `counterfactual.40` |
| 6.4× · 5.42× (robustness) | same | `out/stats.json` → `sensitivity` |
| 11,029 segments · 1,180 km · 33 wards · 690 with lamp evidence · 93.7% prior-only · mean P(dark) 0.276 | `data/pipeline.py` | `out/stats.json` |
| ρ +0.302 · +0.436 | same | same |
| bypass: 6 of 25 with no alternative · median 17.9× · worst 206.9× | `data/derive_screens.py` | `out/routes.json` → `noAlternative` |
| curve: 56% at zero reports · 76% targeted vs 63% random at 400 | same | `out/curve.json` |
| 1,157 POIs · 78 with hours · 6.7% | `data/derived_pois_subbbox.json` | count `opening_hours` |
| IUDX dataset ID and sample record | iudx.org.in catalogue | public resource page |
| 93 cities publish counts, zero coordinates | MoHUA Smart Cities portal, D24 template | `docs/national-data-landscape.md` |

Rounding convention for the deck: **7.7×** on the hero slide, **7.73×** in any
table. 31.4% on the hero, 31.38% in a table. Don't mix within one slide.

---

## Part 6 — Judge Q&A, one owner each

Assign a name to each and rehearse out loud, twice.

**"Where is your streetlight data?"**
1,211 mapped lamps in the bbox, 1,080 carrying a working/not-working label,
per-lamp KML for the corridor, counts for all 198 wards. Beyond that we estimate,
with a band. **BBMP's own records have no coordinates and no pole IDs** — we are
at parity with the municipality on day zero and ahead of it the moment a report
carries a GPS fix.

**"Your ratio is just an optimiser beating random."**
Partly — which is why we built the steelman. Same complaint-driven ward order,
but BBMP picks the single worst segment inside every ward it visits. It still
loses, 1.9×. And we checked the harder version of that objection: our labelled
lamps are concentrated in a few wards, so we re-ran restricted to those wards
(6.4×) and again with every lamp label deleted (5.4×). It survives both. The
gain is in *which wards get visited*, and that is set by the complaint log, not
by us.

**"Your weights are arbitrary."**
Two are sliders, because the municipality should own that choice, not us. The
darkness prior is calibrated against a measured failure rate. And the exposure
blend is set by a measurement — we ran the convergent check, it came back
ρ = 0.03, and that null result is *why* the structural half leads at 0.75.

**"Isn't a lit street always safer?"**
No — hence opposite signs in the two surfaces. The empirical literature is
genuinely mixed: a US randomised controlled trial found real reductions, a UK
study of local-authority switch-offs found no increase in crime or collisions. We
do not claim lighting causes safety. We claim exposure to darkness is a cost
worth ordering repairs by.

**"How much of this is synthetic?"**
Say it before they dig. Segments, lamps, complaints, ward counts, bus departures
and failure rates are all real and all recomputed on 22 August. Telemetry records
are synthetic, IUDX-shaped, and render differently in the UI. Then give the real
count of citizen reports the team filed — **if it is zero, say zero**, and say the
reporting loop is built and unseeded. A judge discovering synthetic data is fatal;
a judge being told about it is nothing.

**"What stops report spam?"**
Photo, GPS, timestamp, spatial dedupe, a confidence threshold before a report
moves the queue, per-device rate limiting. Structurally: one report never
reorders anything, because the posterior needs evidence to move.

**"How does this scale beyond Bengaluru?"**
It needs a road network, a boundary file, and any per-ward lamp count. The first
is universal; the other two exist for every corporation even when unpublished.
Production consumes the geotagged asset registers that already exist under
SLNP/ESCO street-lighting contracts and on IUDX. **We are not asking anyone to
survey anything new.**

**"Liability — you're telling a woman to walk down a specific road."**
Advisory, not a guarantee. Never route through zero-confidence segments. Always
show the shortest route beside the safer one so the choice is the user's.

**"Licensing?"**
OSM is ODbL — attribution and share-alike if anything ships publicly. Most
OpenCity resources carry "No License Provided": fair dealing for a
non-commercial prototype, production on a data-sharing agreement with BBMP.

**"What would another week get you?"**
Not features — the two unmeasured validation legs on slide 13, and the
resolution-loop instrumentation on slide 16.

---

## Part 7 — Generator prompts

If you are building the deck with a tool rather than by hand, paste one of these.

### 7a — Gamma / Beautiful.ai / Tome

Paste this, then replace the generated body copy with the verbatim text from
Part 3. These tools write filler; the slide *structure* is what you want from
them, not the words.

```
Build a 16-slide 16:9 pitch deck, dark theme throughout.

Design system — follow exactly:
- Background #0B0E14. Surfaces #141A24. Hairlines #252C3A.
- Text #E8EBF0. Muted #8A94A6.
- ONE accent, sodium amber #F2A93B, used exactly once per slide.
- Headings Archivo or Inter Tight 600, tracking -2%. Body Inter 400.
- Titles 40pt, body 18pt, captions 13pt, hero numbers 120pt+.
- Two layouts only, alternating: (a) hero-number slide — one giant number,
  one sentence, source line, nothing else; (b) split slide — text in 5
  columns left, visual in 7 columns right.
- NO accent line under any title. NO gradients on text. NO donut charts.
  NO 3D. NO neon or glowing effects. NO stock skyline photography.
- Tone reference: a well-printed civic infrastructure report that happens to
  be on a black page. Not a "smart city dashboard".

Slide titles in order:
1. Roshni — the streetlight repair queue, reordered by who is actually walking
2. Bengaluru's most-filed complaint  [hero number: 31.4%]
3. They are not failing. They are being handed the wrong order.  [hero: 96.4%]
4. Complaining correlates with app-literacy, not exposure
5. Three surfaces, one atom
6. How it works  [full-page architecture diagram]
7. We didn't pick these numbers. We measured them.
8. One variable, opposite signs
9. Same crew. Same budget. Different order.  [hero number: 5.2x]
10. The municipal queue  [full-bleed product screenshot]
11. Both routes. Always.  [product screenshot]
12. The empty state is the feature  [product screenshot]
13. How would you validate a footfall estimate with no official data?
14. The data exists. It's one approval away.
15. Four things we get wrong, on purpose, out loud
16. What another week buys  [ends on the number 5.2x]

Leave slides 10, 11 and 12 as empty full-bleed image frames with captions —
real product screenshots go there and must not be replaced with illustrations
or mockup phone frames.
```

### 7b — Claude / ChatGPT / Copilot, generating a build script

```
Read docs/ppt.md in this repo. Build the 16-slide deck it specifies as a
.pptx, 16:9, using the exact palette, type scale and two layout templates in
Part 2, and the verbatim slide copy in Part 3.

Rules:
- Copy the blockquoted body text verbatim. Do not paraphrase, do not shorten,
  do not "improve" the wording.
- Every [SOURCE] line becomes a 13pt muted text box at the bottom edge.
- [SAY] blocks become PowerPoint speaker notes, never on-slide text.
- Slides 10, 11, 12: full-bleed picture placeholders sized 13.33x7.5in with
  the caption below, ready for real screenshots.
- No accent rule lines under titles.
- Slide 13's chart is a scatter of 1,164 points from out/segments.geojson:
  exposure.activity on x, exposure.structural on y, muted points, amber trend
  line, "rho = 0.03" set large beside it.
- Slide 9's chart is two horizontal bars (2582 amber, 470 dim) with a
  P5-P95 whisker on the second (360 to 595) and a labelled tick at 1631.
Then render to images and visually check every slide for overflow, overlap
and low contrast before declaring it done.
```

### 7c — By hand in PowerPoint or Google Slides

Fastest reliable path if the tools fight you:

1. Set slide size 16:9. Set the theme background to `#0B0E14` on the slide master, text to `#E8EBF0`.
2. Build **two** layouts on the master — hero-number and split — then never build a third.
3. Do all sixteen slides text-only first, straight from Part 3. No visuals yet.
4. Then add visuals in the Part 4 checklist order. Charts in Google Sheets or matplotlib on the ink background, exported as PNG — native PowerPoint charts fight dark themes and lose.
5. Screenshots last, when the screens exist.
6. Then the QA pass in Part 8.

---

## Part 8 — QA before you submit

Do this. Assume there are problems; a first pass that finds nothing means you
weren't looking.

1. **Export to PDF and look at every slide at 100%.** Overlapping text, anything cut off at an edge, source lines colliding with content above, gaps under 0.3".
2. **Grep your own deck for dead claims.** Search the text for `office hour`, `225`, `Horamavu`, `800`, `half a million`, `303 bus`, `VIIRS`. Every one of those is a number or claim we corrected or killed. If any survives, fix it — Part 5 has the right value.
3. **Contrast check.** Muted `#8A94A6` on ink passes for captions. Do not go lighter on the background or darker on the text.
4. **The hatch test.** Open slides 10–12. Can you tell, at a glance, which rows and segments are low-confidence? If not, the honesty argument is invisible and the screenshots need redoing.
5. **Count the accents.** One amber element per slide. If a slide has three, two of them are decoration.
6. **Read slide 9 out loud, timed.** Hero number, pause, fine print, the last sentence. Under thirty seconds.
7. **Present it once to someone who has not seen it,** and have them play hostile judge with Part 6.
8. **Export a PDF backup and put it on a USB stick.** Also record a screen capture of a clean prototype run, and rehearse switching to the recording once, so if the wifi dies it doesn't look like panic.

---

## Part 9 — Still unmeasured

Three things in this deck are not computed. They are marked "not yet measured" on
slide 13 and in the Q&A. Do not let them silently become claims.

1. **Criterion validation** against night pedestrian crashes. `data/raw/btp_road_safety_2023.pdf` and `btp_crashes_2024.pdf` are downloaded and unmined. Highest-value remaining task on the whole project, and it needs a highlighter, not a parser: find the night pedestrian casualty split and any named blackspots inside or near the demo bbox.
2. **Ground-truth pedestrian counts.** Eight stratified segments — two the model scores high, three medium, three low — five-minute counts at 21:30, plus a photograph of the team counting. Report **Spearman** ρ, not Pearson; at n=8 a rank statistic is the only defensible choice.
3. **The team's own seed reports.** However many real reports you filed. If zero, say zero.

If none of the three lands before submission, say so on slide 13. A deck that
names its three open measurements reads stronger than one a judge catches out on
a single soft claim.
