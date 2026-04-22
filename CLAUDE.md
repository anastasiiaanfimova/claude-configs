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
Все credentials хранятся в agent-vault:
- `agent-vault vault credential set --vault edarium KEY=value` — для Edarium (Jira, Confluence)
- `agent-vault vault credential set --vault zencreator KEY=value` — для ZenCreator
- `agent-vault vault credential set KEY=value` — для общих/cross-project ключей (default vault)

Если пользователь просит сохранить токен или ключ — предложить добавить в нужный vault, не в файл.
