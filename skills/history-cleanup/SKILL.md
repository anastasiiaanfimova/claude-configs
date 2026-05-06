---
name: history-cleanup
description: >-
  Manual Claude Code history cleanup — shows what will be deleted, asks for
  confirmation, then cleans. Trims hook-approvals.log to 500 lines; removes
  .jsonl session logs older than 30 days; removes orphaned subagent dirs;
  removes project dirs whose worktree no longer exists; purges full project
  state (transcripts/tasks/file-history/config-entry) for projects whose cwd
  no longer exists on disk via native `claude project purge`.
  Note: the cleanup script also runs automatically as an async SessionStart hook,
  so manual invocation is for ad-hoc inspection or extra-aggressive cleanup.
  Trigger: "cleanup history", "почисти историю", "history-cleanup", "прибраться в истории".
---

# history-cleanup — Claude Code Session History Cleanup

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

# Worktree-orphan project dirs (worktree no longer exists)
for dir in "$HOME/.claude/projects"/*--claude-worktrees-*; do
  [ -d "$dir" ] || continue
  branch="${dir##*--claude-worktrees-}"
  found=0
  for wt in "$HOME"/*/.claude/worktrees; do
    [ -d "$wt/$branch" ] && { found=1; break; }
  done
  [ $found -eq 0 ] && echo "$dir"
done

# Dead-cwd projects (cwd no longer exists, dir not modified in 30+ days)
for dir in "$HOME/.claude/projects"/*/; do
  base=$(basename "$dir")
  case "$base" in *--claude-worktrees-*) continue ;; esac
  [ -n "$(find "$dir" -maxdepth 0 -mtime -30 2>/dev/null)" ] && continue
  jsonl=$(ls "$dir"*.jsonl 2>/dev/null | head -1)
  [ -z "$jsonl" ] && continue
  cwd=$(python3 -c "
import json
try:
  with open('$jsonl') as f:
    for line in f:
      try:
        d=json.loads(line)
        if 'cwd' in d: print(d['cwd']); break
      except: pass
except: pass
" 2>/dev/null)
  [ -n "$cwd" ] && [ ! -d "$cwd" ] && echo "$base → $cwd"
done
```

Show the user a summary:
- `hook-approvals.log`: N lines (will be trimmed to 500)
- `.jsonl` session logs older than 30 days: N files, X MB
- Orphaned subagent dirs: N dirs
- Worktree-orphan project dirs: N dirs
- Dead-cwd projects (will be purged via `claude project purge`): N dirs

### Phase 2 — Confirm

Ask: "Почистить? (hook-approvals.log → 500 строк, старые логи → удалить)"

Wait for confirmation before proceeding.

### Phase 3 — Clean

Run `bash ~/.claude/scripts/history-cleanup.sh` and report what was done.
