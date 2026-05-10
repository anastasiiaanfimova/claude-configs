---
name: history-cleanup
description: >-
  Methodology for rotating an agent CLI's session history — what to keep,
  what to age out, and the manual+hook split that lets the same logic run
  silently in the background and on demand. Tool-agnostic — applies to any
  agent stack that writes per-session log files plus per-project state
  directories.
---

# history-cleanup

An agent CLI accumulates per-session artifacts: session log files
(usually JSONL), per-project state directories, hook approval logs,
subagent scratch dirs. None are individually large; all together, after
months of use, they bloat to gigabytes and slow down session startup.

The methodology: rotate aggressively on a few independent axes, never
touch durable artifacts, and run the same logic both in the background
(as a session-start hook) and on demand (for ad-hoc inspection).

## Five axes of cleanup

The session-history landscape has independent decay surfaces. Each
needs its own rule.

### Axis 1 — Approval log (size cap, not age)

The approval log records every per-command allow/ask decision. It
grows linearly with use and never benefits from old entries. Cap it
at a fixed line count (e.g. 500 lines) — that's plenty for inspecting
recent decisions.

Why size, not age: a heavily-used week produces 1000 lines; a quiet
month produces 50. Age-based truncation either loses the active
context or keeps stale junk.

### Axis 2 — Session logs (age cap)

Per-session JSONL transcripts: useful for auditing recent work, no
value beyond ~30 days. Search and memory layers index what matters;
the raw logs are just the medium.

Delete files older than the threshold. Don't try to be clever about
"keep the last N regardless of age" — age is the right axis.

### Axis 3 — Orphan subagent directories

Subagents leave per-session work directories. When their parent
session ends, the subagent dir often outlives the parent JSONL by
days. After enough time, the dir is unreachable from any active
session.

Detection: a directory under a project's session area, older than
the threshold, with no matching session JSONL alongside it. Delete.

### Axis 4 — Worktree-orphan project directories

If your stack creates per-worktree project directories that mirror
on-disk worktree paths, those directories outlive the worktrees they
were tied to (worktree gets removed, the corresponding `.<agent>`
project state lingers).

Detection: project state directory whose corresponding worktree
no longer exists on disk. Delete the orphan.

### Axis 5 — Dead-cwd projects (full purge)

A project state directory contains a recorded `cwd`. If that `cwd`
no longer exists (the project was moved or deleted), the entire state
directory is dead — there's no scenario where it'll be used again.

Detection: recorded cwd missing from disk + directory hasn't been
modified in the threshold window. Use the agent's native "purge"
operation if it exists (cleaner than `rm -rf` because it also clears
config-level entries) — otherwise delete the directory.

## Survey → confirm → clean

Same pattern as broader cleanup: read-only survey first, summarize
counts, ask, then act.

```
Survey:
  approval log: N lines (will trim to LIMIT)
  session logs >RETENTION days: N files, X MB
  orphan subagent dirs: N
  worktree-orphan project dirs: N
  dead-cwd projects: N

Confirm? (yes / no / pick categories)
```

Even when the same logic runs as a hook (silently), the manual mode
shows the survey and waits. The user's reason for invoking manually
is usually "let me see what's there" — silent execution defeats the
purpose.

## Manual + hook split

The same cleanup logic should run two ways:

| Mode | When | What it does |
|---|---|---|
| Hook (async, silent) | Each session start, after a debounce window | Trim approval log; delete files past thresholds; minimal logging |
| Manual (interactive) | User invokes for ad-hoc inspection | Survey + confirm + clean, with extra-aggressive options |

The hook keeps the steady-state under control. The manual invocation
is for "I noticed startup is slow" or "let me see what's accumulating."

Implementation note: the hook calls the same script as the manual
skill, with a flag that suppresses prompts. One source of truth for
the cleanup logic; two invocation modes.

## What never to delete

- The agent's per-project memory directory (`memory/` or equivalent)
  — that's durable user content, not session artifacts
- `local`-machine-only configs (`settings.local.*`) — explicitly
  excluded from sync, similarly excluded from cleanup
- Active session files (anything modified in the last few days)
- Any file in a directory the user is currently working in

The deletion list should be small and obviously safe. When in doubt,
leave it.

## Threshold defaults

These aren't dogma; they're starting points that work for most
single-developer setups:

- Approval log line cap: ~500
- Session log age: ~30 days
- Orphan dir age: ~30 days
- Dead-cwd minimum age: ~30 days

Tune for your usage. If the agent runs constantly, drop session log
retention to 14 days. If used rarely, extend to 60. The principle
matters more than the number.

## Hard rules

- ✅ Survey first, even when running as a hook (the hook just doesn't
  show the survey to the user; it logs internally)
- ✅ Manual mode is interactive — confirm before deleting
- ✅ Memory directories are never touched
- ✅ One source of truth (a script) for the cleanup logic; hook and
  manual both call it
- ✅ Detect dead cwd by *both* missing path AND age — a project the
  user is about to clone again shouldn't be purged
- ❌ Never delete files newer than the threshold "to be aggressive"
- ❌ Never duplicate the cleanup logic across hook and skill — drift
  inevitable
- ❌ Never silently skip categories — even an empty one should report
  zero

## Anti-patterns

- ❌ Age-based approval log truncation — produces junk-or-nothing
  depending on usage rhythm
- ❌ Deleting all session logs regardless of age — loses recent
  inspection value
- ❌ Purging by cwd alone, no age check — catches projects the user
  paused for two weeks
- ❌ Silent hook with no log line — when something goes wrong, you
  can't tell if the hook ran
- ❌ Different thresholds in the manual skill vs the hook — same
  logic, divergent behavior
