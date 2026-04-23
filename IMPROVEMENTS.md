# Claude Tooling Improvements

_Last updated: 2026-04-23 | Diary range: 2026-04-18 – 2026-04-23_

---

## 🔄 Pending — не сделано

| # | Идея | Источник | Приоритет |
|---|---|---|---|
| 1 | Обновить `statusline.sh` — читать `.effort` из stdin JSON когда anthropics/claude-code#40261 будет закрыт | MemPalace (упомянуто 3+ раз), pending issue #40261 | HIGH |
| 2 | ~~Создать `CLAUDE.md` в рабочих проектах~~ | MemPalace diary 2026-04-15 | — |

> #2 закрыт: все проекты уже имеют CLAUDE.md (Edarium, ZenCreator/frontend/backend/admin). Создан корневой ~/ZenCreator/CLAUDE.md (2026-04-23) ✅

---

## ⏸ Отложено — вернуться позже

Идеи любопытные, но преждевременные для текущей роли QA (тестировщик, не разработчик).

| # | Идея | Когда актуально |
|---|---|---|
| 1 | **TDD.Guard quality gate хуки** — `PostToolUse` запускает тесты/lint автоматически. Паттерн: block Write если тесты падают (nizos/tdd-guard) + Prettier + Jest + tsc (ChrisWiles pattern) | Когда начнётся написание тестового фреймворка и автотестов |
| 2 | **`.claude/commands/` директория** — slash commands для повторяющихся воркфлоу (по образцу ChrisWiles: `/ticket`, `/daily`) | Когда накопятся повторяющиеся многошаговые задачи |

---

## 🆕 Новые предложения

Найдено в этом аудите (diary + web, апрель 2026).

| # | Идея | Источник | Приоритет |
|---|---|---|---|
| 1 | Добавить `NOTION_API_KEY` + `AMPLITUDE_API_KEY` в zencreator vault — pending с 2026-04-23 | Diary 2026-04-23 | HIGH |
| 2 | Починить auth для zozh sync — Google Fit + Zepp токены протухли (~Apr 5), sync не работает | Diary 2026-04-19 | MEDIUM |
| 3 | Попробовать HTTP hooks (новый тип, фев 2026) — POST на endpoint + JSON обратно; полезно для webhook интеграций | Web research | MEDIUM |
| 4 | Async hooks для non-blocking операций — diary write и backup запускать фоном не блокируя Claude | Web research (янв 2026) | MEDIUM |
| 5 | Разобраться с PreCompact хуком: блокирует первый compact если diary не записан — снизить `SAVE_INTERVAL` или добавить auto-write при старте | Diary 2026-04-23 | MEDIUM |
| 6 | Изучить `StopFailure` hook event (новый) — обрабатывать неудачные завершения сессии | Web research | LOW |
| 7 | Изучить Managed Agents API (public beta) — fully managed agent harness с sandboxing и SSE streaming | Web research | LOW |
| 8 | Изучить `ant CLI` — command-line клиент для Claude API с YAML versioning ресурсов | Web research | LOW |

---

## 📡 Новое в Claude Code / Anthropic

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

- `sync-configs` скилл создан и запущен — автосинк claude-configs на GitHub (2026-04-23) ✅
- agent-vault setup complete — LaunchAgent + passwordless mode + edarium/zencreator vaults (2026-04-22) ✅
- dippy PreToolUse hook настроен + bypassPermissions убран (2026-04-15) ✅
- MemPalace project isolation: MCP перенесён из global → per-project .mcp.json (2026-04-16) ✅
- Global pre-commit hook с forbidden words → защищает публичные репо (2026-04-23) ✅
- palace_detect.sh: MEMPALACE_PALACE_PATH выставляется перед каждым хуком (2026-04-16) ✅
- Config #2–5: hermes MCP, settings.local.json, python3, Openclaw gitignore — всё уже было в порядке (verified 2026-04-23) ✅
- CLAUDE.md в рабочих проектах: Edarium + ZenCreator subprojects уже имели, создан ~/ZenCreator/CLAUDE.md (2026-04-23) ✅
