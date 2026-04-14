# claude-configs

My personal Claude Code configuration — custom agents, hooks, CLAUDE.md examples, and patterns I use day-to-day. Feel free to adapt anything here.

## Memory stack

This setup layers three independent memory systems on top of Claude Code. Each solves a different problem:

| Layer | Tool | What it remembers |
|-------|------|-------------------|
| **Cross-session agent memory** | [MemPalace](https://github.com/MemPalace/mempalace) | Who the user is, project context, feedback, preferences — persists across sessions in a diary + knowledge graph |
| **Codebase structure** | [code-review-graph](https://github.com/tirth8205/code-review-graph) | Functions, classes, call relationships, imports — parsed from source with Tree-sitter, queryable as a graph |
| **In-project notes** | Claude Code built-in auto-memory | Markdown files in `~/.claude/projects/*/memory/` — facts Claude saves during sessions |

Since MemPalace captures everything important across sessions, raw `.jsonl` session logs are just disk clutter. `cleanup_history.sh` (run as a `Stop` hook) deletes them after 7 days and removes orphaned subagent directories, keeping `~/.claude/projects/` from growing unbounded. The `memory/` directory is always preserved.

None of these overlap: MemPalace is about the agent knowing the user, code-review-graph is about knowing the codebase, auto-memory is about in-project scratchpad facts.

## What's inside

### `settings/settings.json`

Four hooks that wire the memory stack into Claude Code:

```
UserPromptSubmit → MemPalace session-start
                   Loads relevant memories into context before each message.
                   Without this, MemPalace exists but Claude never reads it.

Stop             → [1] cleanup_history.sh
                       Deletes .jsonl session logs older than 7 days.
                       Safe to do because MemPalace already captured what matters.
                   [2] MemPalace stop hook
                       Claude writes a diary entry + KG facts at end of session.
                       This is how memories actually get saved.
                   (One event, two commands — both run sequentially on session end.)

PreCompact       → MemPalace precompact hook
                   Before Claude Code compresses the context window, important
                   facts are written to MemPalace so they survive compaction.

SessionStart     → code-review-graph check
                   Warns if the codebase graph hasn't been initialized yet.
                   Reminds you to run `code-review-graph build` in new projects.
```

> **Requirements:** MemPalace installed at `~/.mempalace/`, code-review-graph MCP connected. If you don't use these tools, the hook structure is still a useful reference — swap in your own commands.

### `CLAUDE.md`

Project-level instructions that tell Claude to use code-review-graph tools before falling back to file scanning (Grep/Glob/Read). The graph is faster and gives structural context — callers, dependents, test coverage — that file scanning can't.

Copy this into any project's `.claude/settings.json` or root `CLAUDE.md` where you've run `code-review-graph build`.

### `agents/`

Custom subagents for specialized tasks. Drop any of these into `~/.claude/agents/` and Claude Code will route to them automatically.

| Agent | What it does | Model |
|-------|-------------|-------|
| `test-architect` | Test strategy, framework selection, folder structure, phased plan — for greenfield projects | sonnet |
| `api-tester` | Automated REST/gRPC tests — happy path, edge cases, auth flows, DB state verification | sonnet |
| `e2e-tester` | Playwright E2E tests — critical user flows, form interactions, auth | sonnet |
| `coverage-analyst` | Finds gaps in test coverage, prioritizes what to cover next | haiku |
| `test-case-writer` | Human-readable test cases for manual testing in Qase/TestRail | haiku |
| `security-auditor` | API and web app security audit — auth bypasses, injection, broken access control | sonnet |
| `perf-tester` | k6 load tests — concurrent users, queue saturation, SLA validation | sonnet |
| `bug-reporter` | Raw notes → structured bug report ready for Jira/Linear/GitHub Issues | haiku |
| `ai-researcher` | Latest AI news digest — model releases, research papers, industry moves | sonnet |
| `bash-scripter` | Writes and fixes bash/shell scripts — entrypoints, automation, setup scripts | sonnet |
| `docker-debugger` | Diagnoses Docker containers that crash, restart, fail healthchecks | sonnet |
| `release-manager` | npm publish, GitHub releases, changelog, git tags | sonnet |
| `hermes-admin` | Hermes agent config — docker setup, channels, Infisical secrets | sonnet |
| `openclaw-admin` | OpenClaw config — agents, schema, docker-compose overrides | sonnet |
| `mempalace-admin` | MemPalace maintenance — auditing, cleanup, KG health | sonnet |

## How to use

**Agents** — copy any agent file to `~/.claude/agents/`:
```bash
cp agents/bug-reporter.md ~/.claude/agents/
```

Copy what's useful, adjust paths to your setup. [Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)
