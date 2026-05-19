# Dim Kava Big Book — Internal Learning Portal

Внутренний портал обучения для компании Dim Kava: LMS, онбординг, база знаний, новости.

## Структура проекта

```
dimkava-big-book/
├── input/           # Исходники: промпты, HR-контент
├── docs/            # Планирование, маппинг, вопросы
├── design/          # Эталонные шаблоны из Stitch — берём в Django
│   └── reference/   # HTML: authentication, lesson_view, quiz_screen...
├── experiments/     # stitch_lesson_view, stitch_output (исходники)
└── (dimkava_portal/ — появится при реализации)
```

## Документация

**→ [docs/INDEX.md](docs/INDEX.md)** — оглавление, порядок чтения

| Файл | Описание |
|------|----------|
| [docs/ONBOARDING_DEV.md](docs/ONBOARDING_DEV.md) | Роадмап для разработчика (вернулся к проекту) |
| [docs/STRATEGIC_SNAPSHOT.md](docs/STRATEGIC_SNAPSHOT.md) | Текущее состояние, дизайн, следующий шаг |
| [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) | План разработки по фазам |

## Локальная настройка

1. Клонировать репозиторий
2. `python -m venv venv` → `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Скопировать `.env.example` → `.env` (опционально для dev — SQLite по умолчанию)
5. `python manage.py migrate`
6. `python manage.py create_default_users` — создать admin/hr/employee/candidate
7. `python manage.py load_onboarding` — онбординг из YAML
8. `python manage.py load_courses` — курсы из YAML
9. `python manage.py load_articles` — база знаний из YAML
10. `python manage.py load_news` — новости из YAML
11. `python manage.py load_departments` — департаменты и роли из YAML (после load_courses)
12. `python manage.py runserver`

**С credentials из .env.example:** admin@dimkava.ge / changeme_admin (также есть candidate@dimkava.ge)

**Docker (Postgres + Redis):** `docker-compose up -d` — для использования Postgres задайте `DATABASE_URL`.

## Деплой

- **Self-hosted (Windows Server + Docker):** **[docs/WINDOWS_SERVER_DEPLOY.md](docs/WINDOWS_SERVER_DEPLOY.md)** — `docker-compose.prod.yml`, GHCR, GitHub Actions.
- **Railway (legacy):** **[docs/RAILWAY_DEPLOY.md](docs/RAILWAY_DEPLOY.md)**.

Общее для Docker:

- **Образ:** `Dockerfile` включает `gettext` и **`compilemessages`** для UI-переводов (`ru` / `ka`).
- **Подтягивание переводов контента из YAML в БД:** задайте **`AUTO_LOAD_HR_CONTENT=1`** — при каждом старте контейнера выполняются `load_courses`, `load_onboarding`, `load_articles`, `load_news`, `load_departments` (идемпотентно).

## Тесты

```bash
python manage.py test apps.core.tests apps.accounts.tests apps.onboarding.tests apps.courses.tests apps.analytics.tests
```

## Технологии

- Python, Django 4.x
- PostgreSQL, Redis
- Alpine.js, Tailwind CSS
- Без React/Next.js — server-rendered
