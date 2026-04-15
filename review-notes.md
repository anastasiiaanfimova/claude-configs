# Review Notes

Заметки в процессе просмотра ресурсов — что смотрели, что отложили, что пропустили и почему.

---

## elizabethfuentes12/claude-code-dotfiles
*2026-04-15*

**Взяли**
- Стратегию `.gitignore` с явным allowlist — добавили в этот репо. Блокируем всё, явно разрешаем нужное.

**Пропустили**
- Shell-wrapper для автосинка (`claude()` в `.zshrc`) — не нужен. Один компьютер, один источник правды. GitHub — бэкап, не синхронизация между машинами.

---

## hesreallyhim/awesome-claude-code
*2026-04-15*

### THE_RESOURCES_TABLE.csv

**Сейчас**
- [agnix](https://github.com/agent-sh/agnix) — линтер для CLAUDE.md, агентов, хуков, skills. С 16+ агентами полезно следить за консистентностью frontmatter. Посмотреть как ставится и что именно проверяет.
- [TDD Guard](https://github.com/nizos/tdd-guard) — хуки, которые блокируют изменения файлов нарушающие TDD в реальном времени. Хороший пример quality gates через хуки — паттерн интересен сам по себе.
- [Trail of Bits Security Skills](https://github.com/trailofbits/skills) — 15+ security skills (CodeQL, Semgrep, variant analysis, fix verification). Пригодится при углублении security-auditor агента.

**Позже**
- [Claude Code Agents (undeadlist)](https://github.com/undeadlist/claude-code-agents) — workflow для solo разработчика с multi-auditor паттернами и micro-checkpoints. Интересно для понимания оркестрации агентов, не срочно.
- ~~[Dippy](https://github.com/ldayton/Dippy)~~ — **установлен** (v0.2.7, brew). PreToolUse хук на Bash активен.

**Пропустили**
- Командные инструменты, визуальная регрессия, mobile, enterprise — не в контексте.

### Полный репо (README + остальное)

**Сейчас**
- `/repro-issue` slash command — генерирует воспроизводимые тест-кейсы из бага. Для async pipeline сценариев (фото/видео) — прямо в тему.
- CLAUDE.md паттерн по Giselle — post-action checklist (формат → сборка → тесты). Применимо для QA-воркфлоу. Нужно проверить, есть ли CLAUDE.md в проекте.
- Design Review Workflow — slash command → subagent → Playwright MCP. Адаптируемо под визуальную QA generated output.

**Позже**
- [parry](https://github.com/...) — хук-сканер на prompt injection и секреты. Ранняя стадия, отслеживать.
- Observability: ~~`claude-devtools`~~ — **установлен** (v0.4.10, brew), но UI не показывает дерево subagent-ов. Нужно screen recording permission. `ccxray`, `cclogviewer` — не трогали.
- ~~[Rulesync](https://github.com/...)~~ — **dismissed**: инструмент для синхронизации правил между агентами, не для генерации конфигов. Не нужен.
- `claude-code-statusline` с MCP-мониторингом — не трогали.

**Пропустили**
- Ralph (autonomous loops), orchestrators, Britfix (диалект-конвертер), VoiceMode MCP.

---

## trailofbits/claude-code-config
*2026-04-15*

**Взяли**
- PreToolUse хук блокировки `rm -rf` — парсит команду через jq, блокирует деструктивные флаги. Критично при bypassPermissions.
- PostToolUse audit log хук — пишет каждую Bash-команду с timestamp в JSONL. Трейс что агенты реально делают.
- Statusline паттерн: context% с цветом (green/yellow/red) + cost + cache hit rate. Сравнить с текущим statusline.sh.

**Позже**
- Anti-rationalization Stop хук — Haiku evaluator блокирует агента от преждевременной "победы". Отложено: нужно сначала понаблюдать за реальным поведением через claude-devtools (оно установлено, но screen recording не выдан).
- `/clear` вместо `/compact` — компакция lossy, явная очистка контекста между задачами.

**Пропустили**
- Sandbox/deny rules, prek (Rust hooks), языковые тулчейны.

---

## ChrisWiles/claude-code-showcase
*2026-04-15*

**Взяли**
- `settings.json` hooks: `PreToolUse` блокирует коммиты в main, `PostToolUse` — Prettier + `npm install` при изменении `package.json` + Jest на изменённых тест-файлах + `tsc --noEmit`. Готовый паттерн quality gates.
- Slash commands как `.claude/commands/*.md` — каждый кодирует многошаговый воркфлоу. `/ticket` = JIRA → branch → TDD impl → PR. Перенести 16 агентов в эту структуру, чтобы были как `/команды`.
- GitHub Actions: `pr-claude-code-review.yml` — `anthropics/claude-code-action@beta`, 30 мин timeout, 10 turns, передаёт checklist-агента. Шаблон для CI-ревью.

**Позже**
- Skill-eval hook — JS-движок анализирует промпт по ключевым словам и подсказывает нужный skill. Отложено: сейчас skills мало, не актуально до 20+.

**Пропустили**
- Остальная структура проекта — у нас уже есть аналоги.

---

## VoltAgent/awesome-claude-code-subagents
*2026-04-15*

**Взяли**
- Frontmatter-дисциплина: явно указывать `model` (opus/sonnet/haiku) и минимальный набор `tools` для каждого агента. Читающие агенты (coverage-analyst, security-auditor) — только `Read, Grep, Glob`; пишущие — плюс `Write, Edit, Bash`. Стоит пройтись по 16 агентам и выровнять.
- Трёхфазная структура промпта: Analysis → Implementation → Delivery. Использовать как шаблон при написании новых агентов.

**Позже**
- `chaos-engineer` паттерн — resilience testing async pipelines. Отложено: нужен нагрузочный фреймворк сначала, преждевременно без k6 сценариев.
- `accessibility-tester` — WCAG coverage. Отложено: зависит от UI-насыщенности продукта, пока не приоритет.

**Пропустили**
- Coordinator-агенты, language specialists — не в контексте.
- "Улучшить qa-researcher по qa-expert" — расплывчато без конкретного diff.

---

## karanb192/claude-code-hooks
*2026-04-15*

262 тестов, 4 типа хуков.

**Взяли**
- Ничего — всё перекрыто тем что уже стоит.

**Позже**
- `protect-secrets.js` (PreToolUse на Read|Edit|Write|Bash) — блокирует чтение и модификацию sensitive файлов (.env, ключи). Единственное что не покрывает dippy. Посмотреть что именно блокирует и не конфликтует ли с workflow.
- `event-logger.py` (Utils) — логирует все hook events с полными payload-ами. Полезно при отладке хуков, не для постоянного использования.

**Пропустили**
- `block-dangerous-commands.js` — дублирует dippy, который уже стоит и делает это через AST.
- `auto-stage.js` (PostToolUse на Edit|Write) — авто-git-add после каждого изменения. Рискованно: можно случайно застейджить лишнее.
- `notify-permission.js` — Slack-алерт когда Claude ждёт апрув. Solo работа, не нужно.

---
