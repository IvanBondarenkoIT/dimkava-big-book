# План: эталон и синхронизация с dim-kava-education-visual

> **Архив.** Выполнено. Оставлено для истории.
>
> Цель была: добиться 1:1 соответствия визуала с [dim-kava-education-visual](https://github.com/IvanBondarenkoIT/dim-kava-education-visual).

---

## Текущее состояние

| Источник | Стек | Расположение |
|----------|------|--------------|
| stitch_lesson_view | HTML + Tailwind CDN + Material Symbols | experiments/stitch_lesson_view/ |
| dim-kava-education-visual | React + Vite + Tailwind v4 + Lucide | GitHub (внешний) |
| design/reference/ | HTML-копии эталонов | design/reference/ |
| Наш проект | Django + Tailwind v4 prebuild | templates/, static/ |

---

## Итеративный план

### Итерация 1: Структура и источники ✅
- [x] Переместить `experiments/stitch_lesson_view/` → `design/etalon/stitch_lesson_view/`
- [x] Клонировать `dim-kava-education-visual` в `design/etalon/dim-kava-education-visual/`
- [x] Обновить `design/README.md`, `DESIGN_SYSTEM.md` — указать dim-kava-education-visual как главный визуальный эталон

### Итерация 2: CSS и дизайн-токены ✅
- [x] Синхронизировать `static/css/input.css` с `dim-kava-education-visual/src/index.css`
- [x] Привести body, glass-nav, btn-primary, card-atelier к эталону
- [x] Проверить: `bg-linear-to-r`, `rounded-default`, `text-on-surface-variant`

### Итерация 3: Layout и Navbar ✅
- [x] Переработать `base.html` под структуру dim-kava-education-visual:
  - Top navbar (не sidebar): "Atelier" брендинг, Dashboard, Courses, Profile, поиск, аватар
  - Footer: Dim Kava © 2026
- [x] Маршруты: `/` (Dashboard), `/courses`, `/profile`

### Итерация 4: Страницы-компоненты (в работе)
- [x] Dashboard: Hero, Streak/Points, Continue Learning, Recommended, Recent Badges
- [ ] CourseList: Curriculum, категории, карточки курсов
- [ ] LessonView: Back, progress, контент, Next/Previous
- [ ] Profile: по эталону Profile.tsx

### Итерация 5: Иконки и полировка
- [ ] Lucide vs Material Symbols — решить, добавлять ли Lucide для 1:1
- [ ] Анимации (motion) — опционально, Alpine.js или CSS
- [ ] Footer "Dim Kava © 2026"

---

## Маппинг dim-kava-education-visual → Django

| Компонент | Маршрут | Django app |
|-----------|---------|------------|
| Dashboard | / | core |
| CourseList | /courses | courses |
| CourseDetail | /courses/:id | courses |
| LessonView | /courses/:id/lessons/:lessonId | courses |
| Profile | /profile | accounts |

---

## Ключевые отличия эталона

- **Navbar:** Sidebar слева, "Atelier", 3 пункта (Dashboard, Courses, Profile)
- **CSS:** `bg-surface/70 backdrop-blur-xl`, `bg-linear-to-r from-primary to-primary-container`
- **Карточки:** `rounded-default`, `hover:shadow-xl hover:shadow-primary/5`
- **Иконки:** Lucide (Coffee, LayoutDashboard, BookOpen, User)
