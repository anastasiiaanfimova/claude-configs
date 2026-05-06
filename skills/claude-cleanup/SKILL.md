---
name: claude-cleanup
description: >-
  Audit and clean up the Claude Code setup — find stale skill/agent references,
  duplicate sources of truth, unnecessary MCP wrappers, parasitic directories
  (.cursor/, .agents/), mismatches in the skills publish registry, plus old
  session history and orphan MCP processes.
  Updates the MemPalace architecture drawer at the end.
  Trigger: "cleanup claude", "прибраться в клоде", "аудит конфигурации клода",
  "clean up skills", "что устарело", "check for stale references",
  "наведи порядок в конфигурации", "audit claude setup".
---

# Cleanup Claude Setup

Audits the Claude Code configuration for decay: stale references, duplicate documentation,
unnecessary complexity, orphaned files, accumulated session history, and zombie MCP
processes. Proposes fixes, asks for confirmation, executes.

## Scope

### 1 — Skills and agents: stale internal references

For each skill in `~/.claude/skills/*/SKILL.md` and each agent in `~/.claude/agents/*.md`:

- Grep for file paths that no longer exist on disk (e.g., `mcp-servers/<name>/start.sh`, `commands/`, `scripts/`)
- Check for old skill/tool names that were renamed (scan for names that appear in skill files but not in the filesystem)
- Check if skill `name:` frontmatter matches the directory name
- Flag any `description:` trigger list that mentions a name different from the skill's actual `name:`

Report each issue as: `<file>:<line> — <what's stale>`

### 1a — CLAUDE.md и memory drift

Файлы для скана:
- `~/.claude/CLAUDE.md` (global)
- `~/<active-project>/CLAUDE.md` (project — для активного worktree)
- `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- `~/.claude/projects/<project-slug>/memory/*.md`

Truth sources:
- MCP servers: `jq -r '.mcpServers | keys[]' ~/.claude.json ~/<project>/.mcp.json`
- Skills: `ls ~/.claude/skills/` (без REGISTRY.yml)
- Agents: `ls ~/.claude/agents/` (без `.md`)
- Excludes: `~/.claude/skills/claude-cleanup/scanner_excludes.txt`

Что искать:

**(a) MCP server names** — паттерн `mcp__<server>__<tool>`. Извлечь `<server>`, сравнить с truth list. Flag: `<server>` которого нет в `.mcp.json`.
```bash
grep -ohE "mcp__[a-zA-Z0-9-]+__" $FILES | sed 's/^mcp__//; s/__$//' | sort -u
```

**(b) Skill names** — backtick/slash-обёрнутые hyphenated lowercase имена. Сравнить с truth list (skills + agents + excludes). Flag: остаток.
```bash
grep -ohE "[\`/]([a-z][a-z0-9]+-[a-z][a-z0-9-]+)[\` ]" $FILES | sed 's/^[`\/]//; s/[` ]$//' | sort -u
```

**(c) Agent names** — `subagent_type=<name>` или `<name> agent` или `agent: <name>`. Сравнить с `~/.claude/agents/`.

**(d) File paths** — все `~/.claude/...`, `~/<project>/...`, `/Users/<user>/...`. Каждый — `test -e`.
```bash
grep -ohE "(~/\.claude/[a-zA-Z0-9_./-]+|~/<project>/[a-zA-Z0-9_./-]+|/Users/<user>/[a-zA-Z0-9_./-]+)" $FILES | sort -u
```

Report:
```
## CLAUDE.md drift (N issues)
- ~/.claude/CLAUDE.md:42 — упомянут `mcp__old-server__foo` — server не в .mcp.json
- memory/feedback_X.md:13 — путь `~/.claude/mcp-servers/` не существует
```

**Anti-patterns:**
- Не флагать historical контекст («раньше было X, теперь Y», «deprecated», «renamed to»). Heuristic: рядом с упоминанием есть «было»/«старое»/«deprecated»/«renamed»/«убрано» — пропустить.
- False positive в `scanner_excludes.txt` → добавить туда же, не править regex.

---

### 2 — Duplicate sources of truth

Search for files that describe the same information already covered by canonical sources:

Canonical sources (never flag these):
- `~/.claude/skills/<name>/SKILL.md` — skill documentation
- `~/.claude/agents/<name>.md` — agent documentation
- `<project>/CLAUDE.md` — project instructions
- `claude-configs` GitHub repo README — public overview
- MemPalace wing_claude/config drawer — architecture snapshot

**Flag** any of these:
- `docs/` directories under `~/Claude/` or project roots that contain skill/agent/MCP overviews
- Standalone README files that duplicate CLAUDE.md content (check overlap > 50%)
- Multiple files describing the same MCP setup

For each flagged file: show which canonical source already covers the topic, and recommend deleting the duplicate.

### 3 — MCP config wrappers

For each project `.mcp.json` (`~/<project>/.mcp.json`, `~/<project>/.mcp.json`, `~/Claude/**/.mcp.json`):

For entries using a local `start.sh` or wrapper script, read the script and check:
- Does the script only rename an env var? → recommend renaming in Infisical instead
- Does the script only set a static URL/host? → recommend moving to `env:{}` block in `.mcp.json`
- Does the script pass a secret as a CLI `--flag`? → check if `sh -c "..."` inline in args would work instead

If all a wrapper does is call an upstream package with no logic → it can be removed.

### 4 — Parasitic directories

Search project roots for directories that shouldn't exist:

```bash
find ~/<project> ~/<project> ~/Claude -maxdepth 3 -type d \( -name ".cursor" -o -name ".agents" \) 2>/dev/null
```

Flag each: explain why `.claude/` is canonical and these are redundant.

Also check `~/.claude/mcp-servers/` — list what's there and flag any that are just thin wrappers (content is only `npx` or `exec` with no logic).

### 5 — Skills publish registry

Read `~/.claude/skills/REGISTRY.yml` (source of truth).

**Check 1 — REGISTRY completeness:**
- Every directory in `~/.claude/skills/` (excluding `REGISTRY.yml`) must appear in exactly one section of REGISTRY.yml
- Every entry in skill sections (`claude-configs:`, `qa-playbook:`, `local:`) must correspond to an existing directory on disk
- Every entry in `claude-configs-agents:` and `qa-playbook-agents:` must correspond to an existing file in `~/.claude/agents/`
- Every file in `~/.claude/agents/` must appear in either `claude-configs-agents:` or `qa-playbook-agents:`
- Auto-generated files (`.md` files dropped by code-review-graph directly into `~/.claude/skills/`) are exempt — skip files, only check directories
- Flag: directories not in REGISTRY ("unregistered skill"), REGISTRY entries with no directory ("stale entry")

**Check 2 — SKILL.md name frontmatter:**
- Skill `name:` frontmatter in each SKILL.md should match the directory name
- Flag: mismatches

Note: `claude-config-push` and `qa-playbook-push` no longer have their own hardcoded skill lists — they read from REGISTRY.yml directly. Do NOT check for list consistency in those files.

### 6 — Session history and orphan MCP processes

Two cleanup scripts live in `~/.claude/scripts/`:

- `history-cleanup.sh` — trims `hook-approvals.log` to 500 lines, deletes `.jsonl` session logs older than 30 days, removes orphaned subagent dirs.
- `kill-orphan-mcp.sh` — finds MCP server processes older than 1h (code-review-graph, mempalace, sentry, asana, grafana, gitlab, postgres, chrome-devtools, episodic-memory, infisical run wrappers) that survived their parent session.

These run in Step 4 of the workflow below.

---

## Workflow

### Step 1 — Run the audit

Execute checks 1, 1a, 2–5 above. Collect all findings.

### Step 2 — Present findings

Group by category. For each issue show:
- What was found
- Where it is (file:line if applicable)
- Recommended fix (delete / update / rename)

Example format:
```
## Stale references (3 issues)
- ~/.claude/skills/some-skill/SKILL.md:52 — path ~/.claude/skills/old-name/ no longer exists

## Duplicate sources (1 issue)
- ~/Claude/docs/mcp.md — covers MCP setup already in <project>/CLAUDE.md and MemPalace

## Parasitic directories (0 issues)
— None found ✓
```

If nothing found in a category → `— None found ✓`

**Then ask:** "Всё выглядит правильно? Хочешь что-то добавить или пропустить?"
Wait for confirmation before making any changes.

### Step 3 — Execute confirmed fixes

Apply each fix the user confirmed:
- Delete files/directories with `rm -rf`
- Edit SKILL.md/agent files to remove stale references
- Update README.md rows
- Update .mcp.json entries

For each change: print what was done (one line per action).

### Step 4 — System cleanup (history + orphan MCPs)

Run the two cleanup scripts. Order: history first (it's silent), then orphan MCPs (interactive).

**4a — History cleanup**

```bash
bash ~/.claude/scripts/history-cleanup.sh
```

Report what was trimmed (log file size before/after, number of `.jsonl` removed).

**4b — Orphan MCP processes (dry-run → ask → kill)**

First run dry-run to see what's there:

```bash
bash ~/.claude/scripts/kill-orphan-mcp.sh
```

If output says `No orphan MCP processes found` → done, move to Step 5.

If orphans are listed: show the list to the user with sizes/ages, then ask:
"Убить эти orphan MCP-процессы?"

On confirmation, run with `--kill`:

```bash
bash ~/.claude/scripts/kill-orphan-mcp.sh --kill
```

If some processes survive (output says "Killed most. N still alive"), ask:
"Force-kill оставшиеся (SIGKILL)?" → on yes, run with `--kill -9`.

### Step 5 — Update MemPalace

After fixes are applied, update the architecture drawer in MemPalace:
1. Delete the existing `wing_claude / config` drawer (search for it first with `mempalace_search`)
2. Save a fresh drawer with the current state:
   - Current skill list with publish targets
   - Current MCP config summary per project
   - Any notable structural decisions made today

Use `mcp__mempalace__mempalace_diary_write` to log what was cleaned.

---

## Notes

- Read files before grepping — don't rely on memory about what's there
- Don't flag things that are intentionally different (e.g., a `docs/` file that's a WIP the user just created)
- When in doubt about whether something is a duplicate, ask rather than auto-flag
- `settings.local.json` is never stale — it's machine-local by design
- `~/.claude/skills/REGISTRY.yml` is the single source of truth for publish targets — README.md and push skills derive from it
- When adding a new skill: add it to REGISTRY.yml first, then update README.md to match
