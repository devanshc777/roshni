# Architecture

## The shape

```
   OSM walk graph ──┐
   BMTC GTFS ───────┤
   POIs (night) ────┼──► EXPOSURE MODEL ──┐
   Betweenness ─────┘      E(segment)     │
                                          ├──► TRIAGE OPTIMISER ──► queue
   Ward lamp density ─┐                   │      (budgeted knapsack)
   OSM street_lamp ───┼──► DARKNESS MODEL ┘
   OSM lit=* ─────────┤   Beta(α,β) per segment
   Citizen reports ───┘   mean = P(dark), var = confidence
                                          │
                                          └──► ROUTING GRAPH ──► safer route
```

Everything is keyed on **road segment**, not lamp, not point, not ward. One
join key, computed once. See `cold-start.md` for why the segment is the atom.

## Segmentation

Pull the walking network for the demo bbox:

```python
G = ox.graph_from_bbox(north, south, east, west, network_type="walk")
```

Split edges longer than ~150 m so a single long arterial edge does not average
away a dark stretch. Every downstream model attaches to `(u, v, key)`.

Lock the bbox in hour one. 3–4 km². Do not expand it. Ever.

## Darkness model — the weighting, in full

`Beta(α, β)` per segment. Prior from ward lamp density × road-class weight;
evidence from OSM `working` tags, `lit`, citizen reports, and — when access opens
— IUDX current draw. `cold-start.md` carries the reasoning; this is the
normative numeric spec.

**Prior**, deliberately weak (`K = 2`, so two real observations move it):

```
rel    = (ward_lamp_density / city_median_density) × class_weight[roadClass]
P(lit) = clamp(rel / (rel + 1), 0.1, 0.9)
α₀, β₀ = K·P(lit), K·(1 − P(lit))
```

`class_weight`: motorway 1.6, trunk 1.5, primary 1.4, secondary 1.2, tertiary
1.0, residential 0.7, service 0.4, footway 0.3.

**Evidence weights**, every one decayed by age:

| Evidence | w | → |
|---|---|---|
| IUDX telemetry, `current ≈ 0` after dusk | 2.0 | β |
| Repair confirmed by a reporter | 1.5 | α |
| OSM lamp `working=no` | 1.0 | β |
| OSM lamp `working=yes` | 1.0 | α |
| Citizen report "dark", corroborated | 1.0 | β |
| way `lit=no` | 0.8 | β |
| Citizen report "fine" | 0.7 | α |
| Citizen report "dark", single | 0.5 | β |
| OSM lamp, no `working` tag | 0.4 | α |
| way `lit=yes` | 0.3 | α |

**Time decay is not optional.** Half-life 30 days:

```
α = α₀ + Σ wᵢ · 2^(−Δtᵢ / 30)        (same for β)
mean = α / (α + β)                    ← darkness score
var  = αβ / ((α+β)²(α+β+1))           ← confidence band
```

Decay is what makes the model a live system rather than a snapshot, and it is
what lets a repair genuinely clear a segment: the old dark evidence fades while
the confirmed-fix event pushes α.

**Two asymmetries you must respect**, both from `measurements.md`:

- `lit=yes` outnumbers `lit=no` about 34:1. Mappers record lighting when it
  exists and stay silent when it does not, so **missing is not dark.** Never
  treat tag absence as evidence.
- The 1,173 `working`-tagged lamps are **survey-biased** — people mapped them
  *because* lights were broken. Use them as labels; never as a base rate. Hold
  ~200 out as a test set.

Two outputs, used everywhere: **posterior mean** = `P(dark)`, **posterior
variance** = confidence.

## Exposure model

> **MEASURED 22 Aug 2026 — this layer failed, and the failure is the better
> result.** Spearman ρ(activity, structural) = **+0.031** over 1,164 real
> segments; ρ(activity, night bus departures) = **−0.135**. Not a tie artefact
> (1,105 non-degenerate), not a broken graph (that bug was found and fixed
> first), same answer on arterials alone (ρ = 0.022). The two proxies are not
> two views of one latent footfall — they track two different night populations.
> Blending them evenly averages away the population this problem statement
> names, so the structural half now leads at 0.75. Read
> `docs/measured-2026-08-22.md` §5 before presenting this section.

`E(segment)` = night pedestrian exposure. Four inputs, deliberately split into
two disjoint groups so that convergent validation is possible (`validation.md`
Layer 1):

**Group A — activity.** POIs within a 100 m buffer whose `opening_hours` close
after 22:00, weighted by `user_ratings_total`. The night filter is the part that
matches the problem statement and the part other teams will skip.

**Group B — structure.** Edge betweenness centrality on the walk graph, plus
BMTC stop `trip_count` within 400 m with a distance decay. Pure topology and
transit service; no commercial data touches it.

Blend them for the production score, but **keep them computable separately** —
you need the two independent estimates for validation, and you need the
*disagreement* between them because that set is where dark transit-corridor
arterials live, which is precisely the population this problem statement names.

Residential population (WorldPop / HRSL) enters as a weak base term. It is who
sleeps there, not who walks; do not let it dominate.

## The duality — read this twice

Footfall plays **two contradictory roles** in this system:

- In the **repair queue**, footfall is *exposure*: more people at risk on a dark
  street ⇒ prioritise the repair.
- In the **routing engine**, footfall is *protection*: natural surveillance,
  eyes on the street ⇒ prefer this route.

Same variable, opposite sign, depending on which surface consumes it. If you use
it with the same sign in both, your model is internally contradictory and a sharp
judge will find it in thirty seconds — the tell is that your router will send a
woman down a brightly lit empty industrial road at 01:00 and rank it *safe*.

Build the duality in deliberately. Two derived scores from one exposure model:

```
repair_priority   ∝  P(dark) × E × unmet_time
route_penalty     ∝  P(dark) × (1 / (E + ε)) × uncertainty_penalty
```

Put this on a slide. It is your strongest intellectual differentiator and it
costs nothing but clear thinking. Jane Jacobs, *eyes on the street*, 1961 — cite
it, it lands.

While you are there: the empirical literature on lighting and crime is genuinely
mixed. A US randomised controlled trial found meaningful reductions; a UK study
of local-authority streetlight switch-offs found no increase in crime or road
collisions. Knowing the evidence is contested reads as maturity, not weakness,
and it inoculates you against the judge who was going to raise it.

## Exposure weighting

Rank-normalise each component to [0,1] — more robust than z-scores at this n —
then blend:

```
activity   = Σ_poi  night_open(poi) · log1p(user_ratings_total) · exp(−d/100)
structural = 0.6 · betweenness(edge) + 0.4 · Σ_stop trip_count · exp(−d/400)
residential= population within 500 m
E          = w_act·rank01(activity) + w_str·rank01(structural) + w_res·rank01(residential)
```

`night_open` = closing hour after 22:00. That filter is what makes this a *night*
exposure model rather than a generic POI density map, and it is the part most
teams skip.

Keep `activity` and `structural` separately in the output. Their agreement is the
convergent validation; their **disagreement** — structural high, activity low —
is where dark transit corridors through non-commercial land live, which is the
exact population the problem statement names.

## The two derived scores

```
confidence      = 1 − rank01(var)
urgency         = log1p(days_since_oldest_open_report)

repair_priority = E · darkness_mean · confidence · urgency
route_penalty   = lengthM · (1 + λ_d·darkness_mean + λ_e/(E + ε) + λ_u·var)
```

Note `E` multiplies in the first and **divides** in the second. That is the
duality, expressed numerically. If both had `E` in the numerator you have the bug
described above.

## The resolution loop

A report is not the end of a transaction. Two tables:

```
reports(id, segID, ts, kind, photo, device_hash, status)
resolutions(id, segID, ts, source: municipal|telemetry, verified: null|true|false, asks)
```

1. Report filed → β increases → the segment enters the queue, ranked by exposure rather than arrival time.
2. Closure arrives — municipality marks it fixed, or IUDX telemetry shows current returning after dusk.
3. **Verification**: ask the original reporter and the two nearest recent reporters, *"we're told this was fixed — is it?"*
4. Confirmed → `α += 1.5`, old β decays out, segment leaves the queue.
5. **Unconfirmed after two asks** → β holds, urgency escalates, segment flagged **"reported fixed, not verified."**

Step 5 is the feature. BBMP closes 96.4% of electrical complaints; Roshni is the
first thing that can ask **closed, or fixed?** A ward-level line reading *"11% of
closures were not verified by anyone on the ground"* is a metric a municipal
commissioner does not have today and would want immediately. One table and a
notification.

The citizen-facing half of the same loop: **watch a route** (notified when a
segment on your regular walk goes dark or gets fixed), a **night banner** after
21:00 that offers an alternative and never blocks, and **"your report moved 4th
Cross to #7 in this ward's queue"** — which is the only reason anyone files a
second report.

## Triage optimiser — the actual product

Not a heatmap. A budgeted selection problem.

```
maximise    Σ  E_i × P(dark)_i × confidence_i     over selected repairs i
subject to  Σ  cost_i  ≤  budget
```

Greedy by value-per-cost is fine at hackathon scale and is provably within a
factor of the optimum for the fractional relaxation. Twenty lines.

Then compute the same objective for the **complaint-log ordering** — the first
*n* segments by earliest `Grievance Date` from the BBMP grievances file — and
report the ratio:

> These 40 repairs restore 2.6× the exposed pedestrian-kilometres that the
> complaint queue's first 40 would have.

**That ratio is the product.** Everything else is the interface to it. If you
build only one thing in 24 hours, build this.

Expose `budget` as a slider and the three priority weights as sliders. It turns
"your weights are arbitrary" from an attack into "configurable by the
municipality," and it lets a judge poke the model live, which they love.

## Routing

**Use OSMnx + NetworkX. Do not use OSRM.**

OSRM needs a custom Lua profile and an `osrm-extract` / `osrm-contract` rebuild
on every weight change. That is a pipeline re-run per tweak and it will eat your
evening.

```python
for u, v, k, d in G.edges(keys=True, data=True):
    d["safety_weight"] = d["length"] * (1 + λ * route_penalty[(u, v, k)])
path = nx.shortest_path(G, orig, dest, weight="safety_weight")
```

Weights are hot-swappable at runtime, so you can re-route live while a judge
moves a slider. No turn-by-turn and slow on a full metro — both irrelevant inside
a 3 km² demo bbox.

Two rules the router must obey:

1. **Always show the shortest route alongside the safer one.** The user chooses.
   This is a product decision and a liability decision at the same time.
2. **Never route through a segment whose confidence band is wide.** Refusing to
   guess is the behaviour that makes the uncertainty model load-bearing rather
   than decorative.

## Surfaces

**Report.** One tap: "this stretch is dark." GPS, timestamp, optional photo. Its
empty state is the active-learning list — *streets worth checking tonight* —
which is what makes it a data-acquisition instrument rather than a suggestion
box.

**Route.** Two polylines, safer and shortest, with the darkness and confidence
of each rendered honestly.

**Queue.** The hero. Ranked worklist, budget slider, weight sliders, and the
counterfactual ratio in large type at the top. This is the screen a BBMP
executive engineer would actually open, and it is the one you demo first.

## Rendering and the demo path

Naive Leaflet polylines choke somewhere in the low thousands of segments. Either
clip hard to the demo bbox or use MapLibre / deck.gl with a GeoJSON source.

**Precompute everything to static GeoJSON.** No live API calls on the demo path
— not Overpass, not Places, not your own backend if you can avoid it. Hackathon
wifi dies at exactly the wrong moment and a demo that needs the network is a
demo that fails in front of judges. The sliders should recompute from data
already in the browser.

## Stack

Whatever your two developers are fastest in. Suggested, only because it minimises
integration risk:

- **Pipeline:** Python — `osmnx`, `networkx`, `geopandas`, `pandas`. One script,
  input files in, one GeoJSON out.
- **Frontend:** single-page, MapLibre GL, no framework required. Loads the
  precomputed GeoJSON, does the knapsack in JavaScript so sliders are instant.
- **Backend:** optional. If reports need to persist across devices, the smallest
  thing that works. If they do not, keep them client-side and spend the hours on
  the optimiser.

The integration seam that matters: **the pipeline's output GeoJSON schema.**
Freeze it in hour two, write a fixture file with ten fake segments in it, and let
the frontend developer build against the fixture while the pipeline is still
being written. Do this and the two halves meet on the first try.
