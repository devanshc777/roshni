# Pitch

## Open with their own number

> Bengaluru filed 126,974 civic complaints in the first five and a half months of
> 2025. Thirty-one per cent — 39,847, about 236 a day — were "street light not
> working."
>
> BBMP closes 96.4% of electrical complaints. They are not slow and they are not
> failing. They are being handed the queue in the wrong order.

Do not open by criticising the municipality. A government judge will resent it
and it is not what the data says. The data says they execute well and prioritise
badly, and that is a better story anyway.

## The thesis, in one slide

Streetlight complaints concentrate in Jnanabharathi (1,345), Ullalu (1,026),
Hemmigepura (983), Dodda Bidarkallu (967) — newer, peripheral, more app-literate
wards. The older, denser, more-walked inner wards file fewer. (Horamavu 3,128 is
the all-category count; keep the two bases apart.)

> A first-come queue is sorted by **who complains**, not by **who is exposed**.
> The person on a dark arterial at 11pm is not the person filing a ticket at
> 10:39 the next morning.

That last clause is **not** checkable in this data: the grievance clock is
12-hour with AM/PM stripped. Cut it from the slide and let the ward pattern
carry the point.

## Demo order — queue first

Most teams open with the citizen app. Open with the **municipal queue**, because
it is the surface that makes you different and the one with the number on it.

1. **Queue.** "Your crew can do 40 repairs this week. Here are the 40." Drag the
   budget slider. Show the counterfactual ratio moving. **Land on the number.**
2. **Why these 40.** Click one segment. Show exposure, darkness, confidence band.
   Show a wide-band segment next to it and say what the system does about it.
3. **Route.** Two points, safer route and shortest route side by side. Then the
   duality: "watch what happens if I ask it to route at 1am through an empty lit
   industrial road" — and show it declining to call that safe.
4. **Report.** Thirty seconds. Show the empty state — *streets worth checking
   tonight* — and explain that the app directs reporting rather than waiting for
   it.
5. **The learning curve.** Zero reports, 25, 400. "This is useful before it is
   popular."
6. **Validation.** The rank correlation and the photo of your team counting
   pedestrians at 21:47.

Close on the counterfactual ratio again. First number they hear and last.

## Judge Q&A — rehearse every one, assign an owner

**"Where did you get streetlight data?"**
Straight answer, volunteered before they dig: per-lamp geometry for Bellandur,
HSR and the ORR corridor from OpenCity, which turns out to be an OSM export;
ward-level counts for all 198 wards; and a two-date citizen audit of 800 lamps in
Vasanthanagar from 2019 that gives us an empirical failure rate. For everything
else we estimate darkness rather than reading it, and every segment carries a
confidence band. BBMP's own complaint records have no coordinates and no pole
IDs, so we are at parity with the municipality on day zero and ahead of it the
moment a report carries a GPS fix.

**"How much of this data is real?"**
Say it before you are asked. These 31 reports are ours from last night, here is
the photo; these 400 are simulated to demonstrate the learning curve and they
render differently on the map.

**The challenge question — footfall validation.**
`validation.md` has the 45-second spoken version. Learn it. This is the one they
care about.

**"Isn't a lit street always safer?"**
No, and that is why the model uses footfall with opposite signs in the two
surfaces. Jacobs, eyes on the street. The empirical literature is mixed — a US
RCT found real reductions, a UK study of local-authority switch-offs found no
increase in crime or collisions. We do not claim lighting causes safety; we claim
exposure to darkness is a cost worth ordering repairs by.

**"Your weights are arbitrary."**
Two of them are, and they are sliders because the municipality should own that
choice, not us. The third is fitted against night pedestrian crash counts. Here
is the slider — pick your own weights and watch the ranking change.

**"What stops people spamming reports?"**
Photo, GPS, timestamp, spatial dedupe, a confidence threshold before a report
moves the queue, per-device rate limiting. And structurally: a single report
never reorders anything on its own, because the posterior needs evidence to move.

**"Why don't you have the real streetlight data?"**
Because it is gated, and we can show you exactly where. Ninety-three Indian
cities publish streetlight *counts* through MoHUA's Smart Cities portal and zero
publish coordinates — the D24 template is a KPI return, not an asset register.
The pole-level geometry is on IUDX: here is the Bengaluru record, `deviceID` plus
a GeoJSON Point, published by the local authority, marked private, behind a
Request Resource button. So we made Roshni speak IUDX's schema natively and work
without it. Our ask is that someone approves the request.

**"How does this scale beyond Bengaluru?"
The pipeline needs a road network, a ward boundary file, and any per-ward lamp
count — the first is universal, the other two exist for every corporation even
when they are not published. Production Roshni consumes the geotagged asset
registers that already exist under the SLNP/ESCO street-lighting contracts, via a
data-sharing agreement. We are not asking anyone to survey anything new.

**"What would you do with another week?"**
Fit the transfer model properly across wards with different urban form, add
footpath existence from OSM `sidewalk` tags, and instrument the reporting loop to
measure whether targeted requests actually get answered. Do not answer this with
features. Answer it with the next thing you would try to *learn*.

## The closing slide

One screenshot, split: the IUDX `Request Resource` button on the left, the public
sample record on the right —

```json
{"deviceID": "L0302", "location": {"type": "Point", "coordinates": [77.666046, 12.841758]}}
```

— and one line under it: **the data exists, for our city, one approval away, and
we already speak its schema.**

End on the counterfactual ratio after it. First number they hear, last number
they hear.

## Things to say unprompted

Volunteering a limitation is worth more than defending one. Pick three:

- VIIRS nighttime lights are 500 m per pixel — five to ten city blocks — so they
  cannot tell you a street is dark, and we do not use them that way.
- Google review counts undercount thelas, tea stalls and informal vendors, which
  is exactly the population most exposed to dark streets.
- Tree canopy is a large effect on perceived street lighting in Bengaluru and we
  have no data for it.

## What not to do

No LLM chatbot bolted onto the side. No blockchain. No fourth screen. No live API
calls on the demo path. Do not present a screen recording as your primary demo
unless the wifi has actually died.
