# claude-configs

My personal Claude Code configuration — hooks, CLAUDE.md examples, and patterns I use day-to-day. Feel free to adapt anything here.

## What's inside

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

## How to use

Copy what's useful, adjust paths and tool names to your setup. Claude Code hooks documentation: https://docs.anthropic.com/en/docs/claude-code/hooks
