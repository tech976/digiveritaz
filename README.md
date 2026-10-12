# DigiVeritaz

Static marketing site, deployed on Vercel with Cloudflare in front.

## Layout

| Path | What it is |
|---|---|
| `site/` | **The live website.** Vercel's root directory. Every file here maps to a public URL. |
| `seo/` | **A separate Vercel deployment** — the internal SEO tool, `noindex`, with its own `vercel.json` and Python API functions. Not part of the main site. |
| `_ops/` | Everything that operates the site but is never served. |
| `_ops/scripts/` | One-off build and migration scripts, run from the repo root. |
| `_ops/docs/` | Internal runbooks — design system, international SEO, the CRM lead chain. |
| `_ops/chatbot/` | Chatbot ingest and dev tooling. The *live* chatbot endpoint is `site/api/chat.py`. |
| `_ops/faq/` | Archive of FAQs replaced on the site, so any can be restored. |
| `_ops/apps-script-contact-form.gs` | Reference copy of the Google Apps Script behind the lead forms. |
| `_reference/images/` | Original service-page imagery. The site serves optimised `.webp` from `site/assets/`. |
| `_reference/documents/` | Brand guidelines, keyword sheets, content and schema documents. |
| `_local/` | Local scratch. Git-ignored, never committed. |

## Two things not to do

**Do not move or rename anything inside `site/`.** Those paths are live URLs.
`site/vercel.json` holds the redirects; add one there before changing any path.

**Do not move `seo/`.** It is deployed separately and its `vercel.json` and
`api/` functions are resolved relative to that folder.

## Cache busting

JS and CSS are served with a one-year immutable cache and versioned by a
`?v=` query string. Changing a bundle means bumping `?v=` on **every** page
that loads it, or returning visitors keep the old file for a year.
`_ops/scripts/bump_main_js_cache_version.py` does this for `main.min.js`.

`site/js/main.js` and `site/js/main.min.js` are maintained by hand in
parallel — the minified file is what ships, so every change must be made in
both and checked with `node --check`.

## Lead capture

Forms post to a Google Apps Script web app, which writes to the "DV Lead
Form" sheet and pushes to the CRM. The chain, its diagnostics and its
failure modes are documented in `_ops/docs/crm-connection.md`.
