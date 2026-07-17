# Dim Kava — production status (self-hosted)

**Last updated:** 2026-07-17  
**Branch:** `deploy/self-hosted`  
**Status:** live (domain cutover to `bigbook.dimkava.ge` + HTTPS)

## Public access

| Item | Value |
|------|--------|
| URL | https://bigbook.dimkava.ge/ |
| Login | https://bigbook.dimkava.ge/login/ |
| DNS | `bigbook.dimkava.ge` → `178.63.72.227` |
| NAT | WAN `:80` → host `:80`, WAN `:443` → host `:443` |
| Legacy | `http://ge.domkofe.biz:777/` (optional during transition) |

## Server layout

| Path | Purpose |
|------|---------|
| `C:\dimkava\compose\` | `docker-compose.prod.yml`, `.env.prod`, `deploy/Caddyfile` |
| `C:\dimkava\scripts\` | Deploy/maintenance PowerShell scripts |
| `C:\dimkava\backups\` | DB dumps (`backup-db.ps1`) |
| `C:\Projects\dimkava-big-book\` | Git clone (pull + `copy-to-server.ps1`) |

## Stack

- **proxy:** Caddy HTTPS for `bigbook.dimkava.ge` (`PUBLIC_HTTP_PORT=80` + host `:443`)
- **web:** Django/Gunicorn (`dimkava-local:latest` or GHCR)
- **db:** PostgreSQL 15 (internal Docker network only)

## Key `.env.prod` (on server only)

```env
ALLOWED_HOSTS=bigbook.dimkava.ge,178.63.72.227,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://bigbook.dimkava.ge,http://localhost,http://127.0.0.1
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
PUBLIC_HTTP_PORT=80
AUTO_CREATE_DEFAULT_USERS=0
AUTO_LOAD_HR_CONTENT=0
```

After any `ALLOWED_HOSTS` / CSRF / Caddy change:

```powershell
cd C:\dimkava\compose
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --force-recreate web proxy
```

## Domain + HTTPS cutover (run on server)

```powershell
cd C:\Projects\dimkava-big-book
git pull
.\deploy\scripts\copy-to-server.ps1

# Optional: HTTP first (smoke), then HTTPS
# C:\dimkava\scripts\configure-bigbook-https.ps1 -HttpOnly

C:\dimkava\scripts\configure-bigbook-https.ps1
```

Prerequisites: DNS A record, NAT **80+443**, Windows firewall TCP 80/443.

## Routine operations

```powershell
# Update app image
C:\dimkava\scripts\update.ps1

# Backup DB
C:\dimkava\scripts\backup-db.ps1

# Re-apply HTTPS domain settings
C:\dimkava\scripts\configure-bigbook-https.ps1
```

## Done for this phase

- [x] Docker stack on Windows Server
- [x] Public HTTP on `ge.domkofe.biz:777` (legacy)
- [x] Domain `bigbook.dimkava.ge` + HTTPS (Caddy / Let's Encrypt)
- [x] `AUTO_CREATE_DEFAULT_USERS=0` after first login
- [x] Deploy scripts and docs in git (`deploy/self-hosted`)

## Content editing (production)

After the first YAML seed, set in `.env.prod`:

```env
AUTO_LOAD_HR_CONTENT=0
```

Then edit KB articles and courses in portal **Edit** or `/admin/` without restarts overwriting changes. See [WINDOWS_SERVER_DEPLOY.md](../../docs/WINDOWS_SERVER_DEPLOY.md) §13 and [SERVER_EDITORIAL_DEPLOY.md](../../docs/SERVER_EDITORIAL_DEPLOY.md).

## Later (optional)

- [ ] Merge `deploy/self-hosted` → `main`
- [ ] Remove legacy `ge.domkofe.biz:777` NAT if unused
- [ ] GHCR pull instead of `dimkava-local:latest`
- [ ] Strong unique passwords for all default accounts
- [ ] Scheduled `backup-db.ps1` (Task Scheduler)
- [ ] Disable Railway project

## Docs

- [WINDOWS_SERVER_DEPLOY.md](../../docs/WINDOWS_SERVER_DEPLOY.md)
- [PUBLIC_ACCESS_NAT.md](PUBLIC_ACCESS_NAT.md)
- [GITHUB_AND_DOCKER.md](../../docs/GITHUB_AND_DOCKER.md)
