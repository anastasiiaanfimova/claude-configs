# Global Claude Instructions

## Протокол памяти — обязательно в каждой сессии

Три слоя памяти — используются по-разному, не по приоритету:

| Слой | Инструмент | Что хранит | Когда использовать |
|------|-----------|------------|--------------------|
| **MemPalace** | `mempalace_*` MCP tools | Дневник, KG, структурированные воспоминания | Факты, решения, люди, проекты |
| **Episodic memory** | `mcp__episodic-memory__search` | Полный текст прошлых переписок | Конкретные слова, ошибки, команды, детали |
| **Auto-memory файлы** | `~/.claude/projects/.../memory/*.md` | Правила поведения, фидбек, проектные решения | MEMORY.md загружается автоматически при старте — содержимое применяется всегда; отдельные файлы читать по мере надобности |

> `episodic-memory__read` НЕ использовать — файлы слишком большие, падает с "too large".

### При старте сессии (до первого ответа по существу):
Запустить параллельно:
1. `mempalace_status` — получить обзор palace
2. `mempalace_search` по теме разговора или имени проекта
3. `mcp__episodic-memory__search` по сегодняшней дате + теме (например `"2026-04-28 <project>"`) — чтобы подхватить сессии за сегодня, у которых ещё нет diary

### Во время сессии:
- **Факты, решения, люди, проекты** → `mempalace_search` или `mempalace_kg_query`
- **Конкретные слова, ошибки, команды, URL из прошлого** → `mcp__episodic-memory__search` сразу, не как fallback
- **"Что было в сессии где мы делали X"** → оба параллельно
- Файлы из `memory/` — MEMORY.md уже загружен контекстом; отдельные `.md` читать когда нужны детали правила

### Дополнение diary через episodic:
Diary — сжатая AAAK-сводка. Если из неё непонятны детали (что конкретно было, какая команда, какая ошибка):
→ `mcp__episodic-memory__search` с датой записи + ключевым словом из diary

### В конце сессии (перед закрытием или компактом):
- Вызвать `mempalace_diary_write` — записать что произошло, что узнала, что важно
- После `mempalace_diary_write` финальная фраза — `MemPalace saved.` (не "Можно завершить сессию")
- Episodic-memory синкается автоматически через Stop хук — вручную не нужно

## Разделение контекстов проектов

Каждый проект — отдельный контекст. Никогда не упоминать и не использовать знания из другого проекта, если пользователь явно не попросил.

## Управление credentials

Никогда не сохранять API-ключи, токены и секреты в shell-файлы (~/.zshenv, ~/.zshrc, ~/.bashrc и т.д.).
Все credentials хранятся в Infisical (app.infisical.com, US cloud).

**Аутентификация в Infisical CLI — через Universal Auth (machine identity):**
- Identity ID: `cfda84b3-5930-42d1-a8a3-cbaa0c1994ca`, Client ID: `8302427f-4a78-420b-a5b3-be8247c6523e` (Client ID ≠ Identity ID!)
- Client ID + Client Secret хранятся в macOS Keychain (`infisical-client-id` / `infisical-client-secret`)
- `~/.zshrc` определяет функцию `_infisical_token` — она делает `infisical login --method=universal-auth --plain --silent` и возвращает access-token
- Функции `claude()`, `claude-<project>`, `claude-<project>`, `claude-tg` вызывают `INFISICAL_TOKEN=$(_infisical_token) infisical run ...` — каждый запуск получает свежий токен, сессия никогда не протухает
- **НЕ предлагать `infisical login` с email** — это только workaround если universal auth сломан
- Если 401 Invalid credentials: identity не имеет доступа к проекту (**Projects → Access Control → Machine Identities → Add Identity**) или client-secret в Keychain не совпадает с тем что в UI (пересоздать secret, обновить через `security add-generic-password -U`)

**Проекты и папки:**
- `Personal` (`$INFISICAL_PROJECT_PERSONAL`)
  - `/claude/` — общие cross-project ключи (пока пусто)
  - `/<project>/` — Telegram API (TG_API_ID, TG_API_HASH)
  - `/hermes/` — Hermes docker секреты (17 dev + 5 prod), читает через machine identity `hermes-personal`
- `Work` (`$INFISICAL_PROJECT_WORK`)
  - `/<project>/` — Jira/Confluence (JIRA_*, CONFLUENCE_*)
  - `/<project>/` — GitLab, Amplitude, Grafana, Sentry, Asana, Testiny

**Добавление/обновление секрета:**
```
infisical secrets set --projectId="$INFISICAL_PROJECT_WORK" --path="/<project>" KEY=value
```

**Запуск Claude с injected секретами:**
- `claude` — smart function: детектит проект по pwd и автоматически подхватывает нужную папку из Infisical
  - `~/<project>/` → Work/<project>
  - `~/<project>/` → Work/<project>
  - `~/Claude/<project>/` → Personal/<project>
  - остальные папки → plain claude без injection
- `claude-<project>`, `claude-<project>`, `claude-tg` — явные алиасы если нужен контекст из любой папки

**Проекты и их расположение:**
- `~/<project>/` — отдельно (Jira/Confluence работа)
- `~/<project>/` — отдельно (основной продукт)
- `~/Claude/hermes/` — Docker agent, использует Personal/hermes/ через machine identity
- `~/Claude/<project>/` — Telegram reader tool

Если пользователь просит сохранить токен или ключ — предложить добавить в нужный проект/папку Infisical, не в файл.

## code-review-graph (knowledge graph для кода)

Если в корне проекта есть `.code-review-graph/` — это код-граф. Использовать его tools **ПЕРЕД** Grep/Glob/Read: быстрее, дешевле по токенам, даёт структурный контекст (callers, tests, blast radius).

| Задача | Инструмент |
|--------|-----------|
| Поиск функций/классов | `semantic_search_nodes`, `query_graph` |
| Impact analysis | `get_impact_radius`, `get_affected_flows` |
| Code review изменений | `detect_changes` + `get_review_context` |
| Связи (callers/callees/imports/tests) | `query_graph` с pattern |
| Архитектура | `get_architecture_overview`, `list_communities` |
| Покрытие тестами | `query_graph` pattern="tests_for" |
| Рефакторинг (rename, dead code) | `refactor_tool` |

Граф auto-обновляется через хуки. Fall back на Grep/Glob/Read только когда граф не покрывает.

## Принципы работы — всегда применять

Эти принципы — фон для любой работы. Применять при принятии решений (что куда положить, как структурировать, в каком порядке). Детали и примеры — в `feedback_engineering_principles.md`.

- **Multi-pass.** Любая нетривиальная задача — 3 прохода: Pass 1 поверхность → Pass 2 связи → Pass 3 «что критик скажет про мой Pass 1+2». Pass 1 нашёл — не повод останавливаться.
- **Meta-pass (после большого цикла правок).** Когда прошли все детальные pass'ы и сделали много мелких изменений — финальный бёрд-ай: «не сломали ли мы что-то совокупным эффектом, пока копались в деталях?». Проверяет когерентность файлов, скрытые зависимости, drift, потерянные capabilities. Отдельно от Pass-4-self-critique: тот про пропуски в **анализе**, мета-pass про регрессии в **финальном состоянии**.
- **OOP:** Encapsulation (одна вещь — одно место), Inheritance (общее → в базу), Polymorphism (один интерфейс под разные реализации), Abstraction (скрыть детали за чистым интерфейсом).
- **Подходы:** DRY (нет дублирования), KISS (минимум нужного), SOLID (для кода), BDUF (нетривиальное — сначала спроектировать, потом делать), SoC (одна ответственность на компонент).
- **Реализация — правила:**
  - Новый проект → стартовать с MVP (одна рабочая фича, без полной машины). Следующие фичи — после подтверждённой пользы первой.
  - Пробуем что-то новое (подход, тул, скилл, паттерн) → сначала PoC, go/no-go критерии до запуска, не интегрировать до решения.
  - Порядок всегда: PoC → MVP → итерации.

## Поведение — всегда

Cross-project поведенческие правила. Применяются в любом проекте, в любой сессии.

- **Темп.** Не торопить пользователя. Не предлагать «идём дальше?», «продолжаем?», «идём на X?» в конце ответа. Темп задаёт пользователь — закончить задачу, показать результат, остановиться.
- **Продолжение сессии.** Если первое сообщение звучит как «продолжим с...», «продолжаем с #N», «продолжай с...» — сразу `mempalace_diary_read(last_n=1)` и восстанавливать контекст оттуда, не переспрашивать что делали.
- **Git privacy.** В публичные репозитории — только обезличенные данные. Разрешённые названия проектов в публичных репо: только `hermes`, `claude`. Перед коммитом проверить файлы на email/имена/токены/пути с `/Users/<user>/`/названия приватных проектов/vault'ов/Jira-проектов. Если есть — обезличить (`<placeholder>`) или спросить.
- **Именование скилов.** Объект-действие (`git-refresh`, `bug-create`, `tc-update`), не действие-объект. Группирует скилы по объекту в списке.
- **Избегаемые слова и выражения.** Список — `feedback_avoid_phrasing.md`. Перед отправкой текста проверить на запрещённые формулировки (например, «стрелять» и производные). При сомнении — спросить.
- **Git diff перед коммитом.** Перед каждым коммитом показывать пользователю полный diff (`git diff --staged`) и ждать подтверждения.
- **Push инициирует пользователь.** Не предлагать проактивно сделать коммит или push — даже follow-up «один файл, быстро». Пользователь сам скажет когда пушить. После любых правок просто оставлять локальные изменения как есть и продолжать работу.

## Сохранение нового behavioral rule — куда?

Когда пользователь просит сохранить правило поведения (явно «запомни», «правило» или меняет behavior через feedback), **прежде чем писать** определи scope:
- **Cross-project** (применяется в любом проекте — pacing, формат ответов, общие подходы) → `~/.claude/CLAUDE.md`
- **Project-specific** (касается только этого проекта — например ZC asana flow, <project> branch naming) → `<project-memory>/feedback_X.md`
- **Infrastructure facts** (mempalace bug, infisical setup, qa toolkit состав) → `<canonical-project-memory>/project_X.md`

Если cwd говорит project (~/<project>), но обсуждение явно про общую behavior — **спросить** «это правило для всех проектов или только для X?» **перед записью**.

Если ранее сохранил не туда — предложить migrate в правильное место.

Если формулировка содержит «перед/после/каждый раз когда X» — это automated trigger, не behavioral rule → не писать в memory, инвоцировать `update-config` скилл.
Если «разреши/запрети команду» или «установи env» — тоже `update-config` скилл.

## Superpowers — Overrides

Superpowers установлен глобально (scope: user). По правилу самого плагина: **"user instructions always take precedence over superpowers skills"**.

### Brainstorming HARD-GATE — исключения

Скилл `superpowers:brainstorming` требует обязательного брейнсторминга перед любой сложной задачей. Это правило НЕ применяется для следующих action-oriented скиллов — они должны выполняться напрямую без brainstorming-фазы:

- `tc-create`, `tc-update`, `tc-gap` — создание/обновление тест-кейсов (<project> QA)
- `bug-dig`, `bug-review`, `bug-nominate`, `bug-create`, `bug-comment` — bug workflow (<project> QA)
- `mac-cleanup`, `history-cleanup`, `claude-cleanup` — системная чистка
- `claude-config-push`, `qa-playbook-push`, `git-refresh` — git/config операции

### Skill invocation — приоритет

`using-superpowers` требует инвоцировать скиллы "даже при 1% вероятности". Это не отменяет:
1. **Memory Protocol** — при старте сессии всегда до любых скиллов: `mempalace_status` + `mempalace_search` + `episodic-memory__search` по сегодняшней дате (параллельно)
2. **Project-specific workflows** — если в CLAUDE.md проекта описан свой процесс, он имеет приоритет над superpowers-скиллами
