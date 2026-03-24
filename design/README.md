# Design — эталонные шаблоны и дизайн-система

> **Главный визуальный эталон:** [dim-kava-education-visual](https://github.com/IvanBondarenkoIT/dim-kava-education-visual) — React + Tailwind v4.

---

## Структура

```
design/
├── README.md           # этот файл
├── DESIGN_SYSTEM.md    # Философия дизайна, токены, Do's & Don'ts
├── etalon/             # Канонические источники
│   ├── dim-kava-education-visual/   # React-эталон (git clone)
│   └── stitch_lesson_view/          # HTML от Stitch (code.html)
└── reference/          # HTML-копии для Django
    ├── authentication.html
    ├── lesson_view.html
    └── ...
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

## Связь с etalon/

- **design/etalon/dim-kava-education-visual/** — главный эталон (React, Layout, CSS)
- **design/etalon/stitch_lesson_view/** — HTML от Stitch (lesson_view, dashboard, …)
- **design/reference/** — HTML-копии для Django
