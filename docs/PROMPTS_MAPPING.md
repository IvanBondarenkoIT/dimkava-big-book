# Маппинг промптов — Dim Kava Big Book

> Документ описывает, какие промпты есть в проекте, в каком порядке их применять и что каждый добавляет.

---

## Порядок применения (как указано в base.md)

| # | Файл | Путь | Назначение |
|---|------|------|------------|
| 1 | **base.md** | `input/prompts/base.md` | Главная архитектура: tech stack, модели, страницы, структура проекта |
| 2 | **gamification.md** | `input/prompts/gamification.md` | Расширение: очки, бейджи, миссии, уровни, лидерборд |
| 3 | **best_practices.md** | `input/prompts/best_practices.md` | Расширение: менторство, ILP, уведомления, поиск, фидбек |
| 4 | **core-rules.md** | `input/prompts/core-rules.md` | Правила кода: git, Django, тесты, безопасность — применяется везде |

---

## Детальное описание промптов

### 1. base.md — Базовая архитектура

**Что задаёт:**
- Tech stack: Django 4.x, Alpine.js, Tailwind, PostgreSQL, Redis, Celery
- Модели: UserProfile, Course, Lesson, TestQuestion, UserProgress, KBSection, Article, NewsPost, Department, Role, Notification
- URL-структура: /, /login/, /courses/, /onboarding/, /wiki/, /news/, /departments/, /analytics/, /search/
- Layout: topbar, sidebar, breadcrumbs
- i18n: EN / RU / KA
- Роли: employee, hr_manager, admin
- Порядок реализации: 10 шагов (scaffold → onboarding → courses → … → gamification → admin)

**Важно:** Без base.md не имеет смысла применять остальные — он определяет фундамент.

---

### 2. gamification.md — Геймификация

**Что добавляет:**
- Новое приложение `apps/gamification/`
- Модели: GamificationProfile, Badge, UserBadge, Mission, MissionStep, UserMissionProgress, PointsLog
- Сервисы: `award_points`, `award_badge`, `update_mission_progress`, `get_level_progress`
- Сигналы: на lesson_completed, quiz_passed, onboarding_module_completed
- URL: /dashboard/, /leaderboard/
- Правило: compliance/safety контент — минимум геймификации в UI

**Зависит от:** base.md (модели courses, onboarding, accounts)

---

### 3. best_practices.md — Расширения UX и LMS

**Что добавляет:**
- Менторство: Mentor, MentorAssignment, MentorSession
- ILP: IndividualLearningPlan, ILPItem
- AssignmentRule: автоназначение онбординга и курсов по роли/департаменту
- Notification: логика триггеров, поле external_channel
- Content lifecycle: responsible_editor, is_stale, review_required_after_days
- Global search: SearchResult, global_search()
- Feedback: LessonRating, OnboardingFeedback
- "Where to start" — UX-логика следующих шагов

**Зависит от:** base.md, gamification.md

---

### 4. core-rules.md — Правила разработки

**Что задаёт:**
- Переменные окружения: python-decouple, .env.example
- Git: один коммит на шаг, формат сообщений, pre-commit сканирование на секреты
- Checkpoint-протокол: после каждого шага — summary
- Django: CBV, select_related/prefetch_related, service layer, permissions
- Тесты: каждый сервис — хотя бы один unit-тест
- .gitignore, 404/500 страницы
- Deployment на Railway
- Чеклисты: performance, code review, a11y

**Применяется:** на протяжении всего проекта, не только на этапе 4.

---

## Взаимосвязи промптов

```
base.md (фундамент)
    │
    ├── gamification.md (расширяет courses + onboarding)
    │
    └── best_practices.md (расширяет всё: onboarding, courses, accounts, gamification)
                │
                └── core-rules.md (обёртка над всем кодом)
```

---

## Где хранятся промпты

| Категория | Путь | Содержимое |
|-----------|------|------------|
| Промпты | `input/prompts/` | base.md, gamification.md, best_practices.md, core-rules.md |
| HR-контент | `input/hr docs/content/` | onboarding_training_plan.yaml, onboarding_quizzes.yaml, sops_and_standards.yaml, initial_data.json |
| Документация | `input/hr docs/content/README.md` | Как загружать контент в Django |

---

## Как использовать в Cursor

1. Начать диалог с @base.md
2. Для геймификации — добавить @gamification.md
3. Для менторства, ILP и т.д. — @best_practices.md
4. core-rules.md — держать в контексте при любом коде (можно добавить в .cursorrules)
