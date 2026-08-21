# Measured — OSM coverage, Bengaluru

Run against `overpass-api.de/api/interpreter`, **21 August 2026**. These are
counts I actually pulled, not estimates. Re-run them at H1 (`data/overpass.md`)
— OSM changes, and the pitch quotes these.

## Street lamp nodes — `highway=street_lamp`

| Area | bbox | Lamps |
|---|---|---|
| Bengaluru, BBMP-wide | `12.83,77.45,13.14,77.78` | **5,874** |
| **ORR, Silk Board–Marathahalli** | `12.90,77.61,12.97,77.70` | **1,211** |
| Bellandur + HSR Layout | `12.90,77.62,12.94,77.68` | **727** |
| Electronic City | `12.82,77.64,12.89,77.71` | **4** |

### This changes the demo bbox

**Electronic City has four mapped lamps.** Four. The IUDX municipal feed covers
Electronic City; OSM does not. So the two datasets cover adjacent but
non-overlapping ground — which is itself the fragmentation story in one line.

**Lock the demo bbox on the ORR / Bellandur–HSR corridor**
(`12.90,77.61,12.97,77.70`). 1,211 lamps, the OpenCity per-lamp KML, real night
pedestrian load, and it is walkable for the field count. Electronic City stays in
the deck as the *production integration* story, not the demo geography.

## The finding that matters most — labelled outage ground truth

The Bengaluru lamps carry a **`working=yes|no`** tag.

| | Bengaluru-wide |
|---|---|
| `highway=street_lamp` + `working=no` | **658** |
| `highway=street_lamp` + `working=yes` | **515** |
| **Total labelled** | **1,173** — 20% of all mapped lamps |

A 300-node sample inside Bellandur/HSR: `working=no` 202, `working=yes` 95, plus
a couple of `lamp_type=electric`. Nothing else — no wattage, no pole ref, no
operator.

**You have a labelled dependent variable in your demo bbox.** That moves the
project from *assert a darkness model* to *fit and validate one*, and it makes
the Beta update in `cold-start.md` carry real evidence rather than only a prior.

Two honest caveats, both worth volunteering:

- This is **survey-biased**. Whoever mapped these went out *because* lights were
  broken, so the 202:95 ratio is a property of the survey, not the outage rate of
  Bengaluru. Use it as labels, never as a base rate.
- It is a **one-time snapshot** with no timestamp beyond the OSM edit history.
  Pair it with the Vasanthanagar two-date panel (`data-sources.md` §B1) if you
  want anything resembling a failure rate.

Hold out a slice of these as a test set. Do not fit on all 1,173 and then quote
accuracy against them.

## The `lit` tag — weak, but not empty

Inside the ORR demo bbox:

| | Count |
|---|---|
| Highway ways with any `lit` tag | **630** |
| `lit=yes` | **612** |
| `lit=no` | ~**18** |
| All highway ways | **15,384** |
| **Coverage** | **4.1%** |

Better than the sub-2% I expected for an Indian city, and above the "do not build
on it" line — but note the asymmetry: **almost every tagged way is `lit=yes`.**
Mappers record lighting when it exists and stay silent when it does not, so
*absence of the tag tells you nothing*. Treat `lit=yes` as weak positive evidence
and `lit=no` as strong negative evidence, and never treat missing as dark.

## Exposure inputs in the demo bbox

| | Count |
|---|---|
| `highway=bus_stop` nodes | **303** |
| `highway=footway` ways | **1,885** |

303 is the OSM *tag* count. **BMTC's GTFS has 405 stops in the same bbox, with
departure times** — 101,367 daily departures, 6,187 at or after 21:00, and 119
stops with no night service at all. Use GTFS as the input and cite OSM only for
the tag count. 405 stops is a genuinely strong transit-exposure signal for 4 km² — join
these to BMTC `trip_count` (`data-sources.md` §C1) and the structural half of the
exposure model has real inputs rather than a proxy for a proxy.

## Operational note

Overpass rate-limits and returns an XML error body under load. Wrap every call in
a retry that checks whether the response starts with `<` and backs off ~4s. Two
of my calls hit this. Cache every result to disk on first fetch —
`ox.settings.use_cache = True`.

## What to put on a slide

> Bengaluru has 5,874 streetlights mapped in OpenStreetMap. BBMP's own ward
> returns sum to **421,113**. So OSM covers **1.4%** — and 1,173 of those carry a working/not-working label from a citizen
> survey. That is simultaneously the best open streetlight data in India and
> nowhere near enough, which is exactly why the system has to estimate darkness
> rather than look it up.
