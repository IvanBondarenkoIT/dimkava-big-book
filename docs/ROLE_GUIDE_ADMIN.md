## Admin guide — что делать и где смотреть

### Основные задачи администратора
- **Доступы и безопасность**: кто может входить, кто HR, кто кандидат.
- **Стабильность**: миграции, зависимости, запуск в правильном окружении.
- **Админка**: удобство, базовые настройки, проверка прав.

---

### Важно: окружение (частая причина “упало”)
- Запускать проект из **`.venv`**, иначе может не быть зависимостей (например `markdown`).
- Базовые команды:
  - `python manage.py migrate`
  - `python manage.py check`
  - `python manage.py test`

---

### Дефолтные пользователи и демо-контент

Команда:
- `python manage.py create_default_users --update`

Что делает:
- создаёт/обновляет **admin/hr/employee/candidate** из `.env`
- **если контента нет** — автоматически выполняет:
  - `load_courses`
  - `load_onboarding`
  - `load_articles`
  - `load_news`
  - `load_departments`

Отключить автозагрузку контента:
- `python manage.py create_default_users --no-seed`

---

### Как обновлять и дополнять контент (операционный порядок)

Есть два режима:

1) **Админка (ручные изменения)** — делает HR
- Быстрые правки текста/порядка/флагов (`visible_for_candidates`), добавление вопросов в квизы.

2) **YAML-лоадеры (массовые обновления)** — обычно делает Admin/разработчик
- Рабочий порядок команд (когда надо переимпортировать набор контента):
  1. `python manage.py load_courses`
  2. `python manage.py load_onboarding`
  3. `python manage.py load_articles`
  4. `python manage.py load_news`
  5. `python manage.py load_departments` (зависит от курсов)

Рекомендация:
- Если HR правит контент в админке, а вы потом прогоняете YAML-лоадер — решите заранее, какой источник “истина”, чтобы не перетирать правки.

---

### Группы и роли (как сейчас устроено)
- Для удобства используются Django `Group`:
  - `hr_manager`
  - `employee`
  - `candidate`
  - `admin` (для дефолтного admin-пользователя)

Синхронизация:
- `UserProfile.user_type` управляет группами `candidate/employee` автоматически.

Важно:
- Группы — это *удобный маркер*. Ограничение контента для кандидатов реализовано через флаги `visible_for_candidates` в моделях + фильтрацию в селекторах/вьюхах.

---

### Где менять права/доступы
- `/admin/auth/group/` — группы и их права (если решите усилить RBAC)
- `/admin/accounts/userprofile/` — основной источник “кто кандидат/сотрудник”, dept/role, назначенная программа
- `/admin/accounts/assignmentrule/` — правила назначения онбординга/курсов (mock enrolment через slugs)

---

### Деплой/после pull (минимум)
1. `pip install -r requirements.txt` (в `.venv`)
2. `python manage.py migrate`
3. `python manage.py check`
4. `python manage.py test`
5. `python manage.py create_default_users --update`

