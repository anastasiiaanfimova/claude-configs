---
name: claude-audit
description: >-
  Methodology for the "what should I build next?" retrospective for an agent
  toolkit — distinct from "what's broken now?" cleanup. Reads past records
  (diary, memory) through five proactive lenses, cross-references external
  changelog signal, and maintains a running suggestions file with a status
  lifecycle that survives across audits. Tool-agnostic.
---

# claude-audit

A toolkit retro is the cheapest way to surface what *should* be built
next. The trap is treating it as a feelings exercise — asking "what
felt slow?" — instead of as a signal-mining exercise. The user's pain
is already recorded across diary entries, memory files, and prior
unfinished work; the audit's job is to read those signals carefully
and translate them into concrete suggestions with priorities.

This is a different skill from cleanup (which fixes broken things now).
Cleanup is reactive; audit is forward-looking.

## What this is, and isn't

| Is | Isn't |
|---|---|
| A retro on what's missing or repeatedly painful | A summary of what got done |
| Suggestions for new skills / automations / rules | A status report |
| Anchored in concrete signals (diary, memory) | A wishlist |
| File-as-state with a status lifecycle | A throwaway snapshot |

## File-as-state, not throwaway report

The audit writes to a single file (an `IMPROVEMENTS.md` or equivalent)
whose **state persists across runs**. Each item carries a status:

- `🆕` — surfaced this run, new
- `🔄 pending` — surfaced previous run, still relevant
- `✅ done` — completed, kept for history (never deleted)
- `💡 idea` — speculative, parked

When you re-run the audit:

- Existing `🔄` items: keep as `🔄` unless current evidence shows they're
  resolved → move to `✅`
- Existing `✅` items: always preserved; the history is part of the
  artifact's value
- Existing `🆕` items from the previous run: become `🔄` if still
  relevant, otherwise stay archived
- This run's findings: start as `🆕`

Never delete `✅` items. The "done" section is the record of what was
worth building, and it's the lookup answer for "did I already think of
this?"

## Five lenses (run all five, never silently skip)

Diary entries surface explicit pains, but a lot of friction is implicit
— habits the user hasn't named, mistakes the agent doesn't notice. Five
proactive lenses force the audit to look at less-obvious signal.

For each lens: collect candidates, tag with the lens that found them,
include evidence (diary dates or specific entries). If a lens returns
nothing, write `Lens N: clean` explicitly. **Silent omission is not
allowed** — looks identical to a skipped check.

### Lens 1 — Repeating manual actions (3+ sessions → automation candidate)

Look for repeated step sequences across sessions:

- Same bash sequence run before similar tasks
- Steps the user does by hand that already exist in a skill (skill
  isn't triggering, or is incomplete)
- Routines like "before each X I always Y" — if Y isn't automated,
  candidate

The question for each: lib helper, skill, hook, or scripts directory?

### Lens 2 — Repeating agent errors (my own patterns → rule or hook)

Find errors the agent itself repeats:

- MCP signature drift (params guessed wrong, retry needed) — candidate
  for a documented gotcha next to that tool's config
- Rationalization (defending a bad choice that the user pushed back on)
- The same workaround reapplied 3+ times
- Existing rule found in memory but not applied — candidate to
  strengthen the rule's wording or add a hook check

The question: formalize as a behavior rule, or move into an
automated check?

### Lens 3 — Stuck workarounds (2+ sessions, never fixed → escalate)

Workarounds quoted in diary 2+ times that haven't graduated to a real
fix:

- "Workaround = X because Y doesn't work" — candidate to fix Y
  upstream / replace Y / open an issue
- "We're routing around X for now"
- Workaround that appeared >30 days ago and is still in use — extra red

The question: have any been resolved upstream already? (Cross-check
with external-changelog signal.)

### Lens 4 — Knowledge re-asked (user explained, agent forgot)

Moments where the user explained something that should have been
recorded — the next session asks again:

- "User told me X" in one session, no corresponding memory entry,
  next session "what is X?"
- "User confirmed Y without arguing" — implicit validations of an
  unusual choice; should be recorded as feedback even though the
  user didn't push back

The question: what kind of memory file does this belong in?

### Lens 5 — Dead capabilities (declared but never used)

Compare declared capabilities against actual usage in the audit
window:

- Skill in the skills directory but 0 invocations in diary →
  candidate to delete or rewrite the description (not triggering)
- MCP server connected but 0 tool calls → candidate to disconnect
  (token cost for tool listing is real)
- Agent file present but never dispatched → candidate to delete

The question: remove or fix?

## Multi-source signal — internal + external

Internal signal (the five lenses) tells you what's painful in the
current setup. External signal — vendor changelogs, public release
notes — tells you what's newly possible. Cross-check the two:

- A stuck workaround (Lens 3) might be solved by a recent upstream
  release
- A dead capability (Lens 5) might be replaced by a newer alternative
- A repeating manual action (Lens 1) might have a built-in solution
  shipped this month

Add an "external updates" section that summarizes new vendor features
and explicitly cross-references existing pain entries.

## Time window: state it explicitly

Default: ~14 days. Wide enough to catch recurring patterns, narrow
enough to skip stale frustrations from already-fixed problems.

State the actual range in the output ("from YYYY-MM-DD to YYYY-MM-DD,
N entries"). The reader knows what slice the audit reflects.

If fewer than 3 entries fall in window, say so and skip — there's not
enough signal to mine.

## Diary supplements compressed memory

Diary entries are intentionally compressed. When a candidate's evidence
is one sentence in the diary that doesn't explain *why* it was a pain,
supplement with raw conversation search using the entry's date plus a
key term. Compressed signal + raw context = a confident finding.

## Priority — frequency, not feel

| Priority | Trigger |
|---|---|
| HIGH | Seen in diary ≥2 times, OR blocks regular workflow |
| MEDIUM | Mentioned once, OR useful but not urgent |
| LOW / parking | Speculative, nice-to-have |

Resist priority by gut. A single mention rarely justifies HIGH; three
mentions rarely justifies LOW.

## Output shape

```
## Audit — YYYY-MM-DD (range YYYY-MM-DD to YYYY-MM-DD, N entries)

### 🔄 Pending — carried over

| # | Idea | Source | Priority |
|---|---|---|---|
| 1 | ... | (lens or signal) | HIGH |

### 🆕 New suggestions

| # | Idea | Lens | Evidence | Priority |
|---|---|---|---|---|
| 1 | ... | Lens 2 | diary YYYY-MM-DD, YYYY-MM-DD | MEDIUM |

### 📡 External updates worth knowing

- **Feature** — what it does, why relevant, cross-reference to a
  pending item if applicable

### ✅ Done

(history; never removed)
```

If the file gets above ~50 items, merge similar suggestions.
Long lists with no prioritization are a sign of insufficient
prioritization, not of thorough analysis.

## Closing diary entry

After writing the audit, record a compact diary entry:

- Date range analysed
- Count of new suggestions / updated pending / external updates
- Topic tag matching the audit (e.g. `tooling-audit`)

Lets future audits find this run.

## Hard rules

- ✅ Run all five lenses, with explicit `Lens N: clean` if empty
- ✅ State the time window explicitly in the header
- ✅ Persist state across runs (file-as-state)
- ✅ Never delete `✅ done` items
- ✅ Cross-check internal pain against external changelog signal
- ❌ Don't manufacture suggestions when diary shows no clear pains —
  say so explicitly and re-run later
- ❌ Don't use audit as session summary or status report — those are
  separate artifacts (the daily log)
- ❌ Don't suggest from speculation — every suggestion needs concrete
  evidence

## Anti-patterns

- ❌ "Great progress this week!" — that's a vibes report, not an
  audit
- ❌ Bundling 5 unrelated improvements into one item — delays the
  important one
- ❌ Suggesting the same thing every audit and never building it — if
  it's been HIGH for three audits running, raise it explicitly with
  the user
- ❌ Long output (>50 items) — signals insufficient prioritization
- ❌ Suggesting based on a single entry from 2 weeks ago that isn't
  a pattern — windows mean recency, not archival
- ❌ Silent skip on a lens — indistinguishable from "I forgot to run
  it"
