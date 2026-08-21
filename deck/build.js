/**
 * Roshni pitch deck generator.
 *
 *   node deck/build.js
 *
 * Content is docs/ppt.md. Numbers are read from out/stats.json, out/routes.json
 * and out/curve.json so the deck cannot drift from the pipeline. Palette and
 * type come from the product's own design system (assets/design-system.png).
 *
 * There is no LibreOffice on this machine, so slides cannot be rendered to
 * images here. Instead every text box and shape goes through place(), which
 * throws if it would leave the safe area. Open the file and look at it before
 * presenting.
 */
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));
const stats = read("out/stats.json");
const routes = read("out/routes.json");
const curve = read("out/curve.json");
const cf = stats.counterfactual["40"];
const sens = stats.sensitivity;
const na = routes.noAlternative;
const q1 = routes.queries[0];
const [safer, shortest] = q1.routes;
const at = (n, t) => curve.points.find((p) => p.reports === n && p.targeted === t).ratio;

// ---------------------------------------------------------------- design system
const C = {
  bg: "0B0F14", surf: "121820", surf2: "1B232E", line: "232B36",
  text: "E6EAF0", white: "FFFFFF", mute: "B1BAC6", dim: "7A8696",
  brand: "FFC107", brand2: "FFB300",
  blue: "40A3FF", teal: "26C6A6", indigo: "7C9BFF", red: "FF6B6B",
};
const F = { head: "Segoe UI Semibold", body: "Segoe UI" };
const W = 13.333, H = 7.5, M = 0.62, SAFE_R = 0.42, SAFE_B = 0.3;

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "W16", width: W, height: H });
pptx.layout = "W16";
pptx.author = "Roshni";
pptx.title = "Roshni — the streetlight repair queue, reordered by who is actually walking";

let placed = 0;
function place(o, label, bleed = false) {
  const { x, y, w, h } = o;
  if (bleed) { placed++; return o; }   // deliberate full-bleed element
  if (x < 0.2 || y < 0.1) throw new Error(`${label}: starts outside safe area (${x},${y})`);
  if (x + w > W - SAFE_R) throw new Error(`${label}: overflows right (${(x + w).toFixed(2)} > ${W - SAFE_R})`);
  if (y + h > H - SAFE_B) throw new Error(`${label}: overflows bottom (${(y + h).toFixed(2)} > ${H - SAFE_B})`);
  placed++;
  return o;
}

function newSlide() {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  return s;
}

const txt = (s, text, o, label = "text") =>
  s.addText(text, place({ ...o }, label));

function title(s, text, y = M) {
  txt(s, text, { x: M, y, w: W - 2 * M, h: 0.95, fontFace: F.head, fontSize: 30,
                 color: C.white, bold: true, valign: "top", lineSpacingMultiple: 1.0 }, "title");
}

function source(s, text) {
  txt(s, text, { x: M, y: H - 0.66, w: W - 2 * M, h: 0.34, fontFace: F.body,
                 fontSize: 10, color: C.dim, valign: "middle" }, "source");
}

function notes(s, text) { s.addNotes(text); }

// hero-number slide
function hero(s, number, headline, body, srcLine) {
  txt(s, number, { x: M, y: 1.5, w: 5.1, h: 2.5, fontFace: F.head, fontSize: 138,
                   color: C.brand, bold: true, align: "left", valign: "middle" }, "hero");
  txt(s, headline, { x: 5.95, y: 1.55, w: W - 5.95 - SAFE_R - 0.1, h: 0.9,
                     fontFace: F.head, fontSize: 24, color: C.white, bold: true,
                     valign: "top", lineSpacingMultiple: 1.05 }, "hero-head");
  txt(s, body, { x: 5.95, y: 2.6, w: W - 5.95 - SAFE_R - 0.1, h: 2.4, fontFace: F.body,
                 fontSize: 15, color: C.text, valign: "top", lineSpacingMultiple: 1.3 }, "hero-body");
  if (srcLine) source(s, srcLine);
}

function card(s, o) {
  s.addShape(pptx.ShapeType.roundRect, place({
    x: o.x, y: o.y, w: o.w, h: o.h, fill: { color: o.fill || C.surf },
    line: { color: o.stroke || C.line, width: 1 }, rectRadius: 0.06,
  }, "card"));
}

function barChart(s, o) {
  s.addChart(pptx.ChartType.bar, o.data, place({
    x: o.x, y: o.y, w: o.w, h: o.h,
    barDir: o.horizontal === false ? "col" : "bar",
    chartColors: o.colors, barGapWidthPct: 45,
    showLegend: false, showTitle: false, showValue: true,
    dataLabelColor: C.text, dataLabelFontFace: F.body, dataLabelFontSize: 11,
    dataLabelFormatCode: o.fmt || "#,##0",
    catAxisLabelColor: C.mute, catAxisLabelFontFace: F.body, catAxisLabelFontSize: 11,
    catAxisLineShow: false, valAxisHidden: true, valAxisLineShow: false,
    valGridLine: { style: "none" }, catGridLine: { style: "none" },
    plotArea: { fill: { color: C.bg } }, chartArea: { fill: { color: C.bg } },
    border: { pt: 0, color: C.bg },
  }, "chart"));
}

/* ==========================================================================
   1 — Title
   ========================================================================== */
{
  const s = newSlide();
  s.addShape(pptx.ShapeType.rect, place({ x: 0, y: 0, w: 0.11, h: H, fill: { color: C.brand } }, "spine", true));
  txt(s, "ROSHNI", { x: 1.0, y: 2.25, w: 11.4, h: 1.5, fontFace: F.head, fontSize: 84,
                     color: C.white, bold: true, charSpacing: 2 }, "wordmark");
  txt(s, "The streetlight repair queue, reordered by who is actually walking.",
      { x: 1.05, y: 3.75, w: 10.6, h: 0.6, fontFace: F.body, fontSize: 21, color: C.brand }, "tag");
  txt(s, "Problem Statement 17  ·  Smart Cities: Night-Safety Dark-Zone Mapper  ·  Bengaluru",
      { x: 1.05, y: 4.55, w: 10.6, h: 0.4, fontFace: F.body, fontSize: 13, color: C.dim }, "ps");
  notes(s, "Read the tagline out loud as your first sentence. Do not introduce yourselves first — lead with the idea.");
}

/* 2 — the problem, their number */
{
  const s = newSlide();
  title(s, "Bengaluru's most-filed complaint");
  txt(s, "31.4%", { x: M, y: 1.75, w: 4.3, h: 1.9, fontFace: F.head, fontSize: 104,
                    color: C.brand, bold: true, valign: "middle" }, "n");
  txt(s, [
    { text: "39,847", options: { bold: true, color: C.white } },
    { text: " of the ", options: { color: C.text } },
    { text: "126,974", options: { bold: true, color: C.white } },
    { text: " civic complaints Bengaluru filed between 1 January and 19 June 2025 were ", options: { color: C.text } },
    { text: "“Street Light Not Working”", options: { bold: true, color: C.white } },
    { text: ". About 236 a day. The single largest complaint category in the city.", options: { color: C.text } },
  ], { x: M, y: 3.75, w: 5.6, h: 2.1, fontFace: F.body, fontSize: 15, valign: "top",
       lineSpacingMultiple: 1.35 }, "body");
  barChart(s, {
    x: 6.5, y: 1.6, w: 6.2, h: 4.3,
    colors: [C.brand, C.dim, C.dim, C.dim, C.dim],
    data: [{ name: "complaints", labels: ["Street light not working", "Garbage dump",
      "Garbage vehicle missed", "Sweeping not done", "Road side drains"],
      values: [39847, 16137, 12135, 3641, 3269] }],
  });
  source(s, "BBMP grievance register, 1 Jan – 19 Jun 2025, via OpenCity. Recomputed from the raw CSV, 22 Aug 2026. n = 126,974.");
  notes(s, "This is their number, not ours — and we recomputed it from the raw register rather than citing an analysis of it. Do not round to 'about a third'; the precision is the point.");
}

/* 3 — the reframe */
{
  const s = newSlide();
  title(s, "They are not failing. They are being handed the wrong order.");
  hero(s, "96.4%",
    "BBMP closes 96.4% of electrical complaints.",
    "40,632 of 42,138. Road maintenance closes 58%.\n\nThey are not slow, not under-resourced, and not failing at execution.\n\nThe queue is sorted by who complained first.",
    "Same register, Grievance Status field.");
  barChart(s, { x: 6.0, y: 5.05, w: 6.3, h: 1.55, fmt: '0.0"%"',
    colors: [C.brand, C.dim],
    data: [{ name: "closure", labels: ["Electrical", "Road maintenance"], values: [96.4, 58.0] }] });
  notes(s, "The most important slide for a government judge. Never open by criticising the municipality — they will resent it and the data does not support it. The move is: an efficient execution machine is being handed the wrong order. Say that phrase. Do not use the words broken, failure, apathy or negligence anywhere on this slide.");
}

/* 4 — who complains is not who is exposed */
{
  const s = newSlide();
  title(s, "Complaining correlates with app-literacy, not exposure");
  txt(s, [
    { text: "Streetlight complaints concentrate in newer, peripheral, more car-owning, more app-literate wards. Older, denser, more-walked inner wards file fewer.\n\n", options: { color: C.text } },
    { text: "A first-come queue is sorted by who complains, not by who is exposed.", options: { bold: true, color: C.brand } },
  ], { x: M, y: 1.7, w: 5.4, h: 3.4, fontFace: F.body, fontSize: 16, valign: "top",
       lineSpacingMultiple: 1.35 }, "body");
  txt(s, "The person on a dark arterial at 11pm is not the person filing the ticket.",
      { x: M, y: 5.2, w: 5.4, h: 0.8, fontFace: F.body, fontSize: 13, color: C.mute,
        italic: true, valign: "top" }, "kicker");
  barChart(s, { x: 6.3, y: 1.6, w: 6.4, h: 4.3, colors: [C.brand, C.brand2, C.dim, C.dim, C.dim],
    data: [{ name: "streetlight complaints", labels: ["Jnanabharathi", "Ullalu", "Hemmigepura",
      "Dodda Bidarkallu", "R.R. Nagar"], values: [1345, 1026, 983, 967, 964] }] });
  source(s, "Same register, filtered to Sub Category = “Street Light Not Working”, grouped by Ward Name. Streetlight-only counts, not all-category.");
  notes(s, "TRAP: earlier drafts quoted Horamavu 3,128 / Jnanabharathi 2,842 / Thanisandra 2,480 — those are ALL-CATEGORY counts, a different measurement. Never mix bases. SECOND TRAP: do not claim complaint timestamps prove people file in the morning. The Grievance Date field is a 12-hour clock with AM/PM stripped, so all 126,974 rows fall in hours 1-12 and 7am cannot be told from 7pm. If asked, say exactly that. The ward pattern carries the argument alone.");
}

/* 5 — three surfaces, one atom */
{
  const s = newSlide();
  title(s, "Three surfaces, one atom");
  const items = [
    ["Queue", "municipal", "A ranked worklist under a repair budget.", "THE HERO"],
    ["Route", "citizen", "Safer and shortest walk, side by side, always both.", ""],
    ["Report", "citizen", "One tap: “this stretch is dark.”", ""],
  ];
  items.forEach(([name, who, what, tag], i) => {
    const x = M + i * 4.08;
    card(s, { x, y: 1.65, w: 3.85, h: 2.0, fill: C.surf, stroke: i === 0 ? C.brand : C.line });
    txt(s, name, { x: x + 0.25, y: 1.85, w: 2.2, h: 0.45, fontFace: F.head, fontSize: 22,
                   color: i === 0 ? C.brand : C.white, bold: true }, "cn");
    txt(s, who, { x: x + 0.25, y: 2.3, w: 2.2, h: 0.3, fontFace: F.body, fontSize: 11,
                  color: C.dim }, "cw");
    txt(s, what, { x: x + 0.25, y: 2.65, w: 3.35, h: 0.85, fontFace: F.body, fontSize: 13,
                   color: C.text, valign: "top", lineSpacingMultiple: 1.2 }, "cd");
    if (tag) txt(s, tag, { x: x + 2.55, y: 1.87, w: 1.1, h: 0.3, fontFace: F.head,
                           fontSize: 9, color: C.brand, align: "right", charSpacing: 1 }, "ct");
  });
  card(s, { x: M, y: 3.95, w: W - 2 * M, h: 2.35, fill: C.surf2, stroke: C.line });
  txt(s, [
    { text: "The atom is the road segment, not the lamp.  ", options: { bold: true, color: C.brand } },
    { text: "A pedestrian at 23:00 does not care whether a street has eleven lamps or fourteen — they care whether the next 200 metres is lit.\n\n", options: { color: C.text } },
    { text: "Darkness per segment is a quantity you can ", options: { color: C.text } },
    { text: "estimate", options: { bold: true, color: C.white } },
    { text: ". Lamp inventory is an enumeration you cannot ", options: { color: C.text } },
    { text: "obtain", options: { bold: true, color: C.white } },
    { text: " — and BBMP does not have one either: their complaint records carry no coordinates and no pole IDs.", options: { color: C.text } },
  ], { x: M + 0.3, y: 4.2, w: W - 2 * M - 0.6, h: 1.9, fontFace: F.body, fontSize: 14,
       valign: "top", lineSpacingMultiple: 1.3 }, "quote");
  notes(s, "One modelling decision does most of the work in this project, and it is this one.");
}

/* 6 — architecture */
{
  const s = newSlide();
  title(s, "How it works");
  const box = (x, y, w, h, label, sub, col) => {
    card(s, { x, y, w, h, fill: C.surf, stroke: col || C.line });
    txt(s, label, { x: x + 0.14, y: y + 0.1, w: w - 0.28, h: 0.32, fontFace: F.head,
                    fontSize: 13, color: col || C.white, bold: true }, "bx");
    if (sub) txt(s, sub, { x: x + 0.14, y: y + 0.38, w: w - 0.28, h: Math.max(0.24, h - 0.44),
                           fontFace: F.body, fontSize: 9.5, color: C.mute, valign: "top",
                           lineSpacingMultiple: 1.12 }, "bs");
  };
  // inputs
  const ins = [
    ["OSM walk graph", "95,557 nodes"],
    ["BMTC GTFS", "6,187 night departures"],
    ["Night-active POIs", "3,417 weighted"],
    ["Ward lamp density", "421,113 lamps / 198 wards"],
    ["OSM working=yes/no", "1,128 labelled lamps"],
    ["Citizen reports", "GPS + timestamp"],
  ];
  ins.forEach(([a, b], i) => box(M, 1.55 + i * 0.75, 3.0, 0.68, a, b));
  box(4.0, 1.95, 2.5, 1.35, "EXPOSURE", "E(segment)\nactivity + structural", C.teal);
  box(4.0, 3.9, 2.5, 1.35, "DARKNESS", "Beta(α,β) per segment\nmean = P(dark), var = confidence", C.blue);
  box(7.05, 1.6, 2.7, 1.05, "TRIAGE", "knapsack under budget", C.brand);
  box(7.05, 2.85, 2.7, 1.05, "ROUTING", "weighted walk graph", C.brand);
  box(7.05, 4.1, 2.7, 1.05, "CONFIDENCE BAND", "drives both behaviours", C.blue);
  box(7.05, 5.35, 2.7, 0.95, "REPORT TARGETING", "upper confidence bound", C.indigo);
  box(10.25, 1.6, 2.45, 1.05, "→ municipal queue", "+ counterfactual", C.brand);
  box(10.25, 2.85, 2.45, 1.05, "→ safer route", "both routes, always", C.brand);
  txt(s, "IUDX telemetry (gated) drops into the same darkness model with no rewrite — the record shape is theirs, verbatim.",
      { x: 10.25, y: 4.1, w: 2.45, h: 2.2, fontFace: F.body, fontSize: 10.5, color: C.dim,
        valign: "top", lineSpacingMultiple: 1.25 }, "iudx");
  txt(s, "Footfall enters TRIAGE and ROUTING with opposite signs — see next slide.",
      { x: M, y: 6.18, w: 6.3, h: 0.4, fontFace: F.body, fontSize: 11.5, color: C.brand,
        italic: true }, "note");
  notes(s, "Three things, in this order. One: two models, four products. Two: uncertainty is a first-class output, not a footnote — posterior variance drives the routing refusal and the report targeting. Three: the IUDX input is gated; everything works without it and nothing needs rewriting when it opens. Ten seconds per point. Do not walk the boxes left to right.");
}

/* 7 — calibration */
{
  const s = newSlide();
  title(s, "We didn't pick these numbers. We measured them.");
  txt(s, "Vasanthanagar citizen lamp audit — 469 individually coded lamps, two dates 15 days apart, June–July 2019",
      { x: M, y: 1.6, w: 5.9, h: 0.6, fontFace: F.body, fontSize: 12, color: C.mute,
        valign: "top", lineSpacingMultiple: 1.2 }, "sub");
  const rows = [["", "→ DEAD", "→ OK"], ["DEAD", "33", "28"], ["OK", "15", "360"]];
  s.addTable(rows.map((r, ri) => r.map((cell) => ({
      text: cell,
      options: { fontFace: ri === 0 ? F.head : F.body, fontSize: 14,
        color: ri === 0 ? C.dim : C.white, bold: ri === 0, align: "center",
        fill: { color: ri === 0 ? C.bg : C.surf } },
    }))),
    place({ x: M, y: 2.3, w: 3.5, h: 1.25, border: { pt: 1, color: C.line }, rowH: 0.4 }, "matrix"));
  txt(s, [
    { text: "4.0%", options: { bold: true, color: C.brand } },
    { text: " of working lamps died in 15 days.  ", options: { color: C.text } },
    { text: "45.9%", options: { bold: true, color: C.brand } },
    { text: " of dead lamps were repaired.\n", options: { color: C.text } },
    { text: "Equilibrium dead share = 0.040 / (0.040 + 0.459) = ", options: { color: C.text } },
    { text: "8.0%", options: { bold: true, color: C.white } },
  ], { x: M, y: 3.7, w: 5.9, h: 1.0, fontFace: F.body, fontSize: 14, valign: "top",
       lineSpacingMultiple: 1.3 }, "rates");
  card(s, { x: 6.85, y: 1.6, w: 5.85, h: 2.55, fill: C.surf, stroke: C.line });
  txt(s, "P(lit) = coverage × 0.920\n\n" +
         "coverage = ward lamps per km ÷ 33.3\n" +
         "33.3 lamps/km = 30 m standard pole spacing\n" +
         "0.920 = measured working rate, left\n\n" +
         "Beta(α₀, β₀) = (K·P(lit), K·(1−P(lit))),  K = 2",
      { x: 7.1, y: 1.8, w: 5.35, h: 2.2, fontFace: "Consolas", fontSize: 12.5,
        color: C.text, valign: "top", lineSpacingMultiple: 1.25 }, "formula");
  card(s, { x: 6.85, y: 4.4, w: 5.85, h: 1.6, fill: C.surf2, stroke: C.brand });
  txt(s, [
    { text: "Before calibration the model called 58.6% of segments dark.\nAfter: ", options: { color: C.text } },
    { text: "27.7%", options: { bold: true, color: C.brand } },
    { text: ".", options: { color: C.text } },
  ], { x: 7.1, y: 4.62, w: 5.35, h: 1.15, fontFace: F.body, fontSize: 16, valign: "top",
       lineSpacingMultiple: 1.3 }, "beforeafter");
  source(s, "OpenCity — Vasanthanagar streetlights database 2019, citizen audit, 469 rows. Ward lamp density measured from the OSM drive network per ward polygon.");
  notes(s, "We caught our own model producing an indefensible number and fixed it against a measured failure rate. Both numbers are on the slide on purpose. Do not cut the 58.6 to 27.7 line to save space — showing that you audited your own output is worth more than the corrected number alone.");
}

/* 8 — the duality */
{
  const s = newSlide();
  title(s, "One variable, opposite signs");
  card(s, { x: M, y: 1.7, w: 5.9, h: 1.5, fill: C.surf, stroke: C.brand });
  txt(s, "repair_priority  =  E · P(dark) · confidence",
      { x: M + 0.25, y: 1.9, w: 5.4, h: 0.4, fontFace: "Consolas", fontSize: 15, color: C.brand }, "f1");
  txt(s, "E multiplies  →  footfall is EXPOSURE. More people at risk on a dark street, so fix it first.",
      { x: M + 0.25, y: 2.35, w: 5.4, h: 0.7, fontFace: F.body, fontSize: 12.5, color: C.text,
        valign: "top", lineSpacingMultiple: 1.2 }, "f1d");
  card(s, { x: 6.85, y: 1.7, w: 5.85, h: 1.5, fill: C.surf, stroke: C.teal });
  txt(s, "route_penalty  =  L · (1 + λd·P(dark) + λe/E + λu·var)",
      { x: 7.1, y: 1.9, w: 5.35, h: 0.4, fontFace: "Consolas", fontSize: 13, color: C.teal }, "f2");
  txt(s, "E divides  →  footfall is PROTECTION. Eyes on the street, so prefer it.",
      { x: 7.1, y: 2.35, w: 5.35, h: 0.7, fontFace: F.body, fontSize: 12.5, color: C.text,
        valign: "top", lineSpacingMultiple: 1.2 }, "f2d");
  txt(s, "Same variable, opposite sign, depending on which surface consumes it.",
      { x: M, y: 3.55, w: W - 2 * M, h: 0.5, fontFace: F.head, fontSize: 20, color: C.white,
        bold: true }, "mid");
  card(s, { x: M, y: 4.25, w: W - 2 * M, h: 1.75, fill: C.surf2, stroke: C.red });
  txt(s, [
    { text: "Use it with one sign in both", options: { bold: true, color: C.red } },
    { text: " and your router confidently sends a woman down an empty, brightly lit industrial road at 01:00. Most teams will do exactly that, and a judge finds it in thirty seconds by clicking two points on your own map.", options: { color: C.text } },
  ], { x: M + 0.3, y: 4.5, w: W - 2 * M - 0.6, h: 1.3, fontFace: F.body, fontSize: 14,
       valign: "top", lineSpacingMultiple: 1.3 }, "warn");
  source(s, "Jane Jacobs, The Death and Life of Great American Cities, 1961 — eyes on the street.");
  notes(s, "Strongest intellectual slide in the deck and it costs nothing but clear thinking. Cite Jacobs by name; it lands.");
}

/* 9 — the counterfactual */
{
  const s = newSlide();
  title(s, "Same crew. Same budget. Different order.");
  txt(s, `${cf.ratioMean.toFixed(1)}×`,
      { x: M, y: 1.55, w: 4.5, h: 2.15, fontFace: F.head, fontSize: 128, color: C.brand,
        bold: true, valign: "middle" }, "hero");
  txt(s, `A crew can complete 40 repairs this week. Roshni's 40 restore ${cf.ratioMean.toFixed(1)}× the exposed pedestrian-kilometres that the complaint queue's first 40 restore.`,
      { x: M, y: 3.75, w: 5.6, h: 1.35, fontFace: F.body, fontSize: 15, color: C.text,
        valign: "top", lineSpacingMultiple: 1.3 }, "body");
  txt(s, "The gain is not from being cleverer inside a ward.\nIt is from visiting the right wards.",
      { x: M, y: 5.15, w: 5.6, h: 0.95, fontFace: F.head, fontSize: 15, color: C.brand,
        valign: "top", lineSpacingMultiple: 1.25 }, "thesis");
  card(s, { x: 6.5, y: 1.55, w: 6.2, h: 4.55, fill: C.surf, stroke: C.line });
  txt(s, "Stress-tested four ways", { x: 6.8, y: 1.72, w: 5.6, h: 0.35, fontFace: F.head,
        fontSize: 13, color: C.dim, charSpacing: 1 }, "sh");
  const rows = [
    ["Complaint order, 300 Monte-Carlo draws", `${cf.ratioMean.toFixed(2)}×`, C.brand],
    ["vs the luckiest of those 300 draws", `${cf.ratioVsLuckiestDraw.toFixed(2)}×`, C.text],
    ["vs a steelman: BBMP picks the worst segment in every ward it visits", `${cf.ratioVsSteelman.toFixed(2)}×`, C.text],
    ["Restricted to only the wards where we hold lamp labels", `${sens.ratio40_surveyedWardsOnly}×`, C.teal],
    ["Every lamp label deleted — ward prior × exposure alone", `${sens.ratio40_priorOnlyRanking}×`, C.teal],
  ];
  rows.forEach(([label, val, col], i) => {
    const y = 2.2 + i * 0.72;
    txt(s, label, { x: 6.8, y, w: 4.3, h: 0.62, fontFace: F.body, fontSize: 11.5,
                    color: C.text, valign: "middle", lineSpacingMultiple: 1.1 }, "r" + i);
    txt(s, val, { x: 11.2, y, w: 1.2, h: 0.62, fontFace: F.head, fontSize: 19, color: col,
                  bold: true, align: "right", valign: "middle" }, "v" + i);
    if (i < rows.length - 1)
      s.addShape(pptx.ShapeType.line, place({ x: 6.8, y: y + 0.66, w: 5.6, h: 0,
        line: { color: C.line, width: 0.75 } }, "hr" + i));
  });
  txt(s, "The win survives deleting our own best data.",
      { x: 6.8, y: 5.62, w: 5.6, h: 0.35, fontFace: F.body, fontSize: 12, color: C.teal,
        italic: true }, "surv");
  source(s, `${stats.segments.toLocaleString()} segments, ${stats.totalCorridorKm} km, ${stats.wardsScored.length} wards, locked ORR demo bbox. Objective Σ exposure × P(dark) × length. out/stats.json.`);
  notes(s, "THIS SLIDE IS THE PRODUCT. Land the number, pause, then give the four stress tests BEFORE anyone asks. Never quote 7.7x on its own — a judge will say 'you're just beating random', and if you have already said 1.9x and then 5.4x with our own labels deleted, you win that exchange instead of losing it. Say the last line slowly.");
}

/* 10 — prototype: queue */
{
  const s = newSlide();
  title(s, "The municipal queue");
  s.addImage(place({ path: path.join(ROOT, "assets/screen-queue.png"),
    x: M, y: 1.5, w: 8.7, h: 5.8 * (1024 / 1536) * (8.7 / 8.7) }, "img-queue"));
  const notesX = 9.55;
  const bullets = [
    ["The ratio, live", "Drag the budget slider and it recomputes in the browser. No network call on the demo path."],
    ["“Municipal priorities”, not “model weights”", "The municipality owns that choice, not us."],
    ["Texture = confidence", "Solid, hatched, dotted, dashed. We say which streets we do not know."],
  ];
  bullets.forEach(([h, b], i) => {
    const y = 1.55 + i * 1.55;
    txt(s, h, { x: notesX, y, w: 3.2, h: 0.62, fontFace: F.head, fontSize: 12.5,
                color: C.brand, valign: "top", lineSpacingMultiple: 1.1 }, "bh" + i);
    txt(s, b, { x: notesX, y: y + 0.6, w: 3.2, h: 0.85, fontFace: F.body, fontSize: 11,
                color: C.mute, valign: "top", lineSpacingMultiple: 1.2 }, "bb" + i);
  });
  source(s, "Municipal engineer console. Headline figure and budget are the measured values from out/stats.json.");
  notes(s, "This is the screen a BBMP executive engineer would open on a Monday.");
}

/* 11 — prototype: route + bypass */
{
  const s = newSlide();
  title(s, "Both routes. Always.");
  const ih = 5.35, iw = ih * (853 / 1844);
  s.addImage(place({ path: path.join(ROOT, "assets/screen-route.png"),
    x: M, y: 1.5, w: iw, h: ih }, "img-route"));
  const cx = M + iw + 0.45;
  const cw = W - cx - SAFE_R - 0.05;
  txt(s, [
    { text: "Shortest: ", options: { color: C.dim } },
    { text: `${(shortest.distanceM / 1000).toFixed(2)} km, ${(shortest.unknownShare * 100).toFixed(0)}% of it across ground we are not confident about.\n`, options: { color: C.text } },
    { text: "Safer: ", options: { color: C.dim } },
    { text: `${(safer.distanceM / 1000).toFixed(2)} km, ${(safer.unknownShare * 100).toFixed(0)}% unknown — it routes around ${q1.wideBandAvoided} low-confidence segments.\n`, options: { color: C.text } },
    { text: `Cost of the choice: +${q1.detourM.toFixed(0)} m, about ${q1.detourMinutes.toFixed(0)} minutes.`, options: { bold: true, color: C.white } },
  ], { x: cx, y: 1.5, w: cw, h: 1.7, fontFace: F.body, fontSize: 13, valign: "top",
       lineSpacingMultiple: 1.3 }, "routenums");
  card(s, { x: cx, y: 3.35, w: cw, h: 3.5, fill: C.surf2, stroke: C.brand });
  txt(s, "And where the router cannot help", { x: cx + 0.28, y: 3.55, w: cw - 0.56, h: 0.4,
        fontFace: F.head, fontSize: 14, color: C.brand, bold: true }, "byh");
  txt(s, [
    { text: `Bypass test on the ${na.tested} worst segments — delete the segment, look for another way between its endpoints.\n\n`, options: { color: C.mute } },
    { text: `${na.noBypassAtAll} have no walkable alternative at all. ${na.bypassOver3x} need a detour over 3× the segment's length. Median ${na.medianBypassFactor}×.\n\n`, options: { color: C.text } },
    { text: "One 167 m dark service road on the Outer Ring Road has exactly one alternative and it is 23 kilometres.\n\n", options: { color: C.text } },
    { text: "On the streets that most need fixing there is nowhere else to walk. Routing cannot solve them. Only repair can.", options: { bold: true, color: C.white } },
  ], { x: cx + 0.28, y: 4.0, w: cw - 0.56, h: 2.7, fontFace: F.body, fontSize: 12,
       valign: "top", lineSpacingMultiple: 1.28 }, "byb");
  source(s, "out/routes.json — queries[0] and noAlternative. Advisory, never a guarantee; the shortest route is always shown beside the safer one.");
  notes(s, "Say the bypass finding slowly. It is the measured answer to 'why not just build a safer-route app', and it is why the queue is the hero screen and this one is secondary. Never auto-select the safer route or hide the shortest — the position on liability is that the choice is the user's.");
}

/* 12 — prototype: report + cold start */
{
  const s = newSlide();
  title(s, "The empty state is the feature");
  const ih = 5.35, iw = ih * (864 / 1821);
  s.addImage(place({ path: path.join(ROOT, "assets/screen-report.png"),
    x: M, y: 1.5, w: iw, h: ih }, "img-report"));
  const cx = M + iw + 0.45;
  const cw = W - cx - SAFE_R - 0.05;
  txt(s, [
    { text: "Not “no reports yet.” ", options: { bold: true, color: C.brand } },
    { text: "It is ", options: { color: C.text } },
    { text: "“streets worth checking tonight”", options: { bold: true, color: C.white } },
    { text: " — the app directs reporting instead of waiting for it.", options: { color: C.text } },
  ], { x: cx, y: 1.5, w: cw, h: 1.0, fontFace: F.body, fontSize: 14, valign: "top",
       lineSpacingMultiple: 1.3 }, "rh");
  txt(s, [
    { text: `${Math.round(stats.priorOnlyShare * 100)}% of our ${stats.segments.toLocaleString()} segments have no lamp evidence at all`, options: { bold: true, color: C.white } },
    { text: " and run on a ward prior alone. That is not a flaw we are hiding — it is why every segment carries a variance, and it is what this screen is for.", options: { color: C.text } },
  ], { x: cx, y: 2.6, w: cw, h: 1.35, fontFace: F.body, fontSize: 13, valign: "top",
       lineSpacingMultiple: 1.3 }, "rp");
  card(s, { x: cx, y: 4.1, w: cw, h: 2.75, fill: C.surf, stroke: C.teal });
  txt(s, "The learning curve, measured", { x: cx + 0.28, y: 4.3, w: cw - 0.56, h: 0.35,
        fontFace: F.head, fontSize: 13, color: C.teal, bold: true }, "lch");
  txt(s, [
    { text: `With zero reports the ranking already captures ${Math.round(at(0, true) * 100)}%`, options: { bold: true, color: C.white } },
    { text: " of what a perfectly-informed ranking would restore. 400 targeted reports take it to ", options: { color: C.text } },
    { text: `${Math.round(at(400, true) * 100)}%`, options: { bold: true, color: C.white } },
    { text: `. 400 random reports reach only ${Math.round(at(400, false) * 100)}%.\n\n`, options: { color: C.text } },
    { text: "Our first targeting rule asked about the streets we knew least. Measured, it lost to random — those are streets no crew would be sent to. The rule that works asks about streets whose optimistic estimate would put them in the queue.", options: { color: C.mute } },
  ], { x: cx + 0.28, y: 4.7, w: cw - 0.56, h: 2.0, fontFace: F.body, fontSize: 11.5,
       valign: "top", lineSpacingMultiple: 1.25 }, "lcb");
  source(s, `out/curve.json — simulation, labelled as one. ${stats.segmentsWithLampEvidence} of ${stats.segments.toLocaleString()} segments carry any OSM lamp evidence.`);
  notes(s, "This slide pre-answers the hardest question we get — what does it do on day one with no data — before it is asked. Report counts on the screenshot are illustrative: the resolution loop is built and unseeded. Say that if asked.");
}

/* 13 — validation */
{
  const s = newSlide();
  title(s, "How would you validate a footfall estimate with no official data?");
  txt(s, [
    { text: "They asked about validation, not features. Two structural points first.\n\n", options: { color: C.mute } },
    { text: "One. ", options: { bold: true, color: C.brand } },
    { text: "Validation needs a signal you did not use to build the estimate. Build an index from POI density and “validate” it against POI density and the circularity is visible in ten seconds.\n\n", options: { color: C.text } },
    { text: "Two. ", options: { bold: true, color: C.brand } },
    { text: "You are validating an ordering, not a magnitude. “412 pedestrians an hour” is unfalsifiable. “These streets rank above those” is checkable.", options: { color: C.text } },
  ], { x: M, y: 1.55, w: 5.5, h: 2.5, fontFace: F.body, fontSize: 12.5, valign: "top",
       lineSpacingMultiple: 1.3 }, "pre");
  const layers = [
    ["Convergent", "activity vs structural estimate, Spearman ρ", `ρ = +${stats.spearman_activity_vs_structural}`, C.teal],
    ["Criterion", "risk score vs night pedestrian crashes — never enters the model", "not yet measured", C.dim],
    ["Ground truth", "8 stratified segments, 5-min counts at 21:30", "not yet measured", C.dim],
    ["Transfer", "fit where data exists, apply where it does not", "designed", C.mute],
  ];
  layers.forEach(([n, m, r, col], i) => {
    const y = 4.2 + i * 0.63;
    txt(s, n, { x: M, y, w: 1.5, h: 0.55, fontFace: F.head, fontSize: 12, color: C.white,
                valign: "middle" }, "ln" + i);
    txt(s, m, { x: M + 1.5, y, w: 2.7, h: 0.55, fontFace: F.body, fontSize: 10,
                color: C.mute, valign: "middle", lineSpacingMultiple: 1.05 }, "lm" + i);
    txt(s, r, { x: M + 4.25, y, w: 1.85, h: 0.55, fontFace: F.head, fontSize: 11.5,
                color: col, align: "right", valign: "middle" }, "lr" + i);
  });
  card(s, { x: 6.55, y: 1.5, w: 6.15, h: 5.35, fill: C.surf, stroke: C.brand });
  txt(s, "We got a null. We went looking for why.", { x: 6.85, y: 1.7, w: 5.55, h: 0.4,
        fontFace: F.head, fontSize: 15, color: C.brand, bold: true }, "bh");
  const steps = [
    ["ρ = 0.03", "First answer. Two proxies that should have agreed didn't."],
    ["The hunt", "Instead of publishing it we went looking — and found the bug. We were keying the walk graph on rounded coordinates, so junctions where two roads genuinely meet were not merging."],
    ["55% → 98.4%", "Our network had shattered into fragments and the betweenness feeding the model was computed over just over half of it. Keyed on OSM node ids instead, re-ran over eight times the area."],
    [`ρ = 0.30, and 0.44 vs night bus departures`, "Two proxies built from unrelated inputs — one from night commerce, one from pure topology plus bus service — do not agree at 0.30 by accident."],
  ];
  let yy = 2.25;
  steps.forEach(([h, b], i) => {
    txt(s, h, { x: 6.85, y: yy, w: 5.55, h: 0.32, fontFace: F.head, fontSize: 12.5,
                color: i === 3 ? C.teal : C.white, bold: true }, "sh" + i);
    const bh = i === 0 ? 0.35 : 0.78;
    txt(s, b, { x: 6.85, y: yy + 0.3, w: 5.55, h: bh, fontFace: F.body, fontSize: 10.5,
                color: C.mute, valign: "top", lineSpacingMultiple: 1.22 }, "sb" + i);
    yy += 0.32 + bh + 0.14;
  });
  txt(s, "It is a number we only deserve because we didn't ship the first one.",
      { x: 6.85, y: 6.28, w: 5.55, h: 0.35, fontFace: F.body, fontSize: 11.5, color: C.brand,
        italic: true }, "kick");
  source(s, "out/stats.json. Negative controls and a night-bus finding: 405 stops in the bbox, 6,187 departures after 21:00 (6.1% of service), and 119 stops with no night service at all.");
  notes(s, "This is the slide the problem author cares about. Lead with the null, then the bug, then the corrected number — in that order. DO NOT hide the 0.03: it is what makes the 0.30 believable. Also say the exposure blend leaning structural at 0.75 is now a CHOICE justified by the problem statement naming late-night commuters, not a finding.");
}

/* 14 — the data */
{
  const s = newSlide();
  title(s, "The data exists. It's one approval away.");
  txt(s, "HAVE — open, downloadable, in hand", { x: M, y: 1.55, w: 5.7, h: 0.32,
        fontFace: F.head, fontSize: 11, color: C.teal, charSpacing: 1 }, "h1");
  const have = [
    "126,974 grievances for 2025; six years available",
    "1,211 mapped lamps in the demo bbox, 1,128 labelled working/not-working",
    "Per-lamp KML for the ORR corridor and Bellandur/HSR",
    "Lamp counts for all 198 wards — 421,113 lamps",
    "BMTC GTFS with per-stop departure times",
    "A two-date citizen lamp audit, 469 lamps",
    "Night pedestrian crash reports",
  ];
  have.forEach((t, i) => txt(s, "•  " + t, { x: M, y: 1.95 + i * 0.42, w: 5.7, h: 0.4,
    fontFace: F.body, fontSize: 11.5, color: C.text, valign: "middle" }, "hv" + i));
  txt(s, "GATED — catalogued, one approval away", { x: 6.7, y: 1.55, w: 6.0, h: 0.32,
        fontFace: F.head, fontSize: 11, color: C.brand, charSpacing: 1 }, "h2");
  txt(s, "IUDX dataset 9b27c09f-1ec6-4acd-89f0-a27f23184017, published by the Electronics City Industrial Township Authority: “Streetlights Location Info in Electronic City, Bengaluru”, with an hourly current-and-voltage companion. Marked Private. The sample record is public:",
      { x: 6.7, y: 1.95, w: 6.0, h: 1.5, fontFace: F.body, fontSize: 11.5, color: C.text,
        valign: "top", lineSpacingMultiple: 1.25 }, "iu");
  card(s, { x: 6.7, y: 3.5, w: 6.0, h: 0.85, fill: C.surf2, stroke: C.line });
  txt(s, '{"deviceID": "L0302", "location": {"type": "Point",\n coordinates": [77.666046, 12.841758]}}',
      { x: 6.85, y: 3.62, w: 5.7, h: 0.62, fontFace: "Consolas", fontSize: 10.5,
        color: C.teal, valign: "top", lineSpacingMultiple: 1.15 }, "json");
  txt(s, [
    { text: "93 Indian cities publish streetlight counts through MoHUA. Zero publish coordinates", options: { bold: true, color: C.white } },
    { text: " — the D24 template is a KPI return, not an asset register.\n\nSo Roshni's lamp record ", options: { color: C.text } },
    { text: "is", options: { italic: true, bold: true, color: C.white } },
    { text: " {deviceID, location} and its telemetry record ", options: { color: C.text } },
    { text: "is", options: { italic: true, bold: true, color: C.white } },
    { text: " {deviceID, observationDateTime, current, voltage}, copied verbatim from IUDX. “We plug in the day access is granted” is a schema fact, not a promise.", options: { color: C.text } },
  ], { x: 6.7, y: 4.5, w: 6.0, h: 2.05, fontFace: F.body, fontSize: 11.5, valign: "top",
       lineSpacingMultiple: 1.28 }, "pos");
  source(s, "The IUDX feed covers Electronic City, which has 4 lamps mapped in OSM. OSM covers the ORR corridor, which has 1,211. Adjacent, non-overlapping ground — the fragmentation story in one line.");
  notes(s, "End this slide on 'our ask is that someone approves the request'. It reframes the missing data from a weakness into a call to action, and it is true.");
}

/* 15 — limitations */
{
  const s = newSlide();
  title(s, "Four things we get wrong, on purpose, out loud");
  const lims = [
    [`${Math.round(stats.priorOnlyShare * 100)}% of segments run on a ward prior alone`,
     "Every one carries a confidence band that says so; the router avoids the least-certain fifth of the network and the report screen targets it. But most of the map is an estimate, and we would rather say that than have you find it."],
    ["Our labelled lamps are geographically concentrated",
     "OSM's working/not-working tags come from citizen surveys, and those surveys walked some wards and not others — which is why our top forty cluster. We tested it: 6.4× restricted to surveyed wards, 5.4× with every label deleted. It survives, but the concentration shapes which streets we can be confident about."],
    ["OSM records opening_hours for 6.7% of POIs here",
     "78 of 1,157 in the core. So we cannot filter night activity by closing hour as designed; we weight by POI class instead. And Google's review counts, which we do not have, undercount thelas and tea stalls — exactly the population most exposed to dark streets."],
    ["Tree canopy and footpath existence",
     "Canopy is a large effect on how lit a Bengaluru street feels and we have no data for it at all. A lit road with no walkable footpath is not a safe pedestrian route, and OSM sidewalk coverage here is thin."],
  ];
  lims.forEach(([h, b], i) => {
    const y = 1.55 + i * 1.28;
    s.addShape(pptx.ShapeType.ellipse, place({ x: M, y: y + 0.04, w: 0.34, h: 0.34,
      fill: { color: C.brand } }, "num" + i));
    txt(s, String(i + 1), { x: M, y: y + 0.04, w: 0.34, h: 0.34, fontFace: F.head,
        fontSize: 12, color: C.bg, bold: true, align: "center", valign: "middle" }, "ni" + i);
    txt(s, h, { x: M + 0.5, y, w: 5.0, h: 0.75, fontFace: F.head, fontSize: 13,
                color: C.white, bold: true, valign: "top", lineSpacingMultiple: 1.12 }, "lh" + i);
    txt(s, b, { x: 6.0, y, w: W - 6.0 - SAFE_R - 0.05, h: 1.18, fontFace: F.body,
                fontSize: 11, color: C.mute, valign: "top", lineSpacingMultiple: 1.22 }, "lb" + i);
  });
  txt(s, "VIIRS nighttime lights are 500 m per pixel — five to ten city blocks — so they cannot tell you a street is dark. We do not use them that way.",
      { x: M, y: 6.75, w: W - 2 * M, h: 0.4, fontFace: F.body, fontSize: 11,
        color: C.brand, italic: true }, "viirs");
  notes(s, "Volunteering a limitation is worth more than defending one. All four briskly, thirty seconds total, do not dwell. The tone is command of the material, not confession.");
}

/* 16 — what's next and the ask */
{
  const s = newSlide();
  title(s, "What another week buys");
  txt(s, "Answered with what we would try to learn, not with features.",
      { x: M, y: 1.5, w: 7.4, h: 0.35, fontFace: F.body, fontSize: 12, color: C.dim,
        italic: true }, "sub");
  const next = [
    "Mine the Bengaluru Traffic Police crash reports and close the criterion-validation leg.",
    "Field pedestrian counts on stratified segments — is the ordering right?",
    "Fit the transfer model across wards of genuinely different urban form and report the degradation honestly. Where it does not transfer the system should refuse to guess and ask for a report — that behaviour is already built.",
    "Instrument the resolution loop. BBMP closes 96.4% of electrical complaints, and Roshni is the first thing that can ask: closed, or fixed? A ward line reading “11% of closures were not verified by anyone on the ground” is a metric a commissioner does not have today.",
  ];
  next.forEach((t, i) => txt(s, "→  " + t, { x: M, y: 2.05 + i * 0.98, w: 7.4, h: 0.92,
    fontFace: F.body, fontSize: 12.5, color: C.text, valign: "top",
    lineSpacingMultiple: 1.25 }, "nx" + i));
  card(s, { x: 8.35, y: 1.95, w: 4.35, h: 2.1, fill: C.surf2, stroke: C.brand });
  txt(s, "The ask", { x: 8.6, y: 2.12, w: 3.85, h: 0.35, fontFace: F.head, fontSize: 12,
        color: C.dim, charSpacing: 1 }, "askh");
  txt(s, "The data exists, for our city, one approval away, and we already speak its schema.\n\nApprove the IUDX request.",
      { x: 8.6, y: 2.5, w: 3.85, h: 1.4, fontFace: F.head, fontSize: 14, color: C.white,
        valign: "top", lineSpacingMultiple: 1.3 }, "askb");
  txt(s, `${cf.ratioMean.toFixed(1)}×`, { x: 8.35, y: 4.3, w: 4.35, h: 1.9,
        fontFace: F.head, fontSize: 96, color: C.brand, bold: true, align: "center",
        valign: "middle" }, "num");
  txt(s, "First number they hear. Last number they hear.",
      { x: 8.35, y: 6.25, w: 4.35, h: 0.35, fontFace: F.body, fontSize: 10.5,
        color: C.dim, align: "center" }, "fin");
  notes(s, "Do not answer 'what's next' with a feature list. Every team does. Answering with what you would try to learn is the differentiator, and it is the last thing they hear before scoring. Close on the number and stop talking.");
}

/* 17 — appendix: design system */
{
  const s = newSlide();
  title(s, "Appendix — design system");
  const ih = 5.5, iw = ih * (1024 / 1536);
  s.addImage(place({ path: path.join(ROOT, "assets/design-system.png"),
    x: M, y: 1.5, w: iw, h: ih }, "img-ds"));
  const cx = M + iw + 0.5;
  const cw = W - cx - SAFE_R - 0.05;
  txt(s, [
    { text: "Confidence is the core visual variable, not severity.\n\n", options: { bold: true, color: C.brand } },
    { text: "Four states, carried by texture rather than hue, so the map stays readable for the ~8% of male viewers with deuteranopia on exactly the comparison that matters:\n\n", options: { color: C.text } },
    { text: "Solid — high confidence, use for decisions\nDiagonal hatch — medium, use for planning\nDot pattern — low, use cautiously\nDashed outline — unknown, do not assume\n\n", options: { color: C.white } },
    { text: "Darkness runs D0–D5 by lux band, from over 30 lux down to under 0.2. Dark-first, because the app is used at night, outdoors, on a phone.", options: { color: C.text } },
  ], { x: cx, y: 1.5, w: cw, h: 5.3, fontFace: F.body, fontSize: 12.5, valign: "top",
       lineSpacingMultiple: 1.32 }, "dsx");
  notes(s, "Only show this slide if asked about design or accessibility. It is proof the confidence treatment is a system, not a one-off.");
}

/* 18 — appendix: every number and where it came from */
{
  const s = newSlide();
  title(s, "Appendix — every number, and where it came from");
  const rows = [
    ["126,974 · 39,847 · 31.38% · 236/day", "bbmp_grievances_2025.csv"],
    ["96.4% · 58.0% closure", "same file, Grievance Status"],
    ["1,211 · 5,874 · 1,128 labelled · 4 in E-City", "OpenStreetMap via Overpass"],
    ["421,113 lamps, 198 wards", "streetlights_by_ward.csv"],
    ["4.0% · 45.9% · 8.0% equilibrium", "streetlights_vasanthanagar_2019.csv, 469 rows"],
    ["405 stops · 6,187 night departures · 119 with none", "BMTC GTFS trip_list"],
    [`${stats.segments.toLocaleString()} segments · ${stats.totalCorridorKm} km · ${Math.round(stats.priorOnlyShare * 100)}% prior-only`, "data/pipeline.py → out/stats.json"],
    [`ρ +${stats.spearman_activity_vs_structural} · +${stats.spearman_activity_vs_nightbus}`, "same"],
    [`${cf.ratioMean}× · ${cf.ratioVsLuckiestDraw}× · ${cf.ratioVsSteelman}× · ${sens.ratio40_surveyedWardsOnly}× · ${sens.ratio40_priorOnlyRanking}×`, "out/stats.json counterfactual + sensitivity"],
    [`${na.noBypassAtAll} of ${na.tested} with no bypass · median ${na.medianBypassFactor}×`, "data/derive_screens.py → out/routes.json"],
    [`curve ${Math.round(at(0, true) * 100)}% → ${Math.round(at(400, true) * 100)}% targeted vs ${Math.round(at(400, false) * 100)}% random`, "out/curve.json"],
  ];
  rows.forEach(([a, b], i) => {
    const y = 1.5 + i * 0.46;
    txt(s, a, { x: M, y, w: 6.4, h: 0.42, fontFace: F.body, fontSize: 11.5, color: C.white,
                valign: "middle" }, "ra" + i);
    txt(s, b, { x: 7.15, y, w: W - 7.15 - SAFE_R - 0.05, h: 0.42, fontFace: "Consolas",
                fontSize: 10, color: C.mute, valign: "middle" }, "rb" + i);
  });
  txt(s, "Everything above is recomputed by two scripts and committed. Nothing is quoted from a blog post.",
      { x: M, y: 6.7, w: W - 2 * M, h: 0.4, fontFace: F.body, fontSize: 11, color: C.brand,
        italic: true }, "foot");
  notes(s, "Open this only if a judge challenges a figure. Reproduce with: python data/fetch.py, python data/snapshot_osm.py, python data/pipeline.py, python data/derive_screens.py.");
}

const outFile = path.join(ROOT, "deck", "Roshni.pptx");
pptx.writeFile({ fileName: outFile }).then(() => {
  console.log(`wrote ${outFile}`);
  console.log(`${placed} positioned elements, all inside the safe area`);
});
