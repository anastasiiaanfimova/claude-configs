---
name: update-tooling
description: Update all Claude-related tools to their latest versions — MemPalace, code-review-graph, episodic-memory, notebooklm-mcp, and Claude plugins (superpowers, warp). Use this skill whenever the user says "update tools", "обнови тулы", "обнови клода", "check for updates", "update mcp", "update plugins", or asks to update any Claude MCP server, plugin, or related tool.
---

# update-tooling

Updates all Claude MCP servers and plugins to their latest versions. Fully autonomous — runs without user input.

## Components

| Component | Manager |
|---|---|
| `mempalace` | pip (dedicated venv at `~/.mempalace/venv`) |
| `code-review-graph` | uv tool |
| `notebooklm-mcp` | pipx (package: `notebooklm-mcp-cli`) |
| `episodic-memory` | git repo at `~/.episodic-memory` + npm |
| `superpowers` plugin | `claude plugins` |
| `warp` plugin | `claude plugins` |
| `chrome-devtools` | npx `@latest` — auto-updates on each MCP start, no action needed |

---

## Workflow

### Step 1 — Snapshot current versions

Run in parallel to get before-state:

```bash
/Users/<user>/.mempalace/venv/bin/pip show mempalace 2>/dev/null | grep Version | awk '{print $2}'
uv tool list 2>/dev/null | grep code-review-graph
pipx list 2>/dev/null | grep notebooklm
node -e "const p=require('/Users/<user>/.episodic-memory/package.json'); console.log(p.version)" 2>/dev/null
claude plugins list 2>/dev/null
```

Store these values — they'll be used in the final report.

### Step 2 — Run updates

Run the pip/uv/pipx/git updates in parallel, then claude plugin updates sequentially (the CLI doesn't support concurrent plugin operations).

**Parallel:**
```bash
# mempalace
/Users/<user>/.mempalace/venv/bin/pip install --upgrade mempalace 2>&1 | grep -E "Successfully|already"

# code-review-graph
uv tool upgrade code-review-graph 2>&1

# notebooklm-mcp
pipx upgrade notebooklm-mcp-cli 2>&1 | grep -E "upgraded|already"

# episodic-memory
cd /Users/<user>/.episodic-memory && git pull 2>&1 | tail -1 && npm install --silent 2>&1 | tail -1
```

**Sequential (after parallel completes):**
```bash
claude plugins update superpowers@claude-plugins-official 2>&1 | tail -3
claude plugins update warp@claude-code-warp 2>&1 | tail -3
```

If any command errors (tool not found, network issue), note it in the report but continue with the rest.

### Step 3 — Snapshot new versions

Repeat Step 1 to get after-state.

### Step 4 — Print report

Format a summary table comparing before and after:

```
## Tooling update — YYYY-MM-DD

| Component       | Before  | After   | Result            |
|-----------------|---------|---------|-------------------|
| mempalace       | 3.3.3   | 3.3.4   | ✅ updated        |
| code-review-graph | 2.3.1 | 2.3.1   | — already latest  |
| notebooklm-mcp  | 0.5.26  | 0.5.27  | ✅ updated        |
| episodic-memory | 1.0.15  | 1.0.16  | ✅ updated        |
| superpowers     | 5.0.7   | 5.0.8   | ✅ updated        |
| warp            | 2.0.0   | 2.0.0   | — already latest  |
| chrome-devtools | @latest | @latest | — auto            |
```

If anything was updated: add a note — **"Restart Claude Code to apply MCP changes."**

If everything was already latest: say so and skip the restart note.
