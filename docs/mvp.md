# MVP — what we actually build in 24 hours

Scope contract. If it is not in this document it is not in the hackathon build,
however good an idea it is at 3am.

## The one-line spec

**A repair queue for Bengaluru streetlights, ordered by night pedestrian
exposure instead of complaint arrival time, with a citizen reporting loop that
knows which streets are worth checking, speaking IUDX's data schema natively.**

## Demo geography — settled by measurement, not preference

**ORR corridor, Silk Board to Marathahalli, including Bellandur and HSR Layout.**

```python
BBOX = (12.97, 12.90, 77.70, 77.61)   # north, south, east, west
```

Measured 21 Aug 2026 (`measurements.md`):

| Candidate | Mapped lamps |
|---|---|
| **ORR / Bellandur / HSR** | **1,211** |
| Electronic City | **4** |

**Electronic City was the intuitive choice and it is wrong.** Four mapped lamps.
The IUDX municipal feed covers Electronic City; OSM covers the ORR corridor. The
two datasets cover adjacent, non-overlapping ground — which is the fragmentation
story in one line, and worth saying on stage.

The ORR bbox also gives you 303 bus stops, 1,885 footway ways, 630 ways carrying
a `lit` tag, and — the thing that matters most — **1,173 lamps city-wide carrying
`working=yes/no`**, concentrated here. That is labelled ground truth for the
darkness model.

Electronic City stays in the deck as the **production integration** story:
`national-data-landscape.md` §2, and the closing slide.

Do not expand the bbox. Coverage is not a differentiator; the ratio is.

---

## The data contract — freeze in hour two

This is the seam between D1's pipeline and D2's frontend, and it is deliberately
**IUDX-shaped** so the production-integration claim is literally true.

### Lamp record

```json
{
  "deviceID": "L0302",
  "location": { "type": "Point", "coordinates": [77.666046, 12.841758] },
  "source": "osm" | "opencity" | "citizen" | "iudx",
  "confidence": 0.0
}
```

`deviceID`, `location` and the GeoJSON Point shape are copied verbatim from the
IUDX sample record. `source` and `confidence` are ours. When access is granted,
IUDX rows drop in with no transformation.

### Telemetry record (synthetic today, IUDX-shaped)

```json
{ "deviceID": "L0302", "observationDateTime": "2026-08-21T22:10:00+05:30", "current": 0.0, "voltage": 228.4 }
```

Matches the shape of IUDX's *Streetlights Energy Consumption* resource. Current
at zero after dusk is an outage. Today we synthesise these; in production they
arrive from the exchange. **Render synthetic ones differently in the UI.**

### Segment record — the atom everything joins on

```json
{
  "segID": "way123/4",
  "geometry": { "type": "LineString", "coordinates": [[...]] },
  "ward": "Bellandur",
  "roadClass": "secondary",
  "lengthM": 142.0,

  "darkness":   { "alpha": 2.1, "beta": 5.4, "mean": 0.72, "var": 0.021 },
  "exposure":   { "activity": 0.41, "structural": 0.66, "blended": 0.55 },

  "repairPriority": 0.39,
  "routePenalty":   1.84,
  "reportValue":    0.012,

  "evidence": { "reports": 3, "osmLamps": 11, "litTag": null, "wardComplaints2025": 214 }
}
```

Two exposure numbers, kept separate on purpose — they are the two disjoint
estimates that make convergent validation possible (`validation.md` Layer 1) and
you need both to render the disagreement set.

`repairPriority` and `routePenalty` are derived from the same exposure with
**opposite signs**. See `architecture.md` §The duality. Do not collapse them.

**Write a ten-segment fixture file at H2.** D2 builds against it all night.

---

## What we build

### Screen 1 — Report (citizen)

One tap: **"this stretch is dark."** GPS, timestamp, optional photo. Not "report
a broken streetlight" — nobody at 23:00 can identify a fixture, and fixture-keyed
records are unmatchable without an inventory.

The empty state is the feature: **"streets worth checking tonight"**, the top
segments by `reportValue = exposure × darkness_variance`. The app directs
reporting rather than waiting for it. Fifteen lines of code; it is the answer to
the cold-start question (`cold-start.md`).

Ships: form, GPS capture, local persistence, the directed list, a map pin that
distinguishes real from synthetic.

### Screen 2 — Route (citizen)

Two points in, **two polylines out** — safer and shortest, side by side, always
both. OSMnx graph, NetworkX `shortest_path` on a `safety_weight` edge attribute.
Not OSRM (`risks.md` §4).

Two hard behaviours: never route through a wide-confidence-band segment, and
never present the safer route as a guarantee.

Ships: point-to-point routing, both lines, per-segment darkness and confidence
on hover, the refusal behaviour visible.

### Screen 3 — Queue (municipality) — **the hero**

Not a heatmap. A ranked worklist.

- Budget slider: *n* repairs this week.
- Greedy knapsack maximising `Σ exposure × darkness × confidence`.
- Three weight sliders.
- **The counterfactual, in large type**: the same objective evaluated on the first *n* segments by earliest `Grievance Date` from the BBMP file, and the ratio between them.

> These 40 repairs restore **2.6×** the exposed pedestrian-kilometres that the
> complaint queue's first 40 would have.

Everything else in this document is the interface to that number. **If the night
goes badly, build this and nothing else.**

### The learning-curve panel

Same pipeline at 0 / 25 / 100 / 400 reports, plotting triage quality against
report count, with the map beside it at three of those states. Twenty seconds in
the demo and it kills the cold-start question before it is asked. If time allows,
run it twice — random reports vs. actively-selected — and show the targeted curve
dominating.

---

## What we deliberately do not build

| Not building | Why |
|---|---|
| Computer vision on street imagery | The Medium blueprint's stage 1 has no available input — there is no rideshare dashcam feed for a hackathon team. Cite it as future work; do not attempt it. |
| Live IUDX integration | Gated behind an access request. We speak its schema; we do not pretend to have a token. |
| Auth, accounts, real backend | Reports are client-side. Nobody scores you on a login screen. |
| City-wide coverage | 4 km², locked. Coverage is not the differentiator. |
| An LLM chatbot | It adds nothing and reads as padding. |
| Vendor-warranty RAG | Genuinely good idea, entirely a "what's next" slide. |
| Geocoding the Vasanthanagar landmarks | Use that file for its failure-rate constant and its narrative, not its geometry. |

---

## Build order

| Hours | D1 pipeline | D2 frontend | N1 ground truth | N2 narrative |
|---|---|---|---|---|
| H0–1 | **All four:** lock bbox, scoring formula on paper, the one number the demo ends on | | | |
| H1–2 | Freeze the segment schema, write the 10-segment fixture | Build against fixture from here on | Start the ward crosswalk | Deck skeleton with holes where numbers go |
| H2–8 | `fetch.py`, Overpass, **verify the two load-bearing numbers**, OSMnx graph, segmentation, ward join, darkness prior, exposure model | Map renders, 3 surfaces stubbed, sliders wired | Crosswalk asserted, then BTP crash PDFs by hand | SafetiPin rubric, IUDX slide, pitch draft |
| **H8** | **Hard stop on data acquisition** | | | |
| H8–10 | **Triage optimiser + counterfactual** — freshest hours to the product | Queue screen | **Field count, 8 segments, 21:30** | Field count + photos |
| H10–18 | Integration, routing duality, learning curve | Integration, polish | Negative controls, numbers into deck | Fill deck, rehearse structure |
| **H18** | **Feature freeze. No exceptions.** | | | |
| H18–22 | Demo-path bugs only | Demo-path bugs only | Hostile-judge Q&A | Two timed rehearsals + backup recording |
| H22–24 | Buffer. It gets used. | | | |

---

## Definition of done

The MVP ships when all six are true:

1. The queue screen shows a ranked worklist and a counterfactual ratio against complaint order, computed from the real BBMP grievances file.
2. The budget and weight sliders recompute the ranking in the browser with no network call.
3. Routing returns two visibly different polylines and visibly refuses one wide-band segment.
4. The report screen shows the directed "worth checking tonight" list, and synthetic reports are visually distinct from real ones.
5. At least 25 real citizen reports collected by the team, and a field pedestrian count on 8 stratified segments with a Spearman ρ.
6. The whole demo runs from precomputed static GeoJSON with the wifi off.

Item 6 is not optional. A demo that needs the network is a demo that fails in
front of judges.

---

## The three numbers the deck lives on

1. **31.4%** of Bengaluru's 126,974 civic complaints (Jan–19 Jun 2025) were broken streetlights — ~225/day. *Recompute from the raw CSV; do not quote OpenCity's blog.*
2. **96.4%** electrical closure rate — they execute well, they order badly.
3. **The counterfactual ratio** — yours, computed, the last thing the judges hear.

Plus one screenshot: the IUDX `Request Resource` button next to the sample
record `{"deviceID": "L0302", "location": {...}}`. The data exists. It is one
approval away. That is the closing slide.
