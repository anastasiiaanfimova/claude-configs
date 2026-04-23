---
name: tc-gap
description: >-
  Gap analysis: compares existing Testiny TCs against available signal sources
  per project — analytics events (Web), backend handlers (Back), admin
  operations (Admin). Produces a prioritized gap report and updates a Notion
  page. Trigger: "tc-gap", "gap analysis", "what's not covered".
version: 0.2.0
---

# TC Gap — Coverage Gap Analysis

Find what's not covered in Testiny. Signal sources differ per project:

| Project | Signal source |
|---|---|
| Web (id=1) | Analytics platform named events |
| Back (id=2) | Backend handlers (`/backend/app/handlers/`) |
| Admin (id=3) | Admin panel pages and their operations (`/admin/src`) |

Run automatically when invoked — no clarifying questions.

## Workflow

### Step 0 — Read existing Notion gap report page

Before doing anything else, fetch the current gap report page from Notion:
**Page ID:** `<YOUR_NOTION_PAGE_ID>`

Use `mcp__notion__notion-fetch` with that ID.

Extract and carry into the analysis:
1. **Date of last run** — compare to today to understand staleness
2. **Anomalies / questions** — anything flagged ⚠️ in previous report → add to "re-check" list
3. **Section "📌 Notes"** — if present, copy verbatim: it's written manually and must NOT be overwritten

---

### Step 1 — Fetch all TCs from Testiny (parallel)

```bash
for pid in 1 2 3; do
  curl -s "https://app.testiny.io/api/v1/testcase?project_id=${pid}&limit=500" \
    -H "X-Api-Key: <YOUR_TESTINY_API_KEY>"
done
```

Build flat lists per project. Count totals.

---

### Step 2 — Collect signals per project

#### Web → Analytics events

1. `mcp__Amplitude__get_context` → get projectId for Production
2. `mcp__Amplitude__search` with queries for known event families
3. Filter out platform/internal events (`[Guides-Surveys]`, `[Amplitude]`, `$` prefix)
4. Result: list of named product events

#### Back → Backend handlers

Read handler files to discover what's implemented:

```bash
find /path/to/project/backend/app/handlers -name "*.py" | sort
```

Group into functional areas: billing, generation, assets, auth, webhooks.

If code is unavailable, use your known handler map as fallback:

| Area | Handlers |
|---|---|
| Billing — success | payment provider webhooks (stripe, mollie, etc.) |
| Billing — failure | payment error, webhook retry, duplicate webhook |
| Billing — auto-topup | low balance trigger |
| Generation | task create, task fail/rescue, credits refund |
| Assets | upload, batch upload, format validation, preview |
| Auth | OAuth, email registration |

#### Admin → Admin panel operations

Read admin source to discover pages:

```bash
find /path/to/project/admin/src -name "*.tsx" -path "*/pages/*" | sort
```

Map each page to its operations (search, create, edit, delete, promote, etc.).

---

### Step 3 — Cross-reference per project

**Web:** For each analytics event, check if any Web TC title contains all words from the event name (case-insensitive).

**Back:** For each handler/area, check if any Back TC title contains keywords from that area.

**Admin:** For each page+operation pair, check if any Admin TC title covers it.

Mark each: ✅ Covered / ❌ Gap

---

### Step 4 — Output gap report

```
## TC Gap Report
Date: YYYY-MM-DD
Testiny: N total TC (Web: X | Back: Y | Admin: Z)

### Web — Analytics events (M checked, P% covered)
### Back — Backend handlers (M areas, P% covered)
### Admin — Panel operations (M ops, P% covered)

Each section:
  ❌ Gaps: | Signal | Priority | Suggested TC title |
  ✅ Covered (top 5): | Signal | TC |
```

Priority: HIGH = payment/auth/core path or high volume; MEDIUM = feature with no coverage; LOW = edge case.

---

### Step 5 — Update Notion page

After producing the report, update the gap page in Notion:
**Page ID:** `<YOUR_NOTION_PAGE_ID>`

Use `mcp__notion__notion-update-page` with `command: replace_content`.

Page structure — always in this order:
```
[Callout: run date + coverage by project]
[Auto-report: three sections Web / Back / Admin]
---
## 📌 Notes
[Content from Step 0 — copied verbatim if it existed. Never overwrite.]
```

Rules:
- Callout and three report sections → always replaced with fresh data
- `## 📌 Notes` → always preserved, never touched

---

### Step 6 (optional) — Create TCs for top gaps

If user says "create them":
- Apply tc-create workflow for each (top 5 by priority)
- Status: `GUESS` by default
- Folder per project: see `../tc-create/references/testiny-api.md`

## Notes

- Web match is fuzzy word-bag (known limitation: "Post Scheduled" can false-match "Post Published: publishType=scheduled")
- When in doubt about a match, mark as ❌
- Do not ask the user for scope — run all three projects
