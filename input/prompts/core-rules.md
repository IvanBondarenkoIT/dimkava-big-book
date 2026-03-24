# Core Development Rules — Code Quality & Standards

> **Apply this throughout the entire project.** These rules govern how all code is written, structured, and reviewed. They override default Cursor/AI code generation habits where they conflict.

---

## 1. Project Setup Rules

### Environment Variables

- **Never hardcode secrets.** All credentials, keys, and environment-specific values must come from environment variables.
- Use `python-decouple` or `django-environ` to read `.env` files.
- Always keep `.env.example` up to date — every variable in `.env` must have a commented example entry.
- Never commit `.env` to version control. Verify `.gitignore` includes it.

```python
# config/settings/base.py — correct pattern
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE_URL = config('DATABASE_URL')
```

### Settings Split

```
config/settings/
├── base.py          # Shared settings (installed apps, middleware, auth, i18n)
├── development.py   # DEBUG=True, console email, local DB
└── production.py    # Secure cookies, HTTPS, Railway-compatible settings
```

Always run with `DJANGO_SETTINGS_MODULE=config.settings.development` in dev.

---

## 2. Git Workflow Rules

### Every Step = One Commit

After completing each implementation step, commit before moving to the next. No exceptions.

**Commit flow (run in this exact order every time):**

```bash
# Step 1 — Check what's changed
git status
git diff

# Step 2 — Run the safety scan BEFORE staging anything (see section below)
git diff --staged  # if anything is already staged, check it first

# Step 3 — Stage and commit
git add .
git commit -m "feat(courses): add quiz result saving and score display"

# Step 4 — Push
git push
```

### Pre-Commit Safety Scan

**Before every `git commit`, scan for secrets.** Run this command:

```bash
# Quick manual scan — look for these patterns in staged files:
git diff --cached | grep -iE "(secret|password|token|api_key|private_key|DATABASE_URL\s*=\s*postgres)"
```

If any matches appear — **stop, do not commit.** Move the value to `.env` and reference it via `config('VAR_NAME')`.

**For automated scanning, install `detect-secrets`:**

```bash
pip install detect-secrets
detect-secrets scan > .secrets.baseline   # Run once to create baseline
detect-secrets audit .secrets.baseline    # Review flagged items

# Add to pre-commit hook (.git/hooks/pre-commit):
detect-secrets-hook --baseline .secrets.baseline
```

**Common secrets that get accidentally committed:**
- `SECRET_KEY = 'django-insecure-...'` hardcoded in settings
- Database URLs with credentials: `postgres://user:password@host/db`
- Any API keys, tokens, passwords in any file
- `.env` file itself

### Commit Message Format

```
feat(courses): add quiz result saving and score display
fix(auth): redirect to login on session timeout
refactor(gamification): extract level calculation to services
test(gamification): add unit tests for award_points service
docs(readme): update local setup instructions
chore(deps): pin Django to 4.2.x in requirements.txt
```

Prefixes: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `chore`.

One logical change per commit. Do not mix model changes with UI changes in a single commit.

### .gitignore — Required Entries

Make sure these are always in `.gitignore`:

```
.env
*.env
.env.*
!.env.example
__pycache__/
*.pyc
*.pyo
.DS_Store
media/
staticfiles/
.secrets.baseline
db.sqlite3
node_modules/
```

---

## 3. Step Checkpoint Protocol

After completing each major implementation step, **stop and write a checkpoint summary** before continuing. This is mandatory — it keeps context clear for both the developer and the AI assistant.

### Format

```
## ✅ CHECKPOINT — Step N complete

### What was done:
- [List of files created or modified]
- [Key decisions made]
- [Any deviations from the plan and why]

### Current state:
- [What works right now]
- [Known issues or TODOs left for later]

### Next step:
- [Exact name of the next step]
- [Files that will be created/changed]
- [Any dependencies or blockers to be aware of]
```

### Example

```
## ✅ CHECKPOINT — Step 2 complete: Onboarding module

### What was done:
- Created apps/onboarding/models.py with OnboardingModule and OnboardingProgress
- Created apps/onboarding/views.py with OnboardingOverviewView and ModuleDetailView
- Created apps/onboarding/services.py with mark_step_complete()
- Added templates/onboarding/overview.html and module_detail.html
- Wired URLs in apps/onboarding/urls.py and included in config/urls.py
- Emits onboarding_module_completed signal (gamification will hook into this later)

### Current state:
- Onboarding pages render correctly for logged-in users
- Progress is saved to DB on step completion
- Mentor block is a placeholder (Mentor model not yet created)
- Gamification signals are emitted but not yet consumed

### Next step:
- Step 3: Course catalog and lesson pages
- Files: apps/courses/models.py, views.py, services.py, templates/courses/
- Dependency: UserProgress model must reference Lesson (defined in this step)
```

Write this checkpoint as a comment in the chat. If working with an AI assistant (Cursor), paste it at the start of the next conversation session to restore context.

---

## 4. Django-Specific Rules

### URL Naming

Every URL must have a `name`:

```python
# ✅ correct
path('courses/<slug:slug>/', CourseDetailView.as_view(), name='course_detail')

# ❌ wrong — unnamed URL
path('courses/<slug:slug>/', CourseDetailView.as_view())
```

Always use `{% url 'app_name:view_name' %}` in templates, never hardcode paths.

### Views

- Prefer **Class-Based Views (CBVs)** for standard CRUD.
- Use `LoginRequiredMixin` on every view that requires auth — no exceptions.
- Use `UserPassesTestMixin` for role checks.
- Never put business logic or DB queries directly in views. Call service functions and selectors.

```python
# ✅ correct
class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_progress'] = get_course_progress(self.request.user, self.object)
        return context

# ❌ wrong — ORM query inside the view
class CourseDetailView(LoginRequiredMixin, DetailView):
    def get_context_data(self, **kwargs):
        context['progress'] = UserProgress.objects.filter(user=self.request.user, ...).all()
        return context
```

### Models

- Always define `__str__()` on every model.
- Always define `Meta.ordering` where the order matters.
- Use `db_index=True` on fields that are frequently filtered or sorted.
- Use `unique_together` or `UniqueConstraint` to enforce data integrity at the DB level.
- Use `on_delete=models.CASCADE` explicitly — never rely on default behavior.
- Never use `null=True` on `CharField` or `TextField` — use `blank=True` with empty string default instead.

```python
# ✅ correct CharField
title = models.CharField(max_length=200, blank=True, default='')

# ❌ wrong
title = models.CharField(max_length=200, null=True)
```

### Migrations

- Every model change must have a migration.
- Never edit existing migrations after they've been applied (create a new migration instead).
- Name migrations descriptively when using `--name`: `0005_add_status_to_course`.
- Commit migrations to version control.

### ORM Usage

- Use `select_related()` for ForeignKey / OneToOne relations to avoid N+1 queries.
- Use `prefetch_related()` for ManyToMany and reverse FK relations.
- Never loop over a queryset and perform queries inside the loop.

```python
# ✅ efficient
courses = Course.objects.select_related('department').prefetch_related('lessons').all()

# ❌ N+1 problem
for course in Course.objects.all():
    print(course.department.name)  # This hits the DB on every iteration
```

---

## 5. Service Layer Rules

Every `services.py` file must follow these rules:

- Functions take plain Python objects as arguments (User instances, strings, ints) — never `request`.
- All writes that span multiple models must use `@transaction.atomic`.
- All service functions must be fully type-hinted.
- Each function has a one-line docstring explaining what it does and what it returns.

```python
# ✅ correct service function
@transaction.atomic
def enroll_user_in_course(user: User, course: Course) -> 'Enrollment':
    """Enroll user in a course. Idempotent — returns existing enrollment if already enrolled."""
    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
    if created:
        Notification.objects.create(user=user, type='new_course', text=f"You've been enrolled in {course.title}")
    return enrollment
```

---

## 6. Template Rules

- All UI text must be wrapped in `{% trans "..." %}` (required for i18n).
- No raw SQL or Python logic in templates — only display logic.
- Extract repeated blocks into `{% include 'components/...' %}` partials.
- Use `{% block %}` inheritance from `base.html`.

```html
<!-- ✅ correct -->
<h1>{% trans "My Courses" %}</h1>

<!-- ❌ wrong — hardcoded English, not translatable -->
<h1>My Courses</h1>
```

### Component Partials

Keep these in `templates/components/`:

| File | Purpose |
|---|---|
| `progress_bar.html` | Reusable progress bar. Accepts `percent` and `label` vars. |
| `lesson_card.html` | Single lesson card. |
| `course_card.html` | Course grid card. |
| `badge_widget.html` | Badge icon + name. |
| `notification_bell.html` | Topbar bell with unread count. |
| `alert.html` | Success / error / info alert message. |

---

## 7. Static Files and CSS

- Use **Tailwind CSS utility classes** directly in templates — no custom CSS files unless unavoidable.
- For complex repeated styles, use Tailwind's `@apply` in a small `custom.css` file.
- All static files must be organized under `static/`:
  ```
  static/
  ├── css/tailwind.css
  ├── js/alpine.js
  └── images/
  ```
- Run `python manage.py collectstatic` before deploy.

### Tailwind Setup

Use the Tailwind CDN for development:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

For production (Railway), install via npm and compile:
```bash
npm install -D tailwindcss
npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --minify
```

Add the build command to the Railway build step (see Section 13).

---

## 8. Security Rules

These must be active in production settings:

```python
# config/settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://yourdomain.com']
```

- Always use Django's CSRF protection on forms (`{% csrf_token %}`).
- Never use `mark_safe()` on user-generated content.
- Validate and sanitize all file uploads (check MIME type, not just extension).
- Use `get_object_or_404()` instead of `.get()` in views to avoid leaking object existence.

---

## 9. Error Handling

- Use `get_object_or_404()` in all views that look up by slug or ID.
- Create custom 404 and 500 error templates: `templates/404.html` and `templates/500.html`.
- Log unexpected exceptions with `logger.exception()` — never silence errors with bare `except: pass`.

```python
import logging
logger = logging.getLogger(__name__)

# ✅ correct
try:
    result = some_risky_operation()
except Exception:
    logger.exception("Failed to perform risky operation for user %s", user.id)
    raise

# ❌ wrong — swallows the error silently
try:
    result = some_risky_operation()
except:
    pass
```

---

## 10. Code Comments

Comments must be written **for a junior developer** to understand:

```python
# ✅ good comment — explains WHY
# We use get_or_create here to make this idempotent.
# If the badge was already awarded, we skip it silently instead of raising an error.
user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)

# ❌ bad comment — just repeats the code
# Get or create user badge
user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
```

Use `# TODO:` for intentionally incomplete code. Always include a reason:
```python
# TODO: Replace with PostgreSQL full-text search for better performance at scale.
results = Article.objects.filter(content__icontains=query)
```

---

## 11. Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Django app | lowercase, underscore | `knowledge_base` |
| Model | PascalCase, singular | `LessonRating` |
| View | PascalCase + suffix | `CourseDetailView`, `CourseListView` |
| Service function | snake_case, verb first | `award_points`, `enroll_user_in_course` |
| Template | lowercase, underscore | `course_detail.html` |
| URL name | app_name:action_object | `courses:detail`, `courses:list` |
| CSS class | Tailwind only, no custom names unless truly necessary | |
| JavaScript variable | camelCase | `lessonProgress` |

---

## 12. Testing Rules

Every new service function must have at least one unit test.

Use Django's `TestCase` or `pytest-django`:

```python
# ✅ test structure
class AwardPointsServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')

    def test_points_are_added_to_profile(self):
        profile = award_points(self.user, amount=50, source='LESSON')
        self.assertEqual(profile.total_points, 50)

    def test_points_log_entry_is_created(self):
        award_points(self.user, amount=50, source='LESSON', reference='lesson-slug')
        self.assertEqual(PointsLog.objects.filter(user=self.user).count(), 1)
```

**Tests must pass before any commit. If tests are failing — fix them first, do not commit broken code.**

```bash
python manage.py test
# or with pytest-django:
pytest
```

---

## 13. Deployment — Railway (Production)

The project is deployed to **Railway** as the production environment. This is a temporary but fully functional setup. All production configuration lives in `config/settings/production.py`.

### Required Files

**`Procfile`** (in project root):
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
release: python manage.py migrate --no-input && python manage.py collectstatic --no-input
```

**`runtime.txt`** (in project root):
```
python-3.11.x
```

**`requirements.txt`** — must include:
```
django>=4.2,<5.0
gunicorn
psycopg2-binary
whitenoise
dj-database-url
python-decouple
Pillow
detect-secrets
```

### WhiteNoise for Static Files

Railway does not serve static files natively. Use WhiteNoise middleware:

```python
# config/settings/base.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Add right after SecurityMiddleware
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Railway Environment Variables

Set these in the Railway dashboard under the service's "Variables" tab:

```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate a strong random key>
DEBUG=False
DATABASE_URL=<auto-provided by Railway PostgreSQL plugin>
ALLOWED_HOSTS=yourapp.railway.app,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourapp.railway.app,https://yourdomain.com

DEFAULT_ADMIN_EMAIL=admin@dimkava.ge
DEFAULT_ADMIN_PASSWORD=<strong password>
DEFAULT_HR_EMAIL=hr@dimkava.ge
DEFAULT_HR_PASSWORD=<strong password>
DEFAULT_EMPLOYEE_EMAIL=employee@dimkava.ge
DEFAULT_EMPLOYEE_PASSWORD=<strong password>
```

**Never put these values in code or commit them.** Railway injects them as environment variables at runtime.

### Database on Railway

- Add the **PostgreSQL plugin** inside your Railway project.
- Railway auto-sets `DATABASE_URL` — read it via `dj-database-url`:

```python
# config/settings/production.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}
```

### Media Files on Railway

Railway's filesystem is ephemeral — uploaded files (avatars, documents) will be lost on redeploy.

For now (MVP): accept this limitation and document it.
```python
# TODO: Replace local media storage with S3-compatible storage (e.g. Cloudflare R2 or AWS S3)
# when persistent media uploads are required in production.
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

### Deploy Flow

```bash
# Railway auto-deploys on every push to main branch.
# Before pushing to main, always run this sequence:

1. pytest                                          # All tests must pass
2. git diff --cached | grep -iE "(secret|password|token|api_key)"  # Safety scan
3. git commit -m "feat(...): ..."
4. git push origin main
5. railway logs --tail                             # Watch the build log
```

### Useful Railway CLI Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Run management commands against the production DB
railway run python manage.py createsuperuser
railway run python manage.py migrate
railway run python manage.py loaddata fixtures/initial_data.json

# View live logs
railway logs --tail
```

---

## 14. Performance Checklist

Before marking any feature as done, verify:

- [ ] No N+1 queries (use `select_related` / `prefetch_related`).
- [ ] Frequently filtered fields have `db_index=True`.
- [ ] List views are paginated (use Django's `Paginator` or `ListView.paginate_by`).
- [ ] Images are served via `MEDIA_URL`, not embedded as base64.
- [ ] Template context does not contain unnecessary full querysets.
- [ ] Tests pass: `pytest` exits with 0 errors.
- [ ] Safety scan passes: no secrets in staged files.
- [ ] Checkpoint summary written before moving to next step.

---

## 15. Accessibility (a11y) Basics

Even for an internal tool, follow basic accessibility rules:

- All `<img>` tags must have `alt` attributes.
- Form inputs must have associated `<label>` elements (use `for` + `id`, not just proximity).
- Buttons must have visible text or `aria-label` — no icon-only buttons without labels.
- Color must not be the only indicator of state (e.g., don't rely on red/green alone — add text like "Completed" / "Pending").
- Use semantic HTML: `<button>` for actions, `<a>` for navigation, `<h1>`–`<h6>` for headings in order.

---

## 16. Logging

Set up structured logging from day one:

```python
# config/settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

In every app's service layer, create a module-level logger:
```python
import logging
logger = logging.getLogger(__name__)
```

Railway captures stdout/stderr — these logs will be visible in `railway logs`.

---

## 17. README Requirements

Every project must have a `README.md` in the root with:

```markdown
## Local Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values
3. `docker-compose up -d` (starts Postgres + Redis)
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py loaddata fixtures/initial_data.json`
7. `python manage.py runserver`

## Default Users
See `.env.example` for credentials.

## Running Tests
pytest

## Deploying
Push to `main` — Railway auto-deploys.
See core-rules.md Section 13 for full deploy checklist.
```

---

## 18. Code Review Checklist (before marking a task done)

Use this checklist before finishing any step:

- [ ] All new code follows naming conventions (Section 11).
- [ ] No hardcoded strings — all UI text uses `{% trans %}`.
- [ ] No secrets or credentials anywhere in the code.
- [ ] Safety scan passed (`detect-secrets` or manual grep).
- [ ] Tests written and passing for all new service functions.
- [ ] Migrations created and committed for all model changes.
- [ ] No N+1 queries.
- [ ] Custom 404/500 pages exist.
- [ ] New views have `LoginRequiredMixin`.
- [ ] Checkpoint summary written and posted in chat.
- [ ] `.env.example` updated if new env vars were added.
- [ ] Committed with a proper message before moving to next step.
