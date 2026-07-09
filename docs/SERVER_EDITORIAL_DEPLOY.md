# Безопасный деплой на сервер без перезаписи БД

Инструкция для **Windows Server** (`C:\dimkava\compose`). Используйте, когда HR правит контент в админке или портале (**Edit**), и нужно обновить только код приложения.

## Режим по умолчанию

В `C:\dimkava\compose\.env.prod`:

```env
AUTO_LOAD_HR_CONTENT=0
AUTO_CREATE_DEFAULT_USERS=0
```

Проверка:

```powershell
Select-String -Path C:\dimkava\compose\.env.prod -Pattern "AUTO_LOAD_HR_CONTENT|AUTO_CREATE_DEFAULT_USERS"
```

При `AUTO_LOAD_HR_CONTENT=0` при старте контейнера **не** выполняются `load_articles`, `load_courses` и другие loaders — правки HR в PostgreSQL сохраняются.

---

## Безопасный деплой (обновление кода)

```powershell
# 0. Бэкап
cd C:\dimkava\scripts
.\backup-db.ps1

# 1. Код
cd C:\Projects\dimkava-big-book
git pull
.\deploy\scripts\build-local-image.ps1

# 2. Только перезапуск web — БД не трогаем
cd C:\dimkava\compose
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --force-recreate web

# 3. В логах НЕ должно быть "Loading HR content from YAML"
docker compose --env-file .env.prod -f docker-compose.prod.yml logs web --tail 30
```

### Не выполнять в этом сценарии

- `load_articles`, `load_courses`, `load_onboarding`, `load_news`, `load_departments`
- `cleanup_regulations_import` (если не чистите старые `tg-*`)
- смену `AUTO_LOAD_HR_CONTENT` на `1` без бэкапа

---

## Что безопасно / что опасно

| Действие | Редакторский режим (`AUTO_LOAD=0`) |
|----------|-------------------------------------|
| `git pull` + rebuild + `force-recreate web` | OK |
| `migrate` (в entrypoint при старте) | OK |
| Правки через `/edit/...` или `/admin/` | OK |
| `.\backup-db.ps1` | OK, рекомендуется |
| `AUTO_LOAD_HR_CONTENT=1` | **НЕТ** — перезапишет контент из YAML |
| `docker compose run ... load_articles` | **НЕТ** (если не осознанная перезаливка) |

`load_*` делает `update_or_create` по `slug`: статьи с slug из YAML (например `reg-31193`) **затираются**. Статьи с новым slug, которого нет в YAML, **не удаляются**.

---

## Осознанная перезаливка YAML (только с бэкапом)

Когда нужно подтянуть переводы из git, а правки HR не важны:

```powershell
cd C:\dimkava\scripts
.\backup-db.ps1
cd C:\dimkava\compose
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm web python manage.py load_articles
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm web python manage.py load_courses
# Вернуть AUTO_LOAD_HR_CONTENT=0 и force-recreate web
```

---

## Предупреждения Docker Compose про `"yN8k" variable is not set`

Пароль в `.env.prod` содержит `$`. Compose воспринимает `$yN8k` как переменную.

**Исправление:** удвоить `$` в пароле:

```env
# Было:  POSTGRES_PASSWORD=abc$yN8kxyz
# Стало: POSTGRES_PASSWORD=abc$$yN8kxyz
```

То же для `DATABASE_URL`, если пароль в URL содержит `$`.

---

## HR Edit в портале

После деплоя HR видит кнопку **Edit** на статьях, курсах, quiz, новостях, onboarding и ролях. URL: `/edit/...` (только группа `hr_manager` или superuser).

См. также [WINDOWS_SERVER_DEPLOY.md](WINDOWS_SERVER_DEPLOY.md) §13.
