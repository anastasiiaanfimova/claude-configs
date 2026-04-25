---
description: One-time project setup — initialize MemPalace context and project memory
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

2. Create or update `.claude/settings.local.json` — add mempalace to permissions and enabledMcpjsonServers (merge, don't overwrite):
   - Add `"mcp__mempalace__*"` to `permissions.allow` if not already there
   - Add `"mempalace"` to `enabledMcpjsonServers` if not already there

3. Tell the user:
> Файлы созданы. Перезапусти сессию (закрой и открой Claude Code в этой папке) и запусти `/setup` снова — теперь MemPalace подключится автоматически.

Then stop. Do not continue to Phase 2.

---

### Phase 2 — MemPalace setup

Only run this phase if `mempalace_status` is available (MCP connected).

**Step 1 — Check palace**
Call `mempalace_status`, then `mempalace_search` using the project name to find any existing knowledge.

**Step 2 — Create project memory files**

The project memory path is `~/.claude/projects/<encoded-path>/memory/` where `<encoded-path>` is the absolute path to the current directory with `/` replaced by `-`.

Create the following files if they don't already exist:

**MEMORY.md**:
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

**Why:** Проекты внутри ~/Claude/ используют общий palace (~/.mempalace/palace). Независимые проекты (<project>, <project> и т.д.) имеют свой изолированный palace. В обоих случаях MemPalace — основной источник памяти, файлы — резервный слой.
```

**Step 3 — Set up code-review-graph**

Check if `.code-review-graph/` directory exists in the current project root.

- **If it exists** — confirm it's already set up, skip.
- **If it doesn't exist** — tell the user:
  > code-review-graph не настроен. Чтобы установить, выполни в терминале:
  > ```
  > code-review-graph install --platform claude-code && code-review-graph build
  > ```
  > После установки граф будет автоматически обновляться при изменениях файлов.

Don't run the command yourself — the user needs to run it manually in the project terminal.

**Step 4 — Add project to MemPalace knowledge graph**

Call `mempalace_kg_add` with:
- subject: project name (directory name)
- predicate: `setup_date`
- object: today's date (YYYY-MM-DD)

Ask the user: "Расскажи пару слов о проекте — что это, твоя роль, что важно помнить?" Then add what they say as additional KG facts.

**Step 5 — Write diary entry**

Call `mempalace_diary_write` with agent_name `claude`, topic = project name.
Record: project name, setup date, what you learned about the project in this session.

**Step 6 — Report**

Tell the user what was set up and confirm the project is ready.
