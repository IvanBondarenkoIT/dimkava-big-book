# GitHub и Docker: что где происходит

Краткий гид перед первым деплоем. Пошаговый runbook: [WINDOWS_SERVER_DEPLOY.md](WINDOWS_SERVER_DEPLOY.md).

## Коротко

| | GitHub | Docker на вашем ПК |
|---|--------|-------------------|
| Роль | **Собирает** образ сайта (фабрика) | **Скачивает** образ и **запускает** (склад + старт) |
| Где работает | Облако GitHub (Actions) | Ваш компьютер / сервер |
| Нужен запущенный Docker? | Нет | Да (**Engine running**) |

Код в репозитории ≠ работающий сайт, пока образ не собран (GitHub) и не запущен (`docker compose up`).

---

## Схема

```
GitHub (push) → Actions «Docker publish» → GHCR (образ)
                                              ↓ docker pull
Ваш ПК: docker compose → Caddy :80 → Django → PostgreSQL
Браузер → http://localhost/
```

Образ после успешной сборки:

`ghcr.io/ivanbondarenkoit/dimkava-big-book:latest`

---

## GitHub — что смотреть

| Страница | URL (подставьте свой репозиторий) |
|----------|-----------------------------------|
| Actions | `https://github.com/IvanBondarenkoIT/dimkava-big-book/actions` |
| Workflow | Actions → **Docker publish (GHCR)** |
| Packages (образ) | `https://github.com/IvanBondarenkoIT/dimkava-big-book/pkgs/container/dimkava-big-book` |
| PR Checks | Pull Request → вкладка **Checks** |

**Зелёный Docker publish** = образ можно тянуть на ПК.  
**Красный** = сначала чиним CI (лог шага **Build and push**), локальный деплой бессмысленен.

**GitGuardian** = проверка, что в код не попали пароли. Ветка `deploy/self-hosted`, коммит `db052aa` — без `.env.prod.example` в git.

---

## Docker на ПК — что нужно

| Элемент | Путь / команда |
|---------|----------------|
| Docker Desktop | Engine **running** (не stopped) |
| Файлы compose | `C:\dimkava\compose\` |
| Секреты | `C:\dimkava\compose\.env.prod` (не в git) |
| Создать env | `C:\dimkava\scripts\new-env-prod.ps1` |
| Первый запуск | `C:\dimkava\scripts\first-deploy.ps1` |

Проверка окружения одной командой:

```powershell
.\deploy\scripts\verify-setup.ps1
```

---

## Порядок действий (чеклист)

- [ ] **1. GitHub:** Actions → последний run **Docker publish** — зелёный
- [ ] **2. Docker Desktop:** внизу **Engine running**
- [ ] **3. PowerShell:** `docker version` — без ошибки
- [ ] **4.** `.\deploy\scripts\copy-to-server.ps1`
- [ ] **5.** `C:\dimkava\scripts\new-env-prod.ps1` → заполнить `.env.prod`
- [ ] **6.** `docker login ghcr.io` (PAT с `read:packages`)
- [ ] **7.** `C:\dimkava\scripts\first-deploy.ps1`
- [ ] **8.** Браузер: **http://localhost/**
- [ ] **9.** `C:\dimkava\scripts\post-first-login.ps1`

---

## Что прислать в поддержку / AI (если застряли)

1. PR → **Checks** (Docker publish + GitGuardian)
2. Actions → упавший job → лог **Build and push** (последние строки)
3. Docker Desktop — **Engine running** или stopped
4. Вывод `.\deploy\scripts\verify-setup.ps1`

**Не присылайте:** `.env.prod`, токены, пароли.

---

## Частые вопросы

**Установил Docker — сайт уже работает?**  
Нет. Нужны: running Engine + образ в GHCR + `compose up`.

**PR красный — можно деплоить?**  
Лучше дождаться зелёного Docker publish.

**Actions зелёный, но Engine stopped**  
Сборка в облаке прошла; локально запустите Docker Desktop.

**Где полная инструкция?**  
[WINDOWS_SERVER_DEPLOY.md](WINDOWS_SERVER_DEPLOY.md)
