# Стратегический снимок — Dim Kava

> Зафиксировано: дизайн закреплён, план приведён в порядок. Документ обновлять при смене стратегии.

---

## 1. Текущее состояние (зафиксировано)

### Дизайн — закреплён ✅
- **Layout:** Top navbar (без sidebar), max-w-7xl контент
- **Эталоны:** `design/etalon/dim-kava-education-visual`, `design/etalon/stitch_lesson_view`
- **Бренд:** Dim Kava (не Atelier)
- **CSS:** Tailwind v4, static prebuild, `input.css` → `tailwind.css`
- **Компоненты:** glass-nav, card-atelier, btn-primary, btn-secondary, Material Symbols

### Функциональность
- Dashboard, Courses, Onboarding, Knowledge base, News, Profile — реальные данные из БД
- Departments, Analytics, Notifications, Search — страницы есть, данные mock
- Login (TemplateView, форма без обработки)

### Тесты
- `python manage.py test apps.core.tests` — smoke-тесты по всем страницам (26 тестов). Запускать после изменений в шаблонах/URL/views.

### Документация
- [INDEX.md](INDEX.md) — оглавление, порядок чтения
- [ONBOARDING_DEV.md](ONBOARDING_DEV.md) — роадмап для разработчика (вернулся к проекту)
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — фазы 0–11
- [FEATURES_BACKLOG.md](FEATURES_BACKLOG.md) — ачивки, комментарии, HR Task Stack
- [GUIDING_QUESTIONS.md](GUIDING_QUESTIONS.md) + [ANSWERS](ANSWERS) — требования

---

## 2. Следующий шаг по плану

1. **0.6** — ответы на GUIDING_QUESTIONS уже в ANSWERS; при необходимости уточнить план
2. **Фаза 1** — ✅ выполнена (auth, create_default_users, docker-compose, production)
3. **Фаза 2** — ✅ (модели, load_onboarding, mark_step_complete, signals)
4. **Фаза 3** — ✅ (Course, Lesson, Quiz, load_courses, UserProgress)
5. **Фаза 4** — ✅ (KBSection, Article, NewsPost, load_articles, load_news)
6. **Фаза 5** — ✅ (Department, Role, load_departments, learning path)
7. **Фаза 6** — ✅ (Analytics dashboard, HR-only, real metrics)
8. Далее: Notifications → Search → Gamification → Admin

---

## 3. Очистка лишнего (аккуратно)

| Что | Действие | Риск |
|-----|----------|------|
| `experiments/stitch-code` | Удалить (пустой файл) | Нет |
| `experiments/stitch_output/` | Удалить — дублирует design/etalon. DESIGN_SYSTEM_REFERENCE.md уже в design/DESIGN_SYSTEM.md | Низкий: проверить, что design/DESIGN_SYSTEM.md покрывает нужды |
| `design/reference/` | Опционально: убрать из `@source` в input.css, оставить папку как архив, или удалить после проверки. Сейчас input.css сканирует и reference, и stitch_lesson_view — overlap | Средний: при удалении @source пересобрать CSS, проверить все страницы |
| `design/etalon/dim-kava-education-visual/` | В .gitignore, не коммитить | — |

**Порядок очистки:**
1. Удалить `experiments/stitch-code`
2. Удалить `experiments/stitch_output/` (если design/DESIGN_SYSTEM.md достаточен)
3. design/reference — оставить как есть до стабилизации, потом решить

---

## 4. Что не трогать

- `design/etalon/stitch_lesson_view/` — используется в @source
- `templates/`, `static/css/` — актуальные шаблоны и стили
- `docs/` — вся документация
