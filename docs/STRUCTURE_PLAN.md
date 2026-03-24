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
├── docs/                     # Планирование и маппинг (новое)
│   ├── PROMPTS_MAPPING.md
│   ├── STRUCTURE_PLAN.md     # этот файл
│   ├── GUIDING_QUESTIONS.md
│   └── DEVELOPMENT_PLAN.md
└── experiments/              # Эксперименты и разведка (новое)
    ├── README.md             # Правила использования
    └── (временные файлы)
```

---

## Целевая структура (после реализации base.md)

```
dimkava-big-book/
├── input/                    # Исходники — не трогаем при автогенерации
│   ├── prompts/
│   └── hr docs/content/
│
├── docs/                     # Документация проекта
│   ├── PROMPTS_MAPPING.md
│   ├── STRUCTURE_PLAN.md
│   ├── GUIDING_QUESTIONS.md
│   └── DEVELOPMENT_PLAN.md
│
├── experiments/              # Эксперименты
│   ├── README.md
│   ├── temp/                 # Временные файлы (gitignore опционально)
│   └── scratch/              # Черновики, разведка
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
