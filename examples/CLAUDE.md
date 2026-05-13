# Global Claude Instructions — Methodology Example

This document is a **methodology example** for what a global `CLAUDE.md`
can look like for a Claude Code setup that uses a persistent memory
layer. It describes patterns, not a takeable artifact — adapt it to
your stack (your memory MCP, your project layout, your conventions).

## Memory Protocol — required every session

Three memory layers — different roles, not a priority ordering:

| Layer | Tool family | What it holds | When to reach for it |
|------|-----------|------------|--------------------|
| **Memory palace** (`<memory-mcp>`) | MCP tools like `<memory>_search`, `<memory>_diary_*`, `<memory>_add_drawer` | Diary, knowledge graph, structured drawers | Facts, decisions, people, projects |
| **Episodic memory** (`<episodic-mcp>`) | Full-text search over past transcripts | Verbatim text from past conversations | Exact words, errors, commands, URLs |
| **Auto-memory files** | `<auto-memory-dir>/*.md` on disk | Behavioral rules, feedback, project decisions | An index file (e.g. `MEMORY.md`) loads at session start; individual files are read on demand |

### At session start (before the first substantive reply)

Run in parallel:

1. `<memory>_status` — palace overview
2. `<memory>_search` against the conversation topic or project name
3. `<episodic-mcp>__search` for today's date plus topic — picks up
   today's earlier sessions that don't have a diary yet

### During a session

- **Facts, decisions, people, projects** → palace search / knowledge-graph query
- **Exact words, errors, commands, URLs from the past** → episodic search
  immediately (not as a fallback)
- **"In which session did we do X?"** → both in parallel
- **Behavioral rules** — already in context via the MEMORY.md index;
  open individual `.md` files only when the rule's details are needed

### Memory routing

**Principle:** behavioral rules → files (auto-loaded); content → search
(lookup-on-demand). A rule must apply **even when you don't know it
exists** → it needs to be always in context. Content is fetched when
you already know what you're looking for → search is the right tool.

**Writing — where new content goes:**

| What | Where |
|-----|------|
| Cross-project behavioral rule (pacing, naming, general approach) | Global `CLAUDE.md` |
| Project-specific behavioral rule | `<project-memory>/feedback_<rule>.md` |
| Project-specific factual state (statuses, configs) | `<project-memory>/project_<topic>.md` |
| MCP rule / gotcha | Palace `tools/<name>.mcp` drawer |
| Architectural decision | Palace `decisions` room |
| Bug investigation | Palace `bugs` room |
| Skill trace / output | Palace `skills` room |
| Infrastructure (deployment, environments) | Palace `infrastructure` room |
| "Save for later" / discovery | Palace `discovery` room |
| Don't know where | Palace `quick-notes` room |

**Reading — where to look:**

| What I need | Where to look |
|---|---|
| Rule / feedback | Already in context via MEMORY.md — don't search |
| Fact, decision, MCP gotcha | Palace search |
| Exact words / commands / URLs from the past | Episodic search |
| "Which session did X" | Both in parallel |
| Code: relationship graph, callers across files | Code-graph tool (if the project has one) |
| Code: exact name / symbol / function (AST-aware) | AST search tool, when available |

**Checklists before writing memory:**

- Cwd = project, but the discussion is explicitly cross-project → ask
  "for all projects or only X?" before writing
- "Before / after / every time X happens" → automated trigger, not a
  memory entry → use a config-update skill
- "Allow / forbid command", "set env" → config-update skill
- Filed somewhere wrong earlier → offer to migrate

**Naming `feedback_*.md`:**

- The filename describes the **rule** (what to do), not the **subject**
  (where it applies)
- ✓ `feedback_no_estimates_for_other_teams.md`, `feedback_use_skill_templates.md`
- ✗ `feedback_push_<tool>_<shell>.md` — coupled to a skill name (skill
  renamed → file is stale and we won't notice)
- ✗ `feedback_<skill-a>_<skill-b>.md` — coupled to two names
- Subject in the name is fine only when the subject is more stable than
  the rule (TMS / tracker / DB names are stable; skill names are not)

### Diary as compressed summary; episodic as fallback for detail

A diary entry is a compressed AAAK-style summary. If you can't tell
from it what exactly happened (command, error, payload):
→ episodic search with the diary's date plus a keyword.

### After structural changes — file immediately, don't wait for session end

Write a diary entry right after:

- editing global or project `CLAUDE.md`
- editing `settings.json` / `settings.local.json`
- creating or updating files in `<auto-memory-dir>/`
- installing a new hook, skill, or MCP server

### At session end (before close or compact)

- Call `<memory>_diary_write` — record what happened, what was learned,
  what matters
- After `<memory>_diary_write` end with a confirmation phrase like
  `MemPalace saved.` (not "session can be closed")
- Episodic memory syncs via a Stop hook automatically — no manual call

### Confirmation when writing to the memory palace

After every `<memory>_diary_write`, `<memory>_add_drawer`,
`<memory>_update_drawer` — print a confirmation line:

```
{id} — {brief description of what was written or updated}
```

Goal: the user sees the exact address where the content is stored and
can hand it to the next chat for continuity.

### `agent_name` convention for the diary write

`<memory>_diary_write(agent_name=X)` creates wing **`wing_X`** (the
`wing_` prefix is added automatically). **One project, one
`agent_name`** — to avoid fragmenting into parallel wings:

| Context | `agent_name` | Resulting wing |
|---|---|---|
| Global workspace (cross-project sessions) | `claude` | `wing_claude` |
| Per-project session | `<project>` | `wing_<project>` |

**Do not use** combo names (`<base>-<modifier>`, `<base>-<model>`) —
they create fragmented wings that have to be consolidated later.

**Legacy exception pattern.** If the project has a historic wing
without the `wing_` prefix that should remain canonical, the diary tool
will still add the prefix on every write. To preserve the legacy name,
wire a Stop hook that moves freshly-written `wing_<project>` drawers
into the canonical `<project>` wing after each session. If that hook is
removed, the typo-wing reappears on every diary write.

### Proactive documentation sync

When something changes structurally — don't wait for the user to ask.
Update the document that describes it right away.

**In-session trigger:** applied a workaround / hit an unexpected error
/ discovered the documented way doesn't work → in the same response,
write one line about the finding and update the document. Don't defer
to diary.

**Before every diary write** (including mid-session Stop-hook
auto-saves, not only at session end) — run the proactive-sync checklist
and report the result: `Sweep clean.` or `Sweep: <what> → <fixed>.`

### Quick-notes catch-all

When unsure where to file a fact / observation / idea — drop it into a
`quick-notes` room in the palace. Don't burn time classifying mid-task.
A periodic sweep migrates entries to the right rooms or removes stale
ones.

## Project context isolation

Each project is its own context. Never mention or use knowledge from a
different project unless the user explicitly asks for it.

## `~/.claude/` directory structure

- **`skills/<name>/`** — skills (triggered by description match). No
  utility skills with marker prefixes — shared logic lives in `lib/`.
- **`agents/`** — agents (invoked via the Agent tool).
- **`lib/<topic>/`** — shared helpers (scripts, configs, data) consumed
  by skills, agents, hooks. Not triggerable. Example: an anonymization
  toolkit shared between a publish skill and a git pre-commit hook.
- **`scripts/`** — single-file utility wrappers. If a script grows or
  acquires sibling files, it graduates into `lib/<topic>/`.

**Rule:** a helper used by **one** skill → lives inside that skill's
directory. Used by **two or more** → moves to `lib/<topic>/`.

## Code search — tool priority

| What I'm looking for | Which tool |
|---|---|
| Relationship graph, "where is X used" across many files, callers / callees | Code-graph tool (if installed in the project) |
| Exact name / symbol / function, AST-aware lookup | AST CLI (e.g. `probe search`, `probe extract`) — no daemon, parses on demand |
| Code-graph not installed or stale | Fallback to the AST CLI |
| Pure regex without needing structure | `rg` / `grep` |

Both structural tools run **before** Grep/Glob/Read — faster, cheaper
in tokens, give structural context.

## Engineering principles — always applied

Background discipline for every task. Apply when making decisions
(where to put something, how to structure it, in which order).

- **Multi-pass.** Any non-trivial task — three passes: Pass 1 surface
  → Pass 2 connections → Pass 3 "what would a critic say about my
  Pass 1+2?" Finding something in Pass 1 is not a reason to stop.
- **Meta-pass after a large edit cycle.** Once all detailed passes are
  done and many small changes are in — final bird's-eye check: "did we
  break something by aggregate effect while we were buried in
  details?" Catches file coherence, hidden dependencies, drift, lost
  capabilities. Separate from a self-critique pass — that one catches
  gaps in *analysis*; the meta-pass catches regressions in the *final
  state*.
- **Reduce-coupling pass.** Triggers: (1) after root cause, (2) after
  edits across multiple files, (3) when creating a template / capability
  next to existing ones (80%-test: ≥80% overlap → fold-in, not parallel
  files). Propose to the user, don't auto-apply.
- **OOP:** Encapsulation (one thing — one place), Inheritance (shared
  logic into a base), Polymorphism (one interface, many implementations),
  Abstraction (hide details behind a clean interface).
- **Approach checklists:** DRY (no duplication), KISS (the minimum
  needed), SOLID (for code), BDUF (design non-trivial work before
  building), SoC (one responsibility per component).
- **Look at the neighbors.** Starting from zero or unsure of the
  approach → before a plan, survey analogous patterns already in the
  system. The shape you find is the default; deviate only where
  requirements explicitly demand.
- **Pre-read existing memory before creating a new capability.** New
  skill / directory / repo / MCP / settings entry / hook → before
  `Write`/`mkdir`, search memory and re-read the relevant MEMORY.md
  section. Especially for testing / MCP / config infra.
- **Build-order rules:**
  - New project → start with an MVP (one working feature, no full
    machine). Subsequent features land only after the first one's value
    is confirmed.
  - Trying something new (approach, tool, skill, pattern) → PoC first,
    with go/no-go criteria defined before launch. Don't integrate
    until the PoC has a verdict.
  - Order is always: PoC → MVP → iterations.

## Behavior — always

Cross-project behavioral rules. Apply in any project, in any session.

- **Pacing.** Don't push the user. Don't end a reply with "shall we
  continue?", "moving on to X?", "ready for Y?". The user sets the
  pace — finish the task, show the result, stop.
- **Session continuation.** If the user's first message reads like
  "let's continue with...", "continue from #N", "carry on with..." —
  immediately read the latest diary entry and resume context from
  there. Don't re-ask what was being worked on.
- **Git privacy.** Public repositories receive only anonymized data.
  Before commit, scan files for emails / real names / tokens / paths
  with user home directories / private project names / vault names /
  tracker project keys. Anonymize (`<placeholder>`) or ask.
- **Skill naming.** Object-action (`git-refresh`, `task-create`,
  `tc-update`), not action-object. Groups skills by object in listings.
- **Forbidden phrasing.** Maintain a list of phrases to avoid; scan
  drafted text against it before sending.
- **Show git diff before commit.** Before every commit, show the user
  the full diff and wait for approval.
- **No command handoff.** Once a skill has prepared changes, show the
  diff yourself, propose a commit message, wait for approval, then
  execute commit and push **yourself**. Don't hand git commands back to
  the user to copy-paste — you have the tools and the context.
- **Cosmetic fixes — apply immediately, don't ask.** A purely cosmetic
  edit (dead constant, stylistic outlier, dangling reference to a
  removed file, typo, stray whitespace) — fix it in the same response
  where it was noticed. Don't frame as "I found these — should I fix?".
  Test for "cosmetic": if the edit changes behavior, it's not cosmetic
  and warrants discussion.
- **Incidents don't close by themselves.** "It just resolved" is not an
  explanation — it's a sign the cause wasn't found. A vanished problem
  always has a concrete cause: a deploy, a provider fix, a config
  change, a load drop, a manual intervention. Keep digging.
- **Don't rationalize after user feedback.** User picked B with no
  argument ("b", "go with B") — apply B, don't retroactively defend A.
  Explain the choice only if the user explicitly asks "why?".
- **Visibility for long-running processes (>2 min).** Six mechanisms
  designed in during development, not bolted on:
  stdout live ticks + on-disk `_progress.json` + heartbeat lines +
  ETA + failure-tolerant per-item handling + graceful shutdown on
  SIGINT/SIGTERM.
- **MCP signature drift.** On `missing required positional arguments`
  / `Invalid input` — don't trust memory of the schema. Retry with
  alternative parameter names (`content` ↔ `entry`, `wing_id` ↔ `wing`,
  `room_id` ↔ `room`) and both envelopes (`{json: {...}}` vs `{...}`).
  One retry often closes it.
- **Environment facts → verify, not infer.** Before writing a fact
  about the user's environment (OS, tool version, path, hardware,
  process name) into a public artifact (issue, PR, commit message,
  README, public doc) — run one verification command (`sw_vers`,
  `--version`, `uname -a`, `which`, `lsof`). Don't infer from
  formulas (kernel → distro) or from memory. Internal drafting from
  memory is fine; verify before public push.

## Superpowers — Overrides

If a superpowers-style plugin is installed globally, user instructions
take precedence over its skills (most such plugins document this
explicitly). Two overrides worth pinning here:

### Gate skills — scope of application

Superpowers gate skills — typically `brainstorming`,
`test-driven-development`, `systematic-debugging`,
`verification-before-completion`, `subagent-driven-development` —
apply **only** to skills that write or modify code, schemas, or
configs. For action skills (create/update a tracker task, post to a
notebook, run cleanup, run an audit, drive git/config operations) —
no gate: they execute directly.

### Skill invocation — priority

"Invoke skills even at 1% probability" does not override:

1. **Memory protocol** — at session start, always before any skill:
   palace status + palace search + episodic search for today's date, in
   parallel.
2. **Project-specific workflows** — if a project's `CLAUDE.md`
   describes its own process, that takes priority over superpowers
   skills.
