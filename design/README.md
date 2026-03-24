# Design — эталонные шаблоны и дизайн-система

> Шаблоны из Stitch берём **прямо в Django** и наполняем данными. Это эталон визуала.

---

## Структура

```
design/
├── README.md           # этот файл
├── DESIGN_SYSTEM.md    # Философия дизайна, токены, Do's & Don'ts (из Stitch)
└── reference/          # Эталонные HTML-шаблоны — источник для Django
    ├── authentication.html
    ├── lesson_view.html
    ├── candidate_onboarding.html
    ├── employee_dashboard.html
    ├── quiz_screen.html
    ├── knowledge_base.html
    ├── news_feed.html
    ├── admin_content_list.html
    └── desktop_dashboard_layout.html
```

---

## reference/ — эталонные шаблоны

Каждый файл — полная HTML-страница (Tailwind CDN, Material Symbols). При реализации Django:

1. Берём структуру и разметку из эталона
2. Выносим общее в `base.html` (header, footer, tailwind-config)
3. Заменяем статичный контент на `{{ variable }}`, `{% for %}`, `{% block %}`
4. Кладём в `templates/courses/`, `templates/onboarding/` и т.д.

| Эталон | Django / base.md |
|--------|------------------|
| authentication.html | `/login/`, `/logout/`, sign-up |
| lesson_view.html | `/courses/<slug>/lessons/<id>/` |
| candidate_onboarding.html | `/onboarding/` |
| employee_dashboard.html | `/` Home |
| quiz_screen.html | Quiz внутри урока |
| knowledge_base.html | `/wiki/`, `/wiki/<section>/<slug>/` |
| news_feed.html | `/news/` |
| admin_content_list.html | Admin/HR content management |
| desktop_dashboard_layout.html | Layout: topbar, sidebar |

---

## DESIGN_SYSTEM.md

Креативная философия, цвета, типографика, компоненты. Читать перед версткой.

---

## Связь с experiments/

- **experiments/stitch_lesson_view/** — исходные файлы от Stitch (code.html в папках)
- **experiments/stitch_output/** — React-прототип из dim-kava-education-visual
- **design/reference/** — копия эталонов, основное место для работы с Django
