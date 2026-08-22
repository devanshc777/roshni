# The demo, beat by beat

Five minutes. One browser tab. `python -m http.server 8080 --directory web`.

The whole demo is four clicks. Everything below is written to be said out loud —
if you need to read a paragraph off the screen, the screen has failed.

**Before you start:** full-screen the browser, confirm the map has drawn, and
leave the app on the **Map** tab. If you have touched the sliders, hit Reset on
the City screen first.

---

## 0 · The opening line (20 seconds, no screen)

Do not open with "we built a dark-zone map". Open with the problem, because the
problem is the interesting part:

> BBMP closes **96.4%** of electrical complaints. They are good at fixing. The
> queue is the problem: it is sorted by who complained first, and complaining
> tracks app-literacy and car ownership, not how many people walk that street at
> 11pm.
>
> A first-come queue is a competent machine pointed the wrong way. Nobody has to
> work harder or buy anything. They need the list in a different order.

That frames everything after it as a fix rather than a feature.

---

## 1 · Map — "this is Bengaluru after dark" (45 seconds)

Say nothing for three seconds and let them look at it.

> Every ward boundary in Bengaluru — all 225. The dashed rectangle is what we
> measured: 24 wards, about 765,000 people. The rest is context.
>
> Colour is how likely a street is to be unlit. **Width is how many people walk
> it after dark.** So the bright thick line across the middle is the Outer Ring
> Road service corridor — dark *and* heavily walked. That is the whole product in
> one glance.

Then click one segment on the ORR corridor.

> Likely dark, among the busiest, and we only have an estimate — no lamp evidence
> here. Repair priority number three.

**The point to land:** the map is not showing broken lamps. It is showing broken
lamps *weighted by who is exposed to them*. That distinction is the differentiator
the problem statement asks for.

---

## 2 · The sequence — "here is why the queue is wrong" (75 seconds)

Click **See how reports change this**.

Let them read the two columns. Then:

> Same city, same night, two worklists. On the left, first-come ordering. All
> five repairs land in **one ward** — BTM Layout, because BTM Layout files the
> most complaints. On the right, ours: the ORR service roads in Bellanduru and
> Marathahalli, where people are actually walking.

Click **Simulate reports**. Let it run.

> Reports arriving the way they really arrive — commercial, app-literate streets
> first. That bias is not a flaw in the demo, it is the thing we exist to correct.

Let it finish, then read the reveal:

> The walker's unknown ground fell from 63% to 6% — citizen reports genuinely fix
> what a *pedestrian* can see. But the top 40 repairs changed by **one street**,
> because 1,200 reports came from places we already knew about.
>
> **That is the finding.** Reports alone do not fix the ordering. Crowdsourcing
> more complaints just amplifies the existing bias. Fixing the order needs the
> exposure model.

**This is the beat that wins or loses the pitch.** Do not rush it, and do not
apologise for the worklist barely moving — it is the argument.

Close the overlay.

---

## 3 · Walk — "what a person gets" (40 seconds)

Click **Walk**.

> Two ways home. Better lit is 1.85 km, shortest is 1.58. Three minutes longer,
> and it keeps you off 846 metres of street we have no lighting data for.
>
> Note what this does *not* do: it does not hide the short route, and it does not
> throw a safety warning. It offers an alternative and states honestly what we do
> not know. We avoid what we cannot see; we never certify that a street is safe.

If asked how the routing works: same graph, two Dijkstra runs — one weighted by
metres, one by a penalty built from darkness, exposure and uncertainty. Wide-band
segments are priced at 9× rather than deleted, so a route always exists.

---

## 4 · Report — "and this is how the data arrives" (35 seconds)

Click **Report**, then the big button.

> One tap. No account, no lamp number — nobody standing on an unlit road at 23:00
> can identify a lamp post, and asking them to sign up first guarantees no data.
>
> And then the thing no civic app does: **your report moved this street from #70
> to #44 in its ward's repair queue.** Not "thank you, ticket logged".

Wait for the verification prompt to appear, then point at it:

> The city says this was fixed — is it? Closure and repair are different things,
> and this is the only place anybody gets asked which one actually happened. It
> means a ward can be told what share of that 96.4% nobody ever confirmed on the
> street.

---

## 5 · City — "and this is what gets bought" (40 seconds)

Click **City**.

> Same estimate, the other direction. Forty repairs, ranked by how much darkness
> reaches people on foot. **7.8× the pedestrian exposure the complaint queue's
> first forty repairs would have restored.**
>
> Grouped by street, because a crew is dispatched to a street: Service Road,
> Bellanduru, 2,281 metres across 13 stretches.

Toggle **Complaint order** and back.

> And it ends in a CSV, not a dashboard. A dashboard that can only be looked at
> is how every civic analytics project dies.

If you have time, open **Tune scoring** for three seconds and close it again:

> The weights are there if a city disagrees with ours. They are not the pitch.

---

## 6 · Coverage — only if asked, or if you have 20 seconds spare

Click **Coverage**.

> A road network is the only hard requirement. Everything else narrows the
> confidence bands — none of it unlocks a feature. We ran it on Bengaluru because
> Bengaluru publishes unusually good open data.
>
> We have **not** run a second city. Portability is an argument from
> architecture, not a demonstration. We would rather say that than show you a
> city dropdown that does nothing.

Volunteering the limit before being asked is worth more than the claim.

---

## The questions you will get

**"How do you validate footfall with no usage data?"** — the PS challenge
question, and the one to prepare hardest.

> Three steps. Estimate from observable proxies: road class, connectivity,
> night-active land use, transit access. Validate by counting a sample — 10 to 20
> streets spanning the predicted range, by hand or camera, prediction against
> observation. Calibrate, and report the residual.
>
> But the important part: **we do not need a correct footfall number. We need an
> ordering good enough to beat complaint order.** So the number to look at is not
> our headline — it is what survives taking our evidence away. Delete every lamp
> label we hold and it is still **5.42×**. Hold geography and coverage constant
> and it is **6.4×**.

Do **not** answer this with "beta-binomial posterior". That answers a question
nobody asked.

**"Isn't 7.8× just because you picked an easy baseline?"**

> Four stress tests. Against the mean baseline, 7.7×. Against the luckiest of 300
> draws, 4.9×. Against a steelman that picks the worst street in every ward it
> visits, 1.89×. With all lamp labels deleted, 5.42×. It is not a coverage
> artefact.

**"93.7% of your segments have no lamp evidence — so you're guessing?"**

> Yes, and the product says so on every screen. That is why every street carries
> a confidence band and why the band *changes behaviour*: the router avoids the
> least-certain fifth of the network, and the report screen deliberately sends
> people to it. Uncertainty is a control signal, not a disclaimer.

**"Why not just fix the worst streets — why routing at all?"**

> We tested that. On the 25 worst segments, **6 have no walkable alternative at
> all**, and 19 need a detour over 3× — median 17.9×. Routing cannot save the
> worst streets. Only repair can. Which is why the repair queue is the product and
> the route is the reason anyone opens the app.

**"Can this run in my city?"** — see Coverage above. Name the limit.

**"Where does the 7.7 vs 7.8 difference come from?"**

> The browser recomputes it live with a different RNG than the pipeline. Same
> method, same 300 draws, about 1% sampling noise. The canonical figure is 7.73×.

---

## Traps

- **Do not say "2020–2025" about the complaint data.** The 126,974 rows are
  1 Jan – 19 Jun 2025.
- **Do not quote a per-street footfall count.** We show a relative index on
  purpose; an absolute count would invent the quantity we say must be validated.
- **Do not claim convergent validation.** Spearman ρ came out at 0.03 between the
  two exposure halves. It failed, and the failure is the more honest story.
- **Do not use the office-hours-timestamp argument.** The grievance clock is a
  12-hour field with AM/PM stripped. The claim is dead.
- **Do not claim a second city.** Ever.
- **Do not open the sliders early.** They are the answer to a question, not the
  first impression.
- **If the map has not drawn, reload before speaking.** Never narrate a blank map.
