# Public access: domains, ports, NAT

Production URL: **https://bigbook.dimkava.ge/**

Dim Kava Caddy listens on **container port 80** (and obtains TLS on **443** when the site block is a hostname). Compose maps:

- `${PUBLIC_HTTP_PORT:-80}:80`
- `443:443`

## Current production (standard 80/443)

| Hop | Port |
|-----|------|
| Internet HTTP | **80** |
| Internet HTTPS | **443** |
| Firewall/NAT → server | **80** and **443** |
| Docker `proxy` | `80:80`, `443:443` (`PUBLIC_HTTP_PORT=80`) |

```powershell
C:\dimkava\scripts\configure-bigbook-https.ps1
```

Django:

```env
ALLOWED_HOSTS=bigbook.dimkava.ge,...
CSRF_TRUSTED_ORIGINS=https://bigbook.dimkava.ge,...
SECURE_SSL_REDIRECT=true
PUBLIC_HTTP_PORT=80
```

## Legacy: ge.domkofe.biz:777

### Variant A (WAN 777 → host 80)

| Hop | Port |
|-----|------|
| Internet | **777** |
| NAT → host | **80** |
| Docker `proxy` | `80:80` |

CSRF must include `http://ge.domkofe.biz:777` (browser Origin uses port 777).

### Variant B (WAN 777 → host 777)

| Hop | Port |
|-----|------|
| Internet | **777** |
| NAT → host | **777** |
| Docker `proxy` | `777:80` via `PUBLIC_HTTP_PORT=777` |

```powershell
.\deploy\scripts\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -NatVariant B
.\deploy\scripts\verify-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777
```

## Do not expose

- PostgreSQL **5432** to the internet.
