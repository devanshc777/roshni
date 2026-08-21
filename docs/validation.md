# The challenge question

> *How would you validate a footfall estimate for a street where no official
> usage data exists at all?*

## Read the question properly first

They did not ask how to *produce* an estimate. They asked how to *validate* one.
That distinction is the whole answer, and most teams will not notice it — they
will answer with a list of data sources, which is a response to a different
question.

Validation requires **an independent signal you did not use to build the
estimate.** If you build a footfall index from POI density and then "validate" it
against POI density, that is circular and a competent judge will name it in ten
seconds. So the first structural move is to split every source into two piles and
never let them touch:

- **Build pile** — inputs to the model.
- **Validate pile** — held out, never seen by the model, used only to score it.

The second structural move is to be clear about **what claim you are actually
validating.** With no ground truth you will never validate an absolute number.
"Four hundred and twelve pedestrians per hour on this street" is unfalsifiable
and you should not say it. What you *can* validate is an **ordering**: that the
model ranks streets by footfall in roughly the right order. Rank is the claim.
Magnitude is not. Saying this out loud, before you are asked, is the difference
between a team that built a model and a team that understands one.

---

## The four-layer answer

Give the architecture, not the source list.

### Layer 1 — Convergent validation

> **MEASURED 22 Aug 2026 — this layer failed, and the failure is the better
> result.** Spearman ρ(activity, structural) = **+0.031** over 1,164 real
> segments; ρ(activity, night bus departures) = **−0.135**. Not a tie artefact
> (1,105 non-degenerate), not a broken graph (that bug was found and fixed
> first), same answer on arterials alone (ρ = 0.022). The two proxies are not
> two views of one latent footfall — they track two different night populations.
> Blending them evenly averages away the population this problem statement
> names, so the structural half now leads at 0.75. Read
> `docs/measured-2026-08-22.md` §5 before presenting this section.

Build **two estimates from disjoint inputs** and check whether they agree.

- **Estimate A: activity-based.** POIs open after 22:00, weighted by
  `user_ratings_total` as a revealed-preference proxy for visits.
- **Estimate B: structural.** Edge betweenness centrality on the OSMnx walking
  graph, plus BMTC stop trip-counts within a 400 m buffer.

These share no inputs. A uses commercial activity; B uses network topology and
transit service. If they rank-correlate at, say, Spearman ρ = 0.6, that is real
evidence that both are measuring the same latent thing — because there is no
mechanism by which two unrelated proxies agree by accident on a spatial ordering.

Report the ρ. Report where they *disagree*, too. Disagreement is informative:
streets where structure says "busy" and commerce says "empty" are typically
transit corridors through residential or industrial land — and those are exactly
the dark arterials your problem statement is about. **The disagreement set is a
feature, not an error.** Surface it in the UI.

### Layer 2 — Criterion validation

Correlate your risk score against **night pedestrian road crashes**, a variable
the model never saw.

Night pedestrian casualties are an *outcome* of (footfall × darkness). If your
predicted risk ranks high exactly where night pedestrian crashes cluster, that is
external criterion evidence, and it is not circular because crash data never
entered the model.

Sources are the Bengaluru Traffic Police road safety reports in
`data-sources.md` §D1. They are PDFs, so budget a person and a highlighter for
the named blackspots and the day/night pedestrian split, not a parser.

Two honesty caveats to volunteer:

- Crash data is itself **reported** data, with its own under-reporting bias, and
  it is sparse — you will have tens of points, not thousands.
- Crashes need exposure *and* vehicle speed. A correlation of 0.4 here is a good
  result, not a weak one, and you should say so rather than hoping nobody asks.

### Layer 3 — Ground truth

Go outside and count.

Two of you, twenty minutes, eight segments at 21:30. Two the model scores high,
three medium, three low — stratified, not convenience-sampled, or the correlation
is meaningless. Count pedestrians in a fixed five-minute window per segment.

n=8 proves nothing statistically. That is not the point. The point is that you
are the only team in the room whose model touched the physical world, and the
photograph of your teammates counting people on a footpath at 21:47, next to the
scatter plot, does more work in a pitch than any amount of methodology.

Report **Spearman rank correlation**, not Pearson — you are validating an
ordering, and with n=8 a rank statistic is the only defensible choice.

### Layer 4 — Transfer validation

This is the layer that answers the question as literally asked: *a street where
no official usage data exists at all.*

**Fit where data exists, apply where it does not.** Take a corridor that has
BMTC GTFS coverage, dense OSM POIs and known crash history — an ORR stretch, say
— fit your weights there, then apply the fitted model to a peripheral ward with
none of that. Then report the **honest degradation**: how much worse should we
expect the estimate to be, given which inputs are missing?

The generalisation of this is what a judge is really testing for:

> A footfall estimate for a data-free street is only ever as good as the
> *transferability* of the relationship you fitted elsewhere. So the thing to
> validate is not the number — it is the stability of the coefficients across
> held-out geographies. If the POI-to-footfall relationship fitted in
> Indiranagar also holds in Peenya, it will probably hold on the street with no
> data. If it does not, you have learned something more useful than a number:
> that footfall models do not transfer across urban form, and the system should
> refuse to guess there and ask for a report instead.

That last clause is the bridge into the product. A model that knows where it is
untrustworthy is the thing that makes the reporting screen intelligent — see
`cold-start.md`.

---

## Negative controls

Cheap, fast, and almost nobody does them. Pick places where you *know* the answer
and check the model agrees:

- An industrial cul-de-sac at 01:00 should score near zero. If it does not, your
  POI weighting is broken.
- A stretch outside a major bus terminus at 22:00 should score high.
- A gated-layout internal road should score low on through-movement and moderate
  on residential exposure — and if your model cannot distinguish those two, your
  exposure variable is under-specified.

Three negative controls take fifteen minutes and catch the class of bug that a
correlation coefficient hides.

---

## Put the uncertainty in the interface

Every other team will render one confident number per street.

Render a **confidence band**. Segments where you have a report, a mapped lamp,
GTFS coverage and POIs get a narrow band. Segments where you have nothing but a
ward-level prior get a visibly wide one, drawn differently on the map — hatched,
desaturated, whatever reads as *we do not know this*.

This is not decoration. It changes what the product does: the routing engine
**refuses to route through wide-band segments** rather than pretending, and the
reporting screen **sends people to them**. Uncertainty becomes a control signal
rather than a disclaimer.

---

## The 45-second spoken answer

If a judge asks the challenge question live, this is the shape:

> You cannot validate the number, so we do not claim one — we claim an ordering,
> and we validate that four ways. First, convergently: we build two estimates
> from completely disjoint inputs, one from night-open commercial activity, one
> from pure network structure plus bus service, and we check they rank-correlate.
> Two unrelated proxies do not agree by accident. Second, against a criterion the
> model never saw — night pedestrian crash locations, which are an outcome of
> footfall times darkness. Third, we went out at half nine last night and counted
> pedestrians on eight segments; here is the rank correlation and here is the
> photo. And fourth, we fit the weights on a corridor that has data and applied
> them to a ward that has none, so what we are really validating is whether the
> relationship transfers. Where it does not transfer, the system does not guess
> — it widens the confidence band, refuses to route through the street, and asks
> a human to go look.
