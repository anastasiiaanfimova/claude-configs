# claude-configs

My personal Claude Code configuration — custom agents, hooks, CLAUDE.md examples, and patterns I use day-to-day. Feel free to adapt anything here.

## Memory stack

This setup layers three independent memory systems on top of Claude Code. Each solves a different problem:

| Layer | Tool | What it remembers |
|-------|------|-------------------|
| **Cross-session agent memory** | [MemPalace](https://github.com/MemPalace/mempalace) | Who the user is, project context, feedback, preferences — persists across sessions in a diary + knowledge graph |
| **Codebase structure** | [code-review-graph](https://github.com/tirth8205/code-review-graph) | Functions, classes, call relationships, imports — parsed from source with Tree-sitter, queryable as a graph |
| **In-project notes** | Claude Code built-in auto-memory | Markdown files in `~/.claude/projects/*/memory/` — facts Claude saves during sessions |

None of these overlap: MemPalace is about the agent knowing the user, code-review-graph is about knowing the codebase, auto-memory is about in-project scratchpad facts.

Since MemPalace captures everything important across sessions, raw `.jsonl` session logs are just disk clutter. `cleanup_history.sh` (run as a `Stop` hook) deletes them after 7 days and removes orphaned subagent directories, keeping `~/.claude/projects/` from growing unbounded. The `memory/` directory is always preserved.

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

Copy this into a project's root `CLAUDE.md` or `.claude/CLAUDE.md` after running `code-review-graph build` in that project.

### `agents/`

Custom subagents for specialized tasks. Drop any of these into `~/.claude/agents/` and Claude Code will route to them automatically.

#### QA toolkit

Built for a QA role at an AI project — backend + web, LLM wrapper for photo/video generation, async job pipelines. Three agents are fully custom; the rest are standard Claude Code built-in agents stored here for version control.

| Agent | What it does | Model | Origin |
|-------|-------------|-------|--------|
| `qa-researcher` | Digest of new QA tools and testing practices — LLM eval, API testing, async pipelines, load testing. | haiku | custom |
| `test-architect` | Test strategy from scratch — framework selection, folder structure, phased plan. Specialized for async AI/LLM pipelines and SaaS billing flows. | sonnet | custom |
| `api-tester` | Automated REST/gRPC tests — happy path, edge cases, auth flows, DB state verification. | sonnet | built-in |
| `e2e-tester` | Playwright E2E tests — critical user flows, form interactions, auth. | sonnet | built-in |
| `test-case-writer` | Test cases as checklists with inline `//` comments — checks *what* to verify and *why*, not how to navigate the UI. Includes ready-made scenario blocks for async AI generation (submit→poll→result, timeouts, provider errors) and SaaS billing limits. | haiku | custom |
| `coverage-analyst` | Finds gaps in test coverage, prioritizes what to cover next. | haiku | built-in |
| `security-auditor` | API and web app security audit — auth bypasses, injection, broken access control. | sonnet | built-in |
| `perf-tester` | k6 load tests for async AI pipelines — concurrent job submissions, queue saturation, polling storms, SLA validation. | sonnet | custom |
| `bug-reporter` | Raw notes → structured bug report for Jira/Linear/GitHub Issues. Severity guide tuned for SaaS: always captures user plan, job state, quota. | haiku | custom |

#### Claude Code setup

Agents for managing the local Claude Code environment. Built-in agents from Claude Code; `release-manager` and `docker-debugger` have project-specific context baked in.

| Agent | What it does | Model |
|-------|-------------|-------|
| `ai-researcher` | Latest AI news digest — model releases, research papers, industry moves. | haiku |
| `bash-scripter` | Writes and fixes bash/shell scripts — entrypoints, automation, setup scripts. | sonnet |
| `docker-debugger` | Diagnoses Docker containers that crash, restart, or fail healthchecks. Knows the Infisical + Docker Compose patterns used in this setup. | sonnet |
| `release-manager` | npm publish, GitHub releases, changelog, git tags. Configured for the npm publish workflow on macOS. | sonnet |
| `mempalace-admin` | MemPalace maintenance — auditing palace contents, cleanup, KG health. | sonnet |

#### Side projects

Agents for two separate self-hosted projects. Useful only if you run the same setup.

| Agent | What it does | Model |
|-------|-------------|-------|
| `hermes-admin` | [Hermes](https://github.com/anastasiiaanfimova/hermes-docker) config — Docker setup, channels, Infisical secrets, entrypoint debugging. | sonnet |
| `openclaw-admin` | [OpenClaw](https://openclaw.ai) config — agents, schema, docker-compose overrides, GHCR updates. | sonnet |

## How to use

**Agents** — copy any agent file to `~/.claude/agents/`:
```bash
cp agents/bug-reporter.md ~/.claude/agents/
```

Copy what's useful, adjust paths to your setup. [Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)
