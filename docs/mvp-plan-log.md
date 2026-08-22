# MVP plan — iteration log

Three passes. Each one re-read the previous, checked it against what is actually
on disk, and **added and subtracted**. What got cut matters more than what got
added, so the cuts are recorded with the reason.

The plan itself is `docs/mvp-plan.md`. This file is the reasoning behind it.

Skills used: `ponytail` (full) governed every build decision; `jeffallan-skills`
consulted for the stack lanes (`react-expert`, `fastapi-expert`,
`typescript-pro`, `postgres-pro`, `architecture-designer`); web research on map
UI, uncertainty cartography, and — most usefully — civic-tech *failure*
patterns.

---

## Research first, because it changed the plan

Four searches, deliberately including a contrarian one.

**Uncertainty cartography.** Hatching is an *extrinsic* overlay: the uncertainty
layer stays visually separable from the data underneath, and tighter line
spacing conventionally reads as higher confidence. Texture is also the
recommended channel for colour-blind accessibility. Our design system already
does this — solid / hatch / dot / dashed — so it is now a cited convention
rather than a taste call.

**Civic reporting UX.** FixMyStreet's whole flow is "fundamentally a map users
can put a pin on", and it deliberately asks for **location before identity** —
you are never asked your name first. That validates the one-tap report and kills
any temptation to add an account step. Documented UX research on the category:
70% of users do not know the right channel to report an issue, and complaints go
unresolved for lack of *transparency*, not lack of a form. That is the
resolution loop's justification.

**Dark dashboard practice.** Off-white text rather than pure white; elevation
carried by surface lightness rather than shadow; saturated colour reserved for
meaning and everything else desaturated. Matches the design system's tokens.
`mapcn` and `maplibre-theme` exist if we want prebuilt MapLibre dark controls.

**The contrarian search was the valuable one.** Searching for why civic
dashboards *fail* returned the sharpest critique of the thing we are building:

> Dashboards act "not as aids to decision-making but as devices to be passively
> consumed or observed: spectacles to 'take in' rather than tools to guide
> action." They give decision-makers "a sense of control ... a white-washed
> panoramic view" — a false sense of authority over a complex system. The
> recurring failure is "building for, instead of with", and projects die when
> they "cannot be functionally integrated into governmental structures."

Three direct consequences for this plan, all adopted:

1. **The demo must produce an artifact, not a view.** A dashboard you look at is
   the failure mode named above. So the queue screen gets a **Download work
   order (CSV)** button. Forty rows, ward, street, segment ID, why. That is the
   difference between a spectacle and a tool.
2. **"Cannot be integrated into governmental structures" is the actual killer**,
   not UI quality. It is why the IUDX-shaped record and the "no new survey
   required" line are load-bearing rather than decorative.
3. **"Building for, instead of with"** is a limitation we should name rather than
   pretend we solved in one night.

---

## Iteration 1 — first pass

Straight read of `docs/mvp.md` plus the ladder.

**Stack proposed:** Next.js + React + Tailwind + shadcn/mapcn on the front,
FastAPI + PostgreSQL/PostGIS on the back, reports POSTed to an API.

**Rung 1 of the ladder killed the backend immediately.** `docs/mvp.md`'s
definition of done says the whole demo must run from precomputed static files
with the wifi off, and reports are client-side. A backend that exists only to be
switched off during the demo should not exist. So: **no backend in the MVP.**
Production architecture gets documented instead, and stays a slide.

**Also cut in this pass:** Next.js. There is no server, no SSR, no routing
requirement, no SEO. A static Vite build does the same job with a fraction of
the config.

Landing point: Vite + React + TypeScript + MapLibre + Tailwind, static JSON out
of the existing Python pipeline.

### Verify pass 1 — four faults

1. **The plan rendered data. The brief asked for a simulation.** "Simulate
   reports, show dark / not dark spatially, municipality report" is a *loop*,
   not a static map. Iteration 1 had no loop. This is the biggest miss of the
   whole exercise.
2. **`curve.json` is precomputed points.** If reports are simulated live, the
   Beta posterior has to update client-side. That is about twenty lines of TS
   and it makes the learning curve *interactive* instead of a chart.
3. **Tailwind does not earn its place.** The design system is already expressed
   as CSS custom properties — that is literally what `assets/design-system.png`
   specifies. Adding a utility framework to re-express tokens we already have is
   a build step for nothing.
4. **No output artifact.** See the contrarian research above.

### Added
- A live report-simulation slider, 0 → 400, re-running the posterior and the knapsack on every change.
- Client-side Beta update (`score.ts`).
- CSV work-order export.

### Subtracted
- The backend. Entirely.
- Next.js → Vite.
- Tailwind and shadcn → plain CSS custom properties.
- React Router → three tabs and a piece of state. Three screens is not a routing problem.

---

## Iteration 2 — after the simulation loop landed

Re-read against what is actually in `out/`.

### Verify pass 2 — four more faults

1. **The basemap was an unexamined assumption, and it breaks the offline rule.**
   Every plan so far said "MapLibre with a free raster basemap". Raster tiles
   are a network call. The demo is supposed to survive the wifi dying, and
   hackathon wifi dies.

   The fix is better than the problem: **we already have the entire road
   network.** `data/derived_bbox_ways.json` is every `highway` way over 126 km².
   Render it as the basemap — thin, desaturated, our own — and paint the scored
   segments on top. Offline, on-brand, one less dependency, and no tile
   provider to credit at demo time beyond the ODbL line we already owe.

2. **The route screen was going to be three canned journeys.** `out/routes.json`
   holds three precomputed pairs. A judge will want to click somewhere else, and
   "it's precomputed" is a bad sentence to say on stage.

   The demo graph is only ~2,100 segments. **Dijkstra in TypeScript over that is
   trivial** and it makes the duality *demonstrable live*: drag the darkness and
   desertedness weights and watch the safer route move. That is worth far more
   than three static routes, and it is cheaper than explaining the limitation.

3. **Uniformly random simulated reports would look fake and would waste the
   thesis.** Real reports do not arrive uniformly — they arrive from
   app-literate, affluent, car-owning wards. That is the entire argument of the
   project.

   So the simulation gets **two modes**: *"reports as they actually arrive"*,
   biased by activity, and *"reports we asked for"*, chosen by upper confidence
   bound. Watching the queue improve faster under targeting is the measured
   result from `out/curve.json`, live, on the map. This is the demo's best
   twenty seconds.

4. **The 7.7 MB GeoJSON would be loaded by a laptop mid-presentation.** Already
   solved on the pipeline side — `out/segments.demo.geojson` is 2,117 features
   and 1.5 MB — but the plan had not said which file the frontend loads. Now it
   does, explicitly, as part of the frozen contract.

### Added
- Basemap rendered from our own road data. New pipeline output: `out/basemap.geojson`.
- Client-side Dijkstra with live weights. New pipeline output: `out/graph.json`.
- Two simulation modes, biased vs targeted.
- The frozen four-file data contract.

### Subtracted
- Raster basemap tiles, and with them the last network call on the demo path.
- `out/routes.json` as a frontend input. It stays as the deck's evidence and as the bypass analysis; the screen computes its own routes now.

---

## Iteration 3 — cutting back

The plan had grown. This pass only removed things, except for one addition that
removes work elsewhere.

### Verify pass 3

1. **The learning-curve chart component is now dead weight.** It was a static
   picture of exactly what the report slider does live. Two ways to show one
   result is one too many. **Cut the component.** `out/curve.json` stays,
   because the deck needs it and the deck is not interactive.

2. **The telemetry viewer is a slide, not a screen.** `out/telemetry.json` proves
   the IUDX record shape. That claim lands better spoken over slide 14 than as
   a fourth tab nobody clicks. **Cut the screen, keep the file.**

3. **TypeScript: keep, but only where it pays.** The seam that historically
   breaks these builds is the data contract between pipeline and frontend, not
   component internals. So: one `types.ts` mirroring the schema, imported
   everywhere, and no crusade about strictness elsewhere. TS earns its place at
   exactly one boundary.

4. **React: keep.** Checked honestly against the ladder — the queue screen
   re-ranks a list live off four sliders while a map re-paints in sync. That is
   the case React is actually for. Vanilla would be a hand-rolled diff by hour
   three.

5. **One addition, because it deletes work:** the three screens share one
   `useMemo` over one scored-segments array. Queue sorts it, Route weights it,
   Report ranks it by report value. One computation, three consumers — no
   per-screen pipelines, no sync bugs between tabs.

6. **Named the order of abandonment**, because `docs/risks.md` says the way this
   project actually loses is time. Queue → sim slider → CSV → Route → Report.
   Never the queue.

### Added
- One shared scoring memo behind all three screens.
- An explicit abandonment order.

### Subtracted
- The learning-curve chart component.
- The telemetry viewer screen.
- Strict-mode TypeScript everywhere; kept at the data boundary only.

---

## Where it landed

| | Decision | Why |
|---|---|---|
| Pipeline | Python 3.12, pandas + networkx | Exists, works, no GDAL |
| Frontend | Vite + React + TS + MapLibre GL + plain CSS tokens | The re-ranking UI justifies React; nothing justifies a framework above it |
| Backend | **none in the MVP** | The demo must run offline; a backend that gets switched off should not be built |
| Basemap | our own road GeoJSON | Offline, on-brand, one less dependency |
| Routing | Dijkstra in TS over ~2,100 segments | Live weights beat canned routes and cost less than the caveat |
| State | `useState` + one `useMemo` | Three screens is not a state-management problem |
| Output | CSV work order | The answer to "dashboards are spectacles, not tools" |
| Production path | FastAPI + PostGIS + nightly pipeline + IUDX poller | Documented, not built. Honest, and it is the "integrates into government structures" answer |

Four things this deliberately does not build: an account system, a real backend,
a tile server, and a fourth screen. Each was considered and cut for a stated
reason above.

## Sources

- [FixMyStreet Platform, mySociety](https://www.mysociety.org/community/fixmystreet/) · [fixmystreet.org](https://fixmystreet.org/) — location-before-identity flow
- [NeighborFix civic reporting UX case study](https://medium.com/@aravindreddynusum/neighborfix-a-civic-app-designed-to-make-reporting-local-issues-simple-transparent-01ec9a981a47) — the 70%-wrong-channel and transparency findings
- [A dashboard by any other name, Katya Abazajian](https://www.civicsource.info/p/a-dashboard-by-any-other-name) — dashboards as spectacles rather than tools
- [What Does 'Failure' Mean in Civic Tech?, ACM Interactions](https://interactions.acm.org/archive/view/march-april-2024/what-does-failure-mean-in-civic-tech-we-need-continued-conversations-about-discontinuation) — discontinuation and integration failure
- [My failures: civic technology ideas that didn't quite work, Joshua Tauberer](https://medium.com/@joshuatauberer/my-failures-civic-technology-ideas-that-didn-t-quite-work-c73ecf730032)
- [Visualizing uncertainty for lines, Esri](https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/how-to-visualize-uncertainty-for-lines) · [The Visualization of Uncertainty, PSU GEOG 486](https://courses.ems.psu.edu/geog486/node/906) — extrinsic hatching, spacing conventions
- [maplibre-theme](https://github.com/lhapaipai/maplibre-theme) · [mapcn](https://next.jqueryscript.net/shadcn-ui/map-components-maplibre-gl/) — dark MapLibre controls if wanted
- [Dark dashboard practice roundup](https://adminlte.io/blog/dark-dashboard-templates/) — off-white text, surface elevation, saturation reserved for meaning
- Visual references: [map-apps](https://de.pinterest.com/conceptlz/map-apps/) · [map-ui](https://uk.pinterest.com/paulaengelbrech/map-ui/) · [Maps & Navigation](https://www.pinterest.com/dmpr0/maps-navigation/) — the pattern taken is the route-options comparison strip and the mobile bottom sheet


---

## Iteration 4 — building it, which overruled the plan twice

Iterations 1–3 were reasoning. This one is what happened when the thing got
built and run in a browser. Two of its findings contradict decisions made
above, and the build wins.

### Overruled #1 — React was over-built. It is one HTML file.

The plan justified React on "the queue re-ranks a list off four sliders while a
map repaints in sync — that is the case React exists for." Then the ladder got
applied properly: `web/index.html`, vanilla, ~520 lines including CSS, no build
step, no `node_modules` at runtime, two vendored MapLibre files.

Re-ranking 11,029 rows and repainting 2,117 features on every slider tick is a
`sort` and one `setData`. It is instant. There was never a diff to reconcile, so
there was never a case for a framework.

**Subtracted: React, Vite, TypeScript, and the whole build pipeline.** What
survives of the TypeScript argument is real — the data contract is the seam that
breaks — but the enforcement is now a `console.assert` on load rather than a
compiler.

### Overruled #2 — the app disagreed with the deck, and the plan caused it

First working version showed **6.5×** where the deck says 7.7×. Two causes,
both traceable to the plan:

1. **It scored the render subset.** §3 said load `segments.demo.geojson` — but that file is the top 2,000 by priority plus evidence-bearing segments. Scoring a set that was itself selected by priority inflates our side and deflates the ward pool the baseline draws from. Fix: a new geometry-free `out/scoring.json`, columnar, all 11,029 segments, 1.1 MB. Geometry is what makes GeoJSON large, so dropping it costs almost nothing. Render the subset, score everything.
2. **The sliders were a linear blend.** `wD·dark + wE·exposure + wC·conf` is a different objective from the pipeline's product, so the app's ranking could never agree with `repairPriority`. Fix: sliders are **exponents**, mapped `w → 2w`, so the 0.5 default is exponent 1 and the default objective is exactly the pipeline's. **7.6×.** Matches.

The general lesson, which is the same one from the mockup numbers: any second
implementation of the scoring rule will drift from the first. There is now one
objective, expressed twice, and a default that makes them provably equal.

### Six bugs the browser found that no amount of planning would have

| Symptom | Cause | Fix |
|---|---|---|
| Nothing renders, 3 console errors | `zoom` nested inside a multiply. MapLibre requires it directly under `step`/`interpolate` | darkness factor moved into the interpolate stop outputs |
| `does not provide an export named 'default'` | maplibre-gl v6 is ESM with named exports only | `import * as maplibregl` — and it needs a static server, `file://` will not load ES modules |
| Routing graph 8% connected | keyed on rounded coordinates — **the same bug that wrecked betweenness earlier in this project** | keyed on OSM node ids: 85% |
| Headline ratio drifting 7.6 → 7.9 between renders | unseeded `Math.random` in the Monte-Carlo baseline | seeded mulberry32. A number that changes on its own while a judge watches is worse than one that is slightly wrong |
| Wide-band count frozen at exactly a third of segments | counting a **rank-normalised** confidence against a percentile counts a fixed fraction by construction | absolute variance cut, fixed at load from the initial distribution |
| Detail panel invisible | no `z-index`; the MapLibre canvas painted over it | `z-index: 5` on the overlays |

The coordinate-keying one is worth dwelling on: it is the third time in this
project that keying spatial identity on rounded coordinates has silently
produced a broken graph. It should be a rule — **spatial joins key on ids, never
on rounded coordinates.**

### One visual finding

The first render looked like an ordinary road atlas. Darkness was encoded in
colour only, so with a mean P(dark) of 0.28 most segments drew in the pale end
of the ramp and the dark ones were a thin minority.

Fixed by making **width and opacity rise with darkness too**, so a lit street
recedes and a dark one shouts. The product is about finding dark streets; dark
has to be the loud state. Basemap dimmed to `#18202a` to get out of the way.

### What the build added that the plan did not have

Reports narrow confidence bands — they do not move the counterfactual ratio much,
because that ratio compares two orderings and both improve. So the readout for
the report slider is the **wide-band count**, and it makes the measured result
visible live:

| Simulated reports | Busy-after-dark segments still wide-band |
|---|---|
| 0 | 722 |
| 400, arriving as they actually do | 645 &nbsp;(−77) |
| 400, the ones we asked for | **564 &nbsp;(−158)** |

**Directed reporting clears twice as much uncertainty where it matters.** That is
`out/curve.json`'s finding, reproduced live on the map, and it is the twenty
seconds of the demo that kills the cold-start question.

### Verified by exercising it, not by looking at it

Driven through a real browser: determinism (same state twice, same ratio),
ordering toggle changes the top row, 40 rows render, both simulation modes
diverge, weights move the ranking, the detail panel populates nine real fields,
and the CSV export produces 40 rows with real segment ids, wards and streets.

Final stack: **Python pipeline → four static JSON files → one HTML file.** Two
vendored dependencies. Served by `python -m http.server`; no network call on the
demo path.
