# Landmines

Ranked by how likely they are to end you. Read before writing code.

## 1. The ward-name join will eat two hours

Your three key files join on **ward name as free text**:

- Grievances (B3): `Ward Name` — e.g. `Jagajeevanram Nagar`, `Kammanahalli`
- Streetlight counts (B2): `Ward_No` + `Ward Name` — 198 wards
- Boundaries (B4): KML, and there are 2015 / 2022 / 2023 vintages

They will not match cleanly. Transliterated Kannada place names have multiple
accepted English spellings, BBMP re-delimited from 198 to 243 wards in 2023, and
Bengaluru's municipal geography has been reorganised again since. Naive
`merge(on="Ward Name")` will silently drop a third of your rows and you will not
notice until the map has holes at hour nineteen.

**Mitigation, in hour one:** use the **2015 / 198-ward** vintage throughout,
because it is the one that matches both the streetlight counts and the grievance
ward names. Then hand-build the crosswalk **for your demo wards only** — five to
eight wards, ten minutes with a spreadsheet, done and verified. Do not attempt a
city-wide fuzzy match. Assign this to a non-developer; it is exactly the kind of
task that is high-value and does not need code.

Write an assertion that fails loudly if the join drops rows. `assert
len(merged) == len(left)` costs one line and saves the evening.

## 2. You have no streetlight inventory

Your dependent variable does not exist as an enumeration. Fully addressed in
`cold-start.md` — the short version is that the atom is the *segment* and the
quantity is *darkness*, not lamp count, and BBMP does not have an inventory
either.

The thing that kills you is not synthetic data. It is a judge **discovering**
synthetic data. Label it in the UI, collect a real seed set of ~30 reports
yourselves, and say it first.

## 3. Light ≠ safe, and your model will contradict itself

Footfall is exposure in the repair queue and protection in the router. Same
variable, opposite sign. Use it with one sign in both and your router will
confidently send a woman down an empty lit industrial road at 01:00, and a sharp
judge will find that in thirty seconds by clicking two points on your own map.

Build the duality deliberately (`architecture.md` §The duality) and put it on a
slide. Best intellectual differentiator you have.

## 4. Routing will eat your day if you pick the wrong tool

**Do not stand up OSRM with a custom Lua profile.** Every weight change means an
`osrm-extract` / `osrm-contract` rebuild. OSMnx + NetworkX is ~30 lines, weights
are hot-swappable at runtime, and you can re-route live while a judge drags a
slider.

## 5. Your scoring weights will look arbitrary

`risk = 0.4·dark + 0.3·footfall + 0.3·crime` with invented coefficients is the
most common civic-hackathon failure and judges are primed for it.

Two fixes, both cheap. **Expose the weights as sliders** — turns "arbitrary" into
"configurable by the municipality." And **derive at least one weight by fitting**
against night pedestrian crash counts rather than choosing it. One fitted
coefficient among three changes the whole character of the answer.

## 6. Rendering falls over

Naive Leaflet polylines choke in the low thousands of segments. Clip to a 3–4 km²
bbox chosen in hour one, or use MapLibre / deck.gl with a GeoJSON source. Do not
discover this at hour twenty.

## 7. The demo needs the network and the network dies

Hackathon wifi fails at exactly the wrong moment. **Precompute everything to
static GeoJSON.** No Overpass call, no Places call, no backend round-trip on the
demo path. Sliders recompute in the browser from data already loaded.

Have a screen recording as a backup, and rehearse *with the recording* at least
once so switching to it is not visibly a panic.

## 8. Report spam

Anyone can report anything, and a public map that can be poisoned is a public map
that gets poisoned. Photo plus GPS plus timestamp, dedupe by spatial clustering,
confidence threshold before a report affects the queue, rate-limit per device.
Cheap to say, cheap to half-build, and judges ask about it every single time.

## 9. Liability

You are telling a woman at 23:00 to walk down a specific road. Have the position
ready and stated in the product, not improvised on stage: **advisory, not a
guarantee**; never route through zero-confidence segments; always display the
shortest route alongside the safer one so the choice is the user's.

## 10. Licensing

Most OpenCity resources carry "No License Provided." Fine for a prototype. Have
the sentence ready: *fair dealing for a non-commercial prototype; production runs
on a data-sharing agreement with BBMP.* OSM is ODbL — share-alike and attribution
if you ship anything public.

## 11. The time budget — the way you most likely actually lose

Fourteen hours on data pipelines, four on UI, and an unrehearsed demo. This is
how good projects lose to worse ones.

**Hard rules:**

- Data acquisition **stops at H8**, whatever state it is in.
- **Feature freeze at H18.** No exceptions, no "it's a two-minute change."
- Two full rehearsals, end to end, out loud, timed.

The freeze is the step every team skips. It is not a nice-to-have; it is the
single highest-correlation predictor of who presents well.

## 12. Known-unmodelled, and worth saying out loud

- **Tree canopy.** In Bengaluru this is a genuinely large effect on how lit a
  street feels, and you have no data for it. Naming it shows you have walked the
  city.
- **Ward lamp count vintage.** Check the file's date before quoting the numbers
  as current.
- **Footpath existence.** A lit road with no walkable footpath is not a safe
  pedestrian route. OSM `sidewalk=*` coverage in Indian cities is thin, so this
  is a real gap in the model rather than a lazy one.
