# Positioning

April Dunford's five steps, in order. Start from what the customer would do if
we did not exist — never from our features, and never from the market category.

The important structural fact first: **this product has two sides, and only one
of them is the buyer.** The pedestrian is the user and the sensor. The
municipality is the customer. Positioning follows the money; the citizen surface
is how the data arrives and how the purchase gets political cover.

---

## 1. Competitive alternatives — what happens without us

**For a municipal street-lighting division:**

| Alternative | What it actually does | Where it falls down |
|---|---|---|
| **Do nothing** — keep the first-come complaint queue | Works. BBMP closes 96.4% of electrical complaints | Ordered by who complained, and complaining tracks app-literacy and car ownership, not footfall |
| Smart-lighting CMS from an SLNP/ESCO vendor | Real telemetry, real control | Needs a retrofitted node on every pole. Capex per lamp, years to roll out, and it tells you a lamp is out — not which outage matters most |
| Commission a lighting audit | Accurate on the day | One-time, expensive, stale within a fortnight — our own data says 4% of working lamps die every two weeks |
| Build an internal dashboard on their own complaint data | Cheap, familiar | Visualises the same queue in the same order. Reorders nothing |
| Deploy a citizen reporting app (FixMyStreet, Mark-a-Spot, a 311 app) | More reports arrive | More complaints, same first-come ordering. It amplifies the bias rather than correcting it |

**For someone walking home at 23:00:** take the main road and hope; use Google
Maps walking directions, which have no lighting layer at all; check SafetiPin,
which gives an area score rather than a route; or pay for an auto or a cab —
which is what most people with the means actually do, and is the clearest
evidence the problem is real.

**"Do nothing" is the primary alternative on the municipal side, and it is a
competent do-nothing.** That matters: we are not competing with failure. We are
competing with an execution machine that works and is pointed the wrong way.

---

## 2. Unique attributes — verifiable, not spin

1. **Orders repairs by estimated night pedestrian exposure rather than complaint arrival, and quantifies the gap.** 7.7× the exposure-metres restored at a 40-repair budget; 1.9× against a steelman that picks the worst street in every ward it visits; 5.4× with every lamp label we hold deleted.
2. **Works with no lamp inventory.** The only hard requirement is a road network. Ward boundaries, lamp counts, complaint logs, transit feeds and telemetry are each optional, and each one narrows the confidence bands rather than unlocking a feature.
3. **Every segment carries a confidence band, and the band changes behaviour.** The router avoids the least-certain fifth of the network; the report screen sends people to it. Uncertainty is a control signal, not a disclaimer.
4. **Directed reporting.** It asks for reports where a report would change a repair decision. Measured: 400 targeted reports clear twice the uncertainty on busy-after-dark streets that 400 naturally-arriving reports do.
5. **It can ask "closed, or fixed?"** Verification is a separate state from closure, so a ward can be told what share of its closures nobody on the ground ever confirmed.
6. **It speaks the municipal exchange's record shape natively.** The lamp and telemetry records are copied verbatim from IUDX, so switching from estimate to measurement is a credential change, not a rewrite.
7. **The output is a work order, not a view.** A CSV a crew can be dispatched against.
8. **No hardware. No survey. No network at demo time.**

## 3. Value — what those attributes enable

**Municipality:** more safety per repair rupee, with the crews, budget and
complaint desk they already have. No procurement, no poles touched, no citizens
surveyed. Plus one number they do not currently possess — how much of their own
96.4% closure rate was ever verified by a human on the street.

**Pedestrian:** a way home that avoids the dark and the unknown for a few
minutes' detour, an honest statement of what we do not know, and proof that the
report they filed moved their street up the queue.

The one-sentence translation for each:

> *City:* fix the streets that carry people, not the streets that carry
> complaints — starting Monday, with the crew you already have.
>
> *Walker:* three minutes longer, and it keeps you off 846 metres of street
> nobody has any lighting data for.

## 4. Best-fit customer — tightly

Not "cities". Not "smart cities".

> **The street-lighting or electrical division of a large municipal corporation
> that already closes fault complaints quickly, has no geotagged lamp inventory,
> publishes or holds a complaint log, and has more dark streets than its weekly
> repair capacity can cover.**

All four conditions matter. Fast closure means execution is not the bottleneck,
so ordering is the only lever left. No inventory means the estimation machinery
is load-bearing rather than redundant. A complaint log means the counterfactual
can be computed against their own queue, in their own numbers. And capacity
below fault rate is what makes a *queue* exist at all — with infinite crews,
order is irrelevant.

That is BBMP exactly, and it is approximately every Tier-1 and Tier-2 Indian
municipal corporation.

**Anti-fit, said plainly:** a city with working telemetry on every pole does not
need our darkness estimate — though the triage layer still applies on top of
their measurements. And a city whose repair capacity exceeds its fault rate has
no queue worth reordering.

## 5. Market category — chosen last

Three options considered:

- **"Smart street lighting"** — wrong. The category implies hardware, and a buyer hearing it will ask what our node costs. We do not sell a node.
- **"Civic issue reporting"** — wrong. Reporting is our *input*, and the category's incumbents amplify exactly the bias we exist to correct.
- **"Repair prioritisation for street lighting"** — a modifier on the understood category of lighting maintenance management. This is the one.

Positioned as a **layer, not a replacement**, which is also what makes it
buyable inside an organisation that already owns a complaint desk and possibly a
CMS:

> **Roshni is a repair-prioritisation layer for street lighting.** It takes the
> queue your complaint desk already produces and reorders it by how many people
> actually walk each street after dark. It needs no lamp inventory, no new
> hardware and no survey — a road network is the only hard requirement — and it
> gives night walkers a better-lit way home, which is where the next
> report comes from.

### Pressure test

Told to a BBMP executive engineer in one sentence, does it land? *"We reorder the
queue you already have, by footfall, with no new hardware and no survey."* Yes —
it names the one thing we do, threatens nothing they own, and the objection it
invites ("prove the reorder is better") is the objection we have measured.

---

## The generality line, and its limit

> The system needs a road network. That is the only hard requirement.
>
> We built it on Bengaluru because Bengaluru has unusually good open data — a
> public six-year complaint log, ward-level lamp counts for all 198 wards, a
> transit feed with departure times, and 1,128 citizen-labelled lamps. Bengaluru
> is not the product. It is the deepest available proof that the product works.

And the limit, stated rather than hidden: the loaders are Bengaluru-shaped. A new
city needs a schema mapping per source — an afternoon per city, not a redesign —
and **we have not run it on a second city.** Portability is an argument from
architecture, not a demonstration. Do not claim otherwise.

## Where this changes the pitch

Lead with the alternative, not the feature. The strongest opening is not "we
built a dark-zone map" — it is:

> A first-come queue is a competent machine pointed the wrong way. Nobody needs
> to work harder or buy anything for this to get better. They need the list in a
> different order.
