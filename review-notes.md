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
- [Dippy](https://github.com/ldayton/Dippy) — авто-апрув безопасных bash-команд через AST. Уменьшает permission fatigue. Вернуться когда надоест кликать Allow.

**Пропустили**
- Командные инструменты, визуальная регрессия, mobile, enterprise — не в контексте.

### Полный репо (README + остальное)

**Сейчас**
- `/repro-issue` slash command — генерирует воспроизводимые тест-кейсы из бага. Для async pipeline сценариев (фото/видео) — прямо в тему.
- CLAUDE.md паттерн по Giselle — post-action checklist (формат → сборка → тесты). Применимо для QA-воркфлоу. Нужно проверить, есть ли CLAUDE.md в проекте.
- Design Review Workflow — slash command → subagent → Playwright MCP. Адаптируемо под визуальную QA generated output.

**Позже**
- [parry](https://github.com/...) — хук-сканер на prompt injection и секреты. Ранняя стадия, отслеживать.
- Observability: `ccxray` (HTTP proxy, токены/стоимость), `claude-devtools` (subagent tree), `cclogviewer`. Для понимания реального cost 16 агентов.
- [Rulesync](https://github.com/...) — автогенерация конфигов агентов из единого источника. Актуально при выравнивании frontmatter всех 16.
- `claude-code-statusline` с MCP-мониторингом — видно какие MCP дёргаются в реальном времени (MemPalace, code-review-graph, computer-use).

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
- Anti-rationalization Stop хук — Haiku evaluator блокирует агента от преждевременной "победы". Вернуться после наблюдения за поведением агентов в claude-devtools.
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
- Skill-eval hook — JS-движок анализирует промпт по ключевым словам и подсказывает нужный skill. Актуально когда skills станет 20+.

**Пропустили**
- Остальная структура проекта — у нас уже есть аналоги.

---

## VoltAgent/awesome-claude-code-subagents
*2026-04-15*

**Взяли**
- Frontmatter-дисциплина: явно указывать `model` (opus/sonnet/haiku) и минимальный набор `tools` для каждого агента. Читающие агенты (coverage-analyst, security-auditor) — только `Read, Grep, Glob`; пишущие — плюс `Write, Edit, Bash`. Стоит пройтись по 16 агентам и выровнять.
- Трёхфазная структура промпта: Analysis → Implementation → Delivery. Использовать как шаблон при написании новых агентов.

**Позже**
- `chaos-engineer` паттерн — resilience testing async pipelines. Актуально для фото/видео генерации с очередями, но на этапе нагрузочного тестирования.
- `accessibility-tester` — WCAG coverage, зависит от UI-насыщенности продукта.

**Пропустили**
- Coordinator-агенты, language specialists — не в контексте.
- "Улучшить qa-researcher по qa-expert" — расплывчато без конкретного diff.

---
