---
name: sync-configs
description: >-
  Sync local ~/.claude/ files to github.com/anastasiiaanfimova/claude-configs,
  anonymizing private project names before push. Compares local vs repo,
  shows diffs, commits only changed files. Fully automatic.
  Trigger: "sync-configs", "обнови claude-configs", "запуши конфиги",
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
| `~/.mempalace/hook_agent.py` | `hooks/hook_agent.py` |
| `~/.mempalace/palace_detect.sh` | `palace_detect.sh` |

**Skills** — only the ones in this allowlist are synced (others may contain private project references):
```
PUBLIC_SKILLS = [
  agent-vault-cli
  agent-vault-http
  claude-tooling
  sync-configs
]
```
Each skill is synced as `skills/<name>/SKILL.md`.

### Anonymization

Apply these replacements to **every file before writing to repo**:

| Pattern | Replace with |
|---|---|
| `/Users/<user>/` | `/Users/<user>/` |
| `~/<user>/` | `~/<user>/` |
| `<email>` | `<email>` |
| `<project>` (case-insensitive) | `<project>` |
| `<project>` (case-insensitive) | `<project>` |
| `<project>` | `<project>` |
| `--vault <project>` | `--vault <project>` |
| `--vault <project>` | `--vault <project>` |
| `--vault <project>` | `--vault <project>` |

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
# anon.py — apply to stdin, print to stdout
import sys, re

text = sys.stdin.read()
replacements = [
    (r'/Users/<user>/', '/Users/<user>/'),
    (r'~/<user>/', '~/<user>/'),
    (r'anastasiia\.anfimova@gmail\.com', '<email>'),
    (r'(?i)<project>', '<project>'),
    (r'(?i)<project>', '<project>'),
    (r'<project>', '<project>'),
    (r'--vault <project>', '--vault <project>'),
    (r'--vault <project>', '--vault <project>'),
    (r'--vault <project>', '--vault <project>'),
]
for pattern, repl in replacements:
    text = re.sub(pattern, repl, text)
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

For **skills (PUBLIC_SKILLS only)**:
```bash
for name in agent-vault-cli agent-vault-http claude-tooling sync-configs; do
  src="$HOME/.claude/skills/$name/SKILL.md"
  dest="/tmp/claude-configs/skills/$name/SKILL.md"
  [ -f "$src" ] || continue
  mkdir -p "$(dirname "$dest")"
  python3 /tmp/anon.py < "$src" > /tmp/skill_anon.md
  diff /tmp/skill_anon.md "$dest" > /dev/null 2>&1 || cp /tmp/skill_anon.md "$dest"
done
```

For **hook_agent.py** and **palace_detect.sh**: same pattern.

### Step 3 — Check if anything changed

```bash
git -C /tmp/claude-configs status --short
```

If output is empty → print "claude-configs is up to date, nothing to push." and stop (no commit, no diary).

If changes exist → list them for the user:
- `M` = modified
- `A` = new file
- `D` = deleted

### Step 4 — Commit and push

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

### Step 5 — Write diary entry

`mcp__mempalace__mempalace_diary_write` with compact AAAK entry:
- Which files changed
- Commit hash
- Any anonymizations applied (e.g. "replaced <project>×3")

Topic: `claude-configs.sync`

---

## Notes

- **Always anonymize before diffing** — even if the file looks clean, run it through anon.py.
- **Pre-commit hook** in the repo blocks private words as a safety net — if it fires, check anon.py patterns.
- `settings.local.json` is **never** synced — it's machine-local (paths, personal tokens).
- Project-scoped agents (e.g. in `~/Hermes/.claude/agents/`) are never synced here — only `~/.claude/agents/`.
- If a skill is NOT in PUBLIC_SKILLS but the user wants to add it → update this file's `PUBLIC_SKILLS` list and re-run.
