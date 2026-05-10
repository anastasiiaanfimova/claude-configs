---
name: workspace-setup
description: >-
  Methodology for one-time agent context bootstrap on a new project — the
  scoping decision (shared vs isolated), the phased order (infrastructure
  before content), and what should and shouldn't be seeded at first init.
  Tool-agnostic — applicable to any agent stack with a knowledge layer plus
  per-project memory.
---

# workspace-setup

Bootstrapping a project for an agent is two decisions stacked: **what
scope of memory should this project share with others**, and **in what
order do you wire the pieces so the agent can use them in this same
session**. Get scope wrong and contexts bleed; get order wrong and you
spend the first session debugging plumbing instead of working.

## The scoping decision: shared vs isolated context

Before touching files, decide which context bucket this project belongs to:

- **Shared** — the project belongs to a workspace where multiple
  sub-projects collaborate on related work. Memory pools together; the
  agent crossing project boundaries inside this workspace finds what it
  needs.
- **Isolated** — the project is a top-level concern with its own domain,
  audience, or compliance posture. Mixing memory with another project
  would leak context (work topics into personal projects, client A into
  client B).

The default heuristic: a project nested inside a known workspace
directory → shared. A standalone top-level project directory → isolated.

Get this wrong in one direction (sharing where it should be isolated)
and you'll spend cleanup time later splitting palaces / pruning
cross-talk. Get it wrong in the other (isolating what should be shared)
and you'll be re-explaining the same context to the agent every time
you cross a sub-project boundary. Slightly safer to err toward
isolation — merging is easier than splitting after the fact.

## Phased setup: infrastructure first, restart, then content

Agent CLIs typically only see MCP servers and permission settings at
session start. Wiring an MCP server in the middle of a setup session
won't expose its tools to the same session — you have to restart.

This forces a phase split:

### Phase 1 — Infrastructure (no agent calls)

Edit the configuration files that the next session will read:

- The MCP/server descriptor (`.mcp.json` or equivalent) — declare the
  servers this project needs
- The local permission file (whatever the agent uses for project-level
  allow-lists) — grant the new servers permission to be called
- Both are merge operations, not overwrites — a project may already
  have other MCP servers configured

Then **stop**. Tell the user to restart the agent in this directory and
re-run the setup. Do not pretend you'll be able to call the new servers
in the current session — the call will fail or return stale state.

### Phase 2 — Content (after restart)

Now the new servers are live. This phase populates them:

- Verify the agent can reach the new infrastructure (a status call to
  confirm)
- Seed any structural conventions for new isolated stores (see below)
- Create per-project memory files
- Record the project in the knowledge graph
- Write a diary entry that captures what setup happened

Phase 2 only runs when Phase 1 verification passes. If the user
re-invokes setup before restarting → detect that the new servers are
unavailable and refuse to proceed past Phase 1. The error message
should be specific ("restart and re-run") rather than the generic MCP
failure.

## Seed structure for new isolated contexts

A fresh isolated knowledge store starts empty. If you don't seed it
with conventions on day one, every drawer/entry you add later
accumulates ad-hoc. Seed once, the pattern follows.

Useful seed content for an isolated store:

- **Room/category schema** — what each top-level container is for
  (`decisions` / `config` / `recipes` / `rules` etc., names that match
  your taxonomy)
- **Naming convention** for tool-specific entries (e.g. `<tool>.mcp` for
  per-tool config drawers)
- **What not to store** — output dumps, ephemeral state, info derivable
  from code/git
- **Deduplication protocol** — when two entries overlap, which wins

Skip seeding if the project joins a shared store — the conventions live
there already.

## Memory file pattern: auto-loaded index plus on-demand details

Per-project memory files split by access pattern:

| File | Loaded | Purpose |
|---|---|---|
| Index file (e.g. `MEMORY.md`) | Always — auto-injected at session start | Pointers to behavior rules and key facts |
| Behavior-rule files (`feedback_*.md`) | On demand — agent reads when relevant | Detail behind a specific rule |
| Project-state files (`project_*.md`) | On demand | Current configs, environment specifics |

The split exists because the index is *applied even when the agent
doesn't know the rule exists* — so it must always be in context. Detail
files are referenced only when the agent already knows what to look
for.

Initial seed: just the index file with one or two essential pointers
(e.g. memory protocol, scoping rules). Everything else accretes
naturally as the project develops.

## Knowledge graph entry: when, who, what

Add the project to the graph at setup so future sessions can answer
"when did this start? what is it?" without re-asking. Minimum:

- Setup date
- Scope (shared / isolated)
- One sentence on what the project is

Fields beyond this are nice-to-have and accumulate as you learn the
project. Don't try to capture everything on day one — premature
structure decays.

## Operator boundary: don't run installs yourself

External package installs (graph parsers, build steps, indexing tools)
should be **invoked by the user**, not by the agent. Reasons:

- Installs may need terminal-level permissions the agent doesn't have
- Output is interactive (progress bars, password prompts) and breaks
  cleanly outside the agent's tool stream
- The user gets to see the install actually happen, not a wrapped log

Agent's job: detect whether the install is needed (`is the directory
present?`), and if not, output the exact command for the user to run.
Don't shell-out the install yourself.

## Idempotency

Setup must be safe to re-run. Means:

- Detecting "this file already has my entry" before adding
- Merging into existing structures, never replacing
- The user might re-invoke setup after fixing one piece — they
  shouldn't fear losing other state

Idempotency is the single feature that makes setup safe to run after a
restart. Without it, partial-init becomes a fragile sequence.

## Hard rules

- ✅ Decide scope (shared vs isolated) **before** writing files
- ✅ Phase 1 stops at "restart and re-run"; Phase 2 starts only after
  the new infrastructure verifies
- ✅ Seed structure once, on first init of an isolated store
- ✅ Index memory file is always created; rule files only when there
  are rules to encode
- ✅ Knowledge graph gets a setup-date entry on day one
- ✅ Diary entry records what setup did and didn't do
- ❌ Don't pretend Phase 2 can run in the same session as Phase 1
- ❌ Don't run external installs from the agent
- ❌ Don't overwrite existing config files — merge

## Anti-patterns

- ❌ Setting up a sub-project as isolated "to be safe" — produces
  fragmented memory across what should be one context
- ❌ Setting up a top-level project as shared — leaks unrelated topics
- ❌ One-shot all-in-one setup that runs MCP calls in the same session
  as MCP wiring — fails silently
- ❌ Seeding structure into a shared store on every new sub-project —
  duplicates the conventions
- ❌ Index memory file with everything inline — defeats the
  index-vs-detail split
- ❌ No diary entry — the setup itself becomes invisible after the
  session ends
