# OSM / Overpass queries

**Run these in hour one, before you write any modelling code.** Two of the
numbers below are load-bearing for the entire pitch, and if they come back near
zero you want to know at H1, not H16.

**These were run on 21 Aug 2026 and the results are in `docs/measurements.md`.**
Re-run Q1 and Q2 against your locked bbox to confirm — the pitch quotes them —
but you are confirming known numbers, not discovering unknown ones.

| Measured, ORR demo bbox `12.90,77.61,12.97,77.70` | |
|---|---|
| `highway=street_lamp` | **1,211** |
| ways with any `lit` tag | **630** of **15,384** (4.1%), of which `lit=yes` **612** |
| `highway=bus_stop` | **303** |
| `highway=footway` | **1,885** |
| lamps city-wide with `working=yes/no` | **1,173** (658 no, 515 yes) |

Endpoint: `https://maps.mail.ru/osm/tools/overpass/api/interpreter` (POST the query as the `data`
form field). Mirror if it is slow: `https://overpass.kumi.systems/api/interpreter`.
Free, no key, ODbL — attribute if you ship anything public.

Interactive: [overpass-turbo.eu](https://overpass-turbo.eu) — paste, hit run, see
it on a map. Use this for the counting queries; use the CLI for the extracts.

---

## Q1 — The number that decides your darkness layer

How many mapped street lamps exist in Bengaluru at all?

```
[out:json][timeout:120];
node["highway"="street_lamp"](12.83,77.45,13.14,77.78);
out count;
```

And in your actual demo bbox — replace with your locked coordinates:

```
[out:json][timeout:120];
node["highway"="street_lamp"]({{bbox}});
out count;
```

**Interpretation, decided in advance so you are not rationalising at 3am:**

| Count in bbox | What it means | What you do |
|---|---|---|
| > 500 | Real coverage | Lamps are direct evidence in the Beta update. Say so. |
| 50–500 | Patchy, usable | Evidence where present, prior elsewhere. |
| < 50 | Effectively absent | Prior-only darkness layer. **Say this on stage**, do not hide it. |

**Measured: 1,211 in the ORR bbox — the top row.** Lamps are direct evidence.

Also pull the `working` tag, which is the find nobody expects:

```
[out:json][timeout:120];
node["highway"="street_lamp"]["working"="no"]({{bbox}});
out count;
```

658 `working=no` and 515 `working=yes` city-wide. That is a labelled dependent
variable — hold ~200 out as a test set rather than fitting on all of them.

## Q2 — The `lit` tag, before you build on it

```
[out:json][timeout:120];
way["highway"]["lit"](12.83,77.45,13.14,77.78);
out count;
```

Compare against total highway ways in the same bbox:

```
[out:json][timeout:120];
way["highway"](12.83,77.45,13.14,77.78);
out count;
```

**Measured at 4.1% in the demo bbox — above the "do not build on it" line, but
note the asymmetry: `lit=yes` outnumbers `lit=no` roughly 34:1.** Mappers record
lighting when it exists and stay silent when it does not, so **absence of the tag
tells you nothing.** Weak positive evidence for `lit=yes`, strong negative for
`lit=no`, and missing is never dark.

**If `lit` coverage were under ~2% of ways — the usual result for Indian
cities — you would not make it a primary input at all.** A scoring formula whose main variable
is an empty column is how teams lose. Use it as weak evidence in the Beta update
and nothing more. Twenty minutes of counting here saves eight hours of building
on sand.

## Q3 — Extract the lamps you do have

```
[out:json][timeout:180];
(
  node["highway"="street_lamp"]({{bbox}});
  node["lamp_mount"]({{bbox}});
);
out body geom;
```

Check whether any carry `operational_status`, `lamp_type`, `support`, or
`ref` — Bengaluru's surveyed areas may. Those become your held-out labels.

## Q4 — Night-relevant POIs

The night filter is the part that matches this problem statement and the part
other teams will skip.

```
[out:json][timeout:180];
(
  nwr["amenity"~"^(bar|pub|restaurant|cafe|fast_food|hospital|clinic|pharmacy|fuel|atm|bank|police|cinema|nightclub|bus_station)$"]({{bbox}});
  nwr["shop"]({{bbox}});
  nwr["opening_hours"~"2[2-4]:|00:|01:|02:"]({{bbox}});
);
out center tags;
```

OSM `opening_hours` coverage in India is thin, which is why Google Places
(`docs/data-sources.md` §C2) carries the night filter in practice. Pull the OSM
set anyway — it is free, it needs no key, and it is the fallback if the Places
key becomes a problem at 2am.

## Q5 — Transit and pedestrian infrastructure

```
[out:json][timeout:180];
(
  node["highway"="bus_stop"]({{bbox}});
  node["public_transport"="platform"]({{bbox}});
  node["railway"="station"]({{bbox}});
  way["highway"="footway"]({{bbox}});
  way["footway"="sidewalk"]({{bbox}});
);
out body geom;
```

`sidewalk` coverage will be poor. That is itself a finding worth a sentence — a
lit road with no walkable footpath is not a safe pedestrian route, and you have
no data for it. Name it as known-unmodelled (`docs/risks.md` §12); it reads as
someone who has walked the city rather than only queried it.

## Q6 — Ward road length, for the density prior

You need total road-kilometres per ward to turn published lamp counts into
lamps-per-km (`docs/cold-start.md`). Do this in OSMnx rather than Overpass — it
gives you edge lengths directly:

```python
import osmnx as ox, geopandas as gpd

G = ox.graph_from_polygon(ward_polygon, network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False)
road_km = edges["length"].sum() / 1000
density = published_lamp_count / road_km      # lamps per km, per ward
```

Use `network_type="drive"` for the *denominator* — published lamp counts are for
lit carriageways, and the `walk` network includes footpaths and pedestrian ways
that were never lamped by the same programme. Mixing these up deflates your
density by a large factor and it is a silent error.

Use `network_type="walk"` for the *model graph*. Two different graphs, two
different purposes. Do not reuse one for the other.

## Rate limits and courtesy

**Overpass returns an XML error body under load, not JSON.** Two of my calls hit
this. Wrap every request in a retry that checks whether the response starts with
`<` and backs off ~4 seconds:

```python
def overpass(q, tries=3):
    for _ in range(tries):
        r = requests.post(URL, data={"data": q}, timeout=180)
        if r.text.lstrip().startswith("<"):
            time.sleep(4); continue
        return r.json()
    raise RuntimeError("overpass retries exhausted")
```

Overpass is donated infrastructure. Cache every response to disk on first fetch
and never re-query the same thing in a loop — a hackathon team hammering the
public endpoint gets rate-limited at exactly the wrong hour.

```python
import osmnx as ox
ox.settings.use_cache = True
ox.settings.cache_folder = "data/raw/osm_cache"
```

For anything bigger than a city, use a Geofabrik `.osm.pbf` extract instead of
Overpass. You will not need to — your bbox is 3 km² and locked.
