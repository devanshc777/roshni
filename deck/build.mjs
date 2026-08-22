import { createRequire } from "module";
const require = createRequire(import.meta.url);
const pptxgen = require("/home/claude/.npm-global/lib/node_modules/pptxgenjs/dist/pptxgen.cjs.js");

/* ── system ─────────────────────────────────────────────── */
const INK="0B0E14", SURF="141A24", HAIR="252C3A", TEXT="E8EBF0",
      MUTED="8A94A6", SOD="F2A93B", DIM="8A6224";
const F="Arial", MONO="Courier New";
const W=13.33, H=7.5, M=0.7;          // margins
const TY=0.52, TH=0.95;               // reserved title band
const CY=1.78;                        // content top — never varies
const SY=6.86;                        // source line

const p=new pptxgen();
p.layout="LAYOUT_WIDE";
p.author="Roshni"; p.title="Roshni";
p.defineSlideMaster({title:"INK", background:{color:INK}});

const S=(notes)=>{const s=p.addSlide({masterName:"INK"}); if(notes) s.addNotes(notes); return s;};
const eyebrow=(s,t,y=TY)=>s.addText(t.toUpperCase(),{x:M,y,w:W-2*M,h:0.3,fontFace:F,fontSize:12,
  bold:true,color:MUTED,charSpacing:2.4,margin:0});
const title=(s,t,o={})=>s.addText(t,{x:M,y:o.y??TY,w:o.w??(W-2*M),h:TH,fontFace:F,fontSize:o.size??31,
  bold:true,color:TEXT,valign:"top",margin:0,lineSpacing:38});
const source=(s,t)=>s.addText(t,{x:M,y:SY,w:W-2*M,h:0.32,fontFace:F,fontSize:11,color:MUTED,margin:0});
const rule=(s,x,y,w)=>s.addShape(p.ShapeType.rect,{x,y,w,h:0.012,fill:{color:HAIR},line:{width:0}});
const vrule=(s,x,y,h)=>s.addShape(p.ShapeType.rect,{x,y,w:0.012,h,fill:{color:HAIR},line:{width:0}});
const body=(s,runs,o={})=>s.addText(runs,{x:o.x??M,y:o.y??CY,w:o.w??5.1,h:o.h??3.4,fontFace:F,
  fontSize:o.size??16,color:TEXT,valign:"top",margin:0,lineSpacing:o.ls??24});
// hero number: number + unit in ONE paragraph, one line, generous width. Never wraps.
const hero=(s,num,unit,o={})=>s.addText(
  [{text:num,options:{fontSize:o.size??148,bold:true,color:SOD}},
   {text:unit,options:{fontSize:Math.round((o.size??148)*0.44),bold:true,color:SOD}}],
  {x:o.x??M,y:o.y??1.45,w:o.w??6.3,h:o.h??2.1,fontFace:F,valign:"bottom",align:"left",margin:0,wrap:false});
const panel=(s,x,y,w,h)=>s.addShape(p.ShapeType.rect,{x,y,w,h,fill:{color:SURF},line:{width:0}});
const code=(s,t,x,y,w,h,sz=12)=>s.addText(t,{x,y,w,h,fontFace:MONO,fontSize:sz,color:TEXT,
  valign:"top",margin:0,lineSpacing:Math.round(sz*1.42),fill:{color:SURF}});


/* ═══════════════════════════════════════════════════════════
   SPINE:  Problem → Insight → Mechanism → Result → Product → Proof → Ask
   12 story slides + 2 appendix. Evidence sits under the spine,
   reachable in the appendix and the speaker notes, never narrated.
   ═══════════════════════════════════════════════════════════ */

/* ── 1 · title ──────────────────────────────────────────── */
{const s=S("Read the subtitle out loud as your first sentence. Do not introduce yourselves first — lead with the idea.");
 s.addText("ROSHNI",{x:M,y:2.85,w:9,h:1.5,fontFace:F,fontSize:88,bold:true,color:TEXT,charSpacing:6,margin:0});
 s.addText("The streetlight repair queue, reordered by who is actually walking.",
   {x:M,y:4.36,w:9.6,h:0.5,fontFace:F,fontSize:22,color:SOD,margin:0});
 s.addText("Problem Statement 17   ·   Smart Cities: Night-Safety Dark-Zone Mapper   ·   Bengaluru",
   {x:M,y:SY,w:10,h:0.35,fontFace:F,fontSize:13,color:MUTED,margin:0});}

/* ── 2 · PROBLEM: the demand signal already exists ──────── */
{const s=S("Do not explain the dataset yet. The only message on this slide is: there is plenty of demand signal. Their number, not ours, and we recomputed it from the raw register rather than citing an analysis of it. Do not round to 'about a third' — the precision is the point.");
 eyebrow(s,"The city already knows where lights are reported broken");
 hero(s,"39,847","",{y:1.0,h:2.2,w:7.4,size:126});
 body(s,[{text:"streetlight complaints in five and a half months of 2025 — "},
   {text:"31.4% of every civic complaint Bengaluru filed",options:{bold:true,color:SOD}},
   {text:", and the largest single category in the city. Garbage is second, at 16,137.\n\n"},
   {text:"There is no shortage of demand signal.",options:{bold:true}}],
   {y:3.34,w:5.3,h:2.9,size:16.5});
 s.addImage({path:"assets/chart-categories.png",x:6.53,y:2.16,w:6.1,h:3.61});
 source(s,"BBMP grievance register, 1 Jan – 19 Jun 2025, via OpenCity. Recomputed from the raw CSV. n = 126,974.");}

/* ── 3 · PROBLEM: the signal is the wrong one ───────────── */
{const s=S("This is the central problem statement and the most important slide for a government judge. Never open by criticising the municipality — they will resent it and the data does not support it. Say the phrase: the repair system works, the order is wrong. Trap: these are streetlight-only ward counts, not all-category. Do not mix bases.");
 title(s,"The repair system works. The order is wrong.",{size:33});
 s.addText([{text:"96.4%",options:{fontSize:52,bold:true,color:SOD}},
            {text:"  of electrical complaints closed",options:{fontSize:17,color:TEXT}}],
   {x:M,y:CY,w:6.1,h:0.85,fontFace:F,valign:"bottom",margin:0,wrap:false});
 s.addImage({path:"assets/chart-closure.png",x:M-0.02,y:2.86,w:5.5,h:2.16});
 body(s,[{text:"40,632 of 42,138. Road maintenance closes 58%. They are not slow and not under-resourced.\n\n"},
   {text:"A complaint tells you someone noticed. It does not tell you how many people are exposed.",options:{bold:true,color:SOD}}],
   {y:5.28,w:5.4,h:1.4,size:15.5,ls:22});
 vrule(s,6.5,CY,4.34);
 s.addText("Complaining tracks who complains",
   {x:6.88,y:CY,w:5.75,h:0.36,fontFace:F,fontSize:16,bold:true,color:TEXT,margin:0});
 s.addImage({path:"assets/chart-wards.png",x:6.84,y:2.6,w:5.5,h:3.0});
 s.addText("Newer, peripheral, more car-owning wards file most. Older, denser, more-walked wards file fewer — not because their lights work.",
   {x:6.88,y:5.62,w:5.75,h:0.9,fontFace:F,fontSize:14,color:MUTED,margin:0,lineSpacing:20});
 source(s,"Same register. Left: Grievance Status field. Right: Sub Category = “Street Light Not Working”, grouped by Ward Name, 198 wards.");}

/* ── 4 · INSIGHT: change the unit of measurement ────────── */
{const s=S("This is the conceptual leap and the whole project rests on it. Say the two lines and pause. Then: darkness per segment is a quantity you can estimate; lamp inventory is an enumeration you cannot obtain — and BBMP does not have one either, their complaint records carry no coordinates and no pole IDs. Do not explain the inputs here.");
 eyebrow(s,"So we changed the unit of measurement");
 s.addText("A lamp tells you what failed.",
   {x:M,y:1.72,w:11.93,h:0.74,fontFace:F,fontSize:38,bold:true,color:MUTED,margin:0,wrap:false});
 s.addText("A road segment tells you who is exposed.",
   {x:M,y:2.48,w:11.93,h:0.74,fontFace:F,fontSize:38,bold:true,color:TEXT,margin:0,wrap:false});
 rule(s,M,3.5,W-2*M);
 s.addText([{text:"For every 200-metre stretch of road, Roshni estimates "},
   {text:"darkness × pedestrian exposure × confidence",options:{bold:true,color:SOD}},
   {text:"."}],
   {x:M,y:3.78,w:11.9,h:0.5,fontFace:F,fontSize:22,color:TEXT,margin:0});
 body(s,[{text:"Darkness per segment is a quantity you can "},{text:"estimate",options:{bold:true}},
   {text:". Lamp inventory is an enumeration you cannot "},{text:"obtain",options:{bold:true}},
   {text:" — and BBMP does not have one either. Their complaint records carry no coordinates and no pole IDs, so on day zero we are at parity with the municipality and ahead of it the moment a report carries a GPS fix."}],
   {y:4.66,w:11.9,h:1.7,size:17,ls:25});
 source(s,"11,029 segments · 1,180 km · 33 wards, across the locked ORR corridor.");}

/* ── 5 · MECHANISM: one model, three decisions ──────────── */
{const s=S("Almost no technical text here. Three decisions, one estimate. The duality line at the bottom is the strongest intellectual point in the deck and it costs one sentence: use footfall with the same sign in both and your router confidently sends a woman down an empty, brightly lit industrial road at one in the morning. Jane Jacobs, eyes on the street. Full architecture is in Appendix B.");
 title(s,"One estimate. Three decisions.");
 const dec=[["What should the city repair?","THIS WEEK","A ranked worklist under a repair budget, scored by who is exposed rather than who complained.","Municipal queue",true],
            ["Where should I walk?","TONIGHT","Safer and shortest route side by side, always both. It refuses to path through ground we have no data for.","Citizen route",false],
            ["Where is a report worth most?","NEXT","The streets where a single answer would change a repair decision — high exposure, low confidence.","Citizen report",false]];
 dec.forEach(([q,when,txt,who,hero_],i)=>{const x=M+i*4.08;
   rule(s,x,CY,3.77);
   s.addText(when,{x,y:CY+0.18,w:3.77,h:0.26,fontFace:F,fontSize:10.5,bold:true,
     color:hero_?SOD:MUTED,charSpacing:2,margin:0});
   s.addText(q,{x,y:CY+0.5,w:3.72,h:0.8,fontFace:F,fontSize:18,bold:true,
     color:hero_?SOD:TEXT,margin:0,lineSpacing:26});
   s.addText(txt,{x,y:CY+1.36,w:3.72,h:1.2,fontFace:F,fontSize:13.5,color:"B9C0CC",margin:0,lineSpacing:19});
   s.addText(who+(hero_?"   ·   THE HERO":""),{x,y:CY+2.5,w:3.72,h:0.3,fontFace:F,fontSize:11.5,
     bold:true,color:hero_?SOD:MUTED,charSpacing:1.2,margin:0});});
 rule(s,M,4.82,W-2*M);
 s.addText([{text:"One variable, opposite signs.",options:{bold:true,color:TEXT}},
   {text:"   Footfall is exposure in the repair queue — more people at risk on a dark street, so fix it first. It is protection in the router — eyes on the street, so prefer it. Use one sign in both and your router calls an empty, brightly lit industrial road safe at one in the morning.",
    options:{color:"B9C0CC"}}],
   {x:M,y:5.1,w:11.9,h:1.1,fontFace:F,fontSize:15.5,color:TEXT,margin:0,lineSpacing:22});
 source(s,"Jane Jacobs, The Death and Life of Great American Cities, 1961. Full pipeline in Appendix B.");}

/* ── 6 · RESULT ─────────────────────────────────────────── */
{const s=S("The payoff. Land on the number, pause, then volunteer the 1.9x floor BEFORE anyone asks for it. The last line is the thesis of the whole project — say it slowly. Do not recite all four stress tests unless challenged; they are in Appendix A. If pushed: 4.9x against the luckiest of 300 draws, 6.4x restricted to wards where we hold lamp labels, 5.4x with every lamp label deleted. The grievance file has no coordinates, so the baseline is Monte-Carlo'd over 300 draws — wards in complaint order, target inside the ward unknown.");
 eyebrow(s,"Same crew. Same budget. Different order.");
 hero(s,"7.7","×",{y:1.0,h:2.2,w:6.0});
 body(s,[{text:"Under a 40-repair budget, Roshni's forty restore "},
   {text:"4,544 exposed pedestrian-kilometres against 588",options:{bold:true}},
   {text:" for the complaint queue's first forty.\n\n"},
   {text:"The gain is not from being cleverer inside a ward.\nIt is from visiting the right wards.",options:{bold:true,color:SOD}}],
   {y:3.36,w:5.4,h:2.3,size:16.5});
 s.addImage({path:"assets/chart-counterfactual.png",x:6.5,y:1.5,w:6.13,h:2.25});
 rule(s,6.5,4.06,6.13);
 s.addText("And the floor, volunteered",
   {x:6.5,y:4.24,w:6.13,h:0.3,fontFace:F,fontSize:12,bold:true,color:MUTED,charSpacing:1.6,margin:0});
 s.addText([{text:"1.9×",options:{fontSize:34,bold:true,color:SOD}},
   {text:"   against a steelman BBMP that somehow picks the single worst segment in every ward it visits — which a coordinate-free complaint log cannot do.",options:{fontSize:15,color:TEXT}}],
   {x:6.5,y:4.62,w:6.13,h:1.2,fontFace:F,margin:0,lineSpacing:22,valign:"top"});
 s.addText("Three further stress tests — 4.9× against the luckiest of 300 draws, 6.4× restricted to wards where we hold lamp labels, 5.4× with every lamp label deleted — are in Appendix A.",
   {x:6.5,y:5.86,w:6.13,h:0.8,fontFace:F,fontSize:12.5,color:MUTED,margin:0,lineSpacing:18});
 source(s,"11,029 segments · 1,180 km · 33 wards · locked ORR demo bbox. Objective Σ exposure × P(dark) × length. 300 draws. out/stats.json.");}

/* ── 7 · PRODUCT: the queue ─────────────────────────────── */
{const s=S("This is the screen a BBMP executive engineer would open on a Monday. Demonstrate, do not explain. Drag the budget slider so they see the ratio move.");
 title(s,"What the city sees",{size:28});
 s.addImage({path:"assets/screen-queue.png",x:M,y:1.74,w:11.93,h:4.33});
 s.addText([{text:"The ratio, live",options:{bold:true,color:SOD}},
   {text:"  — the budget slider recomputes in the browser.    "},
   {text:"Municipal priorities",options:{bold:true}},
   {text:"  — the municipality’s to set, not ours.    "},
   {text:"Confidence is marked",options:{bold:true}},
   {text:"  — low-confidence rows are hatched, not hidden."}],
   {x:M,y:6.32,w:W-2*M,h:0.3,fontFace:F,fontSize:12,color:TEXT,margin:0});
 s.addText("Prototype, running client-side on the fixture export. No network call on the demo path.",
   {x:M,y:SY,w:W-2*M,h:0.3,fontFace:F,fontSize:11,color:MUTED,margin:0});}

/* ── 8 · PRODUCT: the route ─────────────────────────────── */
{const s=S("Six minutes to walk on ground we actually have data for. Then say the bypass finding slowly — it is the measured answer to 'why not just build a safer-route app', and it is why the queue is the hero and this screen is secondary. Full bypass statistics in Appendix B. Real geography if you want it: Haralur Road in Bellandur carries the widest confidence band in the corridor — no mapped lamps, almost no night bus service, zero streetlight complaints in the ward file. The router will not send you down it. The report screen sends you to it.");
 title(s,"What a walker sees",{size:28});
 s.addImage({path:"assets/screen-route.png",x:M,y:1.5,w:4.22,h:5.12});
 vrule(s,5.22,1.5,5.12);
 body(s,[{text:"Shortest:  1,575 m, and 63% of it crosses ground we are not confident about.\n"},
   {text:"Safer:  2,021 m, 7% unknown — it routes around 18 low-confidence segments.\n\n"},
   {text:"Six minutes to walk on ground we actually have data for.",options:{bold:true,color:SOD}}],
   {x:5.58,y:1.56,w:3.4,h:2.4,size:14,ls:20});
 s.addText("The shortest route is always shown beside the safer one. We do not auto-select and we do not hide it — the choice is the walker’s, and we say plainly which stretches we have no data for.",
   {x:5.58,y:4.24,w:3.4,h:1.5,fontFace:F,fontSize:12.5,color:MUTED,margin:0,lineSpacing:19});
 vrule(s,9.26,1.5,5.12);
 s.addText("But routing cannot fix the worst streets",
   {x:9.64,y:1.56,w:2.99,h:0.9,fontFace:F,fontSize:19,bold:true,color:TEXT,margin:0,lineSpacing:26});
 s.addText("Delete each of the 25 worst segments and look for another way between its endpoints:",
   {x:9.64,y:2.56,w:2.99,h:0.9,fontFace:F,fontSize:13,color:MUTED,margin:0,lineSpacing:19});
 [["6","have no walkable alternative at all"],
  ["19","have a bypass over 3× the segment’s length"],
  ["17.9×","median bypass · worst 206.9×"]].forEach(([n,t],i)=>{const y=3.62+i*0.8;
   s.addText([{text:n,options:{fontSize:21,bold:true,color:SOD}},
     {text:"   "+t,options:{fontSize:12,color:TEXT}}],
     {x:9.64,y,w:2.99,h:0.72,fontFace:F,margin:0,lineSpacing:17,valign:"top"});});
 s.addText("On the streets that most need fixing there is nowhere else to walk. Only repair solves them.",
   {x:9.64,y:5.94,w:2.99,h:0.9,fontFace:F,fontSize:13,bold:true,color:TEXT,margin:0,lineSpacing:18});
 source(s,"out/routes.json, query 1. Bypass test over the 25 highest-priority segments in the corridor.");}

/* ── 9 · PRODUCT: the report ────────────────────────────── */
{const s=S("This pre-answers the hardest question we get — what does it do on day one with no data — before it is asked. If there is time: our first targeting rule asked about the streets we knew least, and measured, it lost to random, because those are streets no crew would ever be sent to. The rule that works asks about streets whose optimistic darkness estimate would put them in the repair queue if it turned out true.");
 title(s,"What a reporter sees",{size:28});
 s.addImage({path:"assets/screen-report.png",x:M,y:1.5,w:4.32,h:5.12});
 vrule(s,5.3,1.5,5.12);
 body(s,[{text:"The empty state is not “no reports yet.” It is "},
   {text:"“streets worth checking tonight”",options:{bold:true,color:SOD}},
   {text:" — so the app directs reporting instead of waiting for it.\n\n"},
   {text:"93.7% of our 11,029 segments have no lamp evidence at all",options:{bold:true}},
   {text:" and run on the ward prior alone. That is not a flaw we are hiding — it is why every segment carries a variance, and it is what this screen is for."}],
   {x:5.66,y:1.56,w:3.2,h:3.4,size:13.5,ls:20});
 s.addText("A report is worth most exactly where we are least sure and most people walk.",
   {x:5.66,y:4.86,w:3.2,h:1.2,fontFace:F,fontSize:12.5,color:MUTED,margin:0,lineSpacing:18});
 vrule(s,9.14,1.5,5.12);
 s.addImage({path:"assets/chart-curve.png",x:9.4,y:1.56,w:3.23,h:1.92});
 s.addText([{text:"With zero reports the prior-only ranking already captures "},
   {text:"56%",options:{bold:true,color:SOD}},
   {text:" of what a perfectly-informed ranking would restore. 400 targeted reports takes it to "},
   {text:"76%",options:{bold:true,color:SOD}},
   {text:"; 400 random reports reach only 63%."}],
   {x:9.4,y:3.68,w:3.23,h:2.0,fontFace:F,fontSize:13,color:TEXT,margin:0,lineSpacing:19});
 s.addText("Simulation, not a field trial — labelled as one in out/curve.json.",
   {x:9.4,y:5.86,w:3.23,h:0.6,fontFace:F,fontSize:11.5,color:MUTED,italic:true,margin:0,lineSpacing:16});
 source(s,"690 of 11,029 segments carry any OSM lamp evidence. out/stats.json · out/curve.json.");}

/* ── 10 · PROOF: we found our own bug ───────────────────── */
{const s=S("The challenge question is about validation, not features — that is the author telling you where the marks are. Lead with the null, then the bug, then the corrected number, in that order. Do NOT hide the 0.03: it is what makes the 0.30 believable. One honesty note if asked about weights: the exposure blend leans structural at 0.75. On the broken numbers that looked like a finding. On the corrected numbers it is a choice, made because the problem statement names late-night commuters. Call it a choice.");
 title(s,"We got a null, distrusted it, and found our own bug",{size:29});
 s.addText([{text:"Validation needs a signal you did not use to build the estimate. "},
   {text:"And you are validating an ordering, not a magnitude — “412 pedestrians an hour” is unfalsifiable; “these streets rank above those” is checkable.",options:{color:MUTED}}],
   {x:M,y:1.62,w:W-2*M,h:0.6,fontFace:F,fontSize:14.5,color:TEXT,margin:0,lineSpacing:20});
 s.addImage({path:"assets/chart-scatter.png",x:M-0.04,y:2.34,w:6.5,h:4.28});
 vrule(s,7.14,2.34,4.28);
 s.addText([{text:"The first answer was ρ = 0.03. Two proxies that should have agreed didn’t. So we went looking, and found we were keying the walk graph on "},
   {text:"rounded coordinates",options:{bold:true,color:TEXT}},
   {text:" — junctions where two roads genuinely meet weren’t merging. The network had shattered, and the betweenness we were feeding the model was computed over 55% of the city.\n\n"},
   {text:"Keyed it on OSM node ids and re-ran over eight times the area. 98.4% now connects, and two proxies built from completely unrelated inputs — night commerce, and pure network topology plus bus service — converge at ρ = 0.30.",options:{color:TEXT}}],
   {x:7.52,y:2.34,w:5.11,h:2.9,fontFace:F,fontSize:13.5,color:MUTED,margin:0,lineSpacing:19});
 rule(s,7.52,5.36,5.11);
 [["Convergent","ρ +0.30, +0.44 vs night bus",true],
  ["Criterion — night pedestrian crashes","not yet measured",false],
  ["Ground truth — stratified field counts","not yet measured",false]].forEach(([a,b,ok],i)=>{
   const y=5.5+i*0.42;
   s.addText(a,{x:7.52,y,w:3.3,h:0.3,fontFace:F,fontSize:12,color:ok?TEXT:MUTED,margin:0});
   s.addText(b,{x:10.85,y,w:1.78,h:0.3,fontFace:F,fontSize:12,bold:ok,color:ok?SOD:MUTED,align:"right",margin:0});});
 source(s,"out/stats.json · data/pipeline.py · BMTC GTFS via Vonter/bmtc-gtfs. Scatter is all 11,029 segments.");}

/* ── 11 · PROOF: measured, and honest about what it isn't ─ */
{const s=S("Volunteering a limitation is worth more than defending one. Left is what we measured rather than chose; right is what we get wrong. Say the right-hand column briskly — thirty seconds — and do not dwell. Tone is command of the material, not confession. Full evidence weights and the transition matrix are in Appendix B.");
 title(s,"Measured, not chosen — and honest about the rest");
 s.addText("WHAT WE MEASURED",{x:M,y:CY,w:5.6,h:0.28,fontFace:F,fontSize:11,bold:true,color:SOD,charSpacing:2,margin:0});
 rule(s,M,CY+0.32,5.6);
 [["The prior is calibrated, not picked","A citizen audit coded 469 Vasanthanagar lamps on two dates 15 days apart: 45.9% of dead lamps were repaired, 4.0% of working lamps died. That is a measured equilibrium of 8.0% dead — so the prior comes from a failure rate we can point at."],
  ["Two disjoint proxies agree","ρ = +0.30 between night commerce and pure network topology, and +0.44 against night bus departures. Unrelated proxies do not agree at 0.30 by accident."],
  ["The win survives deleting our own best data","Restricted to the wards where we hold lamp labels: 6.4×. With every lamp label deleted and the ranking built on ward prior and exposure alone: 5.4×."]]
 .forEach(([h,t],i)=>{const y=CY+0.52+i*1.42;
   s.addText(h,{x:M,y,w:5.6,h:0.3,fontFace:F,fontSize:14.5,bold:true,color:TEXT,margin:0});
   s.addText(t,{x:M,y:y+0.32,w:5.6,h:1.0,fontFace:F,fontSize:12.5,color:"B9C0CC",margin:0,lineSpacing:17});});
 vrule(s,6.5,CY,4.34);
 s.addText("WHAT WE GET WRONG",{x:7.03,y:CY,w:5.6,h:0.28,fontFace:F,fontSize:11,bold:true,color:MUTED,charSpacing:2,margin:0});
 rule(s,7.03,CY+0.32,5.6);
 [["93.7% of segments run on a ward prior alone","690 of 11,029 carry any lamp evidence. Every other one carries a confidence band that says so — the router avoids the least-certain fifth, the report screen targets it. But most of the map is an estimate."],
  ["Our labelled lamps are geographically concentrated","OSM’s working tags come from citizen surveys, and those surveys walked some wards and not others. 657 broken to 471 working is a property of who went mapping, not Bengaluru’s outage rate."],
  ["Two inputs we simply do not have","OSM records opening_hours for 6.7% of POIs here, so we weight night activity by POI class instead. And tree canopy is a large effect on how lit a Bengaluru street feels, with no data at all."]]
 .forEach(([h,t],i)=>{const y=CY+0.52+i*1.42;
   s.addText(h,{x:7.03,y,w:5.6,h:0.3,fontFace:F,fontSize:14.5,bold:true,color:TEXT,margin:0});
   s.addText(t,{x:7.03,y:y+0.32,w:5.6,h:1.0,fontFace:F,fontSize:12.5,color:"B9C0CC",margin:0,lineSpacing:17});});
 source(s,"Vasanthanagar citizen audit, 469 lamps, OpenCity. Everything else out/stats.json. Evidence weights and the transition matrix in Appendix B.");}

/* ── 12 · ASK ───────────────────────────────────────────── */
{const s=S("End on the ask, then the number, then stop talking. It reframes the missing data from a weakness into a call to action, and it is true. If asked what another week buys, answer with what you would try to LEARN, not with features: mine the crash PDFs to close the criterion leg, run stratified field counts, fit the transfer model across different urban form, and instrument the resolution loop so the system can ask 'closed, or fixed?'");
 title(s,"The data exists. It’s one approval away.");
 s.addText("93 Indian cities publish streetlight counts through MoHUA’s Smart Cities portal. Zero publish coordinates — the D24 template is a KPI return, not an asset register.",
   {x:M,y:CY,w:7.4,h:0.7,fontFace:F,fontSize:15,color:"B9C0CC",margin:0,lineSpacing:21});
 s.addText([{text:"The pole-level geometry is on IUDX, for our city, published by the Electronics City Industrial Township Authority, "},
   {text:"marked Private",options:{bold:true,color:TEXT}},
   {text:" — behind a Request Resource button. The sample record is public:"}],
   {x:M,y:2.62,w:7.4,h:0.8,fontFace:F,fontSize:15,color:"B9C0CC",margin:0,lineSpacing:21});
 code(s,'{"deviceID": "L0302",\n "location": {"type": "Point", "coordinates": [77.666046, 12.841758]}}',
   M,3.56,7.4,0.72,12.5);
 s.addText([{text:"Roshni’s lamp record is that record, copied verbatim. "},
   {text:"“We plug into the municipal feed the day access is granted” is a schema fact, not a promise.",options:{bold:true,color:TEXT}},
   {text:" When it opens, the prior is replaced by measurement and the bands collapse — and the queue, the exposure model and all three screens are unchanged."}],
   {x:M,y:4.52,w:7.4,h:1.3,fontFace:F,fontSize:14,color:"B9C0CC",margin:0,lineSpacing:20});
 vrule(s,8.72,CY,4.34);
 s.addText("THE ASK",{x:9.1,y:CY,w:3.53,h:0.3,fontFace:F,fontSize:11,bold:true,color:MUTED,charSpacing:2.2,margin:0});
 s.addText("Approve the IUDX request.",
   {x:9.1,y:CY+0.44,w:3.53,h:1.0,fontFace:F,fontSize:20,bold:true,color:SOD,margin:0,lineSpacing:26});
 s.addText("We are not asking anyone to survey anything new. The register already exists.",
   {x:9.1,y:CY+1.62,w:3.53,h:0.9,fontFace:F,fontSize:14,color:"B9C0CC",margin:0,lineSpacing:20});
 rule(s,9.1,4.66,3.53);
 s.addText([{text:"7.7",options:{fontSize:62,bold:true,color:SOD}},
            {text:"×",options:{fontSize:28,bold:true,color:SOD}}],
   {x:9.1,y:4.84,w:3.53,h:1.0,fontFace:F,valign:"bottom",margin:0,wrap:false});
 s.addText("Same crew. Same budget. Different order.",
   {x:9.1,y:5.88,w:3.53,h:0.4,fontFace:F,fontSize:13,color:MUTED,margin:0,lineSpacing:18});
 source(s,"IUDX dataset 9b27c09f-1ec6-4acd-89f0-a27f23184017 · catalogue.cos.iudx.org.in.");}

/* ── 13 · APPENDIX A — every number ─────────────────────── */
{const s=S("Do not present this. It exists so any number a judge asks about can be found in ten seconds.");
 title(s,"Appendix A — every number, and where it came from",{size:26});
 const cols=[[
   ["126,974","civic complaints, 1 Jan – 19 Jun 2025"],
   ["39,847 · 31.4%","of them “Street Light Not Working”"],
   ["96.4%","electrical closure rate (40,632 / 42,138)"],
   ["58.0%","road-maintenance closure rate"],
   ["421,113","streetlights across 198 BBMP wards"],
   ["11,029","segments scored · 1,180 km · 33 wards"],
   ["95,557","walk-graph nodes · 98.4% one component"]],[
   ["1,508 / 1,128","lamps in snapshot / labelled working=yes|no"],
   ["690 · 6.3%","segments with any lamp evidence"],
   ["27.6%","mean P(dark) across all segments"],
   ["ρ +0.30 / +0.44","activity vs structural / vs night bus"],
   ["405 · 6,187","BMTC stops / departures after 21:00"],
   ["3,417 / 9,199","night-active POIs of all POIs"],
   ["17.9×","median bypass, 25 worst segments"]]];
 cols.forEach((col,ci)=>{const x=M+ci*6.24;
   col.forEach(([v,t],i)=>{const y=CY+i*0.62;
     rule(s,x,y-0.08,5.7);
     s.addText(v,{x,y:y+0.03,w:2.1,h:0.34,fontFace:F,fontSize:14,bold:true,color:TEXT,margin:0});
     s.addText(t,{x:x+2.2,y:y+0.06,w:3.5,h:0.32,fontFace:F,fontSize:12.5,color:MUTED,margin:0});});
   rule(s,x,CY+col.length*0.62-0.08,5.7);});
 s.addText("Counterfactual at a 40-repair budget: 4,544 vs 588 exposed pedestrian-km = 7.7×. Luckiest of 300 draws 4.9×. Steelman 1.9×. Surveyed wards only 6.4×. All lamp labels deleted 5.4×.",
   {x:M,y:6.28,w:W-2*M,h:0.5,fontFace:F,fontSize:12.5,color:TEXT,margin:0,lineSpacing:18});
 source(s,"All figures out/stats.json, out/curve.json, out/routes.json — pipeline run 22 Aug 2026.");}

/* ── 14 · APPENDIX B — the machinery ────────────────────── */
{const s=S("Do not present this either. It is the answer to 'how does the darkness model actually work' and to 'show me the pipeline'.");
 title(s,"Appendix B — the machinery",{size:26});
 s.addText("THE DARKNESS MODEL",{x:M,y:CY,w:5.6,h:0.28,fontFace:F,fontSize:11,bold:true,color:MUTED,charSpacing:2,margin:0});
 rule(s,M,CY+0.32,5.6);
 code(s,
"P(lit)   = coverage × 0.920\n"+
"           coverage = ward lamps/km ÷ 33.3\n"+
"           33.3 = 30 m standard pole spacing\n"+
"           0.920 = measured working rate\n"+
"Beta(α₀, β₀) = (K·P(lit), K·(1−P(lit)))   K = 2",
   M,2.3,5.6,1.5,12);
 s.addText("Evidence updates α and β, each decayed on a 30-day half-life so a confirmed repair genuinely clears a segment:",
   {x:M,y:3.96,w:5.6,h:0.6,fontFace:F,fontSize:12.5,color:"B9C0CC",margin:0,lineSpacing:17});
 [["IUDX zero current after dusk","2.0 → β"],["repair confirmed by a reporter","1.5 → α"],
  ["OSM working = no  /  = yes","1.0 → β / α"],["way lit = no","0.8 → β"],
  ["citizen report, corroborated","1.0 → β"],["OSM lamp, no working tag","0.4 → α"]]
 .forEach(([a,b],i)=>{const y=4.64+i*0.34;
   s.addText(a,{x:M,y,w:3.9,h:0.3,fontFace:F,fontSize:12,color:TEXT,margin:0});
   s.addText(b,{x:M+3.9,y,w:1.7,h:0.3,fontFace:F,fontSize:12,color:MUTED,align:"right",margin:0});});
 vrule(s,6.5,CY,4.34);
 s.addText("THE PIPELINE",{x:7.03,y:CY,w:5.6,h:0.28,fontFace:F,fontSize:11,bold:true,color:MUTED,charSpacing:2,margin:0});
 rule(s,7.03,CY+0.32,5.6);
 [["Inputs","OSM walk graph (95,557 nodes, 98.4% connected) · BMTC GTFS (6,187 night departures) · night-active POIs (3,417 of 9,199) · ward lamp density (421,113 lamps, 198 wards) · OSM working tags (1,128 labelled) · citizen reports · IUDX telemetry, gated"],
  ["Two models","EXPOSURE E(segment) = activity + structural, kept separately so convergent validation is possible.  DARKNESS Beta(α,β), mean = P(dark), var = confidence."],
  ["Four outputs","repair_priority = E · P(dark) · confidence, solved as a knapsack under budget.  route_penalty = L · (1 + λd·P(dark) + λe/E + λu·var) — note E divides.  Confidence band drives the routing refusal.  Report targeting on an upper confidence bound."],
  ["Vasanthanagar transition matrix","469 lamps, 17 Jun → 2 Jul 2019. DEAD→DEAD 33, DEAD→OK 28, OK→DEAD 15, OK→OK 360. 45.9% repaired, 4.0% failed, equilibrium dead share 8.0%."]]
 .forEach(([h,t],i)=>{const y=CY+0.56+i*1.08;
   s.addText(h,{x:7.03,y,w:5.6,h:0.28,fontFace:F,fontSize:13.5,bold:true,color:TEXT,margin:0});
   s.addText(t,{x:7.03,y:y+0.32,w:5.6,h:0.74,fontFace:F,fontSize:12,color:"B9C0CC",margin:0,lineSpacing:16});});
 source(s,"Every element exists in data/pipeline.py. No ML model, no cloud layer, no auth service. VIIRS nightlights are 500 m per pixel and are not used to judge a street.");}

await p.writeFile({fileName:"Roshni.pptx"});
console.log("wrote Roshni.pptx — spine build");
