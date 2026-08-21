# Is this a good problem statement to have picked?

**Yes — but only if you build the repair-prioritisation engine rather than the
map the statement literally describes.**

## The tell

The statement ends with a challenge question about *validation*, not about
features. That is unusual and it is deliberate. A problem author who cared about
the app would have asked "how would you handle offline reporting" or "how would
you scale this to ten cities." They asked how you would validate an estimate with
no ground truth.

That is the author telling you where the marks are. Most teams will skim it, note
that they need a footfall number, and go build red dots on Leaflet. **Answering
that one question well is worth more than the entire frontend.**

## The category is crowded

Be honest about the field you are entering. "Map with red dots plus a report
button" is the single most-built civic hackathon project in existence. Judges at
a smart-cities track have seen it dozens of times. Build the statement literally
and you will be indistinguishable from six other teams, and the winner among
those six will be decided by whose CSS was nicer.

So the question is not "can we build this." Four people in 24 hours can
absolutely build this. The question is whether there is an axis on which you can
be the only team competing. There are three, and they are all cheap:

## Axis 1 — Reframe the output from a map to a procurement decision

Do not show risk. Show the **queue**:

> Your budget covers 40 repairs this month. Here are the 40 that maximise
> exposed pedestrian-kilometres restored. The complaint-log order would have
> restored 38% as much.

This is a knapsack, twenty lines of code, and it converts a visualisation into a
tool that a municipal executive engineer would actually open on a Monday. It also
gives you a **quantified counterfactual against the status quo**, which is the
thing judges write on their scoresheet.

Highest-leverage move available to you and very nearly free. Details in
`architecture.md`.

## Axis 2 — Make validation the centrepiece, not an appendix

They asked. Answer it with numbers, a rank correlation, and a photograph of your
teammates counting pedestrians on a footpath at 21:47.

You would be competing on an axis that nobody else entered, using an evening you
were going to spend awake anyway. `validation.md` has the full architecture.

## Axis 3 — Own the light ≠ safety tension explicitly

A brightly lit empty industrial road at 01:00 is more dangerous than a dimmer
busy market street. Footfall is *exposure* in your repair queue and *protection*
in your router — same variable, opposite sign. Most teams will use it with one
sign in both places and produce a router that confidently sends people down empty
lit roads.

Naming this, and building the duality in deliberately, signals that you thought
about the problem rather than the app. See `architecture.md` §The duality.

## What Bengaluru gives you that most teams will not find

This is the part that changed my read from "risky pick" to "good pick." The data
is unusually good here, and it is not on page one of a search:

- **The complaint log itself is public.** Six years of BBMP grievances with
  `Sub Category = "Street Light Not Working"` as a literal value. You are not
  inventing a baseline to beat — you have the actual queue you are criticising.
- **31.38% of 126,974 complaints in five and a half months of 2025 were broken
  streetlights** — 39,847, about 236 a day. Recomputed 22 Aug 2026. Your opening line.
- **BBMP closes 96.4% of electrical complaints.** So the pitch is not "the
  municipality is failing" — which is lazy and which a government judge will
  resent — it is "the municipality is efficient at execution and is being handed
  the wrong order." That is a much better story and it is true.
- **Complaint volume concentrates in peripheral, newer, app-literate wards.**
  Streetlight-only: Jnanabharathi 1,345, Ullalu 1,026, Hemmigepura 983. (The
  3,128 / 2,842 / 2,480 figures are all-category — different basis.) Complaining is a function of who complains. That is your thesis and
  the city's own data proves it.
- **There is per-lamp point geometry** for Bellandur, HSR and the ORR corridor,
  and a two-date citizen audit of 469 individually coded lamps in Vasanthanagar
  that yields an empirical failure rate: 4.0% of working lamps die per fortnight,
  45.9% of dead ones get fixed, equilibrium dead share 8.0%.

Full manifest with URLs and schemas in `data-sources.md`.

## What will not win

A prettier map. More layers. An LLM chatbot bolted onto the side. "Blockchain for
transparency." Anything whose description is a noun rather than a decision.

## The structural advantage you actually have

**This is a data-reasoning problem wearing a software costume.** Your two
non-developers are not dead weight on this project — they are the field count,
the PDF mining of the traffic police crash reports, the SafetiPin methodology
reading, the ward-name crosswalk, and the deck. That is genuinely where the
marginal points are.

Do not park them on Figma screens. That is the default and it is a waste of half
your team.

## The honest risk

You are betting on a differentiator that lives in a slide and a number rather
than in a visible feature. If your demo fails, or if you run out of time and
present an unrehearsed screen recording, none of the above is visible and you
lose to a worse project with a smoother demo.

Mitigation is not "work faster." It is the **feature freeze at H18** in
`timeline.md`, which every team skips and which is the actual reason good
projects lose.
