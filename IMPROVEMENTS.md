# Claude Tooling Improvements

_Last updated: 2026-04-23 | Diary range: 2026-04-18 – 2026-04-23_

---

## 🔄 Pending — не сделано

Known pain points and gaps tracked across sessions.

| # | Идея | Источник | Приоритет |
|---|---|---|---|
| 1 | Обновить `statusline.sh` — читать `.effort` из stdin JSON когда anthropics/claude-code#40261 будет закрыт | MemPalace (упомянуто 3+ раз), pending issue #40261 | HIGH |
| 2 | Config fix: переместить hermes MCP из глобального `~/.claude.json` → `~/Hermes/.mcp.json` (audit #3) | MemPalace config.audit 2026-04-16 | MEDIUM |
| 3 | Config fix: `~/Hermes/settings.local.json` лежит в корне Hermes/, не в `.claude/` — вероятно не загружается (audit #4) | MemPalace config.audit 2026-04-16 | MEDIUM |
| 4 | Config fix: UserPromptSubmit хук использует `python`, остальные `python3` — унифицировать (audit #7) | MemPalace config.audit 2026-04-16 | LOW |
| 5 | Config fix: `Openclaw/.mcp.json` не в gitignore — риск случайного коммита (audit #9) | MemPalace config.audit 2026-04-16 | LOW |
| 6 | Создать `CLAUDE.md` файлы в рабочих проектах — пока только глобальный | MemPalace diary 2026-04-15 | MEDIUM |
| 7 | TDD.Guard quality gate хуки — `PostToolUse` запускает тесты/lint автоматически | MemPalace, awesome-claude-code review 2026-04-15 | MEDIUM |
| 8 | Добавить `.claude/commands/` директорию когда появятся повторяющиеся воркфлоу | MemPalace diary 2026-04-15 | LOW |

---

## 🆕 Новые предложения

Найдено в этом аудите (diary + web, апрель 2026).

| # | Идея | Источник | Приоритет |
|---|---|---|---|
| 1 | Добавить `NOTION_API_KEY` + `AMPLITUDE_API_KEY` в zencreator vault — pending с 2026-04-23 | Diary 2026-04-23 | HIGH |
| 2 | Починить auth для zozh sync — Google Fit + Zepp токены протухли (~Apr 5), sync не работает | Diary 2026-04-19 | MEDIUM |
| 3 | Попробовать HTTP hooks (новый тип, фев 2026) — POST на endpoint + JSON обратно; полезно для webhook интеграций | Web research | MEDIUM |
| 4 | Async hooks для non-blocking операций — diary write и backup запускать фоном не блокируя Claude | Web research (янв 2026) | MEDIUM |
| 5 | Настроить расписание для `mempalace-backup` — сейчас экспорт только ручной | Diary 2026-04-16 | MEDIUM |
| 6 | Разобраться с PreCompact хуком: блокирует первый compact если diary не записан — снизить `SAVE_INTERVAL` или добавить auto-write при старте | Diary 2026-04-23 | MEDIUM |
| 7 | Изучить `StopFailure` hook event (новый) — обрабатывать неудачные завершения сессии | Web research | LOW |
| 8 | Изучить Managed Agents API (public beta) — fully managed agent harness с sandboxing и SSE streaming | Web research | LOW |
| 9 | Изучить `ant CLI` — command-line клиент для Claude API с YAML versioning ресурсов | Web research | LOW |

---

## 📡 Новое в Claude Code / Anthropic

Фичи и обновления апрель 2026 — файл создан впервые.

- **Monitor tool** — стримит события фоновых процессов в разговор; Claude может tail logs и реагировать live. Уже используется в `/loop` без интервала
- **HTTP hooks** (фев 2026) — новый тип хука: POST на HTTP endpoint, получает JSON назад; дополняет Command/Prompt/Agent hooks
- **Async hooks** (янв 2026) — хуки могут запускаться фоном без блокировки Claude; теперь 4 типа handlers
- **21 lifecycle event** — hooks расширились, добавлены StopFailure, transcript search, MCP elicitation support
- **NO_FLICKER rendering** + **Focus View** — UX-улучшения терминального рендеринга
- **Write tool 60% speed boost** — значимый прирост для файловых операций
- **Ultraplan** — `/ultraplan` отправляет план в облачный веб-редактор для review и inline-комментов, затем запускает удалённо или возвращает локально
- **/team-onboarding** — пакует текущий Claude setup в replayable guide
- **/autofix-pr** — включает auto-fix PR прямо из терминала
- **Managed Agents public beta** — fully managed harness: sandboxing, built-in tools, SSE streaming; альтернатива ручной оркестрации через subprocess
- **ant CLI** — command-line клиент Claude API, YAML versioning ресурсов, нативная интеграция с Claude Code
- **SSE transport deprecated** → предпочтительный HTTP transport для MCP серверов (SSE всё ещё работает)
- **Model deprecations**: `claude-sonnet-4` + `claude-opus-4` → retire June 15 2026 (migrate → 4.6/4.7); `claude-haiku-3` → retired April 19 2026

---

## ✅ Сделано

_(файл создан впервые — история будет накапливаться в следующих аудитах)_

- `sync-configs` скилл создан и запущен — автосинк claude-configs на GitHub (2026-04-23) ✅
- agent-vault setup complete — LaunchAgent + passwordless mode + edarium/zencreator vaults (2026-04-22) ✅
- dippy PreToolUse hook настроен + bypassPermissions убран (2026-04-15) ✅
- MemPalace project isolation: MCP перенесён из global → per-project .mcp.json (2026-04-16) ✅
- Global pre-commit hook с forbidden words → защищает публичные репо (2026-04-23) ✅
- palace_detect.sh: MEMPALACE_PALACE_PATH выставляется перед каждым хуком (2026-04-16) ✅
