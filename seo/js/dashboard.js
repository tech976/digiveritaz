/* DigiVeritaz SEO dashboard.
   Fans out one /api/analyze request per page, CONCURRENCY at a time, and fills
   the page as results land — so 293 pages never becomes one long request.

   Two audiences share this screen. "Plain English" mode is the default and
   assumes no SEO knowledge; "Expert" mode swaps in the technical names and the
   raw numbers. js/guide.js holds all the plain-language copy. */
(() => {
"use strict";

const CONCURRENCY = 6;
const LS_KEY = "dv-seo-keyphrases";
const G = window.DV_GUIDE;
const $  = s => document.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t);
  if (c) n.className = c; if (h != null) n.innerHTML = h; return n; };
const esc = s => String(s ?? "").replace(/[&<>"]/g, c =>
  ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]));

let PAGES = [], CLUSTERS = {}, UNMAPPED = [];
let RESULTS = new Map();
let overrides = load();
let sortKey = "overall", sortDir = 1, running = false, abort = false, selected = null;
let expert = false;

const QS = new URLSearchParams(location.search);
const LIMIT = Math.max(0, parseInt(QS.get("limit") || "0", 10)) || 0;

function load(){ try { return JSON.parse(localStorage.getItem(LS_KEY)) || {}; } catch { return {}; } }
function save(){ try { localStorage.setItem(LS_KEY, JSON.stringify(overrides)); } catch {} }

const keyphraseOf = p => overrides[p.path] || p.keyphrase || "";
const sourceOf    = p => overrides[p.path] ? "custom" : p.keyphrase_source;
// Bands match G.verdict() so the ring colour never disagrees with the word next to it.
const gradeOf     = s => s == null ? "unknown" : s >= 85 ? "good" : s >= 55 ? "ok" : "bad";
const info        = id => G.checks[id] || { cat:"content", impact:1, plain:id, why:"", fix:"" };
const nameOf      = c => expert ? c.label : info(c.id).plain;

/* ------------------------------------------------------------------- boot */
async function boot(){
  let d;
  try { d = await (await fetch("/api/inventory")).json(); }
  catch { $("#hero-sub").textContent = "Could not reach the server — is serve.py running?"; return; }

  PAGES = d.pages || []; CLUSTERS = d.clusters || {}; UNMAPPED = d.unmapped || [];
  [...new Set(PAGES.map(p => p.section))].sort()
    .forEach(s => $("#f-section").append(new Option(s, s)));

  if (QS.get("section")) $("#f-section").value = QS.get("section");
  if (QS.get("q")) $("#q").value = QS.get("q");
  if (QS.get("grade")) $("#f-grade").value = QS.get("grade");
  if (QS.get("expert") === "1") setMode(true);

  $("#hero-sub").textContent =
    `${PAGES.length} pages found on ${(d.origin || "").replace(/^https?:\/\//, "")}. `
    + `Checking them takes about a minute.`;
  render();

  const want = QS.get("page");
  const hit = want && PAGES.find(p => p.path === want || p.path === want + "/");
  if (QS.get("run") === "1"){ await runAudit(); if (hit) openDrawer(hit); }
  else if (hit) openDrawer(hit);
}

/* ------------------------------------------------------------ audit runner */
async function runAudit(){
  if (running) return;
  running = true; abort = false;
  $("#run").disabled = true; $("#stop").hidden = false; $("#export").disabled = true;
  $("#bar").hidden = false;
  RESULTS.clear(); render();

  const queue = visiblePages().slice(0, LIMIT || undefined);
  const total = queue.length;
  let done = 0;

  const worker = async () => {
    while (queue.length && !abort){
      const p = queue.shift();
      const u = `/api/analyze?url=${encodeURIComponent(p.url)}`
              + `&keyphrase=${encodeURIComponent(keyphraseOf(p))}`
              + `&keyphrase_source=${encodeURIComponent(sourceOf(p))}`;
      let rep = null;
      for (let attempt = 0; attempt < 2 && !rep; attempt++){
        try { rep = await (await fetch(u)).json(); }
        catch (e){
          if (attempt) rep = { url:p.url, error:String(e), scores:{}, checks:[], facts:{} };
          else await new Promise(r => setTimeout(r, 400));
        }
      }
      RESULTS.set(p.path, rep);
      done++;
      $("#barfill").style.width = (100 * done / total) + "%";
      $("#hero-sub").textContent = `Checking page ${done} of ${total}…`;
      if (done % 3 === 0 || done === total){ render(); summarise(); }
    }
  };
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));

  running = false;
  $("#run").disabled = false; $("#stop").hidden = true; $("#export").disabled = false;
  $("#run").textContent = "Check again";
  $("#bar").hidden = true;
  render(); summarise();

  const failed = [...RESULTS.values()].filter(r => r.error || r.status !== 200).length;
  $("#hero-sub").textContent =
    (abort ? `Stopped after ${done} of ${total} pages. ` : `Checked ${done} pages. `)
    + (failed ? `${failed} could not be loaded. ` : "")
    + `Last checked ${new Date().toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" })}.`;
}

/* --------------------------------------------------------------- summary */
function audited(){
  return [...RESULTS.values()].filter(r => r.scores && r.scores.overall != null);
}

function summarise(){
  const reps = audited();
  if (!reps.length) return;
  const avg = Math.round(reps.reduce((a, r) => a + r.scores.overall, 0) / reps.length);
  const v = G.verdict(avg), g = gradeOf(avg);

  const ring = $("#ring");
  ring.style.setProperty("--v", avg);
  ring.style.setProperty("--c", { good:"var(--green)", ok:"var(--amber)", bad:"var(--red)" }[g]);
  $("#ringval").textContent = avg;
  $("#hero-word").textContent = v.word;
  $("#hero-word").className = "hero-word " + g;
  $("#hero-line").textContent = G.siteVerdict(avg, reps.length);

  // Counted the same way the fix list counts, so the two can never disagree.
  const withFixes = reps.filter(r => (r.counts?.bad || 0) > 0).length;
  const minor     = reps.filter(r => !(r.counts?.bad || 0) && (r.counts?.ok || 0) > 0).length;
  $("#hero-stats").hidden = false;
  $("#hero-stats").innerHTML =
      stat(withFixes, "pages with something to fix", "bad")
    + stat(minor,     "pages with minor tweaks only", "ok")
    + stat(reps.length - withFixes - minor, "pages all clear", "good")
    + stat(PAGES.length - reps.length, "not checked yet", "na");

  buildFixList(reps);
}

const stat = (n, label, tone) =>
  `<div class="stat"><b class="d ${tone}"></b><strong>${n}</strong><span>${label}</span></div>`;

/* --------------------------------------------------- "fix these first" */
function buildFixList(reps){
  const agg = new Map();
  reps.forEach(r => (r.checks || []).forEach(c => {
    if (c.status !== "bad" && c.status !== "ok") return;
    const e = agg.get(c.id) || { id:c.id, label:c.label, bad:0, ok:0, pages:[] };
    e[c.status]++;
    if (c.status === "bad") e.pages.push(r.url);
    agg.set(c.id, e);
  }));

  // Rank by pages affected x how much the fix matters, failures counting double.
  const ranked = [...agg.values()]
    .map(e => ({ ...e, weight: (e.bad * 2 + e.ok) * info(e.id).impact }))
    .filter(e => e.bad > 0)
    .sort((a, b) => b.weight - a.weight);

  $("#f-check").innerHTML = '<option value="">Any</option>'
    + ranked.map(e => `<option value="${esc(e.id)}">${esc(expert ? e.label : info(e.id).plain)} (${e.bad})</option>`).join("");

  const host = $("#fixlist");
  host.textContent = "";
  $("#fix-section").hidden = ranked.length === 0;

  ranked.slice(0, 10).forEach((e, i) => {
    const g = info(e.id);
    const pct = Math.round(100 * e.bad / reps.length);
    const item = el("details", "fixitem");
    item.innerHTML = `
      <summary>
        <span class="rank">${i + 1}</span>
        <span class="fixmain">
          <span class="fixtitle">${esc(expert ? e.label : g.plain)}</span>
          <span class="fixwhy">${esc(g.why)}</span>
        </span>
        <span class="fixcount">
          <strong>${e.bad}</strong><span>page${e.bad !== 1 ? "s" : ""} · ${pct}%</span>
          <span class="meter"><i style="width:${pct}%"></i></span>
        </span>
        <span class="chev">›</span>
      </summary>
      <div class="fixbody">
        <div class="fixfix"><b>What to do</b><p>${esc(g.fix)}</p></div>
        <div class="fixpages">
          <b>Pages affected</b>
          <ul>${e.pages.slice(0, 8).map(u =>
            `<li><a href="${esc(u)}" target="_blank" rel="noopener">${esc(new URL(u).pathname)}</a></li>`).join("")}
          </ul>
          ${e.pages.length > 8 ? `<button class="linkbtn" data-check="${esc(e.id)}">See all ${e.pages.length} in the table below</button>` : ""}
        </div>
      </div>`;
    host.append(item);
  });

  host.querySelectorAll("button[data-check]").forEach(b => b.onclick = ev => {
    ev.preventDefault();
    $("#f-check").value = b.dataset.check;
    render();
    $("#f-check").scrollIntoView({ behavior:"smooth", block:"center" });
  });

  // Things that are fine everywhere — worth saying so.
  const clean = [...new Set(reps.flatMap(r => (r.checks || []).map(c => c.id)))]
    .filter(id => !agg.has(id) || (!agg.get(id).bad && !agg.get(id).ok));
  $("#wins-section").hidden = clean.length === 0;
  $("#wins").innerHTML = clean.map(id =>
    `<span class="win"><b class="d good"></b>${esc(expert ? (reps.flatMap(r => r.checks).find(c => c.id === id)?.label || id) : info(id).plain)}</span>`).join("");
}

/* ---------------------------------------------------------- table render */
function visiblePages(){
  const q = $("#q").value.trim().toLowerCase();
  const sec = $("#f-section").value, gr = $("#f-grade").value, ck = $("#f-check").value;
  return PAGES.filter(p => {
    const r = RESULTS.get(p.path);
    if (sec && p.section !== sec) return false;
    if (gr && gradeOf(r?.scores?.overall) !== gr) return false;
    if (ck && !(r?.checks || []).some(c => c.id === ck && c.status === "bad")) return false;
    if (q){
      const hay = (p.path + " " + keyphraseOf(p) + " " + (r?.facts?.title || "")).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

function sortVal(p, k){
  const r = RESULTS.get(p.path), f = r?.facts || {}, s = r?.scores || {};
  switch (k){
    case "section":     return p.section;
    case "keyphrase":   return keyphraseOf(p);
    case "seo":         return s.seo ?? 999;
    case "readability": return s.readability ?? 999;
    case "overall":     return s.overall ?? 999;
    case "bad":         return -(r?.counts?.bad ?? -1);
    case "words":       return f.word_count ?? 999;
    default:            return p.path;
  }
}

/* The single worst thing about a page, named in plain English. */
function biggestProblem(r){
  if (!r) return null;
  if (r.error || r.status !== 200) return { tone:"bad", text:"Page would not load" };
  const bad = (r.checks || []).filter(c => c.status === "bad");
  if (!bad.length){
    const ok = (r.checks || []).filter(c => c.status === "ok");
    return ok.length ? { tone:"ok", text:nameOf(ok.sort((a,b) => info(b.id).impact - info(a.id).impact)[0]) }
                     : { tone:"good", text:"Nothing wrong found" };
  }
  bad.sort((a, b) => info(b.id).impact - info(a.id).impact);
  const extra = bad.length - 1;
  return { tone:"bad", text:nameOf(bad[0]) + (extra ? ` +${extra} more` : "") };
}

function render(){
  const list = visiblePages().sort((a, b) => {
    const x = sortVal(a, sortKey), y = sortVal(b, sortKey);
    return (typeof x === "string" ? x.localeCompare(y) : x - y) * sortDir;
  });
  const tb = $("#rows"); tb.textContent = "";
  const frag = document.createDocumentFragment();

  for (const p of list){
    const r = RESULTS.get(p.path), s = r?.scores || {}, f = r?.facts || {};
    const pending = running && !r;
    const g = gradeOf(s.overall);
    const prob = biggestProblem(r);
    const tr = el("tr");
    if (selected === p.path) tr.className = "sel";
    tr.innerHTML =
      `<td class="path" title="${esc(p.path)}">${esc(p.path)}</td>
       <td class="hide-sm sub">${esc(p.section)}</td>
       <td class="kp hide-md">${esc(keyphraseOf(p))}${
         sourceOf(p) !== "sheet" ? '<span class="tag" title="Guessed from the web address — set a real one in the page report">guess</span>' : ""}</td>
       <td class="num">${pending ? '<span class="spin"></span>'
            : `<span class="score ${g}">${s.overall ?? "—"}</span>`}</td>
       <td class="verdict-col">${pending ? "" : `<span class="verdict ${g}">${G.verdict(s.overall).word}</span>`}</td>
       <td class="problem-col">${prob ? `<span class="prob ${prob.tone}"><b class="d ${prob.tone}"></b>${esc(prob.text)}</span>` : ""}</td>
       <td class="num expert-only">${s.seo ?? ""}</td>
       <td class="num expert-only">${s.readability ?? ""}</td>
       <td class="num expert-only">${f.word_count ?? ""}</td>`;
    tr.onclick = () => openDrawer(p);
    frag.append(tr);
  }
  tb.append(frag);
  $("#empty").hidden = list.length > 0;
  $("#shown").textContent = `Showing ${list.length} of ${PAGES.length}`;
}

/* ----------------------------------------------------------------- drawer */
/* ------------------------------------------------ Yoast-style page report */
let serpDevice = QS.get("device") === "mobile" ? "mobile" : "desktop";

/* Yoast's snippet preview: what the page looks like in Google, with the
   desktop and mobile truncation points Google actually uses. */
function snippetPreview(f, url){
  const title = f.title || "(no title)";
  const desc  = f.meta_description
    || "(No description written. Google will pick a sentence from the page itself.)";
  const lim = serpDevice === "mobile" ? { t:55, d:120 } : { t:62, d:160 };
  const cut = (s, n) => s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s;
  let crumb = url;
  try {
    const u = new URL(url);
    crumb = u.hostname.replace("www.", "")
          + u.pathname.replace(/\/$/, "").split("/").join(" › ");
  } catch {}
  const clipped = title.length > lim.t || desc.length > lim.d;
  return `<div class="snippet">
    <div class="snippet-bar">
      <span class="snippet-label">Google preview</span>
      <span class="devtoggle">
        <button data-dev="desktop"${serpDevice === "desktop" ? ' class="on"' : ""}>Desktop</button>
        <button data-dev="mobile"${serpDevice === "mobile" ? ' class="on"' : ""}>Mobile</button>
      </span>
    </div>
    <div class="serp-card ${serpDevice}">
      <div class="serp-url">${esc(crumb)}</div>
      <div class="serp-title">${esc(cut(title, lim.t))}</div>
      <div class="serp-desc">${esc(cut(desc, lim.d))}</div>
    </div>
    ${clipped ? `<p class="serp-note">The “…” is where Google cuts your text off on ${serpDevice}.</p>` : ""}
  </div>`;
}

/* Yoast groups bullets by severity, not by topic. */
const SEVERITY = [
  { key:"bad",  title:"Problems",      tone:"bad",  open:true  },
  { key:"ok",   title:"Improvements",  tone:"ok",   open:true  },
  { key:"na",   title:"Considerations",tone:"na",   open:true  },
  { key:"good", title:"Good results",  tone:"good", open:false },
];
const LIGHT = s => s == null ? { tone:"unknown", word:"Not checked" }
  : s >= 85 ? { tone:"good", word:"Good" }
  : s >= 55 ? { tone:"ok",   word:"OK" }
  :           { tone:"bad",  word:"Needs improvement" };

function bulletList(items){
  return `<ul class="bullets">${items.map(c => {
    const gi = info(c.id);
    return `<li class="b-${c.status}">
      <i class="d ${c.status}"></i>
      <div>
        <span class="lbl">${esc(nameOf(c))}</span>
        <span class="txt">${esc(c.text)}</span>
        ${(c.status === "bad" || c.status === "ok") && gi.why
          ? `<details class="more"><summary>Why this matters</summary>
               <p>${esc(gi.why)}</p><p><b>What to do:</b> ${esc(gi.fix)}</p></details>` : ""}
      </div></li>`;
  }).join("")}</ul>`;
}

/* One Yoast analysis panel — a traffic light, then severity groups. */
function analysisPanel(title, score, checks){
  if (!checks.length) return "";
  const l = LIGHT(score);
  const groups = SEVERITY.map(sev => {
    const items = checks.filter(c => c.status === sev.key)
      .sort((a, b) => info(b.id).impact - info(a.id).impact);
    if (!items.length) return "";
    return `<details class="sevgroup" ${sev.open ? "open" : ""}>
      <summary><i class="d ${sev.tone}"></i><span>${sev.title}</span>
        <em>${items.length}</em></summary>
      ${bulletList(items)}
    </details>`;
  }).join("");
  return `<section class="analysis">
    <header class="analysis-head">
      <h3>${esc(title)}</h3>
      <span class="light ${l.tone}"><i class="d ${l.tone}"></i>${l.word}${
        score != null ? ` · ${score}` : ""}</span>
    </header>
    ${groups}
  </section>`;
}

function openDrawer(p){
  selected = p.path; render();
  const r = RESULTS.get(p.path);
  const f = r?.facts || {};
  $("#d-section").textContent = p.section;
  $("#d-title").textContent = f.title || p.path;
  const a = $("#d-url"); a.textContent = p.url; a.href = p.url;
  const body = $("#d-body"); body.textContent = "";

  if (r && !r.error && r.status === 200)
    body.insertAdjacentHTML("beforeend", snippetPreview(f, p.url));

  const kwbox = el("div", "kwset");
  kwbox.innerHTML = `
    <label for="d-kp">Focus keyphrase</label>
    <p class="sub">The phrase you'd type into Google to find this page. Everything below is measured against it.</p>
    <div class="kwrow">
      <input id="d-kp" value="${esc(keyphraseOf(p))}" placeholder="e.g. seo agency in mumbai">
      <button class="btn btn-primary" id="d-recheck">Check again</button>
    </div>
    ${sourceOf(p) !== "sheet"
      ? `<p class="hint">⚠︎ This phrase was guessed from the web address, so the results below may be misleading. Set the real one for an accurate report.</p>` : ""}`;
  body.append(kwbox);

  if (!r){
    body.append(el("p", "sub", "This page hasn't been checked yet. Press “Check again” above."));
  } else if (r.error || r.status !== 200){
    body.append(el("p", "warn",
      `This page could not be loaded (${esc(r.error || "status " + r.status)}). Nothing else can be checked until it loads.`));
  } else {
    const seoChecks  = (r.checks || []).filter(c => c.group === "seo");
    const readChecks = (r.checks || []).filter(c => c.group === "readability");
    body.insertAdjacentHTML("beforeend",
        analysisPanel("SEO analysis", r.scores.seo, seoChecks)
      + analysisPanel("Readability analysis", r.scores.readability, readChecks));

    if (expert){
      const F = [["Words", f.word_count], ["Title px", f.title_px], ["Meta chars", f.meta_chars],
                 ["Headings", f.headings], ["H1s", f.h1_count], ["Images", f.images],
                 ["Alt missing", f.images_no_alt], ["Internal links", f.internal_links],
                 ["Outbound", f.external_links], ["Flesch", f.flesch]];
      body.append(el("div", "sect", "Raw measurements"));
      body.append(el("div", "facts", F.map(([k, val]) =>
        `<div class="fact"><span>${k}</span><strong>${val ?? "—"}</strong></div>`).join("")));
      if (f.schema_types?.length)
        body.append(el("p", "sub", "Schema: " + esc(f.schema_types.join(", "))));
    }
  }

  const cl = CLUSTERS[p.path];
  if (cl){
    body.insertAdjacentHTML("beforeend",
      `<section class="analysis">
         <header class="analysis-head"><h3>Other phrases worth targeting</h3></header>
         <p class="catblurb">From your keyword sheet — what people search for, and how many do so each month.</p>
         <table class="kwtable">
           <thead><tr><th>Search phrase</th><th class="n">Searches / month</th><th class="n">How hard</th></tr></thead>
           <tbody>${cl.keywords.slice(0, 25).map(k => `<tr>
             <td>${esc(k.keyword)}</td>
             <td class="n">${k.volume != null ? k.volume.toLocaleString() : "—"}</td>
             <td class="n">${k.difficulty ?? "—"}</td></tr>`).join("")}</tbody>
         </table>
         <p class="sub">${cl.keywords.length} phrases · ${cl.total_volume.toLocaleString()} searches a month combined</p>
       </section>`);
  }

  body.querySelectorAll(".devtoggle button").forEach(b => b.onclick = () => {
    serpDevice = b.dataset.dev; openDrawer(p);
  });

  $("#d-recheck").onclick = async () => {
    const kp = $("#d-kp").value.trim();
    if (kp && kp !== p.keyphrase) { overrides[p.path] = kp; save(); }
    else if (!kp) { delete overrides[p.path]; save(); }
    const btn = $("#d-recheck"); btn.disabled = true; btn.textContent = "Checking…";
    const u = `/api/analyze?url=${encodeURIComponent(p.url)}&keyphrase=${encodeURIComponent(kp)}`
            + `&keyphrase_source=${encodeURIComponent(sourceOf(p))}`;
    try { RESULTS.set(p.path, await (await fetch(u)).json()); } catch {}
    render(); summarise(); openDrawer(p);
  };

  $("#drawer").classList.add("open");
  $("#drawer").setAttribute("aria-hidden", "false");
  $("#backdrop").classList.add("on");
}

function closeDrawer(){
  $("#drawer").classList.remove("open");
  $("#drawer").setAttribute("aria-hidden", "true");
  $("#backdrop").classList.remove("on");
  selected = null; render();
}

/* ----------------------------------------------------------------- export */
function exportCsv(){
  const cols = ["path","section","keyphrase","keyphrase_source","verdict","overall","seo",
                "readability","problems","biggest_problem","words","title","url"];
  const rows = [cols.join(",")];
  for (const p of PAGES){
    const r = RESULTS.get(p.path); if (!r) continue;
    const s = r.scores || {}, c = r.counts || {}, f = r.facts || {};
    const v = [p.path, p.section, keyphraseOf(p), sourceOf(p), G.verdict(s.overall).word,
               s.overall, s.seo, s.readability, c.bad, biggestProblem(r)?.text,
               f.word_count, f.title, p.url];
    rows.push(v.map(x => `"${String(x ?? "").replace(/"/g, '""')}"`).join(","));
  }
  const blob = new Blob([rows.join("\n")], { type:"text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `digiveritaz-seo-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click(); URL.revokeObjectURL(a.href);
}

/* ------------------------------------------------------------------ wiring */
function setMode(isExpert){
  expert = isExpert;
  document.body.classList.toggle("expert", expert);
  document.querySelectorAll("#mode button")
    .forEach(b => b.classList.toggle("on", (b.dataset.mode === "expert") === expert));
  try { localStorage.setItem("dv-seo-mode", expert ? "expert" : "plain"); } catch {}
  if (audited().length) summarise();
  render();
}

$("#run").onclick = runAudit;
$("#stop").onclick = () => { abort = true; };
$("#export").onclick = exportCsv;
$("#d-close").onclick = closeDrawer;
$("#backdrop").onclick = closeDrawer;
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDrawer(); });
["#q", "#f-section", "#f-grade", "#f-check"].forEach(s => {
  $(s).addEventListener("input", render);
  $(s).addEventListener("change", render);
});
document.querySelectorAll("#mode button").forEach(b =>
  b.onclick = () => setMode(b.dataset.mode === "expert"));
document.querySelectorAll("th[data-sort]").forEach(th => th.onclick = () => {
  const k = th.dataset.sort;
  sortDir = (sortKey === k) ? -sortDir : (["path","section","keyphrase"].includes(k) ? 1 : 1);
  sortKey = k;
  document.querySelectorAll("th").forEach(t => t.classList.remove("sorted","desc"));
  th.classList.add("sorted"); if (sortDir < 0) th.classList.add("desc");
  render();
});
$("#theme").onclick = () => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = dark ? "light" : "dark";
  try { localStorage.setItem("dv-seo-theme", dark ? "light" : "dark"); } catch {}
};
try {
  const t = QS.get("theme") || localStorage.getItem("dv-seo-theme");
  if (t === "dark" || t === "light") document.documentElement.dataset.theme = t;
  if (localStorage.getItem("dv-seo-mode") === "expert") setMode(true);
} catch {}

boot();
})();
