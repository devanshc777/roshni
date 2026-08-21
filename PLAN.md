# Roshni — the plan

Problem statement 17, Smart Cities: Night-Safety Dark-Zone Mapper. 24 hours,
four people, two developers.

This document is the spine. It answers, in order: is this a real problem, what
is the insight, what can we actually build, what is gated and what happens when
it opens, how the thing works, and why it holds up under a hostile question.
Every claim links to the document that carries the evidence.

---

## 1. Is this a real problem?

Yes, and the city's own data says so more sharply than the problem statement does.

Bengaluru logged **126,974 civic grievances between January and 19 June 2025**.
**31.4% of them — 39,847, about 236 a day — were "Street Light Not Working."** Recomputed from the raw CSV on 22 Aug 2026; see `docs/measured-2026-08-22.md`. It is the
single largest complaint category in the city, ahead of garbage.

Now the part that reframes it. **BBMP closes 96.4% of electrical complaints.**
They are fast. They are not under-resourced relative to the task. Road
maintenance closes at 58%; electrical closes at 96.4%. Execution is not the
bottleneck.

And streetlight complaint volume concentrates in **Jnanabharathi (1,345),
Ullalu (1,026), Hemmigepura (983), Dodda Bidarkallu (967)** — peripheral, newer,
more app-literate, more car-owning wards. (Horamavu 3,128 / Jnanabharathi 2,842 /
Thanisandra 2,480 are the *all-category* counts — do not mix the two bases.) Older, denser, more-walked inner wards file fewer complaints. Not because
their lights work.

> **A first-come queue is sorted by who complains, not by who is exposed.**

The person on a dark arterial at 23:00 is not the person filing a ticket at 10:39
the next morning. **Do not claim the timestamps prove this.** The grievance clock is
12-hour with AM/PM stripped — every hour in 126,974 rows falls in 1–12, so 7am
and 7pm are indistinguishable. The ward pattern carries the argument alone.

So this is not "the municipality is failing," which is lazy and which a
government judge will resent. It is: **an efficient execution machine is being
handed the wrong order.** That is a better story, it is true, and it is the whole
project.

Evidence: `docs/data-sources.md` §B3, `docs/verdict.md`.

---

## 2. The insight

Three moves, in dependency order. Each one dissolves a problem rather than
working around it.

**The atom is the road segment, not the lamp.** A pedestrian at 23:00 does not
care whether a street has eleven lamps or fourteen; they care whether the next
200 metres is lit. *Darkness per segment* is a continuous latent variable you can
estimate. *Lamp inventory* is a discrete enumeration you cannot obtain. Choosing
the estimable quantity is the single most important modelling decision here, and
it is why the missing inventory stops being fatal.

**Footfall carries opposite signs in the two surfaces.** In the repair queue it
is *exposure* — more people at risk on a dark street, so prioritise. In the
router it is *protection* — eyes on the street, so prefer. Use it with the same
sign in both and your router will confidently send a woman down an empty lit
industrial road at 01:00. Building the duality in deliberately is the strongest
intellectual differentiator available and it costs nothing but clear thinking.

**The output is a procurement decision, not a map.** Not "here is risk" but:

> Your crew can complete 40 repairs this week. Here are the 40 that restore the
> most exposed pedestrian-kilometres. The complaint-log order restores 19% as
> much — **measured 5.2×**, and 1.58× against a steelman baseline that lets BBMP
> pick the worst segment in every ward it visits (`docs/measured-2026-08-22.md` §6).

That ratio is the product. It is a knapsack — twenty lines — and it converts a
visualisation into something a BBMP executive engineer would open on a Monday.
Everything else in the build is the interface to that number.

Evidence: `docs/cold-start.md`, `docs/architecture.md`, `docs/verdict.md`.

---

## 3. What we can build tonight, and what is gated

We went and checked rather than assuming. The honest inventory:

### Have — open, downloadable, in hand

| | Detail |
|---|---|
| **The complaint queue itself** | Six years of BBMP grievances, `Sub Category = "Street Light Not Working"` as a literal value. The baseline we beat is *real*, not invented. |
| **1,211 mapped streetlights** in the demo bbox | Measured, 21 Aug 2026. 5,874 city-wide. |
| **1,173 lamps labelled `working=yes/no`** city-wide, **1,080 inside the demo bbox** (614 no / 463 yes) | A labelled dependent variable. Survey-biased — labels, never a base rate. |
| **Per-lamp KML** for the ORR corridor and Bellandur/HSR | OpenCity, OSM-derived, per-lamp Points. |
| **Ward lamp counts, all 198 wards** | The density prior that makes the map non-empty on day zero. |
| **A two-date citizen audit**, 469 coded lamps, Vasanthanagar 2019 | Measured: 4.0% of working lamps die per fortnight, 45.9% of dead ones get fixed, equilibrium dead share **8.0%**. This is the calibration anchor for the darkness prior. |
| **BMTC GTFS**, 405 stops in the bbox with departure times | 101,367 daily departures, **6,187 after 21:00**, and **119 stops with no night service at all**. The strongest non-proxy footfall generator. |
| **Night pedestrian crash reports**, Bengaluru Traffic Police | The non-circular validator. |

### Gated — exists, catalogued, one approval away

**IUDX**, dataset `9b27c09f-1ec6-4acd-89f0-a27f23184017`, publisher Electronics
City Industrial Township Authority, instance Bengaluru:

> **"Streetlights Location Info in Electronic City, Bengaluru"** — the physical
> coordinates of every streetlight installed there. Companion resource: **hourly
> current and voltage per device.**

Marked **Private**. `Request Resource` button. **The sample record is public:**

```json
{"deviceID": "L0302", "location": {"type": "Point", "coordinates": [77.666046, 12.841758]}}
```

### The positioning — say this exactly

> The data exists and we found it. Ninety-three Indian cities publish streetlight
> **counts** through MoHUA's Smart Cities portal; **zero** publish coordinates —
> the D24 template is a KPI return, not an asset register. The pole-level
> geometry is on IUDX, for our city, published by the local authority, marked
> private. So we built Roshni to **speak IUDX's schema natively** and to work
> without it. The ask on our last slide is that someone approves the request.

**Roshni's internal lamp record is `{deviceID, location: GeoJSON Point}` and its
telemetry record is `{deviceID, observationDateTime, current, voltage}` — copied
verbatim from IUDX.** So "we plug in the day access is granted" is not a promise,
it is a schema fact. One design decision, and the gap becomes
forward-compatibility instead of a hole.

What changes on the day access opens: the darkness prior is replaced by
measurement, `current ≈ 0` after dusk becomes hard outage evidence at the highest
weight in the update table, and the confidence bands collapse. **The queue, the
exposure model, the knapsack and all three screens are unchanged.** That is the
test of whether an architecture was honest: nothing has to be rewritten.

Evidence: `docs/national-data-landscape.md`, `docs/measurements.md`,
`docs/data-sources.md`.

---

## 4. How it works

Full specification in `docs/architecture.md`; this is the shape.

```
  OSM walk graph ─┐
  BMTC GTFS ──────┤                                    ┌─► TRIAGE (knapsack)  ─► municipal queue
  night POIs ─────┼─► EXPOSURE  E(seg) ────────────────┤   + counterfactual
  betweenness ────┘        │                           │
                           │ opposite signs            └─► ROUTING (weighted graph) ─► safer route
  ward lamp density ─┐     │
  OSM lamps working=*┼─► DARKNESS  Beta(α,β) ──────────────► confidence band
  lit=yes / lit=no ──┤        mean = P(dark)                      │
  citizen reports ───┤        var  = uncertainty                  ▼
  IUDX telemetry ────┘                                   REPORT TARGETING
   (when granted)                                        exposure × variance
```

**Darkness** is a Beta posterior per segment. Prior from ward lamp density ÷ ward
road-km, weighted by road class. Evidence — OSM `working` tags, `lit`, citizen
reports, and eventually IUDX current draw — updates α and β, with **exponential
time decay (half-life ~30 days)** so old evidence fades and the model stays live.
Posterior mean is the darkness score; posterior variance is the confidence band.

**Exposure** is two deliberately disjoint estimates: *activity* (night-open POIs
weighted by review count) and *structural* (edge betweenness on the walk graph
plus BMTC trip counts within 400 m). Kept separate because their agreement is
what validates them, and their **disagreement** identifies dark transit corridors
through non-commercial land — exactly the streets the problem statement names.

**Triage** maximises `Σ exposure × darkness × confidence` under a repair budget,
greedy by value-per-cost, and reports the ratio against the complaint-ordered
baseline.

**The resolution loop** is what makes it a system rather than a snapshot — and it
produces the sharpest municipal metric in the project. See §5.

---

## 5. The report resolution loop

A report is not the end of a transaction. The loop:

1. **Report** — one tap, "this stretch is dark," GPS and timestamp. β increases; the segment enters the queue.
2. **Queue** — exposure-weighted, so a report from a high-footfall dark street outranks an older report from a quiet one.
3. **Closure** — municipality marks it fixed, *or* IUDX telemetry shows current returning after dusk.
4. **Verification** — the system asks the original reporter and the two nearest recent reporters: *"we're told this was fixed — is it?"*
5. **Confirmed** → α jumps, the old dark evidence decays fast, the segment leaves the queue. **Unconfirmed after two asks** → β holds, urgency escalates, and the segment is flagged **"reported fixed, not verified."**

That last state is the feature. BBMP closes 96.4% of electrical complaints —
Roshni is the first thing that can ask **closed, or fixed?** A dashboard line
reading *"11% of closures in this ward were not verified by anyone on the
ground"* is a metric a municipal commissioner does not currently have and would
immediately want. It costs one extra table and a notification.

**User-facing tracking**, same loop, other end:

- **Watch a route.** A user saves the walk they do every night; they get notified when a segment on it goes dark, and when it is fixed.
- **Night warning.** A route requested after 21:00 that crosses segments above the darkness threshold shows a banner with the safer alternative — never a block, always a choice.
- **Your report did something.** "Your report on 4th Cross moved it to #7 in this ward's repair queue." Closing that loop is the only reason anyone files a second report.

---

## 6. Cross-source validation — the challenge question

> *How would you validate a footfall estimate for a street with no official usage
> data at all?*

They asked about **validation**, not features. That is the author telling you
where the marks are, and most teams will skim it.

Two structural points before any source list. First, validation needs a signal
**you did not use to build the estimate** — build a footfall index from POIs and
"validate" it against POI density and a competent judge names the circularity in
ten seconds. Second, **you are validating an ordering, not a magnitude.** "412
pedestrians per hour" is unfalsifiable. "These streets rank above those" is
checkable. Say that before you are asked.

Four layers:

| Layer | Method | Independence |
|---|---|---|
| **Convergent** | Activity estimate vs structural estimate, Spearman ρ | Disjoint inputs — two unrelated proxies do not agree by accident |
| **Criterion** | Correlate risk score against night pedestrian crashes | Crash data never enters the model |
| **Ground truth** | 8 stratified segments, 5-min counts at 21:30, rank correlation, photo | Physical world |
| **Transfer** | Fit weights where data exists, apply where it does not, report degradation | Answers the question as literally asked |

Plus **negative controls** — an industrial cul-de-sac at 01:00 should score near
zero; a stretch outside a bus terminus at 22:00 should score high. Fifteen
minutes, and they catch the class of bug a correlation coefficient hides.

Plus **uncertainty in the interface.** Every other team renders one confident
number per street. Roshni renders a confidence band, and that band is
load-bearing: the router **refuses to route** through wide-band segments, and the
report screen **sends people to them**. Uncertainty as a control signal, not a
disclaimer.

Full architecture and the 45-second spoken version: `docs/validation.md`.

---

## 7. Defensibility — the questions and the answers

| Question | Answer |
|---|---|
| *Where's your streetlight data?* | 1,211 mapped lamps in the demo bbox, 1,173 labelled working/not-working, per-lamp KML for the corridor, ward counts for all 198 wards. Beyond that we estimate, with a confidence band. **BBMP's own records have no coordinates and no pole IDs** — we're at parity with the municipality on day zero and ahead of it the moment a report carries a GPS fix. |
| *How much is synthetic?* | Volunteer it first. *These 31 reports are ours from last night, here's the photo. These 400 are simulated to show the learning curve and they render differently on the map.* Having synthetic data is fine. A judge **discovering** it is not. |
| *Isn't a lit street always safer?* | No — hence opposite signs in the two surfaces. Jacobs, eyes on the street. And the empirical literature is mixed: a US RCT found real reductions; a UK study of local-authority switch-offs found no increase in crime or collisions. We don't claim lighting causes safety; we claim exposure to darkness is a cost worth ordering repairs by. |
| *Your weights are arbitrary.* | Two are, which is why they're sliders — the municipality should own that choice. The third is fitted against night pedestrian crash counts. Here's the slider; pick your own and watch the ranking change. |
| *What about report spam?* | Photo, GPS, timestamp, spatial dedupe, a confidence threshold before a report moves the queue, per-device rate limiting. Structurally: one report never reorders anything, because the posterior needs evidence to move. |
| *How does it scale?* | It needs a road network, a boundary file, and any per-ward lamp count. Production consumes the geotagged registers that already exist under SLNP/ESCO contracts and on IUDX. **We are not asking anyone to survey anything new.** |
| *Liability?* | Advisory, not a guarantee. Never route through zero-confidence segments. Always show the shortest route alongside the safer one so the choice is the user's. |

**Volunteer three limitations unprompted** — it buys more than defending them
does. VIIRS nightlights are 500 m per pixel, five to ten city blocks, so they
cannot tell you a street is dark and we don't use them that way. Google review
counts undercount thelas and tea stalls — exactly the population most exposed to
dark streets. Tree canopy is a large effect on perceived lighting in Bengaluru
and we have no data for it.

---

## 8. Thought process — how we got here

Worth one slide, because it is the part that is hard to fake.

1. **Asked what data exists** before designing anything. Found the national portals publish indicators, not geometry — and proved it by pulling the catalog API and reading the file sizes: 250 bytes to 133 KB for cities with six-figure lamp counts.
2. **Found the gated layer** on IUDX and read its public sample record, which gave us a production schema for free.
3. **Measured rather than assumed.** Ran Overpass against four candidate bboxes and moved the demo geography off Electronic City — 4 mapped lamps — onto the ORR corridor, 1,211.
4. **Found labelled ground truth we did not expect** — 1,173 lamps carrying `working=yes/no` — which upgraded the darkness model from asserted to fitted.
5. **Changed the deliverable** once we saw the complaint data. The 96.4% closure rate meant the problem was never execution. So we stopped building a map and built a queue.

That sequence — check, measure, then design — is the reason the architecture did
not need rewriting when the data turned out to be different from what we assumed.

---

## 9. What we are not building

Computer vision on street imagery (the published blueprints for this depend on
rideshare dashcam feeds that no hackathon team can obtain). Live IUDX integration
(gated — we speak its schema, we don't pretend to have a token). Auth and
accounts. City-wide coverage. An LLM chatbot. Vendor-warranty RAG.

Each of these is a future-work line, and saying so deliberately reads better than
a half-built version of any of them.

---

## 10. Start here

- **Building it:** `docs/build.md` — commands, order, code skeletons.
- **Scope contract:** `docs/mvp.md` — what ships, the frozen schema, definition of done.
- **UI generation:** `docs/prompts.md` — prompts for v0 / Lovable / Bolt, with references.
- **First action, hour one:** re-run `data/overpass.md` Q1 against your locked bbox and confirm the 1,211. The pitch quotes it.
