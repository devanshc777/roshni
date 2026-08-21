#!/usr/bin/env python
"""Roshni pipeline — real segments for the locked demo bbox.

Inputs (run data/fetch.py and data/snapshot_osm.py first):
  data/derived_bbox_ways.json    every way[highway] over the ward-union bbox,
                                 with OSM node ids and geometry
  data/derived_bbox_lamps.json   street_lamp nodes
  data/derived_bbox_pois.json    amenity / shop nodes
  data/derived_stops_bbox.json   BMTC stops with night-departure counts
  data/raw/streetlights_by_ward.csv, data/raw/bbmp_wards_2015.kml,
  data/raw/bbmp_grievances_2025.csv

Outputs:
  out/segments.geojson           scored segments, full schema
  out/segments.fixture.geojson   12 segments spanning the score range
  out/stats.json                 the numbers the deck quotes

Three geographies, on purpose:
  - the WALK GRAPH spans the whole snapshot, so betweenness is not truncated
    at an arbitrary edge;
  - SCORED SEGMENTS come from the locked demo bbox only — coverage is not the
    differentiator, and a 30k-feature GeoJSON kills the demo;
  - WARD ROAD-KM is measured over whole ward polygons from the drive network,
    because a lamp count divided by a clipped road length is a wrong prior.
"""
import json, math, re, csv, random
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
OUT = ROOT / "out"; OUT.mkdir(exist_ok=True)
random.seed(17)

# Locked demo bbox (docs/measurements.md). Segments are scored inside this only.
LOCK_S, LOCK_W, LOCK_N, LOCK_E = 12.90, 77.61, 12.97, 77.70

SPLIT_M = 150.0
CLASS_W = {"motorway":1.6,"motorway_link":1.6,"trunk":1.5,"trunk_link":1.5,
           "primary":1.4,"primary_link":1.4,"secondary":1.2,"secondary_link":1.2,
           "tertiary":1.0,"tertiary_link":1.0,"unclassified":0.9,"residential":0.7,
           "living_street":0.7,"service":0.4,"pedestrian":0.6,"footway":0.3,
           "path":0.3,"steps":0.3,"cycleway":0.4,"track":0.3}

# Ward lamp counts are returns for lit carriageways, not footpaths. Dividing a
# carriageway lamp count by a road length that includes every footway deflates
# the density prior badly, and silently. Drive classes only.
DRIVE = {"motorway","motorway_link","trunk","trunk_link","primary","primary_link",
         "secondary","secondary_link","tertiary","tertiary_link","unclassified",
         "residential","living_street"}
# Not walkable, so out of the walk graph entirely.
NO_WALK = {"motorway","motorway_link","construction","proposed","raceway","busway"}
# Scored-segment classes. Unnamed service roads and footways stay in the graph
# but are not ranked — a repair crew is not dispatched to an alley.
SCORED = DRIVE | {"pedestrian"}

K = 2.0
FULL_LAMPS_PER_KM = 1000/30      # 30 m standard pole spacing
LAMP_WORKS = 0.920               # Vasanthanagar 2019 panel: equilibrium dead 8.0%

# Night-activity weight by POI class. OSM records opening_hours for ~7% of POIs
# here, so an hours filter has almost no input — class is the proxy.
# Upgrade path: Google Places opening_hours + user_ratings_total, when funded.
NIGHT_POI = {
    "bar":1.0,"pub":1.0,"nightclub":1.0,"fast_food":0.9,"restaurant":0.8,
    "cafe":0.5,"hospital":0.9,"pharmacy":0.6,"fuel":0.8,"atm":0.5,
    "bus_station":0.9,"cinema":0.7,"marketplace":0.6,"convenience":0.6,
    "supermarket":0.4,"ice_cream":0.5,"food_court":0.7,"hotel":0.6,
}

# 2015-vintage KML ward names vs the free-text ward names in the grievance file.
# City-wide exact match is 99/198, which is why this is hand-built for the demo
# wards only (risks.md section 1) rather than a fuzzy match.
WARD_ALIAS = {"Bellanduru": "Bellandur", "Madivala": "Madiwala"}


# ---------- geometry (no geopandas, no GDAL: three formulas) ----------
def hav(a, b):
    (y1,x1),(y2,x2) = a, b
    p = math.pi/180
    dy, dx = (y2-y1)*p, (x2-x1)*p
    h = math.sin(dy/2)**2 + math.cos(y1*p)*math.cos(y2*p)*math.sin(dx/2)**2
    return 2*6371000*math.asin(math.sqrt(h))


def point_in_ring(y, x, ring):
    inside = False
    n = len(ring)
    for i in range(n):
        x1,y1 = ring[i]; x2,y2 = ring[(i+1) % n]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y-y1)*(x2-x1)/(y2-y1): inside = not inside
    return inside


def rank01(vals):
    """Rank-normalise to [0,1]. Ties share the mean rank."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0]*len(vals)
    i = 0
    while i < len(order):
        j = i
        while j+1 < len(order) and vals[order[j+1]] == vals[order[i]]: j += 1
        r = (i+j)/2 / max(1, len(vals)-1)
        for k in range(i, j+1): out[order[k]] = r
        i = j+1
    return out


def spearman(a, b):
    ra, rb = rank01(a), rank01(b)
    ma, mb = sum(ra)/len(ra), sum(rb)/len(rb)
    num = sum((x-ma)*(y-mb) for x,y in zip(ra,rb))
    den = math.sqrt(sum((x-ma)**2 for x in ra) * sum((y-mb)**2 for y in rb))
    return num/den if den else 0.0


class Grid:
    """Uniform spatial hash. Brute-force nearest-neighbour over tens of
    thousands of segments and points is minutes; this makes it seconds."""
    def __init__(self, pts, cell_deg=0.004):
        self.c = cell_deg
        self.g = {}
        for p in pts:
            self.g.setdefault((int(p[0]/self.c), int(p[1]/self.c)), []).append(p)

    def near(self, lat, lon, rings=1):
        ci, cj = int(lat/self.c), int(lon/self.c)
        for i in range(ci-rings, ci+rings+1):
            for j in range(cj-rings, cj+rings+1):
                yield from self.g.get((i, j), ())


# ---------- wards ----------
def load_wards():
    txt = (RAW/"bbmp_wards_2015.kml").read_text(encoding="utf-8", errors="replace")
    wards = []
    for pm in re.findall(r"<Placemark>(.*?)</Placemark>", txt, re.S):
        m = re.search(r"<Data name='Ward Name'>\s*<value>(.*?)</value>", pm, re.S)
        if not m: continue
        rings = []
        for co in re.findall(r"<coordinates>(.*?)</coordinates>", pm, re.S):
            ring = [(float(p[0]), float(p[1]))
                    for p in (t.split(",") for t in co.split()) if len(p) >= 2]
            if len(ring) > 3: rings.append(ring)
        if rings:
            xs = [x for r in rings for x, _ in r]; ys = [y for r in rings for _, y in r]
            wards.append((m.group(1).strip(), rings,
                          (min(ys), min(xs), max(ys), max(xs))))
    return wards


def ward_of(lat, lon, wards):
    for name, rings, (s, w, n, e) in wards:
        if not (s <= lat <= n and w <= lon <= e): continue    # bbox reject first
        for ring in rings:
            if point_in_ring(lat, lon, ring): return name
    return None


def load_ward_lamps():
    out = {}
    with open(RAW/"streetlights_by_ward.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            cnt = next((v for k, v in row.items() if k and "light" in k.lower()), "")
            try: out[(row.get("Ward Name") or "").strip()] = float(str(cnt).replace(",", ""))
            except ValueError: pass
    return out


def load_ward_complaints():
    """Street-light complaints per ward, 2025. Streetlight-only — the
    all-category counts tell a different story and must not be mixed in."""
    out = {}
    with open(RAW/"bbmp_grievances_2025.csv", encoding="utf-8",
              errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("Sub Category") == "Street Light Not Working":
                w = (row.get("Ward Name") or "").strip()
                out[w] = out.get(w, 0) + 1
    return out


# ---------- build ----------
def main():
    ways = json.loads((DATA/"derived_bbox_ways.json").read_text(encoding="utf-8"))
    lamp_nodes = json.loads((DATA/"derived_bbox_lamps.json").read_text(encoding="utf-8"))
    pois = json.loads((DATA/"derived_bbox_pois.json").read_text(encoding="utf-8"))
    stops = json.loads((DATA/"derived_stops_bbox.json").read_text(encoding="utf-8"))
    wards = load_wards()
    ward_lamps = load_ward_lamps()
    ward_complaints = load_ward_complaints()
    print(f"snapshot: {len(ways)} ways, {len(lamp_nodes)} lamps, {len(pois)} pois",
          flush=True)

    # ---- walk graph on real OSM node ids ------------------------------------
    # Rounded-coordinate keying fragmented this badly: real intersections are
    # shared NODES, and two ways crossing there only merge if their coordinates
    # round identically. Node ids make the junctions exact.
    G = nx.Graph()
    coord = {}
    for w in ways:
        if w["tags"].get("highway") in NO_WALK: continue
        nodes, geo = w.get("nodes") or [], w.get("geometry") or []
        if len(nodes) != len(geo) or len(nodes) < 2: continue
        for nid, g in zip(nodes, geo): coord[nid] = (g["lat"], g["lon"])
        for a, b in zip(nodes, nodes[1:]):
            if a == b: continue
            d = max(1.0, hav(coord[a], coord[b]))
            prev = G.get_edge_data(a, b)
            if prev is None or d < prev["length"]: G.add_edge(a, b, length=d)
    giant = max(nx.connected_components(G), key=len)
    print(f"walk graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
          f"giant {len(giant)} ({len(giant)/G.number_of_nodes():.0%})", flush=True)

    # Betweenness dominates runtime and only changes when the snapshot does.
    cache = DATA / "derived_betweenness.json"
    if cache.exists():
        bc_edge = {frozenset(map(int, k.split("_"))): v
                   for k, v in json.loads(cache.read_text()).items()}
        print(f"betweenness loaded from cache ({len(bc_edge)} edges)", flush=True)
    else:
        bc_raw = nx.edge_betweenness_centrality(G.subgraph(giant), k=min(500, len(giant)),
                                                weight="length", seed=17)
        bc_edge = {frozenset(e): v for e, v in bc_raw.items()}
        cache.write_text(json.dumps({f"{min(e)}_{max(e)}": v for e, v in bc_raw.items()}))
        print(f"betweenness computed and cached ({len(bc_edge)} edges)", flush=True)

    # ---- ward road-km, measured over whole ward polygons -------------------
    # No area x density constant any more. Every drive-class way in the
    # ward-union snapshot is assigned to a ward by its midpoint and its length
    # summed. The old approximation put BTM Layout at 108 lamps/km, which is
    # 9 m pole spacing and not real.
    ward_km = {}
    for w in ways:
        if w["tags"].get("highway") not in DRIVE: continue
        geo = w.get("geometry") or []
        if len(geo) < 2: continue
        pts = [(g["lat"], g["lon"]) for g in geo]
        L = sum(hav(pts[i], pts[i+1]) for i in range(len(pts)-1))
        mid = pts[len(pts)//2]
        wd = ward_of(mid[0], mid[1], wards)
        if wd: ward_km[wd] = ward_km.get(wd, 0.0) + L/1000

    # A ward straddling the snapshot edge has its road length clipped, which
    # inflates lamps/km without limit. Hoysala Nagar came out at 218 lamps/km
    # (4.6 m pole spacing) purely from clipping. Only trust wards whose whole
    # polygon is inside the snapshot; the rest take the median.
    SNAP_S, SNAP_W, SNAP_N, SNAP_E = 12.8862, 77.5926, 12.9751, 77.7108
    contained = {name for name, _, (s, w, n, e) in wards
                 if s >= SNAP_S and w >= SNAP_W and n <= SNAP_N and e <= SNAP_E}
    lamps_per_km = {w: ward_lamps[w]/km for w, km in ward_km.items()
                    if km > 1.0 and ward_lamps.get(w) and w in contained}
    med_lpk = (sorted(lamps_per_km.values())[len(lamps_per_km)//2]
               if lamps_per_km else FULL_LAMPS_PER_KM)
    print(f"ward road-km measured for {len(ward_km)} wards; "
          f"lamps/km median {med_lpk:.1f}", flush=True)

    # ---- segments, locked demo bbox only ----------------------------------
    segs = []
    for w in ways:
        cls = w["tags"].get("highway")
        if cls not in SCORED: continue
        nodes, geo = w.get("nodes") or [], w.get("geometry") or []
        if len(nodes) != len(geo) or len(nodes) < 2: continue
        pts = [(g["lat"], g["lon"]) for g in geo]
        c = pts[len(pts)//2]
        if not (LOCK_S <= c[0] <= LOCK_N and LOCK_W <= c[1] <= LOCK_E): continue
        name = w["tags"].get("name", "")
        run, runn, acc, part = [pts[0]], [nodes[0]], 0.0, 0
        for i in range(len(pts)-1):
            acc += hav(pts[i], pts[i+1]); run.append(pts[i+1]); runn.append(nodes[i+1])
            if acc >= SPLIT_M:
                segs.append({"segID": f"way{w['id']}/{part}", "pts": run, "nodes": runn,
                             "roadClass": cls, "name": name, "lengthM": round(acc, 1)})
                run, runn, acc, part = [pts[i+1]], [nodes[i+1]], 0.0, part+1
        if len(run) > 1 and acc > 15:
            segs.append({"segID": f"way{w['id']}/{part}", "pts": run, "nodes": runn,
                         "roadClass": cls, "name": name, "lengthM": round(acc, 1)})
    print(f"segments: {len(segs)} in the locked demo bbox", flush=True)

    # ---- evidence ---------------------------------------------------------
    lamps = [(l["lat"], l["lon"], (l.get("tags") or {}).get("working")) for l in lamp_nodes]
    lamp_grid = Grid(lamps)
    poi_pts = []
    for p in pois:
        t = p.get("tags", {})
        wt = NIGHT_POI.get(t.get("amenity")) or NIGHT_POI.get(t.get("shop"))
        if wt: poi_pts.append((p["lat"], p["lon"], wt))
    poi_grid = Grid(poi_pts)
    stop_pts = [(s["lat"], s["lon"], s["night_trips"]) for s in stops if s["night_trips"] > 0]
    stop_grid = Grid(stop_pts, cell_deg=0.008)

    for s in segs:
        mid = s["pts"][len(s["pts"])//2]
        s["mid"] = mid
        w = ward_of(mid[0], mid[1], wards) or "unknown"
        s["ward"] = w
        s["wardGrievanceName"] = WARD_ALIAS.get(w, w)
        s["lampsYes"] = s["lampsNo"] = s["lampsUntagged"] = 0
        for ly, lx, wk in lamp_grid.near(mid[0], mid[1]):
            if min(hav((ly, lx), p) for p in s["pts"]) <= 30:
                if wk == "yes": s["lampsYes"] += 1
                elif wk == "no": s["lampsNo"] += 1
                else: s["lampsUntagged"] += 1
        s["activity"] = sum(wt*math.exp(-hav((py, px), mid)/100)
                            for py, px, wt in poi_grid.near(mid[0], mid[1]))
        s["nightTransit"] = sum(n*math.exp(-hav((sy, sx), mid)/400)
                                for sy, sx, n in stop_grid.near(mid[0], mid[1]))
        vals = [bc_edge.get(frozenset((a, b)), 0.0)
                for a, b in zip(s["nodes"], s["nodes"][1:])]
        s["betweenness"] = sum(vals)/len(vals) if vals else 0.0
    print("evidence joined", flush=True)

    # ---- darkness ---------------------------------------------------------
    for s in segs:
        lpk = lamps_per_km.get(s["ward"], med_lpk) * CLASS_W.get(s["roadClass"], 0.8)
        coverage = min(0.95, lpk/FULL_LAMPS_PER_KM)
        lit_p = min(0.92, max(0.05, coverage*LAMP_WORKS))
        a, b = K*lit_p, K*(1-lit_p)
        # beta = dark. Snapshot evidence, so no time decay yet; decay switches
        # on when reports carry timestamps.
        a += 1.0*s["lampsYes"] + 0.4*s["lampsUntagged"]
        b += 1.0*s["lampsNo"]
        s["darkness"] = {"alpha": round(a, 3), "beta": round(b, 3),
                         "mean": round(b/(a+b), 4),
                         "var": round((a*b)/((a+b)**2*(a+b+1)), 5)}

    # ---- exposure: two disjoint halves, kept separate ---------------------
    act = rank01([s["activity"] for s in segs])
    bcr = rank01([s["betweenness"] for s in segs])
    ntr = rank01([s["nightTransit"] for s in segs])
    varr = rank01([s["darkness"]["var"] for s in segs])
    for i, s in enumerate(segs):
        structural = 0.6*bcr[i] + 0.4*ntr[i]
        # Measured on this corridor: rho(activity, structural) is ~0 and
        # rho(activity, night bus departures) is negative. The two halves are
        # NOT two proxies for one latent footfall -- they track two different
        # night populations. The problem statement names late-night COMMUTERS,
        # so the structural half leads; activity stays a minority term and a
        # slider.
        s["exposure"] = {"activity": round(act[i], 4),
                         "structural": round(structural, 4),
                         "blended": round(0.25*act[i] + 0.75*structural, 4)}
        s["confidence"] = round(1-varr[i], 4)
        s["repairPriority"] = round(s["exposure"]["blended"]*s["darkness"]["mean"]
                                    * s["confidence"], 5)
        s["routePenalty"] = round(s["lengthM"]*(1 + 1.5*s["darkness"]["mean"]
                                  + 0.3/(s["exposure"]["blended"]+1e-3)
                                  + 8.0*s["darkness"]["var"]), 1)
        s["reportValue"] = round(s["exposure"]["blended"]*s["darkness"]["var"], 5)

    rho = spearman([s["exposure"]["activity"] for s in segs],
                   [s["exposure"]["structural"] for s in segs])

    # ---- counterfactual --------------------------------------------------
    # Complaint order names a WARD, never a segment: the grievance file has no
    # coordinates and no pole ids. So the baseline is Monte-Carlo'd, and a
    # steelman that picks the worst segment per ward is reported alongside it.
    def restored(picked):
        return sum(s["exposure"]["blended"]*s["darkness"]["mean"]*s["lengthM"]
                   for s in picked)

    by_ward = {}
    for s in segs: by_ward.setdefault(s["ward"], []).append(s)
    cw = lambda w: ward_complaints.get(WARD_ALIAS.get(w, w), 0)
    complaint_wards = sorted((w for w in by_ward if cw(w) > 0), key=lambda w: -cw(w))

    ratios = {}
    for budget in (20, 40, 60):
        ours = restored(sorted(segs, key=lambda s: -s["repairPriority"])[:budget])
        draws = []
        for _ in range(300):
            picked, seen, i = [], set(), 0
            while len(picked) < budget and complaint_wards:
                w = complaint_wards[i % len(complaint_wards)]
                pool = [s for s in by_ward[w] if s["segID"] not in seen]
                if pool:
                    c = random.choice(pool); picked.append(c); seen.add(c["segID"])
                i += 1
                if i > budget*20: break
            draws.append(restored(picked))
        draws.sort()
        base = sum(draws)/len(draws)
        # Steelman: same complaint-driven ward order, but BBMP picks the single
        # worst segment inside each ward it visits. A coordinate-free complaint
        # log cannot actually do this, so it is the strongest possible version
        # of the status quo — quote this ratio when a judge pushes back.
        steel, seen, i = [], set(), 0
        while len(steel) < budget and complaint_wards:
            w = complaint_wards[i % len(complaint_wards)]
            pool = [s for s in by_ward[w] if s["segID"] not in seen]
            if pool:
                c = max(pool, key=lambda s: s["darkness"]["mean"]
                        * s["exposure"]["blended"]*s["lengthM"])
                steel.append(c); seen.add(c["segID"])
            i += 1
            if i > budget*20: break
        st = restored(steel)
        ratios[budget] = {
            "ours": round(ours, 1), "baselineMean": round(base, 1),
            "ratioMean": round(ours/base, 2) if base else None,
            "ratioVsLuckiestDraw": round(ours/draws[-1], 2) if draws[-1] else None,
            "baselineSteelman": round(st, 1),
            "ratioVsSteelman": round(ours/st, 2) if st else None,
            "baselineP5": round(draws[len(draws)//20], 1),
            "baselineP95": round(draws[-len(draws)//20], 1)}

    # ---- sensitivity: is the win an artefact of the lamp survey? ----------
    # All 1,128 labelled lamps sit in five wards. Our queue could be "finding"
    # the wards someone happened to survey rather than the wards that are dark.
    # Two checks, both of which have to hold or the headline ratio is inflated.
    surveyed = {s["ward"] for s in segs
                if s["lampsYes"] + s["lampsNo"] + s["lampsUntagged"] > 0}

    def counterfactual(pool, budget, key):
        ours_ = restored(sorted(pool, key=key, reverse=True)[:budget])
        bw = {}
        for s in pool: bw.setdefault(s["ward"], []).append(s)
        order = sorted((w for w in bw if cw(w) > 0), key=lambda w: -cw(w))
        if not order: return None
        draws = []
        for _ in range(150):
            picked, seen, i = [], set(), 0
            while len(picked) < budget:
                w = order[i % len(order)]
                left = [s for s in bw[w] if s["segID"] not in seen]
                if left:
                    c = random.choice(left); picked.append(c); seen.add(c["segID"])
                i += 1
                if i > budget*20: break
            draws.append(restored(picked))
        base = sum(draws)/len(draws)
        return round(ours_/base, 2) if base else None

    # A: same-ward comparison — only the five surveyed wards, so both sides see
    #    the same geography and evidence coverage cannot flatter us.
    in_surveyed = [s for s in segs if s["ward"] in surveyed]
    # B: evidence ablation — rank on the PRIOR ONLY, lamp tags thrown away. If
    #    the ordering still beats complaint order, the win comes from the
    #    exposure model rather than from happening to hold labels.
    prior_key = lambda s: (s["exposure"]["blended"]
                           * (1 - min(0.92, max(0.05,
                              min(0.95, lamps_per_km.get(s["ward"], med_lpk)
                              * CLASS_W.get(s["roadClass"], 0.8)/FULL_LAMPS_PER_KM)
                              * LAMP_WORKS)))
                           * s["lengthM"])
    sensitivity = {
        "surveyedWards": sorted(surveyed),
        "labelledLampsAllInNWards": len(surveyed),
        "ratio40_surveyedWardsOnly": counterfactual(
            in_surveyed, 40, lambda s: s["repairPriority"]),
        "ratio40_priorOnlyRanking": counterfactual(
            segs, 40, prior_key),
        "note": ("ratio40_surveyedWardsOnly holds geography and evidence coverage "
                 "constant on both sides. ratio40_priorOnlyRanking throws the lamp "
                 "tags away entirely and ranks on the ward prior plus exposure. "
                 "Both must beat 1.0 or the headline ratio is a coverage artefact.")}

    # ---- outputs ---------------------------------------------------------
    def feature(s):
        return {"type": "Feature",
                "geometry": {"type": "LineString",
                             "coordinates": [[p[1], p[0]] for p in s["pts"]]},
                "properties": {k: s[k] for k in ("segID","name","ward","roadClass",
                               "lengthM","darkness","exposure","confidence",
                               "repairPriority","routePenalty","reportValue")}
                 | {"evidence": {"osmLampsWorking": s["lampsYes"],
                                 "osmLampsBroken": s["lampsNo"],
                                 "osmLampsUntagged": s["lampsUntagged"],
                                 "nightBusTrips": round(s["nightTransit"], 1),
                                 "wardComplaints2025": cw(s["ward"]),
                                 "reports": 0}}}

    json.dump({"type": "FeatureCollection", "features": [feature(s) for s in segs]},
              open(OUT/"segments.geojson", "w"))
    ranked = sorted(segs, key=lambda s: -s["repairPriority"])
    n = len(ranked)

    # The full file is 7.7 MB / 11k features. MapLibre survives it; a hackathon
    # laptop parsing it while someone drags a slider does not. The demo file is
    # every evidence-bearing segment plus the top 2,000 by priority, coordinates
    # rounded to 5 dp (~1 m). Frontend loads this one.
    demo = {s["segID"]: s for s in ranked[:2000]}
    for s in segs:
        if s["lampsYes"] + s["lampsNo"] + s["lampsUntagged"] > 0:
            demo[s["segID"]] = s
    def thin(f):
        f["geometry"]["coordinates"] = [[round(x, 5), round(y, 5)]
                                        for x, y in f["geometry"]["coordinates"]]
        return f
    json.dump({"type": "FeatureCollection",
               "features": [thin(feature(s)) for s in demo.values()]},
              open(OUT/"segments.demo.geojson", "w"))
    print(f"demo file: {len(demo)} of {len(segs)} segments", flush=True)
    picks = [ranked[i] for i in (0, 1, 2, n//4, n//3, n//2, 2*n//3, 3*n//4, -3, -2, -1)]
    widest = max(segs, key=lambda s: s["darkness"]["var"])
    if widest not in picks: picks.append(widest)
    json.dump({"type": "FeatureCollection", "features": [feature(s) for s in picks]},
              open(OUT/"segments.fixture.geojson", "w"), indent=1)

    with_ev = sum(1 for s in segs if s["lampsYes"]+s["lampsNo"]+s["lampsUntagged"] > 0)
    scored_wards = {s["ward"] for s in segs}
    stats = {
      "lockedBbox": [LOCK_S, LOCK_W, LOCK_N, LOCK_E],
      "segments": len(segs),
      "demoSegments": None,   # filled after the demo file is written
      "totalCorridorKm": round(sum(s["lengthM"] for s in segs)/1000, 1),
      "waysInSnapshot": len(ways), "lampsInSnapshot": len(lamp_nodes),
      "lampsWorkingYes": sum(1 for l in lamps if l[2] == "yes"),
      "lampsWorkingNo": sum(1 for l in lamps if l[2] == "no"),
      "poisTotal": len(pois), "nightPOIs": len(poi_pts),
      "stopsWithNightService": len(stop_pts),
      # The stop snapshot spans the wider ward-union bbox so the 400 m transit
      # buffer is complete for segments at the locked bbox edge. The deck quotes
      # the LOCKED-bbox figures, so they are recomputed here and not inherited.
      "bmtcLockedBbox": {
          "stops": sum(1 for s in stops if LOCK_S <= s["lat"] <= LOCK_N
                       and LOCK_W <= s["lon"] <= LOCK_E),
          "departures": sum(s["trip_count"] for s in stops if LOCK_S <= s["lat"] <= LOCK_N
                            and LOCK_W <= s["lon"] <= LOCK_E),
          "nightDepartures": sum(s["night_trips"] for s in stops if LOCK_S <= s["lat"] <= LOCK_N
                                 and LOCK_W <= s["lon"] <= LOCK_E),
          "stopsWithNoNightService": sum(1 for s in stops if LOCK_S <= s["lat"] <= LOCK_N
                                         and LOCK_W <= s["lon"] <= LOCK_E
                                         and s["night_trips"] == 0)},
      "wardsScored": sorted(scored_wards),
      "graphNodes": G.number_of_nodes(), "graphEdges": G.number_of_edges(),
      "giantComponent": len(giant),
      "giantShare": round(len(giant)/G.number_of_nodes(), 3),
      "spearman_activity_vs_structural": round(rho, 3),
      "spearman_activity_vs_nightbus": round(spearman(
          [s["exposure"]["activity"] for s in segs],
          [s["nightTransit"] for s in segs]), 3),
      "segmentsWithLampEvidence": with_ev,
      "priorOnlyShare": round(1 - with_ev/len(segs), 3),
      "darknessMean": round(sum(s["darkness"]["mean"] for s in segs)/len(segs), 4),
      "wardRoadKm": {w: round(km, 1) for w, km in sorted(ward_km.items())
                     if w in scored_wards},
      "lampsPerKmByWard": {w: round(v, 1) for w, v in sorted(lamps_per_km.items())
                           if w in scored_wards},
      "counterfactual": ratios,
      "sensitivity": sensitivity,
    }
    json.dump(stats, open(OUT/"stats.json", "w"), indent=1)

    assert all(s["darkness"]["mean"] == s["darkness"]["mean"] for s in segs), "darkness NaN"
    assert 0 < ratios[40]["ratioMean"] < 20, "counterfactual ratio implausible"
    assert len(giant)/G.number_of_nodes() > 0.75, "walk graph still fragmented"

    print(json.dumps({k: v for k, v in stats.items()
                      if k not in ("wardsScored", "lampsPerKmByWard", "wardRoadKm")},
                     indent=1))
    print("\nlamps/km by scored ward:")
    for w in sorted(scored_wards):
        print(f"  {w[:22]:22s} roadKm={ward_km.get(w, 0):7.1f} "
              f"lamps={int(ward_lamps.get(w, 0)):6d} "
              f"lpk={lamps_per_km.get(w, float('nan')):6.1f}")
    print("\ntop 10 by repairPriority:")
    for s in ranked[:10]:
        print(f"  {s['repairPriority']:.4f}  {s['name'][:26]:26s} {s['ward'][:16]:16s} "
              f"dark={s['darkness']['mean']:.2f} exp={s['exposure']['blended']:.2f} "
              f"conf={s['confidence']:.2f} lamps={s['lampsYes']}y/{s['lampsNo']}n")


if __name__ == "__main__":
    main()
