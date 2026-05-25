# Деплой на Windows Server (Docker Desktop)

Production-стек: **Caddy** (reverse proxy) → **Django/Gunicorn** → **PostgreSQL**. Образ приложения публикуется в **GHCR** через GitHub Actions; сервер только делает `docker pull`.

**Сначала непонятно GitHub vs Docker?** → [GITHUB_AND_DOCKER.md](GITHUB_AND_DOCKER.md).  
Проверка на машине: `.\deploy\scripts\verify-setup.ps1`

См. также: [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) (старая схема), [I18N_MULTILINGUAL_RUNBOOK.md](I18N_MULTILINGUAL_RUNBOOK.md).

### Текущий прод (зафиксировано)

| Параметр | Значение |
|----------|----------|
| URL | `http://ge.domkofe.biz:777/` |
| Файл env | **`C:\dimkava\compose\.env.prod`** (с точкой; не `env.prod`) |
| `PUBLIC_HTTP_PORT` | `777` (NAT WAN `:777` → host `:777`) |
| После правки `ALLOWED_HOSTS` | `docker compose ... up -d --force-recreate web` |

---

## 1. Требования к серверу

| Параметр | Минимум | Рекомендуется |
|----------|---------|---------------|
| ОС | Windows Server 2019+ или Windows 10/11 | Windows Server 2022 |
| RAM | 4 GB для Docker | 8 GB |
| Docker | Docker Desktop + WSL2 backend | Автозапуск при старте Windows |
| Диск | 20 GB свободно | SSD, отдельный том `C:\dimkava` |
| Сеть | 80/443 (и SSH 22 для CI deploy) | Статический IP или DNS |

Проверка:

```powershell
docker version
docker compose version
```

---

## 2. Структура на сервере

```
C:\dimkava\
├── compose\
│   ├── docker-compose.prod.yml
│   ├── .env.prod                 # секреты (не в git)
│   └── deploy\
│       └── Caddyfile             # или Caddyfile из репозитория
├── backups\                      # pg_dump (скрипт backup-db.ps1)
└── scripts\                      # копии deploy\scripts\*.ps1
```

Скопируйте из репозитория (ветка `deploy/self-hosted` или `main` после merge):

- `docker-compose.prod.yml`
- `deploy/Caddyfile` (LAN) или `deploy/Caddyfile.https.example` → `deploy/Caddyfile`
- `deploy/scripts/*.ps1` → `C:\dimkava\scripts\`

`.env.prod` создаётся на сервере скриптом `new-env-prod.ps1` (не в git).

---

## 3. Подготовка Windows

### 3.1 Docker Desktop

1. Установить [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Settings → General → **Start Docker Desktop when you log in**.
3. Settings → Resources → выделить ≥ 4 GB RAM.

### 3.2 Firewall

```powershell
New-NetFirewallRule -DisplayName "DimKava HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "DimKava HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

PostgreSQL **не** открывать наружу (в `docker-compose.prod.yml` порт 5432 не проброшен).

### 3.3 OpenSSH (для GitHub Actions deploy)

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

Опционально — shell по умолчанию PowerShell (для deploy workflow):

```powershell
New-Item -Force -Path "HKLM:\SOFTWARE\OpenSSH"
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
Restart-Service sshd
```

---

## 4. Настройка `.env.prod`

```powershell
C:\dimkava\scripts\new-env-prod.ps1
notepad C:\dimkava\compose\.env.prod
```

| Переменная | Назначение |
|------------|------------|
| `POSTGRES_PASSWORD` | Пароль БД (обязательно) |
| `SECRET_KEY` | Django secret |
| `DIMKAVA_IMAGE` | `ghcr.io/ivanbondarenkoit/dimkava-big-book:latest` |
| `DEFAULT_ADMIN_PASSWORD` | Пароль первого входа |
| `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` | `localhost,127.0.0.1` и `http://localhost,...` для теста |
| `PUBLIC_HTTP_PORT` | `80` (LAN); `777` если WAN `:777` → host `:777` (см. § публичный IP) |
| `DATABASE_SSL_REQUIRE` | `false` |

`DATABASE_URL` собирается в контейнере из `POSTGRES_*` (`docker-entrypoint.sh`).

**После входа admin:** `post-first-login.ps1` или `AUTO_CREATE_DEFAULT_USERS=0`.

### Режим LAN (HTTP)

- `deploy/Caddyfile` — блок `:80` (по умолчанию в репозитории).
- `SECURE_SSL_REDIRECT=false`, `CSRF_TRUSTED_ORIGINS=http://192.168.x.x`

### Режим публичный домен + порт (HTTP, `ge.domkofe.biz:777`)

DNS **ge.domkofe.biz** → IP сервера (тот же, что `178.63.72.227`). Порт **777** как у health на `:8010`.

1. Скопировать файлы: `copy-to-server.ps1`.
2. На сервере (PowerShell **от администратора** для firewall):

```powershell
C:\dimkava\scripts\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -NatVariant B
C:\dimkava\scripts\verify-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -HostPort 777
```

Опционально оставить доступ по IP: `-PublicIp 178.63.72.227`.

**NAT:** вариант **B** — WAN `:777` → сервер `:777`. Подробно: [`deploy/docs/PUBLIC_ACCESS_NAT.md`](../deploy/docs/PUBLIC_ACCESS_NAT.md).

Минимум в `.env.prod` (скрипт выставляет сам):

```env
ALLOWED_HOSTS=ge.domkofe.biz,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://ge.domkofe.biz:777,http://localhost,http://127.0.0.1
SECURE_SSL_REDIRECT=false
SESSION_COOKIE_SECURE=false
CSRF_COOKIE_SECURE=false
PUBLIC_HTTP_PORT=777
```

Открыть: `http://ge.domkofe.biz:777/login/`.

| Симптом | Действие |
|---------|----------|
| Таймаут снаружи, локально OK | Переключить `-NatVariant A` / `B`, проверить проброс у админа |
| 400 DisallowedHost | IP в `ALLOWED_HOSTS`, `docker compose up -d web` |
| 403 CSRF | `http://IP:777` в `CSRF_TRUSTED_ORIGINS` |
| Редирект по кругу | `SECURE_SSL_REDIRECT=false` |

### Режим публичный домен (HTTPS)

1. DNS A-запись → IP сервера; порты 80/443 доступны из интернета.
2. Скопировать `deploy/Caddyfile.https.example` → `deploy/Caddyfile`, подставить домен.
3. В `.env.prod`:
   - `ALLOWED_HOSTS=portal.example.com`
   - `CSRF_TRUSTED_ORIGINS=https://portal.example.com`
   - `SECURE_SSL_REDIRECT=true`
   - `SESSION_COOKIE_SECURE=true`
   - `CSRF_COOKIE_SECURE=true`

---

## 5. GitHub: сборка образа (GHCR)

Workflow: `.github/workflows/docker-publish.yml`

- Триггер: push в `main` или `deploy/self-hosted`
- Образ: `ghcr.io/<owner>/dimkava-big-book:latest` (+ тег SHA)

**Права:** Settings → Actions → General → Workflow permissions → **Read and write**.

**Приватный репозиторий:** на сервере `docker login ghcr.io` с PAT (`read:packages`).

---

## 6. GitHub: автодеплой на сервер

Workflow: `.github/workflows/deploy-self-hosted.yml`

Секреты репозитория (Settings → Secrets):

| Secret | Описание |
|--------|----------|
| `DEPLOY_HOST` | IP или hostname сервера |
| `DEPLOY_USER` | Пользователь Windows с правом Docker |
| `DEPLOY_SSH_KEY` | Приватный ключ SSH |
| `DEPLOY_SSH_PORT` | `22` (опционально) |
| `DEPLOY_COMPOSE_DIR` | `C:\dimkava\compose` (опционально) |
| `GHCR_USERNAME` | GitHub username |
| `GHCR_TOKEN` | PAT с `read:packages` |

После успешной сборки образа workflow выполняет `pull` + `up -d` на сервере.

Ручное обновление: `deploy\scripts\update.ps1`.

---

## 7. Первый деплой

```powershell
# На сервере
mkdir C:\dimkava\compose, C:\dimkava\backups, C:\dimkava\scripts -Force
# Скопировать файлы из git (см. §2)

cd C:\dimkava\compose
C:\dimkava\scripts\new-env-prod.ps1
notepad .env.prod

docker login ghcr.io
C:\dimkava\scripts\first-deploy.ps1
```

Или из репозитория:

```powershell
.\deploy\scripts\first-deploy.ps1 -ComposeDir C:\dimkava\compose
```

Проверка:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs web --tail 100
```

Откройте `http://<IP>/` → вход `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD`.

---

## 8. После первого входа (чеклист)

- [ ] Сменить пароль admin в интерфейсе (не оставлять `DEFAULT_ADMIN_PASSWORD`)
- [ ] `C:\dimkava\scripts\post-first-login.ps1` или `AUTO_CREATE_DEFAULT_USERS=0` в `.env.prod`
- [ ] `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d web`
- [ ] Настроить Task Scheduler для `backup-db.ps1` (ежедневно)
- [ ] Отключить проект на Railway (экономия)

---

## 9. Бэкапы

```powershell
C:\dimkava\scripts\backup-db.ps1
```

Файлы: `C:\dimkava\backups\dimkava-YYYYMMDD-HHMMSS.sql`

Восстановление:

```powershell
Get-Content C:\dimkava\backups\dimkava-....sql | docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db psql -U dimkava dimkava
```

---

## 10. Устранение неполадок

| Симптом | Решение |
|---------|---------|
| `web` не стартует, ошибка SSL к БД | `DATABASE_SSL_REQUIRE=false` |
| Redirect loop | LAN: `SECURE_SSL_REDIRECT=false`; HTTPS: проверить Caddy и `CSRF_TRUSTED_ORIGINS` |
| 400 Bad Request (DisallowedHost) | IP в `ALLOWED_HOSTS` в **`.env.prod`**, затем `--force-recreate web`; проверить `docker exec ... printenv ALLOWED_HOSTS` |
| 403 CSRF | Добавить `http://IP:777` в `CSRF_TRUSTED_ORIGINS` |
| Снаружи `:777` не открывается | `configure-public-access.ps1`, NAT A/B, `verify-public-access.ps1` |
| Нет образа | `docker login ghcr.io`, проверить `DIMKAVA_IMAGE` |
| Caddy нет сертификата | DNS, порты 80/443, домен в Caddyfile |

Логи:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f web
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f proxy
```

---

## 11. Что происходит при старте контейнера `web`

См. [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md): `migrate` → опционально `AUTO_LOAD_HR_CONTENT` → `AUTO_CREATE_DEFAULT_USERS` → `collectstatic` → Gunicorn.

Медиафайлы хранятся в volume `media_data` (не теряются при пересоздании контейнера).
