---
name: qa-tooling
description: >-
  Tooling audit for QA. Looks at recent work via MemPalace diary, identifies
  pain points and manual steps, and suggests new skills, agents, automations,
  or workflow improvements. NOT a session summary — focused on "what should we
  build next to work more comfortably?"
  Trigger: "qa-tooling", "what to improve in tooling", "suggest new skills".
version: 0.1.0
---

# QA Tooling — Tooling Audit

Look at recent work and answer: **what should we build or improve to make QA easier?**

Output: prioritized suggestions for new skills, agent improvements, MCP tools, automations, workflow changes.

## Workflow

### Step 1 — Read recent diary

`mcp__mempalace__mempalace_diary_read` with `last_n=30`.

Filter entries to last **14 days** from today.
Note the actual date range covered (earliest → latest) — include in report header.

If fewer than 3 entries remain → say so explicitly.

Extract recurring signals:
- What required manual steps that felt repetitive?
- What data was missing or hard to get?
- What produced unexpected/wrong output (false positives, wrong format)?
- What took multiple tries to get right?
- What was skipped because "too much work"?

### Step 2 — Inventory existing skills

```bash
ls ~/.claude/skills/
```

For each skill, note: what it does and any known limitations seen in diary.

### Step 3 — Synthesize suggestions

For each pain point from Step 1, map to a concrete suggestion:

| Pain point type | Possible solution |
|---|---|
| Repeated manual lookup | New skill or reference file |
| Tool produced wrong output | Improvement to existing skill |
| Missing data source | New MCP integration or API reference |
| Multi-step flow done manually | New agent or skill automation |
| Naming/format inconsistency | Update memory rule or skill guideline |

### Step 4 — Output

```
## QA Tooling Audit — YYYY-MM-DD
Diary range: YYYY-MM-DD – YYYY-MM-DD (N entries)

### 🔧 Build / improve

HIGH — solves real pain:
1. [Skill/tool name] — [what it does, why needed]
   Signal from diary: "[quote or pattern]"

MEDIUM — would be convenient:
...

LOW / idea for later:
...

### ✅ What works well (keep as-is)
### ⚠️ Known limitations (not critical)
```

### Step 5 — Write diary entry

`mcp__mempalace__mempalace_diary_write` compact summary. Topic: `qa-tooling`.

## Rules

- Base every suggestion on a concrete signal from diary — no speculative "nice to have"
- One suggestion per pain point — don't bundle unrelated improvements
- Don't reproduce what tc-gap does (coverage analysis) — that's a separate skill
- Keep total output under 15 items
