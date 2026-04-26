---
name: cleanup-history
description: >-
  Manual Claude Code history cleanup — shows what will be deleted, asks for
  confirmation, then cleans. Trims hook-approvals.log to 500 lines; removes
  .jsonl session logs older than 30 days; removes orphaned subagent dirs.
  Trigger: "cleanup history", "почисти историю", "claude-cleanup", "прибраться в истории".
version: 1.0.0
---

## Your task

Clean up Claude Code session history. Three phases: survey → confirm → clean.

### Phase 1 — Survey (read-only)

Report current state:

```bash
# Log file size
LOG="$HOME/.claude/hook-approvals.log"
wc -l "$LOG" 2>/dev/null && echo "lines in hook-approvals.log" || echo "hook-approvals.log not found"

# Count old .jsonl files (>30 days)
find "$HOME/.claude/projects" -maxdepth 2 -name "*.jsonl" -mtime +30 2>/dev/null | wc -l

# Total size of old .jsonl files
find "$HOME/.claude/projects" -maxdepth 2 -name "*.jsonl" -mtime +30 2>/dev/null | xargs du -ch 2>/dev/null | tail -1

# Orphaned subagent dirs (no matching .jsonl, >30 days)
for dir in "$HOME/.claude/projects"/*/; do
  find "$dir" -maxdepth 1 -mindepth 1 -type d -mtime +30 ! -name "memory" ! -name "subagents" | while read -r d; do
    base=$(basename "$d")
    [ ! -f "${d}.jsonl" ] && echo "$d"
  done
done
```

Show the user a summary:
- `hook-approvals.log`: N lines (will be trimmed to 500)
- `.jsonl` session logs older than 30 days: N files, X MB
- Orphaned subagent dirs: N dirs

### Phase 2 — Confirm

Ask: "Почистить? (hook-approvals.log → 500 строк, старые логи → удалить)"

Wait for confirmation before proceeding.

### Phase 3 — Clean

Run `bash ~/.claude/scripts/cleanup_history.sh` and report what was done.
