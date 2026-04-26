---
name: cleanup-mac
description: >-
  macOS system cleanup — сканирует артефакты удалённых программ, стейл-конфиги,
  старые кэши и очищает их. Работает в трёх фазах: survey (чтение) → confirm →
  clean. Полностью автоматизирован для безопасных операций, спрашивает по
  неочевидным случаям. Trigger: "mac-cleanup", "почисти систему", "system
  cleanup", "убери мусор", "почисти мак".
version: 0.2.0
---

# macOS System Cleanup

Три фазы: **Survey** → **Confirm** → **Clean**.

---

## Phase 1 — Survey

Запускай проверки параллельно где возможно.

### 1.1 — Список установленных приложений

```bash
find /Applications -maxdepth 3 -name "*.app" 2>/dev/null \
  | xargs -I{} basename {} .app | sort
```

Сохрани список мысленно — он нужен для кросс-референса ниже.

### 1.2 — LaunchAgents: битые записи

```bash
# User-level: проверяем что бинарник из plist существует
for plist in ~/Library/LaunchAgents/*.plist; do
  prog=$(plutil -extract ProgramArguments.0 raw "$plist" 2>/dev/null)
  [ -n "$prog" ] && [ ! -e "$prog" ] && echo "ORPHANED: $plist → $prog"
done

# System-level (только репорт, sudo нужен для удаления):
ls /Library/LaunchDaemons/ | grep -vE "^(com\.apple|us\.zoom|com\.docker)"
```

### 1.3 — Application Support: orphaned папки

```bash
# Показываем всё, что НЕ com.apple и НЕ Apple-системное
ls ~/Library/Application\ Support/ | grep -vE \
  "^(com\.apple|AddressBook|Animoji|App Store|CallHistory|CloudDocs|\
CrashReporter|DifferentialPrivacy|DiskImages|FaceTime|FileProvider|\
Knowledge|SESStorage|iCloud|homeenergyd|locationaccessstored|\
networkserviceproxy|default\.store)" | sort
```

Для каждой папки: сверяй с 1.1. Если app не установлен → orphan.
Получи размеры orphan-папок: `du -sh ~/Library/Application\ Support/<name>`

### 1.4 — Home dotfolders: проверка

```bash
ls -la ~/ | grep "^d" | awk '{print $NF}' | grep "^\." | sort
```

Сравни с известными легитимными (см. references/known-dotfolders.md).
Для неизвестных папок: проверь размер и содержимое.

### 1.5 — Кэши: orphaned

```bash
du -sh ~/Library/Caches/* 2>/dev/null | sort -rh | head -20
```

Кросс-референс с установленными приложениями (1.1). Orphan = кэш без живого app.

### 1.6 — Brew: устаревшие и неиспользуемые

```bash
brew outdated
brew autoremove --dry-run 2>/dev/null
```

### 1.7 — Docker: build cache

```bash
docker system df 2>/dev/null
```

Если reclaimable > 5GB — предложить `docker builder prune -f`.

### 1.8 — Claude CLI: старые версии

```bash
ls -lh ~/.local/share/claude/versions/ 2>/dev/null
```

Текущую версию (`claude --version`) оставляем + одну предыдущую. Остальные — удалять.

### 1.9 — Downloads: старые установщики

```bash
find ~/Downloads -name "*.dmg" -o -name "*.pkg" 2>/dev/null | while read f; do
  app=$(basename "$f" | sed 's/-[0-9].*//' | sed 's/\.dmg$//' | sed 's/\.pkg$//')
  echo "$f"
done
du -sh ~/Downloads/Apps/ 2>/dev/null
```

Для каждого .dmg/.pkg: если соответствующий app установлен или удалён — установщик не нужен.

### 1.10 — .zshrc: стейл записи

```bash
cat ~/.zshrc
```

Ищи: PATH-записи для удалённых инструментов (lmstudio, pnpm без pnpm, etc.), source/export удалённых программ.

### 1.11 — Shell-файлы: открытые API-ключи

```bash
grep -r "API_KEY\|SECRET\|TOKEN\|api_key" ~/.zshrc ~/.zshenv ~/.bashrc ~/.bash_profile 2>/dev/null \
  | grep -v "^#" | grep -v "Keychain\|security find\|infisical\|INFISICAL"
```

Если находишь — СРАЗУ флагуй как critical. Ключи должны быть в Infisical, не в файлах.

### 1.12 — npm globals: неиспользуемые

```bash
npm list -g --depth=0 2>/dev/null
```

Флагуй пакеты для удалённых приложений (codex без codex app, etc.).

### 1.13 — pipx: сломанные symlinks

```bash
pipx list 2>/dev/null
```

Если видишь "symlink missing" → `pipx reinstall <package>`.

---

## Phase 2 — Report

Структурируй находки по категориям:

### 🔴 Критично (сразу флагуй, не удаляй без ответа)
- API ключи в shell-файлах
- LaunchDaemon для удалённой программы (system-level, нужен sudo)

### 🟠 Автоудаление (безопасно, делай без вопросов)
- Orphaned LaunchAgent plists (user-level)
- Application Support папки удалённых app (если > однозначно удалён)
- Кэши удалённых app
- Homebrew: `brew cleanup --prune=all` + `brew autoremove`
- Claude CLI: старые версии (кроме текущей и предыдущей)
- claude-cleanup: `bash ~/.claude/cleanup_history.sh`
- `pipx reinstall <broken>` для сломанных symlinks
- Пустые директории (0B)
- Старые `known_hosts.old`, zcompdump с другим hostname

### 🟡 Спросить у пользователя
- Большие папки (> 500MB) неизвестного происхождения
- Dotfolders, которые не в known-dotfolders.md
- Docker build cache (если > 5GB reclaimable)
- Brew packages, про которые непонятно используются ли
- DMG/PKG установщики

Показывай таблицу с размерами для каждой категории. Начинай с 🟠 — делай сразу, затем задавай вопросы по 🟡.

---

## Phase 3 — Clean

### Автоматически (🟠):

```bash
# LaunchAgent orphan
launchctl unload ~/Library/LaunchAgents/<name>.plist 2>/dev/null
rm ~/Library/LaunchAgents/<name>.plist

# Application Support
rm -rf ~/Library/Application\ Support/<name>

# Caches
rm -rf ~/Library/Caches/<name>

# Brew
brew cleanup --prune=all
brew autoremove
brew upgrade  # если были outdated

# Claude CLI old versions
rm ~/.local/share/claude/versions/<old_version>

# claude-cleanup
bash ~/.claude/cleanup_history.sh

# Пустые dotfolders
rm -rf ~/.<empty_dir>

# pipx
pipx reinstall <broken_package>
```

### После подтверждения (🟡):

```bash
# Docker build cache
docker builder prune -f

# Большие папки
rm -rf ~/<confirmed_dir>

# DMG/PKG установщики
rm ~/Downloads/Apps/<confirmed_installer>
```

### sudo-команды (🔴, system LaunchDaemon):

Выведи команды для ручного запуска в терминале:
```
sudo launchctl unload /Library/LaunchDaemons/<name>.plist
sudo rm /Library/LaunchDaemons/<name>.plist
sudo rm -rf /Library/Frameworks/<related_framework>
```

---

## Phase 4 — Verify

После очистки пробегись кратко:

```bash
# LaunchAgents
ls ~/Library/LaunchAgents/

# Application Support (только non-apple)
ls ~/Library/Application\ Support/ | grep -vE "^com\.apple|^[A-Z]" | sort

# Docker
docker system df 2>/dev/null

# Brew
brew outdated

# Disk freed (приблизительно через du)
du -sh ~/ 2>/dev/null
```

Выведи итог: что удалено, сколько места освобождено.

---

## Phase 5 — Diary

Записать в MemPalace:
- Что нашли и удалили
- Сколько места освободили
- Любые security-находки (API ключи)

---

## Важные правила

1. **Никогда не удалять без проверки**: всегда сначала смотри размер и содержимое незнакомой папки
2. **API ключи**: если нашла — немедленно флагуй, предложи ротацию + перенос в Infisical
3. **sudo**: не пытаться сделать из Claude Code — выводить команды для ручного запуска
4. **Docker образы и контейнеры**: НЕ трогать (только build cache)
5. **~/Library/Caches/Google, JetBrains, Steam**: легитимные, не трогать
6. **~/.mempalace, ~/.claude, ~/.hermes, ~/.local**: не трогать без явного запроса
7. **Infisical данные (~/.infisical)**: не трогать
8. **DMG в ~/Downloads/Apps**: только спрашивать, не автоудалять
