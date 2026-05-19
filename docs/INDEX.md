# Оглавление документации — Dim Kava

> **Правило:** на каждом шаге разработки сверяться с [core-rules.md](../input/prompts/core-rules.md) — git, тесты, checkpoint, naming.

---

## Точка входа

| Документ | Когда читать | Описание |
|----------|--------------|----------|
| [ONBOARDING_DEV.md](ONBOARDING_DEV.md) | **Вернулся к проекту** — первый файл | Роадмап: старт, порядок чтения, чеклист |

---

## План и текущее состояние

| Документ | Когда читать | Описание |
|----------|--------------|----------|
| [STRATEGIC_SNAPSHOT.md](STRATEGIC_SNAPSHOT.md) | Перед любой работой | Текущее состояние, дизайн закреплён, следующий шаг, тесты |
| [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) | Планирование фазы | Фазы 0–11, задачи, checkpoint-критерии |

---

## Инструкции по ролям (как пользоваться)

| Документ | Для кого | Описание |
|----------|----------|----------|
| [ROLE_GUIDES.md](ROLE_GUIDES.md) | Все | Ссылки на инструкции по ролям |
| [ROLE_GUIDE_CANDIDATE.md](ROLE_GUIDE_CANDIDATE.md) | Candidate | Регистрация, ограничения доступа, как учиться |
| [ROLE_GUIDE_EMPLOYEE.md](ROLE_GUIDE_EMPLOYEE.md) | Employee | Профиль, KPI, ILP, feedback |
| [ROLE_GUIDE_HR.md](ROLE_GUIDE_HR.md) | HR | Кандидаты, контент для кандидатов, мониторинг, конвертация |
| [ROLE_GUIDE_ADMIN.md](ROLE_GUIDE_ADMIN.md) | Admin | Окружение, доступы, стабильность, инциденты |
| [HR_FULL_FUNCTIONAL_CHECKLIST.md](HR_FULL_FUNCTIONAL_CHECKLIST.md) | HR | Полный поэтапный чеклист проверки всего функционала |
| [FUNCTIONAL_OVERVIEW_SHORT.md](FUNCTIONAL_OVERVIEW_SHORT.md) | Все | Короткое и понятное описание функционала системы |
| [DIRECTOR_REPORT_WHAT_WAS_DONE.md](DIRECTOR_REPORT_WHAT_WAS_DONE.md) | Director | Что реализовано, зачем, эффект и следующие шаги |

---

## Контекст и решения

| Документ | Когда читать | Описание |
|----------|--------------|----------|
| [ANSWERS](ANSWERS) | Нужно вспомнить «почему так» | Ответы на GUIDING_QUESTIONS: аудитория, роли, MVP, хостинг |
| [GUIDING_QUESTIONS.md](GUIDING_QUESTIONS.md) | Редактирование ANSWERS | Вопросы, на которые отвечают в ANSWERS |

---

## Референсы (по необходимости)

| Документ | Когда читать | Описание |
|----------|--------------|----------|
| [STRUCTURE_PLAN.md](STRUCTURE_PLAN.md) | «Где это лежит?» | Структура папок, связь design → Django, input → проект |
| [PROMPTS_MAPPING.md](PROMPTS_MAPPING.md) | Работа с AI / Cursor | Какие промпты применять, порядок, связь с фазами |
| [FEATURES_BACKLOG.md](FEATURES_BACKLOG.md) | Будущие фичи (последняя очередь) | Ачивки и комментарии — в конец roadmap; комментарии только после approve HR + админка модерации |
| [I18N_MULTILINGUAL_RUNBOOK.md](I18N_MULTILINGUAL_RUNBOOK.md) | Операции EN/KA/RU | Как переключать язык, грузить и редактировать мультиязычный контент |
| [WINDOWS_SERVER_DEPLOY.md](WINDOWS_SERVER_DEPLOY.md) | **Production на своём сервере** | Windows + Docker Desktop, GHCR, Caddy, GitHub Actions |
| [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) | Деплой Railway (legacy) | Переменные, `AUTO_LOAD_HR_CONTENT`, `compilemessages` в образе |
| [I18N_RU_DONE_AND_KA_PLAN.md](I18N_RU_DONE_AND_KA_PLAN.md) | После фазы RU / перед KA | Что сделано для русского и пошаговый план грузинского без пропусков |

---

## Дизайн (отдельная папка)

| Документ | Путь | Описание |
|----------|------|----------|
| DESIGN_SYSTEM.md | `design/DESIGN_SYSTEM.md` | Токены, цвета, компоненты, философия |
| design/README | `design/README.md` | Структура design/, etalon, reference |

---

## Промпты (для AI, не для чтения подряд)

| Файл | Путь | Назначение |
|------|------|------------|
| base.md | `input/prompts/base.md` | Базовая архитектура |
| gamification.md | `input/prompts/gamification.md` | Очки, бейджи, миссии |
| best_practices.md | `input/prompts/best_practices.md` | Менторство, ILP, поиск |
| **core-rules.md** | `input/prompts/core-rules.md` | **Правила кода — проверять на каждом шаге** |

---

## Архив (выполнено, для истории)

| Документ | Статус | Описание |
|----------|--------|----------|
| [DUMMY_PAGES_PLAN.md](DUMMY_PAGES_PLAN.md) | ✅ Выполнено | План дами-страниц — реализовано в 0.8 |
| [ETALON_SYNC_PLAN.md](ETALON_SYNC_PLAN.md) | ✅ Выполнено | План синхронизации с эталоном — реализовано |
| [STITCH_PROMPT.md](STITCH_PROMPT.md) | Референс | Текст промпта для Stitch (если перегенерировать дизайн) |

---

## Сводка: что читать в каком порядке

**Вернулся после паузы:**
1. ONBOARDING_DEV
2. STRATEGIC_SNAPSHOT
3. DEVELOPMENT_PLAN (фазы + следующий шаг)

**Начал новую фазу:**
1. DEVELOPMENT_PLAN (задачи фазы)
2. core-rules (чек перед коммитом)

**«Почему так сделано?»:**
1. ANSWERS
2. GUIDING_QUESTIONS (если нужно дополнить)

**«Где что лежит?»:**
1. STRUCTURE_PLAN
