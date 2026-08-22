#!/usr/bin/env python
"""City-wide context layer: all 225 BBMP wards, so the map reads as Bengaluru.

Emits two files:
  out/city.geojson      ward outlines as MultiLineString, simplified for a
                        0.5px hairline at city zoom
  out/city_labels.json  one label anchor per ward, plus the demo-bbox rectangle
                        and the city totals the Coverage panel quotes

Outlines rather than polygons on purpose: the map only ever draws ward
boundaries as hairlines, and a MultiLineString of the rings is smaller than a
Polygon with the same geometry. The one filled shape is the demo bbox, which is
built here as its own feature.

    .venv/Scripts/python.exe data/build_city.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KML = ROOT / "data" / "raw" / "bbmp_wards_2023.kml"
OUT = ROOT / "out"

# The locked demo bbox, identical to data/pipeline.py. Kept as a literal in both
# places rather than shared through a module — two files, one constant, and a
# mismatch would be visible on the map immediately.
BBOX = (12.90, 77.61, 12.97, 77.70)          # south, west, north, east

# ~44 m at this latitude. Enough to keep every ward's silhouette recognisable
# while cutting the point count by roughly an order of magnitude.
EPS = 0.0004


def rdp(pts, eps):
    """Ramer-Douglas-Peucker. Plain implementation — shapely is not a dependency
    here and a 2 KB polyline does not need one."""
    if len(pts) < 3:
        return pts
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    dx, dy = x1 - x0, y1 - y0
    norm = (dx * dx + dy * dy) ** 0.5
    worst, wi = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        if norm == 0:
            d = ((px - x0) ** 2 + (py - y0) ** 2) ** 0.5
        else:
            d = abs(dy * (px - x0) - dx * (py - y0)) / norm
        if d > worst:
            worst, wi = d, i
    if worst <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:wi + 1], eps)[:-1] + rdp(pts[wi:], eps)


def field(blob, key):
    m = re.search(r'<SimpleData name="' + key + r'">([^<]*)<', blob)
    return m.group(1) if m else ""


def shoelace(ring):
    a = 0.0
    for i in range(len(ring)):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % len(ring)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


def clip_to_bbox(ring, s, w, n, e):
    """Sutherland-Hodgman against the four bbox edges. The clip region is convex,
    which is the only case this algorithm is correct for, and a bbox always is.

    Used instead of a centroid-in-bbox test: the demo rectangle is comparable in
    size to a single ward, so a centroid test misclassifies edge wards in both
    directions. Area overlap is what we actually want to weight population by.
    """
    def half(poly, keep, intersect):
        if not poly:
            return []
        out = []
        for i in range(len(poly)):
            cur, prv = poly[i], poly[i - 1]
            if keep(cur):
                if not keep(prv):
                    out.append(intersect(prv, cur))
                out.append(cur)
            elif keep(prv):
                out.append(intersect(prv, cur))
        return out

    def lerp_x(p, q, x):
        t = (x - p[0]) / (q[0] - p[0])
        return (x, p[1] + t * (q[1] - p[1]))

    def lerp_y(p, q, y):
        t = (y - p[1]) / (q[1] - p[1])
        return (p[0] + t * (q[0] - p[0]), y)

    poly = list(ring)
    poly = half(poly, lambda p: p[0] >= w, lambda p, q: lerp_x(p, q, w))
    poly = half(poly, lambda p: p[0] <= e, lambda p, q: lerp_x(p, q, e))
    poly = half(poly, lambda p: p[1] >= s, lambda p, q: lerp_y(p, q, s))
    poly = half(poly, lambda p: p[1] <= n, lambda p, q: lerp_y(p, q, n))
    return poly


def main():
    text = KML.read_text(encoding="utf-8", errors="replace")
    placemarks = text.split("<Placemark")[1:]

    feats, labels = [], []
    city_pop = scope_pop = 0
    scope_wards = []
    raw_pts = kept_pts = 0

    for pm in placemarks:
        name = field(pm, "name_en").strip()
        pop = int(field(pm, "population") or 0)
        area = float(field(pm, "ward_area") or 0)
        city_pop += pop

        rings = []
        for block in re.findall(r"<coordinates>([^<]+)</coordinates>", pm):
            ring = []
            for pair in block.split():
                part = pair.split(",")
                if len(part) >= 2:
                    ring.append((round(float(part[0]), 5), round(float(part[1]), 5)))
            if len(ring) >= 3:
                rings.append(ring)
        if not rings:
            continue

        raw_pts += sum(len(r) for r in rings)
        simple = [rdp(r, EPS) for r in rings]
        simple = [r for r in simple if len(r) >= 3]
        kept_pts += sum(len(r) for r in simple)

        # Centroid is a LABEL ANCHOR only. Scope membership and the headline
        # population both come from real area overlap, below.
        flat = [p for r in rings for p in r]
        clon = sum(p[0] for p in flat) / len(flat)
        clat = sum(p[1] for p in flat) / len(flat)

        # Population inside the measured rectangle, area-weighted. Assumes
        # population is spread evenly within a ward, which is wrong in detail
        # and is the reason this is reported to one significant figure as
        # "about N people" rather than as a count.
        s, w, n, e = BBOX
        ward_area = sum(shoelace(r) for r in rings)
        clipped = sum(shoelace(clip_to_bbox(r, s, w, n, e)) for r in rings)
        frac = (clipped / ward_area) if ward_area else 0.0
        scope_pop += pop * frac
        # "in scope" for styling means a ward the demo actually covers, not one
        # that merely grazes the edge
        in_scope = frac > 0.4
        if in_scope:
            scope_wards.append(name)

        feats.append({
            "type": "Feature",
            "properties": {"name": name, "inScope": in_scope},
            "geometry": {"type": "MultiLineString", "coordinates": simple},
        })
        labels.append({
            "name": name, "pop": pop, "areaKm2": round(area, 2),
            "lon": round(clon, 5), "lat": round(clat, 5), "inScope": in_scope,
            "overlap": round(frac, 3),
        })

    s, w, n, e = BBOX
    feats.append({
        "type": "Feature",
        "properties": {"demoBbox": True},
        "geometry": {"type": "Polygon",
                     "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]},
    })

    (OUT / "city.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "features": feats}, separators=(",", ":")))

    meta = {
        "wards": len(labels),
        "cityPopulation": city_pop,
        "scopeWards": len(scope_wards),
        "scopePopulation": round(scope_pop),
        "scopeShare": round(scope_pop / city_pop, 4) if city_pop else 0,
        "scopeWardNames": sorted(scope_wards),
        "bbox": list(BBOX),
        "method": ("scopePopulation is ward population weighted by the share of "
                   "each ward's area falling inside the demo bbox, assuming even "
                   "population density within a ward. Centroids are label anchors "
                   "only. Quote it as 'about' — it is an estimate, not a count."),
        "labels": labels,
    }
    (OUT / "city_labels.json").write_text(json.dumps(meta, separators=(",", ":")))

    kb = (OUT / "city.geojson").stat().st_size / 1024
    print(f"city.geojson      {kb:,.0f} KB   {len(feats) - 1} wards"
          f"   {raw_pts:,} -> {kept_pts:,} points")
    print(f"city_labels.json  {(OUT / 'city_labels.json').stat().st_size / 1024:,.0f} KB")
    print(f"city population   {city_pop:,}")
    print(f"in scope          {len(scope_wards)} wards, {scope_pop:,} people"
          f"  ({100 * scope_pop / city_pop:.1f}%)")

    assert len(labels) == 225, f"expected 225 wards, got {len(labels)}"
    assert kb < 900, f"city.geojson too heavy for an offline page: {kb:.0f} KB"
    assert 0.05 < scope_pop / city_pop < 0.2, "scope share outside sane range"


if __name__ == "__main__":
    main()
