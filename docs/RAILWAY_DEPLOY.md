# Деплой на Railway (Docker)

## Что происходит при старте контейнера

1. **`migrate`** — применение миграций.
2. **Опционально `AUTO_LOAD_HR_CONTENT=1`** — загрузка из YAML в БД:  
   `load_courses` → `load_onboarding` → `load_articles` → `load_news` → `load_departments`.  
   Команды **идемпотентны** (`update_or_create`): при каждом деплое база подтягивает **актуальные переводы** из репозитория (курсы, онбординг, wiki, новости).
3. **Опционально `AUTO_CREATE_DEFAULT_USERS`** — создание пользователей из env (см. `create_default_users`).
4. **`collectstatic`**
5. **Gunicorn**

## UI-переводы (django.po → django.mo)

- В **Dockerfile** при сборке образа устанавливается **gettext** и выполняется **`python manage.py compilemessages`** (настройки `config.settings.base`).  
- В рантайме пересборка `.mo` не обязательна: при изменении `.po` нужен **новый деплой** (пересборка образа).

## Рекомендуемые переменные в Railway

| Переменная | Значение | Назначение |
|------------|----------|------------|
| `AUTO_LOAD_HR_CONTENT` | `1` | Подтягивать мультиязычный контент из YAML при каждом деплое |
| `SECRET_KEY` | (секрет) | Обязательно в production |
| `ALLOWED_HOSTS` | `yourapp.up.railway.app` | Домен приложения |
| `CSRF_TRUSTED_ORIGINS` | `https://yourapp.up.railway.app` | Для HTTPS |
| `DATABASE_URL` | (из Railway Postgres) | Подставляется автоматически при подключении БД |
| `AUTO_CREATE_DEFAULT_USERS` | `1` | Первый запуск: создать admin/hr/employee/candidate из `DEFAULT_*` |
| `AUTO_SEED_DEMO_CONTENT` | `1` | Вместе с `AUTO_CREATE` — сид только если таблицы пустые |

**Важно:** после первого деплоя с пустой БД контент появится либо через **`AUTO_LOAD_HR_CONTENT`**, либо через **`AUTO_SEED_DEMO_CONTENT`** внутри `create_default_users` (если таблицы пустые). Для **обновления переводов** при уже заполненной БД используйте **`AUTO_LOAD_HR_CONTENT=1`**.

## Двуязычие / трёхъязычие в приложении

- **Интерфейс:** `locale/ru`, `locale/ka` + `compilemessages` при сборке образа.  
- **Контент:** поля `*_en`, `*_ka`, `*_ru` в БД, заполняемые из `input/hr docs/content/*.yaml` через `load_*` (см. [I18N_MULTILINGUAL_RUNBOOK.md](I18N_MULTILINGUAL_RUNBOOK.md)).

Переключатель языка в Django: `LocaleMiddleware` + cookie/session.
