# claude-configs

My personal Claude Code configuration — custom agents, hooks, CLAUDE.md examples, and patterns I use day-to-day. Feel free to adapt anything here.

## Plugins

[Superpowers](https://github.com/obra/superpowers) is installed globally (scope: user). It adds structured workflows for brainstorming, planning, TDD, debugging, code review, and git worktrees — available in every project without any per-project config.

Superpowers skills are invoked with `superpowers:<skill-name>` (e.g. `superpowers:brainstorming`, `superpowers:systematic-debugging`). See the plugin repo for the full list.

---

## Memory stack

This setup layers three independent memory systems on top of Claude Code. Each solves a different problem:

| Layer | Tool | What it remembers |
|-------|------|-------------------|
| **Cross-session agent memory** | [MemPalace](https://github.com/MemPalace/mempalace) | Who the user is, project context, feedback, preferences — persists across sessions in a diary + knowledge graph |
| **Conversation search** | [episodic-memory](https://github.com/Anthropic/episodic-memory) | Full-text index of past Claude Code sessions — searchable by topic, code, or question. Synced at session end. |
| **Codebase structure** | [code-review-graph](https://github.com/tirth8205/code-review-graph) | Functions, classes, call relationships, imports — parsed from source with Tree-sitter, queryable as a graph |
| **In-project notes** | Claude Code built-in auto-memory | Markdown files in `~/.claude/projects/*/memory/` — facts Claude saves during sessions |

None of these overlap: MemPalace is about the agent knowing the user, episodic-memory is a searchable archive of raw conversation history, code-review-graph is about knowing the codebase, auto-memory is about in-project scratchpad facts.

Since MemPalace captures everything important across sessions, raw `.jsonl` session logs are just disk clutter. Run `claude-cleanup` (a shell alias) manually whenever you want to prune logs older than 30 days. The `memory/` directory is always preserved.

## What's inside

### `settings/settings.json`

Four hooks that wire the memory stack into Claude Code:

```
UserPromptSubmit → MemPalace session-start
                   Loads relevant memories into context before each message.
                   Without this, MemPalace exists but Claude never reads it.

Stop             → MemPalace stop hook (sync)
                   Claude writes a diary entry + KG facts at end of session.
                   This is how memories actually get saved.
                 → episodic-memory sync (async)
                   Indexes the finished session so it's searchable later.
                 → cleanup_history.sh (async, local-only)
                   Trims hook-approvals.log to 500 lines; prunes .jsonl session
                   logs older than 30 days. Script lives in ~/.claude/scripts/
                   on the local machine — not in this repo.

StopFailure      → MemPalace stop hook (sync, crash path)
                   Same as Stop, but fires when the session ends due to an
                   API error (rate limit, auth failure, etc.). Prepends a crash
                   notice to the diary prompt so Claude records what happened
                   before the session dies.

PreCompact       → MemPalace precompact hook
                   Before Claude Code compresses the context window, important
                   facts are written to MemPalace so they survive compaction.

SessionStart     → code-review-graph check
                   Warns if the codebase graph hasn't been initialized yet.
                   Reminds you to run `code-review-graph build` in new projects.
```

> **Requirements:** MemPalace installed at `~/.mempalace/`, code-review-graph MCP connected. If you don't use these tools, the hook structure is still a useful reference — swap in your own commands.

## Credential management

API keys and tokens never go into shell files (`~/.zshrc`, `~/.zshenv`) or `.env` files. Instead they live in [Infisical](https://infisical.com) — a secrets manager with CLI injection.

**Why Infisical instead of env files:** env files get committed by accident, end up in logs, and leak through shell history. Infisical stores secrets centrally (cloud or self-hosted) and injects them per-command into the process environment only.

### How it works

Secrets are grouped into projects and folders (e.g. `Personal/myproject/`, `Work/clientA/`). CLI auth uses a **machine identity** (Universal Auth) — Client ID + Client Secret stored in the macOS Keychain, exchanged for a fresh access token on every run so the session never expires.

A shell helper fetches the token:

```bash
# ~/.zshrc
_infisical_token() {
  local client_id=$(security find-generic-password -a "$USER" -s infisical-client-id -w)
  local client_secret=$(security find-generic-password -a "$USER" -s infisical-client-secret -w)
  infisical login --method=universal-auth \
    --client-id="$client_id" --client-secret="$client_secret" \
    --plain --silent
}
```

Then run Claude with secrets injected as env vars:

```bash
INFISICAL_TOKEN=$(_infisical_token) infisical run \
  --projectId="$INFISICAL_PROJECT_WORK" --path="/myproject" -- claude
```

### Smart shell function

A `claude()` function in `~/.zshrc` auto-detects the project from `pwd` and injects the right folder:

```bash
claude() {
  case "$PWD" in
    $HOME/ProjectA*) INFISICAL_TOKEN=$(_infisical_token) infisical run \
      --projectId="$INFISICAL_PROJECT_WORK" --path="/projectA" -- command claude "$@" ;;
    $HOME/Claude/mytool*) INFISICAL_TOKEN=$(_infisical_token) infisical run \
      --projectId="$INFISICAL_PROJECT_PERSONAL" --path="/mytool" -- command claude "$@" ;;
    *) command claude "$@" ;;
  esac
}
```

Folders outside the match list run plain `claude` without injection. Explicit aliases (`claude-projecta`, `claude-mytool`) cover cases where you want a specific context from any directory.

### Adding secrets

```bash
infisical secrets set --projectId="$INFISICAL_PROJECT_WORK" \
  --path="/myproject" KEY=value
```

### CLAUDE.md enforces the rule

The global `CLAUDE.md` instructs Claude to never save API keys to shell files — always offer to add them to the right Infisical project/folder instead. Even if the user asks Claude to "save this token", Claude will redirect to Infisical.

## MCP project isolation

MemPalace is configured **per project** via `.mcp.json`, not globally. Claude running in a project directory only sees memories for that project — no cross-contamination.

Two tiers of isolation:

**Shared palace** — sub-projects inside `~/Claude/` share a single palace. No `--palace` flag; `palace_detect.sh` walks up the directory tree to find the nearest `.mcp.json` and falls back to `~/.mempalace/palace`.

```
~/Claude/.mcp.json           → mempalace (no --palace) → ~/.mempalace/palace
~/Claude/<project>/.mcp.json → mempalace (no --palace) → ~/.mempalace/palace  (inherits)
~/Claude/hermes/.mcp.json    → mempalace (no --palace) → ~/.mempalace/palace  (inherits)
```

**Separate palace** — top-level independent projects each get their own isolated palace:

```
~/Hermes/.mcp.json     → mempalace --palace ~/.hermes/mempalace
~/MyProject/.mcp.json  → mempalace --palace ~/.myproject/mempalace
```

The server is always named `mempalace` in each project, so hooks and tool permissions (`mcp__mempalace__*`) are identical everywhere. The `/setup` command automatically picks the right tier based on whether the current directory is inside `~/Claude/`.

If Claude is launched from any other directory, MemPalace is simply unavailable — by design.

### `CLAUDE.md`

The **global** `~/.claude/CLAUDE.md` contains the MemPalace protocol and credential management rules. The MemPalace section instructs Claude to call `mempalace_status` at session start, search before answering about people/projects, and write diary at session end. The credential section instructs Claude to never write API keys to shell files and always redirect to the right Infisical project/folder instead.

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

### `commands/setup.md`

A `/setup` slash command for one-time project initialization. Run it once when starting work in a new project directory.

What it does:
1. Checks MemPalace is available — if not, prints the correct `.mcp.json` snippet to add. Automatically picks the right palace strategy: no `--palace` flag for sub-projects inside `~/Claude/`, separate `~/.projectname/mempalace` for top-level independent projects.
2. Searches the palace for any existing knowledge about this project
3. Creates `~/.claude/projects/.../memory/` files with the MemPalace protocol reminder
4. Checks whether `code-review-graph` is initialized, prompts to run it if not
5. Adds the project to the MemPalace knowledge graph (setup date + project facts you describe)
6. Writes a diary entry so the setup is recorded in palace history

**Requires:** `mempalace` configured in the project's `.mcp.json` (see MCP project isolation above).


### `scripts/`

Helper scripts used by the hooks and tooling.

| Script | What it does |
|--------|-------------|
| `palace_detect.sh` | Resolves which MemPalace palace to use for the current directory. Walks up the directory tree looking for a `.mcp.json` with a `mempalace` entry; falls back to `~/.mempalace/palace`. Used in all hook commands so the right palace is always targeted. |
| `cleanup_history.sh` | Runs on session Stop (async hook). Trims `hook-approvals.log` to 500 lines; prunes `.jsonl` session logs older than 30 days. |

> **Local-only:** [`statusline.sh`](https://github.com/anastasiiaanfimova/claude-statusline) — populates the Claude Code status bar. Lives in `~/.claude/scripts/` and is wired via `statusLine` in `settings.json`. See the linked repo for setup.

### `skills/`

Slash command skills — invokable with `/skill-name` in any Claude Code session. Each skill defines a multi-step automated workflow that Claude executes inline (with full tool access and context), on demand.

Skills differ from agents: agents are subprocesses dispatched for isolated subtasks; skills run in the main conversation. Use skills for repeatable workflows that need judgment, tool calls, and cross-referencing across multiple data sources.

**Install:** copy any skill directory to `~/.claude/skills/` — Claude Code auto-discovers them on startup.

> **Note:** Skills reference project-specific config (TMS project IDs, analytics project IDs, Notion page IDs). Replace `<YOUR_*>` placeholders in each skill's `SKILL.md` and reference files before use.

#### QA skills

Built for QA work on an AI SaaS product — backend + web, analytics events, async generation pipelines.

| Skill | What it does |
|---|---|
| `tc-create` | Creates test cases in Testiny following project naming conventions, priority rules (based on analytics event volume), and Slate.js step format. Verifies all data against a real source — analytics platform, backend code, or monitoring. Never invents steps. |
| `tc-update` | Updates existing test cases in Testiny: bulk field changes (type, priority, status, automation), folder moves, content/steps edits, renames. Handles etag flow automatically. ACTIVE TCs require explicit confirmation before any change. |
| `tc-gap` | Gap analysis: fetches all existing TCs from Testiny, collects signal sources per project (analytics events for web, backend handler map for backend, admin panel pages for admin), cross-references, and outputs a prioritized gap report. Auto-updates a Notion page; preserves manually added notes. |
| `bug-candidates` | Weekly bug triage prep: refreshes signal sources (Sentry, GitLab, Amplitude, Grafana, Asana) in Notion and rebuilds the Bug Candidates list with dedup against the prior week. Output feeds into `bug-dig`. Never auto-creates Asana tasks. |
| `bug-dig` | Investigates a Sentry issue or Asana bug: confirms whether it's a real user-impacting bug, noise, or theoretical risk. Collects evidence across Sentry, Loki, Amplitude, git log, Notion, and code. Writes verdict to Notion Bug Candidates DB; never auto-creates Asana tasks. |
| `refresh-git` | Pulls latest from main for all project repos and rebuilds code-review-graph indexes. Run at the start of a session before code analysis or QA work. |
| `qa-tooling` | Tooling audit: reads MemPalace diary across recent sessions (last 14 days), identifies recurring pain points and manual steps, and suggests new skills, agents, or automations to build. Focused on "what should we build next?" — not a session summary. |

#### Claude skills

| Skill | What it does |
|---|---|
| `claude-tooling` | Cross-project Claude tooling audit. Reads MemPalace across all project wings + diary, searches the web for new Claude Code / Anthropic updates, compares against an existing `IMPROVEMENTS.md` in a GitHub repo, and pushes an updated file with status tracking (🔄 pending / ✅ done / 🆕 new / 📡 new in Claude). Fully autonomous — auto-commits and pushes. No user input needed. |
| `push-config` | Syncs `~/.claude/` files to this GitHub repo. Diffs local vs repo, anonymizes private project names, commits only changed files. Handles CLAUDE.md, settings.json, all agents, public skills, MemPalace hooks, and palace_detect.sh. Updates README if content changed. |
| `mac-cleanup` | macOS system cleanup: scans artifacts from removed apps, stale configs, and old caches. Three-phase: survey (read-only) → confirm → clean. Fully automated for safe operations; asks before anything non-obvious. |
| `find-skills` | Discovers and suggests installable agent skills when you ask "is there a skill for X?" or want to extend Claude's capabilities. Searches the open skills ecosystem. |

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

**Pre-commit hook** — `hooks/pre-commit` is a global hook that blocks private project or service names from leaking into public repos. It checks staged diffs only for repos under your GitHub owner, and only if they're public.

Git never auto-installs hooks on clone — you need to set this up once manually:

```bash
cp hooks/pre-commit ~/.git-hooks/pre-commit
chmod +x ~/.git-hooks/pre-commit
git config --global core.hooksPath ~/.git-hooks
```

Then create `~/.git-hooks/pre-commit.local` with your actual forbidden words:

```bash
FORBIDDEN=(myproject internal-service vault-name)
```

The hook reads `FORBIDDEN` from `.local` if it exists; falls back to an empty list if the file is absent. The `.local` file is gitignored — keep it on the local machine only, never commit it. The `/push-config` skill also runs this hook explicitly before each commit.
