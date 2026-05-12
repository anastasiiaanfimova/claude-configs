# push-mirror — anonymization toolkit

Shared toolkit for keeping a private deny list (`forbidden.txt`) and a per-target
find-replace pipeline (`anon.py` + `replacements/<target>.md`) used when syncing
local files to a public repo.

The orchestrator scripts that used to live here (`push-mirror.sh`,
`commit-and-push.sh`, per-target `configs/`) were removed 2026-05-09 when both
public targets (`qa-playbook` and `claude-configs`) moved to a manual workflow.
What remains is the protection layer.

## Files

| File | Purpose |
|------|---------|
| `forbidden.txt` | Master deny list — patterns that must NOT appear in any public repo. Two consumers: the global git pre-commit hook (`~/.git-hooks/pre-commit`) and the `claude-config-push` skill's post-anonymization sanity check. |
| `anon.py` | Find-replace anonymizer. Reads `replacements/<target>.md`. Substitutes only — does NOT enforce `forbidden.txt`. The sanity check happens at the call site after anon runs. |
| `replacements/<target>.md` | Per-target find-replace rules. **Gitignored** — local-only. Format: `regex_pattern → replacement`. |

## Two-layer privacy model

The tooling has two independent safety nets:

1. **Pre-commit hook** (`~/.git-hooks/pre-commit`) — fires for any
   `anastasiiaanfimova/*` PUBLIC repo at `git commit` time. Scans staged diff
   against `forbidden.txt`. Blocks the commit on match. Catches anything that
   slipped past intentional anonymization.

2. **Post-anonymization sanity check** in skills like `claude-config-push` —
   after running `anon.py` to substitute private terms with placeholders, the
   skill greps the output against `forbidden.txt`. If anything still matches,
   the sync stops with the file/line surfaced. Forces the user to add a
   missing replacement rule before continuing.

Layer 1 is failsafe. Layer 2 catches problems earlier (during sync, not during
commit) and produces a more actionable error.

## Adding a new forbidden term

Edit `forbidden.txt`, one regex per line. Comments (`#`) and empty lines are
ignored. Both consumers re-read the file each time, so no rebuild needed.

## Adding a new replacement rule for a target

Edit `replacements/<target>.md`. Format:

```
private-pattern → <placeholder>
```

Patterns are Python regex. Lines without `→` are ignored. The file is
gitignored; rules stay local.

## Active consumers

| Consumer | What it uses |
|----------|--------------|
| `~/.claude/skills/claude-config-push/SKILL.md` | `anon.py` + `replacements/claude-configs.md` + `forbidden.txt` (sanity scan) |
| `~/.git-hooks/pre-commit` | `forbidden.txt` only |

If `claude-config-push` becomes the only consumer of `anon.py` AND the
pre-commit hook moves elsewhere, the toolkit becomes single-consumer and
should fold into the skill directory per the "helper used by one skill →
inside skill dir" rule. Currently `forbidden.txt` has two consumers (skill +
hook), so the lib stays.
