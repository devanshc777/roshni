# UI generation prompts

For v0, Lovable, Bolt, or ChatGPT/Claude with a canvas. Each prompt is
self-contained — paste it cold, it carries the schema and the references it
needs.

**Rules before you paste anything.**

1. **Generate against the fixture, never the live pipeline.** Give the tool
   `out/segments.fixture.geojson` (ten features, `mvp.md` §The data contract).
   Generated UIs that invent their own data shape are worthless at integration
   time.
2. **One screen per prompt.** Asking for all three at once produces three
   mediocre screens with inconsistent styling.
3. **Generate the shell, hand-write the logic.** These tools are good at layout,
   states and styling; they are bad at spatial code, and they will happily write
   a knapsack that is subtly wrong. Take the components, write the math yourself.
4. **Say "no backend, no auth, no localStorage"** in every prompt or you will get
   a login screen and a Supabase call you did not ask for.

---

## Prompt 0 — the design system (run first, reuse the output)

```
You are designing the visual system for "Roshni", a civic web app about night-time
street lighting in Bengaluru, India. It has three surfaces: a citizen report
screen, a citizen walking-route screen, and a municipal repair-queue dashboard.

Produce a single CSS file of design tokens plus a one-page style reference.

Constraints:
- Dark-first. This is an app about darkness, used at night, on a phone, outdoors.
  Light theme must exist but dark is the default and the one you optimise.
- The core visual variable is CONFIDENCE, not just severity. A street we are
  certain is dark and a street we merely suspect is dark must be immediately
  distinguishable at a glance. Solve this with texture and opacity, not just hue
  — a hatched or dashed treatment for low confidence, solid for high.
- Sequential scale for darkness (light → dark). Do NOT use red/green: this is
  about lighting, and red/green fails for the ~8% of male users with deuteranopia
  on exactly the comparison that matters.
- WCAG AA contrast on all text. Map labels sit over imagery — give them a scrim.
- Indian civic context. Legible, plain, institutional-but-not-drab. It should look
  like something a municipal engineer could open without embarrassment and a
  22-year-old would not be ashamed to have on their phone.

Reference points for tone (describe, do not copy): Citymapper's information
density; FixMyStreet's plainness; Linear's dashboard restraint. Avoid the
"smart city dashboard" cliché of neon-on-black with glowing hexagons.

Output: CSS custom properties for colour, type scale, spacing, radius, and the
confidence texture treatments. Then a short usage note per token.
```

Keep the output. Paste it at the top of every prompt below.

---

## Prompt 1 — the municipal queue (build this first, it is the hero)

```
[paste design tokens from Prompt 0]

Build a single-page React component: a municipal streetlight repair queue for
BBMP, Bengaluru. No backend, no auth, no localStorage. All data comes from a
GeoJSON file loaded from ./segments.geojson — I am attaching a 10-feature sample;
match its property names exactly.

Each feature is a road segment with:
  segID, ward, roadClass, lengthM
  darkness: { alpha, beta, mean, var }      // mean = P(dark) 0-1, var = uncertainty
  exposure: { activity, structural, blended } // 0-1
  repairPriority: number
  evidence: { reports, osmLamps, litTag, wardComplaints2025 }

Layout, in priority order:

1. A HEADLINE NUMBER at the top, large: the counterfactual ratio. Copy:
   "These {n} repairs restore {ratio}× the exposed pedestrian-kilometres that the
   complaint queue's first {n} would have." The ratio is the most important
   element on the page — size it accordingly.

2. A BUDGET SLIDER (1–100 repairs). Moving it must instantly re-rank the list and
   update the headline number. Recompute in the browser; no network call.

3. THREE WEIGHT SLIDERS — darkness, pedestrian exposure, confidence — that
   re-rank live. Label them "municipal priorities", not "model weights".

4. A RANKED WORKLIST, dense rows, most important first. Each row: rank, ward,
   road name, a small darkness bar, a small exposure bar, and a CONFIDENCE
   indicator using the texture treatment from the design tokens. Selecting a row
   highlights the segment on the map.

5. A MAP (MapLibre GL, no API key, use a free raster basemap) beside the list,
   drawing all segments coloured by darkness and textured by confidence. Selected
   segment emphasised.

6. A TOGGLE: "our order" vs "complaint order". Switching it re-draws the list and
   the map so the difference is visible, not just asserted.

Interaction requirements:
- Everything recomputes in <100ms. This is demoed live while someone drags a slider.
- Low-confidence segments must look visibly uncertain, never like a confident estimate.
- Responsive: on narrow screens the map collapses above the list.

Density reference: Linear's issue list, Height's table views. Not a "smart city"
dashboard. No gauges, no donut charts, no glowing borders.
```

---

## Prompt 2 — the citizen report screen

```
[paste design tokens from Prompt 0]

Build a mobile-first React screen for reporting dark streets in Bengaluru. No
backend, no auth, no localStorage — hold reports in component state.

The primary action is ONE TAP: "This stretch is dark." Not "report a broken
streetlight" — a person standing on a road at 11pm cannot identify a specific
fixture, and we do not want them to try. Capture GPS via the browser geolocation
API, a timestamp, and an OPTIONAL photo. Optional means optional: the flow must
complete in under five seconds without one.

The EMPTY STATE is the most important part of this screen. Instead of "no reports
yet", show a ranked list headed "Streets worth checking tonight" — segments where
a report would actually change a repair decision, i.e. high pedestrian exposure
and high uncertainty. Each entry shows the street name, distance from the user,
and a one-line reason ("busy after dark, we have no data here"). Tapping one
starts a report pre-located there.

Also on this screen:
- A map of nearby reports. Reports the user filed themselves are visually distinct.
  Simulated/demo reports must be visually distinct from real ones — a different
  pin treatment plus a legend entry saying so. Do not hide this.
- A "your reports" list with status: Open → Reported fixed → Verified. When a
  report reaches "reported fixed", show a prompt: "We're told this was fixed — is
  it?" with Yes / Not fixed / Can't tell.
- A single line of feedback per report when applicable: "Your report moved 4th
  Cross to #7 in this ward's repair queue." This is the only reason anyone files
  a second report — give it real prominence.

Tone: plain, calm, no gamification, no badges, no points. Someone is using this
while walking alone at night.

Reference: FixMyStreet's flow simplicity; SafetiPin's safety-audit framing. Not
a social feed.
```

---

## Prompt 3 — the citizen route screen

```
[paste design tokens from Prompt 0]

Build a mobile-first React walking-directions screen for Bengaluru at night. No
backend, no auth. Routes are precomputed and loaded from ./routes.json — two
LineString features per query, tagged "safer" and "shortest".

Requirements, in order of importance:

1. ALWAYS SHOW BOTH ROUTES, simultaneously, with an honest comparison strip:
   distance, estimated walking time, and a lit/dark proportion bar for each. The
   user chooses. Never auto-select the safer one and never hide the shortest.

2. Each route is drawn segment-by-segment coloured by darkness, so the user can
   see WHERE it is dark rather than being handed a single score.

3. UNKNOWN IS A FIRST-CLASS STATE. Segments with high uncertainty render in the
   low-confidence texture, and the UI says plainly: "we don't have data for this
   stretch — the safer route avoids it." The safer route must visibly route
   around unknown segments, not through them.

4. A NIGHT BANNER when the local time is after 21:00 and the route crosses
   segments above the darkness threshold. It offers the alternative. It never
   blocks. Copy should be factual, not alarming — no sirens, no red flashing.

5. A "watch this route" toggle. Copy: "We'll tell you if a light on this walk
   goes out, or gets fixed." No account needed; state is in memory for the demo.

6. A permanent, quiet disclaimer near the route choice: this is advisory,
   estimated from partial data, and not a safety guarantee.

Reference: Citymapper's route comparison strip; Google Maps' walking layer. But
darker, calmer, and honest about uncertainty in a way neither of them is.
```

---

## Prompt 4 — the learning-curve panel

```
[paste design tokens from Prompt 0]

Build a small React panel with one chart and three small map thumbnails, for a
pitch demo.

Data (./curve.json): an array of { reports, ratio, targeted } where reports is
the number of citizen reports collected, ratio is how many times better our
repair ordering is than complaint order, and targeted is a boolean marking
whether reports were selected by the system or collected at random.

Chart: reports on x, ratio on y, two lines — "reports we asked for" and "reports
at random". The targeted line should read as clearly dominant. Annotate the point
where the curve flattens.

Beside it, three small static map thumbnails labelled "0 reports", "25 reports",
"400 reports", showing confidence bands narrowing across the three.

One caption under the whole thing: "Useful before it is popular."

Restraint: no animation on load beyond a single 300ms line draw. This is on
screen for twenty seconds during a pitch; it must be readable instantly.
```

---

## After generation — the pass that actually matters

Generated UI is a first draft. Do these four before integrating:

1. **Replace every invented property name** with the real schema. These tools rename fields to what they think is nicer.
2. **Delete the fake data generator** they will have written and point it at the fixture.
3. **Check the confidence treatment survived.** It is the first thing that gets flattened into a plain colour ramp, and it is the thing that makes the product honest.
4. **Rewrite any math they generated.** Knapsack, distance decay, Beta updates — all of it. Layout from the tool, logic from you.

Then run it once with the network off. If it breaks, it was never going to survive the demo.
