---
name: cleanup-claude
description: >-
  Audit and clean up the Claude Code setup — find stale skill/agent references,
  duplicate sources of truth, unnecessary MCP wrappers, parasitic directories
  (.cursor/, .agents/), and mismatches in the skills publish registry.
  Updates the MemPalace architecture drawer at the end.
  Trigger: "cleanup claude", "прибраться в клоде", "аудит конфигурации клода",
  "clean up skills", "что устарело", "check for stale references",
  "наведи порядок в конфигурации", "audit claude setup".
version: 0.1.0
---

# Cleanup Claude Setup

Audits the Claude Code configuration for decay: stale references, duplicate documentation,
unnecessary complexity, and orphaned files. Proposes fixes, asks for confirmation, executes.

## Scope

### 1 — Skills and agents: stale internal references

For each skill in `~/.claude/skills/*/SKILL.md` and each agent in `~/.claude/agents/*.md`:

- Grep for file paths that no longer exist on disk (e.g., `mcp-servers/<name>/start.sh`, `commands/`, `scripts/`)
- Check for old skill/tool names that were renamed (scan for names that appear in skill files but not in the filesystem)
- Check if skill `name:` frontmatter matches the directory name
- Flag any `description:` trigger list that mentions a name different from the skill's actual `name:`

Report each issue as: `<file>:<line> — <what's stale>`

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

Read `~/.claude/skills/README.md`. Cross-check:
- Every directory in `~/.claude/skills/` should have a row in the README
- Every row in README should correspond to an existing directory
- Skill name in README should match `name:` frontmatter in the SKILL.md

Flag: missing rows, stale rows, name mismatches.

Also verify `push-claude-config` PUBLIC_SKILLS list matches the README's "Published to claude-configs" section, and same for `push-qa-playbook` PUBLIC_QA_SKILLS.

---

## Workflow

### Step 1 — Run the audit

Execute checks 1–5 above. Collect all findings.

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

### Step 4 — Update MemPalace

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
- `~/.claude/skills/README.md` is a publish registry, not documentation — different purpose from skill SKILL.md files
