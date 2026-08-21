#!/usr/bin/env python
"""Pull the OSM snapshot the pipeline runs on, once, to disk.

Covers the union bounding box of the 13 demo wards (126 km2), which is a
superset of the locked demo bbox. That matters: segments come from the demo
bbox, but ward road-km must be measured over whole ward polygons or the lamp
density prior is wrong.

Writes:
  data/derived_bbox_ways.json    every way[highway], with OSM node ids + geometry
  data/derived_bbox_lamps.json   every node[highway=street_lamp]
  data/derived_bbox_pois.json    every node[amenity] / node[shop]

overpass-api.de is unreachable from this network and so are z/lz4/kumi/
private.coffee. overpass.osm.ch answers but holds a Switzerland-only extract,
so it returns zero for Bengaluru, which looks exactly like "no data exists".
The mirror below is the one that works.

Tiled 3x3 because a single 126 km2 way query with geometry gets 504'd.
"""
import json, math, time, urllib.request, urllib.parse
from pathlib import Path

EP = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
OUT = Path(__file__).resolve().parent

# union bbox of the 13 demo ward polygons, from bbmp_wards_2015.kml
S, W, N, E = 12.8862, 77.5926, 12.9751, 77.7108
TILES = 3


def overpass(selector, tries=4):
    q = f"[out:json][timeout:300];{selector};out body geom;"
    for attempt in range(tries):
        try:
            r = urllib.request.urlopen(
                EP, data=urllib.parse.urlencode({"data": q}).encode(), timeout=420)
            body = r.read()
            if body[:1] == b"<":
                raise RuntimeError("Overpass returned an XML error body")
            return json.loads(body)["elements"]
        except Exception as e:
            last = e
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"Overpass failed after {tries} tries: {last}")


def tiles():
    for i in range(TILES):
        for j in range(TILES):
            yield (S + (N-S)*i/TILES, W + (E-W)*j/TILES,
                   S + (N-S)*(i+1)/TILES, W + (E-W)*(j+1)/TILES)


def collect(pattern, label):
    """Tiled fetch, deduped by element id. Ways straddling a tile edge come
    back from both tiles; the id dedupe keeps one complete copy."""
    seen = {}
    for k, (s, w, n, e) in enumerate(tiles(), 1):
        box = f"({s:.5f},{w:.5f},{n:.5f},{e:.5f})"
        els = overpass(pattern.format(box=box))
        new = sum(1 for el in els if el["id"] not in seen)
        for el in els:
            seen.setdefault(el["id"], el)
        print(f"  {label} tile {k}/{TILES*TILES}: {len(els)} returned, {new} new, "
              f"{len(seen)} total")
    return list(seen.values())


def main():
    kx = 111.32 * math.cos(((S+N)/2) * math.pi/180)
    print(f"bbox {S},{W},{N},{E}  ~{(E-W)*kx*(N-S)*110.57:.0f} km2, {TILES*TILES} tiles\n")

    jobs = [
        ('way["highway"]{box}', "ways", "derived_bbox_ways.json"),
        ('node["highway"="street_lamp"]{box}', "lamps", "derived_bbox_lamps.json"),
        ('(node["amenity"]{box};node["shop"]{box};)', "pois", "derived_bbox_pois.json"),
    ]
    for pattern, label, fname in jobs:
        els = collect(pattern, label)
        (OUT / fname).write_text(json.dumps(els), encoding="utf-8")
        mb = (OUT / fname).stat().st_size / 1e6
        print(f"-> {fname}: {len(els)} elements, {mb:.1f} MB\n")

    lamps = json.loads((OUT/"derived_bbox_lamps.json").read_text(encoding="utf-8"))
    yes = sum(1 for l in lamps if (l.get("tags") or {}).get("working") == "yes")
    no = sum(1 for l in lamps if (l.get("tags") or {}).get("working") == "no")
    print(f"lamp labels in snapshot: working=yes {yes}, working=no {no}, "
          f"labelled {yes+no} of {len(lamps)}")


if __name__ == "__main__":
    main()
