# Deck outline — Roshni

**Selection is on the deck.** This file is the build spec for it: visual system,
slide-by-slide content with the real numbers already in place, the architecture
diagrams to redraw, which prototype screenshots to capture, the reference list,
and the Q&A appendix.

Every number here is measured — see `docs/measured-2026-08-22.md` for the run
log. Nothing below needs verifying before it goes on a slide. Numbers that are
still unmeasured are marked **[UNMEASURED]** and there are only three.

**16 slides, 16:9.** Judges skim. One idea per slide, one number per slide, and
the number is the biggest thing on it.

---

## Part 1 — Visual system

The deck is about darkness. It should be dark. Not "smart city dashboard" dark —
no neon, no glowing hexagons, no wireframe globes. Closer to a well-printed
infrastructure report that happens to be on a black page.

### Palette

| Role | Hex | Use |
|---|---|---|
| Ink (background) | `#0B0E14` | every slide background |
| Surface | `#141A24` | cards, table rows, code blocks |
| Hairline | `#252C3A` | 1px rules, table borders, dividers |
| Text | `#E8EBF0` | headings and body |
| Muted | `#8A94A6` | captions, sources, axis labels |
| **Sodium** | `#F2A93B` | the accent. The hero number, one highlight per slide, nothing else |
| Sodium dim | `#8A6224` | secondary marks on the same scale |
| Cool dark | `#3B4A7A` | the "dark street" end of the map ramp |

The accent is sodium-vapour amber on purpose — it is the colour of the thing the
project is about. Use it **once per slide**. An accent used four times is not an
accent.

**Darkness ramp** (sequential, light → dark; never red/green — the comparison
that matters would fail for deuteranopia):
`#FDE9C4 → #F2A93B → #A85D2B → #5C3A5E → #2B2F6B`

**Uncertainty is a texture, not a colour.** A wide confidence band renders as a
45° hatch at ~35% opacity with no solid fill, on the map and in the tables. This
is the single most important visual decision in the deck: it is what makes the
honesty visible instead of stated. If a slide flattens it into a plain colour
ramp, the slide is wrong.

### Type

- Headings: **Archivo** or **Inter Tight**, 600 weight, tight tracking (−2%).
  PowerPoint-safe fallback: Segoe UI Semibold.
- Body: **Inter** 400. Fallback: Segoe UI.
- Numbers: same family, tabular figures, 700 weight.
- Scale: slide title 40pt · subhead 24pt · body 18pt · caption 13pt ·
  **hero number 120pt+**.

Never below 18pt for anything a judge is meant to read. Sources go at 13pt in
muted grey along the bottom edge.

### Layout

12-column grid, 64px margins, generous. Two recurring templates:

- **Number slide** — hero number centred at 120pt+, one sentence under it,
  source line at the bottom. Nothing else on the page. Slides 2, 9.
- **Split slide** — 5 columns of text left, 7 of visual right. Everything else.

House rules: no bullet lists longer than four items; no slide with two competing
numbers; every data slide carries its source in muted grey; every screenshot is
a real screenshot of the real prototype, never a mockup frame with a phone
bezel round it.

---

## Part 2 — Slides

### 1 · Title

> **Roshni**
> The streetlight repair queue, reordered by who is actually walking.

Sub-line: Problem Statement 17 · Night-Safety Dark-Zone Mapper · Bengaluru.
Background: one dark photograph of a Bengaluru street at night if you have one
you took yourselves, at 25% opacity behind the ink. If you don't, plain ink.
Do not use a stock photo of a generic city skyline.

### 2 · The problem, in their own number

**Hero: 31.4%**

> Of the 126,974 civic complaints Bengaluru filed between 1 January and 19 June
> 2025, **39,847 — 31.4%, about 236 a day — were "Street Light Not Working."**
> The largest single complaint category in the city. Garbage is second, at 16,137.

Source: BBMP grievance register 2025, via OpenCity. Recomputed from the raw CSV.

Speaker note: this is their number, not ours, and we recomputed it rather than
citing a blog post about it.

### 3 · The reframe — the slide that decides whether they like you

**Hero: 96.4%**

> BBMP closes **96.4%** of electrical complaints. Road maintenance closes 58%.
> They are not slow, not under-resourced, and not failing.
>
> **They are being handed the queue in the wrong order.**

Speaker note: never open by criticising the municipality — a government judge
will resent it and the data does not support it. This slide is the difference
between "another team telling us we're broken" and "a team that read our data."

### 4 · Who complains is not who is exposed

Split slide. Left: the argument. Right: ward map, complaint volume as circle
area, over the ward boundaries.

> Streetlight complaints concentrate in **Jnanabharathi 1,345 · Ullalu 1,026 ·
> Hemmigepura 983 · Dodda Bidarkallu 967 · Rajarajeshwari Nagar 964** — newer,
> peripheral, more car-owning, more app-literate wards. Older, denser,
> more-walked inner wards file fewer. Not because their lights work.
>
> **A first-come queue is sorted by who complains, not by who is exposed.**

Source: same file, filtered to `Sub Category = "Street Light Not Working"`.

Two traps to avoid on this slide. Quote the **streetlight-only** counts above,
not the all-category ones (Horamavu 3,128 etc.) that earlier drafts carried —
they are a different measurement. And do **not** claim complaint timestamps
cluster in office hours: the grievance file's clock is 12-hour with AM/PM
stripped, so it is unknowable. The ward pattern carries the argument alone.

### 5 · What we build

Three surfaces, one shared atom.

| | |
|---|---|
| **Queue** (municipal) | ranked worklist under a repair budget — **the hero** |
| **Route** (citizen) | safer and shortest walking route, side by side, always both |
| **Report** (citizen) | one tap: "this stretch is dark" |

> The atom is the **road segment**, not the lamp. A pedestrian at 23:00 does not
> care whether a street has eleven lamps or fourteen — they care whether the next
> 200 metres is lit. Darkness per segment is a quantity you can *estimate*. Lamp
> inventory is an enumeration you cannot *obtain*. Picking the estimable quantity
> is why the missing inventory stops being fatal.

### 6 · Architecture

Full page, redrawn cleanly. Hairline boxes on ink, amber only on the two output
arrows.

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
   IUDX telemetry ─────┘                            REPORT TARGETING
    (gated)                                         exposure × variance
```

Three things to say over it, in this order:

1. **Two models, four outputs.** Darkness and exposure are estimated
   separately; four different products consume them.
2. **Uncertainty is a first-class output**, not a footnote. Posterior variance
   drives the routing refusal and the report targeting.
3. **The IUDX arrow is dashed.** It is gated. Everything works without it, and
   nothing has to be rewritten when it opens — slide 14.

### 7 · The darkness model is calibrated, not asserted

Split. Left: the transition matrix. Right: the formula and the before/after.

Vasanthanagar citizen audit, 469 individually coded lamps, two dates 15 days
apart, June–July 2019:

```
                     2 July
   17 June      DEAD   OK
   DEAD           33    28      →  45.9% of dead lamps repaired in 15 days
   OK             15   360      →   4.0% of working lamps died in 15 days
```

> Equilibrium dead share = 0.040 / (0.040 + 0.459) = **8.0%**.

So the prior is not a guess:

```
P(lit) = coverage × 0.920         coverage = ward lamps per km ÷ 33.3
                                  33.3 lamps/km = 30 m standard pole spacing
                                  0.920 = measured working rate, above
Beta(α₀, β₀) = (K·P(lit), K·(1−P(lit)))          K = 2, deliberately weak
```

**Before calibration the model called 71% of segments dark. After: 21.4%.**
Put both numbers on the slide. Showing that you caught your own implausible
output is worth more than the corrected number alone.

Evidence then updates α and β — `working=yes/no` tags at weight 1.0, `lit=no` at
0.8, a corroborated citizen report at 1.0, IUDX zero-current-after-dusk at 2.0 —
each decayed by age with a 30-day half-life, so the model stays live and a
confirmed repair genuinely clears a segment.

### 8 · The duality — one variable, opposite signs

The strongest intellectual slide in the deck, and it costs nothing but clear
thinking.

```
repair_priority = E · P(dark) · confidence          E multiplies  → exposure
route_penalty   = L · (1 + λd·P(dark) + λe/E + λu·var)   E divides → protection
```

> Footfall is **exposure** in the repair queue — more people at risk on a dark
> street, so fix it first. It is **protection** in the router — eyes on the
> street, so prefer it. Same variable, opposite sign, depending on which surface
> consumes it.
>
> Use it with one sign in both and your router confidently sends a woman down an
> empty, brightly lit industrial road at 01:00.

Cite Jacobs, *The Death and Life of Great American Cities*, 1961. It lands.

### 9 · The counterfactual — the number the deck lands on

**Hero: 5.2×**

> A crew can complete 40 repairs this week. Roshni's 40 restore **5.2× the
> exposed pedestrian-kilometres** that the complaint queue's first 40 restore.

Under it, in muted text, volunteered before anyone asks:

> The grievance file has no coordinates and no pole IDs — a complaint names a
> **ward**, never a street. So the baseline is Monte-Carlo'd over 300 draws:
> wards in complaint order, target inside the ward unknown. 5.2× is the mean.
> Against the luckiest of 300 draws: 3.5×. Against a steelman BBMP that somehow
> picks the single worst segment in every ward it visits — which a
> coordinate-free complaint log cannot do — **still 1.58×**.
>
> **The gain is not from being cleverer inside a ward. It is from visiting the
> right wards.**

Measured over 1,164 real segments, 160.9 km, 13 wards.
Objective: Σ exposure × P(dark) × length.

This slide is the product. Everything else in the deck is the interface to it.
If you cut slides for time, cut around this one.

### 10 · Prototype — the queue

Screenshot, full bleed, with three callouts in amber.

Must be visible in the shot: the hero ratio in large type, the budget slider,
the ranked worklist with real Bengaluru street names, and **at least one
hatched low-confidence row**. Callouts: (1) the ratio, (2) "municipal
priorities" sliders — *the municipality owns these weights, not us*, (3) the
hatched row — *we do not know this street; we say so*.

Caption: *live in the browser, no network call — the sliders recompute the
knapsack client-side.*

### 11 · Prototype — the route

Screenshot with both polylines visible and the comparison strip.

Must be visible: two visibly different routes, distance and time for each, the
lit/dark proportion bar, and a hatched segment the safer route **goes around**.

Caption: *both routes, always. Advisory, never a guarantee. The safer route
refuses to path through segments we are not confident about.*

Say the duality out loud here, on real geography: on our data **Haralur Road in
Bellandur** carries the widest confidence band in the corridor — no mapped lamps,
almost no night bus service, and zero streetlight complaints in the ward file.
The router will not route you down it. The report screen sends you to it.

### 12 · Prototype — the report, and the cold start

Screenshot of the empty state, which is the whole point.

> The empty state is not "no reports yet." It is **"streets worth checking
> tonight"** — ranked by exposure × uncertainty. The app *directs* reporting
> instead of waiting for it.

> **85% of our 1,164 segments have no lamp evidence at all** and run on the ward
> prior alone. That is not a flaw we are hiding — it is why every segment carries
> a variance, and it is what this screen is for. A report is worth most exactly
> where we are least sure and most people walk.

Caption: *day zero, no reports, no inventory — and the map is already useful and
already honest about where it isn't.*

### 13 · Validation — the challenge question

> *How would you validate a footfall estimate for a street where no official
> usage data exists at all?*

They asked about **validation**, not features. Two structural points first:

1. Validation needs a signal **you did not use to build the estimate.** Build an
   index from POI density and "validate" it against POI density and a judge
   names the circularity in ten seconds.
2. **You are validating an ordering, not a magnitude.** "412 pedestrians per
   hour" is unfalsifiable. "These streets rank above those" is checkable. Say
   this before you are asked.

Then the four layers — and lead with the one that failed, because it is the most
interesting thing in the deck:

| Layer | Method | Result |
|---|---|---|
| **Convergent** | activity estimate vs structural estimate, Spearman ρ | **ρ = +0.03. Failed.** ρ = −0.14 against night bus departures |
| **Criterion** | risk score vs night pedestrian crashes — never enters the model | **[UNMEASURED]** — BTP PDFs downloaded, unmined |
| **Ground truth** | 8 stratified segments, 5-min counts at 21:30, rank correlation, photo | **[UNMEASURED]** — one evening's work |
| **Transfer** | fit where data exists, apply where it does not, report degradation | designed; degradation not yet quantified |

The line to say on the failure, and it should be said with confidence:

> We ran convergent validation over 1,164 segments and **it failed** — ρ = 0.03,
> and night commercial activity is slightly *anti*-correlated with night bus
> service at −0.14. We checked it wasn't an artefact: same answer on arterials
> alone, same answer excluding degenerate segments, and we found and fixed a
> graph bug first.
>
> The two proxies are not two views of one latent footfall. They are two
> different night populations — people out near night commerce, and people
> commuting on bus corridors. Averaging them into one exposure index would have
> averaged away the exact population this problem statement names. So we stopped
> blending them evenly: the structural half leads at 0.75 because the statement
> says *late-night commuters*, and the disagreement set — structural high,
> activity low — is the target, not the error.

Then the two cheap things nobody else does:

- **Negative controls.** An industrial cul-de-sac at 01:00 must score near zero;
  a stretch outside a bus terminus at 22:00 must score high; a gated-layout
  internal road must score low on through-movement and moderate on residential.
  Fifteen minutes, and they catch the class of bug a correlation hides.
- **Uncertainty as a control signal.** Every other team renders one confident
  number per street. We render a band, and the band *does* something: the router
  refuses wide-band segments, the report screen targets them.

**One number to put on this slide that nobody else will have:** BMTC's GTFS
carries every departure time, so night service is directly countable. In our
bbox: **405 stops, 6,187 departures at or after 21:00 — 6.1% of daily service —
and 119 of those 405 stops have no night service at all.** Where the night buses
stop, people walk, and nobody is counting them.

### 14 · The data — what we have, what is gated

Split slide. Left, the inventory; right, the IUDX screenshot.

**Have, open, in hand:** 126,974 grievances (six years available) · 1,211 mapped
lamps in the bbox, 1,080 of them carrying a `working=yes/no` label · per-lamp KML
for the ORR corridor · lamp counts for all 198 wards, 421,113 lamps · BMTC GTFS
with per-stop departure times · a two-date citizen lamp audit · night pedestrian
crash reports.

**Gated, catalogued, one approval away** — IUDX dataset
`9b27c09f-1ec6-4acd-89f0-a27f23184017`, published by the Electronics City
Industrial Township Authority: *"Streetlights Location Info in Electronic City,
Bengaluru"*, with an hourly current-and-voltage companion resource. Marked
Private. The sample record is public:

```json
{"deviceID": "L0302", "location": {"type": "Point", "coordinates": [77.666046, 12.841758]}}
```

> Ninety-three Indian cities publish streetlight **counts** through MoHUA's
> Smart Cities portal. **Zero publish coordinates** — the D24 template is a KPI
> return, not an asset register. The pole-level geometry is on IUDX, for our
> city, published by the local authority, marked private.
>
> So Roshni's internal lamp record **is** `{deviceID, location: GeoJSON Point}`
> and its telemetry record **is**
> `{deviceID, observationDateTime, current, voltage}` — copied verbatim from
> IUDX. "We plug into the municipal feed the day access is granted" is not a
> promise, it is a schema fact. When it opens, the darkness prior is replaced by
> measurement and the bands collapse. The queue, the exposure model, the
> knapsack and all three screens are unchanged.

Worth one line here because it is the fragmentation story in miniature: **the
IUDX feed covers Electronic City, which has exactly 4 lamps mapped in OSM. OSM
covers the ORR corridor, which has 1,211.** The two datasets cover adjacent,
non-overlapping ground.

### 15 · What we know we get wrong

Volunteering limitations buys more than defending them. Four, and they are real:

- **Ward road-km is approximated** from ward area × measured corridor road
  density, because we pulled named roads only. It runs optimistic for dense
  inner wards — BTM Layout comes out at 108 lamps/km, which is 9 m pole spacing
  and not real. Those wards read *lighter* than they are, so **Roshni is
  currently conservative in exactly the wards that complain least.** Fix is the
  full OSM drive network per ward.
- **OSM records `opening_hours` for 6.7% of POIs** in our corridor — 78 of
  1,157. So we cannot filter night activity by hours as designed; we weight by
  POI class instead, and Google's review counts (which we do not have) undercount
  thelas and tea stalls, exactly the population most exposed to dark streets.
- **The `working` tags are survey-biased.** 614 broken to 463 working inside the
  bbox is a property of who went out mapping, not the outage rate of Bengaluru.
  We use them as labels, never as a base rate.
- **Tree canopy** is a large effect on perceived street lighting in Bengaluru and
  we have no data for it at all. **Footpath existence** is the same story — a lit
  road with no walkable footpath is not a safe pedestrian route, and OSM
  `sidewalk` coverage here is thin.

Also say, plainly: VIIRS nightlights are 500 m per pixel — five to ten city
blocks — so they cannot tell you a street is dark, and we do not use them that
way. Half the teams in this track will have a VIIRS raster on a slide.

### 16 · What is next, and the ask

Answer this with what you would try to **learn**, not with features.

- Mine the BTP crash reports and close the criterion-validation leg.
- Field pedestrian counts on stratified segments — is the ordering right?
- Fit the transfer model across wards of genuinely different urban form, and
  report the degradation honestly. Where it does not transfer, the system should
  refuse to guess and ask for a report instead — that behaviour is already built.
- Instrument the resolution loop: **BBMP closes 96.4% of electrical complaints,
  and Roshni is the first thing that can ask *closed, or fixed?*** A ward line
  reading "11% of closures were not verified by anyone on the ground" is a metric
  a commissioner does not have today and would want immediately. One table and a
  notification.

**The ask, as the last thing on the screen:** the data exists, for our city, one
approval away, and we already speak its schema. Approve the IUDX request.

Then end on **5.2×**. First number they hear and the last.

---

## Part 3 — Prototype glimpses

Four screenshots. Generate the screens with the prompts in `docs/prompts.md`,
which already carry the design constraints above.

**Feed the generator `out/segments.fixture.geojson`** — 12 real segments,
already written, real Bengaluru geometry and street names, spanning the whole
score range from Outer Ring Road at 0.535 repair priority down to Haralur Road
at 0.0007 with a 0.083 variance. It exists so the generated UI is populated with
real data instead of a fake-data generator, and so the numbers in the screenshots
match the numbers on the slides. `out/segments.geojson` has all 1,164 if a screen
needs a full map.

| Shot | Screen | Must be visible |
|---|---|---|
| A | Queue | hero ratio · budget slider · ranked list with real street names · one hatched low-confidence row |
| B | Queue detail | one segment expanded: darkness, both exposure halves, the confidence band, the evidence counts |
| C | Route | two polylines · comparison strip · the safer route bending around a hatched segment |
| D | Report empty state | "streets worth checking tonight" · a real street name · the one-line reason |

Rules for the shots: real screenshots only, no phone-bezel mockup frames, no
Lorem, no invented street names. Crop tight and let the amber accent be the only
saturated thing in the frame. If a generated screen renders low confidence as a
plain colour instead of a texture, fix that before screenshotting — it is the
one visual element the whole honesty argument rests on.

---

## Part 4 — References

**Data**

- BBMP grievance register 2020–2025 — OpenCity. `Sub Category = "Street Light Not Working"` as a literal value.
- BBMP streetlight counts, 198 wards, 421,113 lamps — OpenCity.
- Vasanthanagar streetlight audit 2019, 469 lamps, two dates — OpenCity citizen audit.
- Per-lamp KML, ORR corridor and Bellandur/HSR — OpenCity, OSM-derived.
- BBMP ward boundaries, 2015 / 198-ward vintage — the vintage that matches both the lamp counts and the grievance ward names.
- OpenStreetMap — `highway=street_lamp`, `working=*`, `lit=*`, walk network. ODbL.
- BMTC GTFS — Vonter/bmtc-gtfs. Per-stop `trip_list` gives night departure counts.
- Bengaluru Traffic Police road safety reports 2023, 2024 — PDFs, night pedestrian casualties and named blackspots.
- IUDX dataset `9b27c09f-1ec6-4acd-89f0-a27f23184017`, Electronics City Industrial Township Authority — streetlight locations and hourly current/voltage. Private; public sample record.
- MoHUA Smart Cities data portal, D24 street-lighting template — counts, not coordinates. 93 cities.

Full manifest with exact download URLs, schemas and reliability grades:
`docs/data-sources.md` and `data/manifest.json`.

**Concepts and prior art**

- Jane Jacobs, *The Death and Life of Great American Cities*, 1961 — eyes on the street. The duality slide.
- Chalfin et al., RCT on street lighting and crime, New York public housing — real reductions found.
- UK local-authority streetlight switch-off study (Steinbach et al., *J. Epidemiol. Community Health*) — no increase in crime or road collisions. **Cite both.** The literature is genuinely mixed, and knowing that reads as maturity.
- SafetiPin — night-time safety audit methodology, Indian cities. The rubric prior art.
- FixMyStreet — civic reporting flow, the plainness reference.
- Space syntax / edge betweenness as a movement predictor — the structural exposure half.
- Knapsack under a budget constraint — the triage optimiser. Greedy by value-per-cost.
- Beta-binomial conjugate updating with exponential time decay — the darkness posterior.

**Licensing, if asked:** OSM is ODbL, so attribution and share-alike if anything
ships publicly. Most OpenCity resources carry "No License Provided" — fair
dealing for a non-commercial prototype; production runs on a data-sharing
agreement with BBMP.

---

## Part 5 — Judge Q&A

Assign an owner per question and rehearse out loud.

**"Where is your streetlight data?"** 1,211 mapped lamps in the bbox, 1,080
carrying a working/not-working label, per-lamp KML for the corridor, counts for
all 198 wards. Beyond that we estimate, with a band. **BBMP's own records have
no coordinates and no pole IDs** — we are at parity with the municipality on day
zero and ahead of it the moment a report carries a GPS fix.

**"Your ratio is just an optimiser beating random."** Partly, and that is why we
built the steelman: same complaint-driven ward order, but BBMP picks the single
worst segment inside every ward it visits. It still loses, 1.58×. The gain is in
*which wards get visited*, and that is set by the complaint log, not by us.

**"Your weights are arbitrary."** Two are sliders, because the municipality
should own that choice. The darkness prior is calibrated against a measured
failure rate. And the exposure blend is set by a measurement — we ran the
convergent check, it came back ρ = 0.03, and that result is *why* the structural
half leads at 0.75.

**"Isn't a lit street always safer?"** No — hence opposite signs in the two
surfaces. The empirical literature is mixed: a US RCT found real reductions, a UK
switch-off study found no increase in crime or collisions. We do not claim
lighting causes safety. We claim exposure to darkness is a cost worth ordering
repairs by.

**"How much of this is synthetic?"** Volunteer it before they dig. The segments,
lamps, complaints, ward counts, bus departures and failure rates are all real
and all recomputed today. Telemetry records are synthetic, IUDX-shaped, and
render differently in the UI. **[UNMEASURED]** — say the real number of citizen
reports you collected yourselves; if it is zero, say zero, and say the reporting
loop is built and unseeded.

**"What stops report spam?"** Photo, GPS, timestamp, spatial dedupe, a
confidence threshold before a report moves the queue, per-device rate limiting.
Structurally: one report never reorders anything, because the posterior needs
evidence to move.

**"How does this scale beyond Bengaluru?"** It needs a road network, a boundary
file, and any per-ward lamp count. The first is universal; the other two exist
for every corporation even when unpublished. Production consumes the geotagged
registers that already exist under SLNP/ESCO contracts and on IUDX. **We are not
asking anyone to survey anything new.**

**"Liability — you are telling a woman to walk down a specific road."**
Advisory, not a guarantee. Never route through zero-confidence segments. Always
show the shortest route beside the safer one so the choice is the user's.

**"What would another week get you?"** Not features — the three unmeasured
validation legs on slide 13, and the resolution-loop instrumentation on slide 16.

---

## Part 6 — Three things still unmeasured

Everything else in this deck is computed. These are not, and each is marked
**[UNMEASURED]** where it appears:

1. **Criterion validation** against night pedestrian crashes. The BTP PDFs are
   downloaded and unmined. Highest-value remaining task, needs a highlighter,
   not a parser.
2. **Ground-truth pedestrian counts.** Eight stratified segments, five minutes
   each, 21:30, plus a photograph of the team counting. Report Spearman ρ, not
   Pearson — n=8 makes a rank statistic the only defensible choice.
3. **Your own seed reports.** The number of real citizen reports the team filed.

If none of the three lands before submission, say so on slide 13 rather than
implying otherwise. A deck that names its three open measurements reads stronger
than one a judge catches out on a single soft claim.
