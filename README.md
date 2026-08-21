# Roshni

**A streetlight repair queue that knows who is walking.**

Bengaluru's civic grievance system received 126,974 complaints between January
and 19 June 2025. **31.4% of them — roughly 225 a day — were "Street Light Not
Working."** BBMP closes 96.4% of electrical complaints. They are not slow. They
are not under-resourced relative to the task.

They are solving the queue in the wrong order.

A first-come complaint queue is sorted by *who filed*, not by *what is broken* or
*who is exposed to it*. Complaint volume in BBMP's own data concentrates in
peripheral wards — Horamavu (3,128), Jnanabharathi (2,842), Thanisandra (2,480)
— newer, more app-literate, more car-owning areas. The older, denser, more-walked
inner wards file fewer complaints. Not because their lights work. Because the
people on those streets at 11pm are not the people who file tickets.

Roshni re-sorts that queue by **pedestrian exposure**: how many people walk past
a broken light, at night, weighted by how little else is lit around it.

## What it produces

Not a heatmap. A worklist:

> Your crew can complete 40 repairs this week. Here are the 40 that restore the
> most exposed pedestrian-kilometres of night walking. The complaint-log order
> would have restored 38% as much.

That number — the counterfactual against the status quo — is the product.

## Three surfaces

**Report** (citizen). Photograph a dark street, GPS and timestamp attached. Its
second job matters more than its first: the app tells you *where reporting is
most valuable* — the segments with high exposure and low confidence. The report
form is an active-learning loop, not a suggestion box.

**Route** (citizen). Walking directions that price darkness into the edge weight,
shown alongside the shortest route so the user chooses. Never routes through a
segment we have no data on.

**Queue** (municipality). The hero surface. A ranked repair worklist with a
budget slider, tunable priority weights, and a live counterfactual against
complaint order.

## Quickstart

```
python data/fetch.py          # pulls every source in data/manifest.json
```

Then read `docs/data-sources.md`, because half of what fetch.py downloads is not
what its filename suggests.

## Honest limits

We do not have a streetlight inventory for Bengaluru and neither does BBMP —
their own complaint records are ward-level free text with no coordinates. Roshni
estimates darkness rather than reading it, and shows a confidence band on every
segment. See `docs/cold-start.md` for how that is defensible and where it is not.
