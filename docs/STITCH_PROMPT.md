# Промпт для Stitch — Dim Kava Internal Learning Portal

> Скопируйте текст ниже в [Stitch (Google)](https://stitch.withgoogle.com/) для генерации дизайна.
> Этот промпт учитывает: ANSWERS, base.md, mobile-first, роли (включая Кандидатов), MVP.

---

## Текст промпта (копировать в Stitch)

```
Design a mobile-first internal learning portal for a specialty coffee company called "Dim Kava".

Product: Corporate training platform for employees and job candidates. Internal use only — courses, onboarding, knowledge base, news, quizzes.

Target users (design for all):
- Job Candidates — minimal registration (name, email, phone), view intro materials, take tests, see results
- Employees — baristas, store staff, managers (main learning audience)
- HR / Directors — manage content, view reports, assign courses
- Admins — full system access

Platform: Responsive web app. Start with mobile (primary), then provide desktop/tablet variants. Sidebar collapses to hamburger on mobile.

---

Screens to design (in order of priority):

1. Authentication
   - Login: email + password, "Remember me" checkbox
   - Optional buttons: "Continue with Google" / "Continue with Facebook" (placeholders for future)
   - Sign-up for candidates: name, email, phone, password (minimal form)
   - Brand logo at top, clean layout
   - "Forgot password" link

2. Candidate onboarding welcome
   - Short intro: "Welcome to Dim Kava learning"
   - Progress bar (e.g. 0% — 25% — 50% — 75% — 100%)
   - Module list: Day 1, Days 2–3, Week 1, Week 2, Week 3, Month 1, Month 2, Month 3
   - Each module: status badge (Not started / In progress / Completed), estimated time
   - Card-based layout, tap to open module

3. Employee home / dashboard
   - Greeting: "Hi, [Name]"
   - Quick access cards: My onboarding | Courses | Knowledge base | News
   - "Next recommended action" block (e.g. "Continue: Week 1 — Lesson 3" or "Complete quiz: Day 3")
   - Optional small progress summary (e.g. "2 of 8 modules done")

4. Lesson view (course content)
   - Header: lesson title, estimated duration (e.g. "5 min")
   - Content area: text blocks, image placeholders, video placeholder
   - Sticky footer: "Mark as done" button (primary), "Next lesson" (secondary)
   - Breadcrumb or back link to course

5. Quiz / test screen
   - Progress: "Question 3 of 12"
   - One question at a time, clear typography
   - Multiple-choice answers (radio style or card taps)
   - Primary: "Submit" or "Next"
   - Secondary: "Skip for now" (if applicable)
   - After submit: show correct/incorrect, optional brief feedback

6. Knowledge base (wiki)
   - Section list or tabs: Procedures, Service standards, Company info, Training
   - Article list within section: title, short excerpt, "Read" link
   - Article detail: title, body text, optional "Related courses" block

7. News feed
   - List of news cards: title, date, short excerpt, tag (Important / Training / HR / General)
   - Pinned item at top if any
   - Single news post: title, date, full body

8. Admin / HR content list
   - Table or card layout: Courses, Articles, News
   - Filters: status (draft / published), department
   - "Create new" button prominent
   - Row actions: Edit, Preview, Delete

9. Global layout (for desktop)
   - Topbar: logo (left), search bar (center), notification bell with badge (right), user avatar + dropdown (Profile / Logout), language switcher (EN | RU | KA)
   - Sidebar (left, collapsible): nav links — Home, Onboarding, Courses, Knowledge base, News; hide items by role
   - Main content area with breadcrumbs at top
   - Footer: minimal or none

---

Style and visual direction — CRITICAL: Maximally modern, youth-oriented, gamified. Functionality first, but the look must feel fresh, energetic, and engaging like a Gen Z app.

Color palette: Coffee-inspired warm tones, elevated
- Backgrounds: soft cream, light beige, warm white
- Text: dark espresso brown, medium brown for secondary
- Accent: one vibrant accent (muted teal, soft green, or warm amber) for primary buttons, links, highlights, gamification elements
- Gamification elements: progress rings, streak indicators, achievement badges, level-up visuals — use accent color and subtle gradients
- Avoid: harsh reds, cold corporate blues, dull grays

Look and feel: Modern, youth-oriented, gamified. Bold but not noisy. Rounded corners (12–16px). Subtle gradients, soft shadows, micro-interactions. Progress bars, completion badges, "streak" or "level" indicators visible on dashboard. Cards feel like achievements. Plenty of white space. Easy to read and tap.

Typography: Contemporary sans-serif (e.g. Plus Jakarta Sans, Outfit, or similar — not generic Inter). Clear hierarchy, slightly bolder headings. Body text readable on mobile. Captions smaller, muted.

Components: Card-based layout with gamification cues — progress rings, checkmarks, badges, "X of Y completed" counters. Icons: rounded, friendly, possibly filled for completed states. Status badges vibrant (green = done, amber = in progress, gray = not started). Primary buttons prominent, inviting tap.

Brand personality: Youthful specialty coffee culture meets gamified learning — modern, energetic, achievement-driven, warm and inviting. Feels like an app young baristas would enjoy using daily. For mandatory/safety content only: tone down to strictly minimal (no confetti).

Special notes:
- Mobile: tap targets at least 44px, thumb-friendly navigation
- Accessibility: good contrast, labels on all interactive elements
- Multi-language ready: leave space for longer text (Russian, Georgian can be 20–30% longer than English)
```

---

## Что добавлено / изменено относительно твоего черновика

| Аспект | Изменение |
|--------|-----------|
| **Кандидаты** | Явно выделены: минимальная регистрация, свой flow онбординга |
| **Роли** | Уточнены: Candidate, Employee, HR/Director, Admin |
| **Layout** | Добавлен глобальный layout (topbar, sidebar, language switcher) из base.md |
| **Языки** | EN \| RU \| KA в topbar, учёт длины текста |
| **Safety/compliance** | Из base.md: для обязательного контента — минимальный, без «праздничных» элементов |
| **Экраны** | Добавлены: Knowledge base, News, Admin list; уточнены детали уроков и квизов |
| **Mobile** | Tap targets 44px, thumb-friendly |
| **a11y** | Contrast, labels |

---

## После генерации в Stitch

1. ~~Скачай или экспортируй~~ **Готово:** репозиторий [dim-kava-education-visual](https://github.com/IvanBondarenkoIT/dim-kava-education-visual) склонирован в `experiments/stitch_output/`.
2. Референс стилей: **`experiments/stitch_output/DESIGN_SYSTEM_REFERENCE.md`** — токены, компоненты, Tailwind-классы.
3. При переносе в Django templates используй:
   - Tailwind CSS для стилей
   - Alpine.js для интерактивности
   - Компоненты из `templates/components/` (progress_bar, course_card и т.д.)

Могу помочь адаптировать конкретные экраны из Stitch под Django/Tailwind, когда будут готовы.
