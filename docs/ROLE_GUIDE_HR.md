# ROLE GUIDE — HR

Обновлено: 2026-03-26  
Назначение: операционная инструкция HR по управлению кандидатами, контентом и модерацией.

## 1) Основные зоны HR
- HR Hub: `/analytics/hr/` — ежедневная рабочая панель.
- Django Admin: `/admin/` — точечные расширенные операции.

## 2) Ежедневный цикл HR
1. Проверить новых кандидатов в `/analytics/hr/candidates/`.
2. Проверить очереди модерации (`comments`, `onboarding feedback`).
3. Проверить видимость нового контента для кандидатов.
4. Обновить статусы готовых кандидатов (включая conversion).

## 3) Работа с кандидатами
В `Candidates`:
- контролируйте телефон, статус верификации, прогресс;
- отмечайте "verified" при необходимости;
- переводите в сотрудники через `convert to employee`, когда кандидат готов.

Перед конвертацией:
- онбординг пройден;
- ключевые курсы доступны и пройдены;
- базовые атрибуты профиля заполнены.

## 4) Квизы кандидатов: политика retake
- Кандидат отправляет квиз 1 раз.
- После отправки повторная попытка блокируется автоматически.
- HR принимает решение о повторной попытке.
- Разблокировка retake выполняется через HR-доступ в админ-панели `UserProgress`.

## 5) Visibility и контент
Контролируйте флаги:
- `OnboardingProgram.visible_for_candidates`
- `Course.visible_for_candidates`
- `Lesson.visible_for_candidates`

Проверка перед запуском кандидата в обучение:
- нужная программа видна;
- курс и уроки видны;
- под кандидатом открываются `/onboarding/` и `/courses/`.

## 6) Модерация контента
- `Comments`: публикуются только после approve.
- `Onboarding feedback`: видно пользователям только после approve.
- Отклоненные материалы в публичные блоки не попадают.

Рекомендация: проверять pending-очереди минимум 1 раз в рабочий день.

## 7) ILP
- Создается и поддерживается HR через админ-панель.
- Сотрудник видит ILP в профиле и выполняет по шагам.
- HR пересматривает дедлайны и приоритеты по факту прогресса.

## 8) Скриншоты для этой инструкции
- `SHOT-H1`: HR Hub overview `/analytics/hr/`.
![SHOT-H1 hr hub](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-fdfa1eac-25e2-4235-b80f-b42abbc60f26.png)
- `SHOT-H2`: candidates `/analytics/hr/candidates/`.
![SHOT-H2 candidates](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-686be263-b362-434c-b5a8-02e5512457f2.png)
- `SHOT-H3`: visibility `/analytics/hr/visibility/`.
![SHOT-H3 visibility](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-96fd2037-dc0b-41f2-8fa4-2a005bed4485.png)
- `SHOT-H4`: comments moderation `/analytics/hr/comments/`.
![SHOT-H4 comments moderation](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-83c4adbd-f817-4666-8b3b-b582eb0d759c.png)
- `SHOT-H5`: onboarding feedback moderation `/analytics/hr/onboarding-feedback/`.
![SHOT-H5 onboarding feedback moderation](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-6ece1345-edaf-420a-9864-1023a935bc6b.png)
- `SHOT-H6`: content review `/analytics/content-review/`.
![SHOT-H6 content review](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-592436e9-2c0e-4e4a-8771-6339bc26a2e2.png)
- `SHOT-H7`: admin `UserProgress` (lock/attempts + unlock action).
![SHOT-H7 admin userprogress](C:/Users/Computer/.cursor/projects/d-CursorProjects-dimkava-big-book/assets/c__Users_Computer_AppData_Roaming_Cursor_User_workspaceStorage_bbc6fcab8e4ff239132c403c3d74202b_images_image-51a9bcad-b4bc-43dc-bddf-9f5be6ce02fb.png)

