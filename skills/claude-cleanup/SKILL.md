---
name: claude-cleanup
description: >-
  Methodology for periodic agent-config audits — detecting stale references,
  duplicate documentation, useless wrappers, parasitic directories, and
  approval-log accumulation. Centers on the survey-confirm-execute pattern
  and the truth-source-vs-claim diff that powers stale detection.
  Tool-agnostic — applies to any agent stack with declarative configs and
  documentation files that drift.
---

# claude-cleanup

An agent's config decays the same way any code decays: rename a tool,
forget to update three docs that referenced it; add a new MCP server,
leave an old wrapper that does nothing; copy a setup pattern, forget
that another file already documented it. The mess is invisible day to
day and corrosive over months.

This methodology audits the decay in categorical passes, asks before
fixing, and updates the architecture snapshot at the end so the next
audit starts from a known-good baseline.

## Survey → confirm → execute (never auto-fix)

The audit is **never** allowed to fix things during the survey pass.
Agents that find issues and silently rewrite files corrupt trust the
first time they're wrong. The pattern is always:

1. **Survey** — read-only categorical scan, collect findings
2. **Confirm** — show the user grouped findings with proposed fixes,
   wait for explicit per-category yes/no/skip
3. **Execute** — apply only what was confirmed, one line of output
   per action taken

If a category's finding count is zero, say so explicitly (`— None ✓`).
A silent skip looks the same as a skipped check, and the user can't
tell whether the audit actually ran.

## The stale-reference category: truth-source-vs-claim diff

Most cleanup targets are claims about state that no longer match
reality. The audit gets leverage by being explicit about both sides:

- **Where the claim lives** — `file:line` of the text that asserts X
  exists / works / lives at path Y
- **Where ground truth lives** — the filesystem, the live config file,
  `which <binary>`, an MCP server's running state

The diff between them is the finding. Stale claim, stale entry,
mismatched name — all variations of "claim ≠ truth."

Pattern extraction:

| Claim type | Extract from text | Compare against |
|---|---|---|
| Tool/server name | Substring like `<scheme>__<name>__<call>` or backticked tool reference | Live config files (`.mcp.json` etc.) |
| Skill / agent name | Hyphenated lowercase identifiers in backticks or paths | Filesystem listing of skill/agent dirs |
| File path | Absolute or `~/`-prefixed paths in prose | `test -e <path>` |
| Frontmatter `name:` | Skill metadata | Directory name on disk |

Surface findings by file with the line and a one-line explanation:

```
~/.<agent>/skills/<skill>/SKILL.md:42 — references <old-tool>, not in current config
~/<project>/CLAUDE.md:13 — path ~/<deleted-dir>/ no longer exists
```

### Don't flag historical context

Documentation legitimately mentions things that don't exist anymore —
"was X, now Y", "deprecated as of date", "renamed to Z". Heuristic:
if a stale reference is colocated with markers like `was`, `old`,
`deprecated`, `renamed`, or `removed`, skip it. The reference is
deliberate.

### False positives belong in data, not regex

A pattern that misfires (e.g. matches a documentation token that
isn't really a tool name) goes into an excludes file alongside the
audit logic. Tweaking the regex to dodge specific cases couples the
detector to one project's vocabulary. The excludes file is data; it
travels with the audit and stays editable.

## The duplicate-source-of-truth category

A canonical source for any fact: skill spec, agent file, project
instructions, public README, architecture snapshot. A new file
covering the same topic is a duplicate worth flagging — divergence is
the cost.

Detection:

- Look for files in `docs/` directories, README variants, "overview"
  files
- For each candidate: cross-check what topics it covers against the
  canonical source list
- Flag if topic overlap with a canonical source is significant
  (>50% of sections / clear topical match)

For each flagged duplicate, name the canonical source explicitly
("`docs/X.md` covers MCP setup already in `<project>/CLAUDE.md`")
and propose deletion. The user might keep it for a reason; surface
the conflict, don't delete unilaterally.

## The wrapper-script category

MCP server descriptors sometimes call wrapper scripts (`start.sh`,
custom invocations). Many of these are legitimate; some are
historical wrappers that wrap nothing.

For each wrapper, read the contents and ask:

- Does it only rename an env var? → recommend renaming at the source
  (secrets manager) instead
- Does it only set a static URL/host? → move into the descriptor's
  env block
- Does it pass a secret as a CLI flag? → consider inline
  `sh -c "..."` invocation
- Does it just call an upstream package with no logic? → can be
  removed; descriptor calls upstream directly

A removed wrapper is one less file to forget to update.

## The parasitic-directory category

Multiple agents/extensions sometimes target the same project layout
under different directory names (`.cursor/`, `.agents/`, etc.). When
your stack canonicalizes one (`.<agent>/`), the others are
copy-paste residue from following someone else's setup guide and
should go.

Search project roots for "alternate" agent-config directories. Flag
each with one line explaining why the canonical one is sufficient.

## The approval-log category

If your agent keeps a log of approval decisions (allow/ask/deny),
that log is signal for what to add to the allow-list. Mining it:

1. Extract frequent ASK patterns (≥ 2 occurrences)
2. Filter dangerous patterns explicitly (`rm -rf`, `kill`, `sudo`,
   shell flow control, archive-extraction wildcards) — never propose
   these for allow even if they're frequent
3. Cross-reference with current allow rules; skip duplicates
4. For the rest, propose a generalized rule (file paths and hashes
   replaced by globs)

Show the proposal grouped by safe-to-allow vs filtered, with counts.
Wait for confirmation before editing the config. Insert allow rules
in the right scope position (some rule systems are
last-match-wins — placement matters).

## Closing pass: refresh the architecture snapshot

After fixes are applied, the architecture record (whatever your team
uses to capture "current state of the agent setup") needs to reflect
the new reality. Otherwise the next audit starts from a stale
baseline.

This pass:

1. Find the existing architecture snapshot drawer / doc
2. Replace with current state (skill list, MCP config summary,
   notable structural decisions made today)
3. Write a diary entry recording what was cleaned

The closing pass is non-optional. Skipping it is how the audit's
findings end up in the *next* audit as fresh "stale references."

## Hard rules

- ✅ Survey → confirm → execute, never auto-fix during survey
- ✅ Surface zero-finding categories explicitly (`— None ✓`)
- ✅ Stale detection compares claim location to truth source location
- ✅ Don't flag historical context (deprecated/renamed/was)
- ✅ Excludes file for false positives, not regex tweaks
- ✅ Refresh the architecture snapshot at the end
- ❌ Never auto-delete during the survey
- ❌ Never propose dangerous approval rules even if frequent
- ❌ Never overwrite a `local`-machine-only config (`settings.local.*`
  or equivalent) — those are intentionally not shared

## Anti-patterns

- ❌ Mass-delete on a single user "yes" without per-category
  confirmation — one wrong category and you've trashed something
- ❌ Silent zero-finding categories — looks the same as a skipped
  check
- ❌ Tweaking regex to dodge a specific false positive — couples the
  detector to one project's vocabulary
- ❌ Flagging "was X, now Y" notes as stale — they're documentation
- ❌ Skipping the closing snapshot refresh — guarantees next audit
  re-finds the same fixed issues
- ❌ Bundling unrelated cleanup categories ("cleanup the agent setup")
  — confirmation discipline only works at the category level
