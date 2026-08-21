# Deck team — start here

You are building the pitch deck while the two developers make the MVP real.
**Selection is on the deck**, so this is not support work — it is the deliverable.

You should not need to ask a developer anything to finish it. Everything you need
is in this repo and already measured.

---

## 1. Setup — five minutes

```bash
git clone git@github-personal:devanshc777/roshni.git
cd roshni
```

The clone is ~130 MB because the raw data is committed on purpose. Let it finish.

You do **not** need Python, Node, or any tooling. The three files you need are
plain text and JSON:

| File | What it is |
|---|---|
| **`docs/ppt.md`** | **The deck.** Verbatim copy for all 16 slides, palette, type scale, per-slide do/do-not notes. Build from this. |
| `out/stats.json` | Every computed number, machine-readable. Use it to check a figure. |
| `out/segments.fixture.geojson` | 12 real road segments. Feed this to the UI generator so the screenshots carry real street names. |

---

## 2. Read in this order — twenty minutes

1. **`docs/ppt.md` Part 1** — the seven rules and the global do-not list. Read this before you open PowerPoint. Two minutes, and it is what separates this deck from the other forty in the room.
2. **`docs/ppt.md` Part 3** — the sixteen slides. Skim once for shape, then work slide by slide.
3. **`docs/measured-2026-08-22.md`** — where every number came from, and which older claims we killed. Skim §2 and §3 especially; they are the corrections and the dead claims.
4. Optional, only if you want the reasoning behind a slide rather than its content: `docs/deck-outline.md`.

Do not read the whole `docs/` folder. Most of it is developer-facing and will
cost you an hour you do not have.

---

## 3. Build order — do it in this sequence

Working out of order is the main way deck work stalls.

1. **Set up the master first.** 16:9. Background `#0B0E14`, text `#E8EBF0`. Build exactly **two** layouts — hero-number and split — then never build a third. `docs/ppt.md` Part 2 has the palette and type scale.
2. **All sixteen slides, text only.** Paste the blockquoted copy from Part 3 verbatim. No visuals yet. This takes about an hour and it means you always have a complete deck, even if everything after this point runs out of time.
3. **Charts, in the Part 4 checklist order.** Six of them. Build them in Google Sheets or export PNGs — native PowerPoint charts fight dark themes and lose.
4. **Screenshots last**, when the screens exist. Slides 10, 11, 12. Leave sized placeholder frames until then.
5. **QA pass** — `docs/ppt.md` Part 8. Do not skip it. The grep list in step 2 of that pass catches claims we already killed.

If you run out of time, a complete text-only deck with three empty screenshot
frames beats a beautiful half-deck. Step 2 exists for that reason.

---

## 4. Who does what

Two people on the deck. Split like this, not by slide range:

**Person A — words and structure.** Steps 1 and 2 above. Then owns the pitch
script, the timing, and the Q&A rehearsal (`docs/ppt.md` Part 6, one named owner
per question). Runs both rehearsals out loud, timed, with someone playing hostile
judge.

**Person B — visuals.** Steps 3 and 4. Owns the six charts, the architecture
diagram redraw, the IUDX screenshot, and the prototype screenshots once the
screens land. Also owns the hatch treatment — see the takeaways below, it matters
more than it sounds.

**Both, at the end** — the QA pass together. Fresh eyes catch different things.

### The two highest-value non-deck tasks, if either of you has spare capacity

These are worth more than polishing slides, and they close the two rows currently
marked "not yet measured" on slide 13:

1. **Mine the crash PDFs.** `data/raw/btp_road_safety_2023.pdf` and `btp_crashes_2024.pdf`. You want the night pedestrian casualty split and any named blackspots inside or near the demo corridor (HSR / Bellandur / Koramangala / ORR). **Highlighter, not a parser.** This is the only independent validation leg left in the project — nothing else we have is non-circular.
2. **Go outside and count.** Eight segments at 21:30 — two the model scores high, three medium, three low, stratified not convenient. Five-minute pedestrian counts. Ask a developer for the eight street names from `out/segments.geojson`. Bring back a rank correlation and a **photograph of yourselves counting**. Nobody else in the room will have either.

---

## 5. Key takeaways — the eight things to actually understand

You will present this or answer questions about it. Understand these eight and
you can handle anything a judge asks.

**1. The problem is not broken lights. It is the order of the queue.**
BBMP closes **96.4%** of electrical complaints. They execute well. The queue is
sorted by who complained first, and complaining correlates with app-literacy and
car ownership, not with how many people walk that street at 11pm. Never open by
saying the municipality is failing — the data does not say that, and a government
judge will resent it.

**2. The one number the deck lands on is 5.2×.**
Same crew, same 40-repair budget, 5.2× the exposed pedestrian-kilometres
restored. Say it first and say it last. Then immediately volunteer **1.58×** —
the ratio against a steelman BBMP that somehow picks the worst segment in every
ward it visits. Volunteering it wins the "you're just beating random" exchange
instead of losing it. The sentence that goes with it: **the gain is not from
being cleverer inside a ward, it is from visiting the right wards.**

**3. The atom is the road segment, not the lamp.**
Nobody standing on a dark road at 11pm can identify a fixture. Darkness per
200-metre stretch is something you can *estimate*; a lamp inventory is something
you cannot *obtain* — and BBMP does not have one either, their complaint records
carry no coordinates and no pole IDs. Picking the estimable quantity is why the
missing inventory stops being fatal.

**4. Footfall carries opposite signs in the two screens.**
In the repair queue it is **exposure** — more people at risk on a dark street, so
fix it first. In the router it is **protection** — eyes on the street, so prefer
it. Same variable, opposite sign. Most teams use one sign in both and build a
router that confidently sends a woman down an empty, brightly lit industrial road
at 1am. This is our strongest intellectual point and it costs nothing.

**5. Uncertainty is a texture, and it does something.**
Low confidence renders as a 45° hatch, never as a pale colour. And it is not
decoration: the router **refuses** to path through wide-band segments, and the
report screen **sends people to them**. Every honesty claim in the pitch rests on
that hatch being visible in the screenshots. If a generated screen flattens it
into a colour ramp, get it fixed before you screenshot it. This is Person B's
single most important job.

**6. We ran the validation and one layer failed. Say so plainly.**
Spearman ρ = 0.03 between our two exposure estimates. Convergent validation
failed. That is a *better* slide than ρ = 0.6 would have been, because it tells
us the two proxies track two different night populations — people out near night
commerce, and people commuting on bus corridors — and averaging them would have
erased the exact population this problem statement is about. Say "it failed", not
"results were inconclusive." A team that reports a null result and changes its
model because of it is doing science.

**7. The missing data is gated, not absent, and we can point at it.**
93 Indian cities publish streetlight **counts** through MoHUA. Zero publish
coordinates. The pole-level geometry exists on IUDX, for Bengaluru, published by
the local authority, marked Private, behind a Request Resource button — and the
sample record is public. Our lamp record is copied verbatim from theirs, so
"we plug into the municipal feed the day access is granted" is a schema fact, not
a promise. The closing ask is that someone approves the request.

**8. Volunteer three limitations before anyone asks.**
Ward road-km is approximated and makes us conservative in exactly the wards that
complain least. OSM records opening hours for 6.7% of POIs, so we weight by
category instead. Tree canopy is a big effect in Bengaluru and we have zero data
for it. Volunteering a limitation buys more than defending one — thirty seconds
for all three, brisk, then move on. Tone is command of the material, not
confession.

---

## 6. Things that will get you caught

Six specific traps. Each one has bitten a draft of our own docs already.

1. **Do not use the ward numbers Horamavu 3,128 / Jnanabharathi 2,842 / Thanisandra 2,480.** Those are *all-category* complaint counts. The streetlight-only counts are Jnanabharathi 1,345 · Ullalu 1,026 · Hemmigepura 983. Different measurement. Do not mix bases on one slide.
2. **Do not claim complaint timestamps prove people file in the morning.** We tried to check it: the grievance clock is 12-hour with AM/PM stripped, so all 126,974 rows fall in hours 1–12 and 7am is indistinguishable from 7pm. If asked, say exactly that — "the field is 12-hour, we checked, we can't claim it." The ward pattern carries the argument alone.
3. **Do not say the Vasanthanagar audit covers ~800 lamps.** It is 469 rows. Old drafts said 800.
4. **Do not say BBMP has "over half a million" streetlights.** The ward file sums to 421,113.
5. **Do not put a VIIRS nightlights raster on any slide.** It is 500 m per pixel — five to ten city blocks — so it physically cannot tell you a street is dark. Half the teams in this track will have one, and we differentiate by saying so on slide 15. Using one destroys that.
6. **Do not present a screen recording as the primary demo** unless the wifi has actually died. Have the recording ready, and rehearse switching to it once so it does not look like panic.

There is a grep list in `docs/ppt.md` Part 8 step 2 that catches all six in your
own deck text. Run it before you submit.

---

## 7. When to ping a developer

Only for these:

- You need the eight street names for the field count.
- A screenshot's numbers do not match the slide's numbers — that means the UI is on stale data, and it is a real bug worth fixing.
- A judge question needs a number that is not in `out/stats.json`.
- The prototype screens are not ready and you need to know whether to wait or ship placeholder frames.

Everything else — copy, palette, charts, ordering, timing — is yours. Do not wait
for a developer's opinion on a slide. You will not get a better one and it will
cost you twenty minutes.

---

## 8. Definition of done for the deck

- All 16 slides present, text verbatim from `docs/ppt.md` Part 3.
- Six charts built, on the ink background, one amber accent each.
- Slides 10, 11, 12 carry **real** screenshots, or clearly-labelled sized frames if the screens did not land.
- Every slide has its source line, 13pt muted, bottom edge.
- The QA pass in Part 8 completed, including the grep for dead claims.
- Two full rehearsals, out loud, timed, with someone playing hostile judge from Part 6.
- A PDF export on a USB stick, and a screen recording of a clean prototype run as the backup.

The last one is not optional. Hackathon wifi fails at exactly the wrong moment.
