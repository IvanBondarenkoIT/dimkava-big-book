# ROLE GUIDE — ADMIN

Обновлено: 2026-03-26  
Назначение: инструкция по поддержке системы, доступов и стабильной эксплуатации.

## 1) Ответственность администратора
- Поддержка окружения и зависимостей.
- Миграции и консистентность схемы/данных.
- Управление ролями и правами.
- Безопасность конфигурации и инцидент-реакция.

## 2) Базовый запуск после обновления
1. Активировать `.venv`.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py check`
5. `python manage.py test`
6. `python manage.py create_default_users --update`

## 3) Дефолтные пользователи и seed
Основная команда:
- `python manage.py create_default_users --update`

Что делает:
- создает/обновляет `admin`, `hr`, `employee`, `candidate` из `.env`;
- при пустом контенте может запускать автозаполнение.

Отключение автосидинга:
- `python manage.py create_default_users --no-seed`

## 4) Ключевые переменные `.env`
- `SECRET_KEY`
- `DEFAULT_ADMIN_EMAIL`, `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_HR_EMAIL`, `DEFAULT_HR_PASSWORD`
- `DEFAULT_EMPLOYEE_EMAIL`, `DEFAULT_EMPLOYEE_PASSWORD`
- `DEFAULT_CANDIDATE_EMAIL`, `DEFAULT_CANDIDATE_PASSWORD`, `DEFAULT_CANDIDATE_PHONE`
- `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`

## 5) Роли и права
- Группы: `admin`, `hr_manager`, `employee`, `candidate`.
- Для HR обязателен `is_staff=True` (доступ к `/admin/`).
- `UserProfile.user_type` должен соответствовать бизнес-роли.

## 6) Где управлять системой
- Пользователи/профили: `/admin/auth/user/`, `/admin/accounts/userprofile/`
- Контент: разделы `courses`, `onboarding`, `knowledge_base`, `news`
- Модерация: `/admin/comments/comment/`, `/admin/onboarding/onboardingfeedback/`
- Назначения/правила: `/admin/accounts/assignmentrule/`

## 7) Инциденты: минимальный протокол
1. `python manage.py check`
2. `python manage.py showmigrations`
3. `python manage.py test`
4. Проверить актуальность `.env` и секретов.
5. Если проблема ролей: повторить `create_default_users --update`.

## 8) Недельный контроль
- Проверить доступ HR к `/analytics/hr/` и `/admin/`.
- Проверить ограничения кандидата (доступ только к разрешенным зонам).
- Проверить очереди модерации.
- Проверить статус миграций и отсутствие дрейфа схемы.

## 9) Скриншоты для этой инструкции
- `SHOT-A1`: admin users/profiles.
![SHOT-A1 admin home](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-8fdae264-954a-4553-852e-be3d97298651.png)
- `SHOT-A2`: admin `UserProgress` с lock/attempts.
![SHOT-A2 admin userprogress](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-51a9bcad-b4bc-43dc-bddf-9f5be6ce02fb.png)
- `SHOT-A3`: admin comments/onboarding feedback moderation.
![SHOT-A3 hr comments moderation](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-83c4adbd-f817-4666-8b3b-b582eb0d759c.png)

