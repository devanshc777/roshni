#!/usr/bin/env python
"""Derive the three files the Route, Report and learning-curve screens need.

Reads out/segments.geojson (produced by pipeline.py). Writes:

  out/routes.json      three canned origin-destination pairs, safer + shortest
                       for each, with the honest comparison strip numbers
  out/curve.json       triage quality vs report count, targeted vs random
  out/telemetry.json   synthetic IUDX-shaped telemetry for one night

Everything precomputed. Nothing on the demo path touches the network.

Run after pipeline.py:
    .venv/Scripts/python.exe data/derive_screens.py
"""
import json, math, random
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
random.seed(17)

# A segment is "wide band" — we do not know it — above this posterior variance.
# 0.05 sits between the evidence-backed segments (var ~0.01-0.02) and the
# prior-only ones (~0.037) and the never-observed ones (~0.083).
WIDE_VAR = 0.05
WALK_M_PER_MIN = 80.0          # ~4.8 km/h, a real night walking pace
NIGHT_HOURS = range(18, 30)    # 18:00 to 05:00 next day
BASE_DATE = "2026-08-21"       # fixed so output is reproducible


def hav(a, b):
    (y1, x1), (y2, x2) = a, b
    p = math.pi / 180
    dy, dx = (y2 - y1) * p, (x2 - x1) * p
    h = math.sin(dy/2)**2 + math.cos(y1*p)*math.cos(y2*p)*math.sin(dx/2)**2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def load():
    fc = json.loads((OUT / "segments.geojson").read_text(encoding="utf-8"))
    segs = []
    for f in fc["features"]:
        p = dict(f["properties"])
        p["pts"] = [(c[1], c[0]) for c in f["geometry"]["coordinates"]]
        segs.append(p)
    return segs


# ---------------------------------------------------------------- routes.json
def build_graph(segs):
    """Two weights per edge: metres, and the segment's route penalty pro-rated
    across its sub-edges. Wide-band edges are flagged, not deleted — the safer
    route avoids them, the shortest route is allowed through."""
    key = lambda p: (round(p[0], 6), round(p[1], 6))
    G = nx.Graph()
    for s in segs:
        n = len(s["pts"]) - 1
        if n < 1 or s["lengthM"] <= 0:
            continue
        for i in range(n):
            a, b = key(s["pts"][i]), key(s["pts"][i+1])
            if a == b:
                continue
            d = max(1.0, hav(s["pts"][i], s["pts"][i+1]))
            pen = s["routePenalty"] * (d / s["lengthM"])
            wide = s["darkness"]["var"] > WIDE_VAR
            prev = G.get_edge_data(a, b)
            if prev and prev["length"] <= d:
                continue
            G.add_edge(a, b, length=d, penalty=pen, wide=wide,
                       dark=s["darkness"]["mean"], var=s["darkness"]["var"],
                       segID=s["segID"], name=s["name"], ward=s["ward"])
    return G


def path_stats(G, nodes):
    total = lit = dark = unknown = 0.0
    seen, wide_hits = [], 0
    for u, v in zip(nodes, nodes[1:]):
        e = G[u][v]
        total += e["length"]
        if e["wide"]:
            unknown += e["length"]; wide_hits += 1
        elif e["dark"] >= 0.5:
            dark += e["length"]
        else:
            lit += e["length"]
        if e["segID"] not in seen:
            seen.append(e["segID"])
    return {
        "distanceM": round(total, 1),
        "walkMinutes": round(total / WALK_M_PER_MIN, 1),
        "litShare": round(lit / total, 3) if total else 0,
        "darkShare": round(dark / total, 3) if total else 0,
        "unknownShare": round(unknown / total, 3) if total else 0,
        "wideBandEdges": wide_hits,
        "segIDs": seen,
    }


def geom(nodes):
    return {"type": "LineString", "coordinates": [[n[1], n[0]] for n in nodes]}


def candidate_pairs(G, lo=600, hi=2200, cap=500):
    """Real, nameable endpoints: the highest-degree node on each named road,
    paired up so the walk is a plausible night walk rather than a hike."""
    giant = max(nx.connected_components(G), key=len)
    by_name = {}
    for u, v, d in G.edges(data=True):
        if u in giant and d["name"]:
            by_name.setdefault(d["name"], []).append(u)
    anchors = {n: max(set(ns), key=lambda x: G.degree(x))
               for n, ns in by_name.items() if len(ns) >= 4}
    names = sorted(anchors)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i+1:]:
            d = hav(anchors[a], anchors[b])
            if lo <= d <= hi:
                pairs.append((a, anchors[a], b, anchors[b], d))
    random.shuffle(pairs)
    return pairs[:cap]


def pick_queries(G, n_pairs=3):
    """Keep only pairs where the safer route is genuinely a DIFFERENT route,
    then rank by how much darkness and unknown ground it actually avoids.
    A demo route identical to the shortest path proves nothing."""
    scored, used = [], set()
    for na, a, nb, b, straight in candidate_pairs(G):
        try:
            safer = nx.shortest_path(G, a, b, weight="safety")
            short = nx.shortest_path(G, a, b, weight="length")
        except nx.NetworkXNoPath:
            continue
        if safer == short:
            continue
        s, h = path_stats(G, safer), path_stats(G, short)
        detour = s["distanceM"] - h["distanceM"]
        if detour <= 20 or detour > 0.6 * h["distanceM"]:
            continue        # no real choice, or an absurd detour nobody would walk
        avoided = ((h["darkShare"] - s["darkShare"]) +
                   2.0 * (h["unknownShare"] - s["unknownShare"]) +
                   0.05 * (h["wideBandEdges"] - s["wideBandEdges"]))
        if avoided <= 0:
            continue
        scored.append((avoided, na, a, nb, b, straight, safer, short, s, h))
    scored.sort(key=lambda t: -t[0])
    # Reject a candidate that reuses ground an accepted route already covers.
    # Without this, nested pairs on one corridor all show the SAME diversion and
    # three demo routes tell one story.
    out, claimed = [], set()
    for row in scored:
        _, na, _, nb, _, safer, short, s, h = row[0], row[1], row[2], row[3], row[5], row[6], row[7], row[8], row[9]
        if na in used or nb in used:
            continue
        segs_here = set(s["segIDs"]) | set(h["segIDs"])
        if claimed and len(segs_here & claimed) > 0.35 * len(segs_here):
            continue
        out.append(row)
        used.add(na); used.add(nb); claimed |= segs_here
        if len(out) == n_pairs:
            break
    return out


def routes_json(segs):
    G = build_graph(segs)
    # Safer graph: wide-band edges are priced out rather than removed, so a
    # route always exists. 12x makes the router take a long way round instead.
    for _, _, d in G.edges(data=True):
        d["safety"] = d["penalty"] * (12.0 if d["wide"] else 1.0)

    queries = []
    for i, (_, na, a, nb, b, straight, safer, short, s, h) in enumerate(pick_queries(G)):
        queries.append({
            "id": f"q{i+1}",
            "label": f"{na} to {nb}",
            "origin": {"name": na, "coordinates": [a[1], a[0]]},
            "dest": {"name": nb, "coordinates": [b[1], b[0]]},
            "straightLineM": round(straight, 1),
            "routes": [
                {"kind": "safer", "geometry": geom(safer), **s},
                {"kind": "shortest", "geometry": geom(short), **h},
            ],
            "detourM": round(s["distanceM"] - h["distanceM"], 1),
            "detourMinutes": round((s["distanceM"] - h["distanceM"]) / WALK_M_PER_MIN, 1),
            "wideBandAvoided": h["wideBandEdges"] - s["wideBandEdges"],
            "darkShareAvoided": round(h["darkShare"] - s["darkShare"], 3),
        })

    doc = {
        "note": ("Precomputed walking routes. 'safer' minimises the route penalty "
                 "(darkness, desertedness, uncertainty); 'shortest' minimises metres. "
                 "Always show both -- advisory, never a guarantee. Pairs were selected "
                 "so the two routes genuinely differ; a demo route identical to the "
                 "shortest path proves nothing."),
        "wideVarThreshold": WIDE_VAR,
        "walkMetresPerMinute": WALK_M_PER_MIN,
        "queries": queries,
    }
    (OUT / "routes.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return doc


# ----------------------------------------------------------------- curve.json
def curve_json(segs, rounds=(0, 5, 10, 25, 50, 100, 200, 400), trials=12):
    """Does directed reporting beat random reporting, and by how much?

    A simulation, and labelled as one. Treat the current posterior as the truth
    we are trying to recover, then hide the lamp evidence and hand it back one
    report at a time. Quality = share of the oracle's restored exposure that
    the ranking available at that report count actually achieves.

    Targeted reports go where exposure x variance is highest under the CURRENT
    belief -- which is exactly what the report screen's empty state ranks by.
    Random reports go anywhere.
    """
    truth = {s["segID"]: s["darkness"]["mean"] for s in segs}
    prior = {}
    for s in segs:
        ev = s["evidence"]
        n = ev["osmLampsWorking"] + ev["osmLampsBroken"] + ev["osmLampsUntagged"]
        # strip the lamp evidence back out to recover the prior-only belief
        a = s["darkness"]["alpha"] - 1.0*ev["osmLampsWorking"] - 0.4*ev["osmLampsUntagged"]
        b = s["darkness"]["beta"] - 1.0*ev["osmLampsBroken"]
        a, b = max(0.2, a), max(0.2, b)
        prior[s["segID"]] = (a, b, n)

    BUDGET = 40
    value = lambda sid, mean: (idx[sid]["exposure"]["blended"] * mean
                               * idx[sid]["lengthM"])
    idx = {s["segID"]: s for s in segs}
    oracle = sum(sorted((value(s["segID"], truth[s["segID"]]) for s in segs),
                        reverse=True)[:BUDGET])

    def run(n_reports, targeted):
        belief = {sid: (a, b) for sid, (a, b, _) in prior.items()}
        reported = set()
        for _ in range(n_reports):
            pool = [sid for sid in belief if sid not in reported]
            if not pool:
                break
            if targeted:
                def rv(sid):
                    a, b = belief[sid]
                    var = (a*b)/((a+b)**2*(a+b+1))
                    return idx[sid]["exposure"]["blended"] * var
                sid = max(pool, key=rv)
            else:
                sid = random.choice(pool)
            reported.add(sid)
            a, b = belief[sid]
            # a report resolves the segment: 2.5 units of evidence, split by truth
            t = truth[sid]
            belief[sid] = (a + 2.5*(1-t), b + 2.5*t)
        est = {sid: b/(a+b) for sid, (a, b) in belief.items()}
        picked = sorted(belief, key=lambda sid: -value(sid, est[sid]))[:BUDGET]
        return sum(value(sid, truth[sid]) for sid in picked) / oracle

    points = []
    for n in rounds:
        for targeted in (True, False):
            vals = [run(n, targeted) for _ in range(1 if n == 0 else trials)]
            points.append({"reports": n, "targeted": targeted,
                           "ratio": round(sum(vals)/len(vals), 4)})
    doc = {
        "note": ("SIMULATION, and must be labelled as one on any slide. The current "
                 "posterior stands in for ground truth; lamp evidence is withheld and "
                 "returned one report at a time. quality = share of the oracle "
                 "ranking's restored exposure achieved at that report count. "
                 "targeted=true picks reports by exposure x variance, which is what "
                 "the report screen's empty state ranks by."),
        "budget": BUDGET,
        "oracleRestored": round(oracle, 1),
        "trialsPerPoint": trials,
        "points": points,
    }
    (OUT / "curve.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return doc


# ------------------------------------------------------------- telemetry.json
def telemetry_json():
    """Synthetic, IUDX-shaped. Record shape copied verbatim from the public
    sample of the Streetlights Energy Consumption resource, so the production
    path is a credential change and not a rewrite.

    MUST render differently from real data in the UI.
    """
    osm = json.loads((ROOT/"data"/"derived_subbbox_osm.json").read_text(encoding="utf-8"))
    lamps = [l for l in osm["lamps"] if (l.get("tags") or {}).get("working") in ("yes", "no")]
    lamps.sort(key=lambda l: l["id"])
    lamps = lamps[:120]

    recs, devices = [], []
    for i, l in enumerate(lamps):
        dev = f"L{i+301:04d}"
        working = l["tags"]["working"] == "yes"
        devices.append({"deviceID": dev,
                        "location": {"type": "Point",
                                     "coordinates": [round(l["lon"], 6), round(l["lat"], 6)]},
                        "source": "synthetic",
                        "osmWorkingTag": l["tags"]["working"]})
        for h in NIGHT_HOURS:
            day = 21 + (h // 24)
            hh = h % 24
            ts = f"2026-08-{day:02d}T{hh:02d}:10:00+05:30"
            if working:
                cur = round(random.gauss(0.58, 0.03), 3)
                volt = round(random.gauss(228.5, 2.4), 1)
            else:
                cur = 0.0
                volt = round(random.gauss(229.8, 2.1), 1)   # supply live, lamp dead
            recs.append({"deviceID": dev, "observationDateTime": ts,
                         "current": cur, "voltage": volt})

    doc = {
        "note": ("SYNTHETIC. Shape copied verbatim from the IUDX Streetlights Energy "
                 "Consumption resource sample. Zero current after dusk with live "
                 "voltage is the outage signature. Render these differently from real "
                 "data in the UI and say so before anyone asks."),
        "iudxDatasetReference": "9b27c09f-1ec6-4acd-89f0-a27f23184017",
        "outageRule": "current < 0.05 A after dusk, voltage present -> lamp dark",
        "devices": devices,
        "observations": recs,
    }
    (OUT / "telemetry.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return doc


def main():
    segs = load()
    r = routes_json(segs)
    c = curve_json(segs)
    t = telemetry_json()

    assert r["queries"], "no routes built — graph is too fragmented"
    for q in r["queries"]:
        safer, short = q["routes"]
        assert safer["distanceM"] >= short["distanceM"] - 1, \
            f"{q['id']}: safer route is shorter than shortest — weights are wrong"
    tgt = [p["ratio"] for p in c["points"] if p["targeted"] and p["reports"] == 100]
    rnd = [p["ratio"] for p in c["points"] if not p["targeted"] and p["reports"] == 100]
    assert tgt and rnd, "curve missing the 100-report point"

    print(f"routes.json     {len(r['queries'])} queries")
    for q in r["queries"]:
        s, h = q["routes"]
        print(f"  {q['label'][:44]:44s} safer {s['distanceM']:7.0f}m "
              f"dark{s['darkShare']:.2f} unk{s['unknownShare']:.2f} | "
              f"short {h['distanceM']:7.0f}m dark{h['darkShare']:.2f} "
              f"unk{h['unknownShare']:.2f} | detour +{q['detourM']:.0f}m "
              f"| +{q['detourMinutes']:.0f}min | wide avoided {q['wideBandAvoided']}")
    print(f"\ncurve.json      oracle {c['oracleRestored']}, budget {c['budget']}")
    for n in sorted({p["reports"] for p in c["points"]}):
        a = next(p["ratio"] for p in c["points"] if p["reports"] == n and p["targeted"])
        b = next(p["ratio"] for p in c["points"] if p["reports"] == n and not p["targeted"])
        print(f"  {n:4d} reports   targeted {a:.3f}   random {b:.3f}   gap {a-b:+.3f}")
    print(f"\ntelemetry.json  {len(t['devices'])} devices, {len(t['observations'])} observations")


if __name__ == "__main__":
    main()
