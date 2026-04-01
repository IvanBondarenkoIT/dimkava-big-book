# Переводы: что сделано для RU и план для KA

Обновлено: 2026-04-01

## 1) Что зафиксировано для русского (RU)

### UI (статические строки)
- Шаблоны с `{% load i18n %}` и `{% trans %}` для ключевых экранов: база, курсы, онбординг, новости, логин, домашняя.
- Файл переводов: `locale/ru/LC_MESSAGES/django.po` (после правок нужен `compilemessages` → `django.mo`).
- Отдельно закрыты новости: заголовок списка, «Закреплено», «Назад к новостям», теги категорий через `pgettext('news_post_tag', …)` в `NewsPost.localized_tag`.

### Контент в БД (поля `*_ru` в seed + loaders)
- **Курсы:** `courses_seed.yaml` — поля `title_ru`, `description_ru`, контент уроков/квизов по мере заполнения.
- **Онбординг:** `onboarding_training_plan.yaml` — у модулей и **всех шагов** `title_ru` и `content_ru` (включая дни 2–3, недели 1–3, месяцы 1–3).
- **База знаний:** `sops_and_standards.yaml` — статьи с `title_ru` / `content_ru` (в т.ч. должностная инструкция менеджера-консультанта и уровни квалификации).
- **Новости:** `news_seed.yaml` — посты с `title_ru` / `content_ru` (в т.ч. `welcome-2026`).

### Команды после правки YAML
```bash
python manage.py load_courses
python manage.py load_onboarding
python manage.py load_articles
python manage.py load_news
```

### Проверка покрытия RU в YAML (онбординг)
```bash
python tools/fill_onboarding_kb_ru.py
```
Ожидаемо: `steps missing title_ru or content_ru: 0`.

### Тесты
- `python manage.py test apps.core.tests.I18nSmokeTests` (и другие тесты по проекту после изменений).

---

## 2) План перевода на грузинский (KA) — по шагам, без пропусков

### Этап A — интерфейс (`django.po`)
1. Открыть `locale/ka/LC_MESSAGES/django.po`.
2. Сверить с `locale/ru/LC_MESSAGES/django.po`: **каждый `msgid` из RU должен иметь пару в KA** (не оставлять пустой `msgstr` для пользовательских экранов).
3. Особое внимание: строки с `msgctxt` (например `news_post_tag`), onboarding, knowledge base, courses, news.
4. Выполнить `python manage.py compilemessages` (нужен gettext / `msgfmt`).
5. Проверить в браузере переключение `en → ka → ru` по чеклисту ниже.

### Этап B — контент в YAML (зеркало RU)
Для каждого источника добавить или вычитать **`title_ka` / `content_ka` / `description_ka`** там, где для RU уже есть полный набор:

| Источник | Файл | Порядок работ |
|----------|------|----------------|
| Курсы | `input/hr docs/content/courses_seed.yaml` | Модули → уроки → вопросы квиза |
| Онбординг | `input/hr docs/content/onboarding_training_plan.yaml` | Все модули и все шаги |
| База знаний | `input/hr docs/content/sops_and_standards.yaml` (и др. статьи) | Секции и статьи целиком |
| Новости | `input/hr docs/content/news_seed.yaml` | Каждый пост |

После каждого файла — соответствующая команда `load_*`.

### Этап C — автоматизация (опционально, затем вычитка)
- Черновики: `python manage.py load_<entity> --auto-translate-draft` (даёт префиксы `[AUTO-ka]`).
- Или DeepL: см. [I18N_MULTILINGUAL_RUNBOOK.md](I18N_MULTILINGUAL_RUNBOOK.md) раздел «Реальный автоперевод» — `auto_translate_content --lang ka --apply`, затем HR вычитывает.

### Этап D — контрольные списки
**UI (KA):** логин, главная, навигация, курсы (список/деталь/урок/квиз), онбординг (обзор + модуль), база знаний (раздел + статья), новости (список + деталь), профиль.

**Данные:** в админке выборочно открыть записи с языком **Georgian** и убедиться, что нет пустых полей там, где для EN/RU контент опубликован.

### Этап E — вспомогательный скрипт (рекомендуется)
Добавить аналог `tools/fill_onboarding_kb_ru.py` для полей `title_ka` / `content_ka` в `onboarding_training_plan.yaml` и при необходимости — отдельную проверку для KB YAML.

---

## 3) Порядок выполнения KA в репозитории

1. Завершить `django.po` для KA (Этап A).
2. Параллельно или следом: онбординг YAML → load_onboarding (большой объём).
3. База знаний YAML → load_articles.
4. Курсы → load_courses.
5. Новости → load_news.
6. Прогон тестов и ручной смоук на `ka`.

Этот документ — живой чеклист: отмечайте выполненные этапы в PR или в комментарии к задаче.
