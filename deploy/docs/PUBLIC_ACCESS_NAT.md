# Public access: port 777 and NAT (for server admin)

Dim Kava Caddy listens on **container port 80**. From the internet users open:

`http://ge.domkofe.biz:777/` (public hostname and WAN port).

## Variant A (preferred if possible)

| Hop | Port |
|-----|------|
| Internet | **777** |
| Firewall/NAT → server LAN IP | **80** |
| Docker `proxy` | `80:80` (default) |

- On server: `PUBLIC_HTTP_PORT=80` (or omit) in `.env.prod`.
- Windows firewall: allow inbound **TCP 80**.
- Django `CSRF_TRUSTED_ORIGINS` must include `http://ge.domkofe.biz:777` (browser uses port 777).

## Variant B (WAN 777 → host 777)

| Hop | Port |
|-----|------|
| Internet | **777** |
| Firewall/NAT → server LAN IP | **777** |
| Docker `proxy` | `777:80` via `PUBLIC_HTTP_PORT=777` |

- On server: `PUBLIC_HTTP_PORT=777` in `.env.prod`.
- Windows firewall: allow inbound **TCP 777**.

## Quick setup on server

```powershell
cd C:\Projects\dimkava-big-book
.\deploy\scripts\copy-to-server.ps1
.\deploy\scripts\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -NatVariant B
.\deploy\scripts\verify-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777
```

If unsure which variant is active, try **B** first (matches `8010`-style external port mapping), then **A** if port 777 on the host is not listening.

## Do not expose

- PostgreSQL **5432** to the internet.
