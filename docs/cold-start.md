# Cold start

> *"Streetlights not being there from before is a major downside — how does the
> reporting go? Does it work out as: we propose, people go figure it out for a
> while, then we come online with all issues and all problems?"*

That is the right worry and it has a better answer than "yes, wait for reports."

## Reframe one: you are not missing something BBMP has

The instinct is that a real system would start from a streetlight inventory and
you are handicapped without one. **BBMP does not have one either.** Look at their
grievance schema:

```
Complaint ID, Category, Sub Category, Grievance Date, Ward Name, Grievance Status, Staff Remarks, Staff Name
```

No pole ID. No coordinates. Not even a street name field. The municipal system
this project is proposing to improve is operating on *ward-level free text*. You
are not behind the state of the art — you are at parity with it on day zero and
ahead of it the moment you attach a GPS coordinate to a report.

Say that on stage. It reframes your biggest weakness as the industry baseline.

## Reframe two: the unit is not the lamp

The instinct — *lamp + map = public map* — is the trap. It makes the lamp the
atom, which forces you to enumerate lamps, which you cannot do.

**The atom is the road segment, and the quantity is darkness, not lamp count.**

A pedestrian at 23:00 does not care whether this street has eleven lamps or
fourteen. They care whether the next two hundred metres are lit. Darkness per
segment is a *continuous latent variable you can estimate*; lamp inventory is a
*discrete enumeration you cannot obtain*. Choosing the estimable quantity is the
single most important modelling decision in this project.

This also fixes the reporting UX. "Report a broken streetlight" requires the user
to identify a specific fixture, which is friction and produces unmatchable
records. "**This stretch is dark**" — one tap, GPS, optional photo — is what
people can actually answer at night, and it maps directly onto your atom.

## The model: a prior that is never empty

Give every segment a Beta-distributed darkness probability.

**Prior.** Ward *w* has a published lamp count `L_w` (198 wards, `data-sources.md`
§B2). Compute ward road length `R_w` from OSM. Lamp density `d_w = L_w / R_w`
gives lamps per kilometre for that ward. Distribute along the ward's segments
weighted by road class — arterials get more lamps per km than residential lanes,
which is both true and codified in national lighting practice. Convert expected
coverage into `Beta(α₀, β₀)` with a **small pseudo-count** so the prior is weak
and moves easily.

**Evidence.** Every observation updates it:

| Observation | Effect |
|---|---|
| Citizen report: "dark here" | `β += 1` |
| Citizen report: "fine here" | `α += 1` |
| OSM `highway=street_lamp` node on segment | `α += w_osm` |
| OSM lamp tagged non-functional (the Bellandur KML) | `β += w_osm` |
| OSM way tagged `lit=no` | `β += w_tag` |
| Historical BBMP complaint in this ward | weak `β` bump, ward-wide |

**Posterior mean** is the darkness score. **Posterior variance** is the
confidence band. Both fall out of the same two numbers, which is why this
structure is worth the twenty minutes it takes to implement rather than a
hand-rolled weighted average.

Three properties you get for free, all of which are demo moments:

1. **Day zero is not empty.** Every segment has a defensible score from the ward
   prior alone.
2. **Reports have visibly diminishing returns.** The fifth report on a segment
   moves the posterior far less than the first. So the system naturally stops
   asking for reports where it already knows, without you writing any logic for
   that.
3. **Confidence is a first-class output**, not a caveat bolted on at the end.

## The bootstrap loop: reporting is directed, not passive

Here is the part that turns your weakness into the feature.

A suggestion box waits for reports. Roshni **asks for specific ones**. Rank every
segment by

```
report_value = pedestrian_exposure × posterior_variance
```

High exposure and high uncertainty means *a report here changes a repair
decision*. Low exposure or already-certain means *a report here changes nothing*.
Surface the top *n* as "**streets worth checking tonight**" — on the map, and as
the empty state of the report screen.

This is active learning, and it is roughly fifteen lines of code. It is also the
honest answer to the bootstrap question:

> The system does not need many reports. It needs the *right* reports. With
> 198 wards of prior and a few hundred targeted reports on high-exposure
> uncertain segments, the repair queue is already better ordered than
> first-come — and we can show you exactly how much better at each level of
> coverage.

## Show the learning curve in the demo

Twenty seconds, and it kills the cold-start question before it is asked.

Run the pipeline at four report volumes — 0, 25, 100, 400 — and plot the triage
quality metric (exposed pedestrian-km restored per repair, versus complaint
order) against report count. Three states on the map, side by side: prior-only
with everything hatched wide; after 25 targeted reports; after 400.

The curve should rise steeply and then flatten. That shape is the argument. It
says *this is useful early*, and it says *we know when to stop asking*.

If you have time for one extra experiment, run it twice: once with reports drawn
at random, once with reports drawn by the active-learning ranking. The
targeted curve should dominate. That is a real result and it took you an
afternoon of compute.

## Where the synthetic line is, and how to stay on the right side of it

You will need reports on demo day that you did not collect. Fine. The rules:

1. **Label them in the UI.** A synthetic report renders differently from a real
   one. Not in a footnote — on the pin.
2. **Collect a real seed set.** Thirty genuine reports from one evening's walk
   around your demo bbox. Four people, ninety minutes. This is not optional; it
   is what makes the demo a demonstration rather than a mock.
3. **Say it first.** "Four hundred of these are simulated to show the learning
   curve; these thirty-one are ours from last night, and this is the photo."
   Volunteered, it is a design decision. Discovered by a judge, it is a lie.

The failure mode that ends teams is not having synthetic data. It is having
synthetic data that a judge finds.

## What this does not solve

Be clear-eyed about the residual:

- The ward prior is only as good as the ward lamp counts, and those are of
  **unknown vintage** — check the file's date before quoting it as current.
- Darkness inferred from lamp density ignores tree canopy, which in Bengaluru is
  a genuinely large effect on perceived street lighting and which you have no
  data for. Mention it as known-unmodelled; it shows you have walked the city.
- A Beta posterior on "is this segment dark" says nothing about *which* fixture
  to send a crew to. Your municipal output is therefore a **prioritised segment
  list, not a work order.** Do not overclaim it as the latter — the last mile is
  still a person with a ladder finding the pole.
