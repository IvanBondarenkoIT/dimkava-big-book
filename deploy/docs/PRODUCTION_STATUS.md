# Dim Kava — production status (self-hosted)

**Last updated:** 2026-05-25  
**Branch:** `deploy/self-hosted`  
**Status:** live

## Public access

| Item | Value |
|------|--------|
| URL | http://ge.domkofe.biz:777/ |
| Login | http://ge.domkofe.biz:777/login/ |
| DNS | `ge.domkofe.biz` → `178.63.72.227` |
| NAT | WAN `:777` → host `:777` (variant B) |

## Server layout

| Path | Purpose |
|------|---------|
| `C:\dimkava\compose\` | `docker-compose.prod.yml`, `.env.prod`, `deploy/Caddyfile` |
| `C:\dimkava\scripts\` | Deploy/maintenance PowerShell scripts |
| `C:\dimkava\backups\` | DB dumps (`backup-db.ps1`) |
| `C:\Projects\dimkava-big-book\` | Git clone (pull + `copy-to-server.ps1`) |

## Stack

- **proxy:** Caddy (`PUBLIC_HTTP_PORT=777` → container `:80`)
- **web:** Django/Gunicorn (`dimkava-local:latest` or GHCR)
- **db:** PostgreSQL 15 (internal Docker network only)

## Key `.env.prod` (on server only)

```env
ALLOWED_HOSTS=ge.domkofe.biz,178.63.72.227,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://ge.domkofe.biz:777,http://localhost,http://127.0.0.1
SECURE_SSL_REDIRECT=false
PUBLIC_HTTP_PORT=777
AUTO_CREATE_DEFAULT_USERS=0
```

After any `ALLOWED_HOSTS` / CSRF change:

```powershell
cd C:\dimkava\compose
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --force-recreate web
```

## Routine operations

```powershell
# Update app image
C:\dimkava\scripts\update.ps1

# Backup DB
C:\dimkava\scripts\backup-db.ps1

# Re-apply public host settings
C:\dimkava\scripts\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -NatVariant B -PublicIp 178.63.72.227
```

## Done for this phase

- [x] Docker stack on Windows Server
- [x] Public HTTP on `ge.domkofe.biz:777`
- [x] `AUTO_CREATE_DEFAULT_USERS=0` after first login
- [x] Deploy scripts and docs in git (`deploy/self-hosted`)

## Content editing (production)

After the first YAML seed, set in `.env.prod`:

```env
AUTO_LOAD_HR_CONTENT=0
```

Then edit KB articles and courses in `/admin/` without restarts overwriting changes. See [WINDOWS_SERVER_DEPLOY.md](../../docs/WINDOWS_SERVER_DEPLOY.md) §13.

## Later (optional)

- [ ] Merge `deploy/self-hosted` → `main`
- [ ] HTTPS on `ge.domkofe.biz` (Caddy + Let's Encrypt, ports 80/443)
- [ ] GHCR pull instead of `dimkava-local:latest`
- [ ] Strong unique passwords for all default accounts
- [ ] Scheduled `backup-db.ps1` (Task Scheduler)
- [ ] Disable Railway project

## Docs

- [WINDOWS_SERVER_DEPLOY.md](../../docs/WINDOWS_SERVER_DEPLOY.md)
- [PUBLIC_ACCESS_NAT.md](PUBLIC_ACCESS_NAT.md)
- [GITHUB_AND_DOCKER.md](../../docs/GITHUB_AND_DOCKER.md)
