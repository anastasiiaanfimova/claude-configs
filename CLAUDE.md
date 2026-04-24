# Global Claude Instructions

## MemPalace Protocol — обязательно в каждой сессии

### При старте сессии (до первого ответа по существу):
1. Вызвать `mempalace_status` — получить обзор palace
2. Вызвать `mempalace_search` по теме разговора или имени проекта

### Во время сессии:
- Перед ответом о людях, проектах, прошлых событиях → `mempalace_search` или `mempalace_kg_query` ПЕРВЫМ
- Файлы из `~/.claude/projects/.../memory/` — только если MemPalace не дал ответа (резервный слой)

### В конце сессии (перед закрытием или компактом):
- Вызвать `mempalace_diary_write` — записать что произошло, что узнала, что важно

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
  - `/hermes/` — зарезервировано для будущей миграции Hermes docker секретов
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
- `~/Claude/Hermes/` — Docker agent, использует Personal/hermes/ через machine identity
- `~/Claude/Openclaw/` — Docker agent, без Infisical
- `~/Claude/<project>/` — Telegram reader tool

Если пользователь просит сохранить токен или ключ — предложить добавить в нужный проект/папку Infisical, не в файл.
