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

| Файл | Описание |
|------|----------|
| [docs/PROMPTS_MAPPING.md](docs/PROMPTS_MAPPING.md) | Маппинг промптов для Cursor |
| [docs/STRUCTURE_PLAN.md](docs/STRUCTURE_PLAN.md) | План структуры проекта |
| [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) | План разработки по фазам |
| [docs/GUIDING_QUESTIONS.md](docs/GUIDING_QUESTIONS.md) | Наводящие вопросы — заполните перед стартом |

## Локальная настройка (после создания Django-проекта)

1. Клонировать репозиторий
2. Скопировать `.env.example` → `.env`, заполнить значения
3. `docker-compose up -d` (Postgres + Redis)
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py loaddata fixtures/initial_data.json`
7. `python manage.py runserver`

## Дефолтные пользователи

См. `.env.example` — credentials задаются через переменные окружения.

## Тесты

```bash
pytest
```

## Технологии

- Python, Django 4.x
- PostgreSQL, Redis
- Alpine.js, Tailwind CSS
- Без React/Next.js — server-rendered
