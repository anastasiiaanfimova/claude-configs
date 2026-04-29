---
name: setup-project
description: >-
  One-time project setup — initialize MemPalace context, episodic-memory,
  code-review-graph, and project memory files. Run once per new project directory.
  Trigger: "/setup", "setup project", "инициализируй проект", "настрой проект",
  "первый запуск", "init project memory".
---

## Your task

Run one-time setup for this project. Do all steps in order.

Derive the project name from the current directory name (lowercase).

**Determine palace strategy** based on the current directory path:
- If the current directory is inside `/Users/<user>/Claude/` (a sub-project of the Claude workspace) → **shared palace** (no `--palace` flag, uses `~/.mempalace/palace` via palace_detect.sh)
- Otherwise (top-level independent project like <project>, <project>) → **separate palace** at `/Users/<user>/.<project-name>/mempalace`

---

### Phase 1 — Infrastructure

Check if `.mcp.json` exists in the current project root AND contains a `mempalace` entry.

**If `.mcp.json` is missing or has no `mempalace` entry:**

1. Create or update `.mcp.json` — add the `mempalace` server (merge with existing content if file exists):

   **For shared palace (project is inside ~/Claude/):**
   ```json
   {
     "mcpServers": {
       "mempalace": {
         "command": "/Users/<user>/.mempalace/venv/bin/python3",
         "args": ["-m", "mempalace.mcp_server"],
         "type": "stdio",
         "env": {}
       }
     }
   }
   ```

   **For separate palace (top-level independent project):**
   ```json
   {
     "mcpServers": {
       "mempalace": {
         "command": "/Users/<user>/.mempalace/venv/bin/python3",
         "args": ["-m", "mempalace.mcp_server", "--palace", "/Users/<user>/.<project-name>/mempalace"],
         "type": "stdio",
         "env": {}
       }
     }
   }
   ```

2. Check if `.mcp.json` contains an `episodic-memory` entry. If not — add it (merge, don't overwrite):
   ```json
   {
     "mcpServers": {
       "episodic-memory": {
         "command": "episodic-memory-mcp-server",
         "type": "stdio",
         "env": {}
       }
     }
   }
   ```
   Note: episodic-memory uses a single global index regardless of project — no path customization needed.

3. Create or update `.claude/settings.local.json` — add both servers to permissions and enabledMcpjsonServers (merge, don't overwrite):
   - Add `"mcp__mempalace__*"` to `permissions.allow` if not already there
   - Add `"mcp__episodic-memory__*"` to `permissions.allow` if not already there
   - Add `"mempalace"` to `enabledMcpjsonServers` if not already there
   - Add `"episodic-memory"` to `enabledMcpjsonServers` if not already there

4. Tell the user:
> Файлы созданы. Перезапусти сессию (закрой и открой Claude Code в этой папке) и запусти `/setup` снова — теперь MemPalace и episodic-memory подключатся автоматически.

Then stop. Do not continue to Phase 2.

---

### Phase 2 — MemPalace setup

Only run this phase if `mempalace_status` is available (MCP connected).

**Step 1 — Check palace**
Call `mempalace_status`, then `mempalace_search` using the project name to find any existing knowledge.

**Step 2 — Seed organization rules (separate palace only)**

Skip this step if the project is inside `~/Claude/` (shared palace — rules already exist in `wing_claude/decisions`).

For independent projects with a separate palace: call `mempalace_add_drawer` to seed the organization rules so every new palace starts with structure:

```
wing: wing_<project-name>
room: decisions
source_file: mempalace-organization-rules
content:
  ## mempalace-organization-rules — правила хранения данных по MCP и тулам

  ### Разграничение rooms для MCP/tools

  | room | что хранить |
  |------|-------------|
  | `decisions` | правила, протоколы, архитектурные решения по самому palace |
  | `config` | конфигурация MCP-серверов, пути, порты, параметры запуска |
  | `rules` | поведенческие правила для агента (feedback от пользователя) |
  | `recipes` | пошаговые инструкции: как установить, настроить, починить конкретный тул |

  ### Паттерн именования

  Drawer с данными по конкретному MCP-инструменту называть: `<toolname>.mcp`
  Примеры: `mempalace.mcp`, `testiny.mcp`, `asana.mcp`, `grafana.mcp`

  ### Что НЕ хранить в palace

  - Вывод команд целиком (логи, stdout) — только выводы
  - Данные, которые можно получить из кода или git-истории
  - Ephemeral state (текущие значения переменных, временные ID)
  - Дублирующие drawer без новой информации

  ### Протокол чистки дублей

  При обнаружении двух drawer с похожим содержимым:
  - A ⊂ B (A полностью покрыт B) → удалить A, оставить B
  - Оба содержат уникальные детали → мержить в один, удалить оба исходных
  - Проверять через `mempalace_check_duplicate` перед добавлением нового

  ### Протокол добавления нового MCP

  1. `mempalace_check_duplicate` — убедиться что такого drawer ещё нет
  2. Если нет — создать drawer `<toolname>.mcp` в `config` с: путём к серверу, командой запуска, scope (user/project), проектами где используется
  3. Если рецепт установки нетривиален — отдельный drawer в `recipes`
  4. После подключения — запись в diary о том что MCP добавлен и зачем
```

**Step 3 — Create project memory files**

The project memory path is `~/.claude/projects/<encoded-path>/memory/` where `<encoded-path>` is the absolute path to the current directory with `/` replaced by `-`.

Create the following files if they don't already exist:

**MEMORY.md**:
```
# MEMORY.md

- [Memory protocol](feedback_use_mempalace.md) — старт: MemPalace + episodic параллельно; маршрутизация по типу вопроса; diary в конце
```

**feedback_use_mempalace.md**:
```
---
name: MemPalace protocol — обязательный порядок работы с памятью
description: Конкретный протокол — что делать при старте, во время и в конце каждой сессии
type: feedback
---

**КРИТИЧЕСКИ ВАЖНО — выполнять в каждой сессии, даже после компакта:**

## При старте сессии (параллельно):
1. Вызвать `mempalace_status`
2. Вызвать `mempalace_search` по теме разговора или имени проекта
3. Вызвать `mcp__episodic-memory__search` по сегодняшней дате + теме

## Во время сессии (маршрутизация по типу вопроса):
- **Факты, решения, люди, проекты** → `mempalace_search` или `mempalace_kg_query`
- **Конкретные слова, ошибки, команды, URL** → `mcp__episodic-memory__search` сразу
- **"Что было в сессии где делали X"** → оба параллельно
- Файлы из memory/ — только если оба не дали ответа

## Дополнение diary:
Если diary-запись слишком сжата и детали непонятны → `mcp__episodic-memory__search` по дате + ключевому слову

## В конце сессии:
- Вызвать `mempalace_diary_write` — записать что произошло, что узнала, что важно

**Why:** Проекты внутри ~/Claude/ используют общий palace (~/.mempalace/palace). Независимые проекты имеют свой изолированный palace. MemPalace и episodic — равноправные инструменты с разными ролями, не иерархия.
```

**Step 4 — Set up code-review-graph**

Check if `.code-review-graph/` directory exists in the current project root.

- **If it exists** — confirm it's already set up, skip.
- **If it doesn't exist** — tell the user:
  > code-review-graph не настроен. Чтобы установить, выполни в терминале:
  > ```
  > code-review-graph install --platform claude-code && code-review-graph build
  > ```
  > После установки граф будет автоматически обновляться при изменениями файлов.

Don't run the command yourself — the user needs to run it manually in the project terminal.

**Step 5 — Add project to MemPalace knowledge graph**

Call `mempalace_kg_add` with:
- subject: project name (directory name)
- predicate: `setup_date`
- object: today's date (YYYY-MM-DD)

Ask the user: "Расскажи пару слов о проекте — что это, твоя роль, что важно помнить?" Then add what they say as additional KG facts.

**Step 6 — Write diary entry**

Call `mempalace_diary_write` with agent_name `claude`, topic = project name.
Record: project name, setup date, what you learned about the project in this session.

**Step 7 — Report**

Tell the user what was set up and confirm the project is ready.
