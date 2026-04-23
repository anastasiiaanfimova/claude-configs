# Amplitude Notes for tc-gap

## Getting started

Always call `get_context` first to discover the project ID for Production.
Then use `get_events` with that project ID to get the event catalog.

## Key tools

| Tool | Purpose |
|---|---|
| `mcp__Amplitude__get_context` | Lists all projects and org info |
| `mcp__Amplitude__get_events` | Returns event catalog for a project |
| `mcp__Amplitude__search` | Searches for specific events by name |
| `mcp__Amplitude__query_chart` | Runs a chart query (event totals, 30d) |

## Filtering noise events

Skip these — they are platform/internal:
- `$` prefix — analytics system events (`$pageview`, `$identify`)
- `[Amplitude]` prefix — internal events
- `[Guides-Surveys]` prefix — in-app guide/survey events
- `[Experiment]` prefix — experiment exposure events

## Volume query pattern

Use `query_chart` with:
- metric type: event totals
- time range: last 30 days
- group by: event name

## Event naming conventions (typical patterns)

Events tend to follow these patterns in AI SaaS products:
- `Task Created` — async job started
- `Task Completed` / `Task Failed` — job lifecycle
- `Payment *` — billing events
- `Subscription *` — subscription lifecycle
- `User *` / `Logged In` / `Registration Completed` — auth/account
- `Post *` — publishing events (if social publishing is a feature)
