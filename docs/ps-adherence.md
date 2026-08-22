# Are we actually building the problem statement?

Audited against the PS text itself rather than against our own narrative. Method
borrowed from `the-fool` (jeffallan-skills): steelman the position, then attack
it, then rebuild.

**Verdict up front: no, not yet. The one screen we built is the one the problem
statement does not ask for.**

---

## 1. What the PS literally asks for

> Streetlight repair queues typically follow first-come complaint logs without
> factoring in nighttime commuter footfall, leaving dark arterial streets
> carrying late-night commuters unprioritized. **Build a pedestrian-centric
> streetlight reporting and routing system.**
>
> **Key Differentiator:** A **public** "dark-zone risk map" that weights repairs
> by pedestrian exposure **and recommends well-lit, safer alternate routes for
> night walkers.**
>
> **Challenge Question:** How would you validate a footfall estimate for a
> street where no official usage data exists at all?

Four named deliverables. Scored honestly:

| PS asks for | State | Note |
|---|---|---|
| **reporting** system | **not built** | Mockup exists (`assets/screen-report.png`). No working screen. |
| **routing** system | **not built** | Routes are computed (`out/routes.json`, `out/graph.json`) but there is no UI. |
| **public** dark-zone risk map | **not built as public** | What we built is a municipal engineer console. Dense, internal, correct — and not the public artifact the PS names. |
| weights repairs by pedestrian exposure | **built, strong** | This is our best work. 7.6× measured, robust to two ablations. |
| Challenge question | **1 of 4 layers measured** | Convergent ρ = 0.30 done. Criterion, ground-truth, transfer: unmeasured. |

**Two of five green.** The queue console is excellent and it is a differentiator,
but the PS describes it as a *consequence* of the public map, not as the product.

### The steelman, and why it only half holds

*"The queue is where the differentiation is. 'Weights repairs by pedestrian
exposure' is in the differentiator verbatim, so the queue serves the PS."*

Half true. The weighting is required and we have it. But the sentence says the
**public risk map** is the vehicle that does the weighting, and the system is
described as **"reporting and routing"**. A judge with the PS in front of them
will look for a citizen surface first. We currently open with an internal tool.

### The correction

Build all three. Order the story so the public surfaces are the front door and
the queue is the payoff — *this is what the city does with what you gave it.*
That happens to be the flow structure that makes it marketable anyway (§3).

---

## 2. Is it a general solution, or did we just do Bengaluru?

Fair challenge. Audited by asking what would actually break if the bbox moved to
Pune tomorrow.

### What is general

The road network (OpenStreetMap, every city on earth). The `highway=street_lamp`
and `lit=*` tags. The darkness model, the exposure model, the triage optimiser,
the routing penalty, the confidence machinery, the report-targeting rule. None of
these contain the word Bengaluru.

### What is city-specific

Three loaders, and each one is optional:

| Input | Bengaluru source | Elsewhere | If missing |
|---|---|---|---|
| Road network | OSM | OSM | **mandatory** — this is the only hard requirement |
| Ward boundaries | BBMP 2015 KML | any municipal boundary file | fall back to a single zone; the prior loses spatial resolution |
| Per-ward lamp counts | BBMP ward returns | SLNP/ESCO returns, any lamp census | fall back to the class-weight prior alone; bands widen |
| Complaint log | BBMP grievance CSV | any 311/CRM export | the counterfactual cannot be computed, the queue still can |
| Transit | BMTC GTFS | any GTFS feed | structural exposure falls back to betweenness alone |
| Telemetry | IUDX (gated) | any smart-lighting feed | prior instead of measurement |

**That is the generality claim, and it is checkable: the system runs on OSM
alone. Every additional source narrows the confidence bands rather than
unlocking a feature.** Nothing is load-bearing except the road network.

### The honest limitation

The *loaders* are Bengaluru-shaped. A new city needs a schema mapping per source
— an afternoon of work per city, not a redesign. And we have not run it on a
second city, so "it generalises" is an argument from architecture, not a
demonstration. Say that. Do not claim portability we have not exercised.

### The framing to use

> The system needs a road network. That is it. Everything else is optional and
> each optional source narrows the bands.
>
> We ran it on Bengaluru because Bengaluru has unusually good open data — a
> public six-year complaint log, ward-level lamp counts, a GTFS feed with
> departure times, and 1,128 citizen-labelled lamps. So Bengaluru is not the
> product. It is the deepest available proof that the product works.

That is exactly the shape the user proposed, and it is stronger than "we built a
Bengaluru app" in both directions: more general to a judge thinking about scale,
and more credible to a judge thinking about evidence.

---

## 3. The product story — input → resolution → two outputs

The current deck explains the *model* first. That is backwards for a product
pitch. Restructure around the flow, which is what people can hold in their head:

```
   WHAT GOES IN                    WHAT COMES OUT
   ───────────────                 ──────────────────────────────────
   City gives:                     PEDESTRIAN gets
     road network (required)         "walk this way tonight"
     ward boundaries                 two routes, honest comparison
     lamp counts                     a warning, never a block
     complaint log
     transit feed                  MUNICIPALITY gets
                                     "fix these 40 first"
   Citizen gives:                    a CSV work order, ranked
     one tap: "this is dark"         a counterfactual against its own queue
     GPS + time, photo optional
                                   ┌──────────────────────────────┐
                                   │ WHEN IT IS RESOLVED          │
   ( our model sits here, and      │ pedestrian: your street was  │
    we explain it separately )     │   fixed, your report did it   │
                                   │ municipality: closed, or      │
                                   │   actually fixed?             │
                                   └──────────────────────────────┘
```

Three sentences that carry the whole product:

1. **You tell us a street is dark.** One tap. No account, no fixture ID — nobody at 23:00 can identify a lamp post.
2. **Tonight, you get a safer way home.** Two routes, side by side, with how much of each is dark and how much we are unsure about. You choose.
3. **This week, the city gets a work order** ordered by how many people actually walk there — not by who complained first.

And the loop closes: when it is fixed, the person who reported it finds out, and
the city finds out whether "closed" meant *fixed*.

**The model is not the story. The model is the answer to "how do you know?"** —
which is a different slide, asked by a different judge.

---

## 4. So the user-facing screens must be simple

Correct, and the current console proves the point by contrast: it is dense
because its user is a municipal engineer looking at forty rows on a Monday. That
density is right *there* and wrong everywhere else.

Design rule per surface:

| Surface | User | Decisions on screen | Density |
|---|---|---|---|
| **Report** | someone walking alone at 23:00 | **one** — tap the button | almost empty. One action above the fold, nothing competing |
| **Route** | someone deciding how to get home | **one** — safer or shorter | two cards, one strip, one map |
| **Queue** | municipal engineer, Monday, desk | many, deliberately | dense. Linear's issue list, not a phone app |

Concretely for the citizen screens:

- No jargon on screen. Not "posterior variance" — **"we don't have data here."** Not "exposure" — **"busy after dark."** Not "P(dark) 0.89" — **"usually dark."**
- No numbers the user cannot act on. Distance and minutes, yes. Beta parameters, no.
- One primary action, one colour. Everything else recedes.
- Uncertainty stated in words, not read off a scale: *"parts of the shorter way have no lighting data — the safer route avoids them."*
- Never block, never alarm. Offer, and let the person choose.

The model's vocabulary belongs in the console, the deck, and our mouths. Not on
a phone at night.

---

## 5. What this changes, in order

1. **Build the Route screen.** PS names it. `out/graph.json` is ready, 25,342 nodes, 85% connected. Dijkstra twice, comparison strip, plain words.
2. **Build the Report screen.** PS names it. One button, then "streets worth checking tonight".
3. **Make the public map public.** Same data, citizen framing: where is dark, where do we not know. No sliders, no worklist.
4. **Reorder the deck** around input → resolution → two outputs, with the model moved behind "how do you know?".
5. **Close a validation leg.** Criterion validation against the BTP crash PDFs is the highest-value remaining task in the whole project and it needs a highlighter, not a parser.
6. **State the generality claim as the input ladder**, and admit we have not run a second city.

Item 5 is the one that answers the challenge question with evidence instead of
architecture, and the challenge question is the part of the PS that tells you
where the marks are.
