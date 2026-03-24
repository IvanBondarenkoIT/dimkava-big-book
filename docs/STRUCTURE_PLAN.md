# План структуры проекта — Dim Kava Big Book

> Где что хранится. Цель — чистая, предсказуемая структура.

---

## Текущая структура (исходники)

```
dimkava-big-book/
├── input/
│   ├── prompts/              # Промпты для Cursor/AI
│   │   ├── base.md
│   │   ├── gamification.md
│   │   ├── best_practices.md
│   │   └── core-rules.md
│   └── hr docs/
│       └── content/          # HR-контент (YAML, JSON)
│           ├── onboarding_training_plan.yaml
│           ├── onboarding_quizzes.yaml
│           ├── sops_and_standards.yaml
│           ├── initial_data.json
│           └── README.md
├── docs/                     # Планирование и маппинг
│   ├── PROMPTS_MAPPING.md
│   ├── STRUCTURE_PLAN.md
│   ├── GUIDING_QUESTIONS.md
│   └── DEVELOPMENT_PLAN.md
├── design/                   # Эталонные шаблоны
│   ├── DESIGN_SYSTEM.md
│   ├── etalon/               # Канонические источники
│   │   ├── dim-kava-education-visual/  # React-эталон (git clone)
│   │   └── stitch_lesson_view/         # HTML от Stitch
│   └── reference/*.html      # authentication, lesson_view...
└── experiments/
    ├── stitch_output/        # React-прототип (legacy)
    └── README.md
```

---

## Целевая структура (после реализации base.md)

```
dimkava-big-book/
├── input/
│   ├── prompts/
│   └── hr docs/content/
│
├── docs/
│   ├── PROMPTS_MAPPING.md
│   ├── STRUCTURE_PLAN.md
│   ├── GUIDING_QUESTIONS.md
│   └── DEVELOPMENT_PLAN.md
│
├── design/                   # Эталонные шаблоны (Stitch)
│   ├── DESIGN_SYSTEM.md
│   └── reference/*.html      # Берём в Django, наполняем
│
├── experiments/
│   ├── stitch_lesson_view/
│   ├── stitch_output/
│   └── README.md
│
├── dimkava_portal/           # Django-проект (согласно base.md)
│   ├── config/
│   ├── apps/
│   ├── templates/
│   ├── static/
│   ├── locale/
│   ├── media/
│   ├── fixtures/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── docker-compose.yml
│
├── tests/                    # Интеграционные/кросс-модульные тесты (опционально)
│
├── .gitignore
├── .env.example              # или в dimkava_portal/
└── README.md
```

---

## Правила для experiments/

| Правило | Описание |
|---------|----------|
| **Временность** | Файлы в experiments/ — временные. После проверки гипотезы: либо переносим в основную кодовую базу, либо удаляем. |
| **Не трогать прод** | Код в experiments/ не должен напрямую влиять на production. |
| **Именование** | Использовать префиксы: `exp_`, `scratch_`, `WIP_` — чтобы было ясно, что это эксперимент. |
| **README** | В experiments/README.md — краткие правила и примеры. |
| **Коммиты** | Можно коммитить эксперименты отдельными коммитами с префиксом `experiment:` или `wip:`. После подтверждения пользы — squash в нормальный feat. |

---

## Где хранятся тесты

| Уровень | Расположение | Пример |
|---------|--------------|--------|
| Unit (модуль) | `apps/<app>/tests/` | `apps/gamification/tests/test_services.py` |
| Интеграционные | `tests/` в корне (если нужны) | `tests/test_onboarding_flow.py` |
| Фикстуры | `fixtures/` | `fixtures/initial_data.json` |

---

## Связь design/reference/ → Django templates

| Эталон | Django templates |
|--------|------------------|
| authentication.html | accounts/login.html, signup |
| lesson_view.html | courses/lesson_detail.html |
| candidate_onboarding.html | onboarding/overview.html |
| employee_dashboard.html | home.html, dashboard |
| quiz_screen.html | courses/quiz.html (часть урока) |
| knowledge_base.html | knowledge_base/section.html, article.html |
| news_feed.html | news/list.html, news/detail.html |
| admin_content_list.html | admin custom или HR UI |
| desktop_dashboard_layout.html | base.html (layout) |

---

## Связь input/ → dimkava_portal/

| Файл в input/ | Куда попадает в проекте |
|---------------|-------------------------|
| initial_data.json | fixtures/initial_data.json (или management command) |
| onboarding_training_plan.yaml | Загрузка через `load_onboarding` management command |
| onboarding_quizzes.yaml | Загрузка через `load_quizzes` management command |
| sops_and_standards.yaml | Загрузка через `load_article_content` management command |
| prompts/*.md | Только для Cursor — в код не копируются |

---

## Переименование папки "hr docs"

Папка `hr docs` содержит пробел — это может мешать скриптам. Варианты:
- Оставить как есть (работает везде, но неудобно в CLI)
- Переименовать в `hr_docs` или `hrdocs` — проще для скриптов

**Рекомендация:** переименовать в `hr_docs` при первом рефакторинге.
