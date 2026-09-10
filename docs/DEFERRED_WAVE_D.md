# Deferred product plans (Wave D)

These items are intentionally **not** implemented in the P0–C hardening pass.
Each should become its own scoped plan before coding.

| Topic | Why deferred | Suggested first slice |
|-------|--------------|----------------------|
| **KA i18n polish** | RU mostly done; many EN literals remain in accounts/onboarding/notifications | Wrap hardcoded strings + `makemessages -l ka` + smoke KA UI |
| **PostgreSQL FTS** | Current search is basic `icontains` ([apps/search/selectors.py](../apps/search/selectors.py)) | Add `SearchVector` on Article/Course titles when catalog > few hundred rows |
| **Celery** | Stub in requirements; notifications sync today | Only if email/CRM jobs need async; otherwise keep sync |
| **S3 media** | Local/media volumes work on self-hosted Windows | Only if we outgrow local disk on the prod host |
| **Invite-token signup** | Open product question in FEATURES_BACKLOG §3 | Token model + candidate register gate |
| **Anonymize unused candidates** | Privacy policy undecided | Admin action + retention days |
| **Manager / Director role** | Explicitly deferred in docs/ANSWERS | New group + read-only analytics |
| **Open-ended quiz + manual HR grade** | MVP is multiple-choice only | New lesson type + HR grading UI |
| **SSO / OAuth / dark theme / CRM-HRIS** | Explicitly out of near-term scope | Separate discovery |

**Out of scope permanently for this project path:** Railway cloud deploy. Runtime targets are **local (dev)** and **self-hosted prod** (`bigbook.dimkava.ge`) only.

## Do not start Wave D until

1. Wave A authz fix is deployed.
2. `verify-prod-flags.ps1` passes on the server.
3. HR Task Stack + comments used for at least one real moderation cycle.
