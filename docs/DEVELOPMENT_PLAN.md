# План разработки — Dim Kava Internal Learning Portal

> Большой план по шагам. Основа — base.md, порядок — base.md §14.
>
> **Оглавление:** [INDEX.md](INDEX.md) | **Состояние:** [STRATEGIC_SNAPSHOT.md](STRATEGIC_SNAPSHOT.md) | **core-rules:** проверять перед каждым шагом.

---

## Фаза 0: Подготовка ✅

| # | Задача | Статус | Коммит |
|---|--------|--------|--------|
| 0.1 | Git init, .gitignore | ✅ | init |
| 0.2 | Локальное окружение (venv, requirements.txt) | ✅ | chore: add Python env |
| 0.3 | Маппинг промптов (PROMPTS_MAPPING.md) | ✅ | — |
| 0.4 | План структуры (STRUCTURE_PLAN.md) | ✅ | — |
| 0.5 | Наводящие вопросы (GUIDING_QUESTIONS.md) | ✅ | — |
| 0.6 | Ответы на вопросы → корректировка плана | 🔲 | — |
| 0.7 | Tailwind prebuild: static CSS, без FOUC, parity с эталоном | ✅ | — |
| 0.8 | Etalon sync: dim-kava-education-visual, top navbar, все страницы | ✅ | — |

---

## Фаза 1: Project scaffold (base.md Step 1) ✅

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 1.1 | Django project structure | config/, manage.py | ✅ |
| 1.2 | Settings: base, development, production | config/settings/ | ✅ |
| 1.3 | .env.example, python-decouple | .env.example | ✅ |
| 1.4 | docker-compose.yml (Postgres + Redis) | docker-compose.yml | ✅ |
| 1.5 | requirements.txt | requirements.txt | ✅ |
| 1.6 | base.html (layout: topbar only, no sidebar) | templates/base.html | ✅ |
| 1.7 | Auth: login, logout, password reset | accounts/views, templates | ✅ |
| 1.8 | Profile page | accounts/ | ✅ |
| 1.9 | Management command: create default users | accounts/management/ | unit ✅ |
| 1.10 | 404, 500 templates | templates/ | ✅ |

**Checkpoint:** Пользователь может залогиниться, выйти, сбросить пароль, открыть профиль.

---

## Фаза 2: Onboarding module (base.md Step 2) ✅

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 2.1 | OnboardingProgram, OnboardingModule, OnboardingStep | onboarding/models.py | unit ✅ |
| 2.2 | OnboardingProgress | onboarding/models.py | ✅ |
| 2.3 | Load onboarding from YAML (management command) | onboarding/management/ | unit ✅ |
| 2.4 | Onboarding overview page + progress bar | onboarding/views, templates | ✅ |
| 2.5 | Module detail page | onboarding/ | ✅ |
| 2.6 | Mark step complete (service) | onboarding/services.py | unit ✅ |
| 2.7 | Signal: onboarding_module_completed | onboarding/signals.py | ✅ |

**Checkpoint:** Сотрудник видит онбординг, отмечает шаги, прогресс сохраняется.

---

## Фаза 3: Course catalog and lessons (base.md Step 3) ✅

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 3.1 | Course, Lesson, TestQuestion, UserProgress | courses/models.py | ✅ |
| 3.2 | Course list + filters | courses/views | ✅ |
| 3.3 | Course detail | courses/ | ✅ |
| 3.4 | Lesson page (video, text, file, quiz) | courses/ | ✅ |
| 3.5 | Quiz: отображение, проверка, сохранение результата | courses/ | unit ✅ |
| 3.6 | Load courses from YAML | courses/management/ | ✅ |
| 3.7 | Signal: lesson_completed, quiz_passed | courses/signals.py | ✅ |

**Checkpoint:** Каталог курсов, уроки, квизы работают, прогресс сохраняется.

---

## Фаза 4: Knowledge base and news (base.md Step 4) ✅

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 4.1 | KBSection, Article | knowledge_base/models.py | smoke ✅ |
| 4.2 | Wiki home, section, article pages | knowledge_base/views | smoke ✅ |
| 4.3 | Load articles from YAML | knowledge_base/management/ | smoke ✅ |
| 4.4 | NewsPost model, news feed, single post | news/ | smoke ✅ |

**Checkpoint:** База знаний и новости доступны.

---

## Фаза 5: Departments and roles (base.md Step 5) ✅

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 5.1 | Department, Role models | departments/ | smoke ✅ |
| 5.2 | Department list, detail with learning path | departments/views | smoke ✅ |
| 5.3 | Required/recommended courses per role | departments_seed.yaml | smoke ✅ |

**Checkpoint:** HR видит департаменты и роли, learning path отображается.

---

## Фаза 6: Analytics dashboard (base.md Step 6) ✅

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 6.1 | Analytics view (HR/admin only) | analytics/ | smoke ✅ |
| 6.2 | Metrics: courses, onboarding %, completion time | analytics/selectors.py | unit ✅ |
| 6.3 | Mock data → real aggregations | analytics/selectors.py | ✅ |

**Checkpoint:** HR видит дашборд с метриками.

---

## Фаза 7: Notifications (base.md Step 7)

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 7.1 | Notification model | notifications/ | — |
| 7.2 | Topbar bell + unread count | templates/components/ | — |
| 7.3 | Notifications page | notifications/views | — |
| 7.4 | Trigger logic (new course, deadline, badge) | notifications/ | unit |

**Checkpoint:** Уведомления создаются и отображаются.

---

## Фаза 8: Global search (base.md Step 8)

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 8.1 | SearchResult dataclass, global_search() | search/selectors.py | unit |
| 8.2 | Search bar in topbar | templates/ | — |
| 8.3 | Search results page | search/views | — |

**Checkpoint:** Поиск по курсам, статьям, новостям работает.

---

## Фаза 9: Gamification (gamification.md)

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 9.1 | Gamification app, models | gamification/ | — |
| 9.2 | services: award_points, award_badge, update_mission_progress | gamification/services.py | unit |
| 9.3 | selectors: dashboard context, leaderboard | gamification/selectors.py | unit |
| 9.4 | Signals: connect to courses, onboarding | gamification/signals.py | — |
| 9.5 | Dashboard, leaderboard pages | gamification/views | — |
| 9.6 | Badge widget, progress in templates | templates/components/ | — |

**Checkpoint:** Очки, бейджи, миссии, лидерборд работают.

---

## Фаза 10: Admin panel (base.md Step 10)

| # | Задача | Файлы | Тесты |
|---|--------|-------|-------|
| 10.1 | Admin для всех моделей | */admin.py | — |
| 10.2 | Custom list_display, filters, inlines | — | — |
| 10.3 | Stale content indicator (best_practices) | CourseAdmin, ArticleAdmin | — |

**Checkpoint:** HR/Admin управляют контентом через Django Admin.

---

## Фаза 11+: Расширения (best_practices.md)

> **Backlog:** см. [FEATURES_BACKLOG.md](FEATURES_BACKLOG.md) — ачивки у аватара, комментарии с пре-модерацией, HR Task Stack.

| # | Задача | Приоритет |
|---|--------|-----------|
| 11.1 | Mentorship (Mentor, MentorAssignment, MentorSession) | средний |
| 11.2 | Individual Learning Plans (ILP) | средний |
| 11.3 | AssignmentRule (auto-assign) | высокий |
| 11.4 | LessonRating, OnboardingFeedback | средний |
| 11.5 | Content lifecycle (responsible_editor, is_stale) | низкий |
| 11.6 | "Where to start" flow | высокий |

---

## Легенда статусов

- ✅ Выполнено
- 🔲 Не начато
- 🔄 В работе

---

## Core-rules чеклист

Перед каждой фазой: [core-rules](../input/prompts/core-rules.md) — git, тесты, checkpoint, naming.

| § | Тема | Статус |
|---|------|--------|
| 1 | Env vars, settings split | ✅ |
| 2 | Git: шаг = коммит, pre-commit scan | 🔲 |
| 3 | Checkpoint protocol | 🔲 |
| 4 | Django: URL naming, CBV, services | ✅ |
| 5 | Service layer rules | 🔲 |
| 6 | Templates: trans, components | 🔲 |
| 7 | **Static: Tailwind prebuild** | ✅ |
| 8 | Security | 🔲 |
| 9 | Error handling | 🔲 |
| 10 | Code comments | — |
| 11 | Naming conventions | ✅ |
| 12 | Testing | 🔲 |
| 13 | Railway deploy | 🔲 |
| 14 | Performance checklist | 🔲 |
| 15 | A11y | 🔲 |
| 16 | Logging | 🔲 |
| 17 | README | 🔲 |
| 18 | Code review checklist | 🔲 |

---

## Следующий шаг

1. **Проверить [core-rules](../input/prompts/core-rules.md)** перед каждым шагом.
2. Проверить страницы в браузере (стили без FOUC).
3. Перейти к Фазе 1: project scaffold (auth, settings, 404/500).
4. При необходимости — доработать план по ответам из ANSWERS (0.6).
