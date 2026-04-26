---
name: push-config
description: >-
  Sync local ~/.claude/ files to github.com/anastasiiaanfimova/claude-configs,
  anonymizing private project names before push. Compares local vs repo,
  shows diffs, commits only changed files. Fully automatic.
  Trigger: "push-config", "обнови claude-configs", "запуши конфиги",
  "sync configs", "пуш конфигов".
version: 0.1.0
---

# Sync Claude Configs

Diffs local `~/.claude/` files against the GitHub repo, anonymizes private data,
commits changed files, and pushes.

## Config

### Repo
```
Owner:  anastasiiaanfimova
Repo:   claude-configs
Branch: main
Local:  /tmp/claude-configs
```

### Files to sync

| Local source | Repo path |
|---|---|
| `~/.claude/CLAUDE.md` | `CLAUDE.md` |
| `~/.claude/settings.json` | `settings/settings.json` |
| `~/.claude/agents/*.md` | `agents/` |
| `~/.claude/commands/setup.md` | `commands/setup.md` |
| `~/.mempalace/hook_agent.py` | `hooks/hook_agent.py` |
| `~/.mempalace/palace_detect.sh` | `scripts/palace_detect.sh` |

**Skills** — only the ones in this allowlist are synced (others may contain private project references):
```
PUBLIC_SKILLS = [
  claude-tooling
  push-config
]
```
Each skill is synced as `skills/<name>/SKILL.md`.

### Anonymization

Replacement rules and the privacy-scan pattern live in a **local-only** file (never synced):

```
~/.claude/skills/push-config/replacements.md
```

To add a new private project name, append a line:
```
(?i)newproject → <project>
```
Then update the `SCAN:` line at the bottom of that file to include it.

**Never anonymize:** `openclaw`, `hermes`, `claude`, `mempalace`, `anastasiiaanfimova` (GitHub owner).

---

## Workflow

### Step 0 — Clone or pull the repo

```bash
if [ -d /tmp/claude-configs/.git ]; then
  git -C /tmp/claude-configs pull --rebase --quiet
else
  git clone https://github.com/anastasiiaanfimova/claude-configs /tmp/claude-configs
fi
```

### Step 1 — Build anonymization function

Use this Python one-liner for each file. Run it as a function — apply to every file before diffing:

```python
# anon.py — reads patterns from local docs/replacements.md, applies to stdin
import sys, re, os

repl_file = os.path.expanduser('~/.claude/skills/push-config/replacements.md')
replacements = []
with open(repl_file) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('SCAN:'):
            continue
        if ' → ' in line:
            pat, rep = line.split(' → ', 1)
            replacements.append((pat.strip(), rep.strip()))

text = sys.stdin.read()
for pat, rep in replacements:
    text = re.sub(pat, rep, text)
print(text, end='')
```

Save to `/tmp/anon.py` once at the start of the skill run.

### Step 2 — Diff and copy each file

For each file pair (local → repo):

```bash
# Example for CLAUDE.md:
python3 /tmp/anon.py < ~/.claude/CLAUDE.md > /tmp/claude_anon.md
diff /tmp/claude_anon.md /tmp/claude-configs/CLAUDE.md
# If diff is non-empty → copy:
cp /tmp/claude_anon.md /tmp/claude-configs/CLAUDE.md
```

For **agents/**: loop over all `~/.claude/agents/*.md`, anonymize each, compare with repo file, copy if changed. Also check for **new files** (in local but not in repo) and **deleted files** (in repo but not in local) — add or remove accordingly.

For **commands/setup.md**:
```bash
mkdir -p /tmp/claude-configs/commands
python3 /tmp/anon.py < ~/.claude/commands/setup.md > /tmp/setup_anon.md
diff /tmp/setup_anon.md /tmp/claude-configs/commands/setup.md > /dev/null 2>&1 || cp /tmp/setup_anon.md /tmp/claude-configs/commands/setup.md
```

For **skills (PUBLIC_SKILLS only)**:
```bash
for name in claude-tooling push-config; do
  src="$HOME/.claude/skills/$name/SKILL.md"
  dest="/tmp/claude-configs/skills/$name/SKILL.md"
  [ -f "$src" ] || continue
  mkdir -p "$(dirname "$dest")"
  python3 /tmp/anon.py < "$src" > /tmp/skill_anon.md
  diff /tmp/skill_anon.md "$dest" > /dev/null 2>&1 || cp /tmp/skill_anon.md "$dest"
done
```

For **hook_agent.py** and **palace_detect.sh**: same pattern.

### Step 2b — Remove stale skills from repo

After syncing skills, check if the repo has any skill directories **not** in PUBLIC_SKILLS and delete them:

```bash
for repo_skill_dir in /tmp/claude-configs/skills/*/; do
  name=$(basename "$repo_skill_dir")
  if [[ "$name" != "claude-tooling" && "$name" != "push-config" ]]; then
    git -C /tmp/claude-configs rm -r "skills/$name"
    echo "DELETED stale skill from repo: skills/$name"
  fi
done
```

### Step 2c — Privacy scan

Before staging anything, scan all repo files for private names that should have been anonymized:

```bash
REPL_FILE="$HOME/.claude/skills/push-config/replacements.md"
SCAN_PATTERN=$(grep "^SCAN:" "$REPL_FILE" | sed 's/^SCAN: *//')

LEAKS=$(grep -rn "$SCAN_PATTERN" /tmp/claude-configs/ \
  --include="*.md" --include="*.json" --include="*.py" --include="*.sh" \
  2>/dev/null | grep -v ".git" | grep -v "anastasiiaanfimova")

if [ -n "$LEAKS" ]; then
  echo "PRIVACY LEAK DETECTED — aborting push:"
  echo "$LEAKS"
  echo "Fix replacements.md patterns and re-run."
  exit 1
fi
echo "Privacy scan: clean"
```

If any leaks are found → **stop immediately**, do not commit. Report which file and line contains the leak.

### Step 3 — Review and confirm

```bash
git -C /tmp/claude-configs status --short
```

If output is empty → print "claude-configs is up to date, nothing to push." and stop (no commit, no diary).

If changes exist → show the user what will be committed:
- List all changed files (`M` = modified, `A` = new, `D` = deleted)
- For each modified file show a compact diff (`git diff` for unstaged, the actual content delta)
- If any file was deleted from repo (e.g. stale skill) — call it out explicitly

**Then ask:** "Всё выглядит хорошо? Коммитить и пушить?" — and wait for confirmation before proceeding.

If the user has questions or wants to adjust anything — discuss and resolve before moving to Step 4.

### Step 4 — Update README.md (mandatory, before commit)

**Always run this step** — even if README.md itself wasn't in the diff. Any config change may make README stale.

Read `/tmp/claude-configs/README.md` and verify these sections match the current local state:

- **Hooks** (`settings.json` changed): hook names, count, sync/async notes — must match actual hooks in `settings.json`
- **Agents** (`agents/` changed): agent table rows — names, descriptions, models
- **Skills** (`skills/` changed): skill table rows — names, what they do
- **Memory stack** (any change): tool names, descriptions — must match tools actually configured
- **Credentials / vault** (`CLAUDE.md` changed): vault names, workflow still accurate

**Link rule — real links only.** Every tool or product mentioned in README must have a working URL. When adding or editing a mention:
1. Check if the tool already has a link in README — if yes, keep it
2. If no link exists: find the real one (GitHub repo, docs page, npm package) before writing
3. Never use placeholder links like `#`, `(link)`, or invented URLs
4. Format: `[Tool Name](https://real.url)` inline in the text or table cell

Known real links for this setup:
- MemPalace → check current link in README (maintained there)
- code-review-graph → check current link in README
- Superpowers → check current link in README
- episodic-memory → find via `npm info episodic-memory` or `pip show episodic-memory` or search GitHub before adding
- Claude Code hooks docs → `https://docs.anthropic.com/en/docs/claude-code/hooks`
- Infisical → `https://infisical.com`

Edit `/tmp/claude-configs/README.md` directly for any outdated sections. The README update is part of the same commit as the config changes — not a follow-up.

### Step 5 — Commit and push

```bash
cd /tmp/claude-configs

git add -A

CHANGED_FILES=$(git diff --cached --name-only | tr '\n' ' ')
git commit -m "sync configs $(date +%Y-%m-%d): $CHANGED_FILES"

git push origin main
```

Print the commit hash:
```bash
git -C /tmp/claude-configs log --oneline -1
```

### Step 6 — Write diary entry

`mcp__mempalace__mempalace_diary_write` with compact AAAK entry:
- Which files changed
- Commit hash
- Any anonymizations applied (e.g. "replaced <project>×3")
- Whether README was updated

Topic: `claude-configs.sync`

---

## Notes

- **Always anonymize before diffing** — even if the file looks clean, run it through anon.py.
- **Pre-commit hook** in the repo blocks private words as a safety net — if it fires, check anon.py patterns.
- `settings.local.json` is **never** synced — it's machine-local (paths, personal tokens).
- Project-scoped agents (e.g. in `~/Hermes/.claude/agents/`) are never synced here — only `~/.claude/agents/`.
- If a skill is NOT in PUBLIC_SKILLS but the user wants to add it → update this file's `PUBLIC_SKILLS` list and re-run.
