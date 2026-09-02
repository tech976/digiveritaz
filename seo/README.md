# DigiVeritaz SEO dashboard

An internal, Yoast-style on-page SEO audit for every URL in the DigiVeritaz
sitemap. No API keys, no paid services — every score is computed from the page's
own HTML.

Intended to live at `seo.digiveritaz.com`; **not deployed yet** (see *Deploying*).

## Run it

```bash
cd seo
python3 serve.py            # http://localhost:3002
```

Nothing to install — stdlib only, same as `site/api/chat.py`.

Note this is *not* `site/serve.py`: that one is static-only and 501s on `/api/`.
This server dispatches `/api/*` to the same Python functions Vercel will run, so
the dashboard works fully offline against production URLs.

Press **Run audit** to crawl. Pages are fetched 6 at a time and the table fills
in as results land, so no single request goes near Vercel's 10s function limit.

### URL parameters

Deep-link into a view, or drive it from a script:

| Param | Example | Effect |
|---|---|---|
| `run` | `?run=1` | start the audit on load |
| `limit` | `?limit=20` | audit only the first N matching pages (quick spot check) |
| `section` | `?section=Services` | pre-filter to one section |
| `grade` | `?grade=bad` | pre-filter to poor pages |
| `q` | `?q=whatsapp` | pre-fill the search box |
| `page` | `?page=/services/seo/` | open that page's report directly |

## What it checks

**SEO** — keyphrase in title / meta description / slug / introduction /
subheadings / image alt, keyphrase density and length, SEO title pixel width,
meta description length, content length, single H1, heading hierarchy, image alt
coverage, internal and outbound links, canonical, indexability, Open Graph,
Twitter card, JSON-LD schema, `lang`, viewport, HTTP status.

**Readability** — Flesch reading ease, sentence length, paragraph length,
subheading distribution, passive voice, transition words, consecutive sentence
openers.

Each check returns a Yoast-style bullet (green / orange / red). Group scores are
the weighted mean of those bullets on Yoast's 9 / 6 / 3 scale.

Only copy inside `<main>` is analysed — nav, header and footer are excluded, so
word counts and readability reflect the actual page copy.

## Data

| File | Built by | Contents |
|---|---|---|
| `data/keywords.json` | `build_keywords.py` | keyword clusters from `../DV Keywords.xlsx` |
| `data/inventory.json` | `build_inventory.py` | every sitemap URL + its focus keyphrase |

```bash
python3 build_keywords.py                 # re-read the workbook
python3 build_inventory.py                # local sitemap files
python3 build_inventory.py --live         # fetch the production sitemap
```

Both read `.xlsx` and XML with the stdlib only — no `openpyxl`, no `pandas`.

**Focus keyphrases.** 14 pages get theirs from the workbook (highest-volume
keyword in the matching sheet). The other 279 fall back to a keyphrase derived
from the URL slug, which is a weak guess — a derived keyphrase failing
"keyphrase in introduction" usually means the guess was wrong, not that the page
is broken. Override any page's keyphrase in the drawer; overrides persist in
`localStorage`. Supplying a fuller sheet is the way to make the keyphrase checks
meaningful site-wide.

**One cluster has no landing page:** the workbook's *AI Services* sheet holds 25
keywords topped by "ai tools" (110,000/mo) with nothing to rank. Shown on load.

## Layout

```
seo/
├── index.html          dashboard shell
├── css/dashboard.css   brand tokens mirrored from site/css/style.css
├── js/dashboard.js     concurrency pool, filters, drawer, CSV export
├── api/
│   ├── _engine.py      rule engine — parsing, linguistics, assessments
│   ├── analyze.py      GET/POST /api/analyze?url=&keyphrase=
│   └── inventory.py    GET  /api/inventory
├── data/               generated JSON (committed)
├── build_keywords.py   DV Keywords.xlsx  -> data/keywords.json
├── build_inventory.py  sitemap.xml       -> data/inventory.json
├── serve.py            local dev server, static + /api
└── vercel.json
```

`_engine.py` uses the leading-underscore convention already used by
`site/api/_otp.js`: Vercel treats it as a shared module, not a route.

## Deploying

Not wired up yet. When you are ready:

1. New Vercel project with **root directory `seo/`** (keeps it isolated from the
   main site's deploys — a break here cannot take down www).
2. Add `seo.digiveritaz.com` to that project and point the DNS CNAME at Vercel.

**Before it goes public, put authentication in front of it.** The dashboard
publishes a ranked list of your own site's SEO weaknesses; on an open subdomain
that is a competitor's briefing document. Vercel Password Protection or SSO on
the project is the least-effort fix. `X-Robots-Tag: noindex` and the page's
robots meta keep it out of search results, but they do not stop anyone with the
URL.

`api/analyze.py` also refuses any host outside `ALLOWED_HOSTS`, so the endpoint
cannot be used as an open proxy to crawl arbitrary sites.
