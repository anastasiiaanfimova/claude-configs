# CLAUDE.md — claude-configs

This is the **public clone** of `github.com/anastasiiaanfimova/claude-configs`.
A methodology snapshot of one Claude Code setup — patterns for skills,
agents, settings, hooks, and global instructions. Read it for the shape
of the setup; adapt the bits that fit your stack.

This is **not** where the live working skills live (those are in
`~/.claude/skills/`). This is the published artifact, kept around for
visibility and as a reference for other Claude Code users.

## Methodology-only

Everything here is written as methodology — patterns and decision
frameworks that survive moving to a different agent CLI, a different
MCP stack, a different memory tool. Concrete artifacts (`settings/`,
`hooks/`, `agents/`, `templates/`, `lib/`) are kept as illustrative
*examples* with placeholders for paths, scopes, and project-specific
names — not as copy-paste-and-run files.

**Stack-swap test:** every claim in any file here should still apply if
the reader uses a different agent stack — different MCP servers,
different memory layer, different cleanup tooling. If something fails
the test (relies on a specific tool's API or a specific path), it
belongs in the local working skill (`~/.claude/skills/<name>/`), not
here.

This mirrors the **job-change test** used in
[qa-playbook](https://github.com/anastasiiaanfimova/qa-playbook) (TMS
swap, tracker swap). For claude-configs, the analog is "stack-swap":
Cursor, Aider, a different CLI — methodology should survive.

## What's in the repo

| Path | What it is |
|---|---|
| `examples/CLAUDE.md` | Methodology example for a global Claude Code instructions file — memory protocol, behavior rules, engineering principles |
| `skills/<name>/SKILL.md` | Methodology essays for individual skills (`workspace-setup`, `claude-cleanup`, `claude-audit`, `history-cleanup`, `tooling-update`) |
| `agents/<name>.md` | Agent example files — frontmatter + prompt body, with placeholders for any project-specific paths or scopes |
| `settings/` | Illustrative `settings.json` example showing hook event categories and the shape of a Claude Code config |
| `hooks/pre-commit` | Illustrative global pre-commit hook for blocking private names from leaking to public repos |
| `templates/` | Per-language CLAUDE.md skeletons with placeholders |
| `lib/push-mirror/` | Reference toolkit for an anonymizing publish-mirror pattern (README + example forbidden-list + example replacement rules) |

## Editing workflow

1. Edit the relevant file directly. Methodology-style — placeholders
   over real names, patterns over specific implementations.
2. `git add . && git diff --staged` to review.
3. `git commit -m "<msg>"` and `git push`.

No automation, no scripts driving things — manual is the right level
for how often this changes.

## Editing principles

- Reads clean to a stranger using a different agent stack
- Every "rule" should be defensible without referring to a specific
  tool ("never call `mcp__<server>__<tool>`" is not methodology — "never
  delete an architecture snapshot during cleanup" is)
- Examples use placeholders — `<agent>` over `Claude Code`,
  `<config-file>` over specific paths, `<server>` over real MCP names,
  `<scope>` over real npm scope
- When in doubt, the example illustrates the *shape* of a problem, not
  the specific tool that has it
- If you need to refer to a real tool or product to make a point, use a
  full link (`[MemPalace](url)`) — names without context drift

## Don't do here

- Don't edit local working skills from this directory — `~/.claude/skills/`
  is a different audience and a different file
- Don't run any of the working skills here (`/claude-audit`,
  `/claude-cleanup`, etc.) — they expect the local stack and will fail
  or produce wrong output
- Don't bring in real personal data, real project names, or
  organization-private identifiers; anonymization is by design

## When you'll come back here

- Major methodology change in a working skill (rewrote
  `claude-cleanup`'s audit category list → consider updating the
  published variant)
- New methodology worth sharing (cross-cutting principle that's worth
  its own SKILL.md, or a new agent pattern)
- Bug, typo, or outdated reference a reader pointed out

## Maintenance frequency

Methodology changes when the underlying *process* genuinely evolves —
rarely. Example files change when the patterns themselves shift, not
every time the author's local config gets a new line.

This is a visibility artifact, not a kept-current toolkit. If many
sessions go by without updates, that's fine.

## Related public repo

[`qa-playbook`](https://github.com/anastasiiaanfimova/qa-playbook) —
methodology snapshots of QA skills. Adopted the methodology-only
pattern first (2026-05-09 evening); this repo followed by analogy and
finished the migration over the following days.
