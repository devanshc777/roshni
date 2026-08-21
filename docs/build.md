# Build doc — start here

Concrete order, real commands, working skeletons. Read `mvp.md` for scope and
`architecture.md` for why; this is the how.

Everything assumes the demo bbox from `measurements.md`:

```python
BBOX = (12.97, 12.90, 77.70, 77.61)   # north, south, east, west  — ORR / Bellandur–HSR
```

---

## H0 — environment, 15 minutes, do it before anything else

```bash
python -m venv .venv && . .venv/Scripts/activate      # Windows; use bin/activate elsewhere
pip install osmnx networkx geopandas shapely pandas pyproj requests fiona
python -c "import osmnx, networkx, geopandas; print('ok')"
```

`geopandas` on Windows can fight you over GDAL. If `pip` struggles, do not debug
it at hour zero — `pip install pipwin && pipwin install gdal fiona` or just use
conda. Budget fifteen minutes and move on; **losing an hour to GDAL is a real way
teams lose.**

```bash
python data/fetch.py           # pulls every source in data/manifest.json
```

If OpenCity is unreachable, open the URLs from `manifest.json` in a browser and
save to the paths listed. Do not burn hours on someone else's TLS config.

---

## H1 — verify the two load-bearing numbers

The pitch quotes both. Confirm them before building on them.

**Number one — lamps in the bbox.** Expect ~1,211.

```python
import requests
Q = '[out:json][timeout:120];node["highway"="street_lamp"](12.90,77.61,12.97,77.70);out count;'
r = requests.post("https://overpass-api.de/api/interpreter", data={"data": Q}, timeout=180)
print(r.json()["elements"][0]["tags"])
```

**Number two — the complaint share.** Expect ~31.4%.

```python
import pandas as pd
g = pd.read_csv("data/raw/bbmp_grievances_2025.csv")
sl = g[g["Sub Category"] == "Street Light Not Working"]
print(len(g), len(sl), f"{len(sl)/len(g):.1%}")
print(sl.groupby("Ward Name").size().sort_values(ascending=False).head(10))
```

If either number is materially different, you have twenty-three hours to adjust
the pitch instead of seven.

---

## H1–H2 — freeze the seam

The single highest-return hour of the night. **D1 and D2 together**, write the
output schema and a fixture, then split.

```bash
mkdir -p out
```

`out/segments.fixture.geojson` — ten hand-written features in the exact shape
from `mvp.md` §The data contract. D2 builds against this all night and never
waits for the pipeline. Do this and the two halves meet on the first try.

---

## H2–H4 — the graph and the segments

```python
import osmnx as ox, geopandas as gpd
ox.settings.use_cache = True
ox.settings.cache_folder = "data/raw/osm_cache"

N, S, E, W = 12.97, 12.90, 77.70, 77.61

G_walk  = ox.graph_from_bbox(bbox=(W, S, E, N), network_type="walk")   # the model graph
G_drive = ox.graph_from_bbox(bbox=(W, S, E, N), network_type="drive")  # for ward road-km ONLY

edges = ox.graph_to_gdfs(G_walk, nodes=False).reset_index()
edges["segID"] = edges["u"].astype(str) + "/" + edges["v"].astype(str) + "/" + edges["key"].astype(str)
```

Two different graphs, two different purposes. **Do not reuse one for the other** —
the published lamp counts are for lit carriageways, so using the walk network
(which includes footpaths never lamped by that programme) as the density
denominator deflates the prior badly, and it is a silent error.

Split anything over ~150 m so one long arterial edge cannot average away a dark
stretch.

---

## H3–H5 — darkness prior and evidence

**Prior.** Ward lamp count ÷ ward road-km → lamps/km, distributed by road class.

```python
CLASS_W = {"motorway":1.6,"trunk":1.5,"primary":1.4,"secondary":1.2,
           "tertiary":1.0,"residential":0.7,"service":0.4,"footway":0.3}

K = 2.0     # pseudo-count. Deliberately weak: two observations should move it.

def prior(seg, ward_density, city_median_density):
    rel = (ward_density / city_median_density) * CLASS_W.get(seg.highway, 0.8)
    lit_p = min(0.9, max(0.1, rel / (rel + 1)))     # expected P(lit)
    return K * lit_p, K * (1 - lit_p)               # alpha0, beta0
```

**Evidence.** Pull the labelled lamps — this is the part most teams do not have:

```python
Q = '''[out:json][timeout:180];
node["highway"="street_lamp"](12.90,77.61,12.97,77.70);
out body;'''
# tags carry working=yes|no on ~20% of them. Snap each node to its nearest edge
# within 25 m, then accumulate.
```

Weights, with **exponential time decay, half-life 30 days**:

| Evidence | Weight | Into |
|---|---|---|
| IUDX telemetry, `current≈0` after dusk | 2.0 | β |
| Repair confirmed by a reporter | 1.5 | α |
| OSM lamp `working=no` | 1.0 | β |
| OSM lamp `working=yes` | 1.0 | α |
| Citizen report "dark", corroborated | 1.0 | β |
| way `lit=no` | 0.8 | β |
| Citizen report "fine" | 0.7 | α |
| Citizen report "dark", single | 0.5 | β |
| OSM lamp, no `working` tag | 0.4 | α |
| way `lit=yes` | 0.3 | α |

```python
import math
HALF_LIFE_DAYS = 30.0

def posterior(a0, b0, evidence, now):
    a, b = a0, b0
    for w, side, ts in evidence:
        decay = 2 ** (-((now - ts).days) / HALF_LIFE_DAYS)
        if side == "alpha": a += w * decay
        else:               b += w * decay
    mean = a / (a + b)
    var  = (a * b) / ((a + b) ** 2 * (a + b + 1))
    return {"alpha": a, "beta": b, "mean": mean, "var": var}
```

`mean` is darkness (flip the sign convention once and stick to it — β is dark).
`var` is the confidence band, and it is load-bearing: the router refuses wide
bands, the report screen targets them.

Note the asymmetry from `measurements.md`: `lit=yes` outnumbers `lit=no` ~34:1,
so **absence of the tag means nothing.** Never treat missing as dark.

**Hold out ~200 of the 1,173 labelled lamps as a test set.** Do not fit on all of
them and then quote accuracy against them.

---

## H4–H6 — exposure, two disjoint halves

```python
import networkx as nx

# structural: pure topology + transit. No commercial data touches this.
bc = nx.edge_betweenness_centrality(nx.Graph(G_walk), k=300, weight="length")  # k = sampling
# + BMTC stops within 400 m, weighted by trip_count with distance decay
```

```python
# activity: night-open POIs, weighted by revealed preference
#   score = Σ  night_open(poi) · log1p(user_ratings_total) · exp(-d/100)
# night_open = closing hour after 22:00. This filter is the part that matches
# the problem statement and the part other teams skip.
```

Rank-normalise each to [0,1] rather than z-scoring — more robust at this n.

```python
E = w_act * rank01(activity) + w_str * rank01(structural) + w_res * rank01(residential)
```

**Keep `activity` and `structural` in the output separately.** You need both for
convergent validation (`validation.md` Layer 1), and their disagreement set —
structural high, activity low — is where dark transit corridors through
non-commercial land live. That is the population the problem statement names, and
surfacing it is a slide.

---

## H6–H8 — the two derived scores

Same exposure, opposite signs. This is `architecture.md` §The duality; if you get
it wrong the router will call an empty lit industrial road safe.

```python
confidence = 1 - rank01(var)
urgency    = math.log1p(days_since_oldest_open_report)

repair_priority = E * darkness_mean * confidence * urgency

route_penalty   = length_m * (1
                  + LAM_D * darkness_mean          # dark is costly
                  + LAM_E / (E + 1e-3)             # deserted is costly  ← inverted
                  + LAM_U * var)                   # unknown is costly
```

---

## H8–H10 — the triage optimiser. This is the product.

```python
def triage(segments, budget, cost=lambda s: 1.0):
    ranked = sorted(segments, key=lambda s: s["repairPriority"] / cost(s), reverse=True)
    picked, spent = [], 0.0
    for s in ranked:
        if spent + cost(s) > budget: continue
        picked.append(s); spent += cost(s)
    return picked

def restored(picked):
    return sum(s["exposure"]["blended"] * s["darkness"]["mean"] * s["lengthM"] for s in picked)
```

The counterfactual — the number the whole deck lands on:

```python
complaints = (pd.read_csv("data/raw/bbmp_grievances_2025.csv")
                .query('`Sub Category` == "Street Light Not Working"')
                .sort_values("Grievance Date"))
baseline = segments_for_first_n_complaints(complaints, n=budget)
ratio = restored(triage(segments, budget)) / restored(baseline)
print(f"{ratio:.1f}x")
```

**If the night collapses, ship this and nothing else.**

---

## H10–H14 — routing, and the resolution loop

```python
for u, v, k, d in G_walk.edges(keys=True, data=True):
    d["safety_weight"] = route_penalty[(u, v, k)]

safer    = nx.shortest_path(G_walk, orig, dest, weight="safety_weight")
shortest = nx.shortest_path(G_walk, orig, dest, weight="length")
```

Both, always, side by side. Never route through a wide-band segment. **Not
OSRM** — a custom Lua profile means an `osrm-extract` / `osrm-contract` rebuild on
every weight change, and you will not survive that.

Resolution loop — one table, and it produces the sharpest metric in the project:

```
reports(id, segID, ts, kind, photo, device_hash, status)
resolutions(id, segID, ts, source: municipal|telemetry, verified: null|true|false, asks: int)
```

Closure → ask the original reporter plus the two nearest recent ones. Confirmed →
α += 1.5 and old β decays fast. **Unconfirmed after two asks → flag "reported
fixed, not verified."** BBMP closes 96.4% of electrical complaints; Roshni is the
first thing that can ask *closed, or fixed?* See `PLAN.md` §5.

---

## H14–H18 — export and precompute

```python
import json
feats = [{"type":"Feature","geometry":mapping(s.geometry),"properties":props(s)} for s in segs]
json.dump({"type":"FeatureCollection","features":feats}, open("out/segments.geojson","w"))
```

Also emit `out/curve.json` — triage ratio at 0 / 25 / 100 / 400 reports — for the
learning-curve panel.

**Everything precomputed. No Overpass call, no Places call, no backend round-trip
on the demo path.** The sliders recompute the knapsack in JavaScript from data
already in the browser. Hackathon wifi fails at exactly the wrong moment.

---

## Frontend

MapLibre GL, GeoJSON source, no framework required. Naive Leaflet polylines choke
in the low thousands of segments — you will have more than that. Knapsack in JS
so sliders are instant.

See `docs/prompts.md` for generating the three screens.

---

## Sanity assertions — write these, they cost one line each

```python
assert len(merged) == len(edges),        "ward join dropped rows — see risks.md §1"
assert segments["darkness"].notna().all(), "prior failed to cover some segments"
assert 0 <= ratio < 20,                   "counterfactual ratio implausible — check the baseline"
assert holdout_auc > 0.6,                 "darkness model no better than coin flip on held-out lamps"
```

The ward-name join is the one that will actually bite. Grievances key on free-text
`Ward Name`, transliterated Kannada has multiple accepted spellings, and BBMP
re-delimited 198 → 243 wards in 2023. **Use the 2015 / 198-ward vintage
throughout** and hand-build the crosswalk for your demo wards only — five to
eight wards, ten minutes with a spreadsheet, assigned to a non-developer.

---

## Order of abandonment

If you are behind at H14, drop in this order and no other:

1. The learning-curve panel
2. Residential population layer
3. Google Places activity (fall back to OSM POIs — `overpass.md` Q4)
4. Routing screen
5. Report screen

**Never** drop the queue screen or the counterfactual. That is the project.
