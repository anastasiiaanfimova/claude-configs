---
name: claude-config-push
description: >-
  Sync local ~/.claude/ files to github.com/anastasiiaanfimova/claude-configs,
  anonymizing private project names before push. Compares local vs repo,
  shows diffs, commits only changed files. Fully automatic.
  Trigger: "claude-config-push", "обнови claude-configs", "запуши конфиги",
  "sync configs", "пуш конфигов".
---

# Sync Claude Configs

Diffs local `~/.claude/` files against the GitHub repo, anonymizes private
data, commits changed files, and pushes.

The deterministic part (clone/pull, anonymize, diff, copy, stale-removal,
privacy scan, commit, push) lives in shared scripts under
`~/.claude/lib/push-mirror/`. This skill orchestrates them and handles the
parts that need human judgement (review, README update, diary).

## Constants

```
TARGET           = claude-configs
PUSH_MIRROR_DIR  = ~/.claude/lib/push-mirror
PUSH_MIRROR_SH   = ~/.claude/lib/push-mirror/push-mirror.sh
COMMIT_PUSH_SH   = ~/.claude/lib/push-mirror/commit-and-push.sh
REPO_LOCAL       = /tmp/claude-configs
REPO_URL         = https://github.com/anastasiiaanfimova/claude-configs
DIARY_WING       = wing_claude
DIARY_TOPIC      = claude-configs.sync
```

Target sources, registry sections, anonymization toggles, and extra files
are declared in `$PUSH_MIRROR_DIR/configs/claude-configs.sh` — single source
of truth, do not duplicate here.

## Workflow

### Step 1 — Run the sync script

```bash
~/.claude/lib/push-mirror/push-mirror.sh --target claude-configs
```

The script:
- clones or pulls `$REPO_LOCAL` (skips pull if local has uncommitted changes from a previous run)
- reads `~/.claude/skills/REGISTRY.yml` — sections `claude-configs` (skills) and `claude-configs-agents` (agents)
- anonymizes via `anon.py` using `replacements/claude-configs.md`
- copies extra files (`CLAUDE.md`, `settings/settings.json`) from the config
- copies skills as `skills/<name>/SKILL.md`
- copies agents as `agents/<name>.md` (anonymized — `ANONYMIZE_AGENTS=true` for this target)
- removes stale skills/agents from the repo (anything in repo but not in registry)
- runs the privacy scan against `forbidden.txt` — exits 1 if any forbidden pattern is found

**If the script exits non-zero** (privacy leak, missing config, etc.) — stop. Read the error, fix `replacements/claude-configs.md` (add missing rule) or `forbidden.txt`, re-run.

**If the script prints "claude-configs is up to date — nothing to commit"** — stop. No commit, no diary.

### Step 2 — Review changes with the user

Read git status:
```bash
git -C /tmp/claude-configs status --short
```

Show the user what will be committed:
- List all changed files (`M` = modified, `A` = new, `D` = deleted)
- For each modified file show a compact diff (the actual content delta)
- Call out deletions explicitly (e.g. "stale skill X removed")

**Then ask:** "Всё выглядит хорошо? Коммитить и пушить?" — wait for confirmation before Step 3.

### Step 3 — Update README.md (mandatory, before commit)

**Always run this step** — even if README.md itself wasn't in the diff. Any config change may make README stale.

Read `/tmp/claude-configs/README.md` and verify:

- **Hooks section** (`settings.json` changed): hook names, count, sync/async notes — must match actual hooks in the new `settings.json`
- **Memory stack section** (any change): tool names, descriptions — must match tools actually configured
- **Credentials / vault section** (`CLAUDE.md` changed): vault names, workflow still accurate

**Completeness check — run for every directory (always, not just when that dir changed):**

| Repo dir | README section | Row key | How to write a new row |
|---|---|---|---|
| `agents/` | `### \`agents/\`` tables | filename without `.md` | read agent file for description + model |
| `skills/` | `### \`skills/\`` tables | dir name | read `SKILL.md` description field |
| `scripts/` | `### \`scripts/\`` table | filename | read file header comment for purpose |
| `hooks/` | `### \`hooks/\`` table | filename | read file header comment for purpose |

Rules:
- File in repo but no row in README → add the row
- Row in README but no file in repo → remove the row
- File content changed → verify the row description still matches

**Link rule — real links only.** Every tool or product mentioned must have a working URL.
1. If the tool already has a link in README — keep it
2. If no link exists: find the real one (GitHub, docs, npm) before writing
3. Never use placeholders like `#`, `(link)`, or invented URLs
4. Format: `[Tool Name](https://real.url)`

Known real links for this setup:
- MemPalace, code-review-graph, Superpowers — check current link in README (maintained there)
- episodic-memory — find via `npm info episodic-memory` or `pip show` or GitHub before adding
- Claude Code hooks docs — `https://docs.anthropic.com/en/docs/claude-code/hooks`
- Infisical — `https://infisical.com`

Edit `/tmp/claude-configs/README.md` directly. README update is part of the same commit, not a follow-up.

### Step 4 — Commit and push

```bash
~/.claude/lib/push-mirror/commit-and-push.sh --target claude-configs
```

The script stages all changes, runs the global pre-commit hook explicitly (catches any leak that slipped past replacements), commits with `sync claude-configs YYYY-MM-DD: <files>`, pushes to `main`, and prints the new commit hash.

If the pre-commit hook blocks → fix the leak in `replacements/claude-configs.md` and re-run from Step 1.

### Step 5 — Diary entry

`mempalace_diary_write` with:
- `agent_name`: `"claude"`
- `wing`: `wing_claude`
- `topic`: `claude-configs.sync`
- `entry`: AAAK — files changed, commit hash, anonymizations applied (e.g. "replaced <project>×3"), whether README was updated

---

## Notes

- **`replacements/claude-configs.md`** — local-only (gitignored). Add a rule: `regex_pattern → replacement`. To add a name that should be **forbidden everywhere** (not just here), also append it to `~/.claude/lib/push-mirror/forbidden.txt`.
- **`forbidden.txt`** is the master deny-list — used by the global pre-commit hook (`~/.git-hooks/pre-commit`) for any commit to a public anastasiiaanfimova/* repo. After anon, the privacy scan greps the repo dir against this file.
- **`settings.local.json`** is **never** synced — machine-local (paths, personal tokens).
- **Project-scoped agents** (e.g. `~/Hermes/.claude/agents/`) are never synced — only `~/.claude/agents/`.
- **To add a skill:** add it to the `claude-configs:` section in `~/.claude/skills/REGISTRY.yml` — that's the only edit needed.
- **To add an agent:** add it to the `claude-configs-agents:` section.
