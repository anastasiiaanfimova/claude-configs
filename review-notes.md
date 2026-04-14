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

## hesreallyhim/awesome-claude-code — THE_RESOURCES_TABLE.csv
*2026-04-15*

**Сейчас**
- [agnix](https://github.com/agent-sh/agnix) — линтер для CLAUDE.md, агентов, хуков, skills. С 16+ агентами полезно следить за консистентностью frontmatter. Посмотреть как ставится и что именно проверяет.
- [TDD Guard](https://github.com/nizos/tdd-guard) — хуки, которые блокируют изменения файлов нарушающие TDD в реальном времени. Хороший пример quality gates через хуки — паттерн интересен сам по себе.
- [Trail of Bits Security Skills](https://github.com/trailofbits/skills) — 15+ security skills (CodeQL, Semgrep, variant analysis, fix verification). Пригодится при углублении security-auditor агента.

**Позже**
- [Claude Code Agents (undeadlist)](https://github.com/undeadlist/claude-code-agents) — workflow для solo разработчика с multi-auditor паттернами и micro-checkpoints. Интересно для понимания оркестрации агентов, не срочно.
- [Dippy](https://github.com/ldayton/Dippy) — авто-апрув безопасных bash-команд через AST. Уменьшает permission fatigue. Вернуться когда надоест кликать Allow.

**Пропустили**
- Командные инструменты, визуальная регрессия, mobile, enterprise — не в контексте.

---

## ChrisWiles/claude-code-showcase
*в очереди*

---

## VoltAgent/awesome-claude-code-subagents
*в очереди*

---
