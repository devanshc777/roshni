# 24 hours, four people

Two developers (**D1**, **D2**) and two non-developers (**N1**, **N2**). The
allocation matters more than the schedule: this is a data-reasoning problem
wearing a software costume, and if N1 and N2 spend the night on Figma screens you
have thrown away half your team.

## Roles

| | Owns |
|---|---|
| **D1** | Pipeline. OSM graph, segmentation, darkness model, exposure model, triage optimiser. Outputs one GeoJSON. |
| **D2** | Frontend. Three surfaces, MapLibre, sliders, the counterfactual readout. Builds against a fixture from H2. |
| **N1** | Data ground truth. Ward crosswalk, PDF mining of the traffic police crash reports, the field count, the negative controls. |
| **N2** | Narrative. Deck, pitch script, judge Q&A prep, SafetiPin methodology reading, the demo recording. Runs the rehearsals. |

## H0–H1 — Lock everything that is expensive to change

All four, in a room, on paper. No code.

- **Demo bbox.** 3–4 km². Suggested: an ORR stretch between Silk Board and
  Marathahalli, because you have per-lamp KML geometry there, documented crash
  history, and a genuinely heavy night pedestrian load from tech campuses and bus
  stops.
- **The scoring formula**, written out with its inputs named.
- **The one number the demo ends on** — the counterfactual ratio.
- Repo, branch discipline, who merges.

If you leave this hour without a locked bbox you will still be arguing about
coverage at H14.

## H1–H2 — Freeze the seam

**D1 and D2 together.** Write the output GeoJSON schema and a fixture file with
ten fake segments in it. D2 builds against the fixture for the rest of the night.

This is the single highest-return hour in the whole schedule. Do it and the two
halves meet on the first try at H10 instead of the third try at H16.

Meanwhile **N1** starts the ward crosswalk (`risks.md` §1) and **N2** starts the
deck skeleton — the deck is written *before* the results exist, with holes where
numbers go.

## H1–H8 — Data acquisition. Hard stop at H8.

**D1:** run `data/fetch.py`, run the Overpass queries in `data/overpass.md`, and
**verify the two load-bearing numbers in `CLAUDE.md` before anything else.** If
lamp coverage in the bbox is near zero, you find out at H2 and adjust the pitch,
not at H16.

Then: graph, segmentation, ward join, darkness prior, exposure model.

**N1:** crosswalk done and asserted. Then the BTP crash PDFs — you want
pedestrian fatalities with a day/night split and the named blackspots inside or
near the bbox. Highlighter, not parser.

**D2:** map renders, three surfaces stubbed, sliders wired to the fixture.

**H8 is a hard stop on acquisition.** Whatever you have is what you ship with.

## H8–H10 — Go outside and count

**N1 and N2, and one developer if the pipeline is stable.** It is dark, you are
awake, and this is the cheapest differentiator on the table.

Eight segments, stratified — two the model scores high, three medium, three low.
Five-minute pedestrian counts. Photographs, including one of your teammates
counting, timestamped. Three negative controls (`validation.md`).

Come back with a Spearman rank correlation and a photo. Nobody else will have
either.

**D1** meanwhile: triage optimiser and the counterfactual against complaint
order. This is the product; it gets the freshest hours.

## H10–H18 — Integration

Pipeline output meets the real frontend. Routing with the duality. Budget and
weight sliders live. The learning-curve experiment (`cold-start.md`) if there is
room — it is the twenty seconds that kills the cold-start question.

**N2** fills the holes in the deck with real numbers as they land. Nobody writes
the deck at H22.

## H18 — Feature freeze

No exceptions. Not "it's a two-minute change." Not "this one graph."

From here: bug fixes that make the demo path work, and nothing else.

## H18–H22 — Rehearse

**Two full rehearsals, out loud, timed, with someone playing hostile judge.**

Record a screen capture of a clean run as the backup, and rehearse switching to
it once so it does not look like panic if the wifi dies.

Run the judge Q&A list from `pitch.md`. Every one of those questions gets a
rehearsed answer and a named owner.

## H22–H24 — Buffer

It will get used. It always does. If it somehow does not, sleep — an alert team
demos better than a tired team with one more feature.

## The two rules that actually decide this

1. **Acquisition stops at H8.**
2. **Features freeze at H18.**

Every team skips both. Skipping them is the reason good projects lose to worse
ones with smoother demos.
