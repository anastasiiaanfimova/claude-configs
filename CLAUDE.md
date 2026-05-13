# CLAUDE.md — claude-configs

This is the **public clone** of `github.com/anastasiiaanfimova/claude-configs`.
A reference snapshot of one Claude Code setup — concrete configs (settings,
hooks, agents) plus methodology spin-offs (`examples/CLAUDE.md`, `skills/`)
that describe transferable patterns.

This is **not** where the live working skills live (those are in
`~/.claude/skills/`). This is the published artifact, kept around for
visibility and as a reference for other Claude Code users.

## Two kinds of content

claude-configs sits in between qa-playbook (purely methodology) and a
classic dotfiles repo (purely concrete files). It carries both:

| Concrete reference | Methodology |
|---|---|
| `settings/settings.json` | `skills/<name>/SKILL.md` |
| `hooks/pre-commit` | `examples/CLAUDE.md` (global-instructions patterns) |
| `agents/*.md` | |

The split mirrors how each kind of content gets reused. Concrete files
are copy-paste references — someone reads `settings.json` to see what
hooks I wire and adapts the file to their stack. Methodology is process
knowledge — someone reads `skills/claude-cleanup/SKILL.md` to learn
what kinds of decay an agent setup accumulates and how to audit it.

## The methodology pattern (read first if editing skills)

The skills under `skills/` are **methodology-only**, not blueprints.
They describe processes, decision frameworks, anti-patterns — things
that survive moving to a different agent CLI, a different MCP stack, a
different memory tool. The same rule applies to `examples/CLAUDE.md` —
it's pattern documentation, not a copy-paste config. No `<placeholder>`
syntax left for tools, no MCP calls, no specific paths.

**User-change test for skills:** every claim in a `SKILL.md` should
still apply if the reader uses a different agent stack — different MCP
servers, different memory layer, different cleanup tooling. If
something fails the test (relies on a specific tool's API or a specific
path), it belongs in the local working skill (`~/.claude/skills/<name>/`),
not here.

This is different from the qa-playbook **job-change test** (TMS swap,
tracker swap). For claude-configs, the analog is "stack-swap": Cursor,
Aider, a different CLI — methodology should survive.

History of how this pattern was adopted lives in the project's
MemPalace decisions wing (alongside qa-playbook's same migration).
Migration date: 2026-05-09.

## Concrete files: keep accurate, don't methodologize

`settings/settings.json`, `hooks/pre-commit`, `agents/*.md` are concrete
reference. They're useful precisely because they're files someone can
read and adapt. Don't try to convert them to "methodology of writing
hooks" — the file IS the documentation. If a hook changes locally,
update the file here too (manually, no automation).

## Editing workflow

1. Decide: methodology or concrete?
2. **Methodology change** — edit `skills/<name>/SKILL.md` or
   `examples/CLAUDE.md` directly
3. **Concrete change** — edit the relevant file (`settings/`, `hooks/`,
   `agents/`)
4. `git add . && git diff --staged` to review
5. `git commit -m "<msg>"` and `git push`

No automation, no scripts driving things — manual is the right level
for how often this changes.

## Editing principles for skills

- The methodology must read clean to a stranger using a different agent
  stack
- Every "rule" should be defensible without referring to a specific
  tool ("never call `mcp__<server>__<tool>`" is not methodology — "never
  delete an architecture snapshot during cleanup" is)
- Examples generic — `<agent>` over `Claude Code`, `<config-file>` over
  specific paths, `<server>` over real MCP names
- When in doubt, the example illustrates the *shape* of a problem, not
  the specific tool that has it

## Don't do here

- Don't edit local working skills from this directory — `~/.claude/skills/`
  is a different audience and a different file
- Don't run any of the working skills here (`/claude-audit`,
  `/claude-cleanup`, etc.) — they expect the local stack and will fail
  or produce wrong output

## When you'll come back here

- Major methodology change in a working skill (rewrote
  `claude-cleanup`'s audit category list → consider updating the
  published variant)
- A concrete file changed locally (added a hook to settings.json) and
  the public reference should reflect it
- New methodology worth sharing (cross-cutting principle that's worth
  its own SKILL.md)
- Bug, typo, or outdated reference a reader pointed out

## Maintenance frequency

Concrete files (settings, hooks, agents) change when the local setup
genuinely changes — usually monthly at most. Methodology skills change
when the underlying *process* genuinely evolves — rarer.

This is a visibility artifact, not a kept-current toolkit. If many
sessions go by without updates, that's fine.

## Related public repo

`~/Claude/qa-playbook/` — methodology snapshots of QA skills. Adopted
the same methodology-only pattern first (2026-05-09 evening); this repo
followed by analogy.
