# Roshni — product truth

## What it is

A repair-prioritisation layer for street lighting. It takes the queue a city's
complaint desk already produces and reorders it by how many people actually walk
each street after dark.

Not a lighting management system. Not a reporting app. A layer that sits on top
of both and changes the order.

## Who it is for

**Customer — the buyer.** The street-lighting or electrical division of a large
municipal corporation that already closes fault complaints quickly, has no
geotagged lamp inventory, holds a complaint log, and has more dark streets than
its weekly repair capacity can cover. All four conditions have to hold.

**User — the sensor.** Someone walking home after dark who would otherwise take
the main road and hope, or pay for a cab to avoid the problem.

The two sides are not the same person and the product must not pretend they are.
The citizen surface is how the data arrives and how the purchase gets political
cover. The queue is what gets bought.

## What each side gets

| | Gets |
|---|---|
| Walker | a way home that avoids the dark and the unknown for a few minutes' detour, an honest statement of what we do not know, and proof their report moved their street up the queue |
| City | more safety per repair rupee with the crews, budget and complaint desk they already have — and the one number they do not have today: how much of their own closure rate was ever verified by a human on the street |

## The use scene, because it decides the design

Dark. Outdoors. One hand. A phone at arm's length, screen brightness low,
walking. That is why the product is dark-first — not because dark UI is
fashionable, but because the alternative is a white rectangle in someone's face
on an unlit street.

The municipal console is the opposite scene: a desk, a Monday morning, forty
rows to dispatch against. Dense is correct there and wrong on the phone.

## Surfaces

| Surface | Visitor's success | Density |
|---|---|---|
| **Live feed** | understands how input becomes two outputs | narrative, one idea at a time |
| **Walk home** | picks a route | two cards, one decision |
| **Report** | files one report in under five seconds | almost empty |
| **City queue** | dispatches a crew | dense, deliberately |

## Product rules

- **Confidence is the core visual variable, not severity.** A street we know is dark and a street we merely suspect is dark must be distinguishable at a glance. Carried by texture, never by hue alone.
- **No jargon on citizen surfaces.** "usually dark", never "P(dark) 0.89". "we don't have data here", never "posterior variance".
- **Never block, never alarm.** Offer the alternative and let the person choose. Always show the shortest route beside the safer one.
- **Advisory, not a guarantee.** Stated on the surface, not buried in a footer.
- **The output is an artifact, not a view.** A dashboard that can only be looked at is the documented failure mode of this whole category.
- **Uncertainty does something.** The router avoids the least-certain fifth of the network; the report screen sends people to it.
- **No account, ever.** Location before identity. Nobody standing on a road at 23:00 can identify a lamp post, and nobody should be asked to sign up first.

## Constraints

Runs entirely offline from precomputed files — hackathon wifi fails at exactly
the wrong moment. One runtime dependency. No backend, no tile server, no auth.
A road network is the only hard data requirement; every other source narrows the
confidence bands rather than unlocking a feature.

## Deliberately not built

Auth and accounts · a real backend · a tile server · computer vision on street
imagery · live municipal-feed integration (gated; we speak its schema) ·
city-wide coverage · an LLM anywhere.
