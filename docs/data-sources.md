# Data sources

Every source below was checked on 21 August 2026. Grades are mine and they are
opinions: **A** = ready to use, real geometry, trustworthy provenance. **B** =
real and useful but needs work or carries a known bias. **C** = usable only as a
coarse prior or a talking point. **D** = looks promising, will waste your day.

The single most important thing on this page: **Bengaluru has more than you
expect, and almost none of it is what its filename suggests.** Read the schema
notes before you write a loader.

---

## Tier A — real point geometry

### A1. OpenCity — Bellandur & HSR Layout streetlights (KML) — **Grade A**

```
https://data.opencity.in/dataset/68bab2e1-a94b-4ad5-b1b5-dc9658e462e4/resource/fe50a1be-dd38-49d4-8519-427061647da2/download/4a08fef1-b848-4aed-a53f-2c68d478fb34.kml
```

Individual `<Point>` placemarks, one per lamp, with real coordinates
(`77.640134, 12.917071` and so on). ~100 placemarks in the sample inspected.

**The critical detail:** placemark names are of the form `node/4374357051`. Those
are **OpenStreetMap node IDs**. This file is an OSM export, not a municipal
survey. Which means two things, both good:

1. OSM *does* carry `highway=street_lamp` in parts of Bengaluru, so the Overpass
   route is live — go measure it (`overpass.md`) before assuming otherwise.
2. The placemarks are described as **non-functional** street lamps, i.e. somebody
   surveyed outages and mapped them. That is ground truth for your dependent
   variable in one neighbourhood. Treat it as a held-out test set, not training
   data.

### A2. OpenCity — Silk Board to Marathahalli, ORR (KML) — **Grade A**

```
https://data.opencity.in/dataset/68bab2e1-a94b-4ad5-b1b5-dc9658e462e4/resource/e68dc178-f28c-4017-91ab-bb7bd16fb6ae/download/27023068-61ee-4550-90da-a7c92543054d.kml
```

Same structure, along the Outer Ring Road corridor. ORR is the single most
defensible demo corridor in the city: heavy night pedestrian movement from tech
campuses and bus stops, documented crash history, and you have lamp points.

### A3. OpenStreetMap via Overpass — **Grade A. Measured 21 Aug 2026.**

Free, no key, ODbL. Pull `highway=street_lamp` nodes, `lit=yes|no` on ways,
`highway=bus_stop`, `highway=footway`, POIs. See `data/overpass.md` for the exact
queries.

**Measured, ORR demo bbox** (`docs/measurements.md`): **1,211** street lamps,
**5,874** city-wide, **630 / 15,384 ways** carrying `lit` (4.1%), **303** bus
stops, **1,885** footway ways.

**The find: 1,173 lamps city-wide carry `working=yes|no`** — 658 no, 515 yes.
That is a labelled dependent variable, concentrated in Bellandur/HSR, and it
upgrades the darkness model from asserted to fitted. Survey-biased, so use it as
labels and never as a base rate; hold ~200 out as a test set.

Two traps. `lit=yes` outnumbers `lit=no` ~34:1, so **tag absence is not
evidence** — never treat missing as dark. And Electronic City has **four** mapped
lamps, which is why the demo bbox is the ORR corridor and not there.

---

## Tier B — real records, no geometry

### B1. OpenCity — Vasanthanagar streetlights database, 2019 — **Grade A for what it is**

```
https://data.opencity.in/dataset/68bab2e1-a94b-4ad5-b1b5-dc9658e462e4/resource/e11baba7-6b8a-472b-98ab-944fa23fcab7/download/5fe35037-5957-4066-b3a5-3affa97f2bd0.csv
```

Schema: `Zone & Location, Streetlight Code, Landmark, Type of Streetlight,
Remarks, Condition on 17-June-19, Condition on 2-July-19`

469 individually coded lamps. Sample row:

```
Z4 7th Cross from Cgm Road, Z4-7C-01, Near Cgm Rd Corner, LED, , ok, dead
```

**This is the most underrated file in the entire manifest and almost nobody will
find it.** Reasons:

- It is a **two-date panel**. Condition on 17 June and again on 2 July 2019.
  Fifteen days apart. Every `ok → dead` transition gives you an empirical
  fortnightly failure rate for a real Bengaluru ward. That is a genuine
  calibration constant for your outage model, and you can cite where it came
  from.
- Rows with a blank code and `NEW SL REQD / Pole Present` are **gap records** —
  places where a pole exists and a lamp does not. That is a different failure
  mode from a dead bulb and your municipal queue should treat it differently
  (different crew, different cost).
- It carries lamp **type** (LED vs Sodium), which is a proxy for retrofit vintage
  and therefore for expected failure rate.
- It was compiled by **Citizens for Citizens (CSC)** with BBMP. It is a citizen
  audit. It is precedent for your reporting screen and it means you are not
  proposing something unprecedented — you are proposing to scale something that
  has already been done by hand.

No coordinates. Landmark plus street name is geocodable but do not spend hackathon
hours on it; use the file for its failure-rate constant and its narrative.

### B2. OpenCity — streetlights per BBMP ward — **Grade B**

```
https://data.opencity.in/dataset/68bab2e1-a94b-4ad5-b1b5-dc9658e462e4/resource/17cafe43-76ac-47fb-b893-fd2d2f0ebd0c/download/4aad68d1-752a-4ca0-b075-c40f27582a0f.csv
```

Schema: `Ward_No, Ward Name, Street lights#`. 198 rows. Kempegowda 2,379.
Thanisandra 5,022. Jakkuru 4,351.

This is exactly the "10 lights at X place" aggregate you would normally dismiss.
**Do not dismiss it.** Divide by ward road-length from OSM and you get a
lamps-per-kilometre density per ward, which is the prior for every segment in
that ward before any report arrives. It is the thing that makes the map non-empty
on day zero. See `cold-start.md`.

### B3. OpenCity — BBMP grievances, 2020–2025 — **Grade A. This is the baseline you beat.**

```
2025 https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/1342a93b-9a61-4766-9c34-c8357b7926c2/download/b0d6e9ff-5eef-48bf-ba86-985dbe8112d1.csv
2024 https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/2a3f29ef-a7a1-4fc3-b125-cbcc958a89d1/download/82f88d50-71c5-4203-92ac-5ccb5cabc7a2.csv
2023 https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/fae120ab-d95c-4281-aa86-5bf694712472/download/d4419a76-e2af-44b3-aa25-369c85126f0f.csv
2022 https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/e44f1808-4923-4390-b62c-710d19ab876b/download/b4dd8dd1-1628-4f35-9247-ef5afaad214d.csv
2021 https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/bada528d-f4f5-4ace-9dd1-8ac459fe350b/download/9e7e6892-06b6-4fdc-967a-e4787562f155.csv
2020 https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/58808356-4b0a-4b02-9d70-75993b4dcd1c/download/413fa9ec-8d06-4ecb-884e-1436c5a0f5dd.csv
```

Schema: `Complaint ID, Category, Sub Category, Grievance Date, Ward Name,
Grievance Status, Staff Remarks, Staff Name`

Sample row:

```
20771690, Electrical, Street Light Not Working, 2025-06-19 10:39:00, Jagajeevanram Nagar, Registered, 1st Assignment Based on Ward Mapping, syed zameer/JE
```

**`"Street Light Not Working"` is a literal Sub Category value.** You can filter
six years of complaints down to exactly your problem in one line of pandas.

What it gives you:

- **The status-quo queue itself.** Sorted by `Grievance Date`, this *is* the
  first-come ordering the problem statement criticises. Your counterfactual has a
  real baseline, not an invented one.
- **Ward-level demand signal**, six years deep, so you can show that complaint
  volume is stable and structural, not noise.
- **Time-of-day of filing.** Complaints about darkness get filed in the morning.
  Worth one slide: the people who experience the problem at 11pm are not the
  people at a keyboard the next morning.

What it does **not** give you: coordinates, a closure date, or any indication of
what was actually repaired. `Grievance Status` is the only outcome field. Do not
claim resolution-time analysis from this file — there is one date column.

### B4. OpenCity — BBMP ward boundaries — **Grade B**

```
2015 (198 wards) https://data.opencity.in/dataset/87b978d1-352e-4b90-aa2c-9991e55d3425/resource/a0329df6-2924-43f4-8fe4-7a6ffcc1d53d/download/806d6b9c-e8d9-4eb0-a3a3-b2ba68ec3cda.kml
2022             https://data.opencity.in/dataset/87b978d1-352e-4b90-aa2c-9991e55d3425/resource/9423dbca-db2b-47df-823e-8546f4fb8f2a/download/53418b48-c08d-43bd-be0e-31b46cd0f798.kml
2023 final       https://data.opencity.in/dataset/87b978d1-352e-4b90-aa2c-9991e55d3425/resource/4dd58225-3ad2-4a99-9003-4e8d71e7f99f/download/e56d21e8-0c44-4c35-9e5d-c732f6f59c97.kml
```

KML only, no GeoJSON — convert with `mapshaper` or `geopandas`.

**Use the 2015 / 198-ward file.** It is the one that matches the streetlight
counts (B2) and the ward names in the grievances (B3). The 2023 delimitation went
to 243 wards and Bengaluru's municipal geography has since been reorganised
again; joining across those vintages is a rabbit hole. See `risks.md` §2 — this
is the join that will eat two hours if you let it.

---

## Tier C — exposure inputs

### C1. BMTC GTFS (unofficial) — **Grade A**

```
https://raw.githubusercontent.com/Vonter/bmtc-gtfs/main/gtfs/bmtc.zip
https://raw.githubusercontent.com/Vonter/bmtc-gtfs/main/geojson/stops.geojson
https://raw.githubusercontent.com/Vonter/bmtc-gtfs/main/csv/aggregated.csv
```

Scraped from the Namma BMTC app, parsed to GTFS, GeoJSON and CSV. The
`aggregated` files carry a `trip_count` per stop — a direct measure of service
intensity without you having to parse `stop_times`.

This is your strongest *non-proxy* footfall generator: people alight from buses
and then walk 300–800 m. A stop with 400 trips a day and service past 22:00 puts
real pedestrians on the surrounding streets, and you can defend that causally in
a way you cannot defend "there are lots of shops here."

**Caveat to state out loud, because the repo states it:** the maintainer warns
the source app is unreliable for timetables and stop timings, and only routes
with functional live tracking are included. So *counts* are directionally sound;
*precise minute-level last-bus times* are not. Use trip counts and service span,
not scheduled arrival minutes.

### C2. Google Places — `user_ratings_total` and `opening_hours` — **Grade B**

Review count is revealed preference — a chemist with 800 reviews sees more feet
than one with 40. The real move is filtering POIs to those **closing after
22:00**: twelve businesses open past ten generate night pedestrians; forty
daytime shops do not. That single filter is what matches this problem statement
and most teams will not apply it.

Bias to state openly: it undercounts thelas, tea stalls, informal vendors, and
anything serving non-smartphone users — which is precisely the population most
exposed to dark streets. Say this before a judge says it.

Popular Times is **not** in the official Places API. The `populartimes` scraper
breaks constantly, BestTime is paid. Do not put your demo on that dependency.

### C3. Betweenness centrality on the walk graph — **Grade A, and free**

Not a dataset. Take the OSMnx walking graph and compute edge betweenness: how
many shortest paths between all node pairs traverse each edge. It is a pure
structural measure of "how much through-movement this street carries," it needs
no external data at all, it is one line in NetworkX, and it correlates with
observed pedestrian flow well enough that space-syntax researchers have built
careers on it.

Nobody else in the room will have this. It costs you fifteen minutes and it is a
genuinely independent estimate — which makes it the second leg of your convergent
validation (see `validation.md`).

### C4. Gridded population — WorldPop 100 m / Meta HRSL 30 m — **Grade C**

Both in the Google Earth Engine catalog, so you avoid multi-GB GeoTIFF
downloads. Use for "residents within 500 m of this segment."

Limitation that matters: this is **residential** population. It tells you who
sleeps there, not who walks at 23:00. Base layer, never the answer.

### C5. VIIRS nighttime lights — **Grade C, and be honest**

`NASA/VIIRS/002/VNP46A2` (daily, moonlight-corrected) or
`NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG` (monthly, ~464 m) in Earth Engine.

**500 m is five to ten city blocks. It cannot tell you a street is dark.** Any
team claiming otherwise gets dismantled by a judge who knows remote sensing.

What it legitimately does: confirm that a neighbourhood your model flags is
genuinely low-radiance, and give you a multi-year time series so a ward whose
radiance dropped between 2023 and 2025 becomes a flag worth investigating.
Volunteering this limitation unprompted buys you more credibility than the layer
itself is worth.

---

## Tier D — validators (see `validation.md`)

### D1. Bengaluru Traffic Police road safety reports — **Grade B, PDF**

```
Road Safety Report 2023  https://data.opencity.in/dataset/81336158-a834-4e79-a866-8196ea8b75d3/resource/2261ce08-a0cb-46e1-a1a1-1025ae1f0b72/download/6c425f17-b19b-402f-a638-6b9cae856025.pdf
BTP crashes 2024         https://data.opencity.in/dataset/03d4d85b-7743-4af8-bc08-2155705688f3/resource/9ecd5c73-045e-4b39-93b9-0c5c9e1378b7/download/92622f36-6abd-4ac7-a0cb-1b096eaeaa7f.pdf
BMR road safety report   https://data.opencity.in/dataset/81336158-a834-4e79-a866-8196ea8b75d3/resource/65a9b2b1-f80e-4df7-9aeb-28713da44ad5/download/16d3b7ca-62e2-45dd-ae88-e89d2a2dd89c.pdf
```

PDFs, so tabular extraction is manual — budget for one person with a highlighter,
not a parser. What you want out of them: **pedestrian fatalities with a
day/night split, and named blackspot locations.** Night pedestrian crashes are an
outcome of (footfall × darkness), which makes them a non-circular criterion
validator for your risk score.

Also worth checking: the collection at
`https://data.opencity.in/dataset/road-accidents-in-karnataka` and the BTP
organisation page `https://data.opencity.in/dataset?organization=bengaluru-traffic-police`.

### D2. SafetiPin — **Grade C for data, Grade A for methodology**

Indian organisation doing precisely this problem since 2013. Their audits code
eight parameters — lighting, openness, visibility, crowd, presence of people,
presence of women, security, and transport — each on a defined 0–3 rubric. Delhi
alone has 35,000+ audit points.

Raw data is not downloadable. But their published city reports give ward-level
numbers usable as a held-out validation set, and — more valuable in a 24-hour
window — **citing their rubric shows you did domain reading.** Their "crowd" and
"gender usage" parameters are literally a manual footfall estimate; adopting
their scale rather than inventing your own is free credibility.

### D3. Your own manual count — **Grade A, and mandatory**

Two people, twenty minutes, six to ten segments at 21:30. Pick two the model
scores high, two medium, two low. Count pedestrians.

n=8 is laughably small and that is fine — you are not proving the model, you are
demonstrating that you understand a model has to touch ground somewhere. Report
a Spearman rank correlation. Put a photograph of your teammates counting people
on a road at 21:47 next to that scatter plot.

**This is the single cheapest differentiator available to you and no other team
will have it.** You are awake anyway. It is dark anyway.

---

## Tier E — will waste your day

**Uber Movement.** Discontinued. Archive CSVs from 2016–2020 exist for Bangalore
but it is car travel time, not pedestrians. Wrong variable, dead source.

**Strava Metro.** Free for public agencies, behind an application process you
will not complete in 24 hours. The public heatmap is view-only and scraping tiles
breaks their terms. Also biased toward affluent daytime runners — precisely the
wrong population.

**Census 2011 ward data.** Fifteen years old. Density still correlates, but say
the year out loud or a judge will say it for you.

**Telecom CDR / operator mobility data.** Does not exist publicly in India. Do
not gesture at it as though it does.

**EESL SLNP dashboard.** Publishes aggregate LED counts only. The per-pole
geotagged asset registers exist inside ESCO vendor CCMS systems and are not
public. Worth one sentence in the "how this scales" slide — *"the geotagged
inventory already exists under the SLNP contracts; production Roshni consumes it
via a data-sharing MoU"* — and zero minutes of implementation.

---

## Tier F — national portals (full write-up in `national-data-landscape.md`)

### F1. MoHUA Smart Cities portal — **Grade C. Indicator, not geometry.**

Unauthenticated JSON API behind the Nuxt catalog UI (a plain page fetch looks
empty; it is not):

```
https://smartcities.data.gov.in/backend/dmspublic/v1/resources?limit=100&offset=0&filters[domain_visibility]=777&query=street%20light
```

`total: 93` streetlight resources across ~45 cities. **File sizes run 250 B to
133 KB** — these are the `D24` standard indicator return ("number of street
lights in the city, LED / conventional"), not asset registers. No coordinates,
anywhere, in any of them.

Worth exactly one slide as a national denominator: 45 cities publish how many
lights they have, zero publish where they are.

The `data.gov.in` file host 403s XHR and errors on scripted navigation. Click
the download link in a normal browser; do not debug it.

### F2. IUDX — **Grade A for schema and narrative, gated for data.**

`catalogue.cos.iudx.org.in`. Bengaluru, publisher Electronics City Industrial
Township Authority, dataset `9b27c09f-1ec6-4acd-89f0-a27f23184017`:
**"Streetlights Location Info in Electronic City, Bengaluru"** — the physical
coordinates of every streetlight there, with a companion resource carrying
hourly current and voltage per device.

Marked **Private**; needs registration and a `Request Resource` approval. **But
the sample record is public**, and it is our data contract:

```json
{"deviceID": "L0302", "location": {"type": "Point", "coordinates": [77.666046, 12.841758]}}
```

Build to this shape. See `national-data-landscape.md` §2 for why that single
decision is worth more than the data would have been.

### F3. DataMeet municipal spatial data — **Grade B, boundaries only**

`https://github.com/datameet/Municipal_Spatial_Data/archive/master.zip`

Five cities — Bangalore, Ahmedabad, Bhopal, Bhubaneswar, Pune — municipality
boundary GeoJSON, CC BY 4.0, WGS84. No asset layers. A clean licensed fallback
if the OpenCity BBMP ward KML gives trouble, and nothing more.

---

## Licensing

Most OpenCity resources carry **"No License Provided."** For a hackathon
prototype that is fine. Have the sentence ready anyway: *"used under fair dealing
for a non-commercial prototype; a production deployment would run on a
data-sharing agreement with BBMP, which is how the SLNP asset register would come
in too."* Noticing the licence gap before a judge points at it reads as maturity.

OSM is **ODbL** — share-alike, attribution required. If you ship anything public,
attribute. BMTC GTFS is a scrape of a public app; credit the repo.
