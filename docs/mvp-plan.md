# MVP plan — architecture, UI/UX, integration

The buildable plan. Reasoning and the three verification passes that produced it
are in `docs/mvp-plan-log.md`; read that if a decision looks arbitrary.

Scope contract stays `docs/mvp.md`. Numbers stay `docs/measured-2026-08-22.md`
§10. This document is *how it gets built*.

---

## 1. Architecture

### 1.1 The demo — what actually ships

```
  ┌─ OFFLINE BUILD (Python, runs before the demo) ──────────────────────┐
  │                                                                     │
  │  data/fetch.py          23 open sources  →  data/raw/               │
  │  data/snapshot_osm.py   Overpass, 126 km², tiled                    │
  │  data/pipeline.py       graph · darkness · exposure · triage         │
  │  data/derive_screens.py routes · curve · telemetry · bypass          │
  │                                                                     │
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │  four static files, frozen contract
                                 ▼
  ┌─ BROWSER (no server, no network) ───────────────────────────────────┐
  │                                                                     │
  │   segments.demo.geojson ──┐                                         │
  │   basemap.geojson ────────┤                                         │
  │   graph.json ─────────────┼──►  score.ts   Beta posterior           │
  │   stats.json ─────────────┘     ├─ knapsack + counterfactual        │
  │                                 ├─ Dijkstra, live weights           │
  │                                 └─ report simulation                │
  │                                        │                            │
  │             ┌──────────────────────────┼──────────────────────┐     │
  │             ▼                          ▼                      ▼     │
  │          QUEUE                      ROUTE                 REPORT    │
  │      ranked worklist          safer vs shortest      worth checking │
  │      + CSV work order         + live weights         + resolution   │
  └─────────────────────────────────────────────────────────────────────┘
```

Everything after the build step is a pure function of four files. No API, no
database, no tile server, no auth. **Unplug the network and the demo is
identical** — which is the point, because hackathon wifi fails at exactly the
wrong moment (`docs/risks.md` §7).

### 1.2 Production — documented, not built

The honest answer to "how does this integrate", which is the question that
actually kills civic tech projects:

```
  IUDX exchange ──► poller ──┐
  BBMP grievance feed ───────┤
  Citizen reports (POST) ────┼──► FastAPI ──► PostgreSQL + PostGIS
  OSM diffs (nightly) ───────┘        │            │
                                      │            ├─ segments, evidence, reports
                                      │            └─ resolutions (closed vs verified)
                                      │
                                nightly pipeline ──► materialised scores
                                      │
                                      └──► same four files, same frontend
```

The frontend does not change. That is the test of whether the demo architecture
was honest: production adds an ingestion path and a database *behind* the same
contract, and the three screens are untouched.

Stack for that path, if it is ever built: FastAPI (async, and the IUDX poller is
IO-bound), PostgreSQL + PostGIS (the segment geometry and the spatial dedupe of
reports both want real spatial indexes), one nightly job. Not tonight.

---

## 2. Tech stack

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Pipeline | Python 3.12, `pandas` + `networkx` | Already built and working. No geopandas, no GDAL — haversine, ray-casting point-in-polygon and a shoelace are forty lines and cost zero install risk |
| Build | **none** | See `mvp-plan-log.md` iteration 4: it got built and React turned out to be over-built. One HTML file, vanilla, ~520 lines with CSS, no build step |
| UI | vanilla JS + DOM | Re-ranking 11,029 rows and repainting 2,117 features per slider tick is a `sort` and one `setData`. There was never a diff to reconcile |
| Types | `console.assert` at load | The data contract really is the seam that breaks — but an assert on boot catches it without a compiler |
| Map | MapLibre GL JS | Leaflet chokes on thousands of polylines (`risks.md` §6). No API key, no token |
| Styling | plain CSS custom properties | The design system already *is* tokens. A utility framework to re-express them is a build step for nothing |
| State | one `state` object + one `render()` | Three screens is not a state-management problem |
| Routing | three tabs | Three screens is not a routing problem |
| Backend | **none** | The demo runs offline. A backend that gets switched off should not be built |

Total runtime dependencies: **one** (`maplibre-gl`, two vendored files). No
build step. Served with `python -m http.server`, because ES modules will not
load over `file://` — still no network call on the demo path.

> Iteration 4 overruled the React/Vite/TypeScript row above after the thing was
> actually built. The reasoning is in the log; this table records where it
> landed, not where it started.

---

## 3. The frozen data contract

Freeze this before either developer writes a line. It is the only seam.

| File | Size | Contents |
|---|---|---|
| `out/segments.demo.geojson` | ~1.5 MB | 2,117 scored `LineString` features. Every evidence-bearing segment plus the top 2,000 by priority |
| `out/basemap.geojson` | ~3 MB | Every road in the bbox, geometry only, no properties. Drawn thin and desaturated underneath everything |
| `out/graph.json` | ~1 MB | `{nodes: {id: [lon,lat]}, edges: [[a, b, lengthM, segID]]}` — the walk graph for client-side routing |
| `out/stats.json` | 4 KB | The measured figures the UI quotes, so no number is typed into a component |
| `out/scoring.json` | ~1.1 MB | **Columnar, geometry-free, all 11,029 segments.** The maths runs over this; the GeoJSON above is only for drawing. Scoring the render subset inflates our own side and makes the app disagree with the deck |

Segment properties, verbatim from `data/pipeline.py`:

```ts
type Segment = {
  segID: string; name: string; ward: string; roadClass: string; lengthM: number;
  darkness:   { alpha: number; beta: number; mean: number; var: number };
  exposure:   { activity: number; structural: number; blended: number };
  confidence: number;         // 0-1, = 1 - rank(var). Drives the texture.
  repairPriority: number;
  routePenalty: number;
  reportValue: number;
  evidence: {
    osmLampsWorking: number; osmLampsBroken: number; osmLampsUntagged: number;
    nightBusTrips: number; wardComplaints2025: number; reports: number;
  };
};
```

All five files are on disk. `basemap.geojson`, `graph.json` and `scoring.json`
were added to `data/pipeline.py` for this plan; the rest already existed.

---

## 4. Client-side model — inside `web/index.html`

Four pure functions, no framework. This is the part that must be hand-written
rather than generated; a generator will produce a knapsack that is subtly wrong.

The three sliders are **exponents**, mapped `w → 2w`, so the 0.5 default makes
the objective exactly the pipeline's `repairPriority`. That is why the app's
ratio agrees with the deck instead of drifting from it.

```ts
// Beta posterior, given simulated reports on top of the pipeline's evidence.
posterior(seg, reports): { mean, var }
    α = seg.darkness.alpha + Σ w·(report says fine)
    β = seg.darkness.beta  + Σ w·(report says dark)
    mean = β/(α+β)          // beta is dark — one sign convention, never flipped
    var  = αβ/((α+β)²(α+β+1))

// Greedy by value-per-cost. Unit cost, so it is a straight sort.
triage(segs, budget, weights): Segment[]

// The number the demo lands on. Complaint order names a ward, never a segment,
// so the baseline is Monte-Carlo'd — 60 draws in the browser, not 300.
counterfactual(segs, budget): { ratio, p5, p95 }

// Dijkstra twice: once on length, once on the live-weighted penalty.
route(graph, from, to, λ): { safer, shortest }
    penalty = lengthM · (1 + λd·mean + λe/exposure + λu·var)
```

Two invariants worth an assert each, because both have already been got wrong
once in this project:

- **`beta` is dark.** One sign convention, asserted at load.
- **Exposure multiplies in `repairPriority` and divides in `routePenalty`.** If
  both are in the numerator the router calls an empty lit industrial road safe.

### Report simulation — `sim.ts`

Two modes, and the contrast between them *is* the thesis.

| Mode | How reports are chosen | What it shows |
|---|---|---|
| **As they actually arrive** | sampled with probability ∝ activity exposure — app-literate, commercial, affluent streets | the complaint-log bias, reproduced |
| **Reports we asked for** | argmax of upper confidence bound: `exposure × min(1, mean + 1.5·sd) × length` | directed reporting, which beats random from ~10 reports on |

A report resolves toward the pipeline's posterior mean with 2.5 units of
evidence. Drag the slider 0 → 400 and the map sharpens; switch mode and the
queue quality diverges. That is the learning curve, live, and it replaces the
chart component that earlier drafts carried.

---

## 5. UI/UX plan

### 5.1 Visual system

Taken from the product's own design system (`assets/design-system.png`), not
invented for the build.

```css
:root {
  --bg-0:#0B0F14; --bg-1:#121820; --bg-2:#1B232E; --bg-3:#232B36;
  --text-0:#FFFFFF; --text-1:#E6EAF0; --text-2:#B1BAC6; --text-3:#7A8696;
  --brand:#FFC107; --brand-2:#FFB300;
  --blue:#40A3FF; --teal:#26C6A6; --indigo:#7C9BFF; --error:#FF6B6B;
}
```

**Darkness is a six-step lux scale, D0–D5** (>30 lux down to <0.2), sequential
light→dark. Never red/green: the light-to-dark comparison is exactly the one
deuteranopia breaks.

**Confidence is texture, in four states.** This is the single most important
visual decision in the product, and cartographic practice backs it — a hatched
overlay is *extrinsic*, so the uncertainty layer stays visually separable from
the value underneath, and texture is the recommended channel for colour-blind
accessibility.

| Confidence | Treatment | Meaning |
|---|---|---|
| High | solid | use for decisions |
| Medium | diagonal hatch | use for planning |
| Low | dot pattern | use cautiously |
| Unknown | dashed outline | do not assume |

In MapLibre, line texture comes from `line-dasharray` driven by a `step`
expression on `confidence`, with `line-opacity` falling as confidence falls.

### 5.2 Screen 1 — Queue (municipal). The hero.

Reference: the console mockup in `assets/screen-queue.png`. Density reference is
Linear's issue list, not a smart-city dashboard — no gauges, no donuts, no
glowing borders.

```
┌────────────────────────────────────────────────────────────────────────┐
│ ROSHNI · Repair Prioritisation          [Our order | Complaint order]  │
├────────────────────────────────────────────────────────────────────────┤
│  These  40  repairs restore   7.7×   the exposed pedestrian-km …       │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Repair budget  ──●────  40   │  Municipal priorities                   │
│                              │  Darkness ──●──  Exposure ──●──  Conf ─●│
├──────────────────────────────┴─────────────────────────────────────────┤
│ RANKED WORKLIST              │  MAP — darkness by segment              │
│ # ward  street  D  E  conf   │  (texture = confidence)                 │
│ 1 …                          │                                         │
│ …                            │                                         │
├──────────────────────────────┴─────────────────────────────────────────┤
│ Simulated reports ──●──── 0        [as they arrive | we asked for]     │
│                                    [ Download work order (CSV) ]       │
└────────────────────────────────────────────────────────────────────────┘
```

Behaviours, in priority order:

1. **The ratio is the largest object on the page** and it moves when the budget moves. Recompute in the browser, under 100 ms, no network call.
2. **Sliders are labelled "municipal priorities", not "model weights."** The municipality owns that choice, not us.
3. **Selecting a row highlights the segment**; selecting a segment scrolls the row into view. Both directions, or it feels broken.
4. **Low-confidence rows carry the texture**, never a plain colour. If this gets flattened the honesty argument becomes invisible.
5. **"Our order" vs "complaint order" toggle** re-draws list and map, so the difference is visible rather than asserted.
6. **Download work order** emits a CSV of the current selection: rank, ward, street, segID, darkness, exposure, confidence, why. This is the deliverable — a dashboard you can only look at is the documented failure mode of the whole category.

### 5.3 Screen 2 — Route (citizen)

Reference: `assets/screen-route.png`. Pattern taken from route-comparison UIs —
Citymapper's comparison strip, and the mobile bottom-sheet convention.

- **Both routes, always, side by side.** Distance, walking time, and a lit / dark / unknown proportion bar for each. The user chooses. Never auto-select the safer one, never hide the shortest.
- **Each route drawn segment-by-segment** by darkness, so the user sees *where* it is dark rather than being handed a score.
- **Unknown is a first-class state.** Wide-band segments render in the low-confidence texture and the safer route visibly bends around them.
- **Live weights.** Dragging λd / λe / λu re-routes instantly. This is where the duality becomes demonstrable rather than claimed: turn desertedness up and watch the route refuse an empty lit road.
- **Night banner** after 21:00 when the route crosses dark segments. Offers the alternative, never blocks, factual copy, no sirens.
- **Watch this route** toggle, in-memory.
- **A permanent quiet disclaimer**: advisory, estimated from partial data, not a safety guarantee.

One thing to say on this screen, from `out/routes.json` → `noAlternative`: on the
25 worst segments, 6 have no walkable bypass at all and 19 need a detour over 3×
the segment length. Routing cannot fix those streets. Only repair can.

### 5.4 Screen 3 — Report (citizen)

Reference: `assets/screen-report.png`. Flow reference is FixMyStreet, which asks
for **location before identity** — you are never asked your name first.

- **One tap: "This stretch is dark."** Not "report a broken streetlight" — nobody standing on a road at 23:00 can identify a fixture. GPS, timestamp, optional photo. Optional means the flow completes in under five seconds without one.
- **The empty state is the feature.** Not "no reports yet" but **"streets worth checking tonight"**, ranked by `reportValue`, each with a one-line reason: *busy after dark, we have no data here.*
- **Simulated reports render differently from real ones**, with a legend entry saying so. Never hide this.
- **The resolution loop**: Open → Reported fixed → *"we're told this was fixed — is it?"* → Verified, or **flagged "reported fixed, not verified."** That last state is the feature: BBMP closes 96.4% of electrical complaints and this is the first thing that can ask *closed, or fixed?*
- **Impact line**: "your report moved 4th Cross Road from #7 to #4 in this ward's queue." The only reason anyone files a second report. Documented UX research on this category found complaints go unresolved for lack of *transparency*, not lack of a form.
- No gamification, no badges, no points. Someone is using this while walking alone at night.

### 5.5 Accessibility floor

Non-negotiable, and cheap: WCAG AA contrast on all text; 44 px minimum tap
targets; confidence never encoded by hue alone; map labels sit on a scrim;
`prefers-reduced-motion` respected; the whole thing legible outdoors at night on
a phone at arm's length.

---

## 6. Integration plan

### 6.1 The seam, and how the two developers meet at it

The failure mode is D2 waiting on D1's pipeline. It is avoided by making the
contract real before either starts.

| Step | Owner | Output |
|---|---|---|
| 0 | both | Freeze §3. Write `types.ts` from it. Commit. |
| 1 | D1 | Add `basemap.geojson` and `graph.json` to `derive_screens.py` |
| 2 | D2 | `web/index.html` reading the five files from `web/data/` |
| 3 | D2 | scoring against `scoring.json`, verified by asserts on load |
| 4 | D1 | Rerun pipeline; D2 swaps the files in. Nothing else changes |

`out/segments.fixture.geojson` — 12 real segments spanning the whole score range
including one wide-band one — is the file to build against from minute one. It
loads instantly and it exercises every visual state.

### 6.2 Loading

```
web/data/segments.demo.geojson    render
web/data/basemap.geojson          render
web/data/graph.json               routing
web/data/scoring.json             all maths, all 11,029 segments
web/data/stats.json               figures quoted in the UI
```

Fetched once at boot, held in memory, never refetched. `cp out/* web/data/`
after a pipeline run — that is the whole deploy step.

Serve with `python -m http.server 8080 --directory web`. A server is needed only
because browsers refuse ES modules over `file://`; nothing leaves the machine.

### 6.3 The one shared computation

```
raw segments ──► useMemo(posterior + score, [reports, simMode, weights])
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      Queue        Route        Report
     (sorts)     (weights)   (ranks by reportValue)
```

One array, three consumers. No per-screen pipeline, so the tabs cannot disagree
with each other.

### 6.4 Verification, at the boundary where it matters

Not a test suite. Four asserts that run on load and fail loudly:

```ts
assert(segments.every(s => s.darkness.mean >= 0 && s.darkness.mean <= 1));
assert(counterfactual(segments, 40).ratio > 1);        // else the baseline is wrong
assert(route(g, a, b, λ).safer.distanceM >= route(g, a, b, λ).shortest.distanceM);
assert(triage(segments, 40).length === 40);
```

Plus one thing to check by hand before demoing, because no assert catches it:
**turn the wifi off and reload.**

---

## 7. Build order, and what to drop

| Hours | Build |
|---|---|
| 0–0.5 | Freeze the contract, `types.ts`, Vite scaffold, four files loading |
| 0.5–1 | `basemap.geojson` + `graph.json` added to the pipeline |
| 1–3 | **Queue screen** — worklist, map, budget + priority sliders, live ratio |
| 3–3.5 | CSV work order |
| 3.5–4.5 | Report simulation slider and the two modes |
| 4.5–6 | Route screen — Dijkstra, comparison strip, live weights |
| 6–7 | Report screen — empty state, resolution loop |
| 7–8 | Polish, offline check, screenshots for slides 10–12 |

**Order of abandonment**, if behind: Report screen → Route screen → simulation
modes → CSV → *never the queue, never the counterfactual.* That is the project.

## 8. Definition of done

1. Queue shows a ranked worklist and a counterfactual ratio computed from the real BBMP grievance file.
2. Budget and priority sliders recompute in-browser with no network call.
3. Routing returns two visibly different polylines and visibly avoids a wide-band segment.
4. The report slider visibly sharpens the map, and the two simulation modes visibly diverge.
5. Low confidence renders as texture, not colour, on every surface.
6. **The whole demo runs with the wifi off.** Not optional.
7. `Download work order` produces a CSV a municipal engineer could act on.

## 9. Not building, and why

| Not built | Reason |
|---|---|
| Any backend | Demo runs offline; production path is documented in §1.2 |
| Auth, accounts | Nobody scores a login screen. FixMyStreet does not ask for identity first either |
| Tile server / raster basemap | Network call on the demo path. We already own the road network |
| Learning-curve chart | The report slider shows it live; two ways to show one result is one too many |
| Telemetry viewer | It is a schema claim. It belongs on a slide |
| Computer vision on street imagery | The published blueprints need rideshare dashcam feeds no hackathon team can get |
| Live IUDX integration | Gated. We speak its schema; we do not pretend to hold a token |
| City-wide coverage | Coverage is not the differentiator. The ratio is |
| An LLM anywhere | It adds nothing and invites a question we would lose |

One limitation to state rather than solve: the documented reason civic tech
projects die is "building **for** instead of **with**" — and we have not built
this with BBMP. One night does not fix that. Saying so is better than pretending
a data-sharing agreement is a formality.
