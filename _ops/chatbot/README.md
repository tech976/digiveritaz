# DigiVeritaz AI Chatbot ("Veri")

A lead-qualification chat widget for the DigiVeritaz site. It behaves like a
junior sales rep: greets contextually, qualifies the visitor (service, industry,
budget, timeline, contact), recommends the right service page, injects **real**
case-study proof, answers FAQs, and always pushes toward **book a call / leave
details / WhatsApp**. Every answer is grounded in the site's own content (RAG).

## Architecture (no server, no database)

| Piece | What it is |
|---|---|
| **Retrieval (RAG)** | Lexical TF-IDF over `site/api/kb_index.json` (built from the site's own pages). Pure Python, in-memory — no vector DB, no embeddings cost. |
| **Backend** | One Vercel **Serverless Function**: `site/api/chat.py` → `POST /api/chat`. Stdlib only. |
| **LLM** | **Groq** primary → **Groq key 2** → **Gemini** fallback. Never dead-ends. |
| **Lead capture** | `capture_lead` tool-call → forwarded to `LEAD_WEBHOOK_URL` (your existing contact Apps Script / Sheet). Always logged to stdout as a backstop. |
| **Booking / handoff** | Configurable: WhatsApp (`WHATSAPP_NUMBER`) + contact page (`BOOKING_URL`). |
| **Widget** | Vanilla JS injected via `site/js/main.min.js` (+ CSS in `style.min.css`), brand green, mobile-first, no layout shift. |
| **Analytics** | One `ANALYTICS {...}` JSON line per chat (provider, captured, end-state) → Vercel function logs. |

State is **stateless**: the widget keeps the conversation in `sessionStorage` and
sends it each turn, so the function needs no storage.

## Environment variables

Copy `chatbot/.env.example` → repo-root `.env` (git-ignored) for local dev, and
set the **same** vars in **Vercel → Project → Settings → Environment Variables**
for production.

| Var | Purpose |
|---|---|
| `GROQ_API_KEY` | primary LLM |
| `GROQ_API_KEY_2` | fallback LLM (optional) |
| `GEMINI_API_KEY` | final fallback (optional) |
| `GROQ_MODEL` | default `llama-3.3-70b-versatile` |
| `GEMINI_MODEL` | default `gemini-2.0-flash` |
| `LEAD_WEBHOOK_URL` | where qualified leads are POSTed (the contact Apps Script) |
| `WHATSAPP_NUMBER` | digits only, e.g. `919956655662` |
| `BOOKING_URL` | e.g. `/contact-us/` (swap for a Calendly/Cal.com URL later) |

> **Never commit secrets.** `.env` is git-ignored; only `.env.example` is committed.

## Run locally

```bash
# 1) create repo-root .env from the example and fill in your keys
cp chatbot/.env.example .env

# 2) (re)build the knowledge base from the site's pages  — no API key needed
python chatbot/ingest.py

# 3) start the site + chat API together
python chatbot/devserver.py 3000
# open http://localhost:3000  → click "Chat with us" (bottom-right)
```

`devserver.py` mimics Vercel's clean URLs and serves `POST /api/chat` locally so
you can test the whole widget without the Vercel CLI.

## Update the knowledge base

Whenever service pages / case studies / FAQ change:

```bash
python chatbot/ingest.py     # rewrites site/api/kb_index.json (commit it)
```

It crawls all top-level pages + `case-study/*` + FAQ, strips nav/footer/scripts,
chunks the text. Commit the regenerated `kb_index.json`.

## Deploy on Vercel

1. The function lives at `site/api/chat.py`. Confirm the Vercel project **Root
   Directory = `site`** (Settings → General) — same root that serves the static site.
2. Add the env vars above in **Settings → Environment Variables** (Production +
   Preview).
3. `vercel.json` already declares the function (`maxDuration: 10`, bundles
   `kb_index.json`). Push the branch / merge to the production branch — Vercel
   builds the static site **and** the Python function automatically.
4. Test `https://www.digiveritaz.com/api/chat` (GET → health JSON) and the widget.

> **Free (Hobby) plan note:** 10s function limit (Groq stays well under it).
> Hobby is officially non-commercial — consider **Pro** for a commercial launch.
> Switching plans needs **no code changes**.

## Integration points (where to wire your stack later)

- **CRM:** point `LEAD_WEBHOOK_URL` at your Lead Management endpoint. The payload
  is form-encoded: `name, business, email, phone, service, industry, budget,
  timeline, notes, source=website-chatbot`.
- **Booking:** set `BOOKING_URL` to a Calendly/Cal.com link to upgrade the
  "Book a call" action from the contact page to a real calendar.
- **Vector search (optional upgrade):** the KB schema has room for an `embedding`
  field; swap the TF-IDF `retrieve()` for embeddings if you outgrow lexical search.
- **Mobile "Live Chat" button:** on the `abhishek-edits` branch there's a
  placeholder Live Chat button — wire it to open this widget when both merge.

## Guardrails (in the system prompt)

Only discusses DigiVeritaz; never invents prices/guarantees/case-study numbers
(grounds every claim in retrieved content); never quotes specific prices (routes
to a call); always attempts to capture contact details; escalates to
WhatsApp/human when unsure.
