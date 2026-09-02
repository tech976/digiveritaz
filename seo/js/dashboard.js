/* DigiVeritaz SEO dashboard.
   Fans out one /api/analyze request per page, CONCURRENCY at a time, and fills
   the table as results land — so 293 pages never becomes one long request. */
(() => {
"use strict";

const CONCURRENCY = 6;
const LS_KEY = "dv-seo-keyphrases";   // per-page focus keyphrase overrides
const $  = s => document.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t);
  if (c) n.className = c; if (h != null) n.innerHTML = h; return n; };
const esc = s => String(s ?? "").replace(/[&<>"]/g, c =>
  ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]));

let PAGES = [], CLUSTERS = {}, UNMAPPED = [];
let RESULTS = new Map();          // path -> report
let overrides = load();
let sortKey = "path", sortDir = 1, running = false, abort = false, selected = null;

/* Deep-linkable state: ?section=Services&q=seo&run=1&limit=20
   `limit` audits only the first N matching pages — handy for a quick spot check
   without crawling all 293. */
const QS = new URLSearchParams(location.search);
const LIMIT = Math.max(0, parseInt(QS.get("limit") || "0", 10)) || 0;

function load(){ try { return JSON.parse(localStorage.getItem(LS_KEY)) || {}; }
                 catch { return {}; } }
function save(){ try { localStorage.setItem(LS_KEY, JSON.stringify(overrides)); } catch {} }

const keyphraseOf = p => overrides[p.path] || p.keyphrase || "";
const sourceOf    = p => overrides[p.path] ? "custom" : p.keyphrase_source;
const gradeOf     = s => s == null ? "unknown" : s >= 80 ? "good" : s >= 55 ? "ok" : "bad";

/* ------------------------------------------------------------------ boot */
async function boot(){
  let d;
  try {
    d = await (await fetch("/api/inventory")).json();
  } catch (e) {
    $("#note").textContent = "Could not load /api/inventory — is serve.py running?";
    return;
  }
  PAGES = d.pages || []; CLUSTERS = d.clusters || {}; UNMAPPED = d.unmapped || [];
  $("#origin").textContent = d.origin || "";
  $("#c-pages").textContent = PAGES.length;
  $("#c-kw").textContent = PAGES.filter(p => p.keyphrase_source === "sheet").length;

  const secs = [...new Set(PAGES.map(p => p.section))].sort();
  secs.forEach(s => $("#f-section").append(new Option(s, s)));

  if (QS.get("section") && secs.includes(QS.get("section"))) $("#f-section").value = QS.get("section");
  if (QS.get("q")) $("#q").value = QS.get("q");
  if (QS.get("grade")) $("#f-grade").value = QS.get("grade");
  $("#note").textContent =
    `${PAGES.length} pages ready. ${UNMAPPED.length ? UNMAPPED.length + " keyword cluster(s) have no landing page. " : ""}Press “Run audit”.`;
  render();

  // ?page=/services/seo/ opens that page's report directly — a shareable link
  // to one finding rather than the whole table.
  const want = QS.get("page");
  if (want){
    const hit = PAGES.find(p => p.path === want || p.path === want + "/");
    if (hit){
      if (QS.get("run") === "1"){
        await runAudit();
        openDrawer(hit);
        return;
      }
      openDrawer(hit);
    }
  }
  if (QS.get("run") === "1") runAudit();
}

/* ------------------------------------------------------------ audit runner */
async function runAudit(){
  if (running) return;
  running = true; abort = false;
  $("#run").disabled = true; $("#stop").hidden = false; $("#export").disabled = true;
  RESULTS.clear(); render();

  const queue = visiblePages().slice(0, LIMIT || undefined);
  const total = queue.length;
  let done = 0;

  const worker = async () => {
    while (queue.length && !abort) {
      const p = queue.shift();
      const u = `/api/analyze?url=${encodeURIComponent(p.url)}`
              + `&keyphrase=${encodeURIComponent(keyphraseOf(p))}`
              + `&keyphrase_source=${encodeURIComponent(sourceOf(p))}`;
      // One retry: a single dropped connection shouldn't cost a page.
      let rep = null;
      for (let attempt = 0; attempt < 2 && !rep; attempt++){
        try { rep = await (await fetch(u)).json(); }
        catch (e) {
          if (attempt) rep = { url: p.url, error: String(e), scores: {}, checks: [], facts: {} };
          else await new Promise(r => setTimeout(r, 400));
        }
      }
      RESULTS.set(p.path, rep);
      done++;
      $("#barfill").style.width = (100 * done / total) + "%";
      $("#note").textContent = `Auditing ${done} of ${total}… ${p.path}`;
      if (done % 3 === 0 || done === total) { render(); summarise(); }
    }
  };
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));

  running = false;
  $("#run").disabled = false; $("#stop").hidden = true; $("#export").disabled = false;
  const failed = [...RESULTS.values()].filter(r => r.error || r.status !== 200).length;
  $("#note").textContent = (abort ? `Stopped after ${done} of ${total} pages.` : `Audited ${done} pages.`)
    + (failed ? `  ${failed} could not be fetched.` : "");
  render(); summarise();
}

/* ------------------------------------------------------------- summary cards */
function summarise(){
  const reps = [...RESULTS.values()].filter(r => r.scores && r.scores.overall != null);
  if (!reps.length) return;
  const avg = Math.round(reps.reduce((a, r) => a + r.scores.overall, 0) / reps.length);
  const g = gradeOf(avg);
  const colour = { good: "var(--green)", ok: "var(--amber)", bad: "var(--red)" }[g];
  const ring = $("#ring");
  ring.style.setProperty("--v", avg); ring.style.setProperty("--c", colour);
  $("#ringval").textContent = avg;
  $("#ringsub").textContent = `Mean of ${reps.length} audited page${reps.length !== 1 ? "s" : ""}`;

  const tally = { good: 0, ok: 0, bad: 0 };
  reps.forEach(r => tally[gradeOf(r.scores.overall)]++);
  $("#c-grades").innerHTML =
      `<span class="pill good"><i class="d good"></i>${tally.good} good</span>`
    + `<span class="pill ok"><i class="d ok"></i>${tally.ok} needs work</span>`
    + `<span class="pill bad"><i class="d bad"></i>${tally.bad} poor</span>`;

  const bad = reps.reduce((a, r) => a + (r.counts?.bad || 0), 0);
  $("#c-bad").textContent = bad;
  $("#c-pages-sub").textContent = `${reps.length} audited of ${PAGES.length}`;

  // Rank the failing checks by how many pages they affect.
  const byCheck = new Map();
  reps.forEach(r => (r.checks || []).filter(c => c.status === "bad").forEach(c => {
    const e = byCheck.get(c.id) || { label: c.label, n: 0 };
    e.n++; byCheck.set(c.id, e);
  }));
  const top = [...byCheck.entries()].sort((a, b) => b[1].n - a[1].n);
  $("#f-check").innerHTML = '<option value="">Any</option>'
    + top.map(([id, v]) => `<option value="${esc(id)}">${esc(v.label)} (${v.n})</option>`).join("");
  if (top.length){
    $("#topissues-card").hidden = false;
    $("#topissues").innerHTML = top.slice(0, 8).map(([id, v]) => {
      const pct = Math.round(100 * v.n / reps.length);
      return `<div style="display:flex;align-items:center;gap:10px;padding:5px 0">
        <span style="flex:0 0 210px;font-weight:600">${esc(v.label)}</span>
        <span style="flex:1;height:7px;background:var(--border);border-radius:5px;overflow:hidden">
          <span style="display:block;height:100%;width:${pct}%;background:var(--red)"></span></span>
        <span class="sub" style="flex:0 0 100px;text-align:right;margin:0">${v.n} pages · ${pct}%</span>
      </div>`;
    }).join("");
  }
}

/* -------------------------------------------------------------- table render */
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
    case "seo":         return s.seo ?? -1;
    case "readability": return s.readability ?? -1;
    case "overall":     return s.overall ?? -1;
    case "bad":         return r?.counts?.bad ?? -1;
    case "words":       return f.word_count ?? -1;
    default:            return p.path;
  }
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
    const tr = el("tr");
    if (selected === p.path) tr.className = "sel";
    const pending = running && !r;
    const cell = v => `<span class="score ${gradeOf(v)}">${v == null ? "—" : v}</span>`;
    tr.innerHTML =
      `<td class="path" title="${esc(p.path)}">${esc(p.path)}</td>
       <td class="hide-sm sub" style="margin:0">${esc(p.section)}</td>
       <td class="kp hide-sm">${esc(keyphraseOf(p))}<span class="tag">${esc(sourceOf(p))}</span></td>
       <td class="num">${pending ? '<span class="spin"></span>' : cell(s.seo)}</td>
       <td class="num">${pending ? "" : cell(s.readability)}</td>
       <td class="num">${pending ? "" : cell(s.overall)}</td>
       <td class="num hide-sm">${r ? miniCounts(r) : ""}</td>
       <td class="num hide-sm">${f.word_count ?? ""}</td>`;
    tr.onclick = () => openDrawer(p);
    frag.append(tr);
  }
  tb.append(frag);
  $("#empty").hidden = list.length > 0;
  $("#shown").textContent = `${list.length} of ${PAGES.length} pages`;
}

function miniCounts(r){
  const c = r.counts || {};
  if (r.error) return `<span class="pill bad">error</span>`;
  return `<span class="mini">
    <b class="d bad"></b>${c.bad || 0}
    <b class="d ok" style="margin-left:6px"></b>${c.ok || 0}
    <b class="d good" style="margin-left:6px"></b>${c.good || 0}</span>`;
}

/* -------------------------------------------------------------------- drawer */
function openDrawer(p){
  selected = p.path; render();
  const r = RESULTS.get(p.path);
  $("#d-title").textContent = r?.facts?.title || p.path;
  const a = $("#d-url"); a.textContent = p.url; a.href = p.url;
  const body = $("#d-body"); body.textContent = "";

  // focus keyphrase editor
  const kwbox = el("div", "kwset");
  kwbox.innerHTML = `<label style="font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)">Focus keyphrase</label>
    <input id="d-kp" value="${esc(keyphraseOf(p))}">
    <button class="btn btn-primary" id="d-recheck">Re-analyse</button>`;
  body.append(kwbox);

  if (!r){
    body.append(el("p", "sub", "Not audited yet — set a keyphrase and press Re-analyse, or run the full audit."));
  } else if (r.error){
    body.append(el("p", "sub", "Could not fetch this page: " + esc(r.error)));
  } else {
    const s = r.scores || {};
    const bar = el("div", "scorebar");
    bar.innerHTML = ["seo", "readability", "overall"].map(k =>
      `<div class="b"><span>${k === "seo" ? "SEO" : k === "readability" ? "Readability" : "Overall"}</span>
       <strong class="score ${gradeOf(s[k])}" style="background:none;padding:0">${s[k] ?? "—"}</strong></div>`).join("");
    body.append(bar);

    const f = r.facts || {};
    body.append(el("div", "sect", "Page facts"));
    const facts = el("div", "facts");
    const F = [
      ["Words", f.word_count], ["Title px", f.title_px], ["Meta chars", f.meta_chars],
      ["Headings", f.headings], ["H1s", f.h1_count], ["Images", f.images],
      ["Alt missing", f.images_no_alt], ["Internal links", f.internal_links],
      ["Outbound", f.external_links], ["Flesch", f.flesch],
    ];
    facts.innerHTML = F.map(([k, v]) =>
      `<div class="fact"><span>${k}</span><strong>${v ?? "—"}</strong></div>`).join("");
    body.append(facts);
    if (f.schema_types?.length)
      body.append(el("p", "sub", "Schema: " + esc(f.schema_types.join(", "))));

    for (const [group, title] of [["seo", "SEO analysis"], ["readability", "Readability analysis"]]){
      const items = (r.checks || []).filter(c => c.group === group)
        .sort((a, b) => ({ bad: 0, ok: 1, na: 2, good: 3 })[a.status] - ({ bad: 0, ok: 1, na: 2, good: 3 })[b.status]);
      if (!items.length) continue;
      body.append(el("div", "sect", title));
      const ul = el("ul", "bullets");
      ul.innerHTML = items.map(c =>
        `<li><i class="d ${c.status}"></i><div><span class="lbl">${esc(c.label)}</span>
         <span class="txt">${esc(c.text)}</span></div></li>`).join("");
      body.append(ul);
    }
  }

  // keyword cluster from the sheet
  const cl = CLUSTERS[p.path];
  if (cl){
    body.append(el("div", "sect", `Keyword cluster — ${esc(cl.sheet)}`));
    const content = r?.facts ? null : null;
    const tbl = el("table", "kwtable");
    tbl.innerHTML = `<thead><tr><th>Keyword</th><th>Intent</th><th class="n">Volume</th><th class="n">KD</th></tr></thead>`
      + "<tbody>" + cl.keywords.slice(0, 25).map(k =>
        `<tr><td>${esc(k.keyword)}</td><td class="sub" style="margin:0">${esc(k.intent || "—")}</td>
         <td class="n">${k.volume != null ? k.volume.toLocaleString() : "—"}</td>
         <td class="n">${k.difficulty ?? "—"}</td></tr>`).join("") + "</tbody>";
    body.append(tbl);
    body.append(el("p", "sub",
      `${cl.keywords.length} keywords · ${cl.total_volume.toLocaleString()} combined monthly volume`));
  }

  $("#d-recheck").onclick = async () => {
    const kp = $("#d-kp").value.trim();
    if (kp && kp !== p.keyphrase) { overrides[p.path] = kp; save(); }
    else if (!kp) { delete overrides[p.path]; save(); }
    $("#d-recheck").disabled = true; $("#d-recheck").textContent = "Analysing…";
    const u = `/api/analyze?url=${encodeURIComponent(p.url)}&keyphrase=${encodeURIComponent(kp)}`
            + `&keyphrase_source=${encodeURIComponent(sourceOf(p))}`;
    try { RESULTS.set(p.path, await (await fetch(u)).json()); } catch (e) {}
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

/* -------------------------------------------------------------------- export */
function exportCsv(){
  const cols = ["path", "section", "keyphrase", "keyphrase_source", "seo", "readability",
                "overall", "bad", "ok", "good", "words", "title_px", "meta_chars",
                "h1_count", "images_no_alt", "internal_links", "flesch", "title", "url"];
  const rows = [cols.join(",")];
  for (const p of PAGES){
    const r = RESULTS.get(p.path); if (!r) continue;
    const s = r.scores || {}, c = r.counts || {}, f = r.facts || {};
    const v = [p.path, p.section, keyphraseOf(p), sourceOf(p), s.seo, s.readability, s.overall,
               c.bad, c.ok, c.good, f.word_count, f.title_px, f.meta_chars, f.h1_count,
               f.images_no_alt, f.internal_links, f.flesch, f.title, p.url];
    rows.push(v.map(x => `"${String(x ?? "").replace(/"/g, '""')}"`).join(","));
  }
  const blob = new Blob([rows.join("\n")], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `digiveritaz-seo-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click(); URL.revokeObjectURL(a.href);
}

/* --------------------------------------------------------------------- wiring */
$("#run").onclick    = runAudit;
$("#stop").onclick   = () => { abort = true; };
$("#export").onclick = exportCsv;
$("#d-close").onclick = closeDrawer;
$("#backdrop").onclick = closeDrawer;
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDrawer(); });
["#q", "#f-section", "#f-grade", "#f-check"].forEach(s => {
  $(s).addEventListener("input", render);
  $(s).addEventListener("change", render);
});
document.querySelectorAll("th[data-sort]").forEach(th => th.onclick = () => {
  const k = th.dataset.sort;
  sortDir = (sortKey === k) ? -sortDir : (["path", "section", "keyphrase"].includes(k) ? 1 : -1);
  sortKey = k;
  document.querySelectorAll("th .arrow").forEach(a => a.remove());
  th.append(Object.assign(document.createElement("span"),
    { className: "arrow", textContent: sortDir > 0 ? " ▲" : " ▼" }));
  render();
});
$("#theme").onclick = () => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = dark ? "light" : "dark";
  try { localStorage.setItem("dv-seo-theme", dark ? "light" : "dark"); } catch {}
};
try { const t = localStorage.getItem("dv-seo-theme"); if (t) document.documentElement.dataset.theme = t; } catch {}

boot();
})();
