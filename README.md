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
                   [3] MemPalace snapshot export (async)
                       Exports all palace drawers to human-readable Markdown in
                       ~/.mempalace/export/, then git commits + pushes to a private
                       backup repo. ChromaDB is binary — this creates a browsable,
                       git-tracked copy of everything MemPalace knows.
                   (One event, three commands. Hook [2] is synchronous — it blocks
                   until Claude writes the diary. Hooks [1] and [3] run async.)

PreCompact       → MemPalace precompact hook
                   Before Claude Code compresses the context window, important
                   facts are written to MemPalace so they survive compaction.

SessionStart     → code-review-graph check
                   Warns if the codebase graph hasn't been initialized yet.
                   Reminds you to run `code-review-graph build` in new projects.
```

> **Requirements:** MemPalace installed at `~/.mempalace/`, code-review-graph MCP connected. If you don't use these tools, the hook structure is still a useful reference — swap in your own commands.

## Credential management

API keys and tokens never go into shell files (`~/.zshrc`, `~/.zshenv`) or `.env` files. Instead they live in [agent-vault](https://github.com/Infisical/agent-vault) — an encrypted local credential proxy for AI agents.

**Why agent-vault instead of env files:** env files get committed by accident, end up in logs, and leak through shell history. agent-vault stores credentials AES-256-GCM encrypted on disk and injects them only when explicitly invoked.

### How it works

Credentials are grouped into vaults per project or scope:

```bash
agent-vault vault credential set KEY=value --vault myproject
agent-vault vault credential set KEY=value           # default vault
```

To run Claude with credentials injected as env vars:

```bash
agent-vault vault run --vault myproject -- claude
```

Claude sees the credentials as environment variables for that session. The raw values never appear in shell config or command history.

### CLAUDE.md enforces the rule

The global `CLAUDE.md` instructs Claude to never save API keys to shell files — always offer `agent-vault vault credential set` instead. This means even if the user asks Claude to "save this token", Claude will redirect to the vault.

## MCP project isolation

MemPalace is configured **per project** via `.mcp.json`, not globally. Each project directory has its own palace so Claude running from that directory only sees memories for that project — no cross-contamination.

```
~/Claude/.mcp.json     → mempalace → ~/.mempalace/palace      (main)
~/Openclaw/.mcp.json   → mempalace → ~/.openclaw/mempalace/palace
~/Hermes/.mcp.json     → mempalace → ~/.hermes/mempalace
~/MyProject/.mcp.json  → mempalace → ~/.myproject/mempalace
```

The server is always named `mempalace` in each project, so hooks and tool permissions (`mcp__mempalace__*`) are identical everywhere. The only difference is which palace they point to.

If Claude is launched from any other directory, MemPalace is simply unavailable — by design.

### `CLAUDE.md`

The **global** `~/.claude/CLAUDE.md` contains the MemPalace protocol and credential management rules. The MemPalace section instructs Claude to call `mempalace_status` at session start, search before answering about people/projects, and write diary at session end. The credential section instructs Claude to never write API keys to shell files and always redirect to agent-vault instead.

The `code-review-graph` block that was here previously is **project-specific** — it belongs in a project's own `CLAUDE.md` or `.claude/CLAUDE.md`, not in the global file. Copy it into any project where you've run `code-review-graph build`.

### `agents/`

Custom subagents for specialized tasks. Drop any of these into `~/.claude/agents/` and Claude Code will route to them automatically.

#### Claude Code setup

Agents for managing the local Claude Code environment. Built-in agents from Claude Code; `release-manager` and `docker-debugger` have project-specific context baked in.

| Agent | What it does | Model |
|-------|-------------|-------|
| `ai-researcher` | Latest AI news digest — model releases, research papers, industry moves. | haiku |
| `bash-scripter` | Writes and fixes bash/shell scripts — entrypoints, automation, setup scripts. | sonnet |
| `docker-debugger` | Diagnoses Docker containers that crash, restart, or fail healthchecks. Knows the Infisical + Docker Compose patterns used in this setup. | sonnet |
| `release-manager` | npm publish, GitHub releases, changelog, git tags. Configured for the npm publish workflow on macOS. | sonnet |
| `mempalace-admin` | MemPalace maintenance — auditing palace contents, cleanup, KG health. | sonnet |

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

#### Side projects

Agents for separate self-hosted projects. These are **project-scoped** — not in `~/.claude/agents/` globally, but placed in `.claude/agents/` inside the specific project directory. This keeps them out of unrelated contexts.

| Agent | What it does | Model |
|-------|-------------|-------|
| `hermes-admin` | [Hermes](https://github.com/anastasiiaanfimova/hermes-docker) config — Docker setup, channels, Infisical secrets, entrypoint debugging. | sonnet |
| `openclaw-admin` | [OpenClaw](https://github.com/anastasiiaanfimova/openclaw) config — agents, models, docker-compose, Infisical secrets, schema validation. | sonnet |

### `commands/setup.md`

A `/setup` slash command for one-time project initialization. Run it once when starting work in a new project directory.

What it does:
1. Checks MemPalace is available — if not, prints the exact `.mcp.json` snippet to add
2. Searches the palace for any existing knowledge about this project
3. Creates `~/.claude/projects/.../memory/` files with the MemPalace protocol reminder
4. Checks whether `code-review-graph` is initialized, prompts to run it if not
5. Adds the project to the MemPalace knowledge graph (setup date + project facts you describe)
6. Writes a diary entry so the setup is recorded in palace history

**Requires:** `mempalace` configured in the project's `.mcp.json` (see MCP project isolation above).

## How to use

**Agents** — copy any agent file to `~/.claude/agents/`:
```bash
cp agents/bug-reporter.md ~/.claude/agents/
```

**`/setup` command** — copy to `~/.claude/commands/`:
```bash
cp commands/setup.md ~/.claude/commands/
```
Then run `/setup` from any new project directory.

Copy what's useful, adjust paths to your setup. [Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)

**Pre-commit hook** — `hooks/pre-commit` blocks commits that contain private project or service names. After cloning, install it and add your own forbidden words:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
# then edit .git/hooks/pre-commit and fill in FORBIDDEN=()
```
