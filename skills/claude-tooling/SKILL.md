---
name: claude-tooling
description: >-
  Cross-project Claude tooling audit. Reads MemPalace (all wings) + diary,
  searches for new Claude Code / Anthropic updates via web, compares against
  existing local IMPROVEMENTS.md, and writes updated file with status tracking.
  Fully automatic — no user input needed.
  Trigger: "claude-tooling", "что улучшить в Claude", "аудит клода",
  "новое в Claude Code", "обнови improvements".
version: 0.1.0
---

# Claude Tooling — Cross-Project Audit

Reads all available signal, compares with existing suggestions, writes updated `IMPROVEMENTS.md` locally.
Fully autonomous — runs without user input.

## File

```
Local: ~/Claude/digests/IMPROVEMENTS.md
```

## Workflow

### Step 0 — Read existing IMPROVEMENTS.md

```bash
cat ~/Claude/digests/IMPROVEMENTS.md 2>/dev/null || echo "NOT_FOUND"
```

If `NOT_FOUND` → file doesn't exist yet, will be created fresh.
If found → extract:
1. **Existing items** with their status: `🔄 pending`, `✅ done`, `💡 idea`
2. **"📡 Новое в Claude"** section — note what was already recorded to avoid duplicates

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

Extract: recurring themes, mentioned gaps, workarounds that suggest missing automation.

---

### Step 2 — Diary: cross-project pain points

`mcp__mempalace__mempalace_diary_read` with `agent_name=claude`, `last_n=40`.

Filter to last **14 days**. Note actual date range (earliest → latest).

Extract:
- Anything that required multiple retries or workarounds
- Missing data that slowed down a task
- Tools/skills that were suggested but not yet built
- Errors or unexpected outputs from existing skills/hooks

---

### Step 3 — Web: new Claude / Anthropic updates

Use `WebSearch` with these queries (run in parallel):
- `"Claude Code" new features 2026`
- `Anthropic Claude API updates changelog 2026`
- `Claude Code MCP servers new 2026`
- `Claude Code hooks settings improvements 2026`

For each result, extract: feature name, what it does, why it might help.
Skip marketing fluff — only concrete features or capabilities.
Cross-check against "📡 Новое в Claude" section from Step 0 to avoid duplicates.

---

### Step 4 — Synthesize

Build the updated `IMPROVEMENTS.md` with this structure:

```markdown
# Claude Tooling Improvements

_Last updated: YYYY-MM-DD | Diary range: YYYY-MM-DD – YYYY-MM-DD_

---

## 🔄 Pending — не сделано

Items from previous file that are still relevant.
Keep original text. Add a note if diary confirms it's still a pain.

| # | Идея | Источник | Приоритет |
|---|---|---|---|
| 1 | ... | diary / MemPalace / web | HIGH |

---

## 🆕 Новые предложения

New items from this audit not seen in previous file.

| # | Идея | Источник | Приоритет |
|---|---|---|---|
| 1 | ... | ... | ... |

---

## 📡 Новое в Claude Code / Anthropic

Recent features or updates worth knowing about.
Skip if already in previous file.

- **Feature name** — what it does, why relevant
- ...

---

## ✅ Сделано

Items from previous file marked as done. Keep for history.

- ...
```

**Priority rules:**
- HIGH: seen in diary ≥2 times, OR blocks regular workflow
- MEDIUM: mentioned once, OR useful but not urgent
- LOW: nice-to-have, speculative

**Status rules:**
- Previous `🔄` item: keep as `🔄` unless diary/MemPalace confirms it's resolved → then move to `✅`
- Previous `✅` item: always keep in the Done section, never remove
- New items from this audit: start as `🆕`, will become `🔄` next run if not done

---

### Step 5 — Write to local file

Use the Write tool to overwrite `~/Claude/digests/IMPROVEMENTS.md` with the new content.

Confirm: print "Written to ~/Claude/digests/IMPROVEMENTS.md".

---

### Step 6 — Write diary entry

`mcp__mempalace__mempalace_diary_write` with compact AAAK summary:
- Date range analysed
- Count of new suggestions / updated pending / new Claude features found

Topic: `claude-tooling`

---

## Notes

- This skill has NO project scope — it reads ALL wings of MemPalace
- Do not filter by <project> or any other project when searching MemPalace
- If WebSearch is unavailable, skip Step 3 and note it in the file
- Never remove `✅ done` items from the file — they are history
- Never remove `🔄 pending` items unless diary confirms they are resolved
- Keep total file under 50 items — if more, merge similar suggestions
