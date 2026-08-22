# Roshni

**The streetlight repair queue, reordered by who is actually walking.**

Hackathon project, 24 hours, team of 4 (2 developers). Problem statement 17 —
Smart Cities, Night-Safety Dark-Zone Mapper. Lives under `C:\Dev\hackathon\`.

## Status

**Measured and running, 22 Aug 2026.** All 23 sources are downloaded
(`data/raw/`), `data/pipeline.py` produces 1,164 real segments, and the deck
numbers are computed. **`docs/measured-2026-08-22.md` is the authority on every
number** — where an older doc disagrees, that file wins. Three things remain
unmeasured and are flagged as such: criterion validation against the BTP crash
PDFs, field pedestrian counts, and the team's own seed reports.

**OSM coverage is measured** (21 Aug 2026, `docs/measurements.md`) — 1,211
street lamps in the ORR demo bbox, 5,874 city-wide, and **1,173 carrying a
`working=yes/no` label**, which is a real dependent variable. Electronic City has
four, so it is the production-integration story and not the demo geography.

**Verified**: 39,847 of 126,974 = **31.38%**, recomputed from the raw CSV.
Electrical closure rate **96.4%** confirmed exactly. The counterfactual is
computed: **7.73×** at a 40-repair budget, **1.89×** against a steelman
baseline, and **5.42×** with every lamp label deleted. (The earlier 5.2× / 1.58×
figures predate the full-bbox pipeline rebuild — see `measured-2026-08-22.md` §10.)

**Two claims died on measurement** and must not reach a slide: the
office-hours-timestamp argument (the grievance clock is 12-hour with AM/PM
stripped) and convergent validation (Spearman ρ = 0.03 — it failed, and the
failure is the better story). Both are written up in `docs/measured-2026-08-22.md`.

## The one-sentence thesis

BBMP closes 96.4% of electrical complaints — they are good at *fixing* and bad at
*ordering*, because the queue is sorted by who complained first, and complaining
correlates with affluence and app-literacy rather than with how many people walk
that street at 11pm. Roshni re-sorts the queue by pedestrian exposure.

## Read before acting

| File | What it is |
|---|---|
| `PLAN.md` | **The spine.** Is it a real problem, the insight, have-vs-gated, architecture, the resolution loop, defensibility, thought process. Read this first. |
| `README.md` | The public face. The thesis, the three screens, quickstart. |
| `PRODUCT.md` | Product truth: who it is for, what the deliverable actually is, what we deliberately are not building. |
| `docs/mvp.md` | **Scope contract.** What ships in 24 hours, the frozen data schema, the build order, definition of done. If it is not in here it is not in the build. |
| `docs/build.md` | **How to start building.** Commands, order, working code skeletons, sanity assertions, order of abandonment. |
| `docs/measured-2026-08-22.md` | **Authority on every number.** Confirmed / corrected / dead, plus the counterfactual and the infrastructure gotchas. Read before quoting anything. |
| `docs/ps-adherence.md` | **Audit against the problem-statement text**, not our narrative. What the PS names vs what exists, the generality claim as an input ladder, the product story, and why the citizen screens must be plain. |
| `docs/positioning.md` | Positioning via competitive alternatives. The category is "repair-prioritisation layer for street lighting" — a layer, not a replacement. Carries the one-liner and the pitch opening. |
| `docs/deploy.md` | **How to run and deploy it.** Local server is the demo path; GitHub Pages is the backup, with the one manual settings step. |
| `docs/reimagine-report.md` | **What is built now**, screen by screen, with screenshots and the provenance of every on-screen number. Start here for the current state. |
| `docs/reimagine-demo.md` | **The demo script.** Four clicks, what to say per beat, the questions you will get, and the traps. |
| `docs/reimagined-plan.md` | The presentation rebuild: the diagnosis, the plan, and what a three-lens review round changed before and during the build. |
| `docs/mvp-plan.md` · `docs/mvp-plan-log.md` | The build plan and the four verification passes behind it, including the two places building it overruled the plan. |
| `web/index.html` | **The working app.** Four tabs — Live feed, Walk home, Report, City queue. Vanilla, one file, offline, responsive. `python -m http.server 8080 --directory web`. |
| `PRODUCT.md` | Product truth: the two sides (customer vs user), the use scene that decides the design, the surface table, and the product rules. |
| `assets/diagrams.py` | Renders the two deck diagrams from `out/stats.json` so they cannot drift. |
| `docs/deck-start-here.md` | **Onboarding for the non-developers.** Setup, read order, build order, who-does-what, the eight key takeaways, the six traps that get you caught, definition of done. Point deck teammates here first. |
| `docs/ppt.md` | **Build the deck from this.** Verbatim slide copy for all 16 slides, visual system, per-slide do/do-not notes, asset checklist, number provenance, generator prompts, QA pass. Non-developer can finish the deck from this file alone. |
| `docs/deck-outline.md` | The reasoning behind the deck — why each slide exists. `ppt.md` is the buildable version. |
| `data/pipeline.py` | Builds `out/segments.geojson` (1,164 segments), the fixture, and `out/stats.json`. pandas + networkx only — no GDAL. |
| `docs/measurements.md` | Measured OSM coverage. Real Overpass counts, dated. Settles the demo bbox. |
| `docs/prompts.md` | UI generation prompts for v0 / Lovable / Bolt, with references and the post-generation pass. |
| `docs/verdict.md` | Honest read on whether this problem statement was a good pick and where the marks actually are. |
| `docs/data-sources.md` | **The manifest.** Every source, exact download URL, schema, reliability grade, and what it can and cannot support. Start here. |
| `docs/national-data-landscape.md` | What MoHUA / ICCC / NUDM / IUDX actually publish versus hold. Settles the "all 100 Smart Cities have mapped assets" claim, and carries the IUDX record schema we build against. |
| `docs/validation.md` | The answer to the challenge question, as an architecture rather than a source list. |
| `docs/architecture.md` | System design. The darkness model, the exposure model, the triage optimiser, the routing graph. |
| `docs/cold-start.md` | How the thing works on day zero with no lamp inventory and no reports. The hardest question we will be asked. |
| `docs/risks.md` | Ranked landmines with mitigations. Read this before writing code, not after. |
| `docs/timeline.md` | H0–H24 with role allocation for four people, two of whom do not write code. |
| `docs/pitch.md` | Demo script and judge Q&A prep. |
| `data/manifest.json` | Machine-readable source list. |
| `data/fetch.py` | Downloads everything in the manifest. Run it first. |
| `data/overpass.md` | OSM queries. Run these before believing anything about lamp coverage. |

## Conventions

Prose over bullets in the docs. Numbers get a source or a "verify this" flag —
never a bare assertion. When something is unmeasured, say **unmeasured** rather
than rounding it into a claim; the pitch is stronger for it and a judge will find
the gap anyway.

Data contract: the lamp and telemetry records are **IUDX-shaped on purpose**
(`deviceID` + GeoJSON `Point`), so "we plug into the municipal feed the day
access is granted" is literally true rather than hand-waving. Do not redesign
those two record shapes for convenience.

Scope discipline: **one city, one demo bbox, locked in hour one.** Every hour
spent widening coverage is an hour not spent on the triage optimiser, which is
the only part of this that is actually novel.
