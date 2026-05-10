---
name: tooling-update
description: >-
  Methodology for keeping a multi-package-manager agent toolkit in sync —
  the snapshot/update/snapshot pattern, parallel-where-safe vs sequential-
  where-required, pinned-version awareness, and patch re-application
  reminders. Tool-agnostic — applies to any setup where one toolkit spans
  pip, uv, pipx, git+npm, plugin manager, etc.
---

# tooling-update

An agent toolkit is rarely installed through one package manager. Some
components live in pip, some in uv, some in pipx, some in
git+npm clones, some in a built-in plugin store. Each manager has its
own update command, its own version reporting, its own concurrency
constraints.

The methodology unifies the update flow and produces a clean
before/after report so the user can see what actually moved.

## Snapshot → update → snapshot

The pattern is three steps, not "run upgrade and hope":

1. **Snapshot before** — record current versions across all managers
2. **Run updates** — apply upgrade commands per component
3. **Snapshot after** — record new versions
4. **Diff** — produce a single table comparing before/after with one
   row per component

Why bother with explicit snapshots when most managers print "already
latest" or "upgraded to X" inline? Two reasons:

- Some managers don't show the *previous* version — only the new one
- Mixed-manager output is unreadable; a unified table tells the user
  "what actually changed" in one glance

## Parallel where safe, sequential where forbidden

Update commands are mostly independent — pip and uv don't lock against
each other. Run them in parallel to cut total time.

The exception is the agent's own plugin manager (`<agent> plugins
update`-style CLIs). These often serialize internally; running two
plugin updates concurrently produces races or silent skips. Run those
sequentially after the parallel batch completes.

Rule: parallel for separate-manager commands; sequential for
same-manager commands when the manager isn't reentrant.

## Pinned-version awareness — don't blindly upgrade

Some components have a known stable version that you've deliberately
pinned. An auto-upgrade silently moves them off the pinned point and
reintroduces the bug you were avoiding.

Before upgrading any pinned component:

- Read the recorded reason for the pin (a project memory file, a
  drawer, an inline note in the skill)
- Decide explicitly: "still pinning" (skip upgrade) or "trying the
  new version" (upgrade + re-test)
- Never default to "upgrade because the user said /update"

Output the pin awareness in the report — even if you skipped, the
user should see "pinned at X, not upgraded" rather than wonder why
the version didn't change.

## Patch re-application reminders

Some components have local patches applied on top of the upstream
version (workarounds for upstream bugs, inline fixes). A `pip install
--upgrade` overwrites the patch.

For each upgraded component with a known patch:

1. Note in the run output: "patch X needs re-applying after this
   upgrade"
2. Re-apply the patch as part of the upgrade flow, OR
3. Refuse to upgrade until the user confirms the patch will be
   re-applied

The choice depends on how automated the patch is. If it's a
one-liner, re-apply automatically. If it's a multi-step manual
edit, refuse to upgrade silently.

## Restart-required awareness

Some upgrades take effect on the next process invocation; others need
the agent CLI restarted entirely (MCP server upgrades, plugin
upgrades, sometimes the CLI itself).

End the report with a one-line restart note when applicable:

```
Restart the agent to apply MCP changes.
```

Skip the note when nothing was upgraded or all upgrades take effect
without restart.

## Failure-tolerant: log, continue, don't roll back

If one component's upgrade fails (network issue, missing manager, lock
contention) — log the failure, mark it in the table, continue with the
rest. Don't abort the whole run.

A successful run with one row showing `❌ failed: <error>` is far more
useful than a partial state with no record of what got through.

There's no rollback mechanic; partial upgrade is the steady state when
something goes wrong. The fix is to re-run after addressing the cause.

## Output shape

```
## Tooling update — YYYY-MM-DD

| Component       | Before  | After   | Result              |
|-----------------|---------|---------|---------------------|
| <component>     | X.Y.Z   | X.Y.Z+1 | ✅ updated          |
| <component>     | X.Y.Z   | X.Y.Z   | — already latest    |
| <pinned>        | X.Y.Z   | X.Y.Z   | 🔒 pinned, skipped  |
| <component>     | ?       | ?       | ❌ failed: <error>  |
```

After the table, surface side-effects:

- Patch re-application reminders for upgraded patched components
- Restart note if any upgrade requires it
- Brief summary line ("3 updated, 2 already latest, 1 pinned, 0 failed")

## Hard rules

- ✅ Snapshot before and after, always — table is the deliverable
- ✅ Parallel for independent managers; sequential for non-reentrant
  ones
- ✅ Pinned components are explicitly checked, not silently
  upgraded — and shown in the table even when skipped
- ✅ Patches re-applied (or refused) after upgrades that overwrite
  them
- ✅ Failure is per-component; one failure doesn't abort the run
- ❌ Don't print the manager's raw upgrade output as the report —
  unify into the table
- ❌ Don't skip the restart note when upgrades require restart —
  silent state divergence

## Anti-patterns

- ❌ "Upgrade everything to latest" without checking pins — silently
  reintroduces avoided bugs
- ❌ Aborting the whole run on one component failure — strands
  successful upgrades in an unreported state
- ❌ No before-snapshot ("upgrade and hope the manager prints
  versions") — half the report is missing
- ❌ Concurrent calls to a non-reentrant plugin manager — races and
  silent skips
- ❌ Forgetting to re-apply a known patch after upgrading the patched
  component — silently regresses to the upstream bug
- ❌ Restart note skipped when needed — the user works against stale
  MCP state and doesn't know
