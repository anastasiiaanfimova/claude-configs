---
name: claude-tooling
description: >-
  Cross-project Claude tooling audit. Reads MemPalace (all wings) + diary,
  searches for new Claude Code / Anthropic updates via web, compares against
  existing IMPROVEMENTS.md in a GitHub repo, and pushes an updated file with
  status tracking. Fully automatic — no user input needed.
  Trigger: "claude-tooling", "audit Claude setup", "update improvements", "new in Claude Code".
version: 0.1.0
---

# Claude Tooling — Cross-Project Audit

Reads all available signal, compares with existing suggestions, pushes updated `IMPROVEMENTS.md` to GitHub.
Fully autonomous — runs without user input.

## Repo

```
Owner: <YOUR_GITHUB_OWNER>
Repo:  <YOUR_REPO>
File:  IMPROVEMENTS.md
Branch: main
```

## Workflow

### Step 0 — Read existing IMPROVEMENTS.md from GitHub

```bash
gh api repos/<YOUR_GITHUB_OWNER>/<YOUR_REPO>/contents/IMPROVEMENTS.md 2>/dev/null \
  | python3 -c "
import sys, json, base64
try:
    d = json.load(sys.stdin)
    print('SHA:', d['sha'])
    print('---CONTENT---')
    print(base64.b64decode(d['content']).decode())
except: print('NOT_FOUND')
"
```

If `NOT_FOUND` → file doesn't exist yet, will be created fresh.
If found → extract:
1. **SHA** — needed for the PUT request later
2. **Existing items** with their status: `🔄 pending`, `✅ done`, `💡 idea`
3. **"📡 New in Claude"** section — note what was already recorded to avoid duplicates

---

### Step 1 — MemPalace: search across all projects

Run several searches WITHOUT wing filter to capture cross-project signals:

```
mcp__mempalace__mempalace_search("Claude Code pain points slow workflow")
mcp__mempalace__mempalace_search("skill improvement automation missing tool")
mcp__mempalace__mempalace_search("hook permission settings Claude")
mcp__mempalace__mempalace_search("MCP server missing integration")
mcp__mempalace__mempalace_search("manual step repetitive annoying workaround")
```

---

### Step 2 — Diary: cross-project pain points

`mcp__mempalace__mempalace_diary_read` with `agent_name=claude`, `last_n=40`.
Filter to last **14 days**. Note actual date range.

---

### Step 3 — Web: new Claude / Anthropic updates

Use `WebSearch` (run in parallel):
- `"Claude Code" new features 2026`
- `Anthropic Claude API updates changelog 2026`
- `Claude Code MCP servers new 2026`
- `Claude Code hooks settings improvements 2026`

Skip marketing — only concrete features or capabilities.
Cross-check against Step 0 to avoid duplicates.

---

### Step 4 — Synthesize → IMPROVEMENTS.md

```markdown
# Claude Tooling Improvements

_Last updated: YYYY-MM-DD | Diary range: YYYY-MM-DD – YYYY-MM-DD_

---

## 🔄 Pending

| # | Idea | Source | Priority |
|---|---|---|---|

## 🆕 New suggestions

| # | Idea | Source | Priority |
|---|---|---|---|

## 📡 New in Claude Code / Anthropic

- **Feature name** — what it does, why relevant

## ✅ Done

- ...
```

Priority: HIGH = seen in diary ≥2 times or blocks workflow; MEDIUM = mentioned once; LOW = nice-to-have.

Status rules:
- Previous `🔄` → keep as `🔄` unless confirmed resolved → then move to `✅`
- Previous `✅` → always keep in Done, never remove
- New items → start as `🆕`, become `🔄` next run if not done

---

### Step 5 — Push to GitHub

```bash
# Encode content
CONTENT_B64=$(echo "<new file content>" | base64)

# If file existed (has SHA from Step 0):
gh api repos/<YOUR_GITHUB_OWNER>/<YOUR_REPO>/contents/IMPROVEMENTS.md \
  -X PUT \
  -f message="tooling audit $(date +%Y-%m-%d)" \
  -f content="$CONTENT_B64" \
  -f sha="<sha_from_step_0>"

# If file is new (no SHA):
gh api repos/<YOUR_GITHUB_OWNER>/<YOUR_REPO>/contents/IMPROVEMENTS.md \
  -X PUT \
  -f message="tooling audit $(date +%Y-%m-%d) [init]" \
  -f content="$CONTENT_B64"
```

Confirm: response should include `"commit"` key. Print the commit URL.

---

### Step 6 — Write diary entry

`mcp__mempalace__mempalace_diary_write` compact summary. Topic: `claude-tooling`.

---

## Notes

- This skill has NO project scope — reads ALL wings of MemPalace
- If WebSearch is unavailable, skip Step 3 and note it in the file
- Never remove `✅ done` items — they are history
- Keep total file under 50 items — merge similar suggestions if needed
