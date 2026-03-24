# Онбординг разработчика — вернулся к проекту

> **Для кого:** ты вернулся к Dim Kava после паузы (неделя, полгода, год).  
> **Цель:** за 15–30 минут восстановить контекст и понять, что делать дальше.
>
> **Оглавление всех документов:** [INDEX.md](INDEX.md)

---

## Шаг 0: Быстрый старт (2 мин)

```bash
cd dimkava-big-book
python -m venv venv
venv\Scripts\activate   # Windows; Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Открой http://127.0.0.1:8000 — главная должна открыться.

```bash
python manage.py test apps.core.tests
```

Все 23 smoke-теста должны пройти. Если падают — что-то сломалось, смотри git diff / последние коммиты.

---

## Шаг 1: Что это за проект (5 мин)

**Dim Kava** — внутренний портал обучения для кофейни (LMS + онбординг).  
Сотрудники проходят курсы, тесты, онбординг. HR видит аналитику, департаменты, задачи.

**Сейчас:** все страницы есть (mock-данные), дизайн закреплён. Реальная логика (модели, auth, БД) — в работе по фазам.

**Читай:** [STRATEGIC_SNAPSHOT.md](STRATEGIC_SNAPSHOT.md) — состояние, дизайн, следующий шаг.

---

## Шаг 2: План и фазы (5 мин)

**Читай:** [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)

- Фаза 0 — подготовка (почти всё ✅)
- Фаза 1 — scaffold: auth, settings, docker
- Фазы 2–10 — онбординг, курсы, KB, новости, departments, analytics, notifications, search, gamification, admin
- Фаза 11+ — расширения

**Следующий шаг** всегда внизу DEVELOPMENT_PLAN и в STRATEGIC_SNAPSHOT.

---

## Шаг 3: Где что лежит (3 мин)

| Папка | Назначение |
|-------|------------|
| `config/` | Django: urls, settings, wsgi |
| `apps/` | core, accounts, courses, onboarding, knowledge_base, news, departments, analytics, notifications, search |
| `templates/` | base.html + шаблоны по приложениям |
| `static/css/` | input.css (Tailwind source), tailwind.css (собранный) |
| `design/` | DESIGN_SYSTEM.md, etalon/, reference/ — эталоны для верстки |
| `input/prompts/` | base.md, gamification.md и др. — промпты для AI |
| `input/hr docs/content/` | YAML/JSON контента для загрузки |
| `docs/` | вся документация |

**Читай:** [STRUCTURE_PLAN.md](STRUCTURE_PLAN.md) — подробнее.

---

## Шаг 4: Контекст и решения (5 мин)

**Читай:** [ANSWERS](ANSWERS) — ответы на GUIDING_QUESTIONS: аудитория, роли, MVP, хостинг, язык интерфейса и т.д.

**Важно:**
- Бренд — **Dim Kava** (не Atelier, не Barista Atelier)
- Layout — **top navbar** (без sidebar)
- Контент — в `input/hr docs/content/`, загрузка из YAML
- CSS — Tailwind v4, prebuild (не CDN), `.\tailwindcss.exe -i ./static/css/input.css -o ./static/css/tailwind.css --minify` после правок классов

---

## Шаг 5: Backlog и расширения (по желанию)

**Читай:** [FEATURES_BACKLOG.md](FEATURES_BACKLOG.md) — ачивки у аватара, комментарии с пре-модерацией, HR Task Stack.

**Читай:** [PROMPTS_MAPPING.md](PROMPTS_MAPPING.md) — связь промптов (base.md, gamification.md и т.д.) с фазами.

---

## Чеклист перед работой

- [ ] `python manage.py runserver` — проект поднимается
- [ ] `python manage.py test apps.core.tests` — тесты проходят
- [ ] Прочитан STRATEGIC_SNAPSHOT
- [ ] Прочитан DEVELOPMENT_PLAN (хотя бы фазы и следующий шаг)

---

## Если сломалось

1. Запустить тесты — упадёт на конкретной странице
2. `git status` / `git log -5` — что меняли
3. Проверить `templates/base.html`, `config/urls.py` — часто ломается там
4. CSS не применяется → пересобрать Tailwind, проверить `static/css/input.css` и `@source`

---

## Порядок чтения (сводка)

1. **[INDEX.md](INDEX.md)** — оглавление (если нужно найти документ)
2. **STRATEGIC_SNAPSHOT.md** — текущее состояние
3. **DEVELOPMENT_PLAN.md** — план, фазы, следующий шаг
4. **STRUCTURE_PLAN.md** — структура проекта
5. **ANSWERS** — контекст решений
6. **FEATURES_BACKLOG.md** — идеи на будущее

**Перед каждым шагом:** проверить [core-rules](../input/prompts/core-rules.md).
