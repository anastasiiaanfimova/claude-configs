# claude-configs

A reference snapshot of one Claude Code setup — concrete configs (hooks,
agents, settings) plus methodology spin-offs of the local working skills.
Feel free to adapt anything here.

Two kinds of content:

- **Concrete reference** — `settings/settings.json`, `hooks/pre-commit`,
  `agents/`, `examples/CLAUDE.md` are actual files. Read and adapt to
  your stack.
- **Methodology** — `skills/<name>/SKILL.md` describe processes,
  decision frameworks, and anti-patterns that survive switching to a
  different agent CLI / MCP stack / memory tool. Tool-agnostic by
  construction.

See [`CLAUDE.md`](CLAUDE.md) for the methodology pattern (and the
job-change test that decides what gets a methodology variant).

## Plugins

[Superpowers](https://github.com/obra/superpowers) is installed globally (scope: user). It adds structured workflows for brainstorming, planning, TDD, debugging, code review, and git worktrees — available in every project without any per-project config.

Superpowers skills are invoked with `superpowers:<skill-name>` (e.g. `superpowers:brainstorming`, `superpowers:systematic-debugging`). See the plugin repo for the full list.

---

## Memory stack

This setup layers four independent memory systems on top of Claude Code. Each solves a different problem:

| Layer | Tool | What it remembers |
|-------|------|-------------------|
| **Cross-session agent memory** | [MemPalace](https://github.com/MemPalace/mempalace) | Who the user is, project context, feedback, preferences — persists across sessions in a diary + knowledge graph |
| **Conversation search** | [episodic-memory](https://github.com/obra/episodic-memory) | Full-text index of past Claude Code sessions — searchable by topic, code, or question. Synced at session end. |
| **Codebase structure** | [code-review-graph](https://github.com/tirth8205/code-review-graph) | Functions, classes, call relationships, imports — parsed from source with Tree-sitter, queryable as a graph |
| **In-project notes** | Claude Code built-in auto-memory | Markdown files in `~/.claude/projects/*/memory/` — facts Claude saves during sessions |

> Contributed the high-water-mark fix for incremental indexing of appended exchanges in episodic-memory ([PR #85](https://github.com/obra/episodic-memory/pull/85)) — [shipped in v1.1.0](https://github.com/obra/episodic-memory/releases/tag/v1.1.0).

None of these overlap: MemPalace is about the agent knowing the user, episodic-memory is a searchable archive of raw conversation history, code-review-graph is about knowing the codebase, auto-memory is about in-project scratchpad facts.

Since MemPalace captures everything important across sessions, raw `.jsonl` session logs are just disk clutter. The `history-cleanup` script runs automatically on SessionStart (async, no slowdown) — prunes logs older than 30 days, removes orphaned subagent dirs, and clears project state for worktrees that no longer exist. Invoke `/history-cleanup` manually for ad-hoc inspection or extra-aggressive cleanup. The `memory/` directory is always preserved.

## What's inside

### `settings/settings.json`

Seven hooks that wire the memory stack, safety layer, and history hygiene into Claude Code:

```
UserPromptSubmit → MemPalace session-start hook
                   Initializes session tracking state so the stop hook knows
                   how many exchanges have occurred.

Stop             → MemPalace stop hook (sync)
                   Claude writes a diary entry + KG facts at end of session.
                   This is how memories actually get saved.
                 → episodic-memory sync (async)
                   Indexes the finished session so it's searchable later.
                 → crg-dedup.sh dedup (async)
                   Kills duplicate code-review-graph MCP processes — keeps one
                   per repo, removes extras left by subagents or parallel sessions.

StopFailure      → MemPalace stop hook (sync, crash path)
                   Same as Stop, but fires when the session ends due to an
                   API error (rate limit, auth failure, etc.).

PreCompact       → MemPalace precompact hook (async)
                   Fires before context compaction so in-progress session
                   content can be saved before detailed context is lost.

SessionStart     → code-review-graph check
                   Warns if the codebase graph hasn't been initialized yet.
                   Reminds you to run `code-review-graph build` in new projects.
                 → crg-dedup.sh orphans (async)
                   Kills code-review-graph processes orphaned by crashed sessions
                   (PPID=1). Prevents accumulation across session restarts.
                 → history-cleanup.sh (async)
                   Trims hook-approvals.log, removes .jsonl session logs older
                   than 30 days, removes orphaned subagent dirs and project
                   dirs whose worktrees no longer exist.

PreToolUse       → [dippy](https://github.com/ldayton/Dippy) (Bash commands)
                   AST-based approval filter for shell commands. Auto-approves
                   safe read-only and standard dev commands; blocks destructive
                   ones; prompts for anything in between. Configured via
                   ~/.dippy/config. Install: brew tap ldayton/dippy && brew install dippy
```

> **MemPalace workarounds (as of v3.3.1 stable, 2026-04-29):**
>
> All seven hooks are active. The `mine` (indexing) sub-process is disabled via a local venv patch —
> all hooks run normally and diary saves work, but `mempalace mine` is never spawned.
>
> **Why:** `mine --mode convos` scans the entire session directory (100+ JSONL files) on every
> Stop hook, consuming 90–200% CPU for minutes at a time. Even with a PID guard, the next Stop
> fires a new `mine` as soon as the old one finishes. Diary saves (`_save_diary_direct`) are
> unaffected — they use a separate code path and always complete.
>
> **Local patch applied** to `~/.mempalace/venv/.../mempalace/hooks_cli.py` —
> `_maybe_auto_ingest()` and `_mine_sync()` are made no-ops (return immediately with a log line).
> **This patch is lost on `pip install mempalace`** — re-apply after every upgrade.
>
> Relevant open issues — remove the patch once these are resolved upstream:
> - [#1212](https://github.com/MemPalace/mempalace/issues/1212) — Stop hook spawns concurrent `mine` processes that bypass PID guard
> - [#1083](https://github.com/MemPalace/mempalace/issues/1083) — Stop + PreCompact auto-run `mine` with no opt-out
> - [#1110](https://github.com/MemPalace/mempalace/issues/1110) — feat: split `hooks.auto_save` and `hooks.auto_mine` (config option to disable mine without removing diary saves)

> **code-review-graph process accumulation workaround (as of 2026-05-02):**
>
> When using `code-review-graph serve` with Claude Code's Agent tool, processes accumulate as
> orphans — each subagent session spawns its own MCP processes, and when the subagent exits its
> children get reparented to PID 1 instead of being killed. With 3 repos × multiple subagent
> sessions, 20+ processes can accumulate, consuming ~17% CPU.
>
> **Workaround:** two hooks in `settings.json` (included in this config):
> - `SessionStart → crg-dedup.sh orphans` — kills processes orphaned by crashed sessions (PPID=1)
> - `Stop → crg-dedup.sh dedup` — keeps one process per repo, kills extras
>
> The script lives at `~/.claude/scripts/crg-dedup.sh` (not in this repo — local only).
>
> Remove the hooks once this is resolved upstream:
> - [#416](https://github.com/tirth8205/code-review-graph/issues/416) — MCP serve processes accumulate as orphans when used with Claude Code subagents

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

The server is always named `mempalace` in each project, so hooks and tool permissions (`mcp__mempalace__*`) are identical everywhere. The `/workspace-setup` command automatically picks the right tier based on whether the current directory is inside `~/Claude/`.

If Claude is launched from any other directory, MemPalace is simply unavailable — by design.

### `examples/CLAUDE.md`

A sample of what a global `~/.claude/CLAUDE.md` can contain — the
concrete instructions file Claude Code auto-loads at session start.
Adapt to your own setup.

What's in the sample:

- **Memory protocol** — three layers used in parallel at session start (MemPalace + episodic-memory + auto-memory files), each for different lookup needs (facts vs. specific words/commands vs. behavior rules)
- **Project context separation** — never mix knowledge across projects unless explicitly asked
- **Credential management** — API keys and tokens never go to shell files, always Infisical
- **code-review-graph** — generic instructions on using the graph tools before falling back to Grep/Glob/Read in any project that has `.code-review-graph/` initialized
- **Engineering principles** — multi-pass discipline, OOP (Encapsulation/Inheritance/Polymorphism/Abstraction), DRY/KISS/SOLID/BDUF/SoC, PoC→MVP rollout
- **Behavioral rules** — pacing, session-continue handling, git privacy for public repos, skill naming convention, avoided phrasing
- **Behavioral rule scoping** — when saving a new rule, decide cross-project vs. project-specific vs. infrastructure-fact and route to the right file
- **Superpowers overrides** — exceptions to brainstorming hard-gate for action-oriented skills, memory protocol priority over skill invocation

> The repo's own `CLAUDE.md` (in the root) is a meta-doc about editing
> this repo, not a sample. Different file, different audience.

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
| `security-auditor` | Audits REST API and web apps for security vulnerabilities — auth bypasses, broken access control, injection, insecure configs. QA-focused, not compliance auditing. | sonnet |

> **QA agents** (test-architect, e2e-tester, bug-reporter, etc.) are published separately — see [qa-playbook](https://github.com/anastasiiaanfimova/qa-playbook).

#### Side projects

Agents for separate self-hosted projects. These are **project-scoped** — not in `~/.claude/agents/` globally, but placed in `.claude/agents/` inside the specific project directory. This keeps them out of unrelated contexts.

| Agent | What it does | Model |
|-------|-------------|-------|
| `hermes-admin` | [Hermes](https://github.com/anastasiiaanfimova/hermes-docker) config — Docker setup, channels, Infisical secrets, entrypoint debugging. | sonnet |

### `hooks/`

Two files that extend the hook infrastructure.

| File | What it does |
|------|-------------|
| `pre-commit` | Global git pre-commit hook — blocks private project names from leaking into public repos. Reads the deny list from `~/.claude/lib/push-mirror/forbidden.txt` (one pattern per line). Runs only for public repos under `anastasiiaanfimova`. |

> **Local-only scripts** (not in this repo): [`statusline.sh`](https://github.com/anastasiiaanfimova/claude-statusline) — populates the status bar; `history-cleanup.sh` — manual history cleanup (invoked via `/history-cleanup` skill); `kill-orphan-mcp.sh` — finds and kills MCP server processes orphaned from crashed sessions; `palace_detect.sh` — lives in `~/.mempalace/`, part of the MemPalace installation.

### `skills/`

Methodology spin-offs of the local working skills — process knowledge,
decision frameworks, anti-patterns. Tool-agnostic; designed to survive
switching agent CLI / MCP stack / memory tool.

These are **reference documents**, not drop-in slash commands. The
local working versions in `~/.claude/skills/` carry the actual MCP
calls and paths; here you get the underlying methodology.

If you want to install one as a working skill in your environment, copy
the directory and adapt the abstract references to your stack:

```bash
cp -r skills/claude-cleanup ~/.claude/skills/
# Then edit ~/.claude/skills/claude-cleanup/SKILL.md to reference your real
# MCP servers, file paths, tool names, etc.
```

#### Skills

| Skill | What it covers |
|---|---|
| `workspace-setup` | One-time project bootstrap methodology — shared vs isolated context decision, phased setup (infrastructure-then-restart-then-content), seed-structure rules for new isolated stores, the index+rules memory file pattern |
| `claude-cleanup` | Periodic agent-config audit methodology — survey-confirm-execute discipline, truth-source-vs-claim diff for stale-reference detection, duplicate / wrapper / parasitic-dir / approval-log categories |
| `claude-audit` | Forward-looking "what should I build next?" retro — five proactive lenses (manual reps, agent errors, stuck workarounds, knowledge re-asked, dead capabilities), file-as-state with status lifecycle, internal+external signal cross-check |
| `history-cleanup` | Session-history rotation methodology — five independent decay axes (approval log, session logs, orphan subagent dirs, worktree-orphan project dirs, dead-cwd projects), survey-confirm-clean phases, manual+hook split |
| `tooling-update` | Multi-package-manager update methodology — snapshot-update-snapshot pattern, parallel-where-safe vs sequential-where-required, pinned-version awareness, patch re-application reminders |
| `claude-config-push` | Sync mechanism for this repo. **Being rewritten under the new manual workflow** — until then, the listing here is the prior automation; not yet methodology. |

> **QA skills and agents** (tc-create, tc-gap, bug-dig, etc.) are published separately — see [qa-playbook](https://github.com/anastasiiaanfimova/qa-playbook).

## How to use

**Agents** — copy any agent file to `~/.claude/agents/`:
```bash
cp agents/bug-reporter.md ~/.claude/agents/
```

**`/workspace-setup` skill** — copy to `~/.claude/skills/workspace-setup/`:
```bash
mkdir -p ~/.claude/skills/workspace-setup
cp skills/workspace-setup/SKILL.md ~/.claude/skills/workspace-setup/
```
Then run `/workspace-setup` from any new project directory.

Copy what's useful, adjust paths to your setup. [Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)

**Pre-commit hook** — `hooks/pre-commit` is a global hook that blocks private project or service names from leaking into public repos. It checks staged diffs only for repos under your GitHub owner, and only if they're public.

Git never auto-installs hooks on clone — you need to set this up once manually:

```bash
cp hooks/pre-commit ~/.git-hooks/pre-commit
chmod +x ~/.git-hooks/pre-commit
git config --global core.hooksPath ~/.git-hooks
```

The hook reads its deny list from a single source: `~/.claude/lib/push-mirror/forbidden.txt` (one regex pattern per line; comments allowed). If the file doesn't exist, the hook silently exits — so you must create it before this hook protects anything:

```bash
mkdir -p ~/.claude/lib/push-mirror
cat > ~/.claude/lib/push-mirror/forbidden.txt <<'EOF'
# One pattern per line. Case-insensitive (hook uses grep -iE).
myproject
internal-service
vault-name
EOF
```

To add or remove a forbidden word later, just edit `forbidden.txt` directly. The `/claude-config-push` skill also runs this hook explicitly before each commit.
