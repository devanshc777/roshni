# The national data landscape — what is actually published

Written after directly querying MoHUA's Smart Cities portal API, IUDX's central
catalogue, and DataMeet on 21 Aug 2026. This document exists because the
commonly-repeated claim — *"all 100 Smart Cities have fully mapped asset layers
including streetlights"* — is **half true in a way that matters enormously for
scoping.**

## The claim, and what is actually there

The claim: MoHUA stood up Integrated Command and Control Centres (ICCCs) in all
100 Smart Cities; those cities have mapped asset layers covering streetlights,
water pipelines and electricity poles; under NUDM 3,300+ ULBs are integrating
municipal data; and it all sits on internal dashboards accessible only to
government administrators and authorised vendors.

**Every clause of that is true. The misleading part is the word "asset layers."**
Two different things get published under that phrase and they are not remotely
interchangeable:

| | What it is | Where it is |
|---|---|---|
| **Indicator** | *"This city has 84,000 streetlights, 61,000 of them LED"* | Published openly, 93 resources, ~45 cities |
| **Asset geometry** | *`{deviceID: "L0302", location: {Point, [77.666046, 12.841758]}}`* | Catalogued openly, **access-controlled** |

The indicator is what's on `smartcities.data.gov.in`. The geometry is what's on
IUDX. Conflating them is how a team ends up promising a national streetlight map
in a pitch and delivering a bar chart.

---

## Finding 1 — smartcities.data.gov.in has 93 streetlight resources and none have coordinates

The catalog UI is a Nuxt app, so a plain page fetch returns "No Result Found" and
looks empty. It is not. There is an **unauthenticated JSON API** behind it:

```
https://smartcities.data.gov.in/backend/dmspublic/v1/resources
    ?limit=100
    &offset=0
    &filters[domain_visibility]=777
    &query=street%20light
```

Returns `total: 93`. Each row carries `catalog_title`, `cdos_state_ministry`
(the city), a direct `datafile` URL, `file_format`, `file_size` and `frequency`.
Related endpoints found in the same page load:

```
/backend/dmspublic/v1/resources?filters[catalog_reference]=<nid>   resources in a catalog
/backend/dms/v1/catalog/<slug>?_format=json                        catalog metadata
/backend/dms/v1/api-export/catalog/<nid>                           catalog export (title, keywords, jurisdiction)
```

Cities with a streetlight resource include Surat, Pune, NDMC, Indore, Bhopal,
Jaipur, Faridabad, Thane, Nagpur, Ahmedabad, Coimbatore, Salem, Madurai,
Tiruchirappalli, Thiruvananthapuram, Shimla, Jammu, Amritsar, Patna, Warangal,
Karimnagar, Kalyan-Dombivli, Pimpri-Chinchwad, Bareilly, Saharanpur, Namchi,
Dharamshala and about twenty more.

**Then look at the file sizes.** They run from **250 bytes to 133 KB**. Most sit
between 300 B and 5 KB. A city with 80,000 streetlights cannot express its
inventory in 324 bytes.

The catalog metadata says it outright. From
`/backend/dms/v1/api-export/catalog/602922107` (Street Lights : Surat):

> "This catalog describes the number of street lights available in the city
> which are LED / Conventional."

`D24` in all those filenames is the Smart Cities Mission standard indicator
template — **D24 = count of street lights, split LED vs conventional.** It is a
KPI return, not an asset register. Every city filed the same form.

**Verdict: useful for one slide, useless as a data layer.** What it *is* good
for: a national denominator. "Forty-five cities publish how many lights they
have. Zero publish where they are. That gap is the problem we are solving."

Two footnotes worth having:

- One row lists an **API endpoint rather than a file** — Bhopal, `http://125.20.96.211:6082`. Likely an ICCC feed that leaked into the catalogue. Unauthenticated HTTP on a bare IP; do not build on it, but it is evidence that the live systems exist.
- The `data.gov.in` file host returns **403 to XHR** and errors on scripted navigation. Clicking the download link in a normal browser session works. Do not burn hackathon hours on this — click it by hand.

---

## Finding 2 — IUDX has exactly the data you want, for exactly your city, behind a request button

This is the important one.

The **India Urban Data Exchange** central catalogue at
`catalogue.cos.iudx.org.in` lists, for instance Bengaluru, publisher
**Electronics City Industrial Township Authority**:

**"Streetlights Location Info in Electronic City, Bengaluru"**

> "Publishes the physical coordinates of all the streetlights installed in
> Electronic City, Bengaluru. The hourly energy consumption information of the
> streetlight such as current, voltage, etc. can be found in the Streetlights
> Energy Consumption resource."

Dataset id `9b27c09f-1ec6-4acd-89f0-a27f23184017`. Marked **1 Private** —
consuming it requires registration and a `Request Resource` approval.

**But the sample data is public without login.** The exact record shape:

```json
{
  "deviceID": "L0302",
  "location": {
    "type": "Point",
    "coordinates": [77.666046, 12.841758]
  }
}
```

That coordinate is in Electronic City, south-east Bengaluru. Alongside it sits
**"Streetlights Energy Consumption Info in Electronic City, Bengaluru"** —
hourly current and voltage per `deviceID`, which is a **real outage signal**: a
lamp drawing no current at 22:00 is off.

### Why this changes the project

Three things fall out of it, all of them free:

1. **Adopt this as your internal data contract.** Make Roshni's lamp record
   `{deviceID, location: GeoJSON Point}` and its telemetry record
   `{deviceID, timestamp, current, voltage}`. Then *"the day access is granted we
   plug in"* stops being hand-waving and becomes literally true — you are
   already speaking IUDX's schema. That is a one-line design decision that
   converts your biggest weakness into forward-compatibility, and it is the kind
   of thing a judge from a smart-cities background will recognise instantly.

2. **Electronic City is a strong demo bbox.** Heavy IT-campus night pedestrian
   movement, adjacent to the ORR corridor where you already have per-lamp OSM
   KML from OpenCity, and now provably the subject of a real municipal asset
   feed.

3. **You have a genuine ask for the closing slide.** Not "give us funding" —
   *"approve this resource request."* Screenshot the Request Resource button.
   That is a specific, small, achievable next step, and specificity reads as
   seriousness.

### The honest caveat

Electronic City is an industrial township authority, not BBMP, and it covers a
small slice of Bengaluru. Do not imply the whole city is instrumented. The claim
you can defend is: *"pole-level location and hourly power telemetry exist,
today, for part of our demo geography, published by the local authority into the
national exchange, and gated behind an access request."* That is strong enough.
Overstating it is not.

---

## Finding 3 — DataMeet is boundaries only

`projects.datameet.org/Municipal_Spatial_Data/` covers **five cities** —
Bangalore, Ahmedabad, Bhopal, Bhubaneswar, Pune — with **municipality boundary
GeoJSON only**. CC BY 4.0, WGS84, whole repo downloadable as a zip from GitHub.

No asset layers. No poles. The screenshot claiming it offers "administrative
outlines rather than precise pole coordinates" is accurate, and that is exactly
its value: a clean, licensed boundary file if the OpenCity BBMP KML gives you
trouble. Nothing more.

---

## Finding 4 — assessing the Medium "AI Dark Spot Auditor" blueprint

Worth reading, worth citing, **not worth building.** Its four-stage design:

1. Dashcam telemetry from rideshare fleets and night buses, with GPS and lux.
2. Low-light CV — YOLOv8 / ViT, enhancement filters — classifying fixtures as `FAULTY_DARK`.
3. PostGIS `ST_DWithin` match to a municipal asset DB within a **15 m radius** to recover a pole ID.
4. RAG over municipal tender documents (LlamaIndex, `gpt-4o-mini`) to find the vendor and warranty, then auto-dispatch a JSON ticket.

It also names two resources you should note: **Roboflow Universe** has pre-labelled
night streetlight datasets with bounding boxes on lit and unlit fixture heads,
YOLO-ready; and **ExDark** (Exclusively Dark) is the academic low-light image
dataset.

**Where it is right, and you should steal it:**

- Stage 3 is the correct architecture *if the asset DB exists* — and IUDX proves it does. `ST_DWithin` at 15 m is the right join.
- The pole ID format it cites, `EESL-DEL-S12-409`, matches the SLNP/ESCO contracting reality.
- Vendor-warranty routing is a genuinely good idea for a production system and belongs on your "what's next" slide.

**Where it does not survive contact with your constraints:**

- **Stage 1 does not exist.** There is no dashcam feed from Ola or Uber available to a hackathon team. The pipeline is architecturally sound and has no input.
- **Stage 3 assumes the asset DB you don't have access to.** It presupposes exactly the gated thing.
- **It has no prioritisation logic at all.** Detection is deterministic — flagged plus matched equals ticket. Which means it reproduces first-come queueing, the exact failure your problem statement names. It is a *detection* system where the brief asks for a *triage* system.

**The one thing to take from it and put on a slide:** it is independent evidence
that a serious person, writing publicly, designed this system around a municipal
asset DB match and could not get one either. Cite it as corroboration that the
gap is structural rather than a gap in your research.

---

## Reconciled picture — what to say when asked "why don't you have the real data"

Four sentences, in this order:

> The data exists and we found it. Ninety-three Indian cities publish streetlight
> **counts** through MoHUA's Smart Cities portal, and zero of them publish
> **coordinates** — the D24 template is a KPI return, not an asset register. The
> pole-level geometry is on IUDX: here is the Bengaluru record, `deviceID` plus a
> GeoJSON Point, published by the local authority, marked private and gated
> behind an access request. So we built Roshni to speak IUDX's schema natively
> and to work without it — and the ask on our last slide is that someone approve
> the request.

That answer does four things at once: it proves you looked, it shows you
understand the difference between an indicator and an asset, it makes your
architecture forward-compatible, and it ends on a concrete request rather than a
complaint.
