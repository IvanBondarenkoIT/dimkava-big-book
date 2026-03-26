## Admin guide — эксплуатация, доступы и стабильность

### Зона ответственности Admin
- Поддержка рабочего окружения и зависимостей.
- Миграции и целостность данных.
- Роли/доступы (HR, employee, candidate, admin).
- Безопасность: `.env`, секреты, контроль инцидентов.

---

### Быстрый старт после pull
1. Активировать `.venv`.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py check`
5. `python manage.py test`
6. `python manage.py create_default_users --update`

---

### Дефолтные пользователи и seed
Команда:
- `python manage.py create_default_users --update`

Эффект:
- создаёт/обновляет `admin/hr/employee/candidate` из `.env`;
- если контент пустой, автозапускает:
  - `load_courses`
  - `load_onboarding`
  - `load_articles`
  - `load_news`
  - `load_departments`

Отключить автосидинг:
- `python manage.py create_default_users --no-seed`

---

### Критичные `.env` переменные (минимум)
- `SECRET_KEY`
- `DEFAULT_ADMIN_EMAIL`, `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_HR_EMAIL`, `DEFAULT_HR_PASSWORD`
- `DEFAULT_EMPLOYEE_EMAIL`, `DEFAULT_EMPLOYEE_PASSWORD`
- `DEFAULT_CANDIDATE_EMAIL`, `DEFAULT_CANDIDATE_PASSWORD`, `DEFAULT_CANDIDATE_PHONE`
- `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`

---

### Права и группы
Основные группы:
- `hr_manager`
- `employee`
- `candidate`
- `admin`

Ключевые моменты:
- HR должен быть `is_staff=True`, иначе не войдёт в админку.
- Тип профиля (`UserProfile.user_type`) синхронизирует роли candidate/employee.
- Для HR используются явные model-права на управление профильными сущностями.

---

### Где админу управлять системой
- Пользователи/профили: `/admin/auth/user/`, `/admin/accounts/userprofile/`
- Assignment rules: `/admin/accounts/assignmentrule/`
- Контент: `courses`, `onboarding`, `knowledge_base`, `news`
- Модерация:
  - комментарии: `/admin/comments/comment/`
  - onboarding feedback: `/admin/onboarding/onboardingfeedback/`

---

### Операционный режим контента
Есть 2 режима:
1. Ручные правки в админке (обычно HR).
2. Массовый импорт YAML-командами (обычно Admin/Dev).

Если совмещаете оба режима:
- заранее фиксируйте “источник истины”,
- иначе YAML может перетереть ручные правки.

---

### Инциденты и диагностика (минимальный протокол)
1. `python manage.py check`
2. `python manage.py showmigrations`
3. `python manage.py test`
4. Проверить `.env` и доступность зависимостей в `.venv`
5. При проблемах ролей: переприменить `create_default_users --update`

---

### Чеклист Admin (еженедельно)
- Проверить, что HR заходит в `/admin/` и `/analytics/hr/`.
- Проверить, что кандидат может открыть только допустимые разделы.
- Проверить pending-очереди модерации (comments/feedback).
- Проверить отсутствие секретов в коде и корректность `.env`.

