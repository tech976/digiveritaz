# Website leads → Sheet → CRM

How a lead gets from digiveritaz.com into the CRM, how to tell when it doesn't,
and the fix for the failure that cost us hours on 5 Oct 2026.

If you are here because **leads are not showing up in the CRM**, skip to
[Diagnose it in 30 seconds](#diagnose-it-in-30-seconds).

---

## The chain

```
visitor submits a form
        │
        ▼
Apps Script web app  (/exec, action=lead_save)
        │
        ├──► "DV Lead Form" Google Sheet        ← ALWAYS happens. The source of truth.
        ├──► notification email to the team     ← Complete leads only
        ├──► thank-you email to the visitor     ← Complete leads only
        └──► POST to the CRM webhook            ← Complete leads only. BEST-EFFORT.
                     │
                     ▼
        crm.digiveritaz.tech/api/website/lead
                     │
                     ▼
              leads pipeline (source='website')

        ┌──────────────────────────────────────────────┐
        │ BACKSTOP: the CRM also PULLS from the sheet  │
        │ every 10 min and ingests anything the push   │
        │ never delivered.                             │
        └──────────────────────────────────────────────┘
```

Two things to understand about this shape:

1. **The sheet write and the CRM push are independent.** A lead can be complete
   in the sheet and absent from the CRM. That is not data loss, it is a delivery
   failure, and the sheet is how you recover.
2. **The push is best-effort by design** — it sits in a `try/catch` so a CRM
   outage can never stop a lead being captured. The cost is that a *permanent*
   push failure used to be invisible. Both halves of that are now addressed: the
   outcome is written into the sheet (see [CRM Push column](#the-crm-push-column))
   and the CRM pulls as a backstop.

Partial leads (the form was started, the phone entered, never submitted) are
written to the sheet with `Status = Partial` and are deliberately **not** pushed
or pulled into the pipeline.

---

## Where everything lives

### Website side

| What | Where |
|---|---|
| Live endpoint | `https://script.google.com/macros/s/AKfycby3DZjNUqSEU2Pg2rv45pnYTZT78L4405Et0SJ_NOBybsDLyd6ZWzxlSaEMx1TnKZkc/exec` |
| Apps Script source (reference copy) | `_ops/apps-script-contact-form.gs` |
| Manifest (reference copy) | `_ops/appsscript.json` |
| Sheet | `DV Lead Form` — tab name is in `SHEET_NAME` |
| Lead ID column | **M** — rows are upserted on it, so one lead is one row |
| Secret | Script Property `CRM_WEBHOOK_SECRET`. **Never in the code, never in the repo.** |

`_ops/apps-script-contact-form.gs` is a **snapshot, not a deployment**. Pushing it
to git changes nothing live. To deploy: paste it into the Apps Script editor, save,
then **Deploy → Manage deployments → ✏️ → Version: New version**.

> **Create a new VERSION, not a new deployment.** A new deployment gets a new
> `/exec` URL, which the website does not know about — the old URL keeps serving
> the old code and you will chase ghosts. This has already happened once.

### CRM side (`Durva Crm` repo)

| What | Where |
|---|---|
| Inbound webhook | `backend/routes/website-leads.js` → `POST /api/website/lead` |
| Shared ingest logic | `ingestWebsiteLead()` in the same file |
| Sheet-pull backstop | `backend/website-sheet-sync.js` |
| Sweep schedule | `backend/jobs.js` → `startWebsiteSheetSync()`, every 10 min |
| One-off backfill | `scripts/sync-website-sheet.js` |
| Read-only sheet mirror (BD tab) | `backend/routes/website-submissions.js` |
| Attribution parser | `backend/attribution.js` |

Environment variables:

| Var | Purpose |
|---|---|
| `WEBSITE_LEAD_SECRET` | Validates the inbound webhook. Must equal the Apps Script `CRM_WEBHOOK_SECRET`. |
| `WEBSITE_SHEET_URL` | The `/exec` URL. Powers the BD mirror tab **and the backstop sweep** — if unset, the safety net is off. |
| `WEBSITE_SHEET_SECRET` | Only if the read secret differs from `WEBSITE_LEAD_SECRET`. Normally leave empty. |

The webhook and the backstop both run through `ingestWebsiteLead()`, so dedup,
attribution and enrichment cannot drift between the two paths. Keep it that way.

### Form source slugs

The site sends `_source`; the CRM maps it to a readable form name in
`SOURCE_LABELS`. **Add new slugs there**, or leads show up as the generic
"Website form".

| `_source` | CRM label |
|---|---|
| `website-contact-form` | Contact-us form |
| `website-popup-form` | Project popup |
| `website-popup-v2` | Free-proposal popup |
| `get-proposal-page` | Free-proposal popup |
| `website-enquiry-page` | Enquiry page |
| `website-chatbot` | Website chatbot |

---

## Diagnose it in 30 seconds

Every endpoint below is **read-only and creates no lead**. `<SECRET>` is the
Script Property value; get it from the CRM's `WEBSITE_LEAD_SECRET`.

### 1. Is the endpoint alive and configured?

```
<EXEC_URL>?diag=1
```

Check `build` (which version is actually live), `sheet_found`, `crm_secret_set`,
and `secret_left_in_code` — the last must be `false`.

### 2. Can Apps Script reach the CRM at all?  ← **the important one**

```
<EXEC_URL>?diag=crm&secret=<SECRET>
```

It posts to the CRM with a **deliberately wrong** secret, so the CRM rejects it
and no lead is created. We only want to know whether the request leaves Google.

```jsonc
// HEALTHY — a 401 is the correct answer to a wrong secret
{ "reached": true, "http": 401,
  "verdict": "OK — the request left Apps Script and the CRM answered." }

// BROKEN — this is the fault, and the error names it
{ "reached": false,
  "error": "Exception: You do not have permission to call UrlFetchApp.fetch...",
  "verdict": "THE CALL NEVER LEFT APPS SCRIPT" }
```

### 3. Are the editor and the live URL the same project and account?

```
<EXEC_URL>?diag=who&secret=<SECRET>
```

Compare `script_id` with the `/projects/<id>/edit` in the editor's address bar,
and `effective_user` with the editor's top-right avatar. Run `whoAmI` in the
editor for the same values from that side. If they disagree, the account you are
fixing is not the one serving the website.

### 4. What is actually in the sheet?

```
<EXEC_URL>?action=list&secret=<SECRET>
```

Every row, Partial and Complete, keyed by header name.

### 5. What did the CRM receive?

```
pm2 logs crm | grep website-lead
```

`[website-lead] POST received:` on every hit, `CREATED` / `REJECTED 401` /
`skipped (status != Complete)` after it.

---

## The CRM Push column

Column **"CRM Push"** in the sheet records the outcome of each push, next to the
lead:

| Value | Means |
|---|---|
| `OK 201` | Created in the CRM. |
| `OK 200` | Updated an existing CRM lead. |
| `FAILED 401 — ...` | Reached the CRM, secret rejected. The two secrets disagree. |
| `FAILED 5xx — ...` | Reached the CRM, the CRM errored. |
| `FAILED — Exception: ...do not have permission...` | Never left Apps Script. See [the stuck grant](#the-failure-that-cost-us-hours-5-oct-2026). |
| `SKIPPED — CRM_WEBHOOK_SECRET not set` | The Script Property is missing. |
| *(empty)* | Partial lead — no push is attempted. Normal. |

The column is created automatically on first use. **If you see `FAILED` repeating
on new leads, the push is down and the backstop is carrying you.**

---

## The failure that cost us hours (5 Oct 2026)

### What happened

Leads saved to the sheet in full, the team got their emails, and **nothing
reached the CRM for hours**. No error was visible anywhere.

### Root cause

Apps Script had lost its grant for
`https://www.googleapis.com/auth/script.external_request`. `UrlFetchApp.fetch`
threw on every single push, and `postLeadToCRM_`'s `catch` swallowed it. The only
trace was a line in an execution log nobody reads.

It was **a stuck OAuth grant**, not a missing scope. The scope was requestable
the whole time — the existing grant simply would not re-negotiate, which is why
nothing in the editor ever produced a consent prompt.

### The fix that worked

1. Project Settings → tick **"Show 'appsscript.json' manifest file in editor"**.
2. Add the scopes explicitly to `appsscript.json` (see `_ops/appsscript.json`):
   `script.external_request`, `spreadsheets`, `script.send_mail`
   (plus `script.scriptapp` if the project uses triggers).
3. Go to **myaccount.google.com/permissions**, find this script project, and
   **Remove access**. ← **This is the step that actually fixed it.**
4. In the editor: Run → **`forceAuth`**. You now get a full, fresh consent
   screen. Accept it; the list must include **"Connect to an external service"**.
5. **Deploy → Manage deployments → ✏️ → Version: New version.**
6. Verify with `?diag=crm` → `reached: true`.

Steps 1–2 and 5 are all necessary, but on their own they do nothing. Step 3 is
the one that breaks the deadlock.

### Two traps that wasted the most time

**`checkCrmSecret` can never trigger a permission prompt.** It only touches
`PropertiesService` and `Logger`, and neither needs an OAuth scope — so Google
has nothing to ask for and runs it straight through, no matter how unauthorised
the project is. **Use `forceAuth`**, which calls `UrlFetchApp` and forces Google
to either prompt or refuse.

**`curl -L` on a POST to `/exec` returns a Google Drive "Page not found" page.**
The 302 to `script.googleusercontent.com` drops the POST body. The request
usually *did* execute — confirm with `?action=list` rather than believing the
HTML.

### A third trap, from earlier

A previous version defaulted the secret to the literal `'REDACTED_IN_REPO'`.
Pasted live without the Script Property set, the placeholder *became* the secret:
CRM pushes were rejected, and anyone sending `?secret=REDACTED_IN_REPO` could
read the entire lead sheet. It now fails closed — `|| ''` and every secret-gated
path denies on an empty secret. **Never reintroduce a literal fallback.**

---

## Backfilling leads the CRM missed

Safe to re-run; rows already in the CRM are filtered out in SQL before any write.
Backfilled leads keep their real submission time from the sheet, so they sort
into their true position instead of jumping to the top of the Leads list.

```bash
cd /opt/crm
node scripts/sync-website-sheet.js --dry-run              # list what is missing
node scripts/sync-website-sheet.js --since 2026-10-01     # limit the window
node scripts/sync-website-sheet.js                        # ingest
```

The same sweep runs automatically every 10 minutes. The script is for an
immediate catch-up and for seeing what the gap actually was.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `?diag=crm` → `reached: false`, "do not have permission" | OAuth grant stuck or scope ungranted | [The fix that worked](#the-fix-that-worked) |
| `CRM Push` = `FAILED 401` | Secrets disagree | Make Script Property `CRM_WEBHOOK_SECRET` equal the CRM's `WEBSITE_LEAD_SECRET` |
| `CRM Push` = `SKIPPED` | Script Property missing | Project Settings → Script Properties, or run `setCrmSecret()` |
| `?diag=1` shows an old `build` | Deployment pinned to an old version | Manage deployments → **New version** (not a new deployment) |
| Sheet feed returns HTML, not JSON | Deployment not public, or read action missing from the deployed version | Redeploy with access **Anyone** |
| `?action=list` → `crm_secret_not_configured` | Script Property missing | As above |
| `?action=list` → `unauthorized` | Wrong secret | Compare with `WEBSITE_LEAD_SECRET` |
| Leads in CRM labelled "Website form" | `_source` slug not in `SOURCE_LABELS` | Add it in `backend/routes/website-leads.js` |
| Duplicate CRM leads | `external_id` null on old rows | Already handled — resubmits heal duplicates via the natural key |
| CRM never live-refreshes synced leads | — | Already handled — the sweep calls `broadcastDataChanged('leads')` |
| `diag=who` disagrees with the editor | Wrong project or account | Fix the account that `effective_user` names |

---

## Rules worth not relearning

- **Never commit the secret.** It lives in a Script Property and in the CRM's
  `.env`. Both repos are verified at zero occurrences. Rotate it if it ever
  passes through a terminal, a chat or a paste buffer.
- **New version, never new deployment.** A new deployment means a new `/exec`
  URL the website doesn't know about.
- **Never let a secret fall back to a literal.** Fail closed.
- **A failure that only logs is a failure you will not notice.** That is the
  whole lesson of 5 Oct. Record outcomes where the people doing the work are
  already looking — for us, a column in the sheet.
- **Keep one ingest path.** The webhook and the backstop share
  `ingestWebsiteLead()` on purpose.
- `timeout` is not installed on the dev Mac. Commands wrapped in it silently do
  nothing and the test you think you ran did not run.

---

## History

| Commit | Repo | What |
|---|---|---|
| `f4f89b6c` | site | v14 — `forceAuth()`, and the push outcome written to the sheet |
| `aa389d06` | site | `?diag=who` / `whoAmI()` identity diagnostics |
| `95f45e50` | site | Identified the missing external-request scope; reference manifest |
| `e0281243` | site | `?diag=crm` connectivity self-test; log every push result |
| `6257f25` | crm | Sheet-pull backstop, shared `ingestWebsiteLead()`, backfill script |

Verified working 5 Oct 2026, 20:50 IST: lead `dv-crmfix-1791213630` saved with
every field populated and `CRM Push = OK 201`.
