# claude-configs

A methodology snapshot of one [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
setup — patterns for skills, agents, settings, hooks, and global
instructions. Read for the shape of the setup, adapt the bits that fit
your stack.

Everything here is **methodology** — patterns and decision frameworks
that survive moving to a different agent CLI / MCP stack / memory tool.
Concrete artifacts (`settings/`, `hooks/`, `agents/`, `templates/`,
`lib/`) are kept as illustrative *examples* with placeholders for
paths, scopes, and project-specific names — not as copy-paste-and-run
files.

For the editing principles and the "stack-swap test" that decides
what belongs here, see [`CLAUDE.md`](CLAUDE.md).

## What's in the repo

| Path | What it is |
|---|---|
| [`examples/CLAUDE.md`](examples/CLAUDE.md) | Methodology example for a global Claude Code instructions file — memory protocol, behavior rules, engineering principles |
| [`skills/`](skills/) | Methodology essays for individual skills (`workspace-setup`, `claude-cleanup`, `claude-audit`, `history-cleanup`, `tooling-update`) |
| [`agents/`](agents/) | Agent example files — frontmatter + prompt body, with placeholders for project-specific paths and scopes |
| [`settings/`](settings/) | Illustrative `settings.json` example showing hook event categories and the shape of a Claude Code config |
| [`hooks/`](hooks/) | Illustrative global pre-commit hook for blocking private names from leaking to public repos |
| [`templates/`](templates/) | Per-language CLAUDE.md skeletons with placeholders |
| [`lib/push-mirror/`](lib/push-mirror/) | Reference toolkit for an anonymizing publish-mirror pattern |

## Plugins

[Superpowers](https://github.com/obra/superpowers) is installed
globally (scope: user). It adds structured workflows for brainstorming,
planning, TDD, debugging, code review, and git worktrees — available
in every project without per-project config. Skills are invoked as
`superpowers:<skill-name>` (e.g. `superpowers:brainstorming`).

## Memory stack pattern

This setup layers four independent memory systems on top of Claude
Code. Each solves a different problem; none overlap.

| Layer | Tool | What it remembers |
|-------|------|-------------------|
| **Cross-session agent memory** | [MemPalace](https://github.com/MemPalace/mempalace) | Who the user is, project context, feedback, preferences — persists across sessions in a diary + knowledge graph |
| **Conversation search** | [episodic-memory](https://github.com/obra/episodic-memory) | Full-text index of past sessions — searchable by topic, code, or question. Synced at session end. |
| **Codebase structure** | [code-review-graph](https://github.com/tirth8205/code-review-graph) | Functions, classes, call relationships, imports — parsed with Tree-sitter, queryable as a graph |
| **In-project notes** | Claude Code built-in auto-memory | Markdown files in `~/.claude/projects/*/memory/` — facts Claude saves during sessions |

The split: MemPalace is about the agent knowing the user;
episodic-memory is a searchable archive of raw conversation history;
code-review-graph is about knowing the codebase; auto-memory is an
in-project scratchpad.

Since MemPalace captures everything important across sessions, raw
`.jsonl` session logs are disk clutter. A `history-cleanup` script
runs automatically on SessionStart (async, no slowdown) — prunes logs
older than 30 days, removes orphaned subagent dirs, and clears project
state for worktrees that no longer exist.

> Patterns to watch for if you wire similar tooling: an MCP server that
> spawns sub-processes on every hook can starve CPU; a stdio MCP server
> can orphan processes under nested agent invocations. Prefer
> persistent-daemon mode (SSE / HTTP) for any MCP that's used heavily.

## Hooks wired in this setup

The shape of `settings/settings.json` — what events get hooked and why:

```
UserPromptSubmit → memory-MCP session-start (initializes session tracking
                   so the stop hook knows how many exchanges have occurred)

Stop             → memory-MCP stop (sync) — writes diary entry + KG facts
                 → conversation-archive sync (async) — indexes the finished
                   session so it's searchable later

StopFailure      → memory-MCP stop (sync, crash path) — same as Stop, but
                   fires when the session ends due to an API error
                   (rate limit, auth failure, etc.)

PreCompact       → memory-MCP precompact (async) — saves in-progress
                   session content before context compaction discards detail

SessionStart     → code-graph init check — warns if the codebase graph
                   isn't initialized yet
                 → history-cleanup (async) — trims approval log, prunes
                   old session logs, removes orphan dirs

PreToolUse       → AST-based shell command filter (e.g. dippy) — auto-approves
                   safe read-only commands, blocks destructive ones, prompts
                   for anything in between
```

If you don't use these specific tools, the hook structure is still a
useful reference — swap in your own commands.

## Credential-management pattern

API keys and tokens never go into shell files (`~/.zshrc`, `~/.zshenv`)
or `.env` files. Instead they live in
[Infisical](https://infisical.com) — a secrets manager with CLI
injection.

**Why over env files:** env files get committed by accident, end up in
logs, and leak through shell history. Infisical stores secrets
centrally (cloud or self-hosted) and injects them per-command into the
process environment only.

### Shape of the integration

Secrets are grouped into projects and folders (e.g.
`<scope>/<project>/`). CLI auth uses a **machine identity** (Universal
Auth) — Client ID + Client Secret stored in the OS keychain, exchanged
for a fresh access token on every run.

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

A wrapper function in `~/.zshrc` auto-detects the project from `pwd`
and injects the right folder:

```bash
claude() {
  case "$PWD" in
    $HOME/<project-a>*) INFISICAL_TOKEN=$(_infisical_token) infisical run \
      --projectId="$INFISICAL_PROJECT_ID" --path="/<project-a>" -- command claude "$@" ;;
    $HOME/<project-b>*) INFISICAL_TOKEN=$(_infisical_token) infisical run \
      --projectId="$INFISICAL_PROJECT_ID" --path="/<project-b>" -- command claude "$@" ;;
    *) command claude "$@" ;;
  esac
}
```

Directories outside the match list run plain `claude` without
injection. The global `CLAUDE.md` instructs Claude to never save API
keys to shell files — always offer to add them to the right
Infisical project/folder instead.

## MCP project-isolation pattern

A memory MCP can be configured **per project** via `.mcp.json` rather
than globally. Claude running in a project directory then only sees
memories for that project — no cross-contamination.

Two tiers of isolation:

**Shared store** — sub-projects inside a common workspace share a
single backing store. No `--store` flag; the MCP entry walks up to find
the nearest `.mcp.json` and falls back to a default store path.

```
~/Workspace/.mcp.json             → memory-mcp                    → ~/.memory-mcp/default
~/Workspace/<sub-project>/.mcp.json → memory-mcp                  → ~/.memory-mcp/default (inherits)
```

**Separate store** — top-level independent projects each get their
own isolated store:

```
~/<project-a>/.mcp.json → memory-mcp --store ~/.memory-mcp/<project-a>
~/<project-b>/.mcp.json → memory-mcp --store ~/.memory-mcp/<project-b>
```

The server name stays consistent in each project, so hooks and tool
permissions (`mcp__<server>__*`) are identical everywhere.

If Claude is launched from any other directory, the memory MCP is
simply unavailable — by design.

## Agents

Agent files combine a frontmatter (name, description, tools, model,
optional MCP servers) with a prompt body. Drop any of these into
`~/.claude/agents/` and Claude Code routes to them automatically.

| Agent | What it does | Model |
|-------|--------------|-------|
| `ai-researcher` | Latest AI news digest — model releases, research papers, industry moves | haiku |
| `bash-scripter` | Writes and fixes bash/shell scripts — entrypoints, automation, setup scripts | sonnet |
| `docker-debugger` | Diagnoses Docker containers that crash, restart, or fail healthchecks. Knows secrets-manager + Docker Compose patterns | sonnet |
| `release-manager` | npm publish, GitHub releases, changelog, git tags | sonnet |
| `mempalace-admin` | MemPalace maintenance — auditing palace contents, cleanup, KG health | sonnet |
| `security-auditor` | Audits REST API and web apps for security vulnerabilities — QA-focused, not compliance auditing | sonnet |

> **QA agents** (test-architect, e2e-tester, bug-reporter, etc.) are
> published separately — see
> [qa-playbook](https://github.com/anastasiiaanfimova/qa-playbook).

## Skills

Methodology essays — process knowledge, decision frameworks,
anti-patterns. Tool-agnostic; designed to survive switching agent CLI /
MCP stack / memory tool.

These are **reference documents**, not drop-in slash commands. To
adapt one as a working skill in your environment, copy the directory
and replace the abstract references with your real MCP servers, file
paths, and tool names.

| Skill | What it covers |
|---|---|
| `workspace-setup` | One-time project bootstrap methodology — shared vs isolated context decision, phased setup, seed-structure rules for new isolated stores, the index+rules memory file pattern |
| `claude-cleanup` | Periodic agent-config audit methodology — survey-confirm-execute discipline, truth-source-vs-claim diff for stale-reference detection, duplicate / wrapper / parasitic-dir categories |
| `claude-audit` | Forward-looking "what should I build next?" retro — five proactive lenses (manual reps, agent errors, stuck workarounds, knowledge re-asked, dead capabilities), file-as-state with status lifecycle, internal+external signal cross-check |
| `history-cleanup` | Session-history rotation methodology — five independent decay axes, survey-confirm-clean phases, manual+hook split |
| `tooling-update` | Multi-package-manager update methodology — snapshot-update-snapshot pattern, parallel-where-safe vs sequential-where-required, pinned-version awareness, pre-flight upstream-issue scan |

## Pre-commit hook

`hooks/pre-commit` is a global git pre-commit hook that blocks private
project or service names from leaking into public repos. It scans
staged diffs only for repos under a specific GitHub owner (configured
in the hook) and only if the remote is public.

Git never auto-installs hooks on clone — set up once manually:

```bash
cp hooks/pre-commit ~/.git-hooks/pre-commit
chmod +x ~/.git-hooks/pre-commit
git config --global core.hooksPath ~/.git-hooks
```

The hook reads its deny list from `~/.git-hooks/forbidden.txt` (one
regex pattern per line; comments allowed). If the file doesn't exist,
the hook silently exits — create it before relying on protection:

```bash
cat > ~/.git-hooks/forbidden.txt <<'EOF'
# One pattern per line. Case-insensitive (hook uses grep -iE).
<private-project-a>
<internal-service>
<vault-name>
EOF
```

## How to adapt

Methodology repos work best when you treat them as starting points:

- Pick the agent, skill, or pattern you want
- Copy the file into your local setup
- Replace placeholders (`<project>`, `<scope>`, `<server>`, etc.)
  with your real names
- Adapt the prompt or workflow to your actual MCP servers, tools, and
  conventions

For agents and skills, the methodology file describes *the shape* of
the work; you fill in the specifics. For settings and hooks, the
example shows *the structure*; you bring your own commands.

[Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)

## Related public repo

[`qa-playbook`](https://github.com/anastasiiaanfimova/qa-playbook) —
methodology snapshots of QA skills. Adopted the methodology-only
pattern first; this repo followed by analogy.
