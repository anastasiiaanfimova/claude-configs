# Resources

Useful repositories and references for Claude Code setup, agents, and tooling.
Worth checking periodically for new patterns and updates.

## Claude Code configuration & agents

### Curated lists
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — most comprehensive index: agents, hooks, CLAUDE.md templates, slash commands, status lines, MCP configs
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — 100+ subagents by task type, with correct YAML frontmatter

### Real setups (copy & adapt)
- [elizabethfuentes12/claude-code-dotfiles](https://github.com/elizabethfuentes12/claude-code-dotfiles) — syncing ~/.claude via Git: what to version, what to exclude (.gitignore patterns)
- [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) — end-to-end example: quality gate hooks, slash commands orchestrating agents, GitHub Actions integration
- [trailofbits/claude-code-config](https://github.com/trailofbits/claude-code-config) — production setup from Trail of Bits security team

### Hooks
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) — hook lifecycle patterns, Python+uv implementation
- [karanb192/claude-code-hooks](https://github.com/karanb192/claude-code-hooks) — copy-paste-ready hook collection
- [nizos/tdd-guard](https://github.com/nizos/tdd-guard) — hooks that block file changes violating TDD principles; good reference for quality gate patterns
- [ldayton/Dippy](https://github.com/ldayton/Dippy) — auto-approve safe bash commands via AST; reduces permission fatigue without disabling safety

### Tooling
- [agent-sh/agnix](https://github.com/agent-sh/agnix) — linter for CLAUDE.md, agents, hooks, skills; IDE plugins included; useful when managing many agents

### Skills & workflows
- [trailofbits/skills](https://github.com/trailofbits/skills) — 15+ security skills: CodeQL, Semgrep, variant analysis, fix verification; good reference for security-auditor agent
- [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) — solo dev workflow with multi-auditor patterns, micro-checkpoints, parallel agents

### Reference
- [Anthropic CLAUDE.md](https://github.com/anthropics/claude-code-action/blob/main/CLAUDE.md) — official reference implementation from Anthropic
- [Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)
