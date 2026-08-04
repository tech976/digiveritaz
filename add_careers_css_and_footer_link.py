#!/usr/bin/env python3
"""Style the careers page and add its link to the footer sitewide.

The careers page reuses .c-about/.prose (already styled), so only the
three new components need rules: the teams grid, the hiring steps list
and the open-roles cards/empty state.

The footer "Company" column is inlined in every page, so the link is
injected across all of them plus the FOOT template in build.py.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
CSS = SITE / "css"

MARKER = "/* careers page v11 */"
NEW_VER = "1787200000"

PRETTY = """

/* careers page v11 */
.team-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:18px 0 28px}
.team-card{
  background:#fff;border:1px solid var(--border);border-radius:12px;padding:16px 18px;
}
.team-card h4{margin:0 0 6px;font-size:1rem;font-weight:700;color:#0f172a}
.team-card p{margin:0;font-size:.92rem;line-height:1.6;color:#475569}

.hire-steps{list-style:none;counter-reset:hs;padding:0;margin:18px 0 26px}
.hire-steps li{
  counter-increment:hs;position:relative;padding:0 0 18px 46px;
  border-left:2px solid var(--border);margin-left:14px;
}
.hire-steps li:last-child{border-left-color:transparent;padding-bottom:0}
.hire-steps li:before{
  content:counter(hs);position:absolute;left:-15px;top:-2px;
  width:28px;height:28px;border-radius:50%;
  background:var(--green);color:#fff;font-size:.85rem;font-weight:700;
  display:grid;place-items:center;
}
.hire-steps li strong{display:block;margin-bottom:3px;color:#0f172a}
.hire-steps li span{color:#475569;line-height:1.6}

.job-grid{display:grid;gap:14px;margin:18px 0 28px}

/* open positions: 3-up grid of blocks; an opened block spans the full row */
.job-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:22px 0 30px;align-items:start}
.job-card{
  position:relative;background:#fff;border:1px solid var(--border);border-radius:16px;
  overflow:hidden;transition:border-color .2s,box-shadow .2s,transform .2s;
  display:flex;flex-direction:column;height:100%;
}
.job-card:before{
  content:"";position:absolute;left:0;top:0;bottom:0;width:4px;
  background:linear-gradient(180deg,#22c55e,#15803d);
  opacity:0;transition:opacity .2s;
}
.job-card:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(17,24,39,.09)}
.job-card:hover:before{opacity:.55}
.job-card:has(details[open]){
  grid-column:1/-1;border-color:rgba(34,197,94,.45);
  box-shadow:0 14px 36px rgba(17,24,39,.10);transform:none;
}
.job-card:has(details[open]):before{opacity:1}
.job-det{display:flex;flex-direction:column;height:100%}

.job-summary{
  list-style:none;cursor:pointer;position:relative;
  padding:26px 26px 78px;height:100%;box-sizing:border-box;
}
.job-summary::-webkit-details-marker{display:none}
.job-summary:hover{background:#fafcfa}
.job-team{
  display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--green-dark);background:#f0fdf4;border:1px solid rgba(34,197,94,.22);
  border-radius:999px;padding:4px 11px;margin-bottom:13px;
}
.job-summary h3{margin:0 0 10px;font-size:1.22rem;line-height:1.3;letter-spacing:-.01em}
.job-blurb{margin:0 0 16px;font-size:.92rem;line-height:1.65;color:#64748b}
.job-meta{display:flex;flex-direction:column;gap:9px}
.job-meta span{display:inline-flex;align-items:center;gap:8px;font-size:.85rem;color:#64748b;font-weight:500}
.job-meta svg{
  width:15px;height:15px;flex-shrink:0;
  fill:none;stroke:#94a3b8;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;
}
.job-more{
  position:absolute;left:26px;bottom:24px;
  display:inline-flex;align-items:center;gap:6px;
  font-size:.85rem;font-weight:600;color:#64748b;transition:color .2s;
}
.job-summary:hover .job-more{color:var(--green-dark)}
.job-caret{display:grid;place-items:center;transition:transform .25s}
details[open] .job-caret{transform:rotate(180deg)}
.job-apply{
  position:absolute;right:26px;bottom:20px;left:auto;top:auto;transform:none;
  padding:9px 20px;font-size:.88rem;white-space:nowrap;z-index:2;
}
/* expanded: keep Apply at the top of the card, not below all the detail */
.job-card:has(details[open]) .job-apply{top:26px;bottom:auto}
.job-body{padding:0 26px 26px;border-top:1px solid var(--border);padding-top:20px}
.job-body > p:first-child{margin-top:0}
@media(max-width:1000px){.job-grid{grid-template-columns:repeat(2,1fr)}}

.job-sub{margin:16px 0 6px;font-size:.9rem;font-weight:700;letter-spacing:.04em;
  text-transform:uppercase;color:#0f172a}
.job-list{margin:0 0 4px;padding-left:20px}
.job-list li{margin:0 0 6px;line-height:1.6;color:#475569}
.job-note{margin:0 0 10px;line-height:1.7;color:#475569}
.job-sub:first-of-type{margin-top:20px}
[data-theme="dark"] .job-sub{color:#f1f5f9}
[data-theme="dark"] .job-list li,[data-theme="dark"] .job-note{color:#cbd5e1}

.job-empty{
  background:#f8fafc;border:1px dashed var(--border);border-radius:14px;
  padding:24px 26px;margin:18px 0 28px;
}
.job-empty p{margin:0 0 10px}
.job-empty .btn{margin-top:6px}

[data-theme="dark"] .team-card,
[data-theme="dark"] .job-card{background:rgba(255,255,255,.03);border-color:rgba(255,255,255,.1)}
[data-theme="dark"] .team-card h4,
[data-theme="dark"] .hire-steps li strong{color:#f1f5f9}
[data-theme="dark"] .team-card p,
[data-theme="dark"] .hire-steps li span,
[data-theme="dark"] .job-meta li{color:#cbd5e1}
[data-theme="dark"] .job-meta li{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.1)}
[data-theme="dark"] .job-empty{background:rgba(255,255,255,.03);border-color:rgba(255,255,255,.16)}
[data-theme="dark"] .job-team{background:rgba(34,197,94,.12)}
[data-theme="dark"] .job-summary:hover{background:rgba(255,255,255,.04)}
[data-theme="dark"] .job-meta span,[data-theme="dark"] .job-blurb,[data-theme="dark"] .job-more{color:#94a3b8}
[data-theme="dark"] .job-meta svg{stroke:#64748b}
[data-theme="dark"] .job-card:hover{box-shadow:0 10px 28px rgba(0,0,0,.35)}
[data-theme="dark"] .job-meta span{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.1);color:#cbd5e1}
[data-theme="dark"] .job-body{border-top-color:rgba(255,255,255,.1)}

/* recruitment form */
.c-apply h2{margin:0 0 8px}
.apply-lead{color:#475569;margin:0 0 22px}
.req{color:#dc2626;font-weight:700}
.cf-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.cf-field{display:flex;flex-direction:column;min-width:0}
.cf-full{grid-column:1/-1}
.cf-field label{font-size:.88rem;font-weight:600;color:#0f172a;margin-bottom:6px}
.cf-field input,.cf-field select,.cf-field textarea{
  width:100%;padding:12px 14px;border:1px solid var(--border);border-radius:11px;
  font-family:inherit;font-size:.94rem;background:#fff;color:#0b1220;
  box-sizing:border-box;transition:.18s;
}
.cf-field input:focus,.cf-field select:focus,.cf-field textarea:focus{
  outline:none;border-color:var(--green);box-shadow:0 0 0 3px rgba(34,197,94,.15);
}
.cf-field textarea{resize:vertical;min-height:96px}
.cf-consent{display:flex;gap:10px;align-items:flex-start;margin:18px 0 0;font-size:.9rem;color:#475569;line-height:1.6}
.cf-consent input{accent-color:var(--green);width:17px;height:17px;margin-top:2px;flex-shrink:0}
.cf-hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}
.cf-actions{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin-top:22px}
.cf-msg{margin:0;font-size:.92rem;color:#475569}
.cf-msg.is-ok{color:var(--green-dark);font-weight:600}
.cf-msg.is-err{color:#dc2626;font-weight:600}
[data-theme="dark"] .apply-lead,[data-theme="dark"] .cf-consent,[data-theme="dark"] .cf-msg{color:#cbd5e1}
[data-theme="dark"] .cf-field label{color:#f1f5f9}
[data-theme="dark"] .cf-field input,[data-theme="dark"] .cf-field select,[data-theme="dark"] .cf-field textarea{
  background:#0b1220;color:#f1f5f9;border-color:#1e293b;
}
@media(max-width:640px){.cf-grid{grid-template-columns:1fr}}

/* apply panel: hidden until an Apply button is clicked */
.c-apply{display:none;padding:10px 0 90px}
.c-apply.is-open{display:block}
.apply-head{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}
.apply-close{
  flex:0 0 auto;width:38px;height:38px;border-radius:50%;border:1px solid var(--border);
  background:#fff;color:#64748b;font-size:1.5rem;line-height:1;cursor:pointer;transition:.2s;
}
.apply-close:hover{background:#f1f5f9;color:#0f172a}

/* OTP */
.otp-row{display:flex;gap:8px;align-items:stretch}
.otp-row[hidden]{display:none}
.otp-row input{flex:1 1 auto;min-width:0}
.otp-btn{
  flex:0 0 auto;white-space:nowrap;background:var(--green);color:#fff;border:0;
  padding:0 16px;border-radius:11px;font-weight:700;font-size:.85rem;cursor:pointer;transition:.2s;
}
.otp-btn:hover{background:var(--green-dark)}
.otp-btn:disabled{opacity:.6;cursor:default}
.otp-msg{display:block;margin-top:6px;font-size:.83rem;color:#64748b;min-height:1em}
.otp-msg.is-ok{color:var(--green-dark);font-weight:600}
.otp-msg.is-err{color:#dc2626;font-weight:600}
#ca-submit:disabled{cursor:not-allowed}
[data-theme="dark"] .apply-close{background:transparent;border-color:rgba(255,255,255,.14);color:#94a3b8}
[data-theme="dark"] .apply-close:hover{background:rgba(255,255,255,.06);color:#f1f5f9}
[data-theme="dark"] .otp-msg{color:#94a3b8}

@media(max-width:640px){
  .team-grid{grid-template-columns:1fr}
  .job-grid{grid-template-columns:1fr}
  .job-summary{padding:22px 20px 74px}
  .job-more{left:20px;bottom:22px}
  .job-apply{right:20px;bottom:18px}
  .job-body{padding:20px 20px 22px}
  .job-body{padding:16px 16px 18px}
}
"""

MIN = (
    MARKER
    + ".team-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:18px 0 28px}"
    ".team-card{background:#fff;border:1px solid var(--border);border-radius:12px;padding:16px 18px}"
    ".team-card h4{margin:0 0 6px;font-size:1rem;font-weight:700;color:#0f172a}"
    ".team-card p{margin:0;font-size:.92rem;line-height:1.6;color:#475569}"
    ".hire-steps{list-style:none;counter-reset:hs;padding:0;margin:18px 0 26px}"
    ".hire-steps li{counter-increment:hs;position:relative;padding:0 0 18px 46px;"
    "border-left:2px solid var(--border);margin-left:14px}"
    ".hire-steps li:last-child{border-left-color:transparent;padding-bottom:0}"
    ".hire-steps li:before{content:counter(hs);position:absolute;left:-15px;top:-2px;width:28px;height:28px;"
    "border-radius:50%;background:var(--green);color:#fff;font-size:.85rem;font-weight:700;display:grid;place-items:center}"
    ".hire-steps li strong{display:block;margin-bottom:3px;color:#0f172a}"
    ".hire-steps li span{color:#475569;line-height:1.6}"
    ".job-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:22px 0 30px;align-items:start}"
    ".job-card{position:relative;background:#fff;border:1px solid var(--border);border-radius:16px;overflow:hidden;"
    "transition:border-color .2s,box-shadow .2s,transform .2s;display:flex;flex-direction:column;height:100%}"
    '.job-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;'
    "background:linear-gradient(180deg,#22c55e,#15803d);opacity:0;transition:opacity .2s}"
    ".job-card:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(17,24,39,.09)}"
    ".job-card:hover:before{opacity:.55}"
    ".job-card:has(details[open]){grid-column:1/-1;border-color:rgba(34,197,94,.45);"
    "box-shadow:0 14px 36px rgba(17,24,39,.10);transform:none}"
    ".job-card:has(details[open]):before{opacity:1}"
    ".job-det{display:flex;flex-direction:column;height:100%}"
    ".job-summary{list-style:none;cursor:pointer;position:relative;padding:26px 26px 78px;height:100%;box-sizing:border-box}"
    ".job-summary::-webkit-details-marker{display:none}.job-summary:hover{background:#fafcfa}"
    ".job-team{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;"
    "color:var(--green-dark);background:#f0fdf4;border:1px solid rgba(34,197,94,.22);border-radius:999px;padding:4px 11px;margin-bottom:13px}"
    ".job-summary h3{margin:0 0 10px;font-size:1.22rem;line-height:1.3;letter-spacing:-.01em}"
    ".job-blurb{margin:0 0 16px;font-size:.92rem;line-height:1.65;color:#64748b}"
    ".job-meta{display:flex;flex-direction:column;gap:9px}"
    ".job-meta span{display:inline-flex;align-items:center;gap:8px;font-size:.85rem;color:#64748b;font-weight:500}"
    ".job-meta svg{width:15px;height:15px;flex-shrink:0;fill:none;stroke:#94a3b8;stroke-width:1.8;"
    "stroke-linecap:round;stroke-linejoin:round}"
    ".job-more{position:absolute;left:26px;bottom:24px;display:inline-flex;align-items:center;gap:6px;"
    "font-size:.85rem;font-weight:600;color:#64748b;transition:color .2s}"
    ".job-summary:hover .job-more{color:var(--green-dark)}"
    ".job-caret{display:grid;place-items:center;transition:transform .25s}"
    "details[open] .job-caret{transform:rotate(180deg)}"
    ".job-apply{position:absolute;right:26px;bottom:20px;left:auto;top:auto;transform:none;"
    "padding:9px 20px;font-size:.88rem;white-space:nowrap;z-index:2}"
    ".job-card:has(details[open]) .job-apply{top:26px;bottom:auto}"
    ".job-body{padding:0 26px 26px;border-top:1px solid var(--border);padding-top:20px}"
    ".job-body > p:first-child{margin-top:0}"
    "@media(max-width:1000px){.job-grid{grid-template-columns:repeat(2,1fr)}}"
                ".job-sub{margin:16px 0 6px;font-size:.9rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#0f172a}"
    ".job-list{margin:0 0 4px;padding-left:20px}"
    ".job-list li{margin:0 0 6px;line-height:1.6;color:#475569}"
    ".job-note{margin:0 0 10px;line-height:1.7;color:#475569}"
    ".job-sub:first-of-type{margin-top:20px}"
    '[data-theme="dark"] .job-sub{color:#f1f5f9}'
    '[data-theme="dark"] .job-list li,[data-theme="dark"] .job-note{color:#cbd5e1}'
    ".job-empty{background:#f8fafc;border:1px dashed var(--border);border-radius:14px;padding:24px 26px;margin:18px 0 28px}"
    ".job-empty p{margin:0 0 10px}.job-empty .btn{margin-top:6px}"
    '[data-theme="dark"] .team-card,[data-theme="dark"] .job-card{background:rgba(255,255,255,.03);border-color:rgba(255,255,255,.1)}'
    '[data-theme="dark"] .team-card h4,[data-theme="dark"] .hire-steps li strong{color:#f1f5f9}'
    '[data-theme="dark"] .team-card p,[data-theme="dark"] .hire-steps li span,[data-theme="dark"] .job-meta li{color:#cbd5e1}'
    '[data-theme="dark"] .job-meta li{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.1)}'
    '[data-theme="dark"] .job-empty{background:rgba(255,255,255,.03);border-color:rgba(255,255,255,.16)}'
    '[data-theme="dark"] .job-team{background:rgba(34,197,94,.12)}'
    '[data-theme="dark"] .job-summary:hover{background:rgba(255,255,255,.04)}'
    '[data-theme="dark"] .job-meta span,[data-theme="dark"] .job-blurb,[data-theme="dark"] .job-more{color:#94a3b8}'
    '[data-theme="dark"] .job-meta svg{stroke:#64748b}'
    '[data-theme="dark"] .job-card:hover{box-shadow:0 10px 28px rgba(0,0,0,.35)}'
    '[data-theme="dark"] .job-meta span{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.1);color:#cbd5e1}'
    '[data-theme="dark"] .job-body{border-top-color:rgba(255,255,255,.1)}'
    ".c-apply h2{margin:0 0 8px}"
    ".apply-lead{color:#475569;margin:0 0 22px}.req{color:#dc2626;font-weight:700}"
    ".cf-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}"
    ".cf-field{display:flex;flex-direction:column;min-width:0}.cf-full{grid-column:1/-1}"
    ".cf-field label{font-size:.88rem;font-weight:600;color:#0f172a;margin-bottom:6px}"
    ".cf-field input,.cf-field select,.cf-field textarea{width:100%;padding:12px 14px;border:1px solid var(--border);"
    "border-radius:11px;font-family:inherit;font-size:.94rem;background:#fff;color:#0b1220;box-sizing:border-box;transition:.18s}"
    ".cf-field input:focus,.cf-field select:focus,.cf-field textarea:focus{outline:none;border-color:var(--green);"
    "box-shadow:0 0 0 3px rgba(34,197,94,.15)}"
    ".cf-field textarea{resize:vertical;min-height:96px}"
    ".cf-consent{display:flex;gap:10px;align-items:flex-start;margin:18px 0 0;font-size:.9rem;color:#475569;line-height:1.6}"
    ".cf-consent input{accent-color:var(--green);width:17px;height:17px;margin-top:2px;flex-shrink:0}"
    ".cf-hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}"
    ".cf-actions{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin-top:22px}"
    ".cf-msg{margin:0;font-size:.92rem;color:#475569}"
    ".cf-msg.is-ok{color:var(--green-dark);font-weight:600}.cf-msg.is-err{color:#dc2626;font-weight:600}"
    '[data-theme="dark"] .apply-lead,[data-theme="dark"] .cf-consent,[data-theme="dark"] .cf-msg{color:#cbd5e1}'
    '[data-theme="dark"] .cf-field label{color:#f1f5f9}'
    '[data-theme="dark"] .cf-field input,[data-theme="dark"] .cf-field select,[data-theme="dark"] .cf-field textarea{'
    "background:#0b1220;color:#f1f5f9;border-color:#1e293b}"
    "@media(max-width:640px){.cf-grid{grid-template-columns:1fr}}"
    ".c-apply{display:none;padding:10px 0 90px}.c-apply.is-open{display:block}"
    ".apply-head{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}"
    ".apply-close{flex:0 0 auto;width:38px;height:38px;border-radius:50%;border:1px solid var(--border);"
    "background:#fff;color:#64748b;font-size:1.5rem;line-height:1;cursor:pointer;transition:.2s}"
    ".apply-close:hover{background:#f1f5f9;color:#0f172a}"
    ".otp-row{display:flex;gap:8px;align-items:stretch}.otp-row[hidden]{display:none}"
    ".otp-row input{flex:1 1 auto;min-width:0}"
    ".otp-btn{flex:0 0 auto;white-space:nowrap;background:var(--green);color:#fff;border:0;padding:0 16px;"
    "border-radius:11px;font-weight:700;font-size:.85rem;cursor:pointer;transition:.2s}"
    ".otp-btn:hover{background:var(--green-dark)}.otp-btn:disabled{opacity:.6;cursor:default}"
    ".otp-msg{display:block;margin-top:6px;font-size:.83rem;color:#64748b;min-height:1em}"
    ".otp-msg.is-ok{color:var(--green-dark);font-weight:600}.otp-msg.is-err{color:#dc2626;font-weight:600}"
    "#ca-submit:disabled{cursor:not-allowed}"
    '[data-theme="dark"] .apply-close{background:transparent;border-color:rgba(255,255,255,.14);color:#94a3b8}'
    '[data-theme="dark"] .apply-close:hover{background:rgba(255,255,255,.06);color:#f1f5f9}'
    '[data-theme="dark"] .otp-msg{color:#94a3b8}'
    "@media(max-width:640px){.team-grid{grid-template-columns:1fr}"
    ".job-grid{grid-template-columns:1fr}"
    ".job-summary{padding:22px 20px 74px}"
    ".job-more{left:20px;bottom:22px}.job-apply{right:20px;bottom:18px}"
    ".job-body{padding:20px 20px 22px}"
    ".job-body{padding:16px 16px 18px}}"
)

# footer Company column: add Careers just before Contact
OLD_LI = '<li><a href="/contact-us/">Contact</a></li>'
NEW_LI = '<li><a href="/careers/">Careers</a></li>\n            ' + OLD_LI


def main():
    for name in ("style.css", "style.min.css"):
        p = CSS / name
        src = p.read_text(encoding="utf-8")
        if MARKER in src:
            print(f"  = already styled: {name}")
        else:
            p.write_text(src + (MIN if ".min." in name else PRETTY), encoding="utf-8")
            print(f"  + {name}")

    added = 0
    for p in sorted(list(SITE.rglob("*.html")) + [SITE / "build.py"]):
        if not p.is_file():
            continue
        src = p.read_text(encoding="utf-8")
        if '"/careers/"' in src or OLD_LI not in src:
            continue
        p.write_text(src.replace(OLD_LI, NEW_LI, 1), encoding="utf-8")
        added += 1
    print(f"\nfooter Careers link added to {added} files")

    bumped = 0
    for p in sorted(SITE.rglob("*.html")):
        src = p.read_text(encoding="utf-8")
        new = re.sub(r"(css/style\.min\.css\?v=)\d+", r"\g<1>" + NEW_VER, src)
        if new != src:
            p.write_text(new, encoding="utf-8")
            bumped += 1
    print(f"style.min.css cache-buster bumped to {NEW_VER} in {bumped} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
