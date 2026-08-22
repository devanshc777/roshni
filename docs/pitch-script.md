# Pitch script — the spine

`Roshni.pptx` (spine build) is **12 story slides + 2 appendix**. The old
16-slide build is `Roshni-v2.pptx`; it is more rigorous and less memorable, and
it is kept as a fallback.

## The principle

A deck serves two audiences that want opposite things. The **listener** wants a
chain they can retell to a colleague afterwards. The **examiner** wants evidence
they can poke. Interleave them into one linear sequence and you serve neither —
the listener drowns in mechanism, the examiner cannot find the number.

So: **a spine, and its evidence.** The spine is a short causal chain where every
link stands alone. Under each link sits the evidence that defends it — present,
reachable, never narrated.

The test for what belongs on the spine: **would removing it break the chain?**
If it only makes a link *more defensible*, it is evidence. The Beta posterior
does not break the chain. "Complaints do not measure exposure" does.

Two corollaries:

- **The result arrives the moment the audience first has enough context to want it** — right after you name the mechanism, not after you explain it. It is now slide 6 of 12, not slide 8 of 16.
- **One defensive number, not a battery.** One volunteered stress test reads as rigour; four reads as anxiety. `1.9×` is on the result slide. `4.9× / 6.4× / 5.4×` moved to Appendix A and the speaker notes.

## The chain

> Bengaluru already has the demand signal → the demand signal is not exposure →
> so we changed the unit of measurement → one estimate drives three decisions →
> same budget, 7.7× the restored exposure → here are the three screens →
> here is why you can trust it → approve the request.

## Slide map

| # | Beat | Lands on |
|---|---|---|
| 1 | — | Roshni |
| 2 | Problem | **39,847** streetlight complaints, 31.4% of everything |
| 3 | Problem | **96.4%** closed — the system works, the order is wrong |
| 4 | Insight | *A lamp tells you what failed. A road segment tells you who is exposed.* |
| 5 | Mechanism | One estimate, three decisions — plus the opposite-signs line |
| 6 | **Result** | **7.7×** — and the volunteered **1.9×** floor |
| 7–9 | Product | Queue · Route · Report |
| 10–11 | Proof | The null we found and fixed · measured vs. honest |
| 12 | Ask | Approve the IUDX request → 7.7× |
| 13–14 | Appendix | Every number · the machinery |

Slides 2, 3 and 6 are hero-number slides. Alternate — never run three splits in
a row.

## The one-minute version

Learn this. It is what a judge repeats to another judge afterwards.

> Bengaluru filed nearly forty thousand streetlight complaints in five and a half
> months — thirty-one per cent of every civic complaint in the city. And BBMP
> closes ninety-six per cent of electrical complaints. So the problem was never
> fixing lights. It is deciding which ones matter most.
>
> A complaint tells you someone noticed a broken light. It does not tell you how
> many people are exposed to that darkness. So we changed the unit. A lamp tells
> you what failed; a road segment tells you who is exposed. For every two hundred
> metres of road we estimate darkness, pedestrian exposure, and confidence.
>
> That one estimate drives three decisions: what the city should repair, where a
> walker should go tonight, and where the next report is worth most.
>
> Under the same forty-repair budget, our ranking restores four thousand five
> hundred exposed pedestrian-kilometres against five hundred and eighty-eight
> for the complaint queue. Seven point seven times. And against a steelman that
> picks the worst segment in every ward it visits — which a complaint log with no
> coordinates cannot do — still one point nine.
>
> We do not hide uncertainty. Our first validation came back a null, we distrusted
> it, found a bug in our own graph, fixed it and re-ran.
>
> It works today on open data. The municipal telemetry is one approval away, and
> our record format is copied from theirs.
>
> Same crew. Same budget. Different order.

## Timing

Eight minutes, if that is the slot:

| | |
|---|---|
| 1–3 | 90 s — problem and reframe. Do not linger; slide 3 is the point. |
| 4–5 | 90 s — the insight and the three decisions. Pause after the lamp/segment line. |
| 6 | 60 s — land the number, pause, then volunteer 1.9× before anyone asks. |
| 7–9 | 150 s — demo. Drag the budget slider. Do not narrate the implementation. |
| 10–11 | 90 s — the null, the bug, the fix. Then the limitations, briskly. |
| 12 | 30 s — the ask, then the number, then stop talking. |

The two hardest disciplines: **do not explain the pipeline on slide 5**, and
**stop talking after slide 12**.

## Demoted, not deleted

These are excellent answers to questions and poor story beats. All are in the
appendices or the speaker notes:

Beta(α, β) and the prior construction · the individual evidence weights · the
30-day half-life · the full Vasanthanagar transition matrix · the detailed bypass
statistics · VIIRS resolution · the full data inventory · three of the four
stress tests · the POI opening-hours caveat · the full four-layer validation
architecture.

Two exceptions I kept on the spine deliberately, against the advice to cut them:

- **The bypass finding** — *6 of the 25 worst segments have no walkable alternative at all, median bypass 17.9×* — stays as one line on slide 8. It is the measured answer to "why not just build a routing app?", and without it the answer is a preference rather than a fact.
- **The opposite-signs line** stays as one sentence on slide 5. It is what explains how a single estimate can drive three decisions without contradicting itself, and it is the point most teams get wrong without noticing.

## What did not change

Every figure is still the one computed by the pipeline and verified against
`out/segments.geojson` — 11,029 features, ρ 0.302, ρ_nightbus 0.436, mean P(dark)
0.2764, 690 evidence-bearing segments, 33 wards, 1,180.0 km. The four open
decisions in `docs/deck-rebuild.md` still stand, in particular the queue
screenshot reading *"Top 25 of 10 segments"*.
