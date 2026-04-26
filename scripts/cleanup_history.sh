#!/bin/bash
# Auto-cleanup of Claude Code conversation history older than 30 days
# Runs on session Stop hook. Keeps current session and memory/ dirs intact.

# Trim hook-approvals.log to last 500 lines
LOG="$HOME/.claude/hook-approvals.log"
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 500 ]; then
  tail -500 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi

PROJECTS_DIR="$HOME/.claude/projects"
MAX_AGE_DAYS=30

find "$PROJECTS_DIR" -maxdepth 2 -name "*.jsonl" \
  ! -newer "$PROJECTS_DIR" \
  -mtime +$MAX_AGE_DAYS \
  -delete 2>/dev/null

# Remove orphaned subagent dirs (UUID dirs with no matching .jsonl)
for dir in "$PROJECTS_DIR"/*/; do
  find "$dir" -maxdepth 1 -mindepth 1 -type d \
    -mtime +$MAX_AGE_DAYS \
    ! -name "memory" \
    ! -name "subagents" | while read -r d; do
      # Only delete if no recent .jsonl with same name exists
      base=$(basename "$d")
      if [ ! -f "${d}.jsonl" ]; then
        rm -rf "$d" 2>/dev/null
      fi
    done
done
