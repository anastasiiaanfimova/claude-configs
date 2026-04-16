---
description: One-time project setup — initialize MemPalace context and project memory
---

## Your task

Run one-time setup for this project. Do all steps in order.

### Step 1 — Check MemPalace
Call `mempalace_status` to confirm it's available.
Then call `mempalace_search` using the project name (derive from current directory name) to find any existing knowledge about this project.

### Step 2 — Create project memory files

The project memory path is `~/.claude/projects/<encoded-path>/memory/` where `<encoded-path>` is the absolute path to the current directory with `/` replaced by `-`.

Create the following files if they don't already exist:

**MEMORY.md** (index file — one line per memory file):
```
# MEMORY.md

- [MemPalace protocol](feedback_use_mempalace.md) — MemPalace first, file memory is backup; write diary at session end
```

**feedback_use_mempalace.md**:
```
---
name: MemPalace protocol — обязательный порядок работы с памятью
description: Конкретный протокол — что делать при старте, во время и в конце каждой сессии
type: feedback
---

**КРИТИЧЕСКИ ВАЖНО — выполнять в каждой сессии, даже после компакта:**

## При старте сессии:
1. Вызвать `mempalace_status`
2. Вызвать `mempalace_search` по теме разговора или имени проекта

## Во время сессии:
- Перед ответом о людях, проектах, прошлых событиях → `mempalace_search` или `mempalace_kg_query` ПЕРВЫМ
- Файлы из memory/ — только если MemPalace не дал ответа

## В конце сессии:
- Вызвать `mempalace_diary_write` — записать что произошло, что узнала, что важно

**Why:** Единая конфигурация памяти во всех проектах. MemPalace — основной источник, файлы — резервный слой.
```

### Step 3 — Set up code-review-graph

Check if `.code-review-graph/` directory exists in the current project root.

- **If it exists** — confirm it's already set up, skip.
- **If it doesn't exist** — tell the user:
  > code-review-graph не настроен. Чтобы установить, выполни в терминале:
  > ```
  > code-review-graph install --platform claude-code && code-review-graph build
  > ```
  > После установки граф будет автоматически обновляться при изменениях файлов.

Don't run the command yourself — the user needs to run it manually in the project terminal.

### Step 4 — Add project to MemPalace knowledge graph

Call `mempalace_kg_add` with:
- subject: project name (directory name)
- predicate: `setup_date`
- object: today's date (YYYY-MM-DD)

Ask the user: "Расскажи пару слов о проекте — что это, твоя роль, что важно помнить?" Then add what they say as additional KG facts.

### Step 5 — Write diary entry

Call `mempalace_diary_write` with agent_name `claude`, topic = project name.
Record: project name, setup date, what you learned about the project in this session.

### Step 6 — Report

Tell the user what was set up and confirm the project is ready.
