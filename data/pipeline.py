#!/usr/bin/env python
"""Roshni pipeline — real segments for the demo sub-bbox.

Inputs are already on disk (see fetch.py and the derived_*.json snapshots):
  data/derived_subbbox_osm.json    ways + street_lamp nodes, HSR/Bellandur core
  data/derived_pois_subbbox.json   amenity/shop nodes, same box
  data/derived_stops_bbox.json     BMTC stops with night-departure counts
  data/raw/streetlights_by_ward.csv, data/raw/bbmp_wards_2015.kml,
  data/raw/bbmp_grievances_2025.csv

Outputs:
  out/segments.geojson             every segment, full schema
  out/segments.fixture.geojson     12 segments spanning the score range
  out/stats.json                   the numbers the deck quotes

Sub-bbox, not the full demo bbox: 12.915-12.940 N, 77.620-77.670 E. Widen by
re-running the two Overpass snapshots — nothing downstream changes.
"""
import json, math, re, csv, random
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "out"; OUT.mkdir(exist_ok=True)
random.seed(17)

SPLIT_M = 150.0
CLASS_W = {"motorway":1.6,"trunk":1.5,"primary":1.4,"secondary":1.2,
           "tertiary":1.0,"residential":0.7,"service":0.4,"footway":0.3}
K = 2.0
# night-activity weight by POI class. OSM records opening_hours for 6.7% of POIs
# in this corridor, so an hours filter has no input — class is the proxy.
# Upgrade path: Google Places opening_hours + user_ratings_total, when funded.
NIGHT_POI = {
    "bar":1.0,"pub":1.0,"nightclub":1.0,"fast_food":0.9,"restaurant":0.8,
    "cafe":0.5,"hospital":0.9,"pharmacy":0.6,"fuel":0.8,"atm":0.5,
    "bus_station":0.9,"cinema":0.7,"marketplace":0.6,"convenience":0.6,
    "supermarket":0.4,"ice_cream":0.5,"food_court":0.7,"hotel":0.6,
}

# ---------- geometry helpers (no geopandas: one formula, two uses) ----------
def hav(a, b):
    (y1,x1),(y2,x2) = a, b
    p = math.pi/180
    dy, dx = (y2-y1)*p, (x2-x1)*p
    h = math.sin(dy/2)**2 + math.cos(y1*p)*math.cos(y2*p)*math.sin(dx/2)**2
    return 2*6371000*math.asin(math.sqrt(h))

def line_len(pts):
    return sum(hav(pts[i], pts[i+1]) for i in range(len(pts)-1))

def point_in_ring(y, x, ring):
    inside = False
    n = len(ring)
    for i in range(n):
        x1,y1 = ring[i]; x2,y2 = ring[(i+1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y-y1)*(x2-x1)/(y2-y1)
            if x < xi: inside = not inside
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

# ---------- wards ----------
def load_wards():
    """2015 / 198-ward vintage — the one that matches both the lamp counts and
    the grievance ward names (risks.md §1)."""
    txt = (RAW/"bbmp_wards_2015.kml").read_text(encoding="utf-8", errors="replace")
    wards = []
    for pm in re.findall(r"<Placemark>(.*?)</Placemark>", txt, re.S):
        m = re.search(r"<Data name='Ward Name'>\s*<value>(.*?)</value>", pm, re.S)
        if not m: continue
        name = m.group(1).strip()
        rings = []
        for co in re.findall(r"<coordinates>(.*?)</coordinates>", pm, re.S):
            ring = []
            for tok in co.split():
                p = tok.split(",")
                if len(p) >= 2: ring.append((float(p[0]), float(p[1])))
            if len(ring) > 3: rings.append(ring)
        if rings: wards.append((name, rings))
    return wards

def ward_of(lat, lon, wards):
    for name, rings in wards:
        for ring in rings:
            if point_in_ring(lat, lon, ring): return name
    return None

def load_ward_lamps():
    out = {}
    with open(RAW/"streetlights_by_ward.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("Ward Name") or "").strip()
            cnt = next((v for k,v in row.items() if k and "light" in k.lower()), "")
            try: out[name] = float(str(cnt).replace(",", ""))
            except ValueError: pass
    return out

# 2015-vintage KML ward names vs the free-text ward names in the grievance file.
# Two spellings differ across our 13 demo wards; the city-wide exact-match rate
# is 99/198, which is why this is hand-built for the demo wards only (risks.md
# section 1) and not a fuzzy match.
WARD_ALIAS = {"Bellanduru": "Bellandur", "Madivala": "Madiwala"}

def load_ward_complaints():
    """Street-light complaints per ward, 2025 file. Streetlight-only, not
    all-category: the all-category counts are a different story."""
    out = {}
    with open(RAW/"bbmp_grievances_2025.csv", encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("Sub Category") == "Street Light Not Working":
                w = (row.get("Ward Name") or "").strip()
                out[w] = out.get(w, 0) + 1
    return out

# ---------- build ----------
def main():
    osm = json.loads((ROOT/"data"/"derived_subbbox_osm.json").read_text(encoding="utf-8"))
    pois = json.loads((ROOT/"data"/"derived_pois_subbbox.json").read_text(encoding="utf-8"))
    stops = json.loads((ROOT/"data"/"derived_stops_bbox.json").read_text(encoding="utf-8"))
    wards = load_wards()
    ward_lamps = load_ward_lamps()
    ward_complaints = load_ward_complaints()

    # segments: split every way at ~150 m so one long arterial cannot average
    # away a dark stretch.
    segs = []
    for w in osm["ways"]:
        pts = [(g["lat"], g["lon"]) for g in w.get("geometry", [])]
        if len(pts) < 2: continue
        cls = w["tags"].get("highway", "residential")
        name = w["tags"].get("name", "")
        run, acc, part = [pts[0]], 0.0, 0
        for i in range(len(pts)-1):
            acc += hav(pts[i], pts[i+1]); run.append(pts[i+1])
            if acc >= SPLIT_M:
                segs.append({"segID": f"way{w['id']}/{part}", "pts": run,
                             "roadClass": cls, "name": name, "lengthM": round(acc,1)})
                run, acc, part = [pts[i+1]], 0.0, part+1
        if len(run) > 1 and acc > 15:
            segs.append({"segID": f"way{w['id']}/{part}", "pts": run,
                         "roadClass": cls, "name": name, "lengthM": round(acc,1)})

    # Walk graph over EVERY geometry vertex, keyed on rounded coordinates.
    # Endpoints-only keying fragments the graph — real intersections sit at
    # interior vertices, so betweenness came out meaningless. Vertex-level
    # keying reconnects them; per-segment betweenness is the mean over the
    # vertex pairs the segment covers.
    G = nx.Graph()
    key = lambda p: (round(p[0], 6), round(p[1], 6))
    for s in segs:
        for i in range(len(s["pts"])-1):
            a, b = key(s["pts"][i]), key(s["pts"][i+1])
            if a != b: G.add_edge(a, b, length=max(1.0, hav(s["pts"][i], s["pts"][i+1])))
    giant = max(nx.connected_components(G), key=len)
    Gg = G.subgraph(giant)
    bc = nx.edge_betweenness_centrality(Gg, k=min(400, len(giant)), weight="length", seed=17)
    bc = {frozenset(e): v for e, v in bc.items()}
    bc_seg = {}
    for s in segs:
        vals = [bc.get(frozenset((key(s["pts"][i]), key(s["pts"][i+1]))), 0.0)
                for i in range(len(s["pts"])-1)]
        bc_seg[s["segID"]] = sum(vals)/len(vals) if vals else 0.0

    # per-segment evidence
    lamps = [(l["lat"], l["lon"], (l.get("tags") or {}).get("working")) for l in osm["lamps"]]
    poi_pts = []
    for p in pois:
        t = p.get("tags", {})
        w = NIGHT_POI.get(t.get("amenity")) or NIGHT_POI.get(t.get("shop"))
        if w: poi_pts.append((p["lat"], p["lon"], w))
    stop_pts = [(s["lat"], s["lon"], s["night_trips"]) for s in stops if s["night_trips"] > 0]

    for s in segs:
        mid = s["pts"][len(s["pts"])//2]
        s["mid"] = mid
        w = ward_of(mid[0], mid[1], wards) or "unknown"
        s["ward"] = w
        s["wardGrievanceName"] = WARD_ALIAS.get(w, w)
        s["lampsYes"] = s["lampsNo"] = s["lampsUntagged"] = 0
        for ly, lx, wk in lamps:
            if abs(ly-mid[0]) > 0.006 or abs(lx-mid[1]) > 0.006: continue
            if min(hav((ly,lx), p) for p in s["pts"]) <= 30:
                if wk == "yes": s["lampsYes"] += 1
                elif wk == "no": s["lampsNo"] += 1
                else: s["lampsUntagged"] += 1
        s["activity"] = sum(w*math.exp(-hav((py,px), mid)/100)
                            for py, px, w in poi_pts
                            if abs(py-mid[0]) <= 0.004 and abs(px-mid[1]) <= 0.004)
        s["nightTransit"] = sum(n*math.exp(-hav((sy,sx), mid)/400)
                                for sy, sx, n in stop_pts
                                if abs(sy-mid[0]) <= 0.008 and abs(sx-mid[1]) <= 0.008)
        s["betweenness"] = bc_seg.get(s["segID"], 0.0)

    # Darkness prior, calibrated rather than asserted. Three constants, each
    # measured or standard:
    #   FULL_LAMPS_PER_KM  1000/30 — 30 m pole spacing is the standard interval
    #   LAMP_WORKS         0.920  — Vasanthanagar 2019 two-date panel: 4.0% of
    #                              working lamps die per fortnight, 45.9% of dead
    #                              ones get fixed, so equilibrium dead = 8.0%
    #   road density       measured from this corridor's own OSM road length
    # Ward road-km comes from ward polygon area x that density. Named-road-only
    # input undercounts road length, so coverage runs optimistic — replace with
    # the full OSM drive network per ward when there is time.
    FULL_LAMPS_PER_KM, LAMP_WORKS = 1000/30, 0.920
    corridor_km = sum(s["lengthM"] for s in segs)/1000
    corridor_area = hav((12.915,77.620),(12.940,77.620))/1000 * hav((12.915,77.620),(12.915,77.670))/1000
    road_density = corridor_km/corridor_area

    def ring_area_km2(ring):
        # shoelace on a local equirectangular projection
        y0 = sum(p[1] for p in ring)/len(ring)
        kx = 111.32*math.cos(y0*math.pi/180); ky = 110.57
        s2 = 0.0
        for i in range(len(ring)):
            x1,y1 = ring[i]; x2,y2 = ring[(i+1) % len(ring)]
            s2 += (x1*kx)*(y2*ky) - (x2*kx)*(y1*ky)
        return abs(s2)/2

    ward_area = {}
    for name, rings in wards:
        ward_area[name] = max(ward_area.get(name, 0.0), max(ring_area_km2(r) for r in rings))
    lamps_per_km = {}
    for w in {s["ward"] for s in segs}:
        km = ward_area.get(w, 0) * road_density
        if km > 0.5 and ward_lamps.get(w): lamps_per_km[w] = ward_lamps[w]/km
    med_lpk = (sorted(lamps_per_km.values())[len(lamps_per_km)//2]
               if lamps_per_km else FULL_LAMPS_PER_KM)

    for s in segs:
        lpk = lamps_per_km.get(s["ward"], med_lpk) * CLASS_W.get(s["roadClass"], 0.8)
        coverage = min(0.95, lpk/FULL_LAMPS_PER_KM)
        lit_p = min(0.92, max(0.05, coverage*LAMP_WORKS))
        a, b = K*lit_p, K*(1-lit_p)
        # evidence. beta = dark. Snapshot data, so no time decay applied here;
        # decay switches on when reports carry timestamps.
        a += 1.0*s["lampsYes"] + 0.4*s["lampsUntagged"]
        b += 1.0*s["lampsNo"]
        mean_dark = b/(a+b)
        var = (a*b)/((a+b)**2*(a+b+1))
        s["darkness"] = {"alpha": round(a,3), "beta": round(b,3),
                         "mean": round(mean_dark,4), "var": round(var,5)}

    # exposure: two disjoint halves, kept separate on purpose
    act = rank01([s["activity"] for s in segs])
    bcr = rank01([s["betweenness"] for s in segs])
    ntr = rank01([s["nightTransit"] for s in segs])
    varr = rank01([s["darkness"]["var"] for s in segs])
    for i, s in enumerate(segs):
        structural = 0.6*bcr[i] + 0.4*ntr[i]
        # Measured on this corridor: rho(activity, structural) = +0.03 and
        # rho(activity, night bus departures) = -0.14. The two halves are NOT
        # two proxies for one latent footfall -- they track two different night
        # populations. The problem statement names late-night COMMUTERS, so the
        # structural half leads; activity stays a minority term and a slider.
        s["exposure"] = {"activity": round(act[i],4), "structural": round(structural,4),
                         "blended": round(0.25*act[i] + 0.75*structural, 4)}
        s["confidence"] = round(1-varr[i], 4)
        s["repairPriority"] = round(s["exposure"]["blended"]*s["darkness"]["mean"]*s["confidence"], 5)
        s["routePenalty"] = round(s["lengthM"]*(1 + 1.5*s["darkness"]["mean"]
                                  + 0.3/(s["exposure"]["blended"]+1e-3)
                                  + 8.0*s["darkness"]["var"]), 1)
        s["reportValue"] = round(s["exposure"]["blended"]*s["darkness"]["var"], 5)

    rho = spearman([s["exposure"]["activity"] for s in segs],
                   [s["exposure"]["structural"] for s in segs])

    # counterfactual: complaint order gives a ward, never a segment, so the
    # within-ward target is unknown. Monte-Carlo it and report the spread.
    def restored(picked):
        return sum(s["exposure"]["blended"]*s["darkness"]["mean"]*s["lengthM"] for s in picked)

    by_ward = {}
    for s in segs: by_ward.setdefault(s["ward"], []).append(s)
    cw = lambda w: ward_complaints.get(WARD_ALIAS.get(w, w), 0)
    complaint_wards = sorted((w for w in by_ward if cw(w) > 0), key=lambda w: -cw(w))

    ratios = {}
    for budget in (20, 40, 60):
        ours = restored(sorted(segs, key=lambda s: -s["repairPriority"])[:budget])
        draws = []
        for _ in range(300):
            picked, i = [], 0
            while len(picked) < budget and complaint_wards:
                w = complaint_wards[i % len(complaint_wards)]
                pool = [s for s in by_ward[w] if s not in picked]
                if pool: picked.append(random.choice(pool))
                i += 1
                if i > budget*20: break
            draws.append(restored(picked))
        draws.sort()
        base = sum(draws)/len(draws)
        # Steelman baseline: same complaint-driven ward order, but BBMP picks the
        # single worst segment it can find inside each ward. Not what a
        # coordinate-free complaint log can actually do -- it is the strongest
        # version of the status quo, so the ratio against it is the one to quote
        # when a judge pushes back.
        steel, i = [], 0
        while len(steel) < budget and complaint_wards:
            w = complaint_wards[i % len(complaint_wards)]
            pool = [s for s in by_ward[w] if s not in steel]
            if pool:
                steel.append(max(pool, key=lambda s: s["darkness"]["mean"]*s["exposure"]["blended"]*s["lengthM"]))
            i += 1
            if i > budget*20: break
        ratios[budget] = {"ours": round(ours,1), "baselineMean": round(base,1),
                          "ratioMean": round(ours/base,2) if base else None,
                          "ratioVsLuckiestDraw": round(ours/draws[-1],2) if draws[-1] else None,
                          "baselineSteelman": round(restored(steel),1),
                          "ratioVsSteelman": round(ours/restored(steel),2) if steel and restored(steel) else None,
                          "baselineP5": round(draws[len(draws)//20],1),
                          "baselineP95": round(draws[-len(draws)//20],1)}

    # outputs
    def feature(s):
        return {"type":"Feature",
                "geometry":{"type":"LineString","coordinates":[[p[1],p[0]] for p in s["pts"]]},
                "properties":{k:s[k] for k in ("segID","name","ward","roadClass","lengthM",
                              "darkness","exposure","confidence","repairPriority",
                              "routePenalty","reportValue")}
                 | {"evidence":{"osmLampsWorking":s["lampsYes"],"osmLampsBroken":s["lampsNo"],
                                "osmLampsUntagged":s["lampsUntagged"],
                                "nightBusTrips":round(s["nightTransit"],1),
                                "wardComplaints2025":ward_complaints.get(s["wardGrievanceName"],0),
                                "reports":0}}}

    json.dump({"type":"FeatureCollection","features":[feature(s) for s in segs]},
              open(OUT/"segments.geojson","w"))
    ranked = sorted(segs, key=lambda s: -s["repairPriority"])
    picks = [ranked[i] for i in (0,1,2,len(ranked)//4,len(ranked)//3,len(ranked)//2,
                                 2*len(ranked)//3,3*len(ranked)//4,-3,-2,-1)]
    widest = sorted(segs, key=lambda s: -s["darkness"]["var"])[0]
    if widest not in picks: picks.append(widest)
    json.dump({"type":"FeatureCollection","features":[feature(s) for s in picks]},
              open(OUT/"segments.fixture.geojson","w"), indent=1)

    stats = {
      "segments": len(segs), "waysIn": len(osm["ways"]), "lampsIn": len(osm["lamps"]),
      "lampsWorkingYes": sum(1 for l in lamps if l[2]=="yes"),
      "lampsWorkingNo": sum(1 for l in lamps if l[2]=="no"),
      "nightPOIs": len(poi_pts), "poisTotal": len(pois),
      "stopsWithNightService": len(stop_pts),
      "wardsTouched": sorted({s["ward"] for s in segs}),
      "graphNodes": G.number_of_nodes(), "graphEdges": G.number_of_edges(),
      "giantComponent": len(giant),
      "spearman_activity_vs_structural": round(rho, 3),
      "spearman_activity_vs_nightbus": round(spearman([s["exposure"]["activity"] for s in segs],
                                            [s["nightTransit"] for s in segs]), 3),
      "segmentsWithLampEvidence": sum(1 for s in segs if s["lampsYes"]+s["lampsNo"]+s["lampsUntagged"] > 0),
      "priorOnlyShare": round(1 - sum(1 for s in segs if s["lampsYes"]+s["lampsNo"]+s["lampsUntagged"] > 0)/len(segs), 3),
      "totalCorridorKm": round(corridor_km, 1),
      "roadDensityKmPerKm2": round(road_density,2),
      "lampsPerKmByWard": {w: round(v,1) for w,v in sorted(lamps_per_km.items())},
      "darknessMean": round(sum(s["darkness"]["mean"] for s in segs)/len(segs), 4),
      "counterfactual": ratios,
    }
    json.dump(stats, open(OUT/"stats.json","w"), indent=1)

    assert all(s["darkness"]["mean"] == s["darkness"]["mean"] for s in segs), "darkness NaN"
    assert 0 < ratios[40]["ratioMean"] < 20, "counterfactual ratio implausible"
    print(json.dumps(stats, indent=1))
    print("\ntop 10 by repairPriority:")
    for s in ranked[:10]:
        print(f"  {s['repairPriority']:.4f}  {s['name'][:26]:26s} {s['ward'][:16]:16s} "
              f"dark={s['darkness']['mean']:.2f} exp={s['exposure']['blended']:.2f} "
              f"conf={s['confidence']:.2f} lamps={s['lampsYes']}y/{s['lampsNo']}n")

if __name__ == "__main__":
    main()
