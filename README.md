# claude-configs

My personal Claude Code configuration — custom agents, hooks, CLAUDE.md examples, and patterns I use day-to-day. Feel free to adapt anything here.

## What's inside

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

### `CLAUDE.md`

Project-level instructions for Claude Code using the [code-review-graph](https://github.com/tirth8205/code-review-graph) MCP. Shows how to:
- Direct Claude to use graph tools before file scanning
- Structure a tool reference table
- Define a workflow for code review and impact analysis

Adapt the tool names to whatever MCPs you use — the pattern works for any MCP-heavy setup.

### `settings/settings.json`

Claude Code hooks wired up to [MemPalace](https://github.com/MemPalace/mempalace) (persistent AI memory) and code-review-graph. Shows usage of:
- `UserPromptSubmit` — runs before Claude processes each message
- `Stop` — runs when a session ends (cleanup + diary write)
- `PreCompact` — runs before context compaction
- `SessionStart` — checks if code-review-graph is initialized in the current project

> **Note:** these hooks require MemPalace installed at `~/.mempalace`. If you don't use MemPalace, the hook structure is still a useful reference — swap in your own commands.

### `cleanup_history.sh`

Auto-deletes Claude Code session `.jsonl` files older than 7 days and removes orphaned subagent directories. Designed to run as a `Stop` hook. Keeps the `memory/` directory intact.

If you use MemPalace, it persists everything important (diary, KG, agent memory) across sessions — so the raw `.jsonl` session logs are just disk clutter. This script keeps the `~/.claude/projects/` directory from growing unbounded.

## How to use

**Agents** — copy any agent file to `~/.claude/agents/`:
```bash
cp agents/bug-reporter.md ~/.claude/agents/
```

**Everything else** — copy what's useful, adjust paths and tool names to your setup.

Claude Code hooks documentation: https://docs.anthropic.com/en/docs/claude-code/hooks
