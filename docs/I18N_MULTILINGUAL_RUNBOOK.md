# I18N MULTILINGUAL RUNBOOK (EN/KA/RU)

Обновлено: 2026-03-27  
Назначение: операционная инструкция по работе с трехъязычным UI и контентом.

## 1) Базовые правила
- Default язык: `en`.
- Дополнительные языки: `ka`, `ru`.
- UI язык выбирается через переключатель Language (вне navbar).
- Для контента используется fallback:
  1. текущий язык,
  2. `en`,
  3. legacy поле.

## 2) Как переключать язык
- В приложении используйте селектор `Language`.
- Переключение сохраняется через Django `set_language`.
- Для pre-login экрана (`/login/`) переключатель доступен в правом верхнем углу.

## 3) Поля контента в моделях
- Courses:
  - `title_en/title_ka/title_ru`
  - `description_en/description_ka/description_ru`
  - `Lesson.title_*`, `Lesson.content_*`
  - `TestQuestion.question_text_*`, `TestQuestion.options_*`
- Onboarding:
  - `OnboardingProgram.title_*`, `description_*`
  - `OnboardingModule.title_*`, `description_*`
  - `OnboardingStep.title_*`, `content_*`
- Knowledge Base:
  - `KBSection.title_*`
  - `Article.title_*`, `content_*`
- News:
  - `NewsPost.title_*`, `content_*`

## 4) Загрузка контента (seed/loaders)

Поддерживаются оба формата:
- старый:
  - `title`, `description`, `content`
- новый:
  - `title_en`, `title_ka`, `title_ru`
  - `description_en`, `description_ka`, `description_ru`
  - `content_en`, `content_ka`, `content_ru`

Команды:
- `python manage.py load_courses`
- `python manage.py load_onboarding`
- `python manage.py load_articles`
- `python manage.py load_news`

Автозаполнение черновиков переводов:
- `python manage.py load_courses --auto-translate-draft`
- аналогично для остальных loader-команд.

Важно:
- режим `--auto-translate-draft` создает черновые ka/ru значения;
- перед публикацией HR должен проверить и отредактировать переводы.

### 4.2) Заполнение грузинского в YAML через DeepL (рекомендуется для KA)

Требуется `DEEPL_AUTH_KEY` в `.env` (см. `.env.example`).

- Проверка объёма без ключа и без записи:  
  `python manage.py translate_seed_yaml_ka --dry-run`
- Запись переводов в файлы `input/hr docs/content/*.yaml`:  
  `python manage.py translate_seed_yaml_ka`  
  или выборочно: `--only onboarding|news|sops|courses`

После этого снова выполните команды `load_*` из п. 4.

Перевод в **БД** из уже загруженного EN (пустые или `[AUTO-ka]` поля):  
`python manage.py auto_translate_content --lang ka --apply`

## 4.1) Реальный автоперевод (DeepL)

Если нужно **получить настоящие переводы**, а не префиксы вида `[AUTO-ru]/[AUTO-ka]`, подключите DeepL.

### Настройка

В `.env` добавьте:
- `DEEPL_AUTH_KEY=...` (ключ DeepL)
- (опционально) `DEEPL_API_URL=https://api-free.deepl.com/v2/translate` (или pro endpoint)

### Запуск

Dry-run (без записи в БД):
- `python manage.py auto_translate_content --lang ru`
- `python manage.py auto_translate_content --lang ka`

Применить (запишет переводы в `*_ru/*_ka`, уберёт смысловую необходимость `[AUTO-*]`):
- `python manage.py auto_translate_content --lang ru --apply`
- `python manage.py auto_translate_content --lang ka --apply`

Важно:
- команда переводит из `*_en` и **заполняет только пустые или `[AUTO-..]` поля**;
- для качества перевода HR всё равно должен вычитать контент перед публикацией.

## 5) Редактирование в админке
- В админке у контентных моделей выделены группы полей:
  - English
  - Georgian
  - Russian
  - Legacy/Fallback
- Минимум для публикации: заполнить EN.
- Рекомендуемо: проверять ka/ru для пользовательских ролей, где язык уже используется.

## 6) Проверка после изменений
1. `python manage.py makemigrations --check --dry-run`
2. `python manage.py test apps.core.tests.I18nSmokeTests`
3. Переключить `en -> ka -> ru` и проверить:
   - navbar + login,
   - курсы/уроки/квизы,
   - onboarding,
   - knowledge base,
   - news.

## 7) Статус RU и дорожная карта KA

Итоги по русскому и пошаговый план грузинского (чеклисты, файлы, команды): см. **[I18N_RU_DONE_AND_KA_PLAN.md](I18N_RU_DONE_AND_KA_PLAN.md)**.
