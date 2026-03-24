# План создания дами-страниц

> **Архив.** Выполнено в рамках DEVELOPMENT_PLAN 0.8. Оставлено для истории.
>
> Создавали «пустышки» в стиле design/reference/, потом наполняли функционалом.
> Без моделей, без БД — только views + templates с mock-контентом.

## Статус: ✅ Выполнено

Дами-страницы созданы. Запуск: `python manage.py runserver`

---

## Список страниц (из base.md + design/reference)

| # | URL | Страница | Референс | Примечание |
|---|-----|----------|----------|------------|
| 1 | `/` | Home / Dashboard | employee_dashboard, desktop_dashboard_layout | Главная |
| 2 | `/login/` | Login | authentication | Без реальной авторизации |
| 3 | `/logout/` | Logout | — | Redirect на login |
| 4 | `/profile/` | Profile | employee_dashboard (Profile из stitch_output) | Профиль |
| 5 | `/onboarding/` | Onboarding overview | candidate_onboarding | Прогресс, модули |
| 6 | `/onboarding/<slug>/` | Module detail | — | Создаём в том же стиле |
| 7 | `/courses/` | Course catalog | employee_dashboard (карточки курсов) | Список курсов |
| 8 | `/courses/<slug>/` | Course detail | — | Создаём в том же стиле |
| 9 | `/courses/<slug>/lessons/<id>/` | Lesson page | lesson_view | Урок |
| 10 | `/courses/<slug>/lessons/<id>/quiz/` | Quiz | quiz_screen | Квиз (или часть урока) |
| 11 | `/wiki/` | Knowledge base home | knowledge_base | Секции |
| 12 | `/wiki/<section>/` | Section | knowledge_base | Список статей |
| 13 | `/wiki/<section>/<slug>/` | Article | knowledge_base | Статья |
| 14 | `/news/` | News feed | news_feed | Список новостей |
| 15 | `/news/<slug>/` | News post | news_feed | Одна новость |
| 16 | `/departments/` | Departments list | — | Создаём в том же стиле |
| 17 | `/departments/<slug>/` | Department detail | — | Создаём в том же стиле |
| 18 | `/analytics/` | HR Analytics | admin_content_list | Дашборд HR |
| 19 | `/notifications/` | Notifications | — | Создаём в том же стиле |
| 20 | `/search/` | Search results | — | Создаём в том же стиле |

---

## Порядок реализации (по шагам)

### Шаг 1: Project scaffold
- Django project (dimkava_portal/)
- config/settings (base, development)
- apps: core (или home), accounts, onboarding, courses, knowledge_base, news, departments, analytics, notifications, search
- requirements.txt, .env.example
- manage.py runserver работает

### Шаг 2: Base layout
- base.html из desktop_dashboard_layout
- Tailwind CDN + цвета из design
- Sidebar, topbar, {% block content %}

### Шаг 3: Auth-страницы (дами)
- login.html из authentication
- logout view (redirect)
- Всегда «залогинены» (без проверки)

### Шаг 4: Main pages (Home, Profile)
- home.html (dashboard)
- profile.html

### Шаг 5: Onboarding
- onboarding/overview.html
- onboarding/module_detail.html (дами для slug)

### Шаг 6: Courses
- courses/list.html
- courses/detail.html (дами)
- courses/lesson_detail.html из lesson_view
- courses/quiz.html из quiz_screen

### Шаг 7: Knowledge base
- knowledge_base/home.html
- knowledge_base/section.html
- knowledge_base/article.html

### Шаг 8: News
- news/list.html
- news/detail.html

### Шаг 9: Departments, Analytics, Notifications, Search
- departments/list.html, detail.html
- analytics/dashboard.html
- notifications/list.html
- search/results.html

### Шаг 10: 404, 500
- templates/404.html, 500.html

---

## Mock-данные

В каждой view передаём через context словарь с фейковыми данными. Пример:
```python
context = {
    'user_name': 'Alex',
    'progress': 25,
    'modules': [{'slug': 'day-1', 'title': 'Day 1', 'status': 'completed'}, ...],
}
```

---

## Референс стиля

Все страницы — по design/reference/ и design/DESIGN_SYSTEM.md.
Цвета, шрифты, компоненты — без изменений.
