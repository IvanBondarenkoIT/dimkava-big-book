# Dimkava Internal Learning Portal — Base Architecture Prompt

> **How to use these files in Cursor:**
> 1. Start with this file (`base.md`) — it defines the full project.
> 2. Apply `gamification.md` — it extends the project with the gamification subsystem.
> 3. Apply `best_practices.md` — it adds UX and LMS best practices on top.
> 4. Apply `core-rules.md` — it enforces code quality rules throughout.

---

## Role

You are a senior full-stack developer and UX architect. Design and implement a corporate internal training portal — a modern LMS and onboarding platform for employees.

**Goal:** Build an internal "Company University" that:
- Trains employees (courses, lessons, quizzes, learning paths).
- Runs structured onboarding for new hires.
- Serves as a knowledge base and internal news hub.
- Gives management and HR basic analytics on learning progress.

---

## 1. Tech Stack

- **Backend:** Python / Django 4.x
- **Frontend:** Django HTML Templates + Alpine.js (for lightweight interactivity, no heavy SPA needed) + Tailwind CSS
- **Database:** PostgreSQL
- **Media storage:** Local filesystem for dev; design with S3-compatible storage in mind for prod
- **Task queue:** Celery + Redis (for notifications and background jobs — stub it for now, but structure the code for it)

**Do NOT use Next.js, React, or any Node-based frontend framework.** This is a server-rendered Django project.

Code must be modular with clear file and component names. Comments must be understandable for a junior developer.

---

## 2. Authentication & User Accounts

Implement a complete authentication system:

- **Login page** (`/login/`) — email + password, remember me checkbox.
- **Logout** — POST endpoint, redirects to login.
- **Password reset** — "Forgot password" flow with email link (use Django's built-in `PasswordResetView`; mock email backend in dev).
- **Profile page** (`/profile/`) — display name, role, department, avatar upload, language preference.
- **Sessions** — use Django's default session backend; set reasonable `SESSION_COOKIE_AGE`.

**Default users (created via management command or fixture, credentials from environment variables):**

```python
# .env
DEFAULT_ADMIN_EMAIL=admin@dimkava.ge
DEFAULT_ADMIN_PASSWORD=changeme_admin

DEFAULT_HR_EMAIL=hr@dimkava.ge
DEFAULT_HR_PASSWORD=changeme_hr

DEFAULT_EMPLOYEE_EMAIL=employee@dimkava.ge
DEFAULT_EMPLOYEE_PASSWORD=changeme_employee
```

---

## 3. Roles and Permissions

Three roles (extend Django's built-in groups):

| Role | Access |
|---|---|
| `employee` | Own courses, onboarding, news, knowledge base, own profile |
| `hr_manager` | Everything above + departments/roles section, analytics dashboard, user management |
| `admin` | Full access including Django admin panel |

Use Django's `@permission_required` decorators and `user_passes_test` for view-level access control. Create a `permissions.py` helper per app.

Create default users for each role on first setup (see environment variables above).

---

## 4. Internationalization (i18n)

The platform must support **3 languages: English (default), Russian, Georgian.**

- Use Django's built-in `i18n` framework (`django.utils.translation`, `{% trans %}`, `{% blocktrans %}`).
- Language switcher in the top navigation bar.
- Store user's language preference in their profile (`language` field: `en` / `ru` / `ka`).
- All UI text in templates must be wrapped in `{% trans "..." %}`.
- Create translation files: `locale/en/`, `locale/ru/`, `locale/ka/`.
- For now, English strings are real; Russian and Georgian can be TODO stubs.

---

## 5. Project File Structure

```
dimkava_portal/
├── config/                     # Django project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/               # Auth, users, roles, profiles
│   ├── onboarding/             # Onboarding flow and modules
│   ├── courses/                # LMS: courses, lessons, quizzes
│   ├── knowledge_base/         # Wiki articles and sections
│   ├── news/                   # Company news and announcements
│   ├── departments/            # Departments, roles, learning paths
│   ├── analytics/              # HR dashboard and metrics
│   ├── notifications/          # Internal notification center
│   └── gamification/           # Points, badges, missions (see gamification.md)
├── templates/
│   ├── base.html               # Main layout with sidebar + topbar
│   ├── components/             # Reusable template partials
│   │   ├── progress_bar.html
│   │   ├── lesson_card.html
│   │   ├── course_card.html
│   │   ├── badge_widget.html
│   │   └── notification_bell.html
│   └── [app_name]/             # Per-app templates
├── static/
│   ├── css/
│   │   └── tailwind.css
│   ├── js/
│   │   └── alpine.js           # Alpine.js for interactivity
│   └── images/
├── locale/                     # i18n translation files
│   ├── en/
│   ├── ru/
│   └── ka/
├── media/                      # User uploads (avatars, documents)
├── fixtures/                   # Seed data (JSON)
│   └── initial_data.json
├── manage.py
├── requirements.txt
├── .env.example
└── docker-compose.yml          # Postgres + Redis for local dev
```

---

## 6. Core Data Models

### accounts app

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES)  # employee / hr_manager / admin
    department = models.ForeignKey('departments.Department', null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    language = models.CharField(max_length=2, choices=[('en','English'),('ru','Russian'),('ka','Georgian')], default='en')
    # Future integrations
    crm_id = models.CharField(max_length=100, blank=True)
    hris_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### courses app

```python
class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    department = models.ForeignKey('departments.Department', null=True)
    level = models.CharField(choices=[('beginner','Beginner'),('intermediate','Intermediate'),('manager','Manager')])
    estimated_minutes = models.PositiveIntegerField()
    status = models.CharField(choices=[('draft','Draft'),('review','Review'),('published','Published')], default='draft')
    author = models.ForeignKey(User, related_name='authored_courses')
    last_reviewed_at = models.DateTimeField(null=True)  # For stale content detection (> 6 months)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    lesson_type = models.CharField(choices=[('video','Video'),('text','Text'),('file','File'),('quiz','Quiz')])
    content = models.TextField(blank=True)       # Text content or markdown
    video_url = models.URLField(blank=True)      # YouTube / external URL (only shown if set)
    file = models.FileField(upload_to='lessons/', blank=True)
    is_required = models.BooleanField(default=True)

class TestQuestion(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField()                 # [{"text": "...", "is_correct": true}, ...]
    order = models.PositiveIntegerField()

class UserProgress(models.Model):
    user = models.ForeignKey(User)
    lesson = models.ForeignKey(Lesson)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)
    quiz_score = models.PositiveIntegerField(null=True)  # 0-100
    # Event hooks for future webhooks
    # CourseCompleted, OnboardingCompleted — emit Django signals on these
```

### knowledge_base app

```python
class KBSection(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)  # e.g. "coffee", "finance"

class Article(models.Model):
    section = models.ForeignKey(KBSection)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()              # Rich text / Markdown
    status = models.CharField(choices=[('draft','Draft'),('review','Review'),('published','Published')])
    author = models.ForeignKey(User)
    updated_at = models.DateTimeField(auto_now=True)
    related_courses = models.ManyToManyField('courses.Course', blank=True)
```

### news app

```python
class NewsPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    tag = models.CharField(choices=[('important','Important'),('training','Training'),('hr','HR'),('general','General')])
    is_pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField()
    author = models.ForeignKey(User)
```

### departments app

```python
class Department(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Role(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department)
    description = models.TextField()
    recommended_courses = models.ManyToManyField('courses.Course', blank=True)
    required_courses = models.ManyToManyField('courses.Course', blank=True, related_name='required_for_roles')
```

### notifications app

```python
class Notification(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(choices=[
        ('new_course','New Course'),
        ('deadline','Deadline'),
        ('onboarding','Onboarding Reminder'),
        ('news','News'),
        ('badge','Badge Earned'),
    ])
    text = models.CharField(max_length=500)
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Architecture note: add external_channel = CharField (email/slack) here in the future
    # without breaking this model
```

---

## 7. Site Structure — Pages and URLs

```
/                               → Home (dashboard)
/login/                         → Login
/logout/                        → Logout
/profile/                       → User profile

/onboarding/                    → Onboarding overview with progress bar
/onboarding/<module_slug>/      → Individual onboarding module

/courses/                       → Course catalog with filters
/courses/<slug>/                → Course detail page
/courses/<slug>/lessons/<id>/   → Lesson page (video / text / file / quiz)

/wiki/                          → Knowledge base home
/wiki/<section_slug>/           → Section with article list
/wiki/<section_slug>/<slug>/    → Article page

/news/                          → News feed
/news/<slug>/                   → Single news post

/departments/                   → Department and role list (HR/admin only)
/departments/<slug>/            → Department detail with learning path

/analytics/                     → HR analytics dashboard (hr_manager/admin only)

/notifications/                 → All notifications

/search/                        → Global search results page
```

---

## 8. Main Layout (base.html)

Use semantic HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`.

**Layout structure:**
- **Topbar** (full width): Logo, global search bar, notifications bell (with unread count badge), user avatar + name dropdown (profile / logout), language switcher (EN / RU / KA).
- **Sidebar** (left, collapsible on mobile): Navigation links to all main sections. Show active state. Hide restricted sections based on user role.
- **Main content area**: Scrollable. Breadcrumbs at top.
- **Mobile first**: Sidebar collapses to hamburger menu. Use Tailwind responsive prefixes (`sm:`, `md:`, `lg:`).

---

## 9. UX Principles

- **Clear hierarchy**: Employee always knows where they are and what to do next.
- **Minimal noise**: Lots of white space, readable fonts, emphasis on progress and clear action buttons.
- **"Where to start" hint**: In each section, show a "Start here" prompt and "Next step" logic (e.g., after onboarding completes → "Go to recommended courses").
- **Visual separation**: Visually distinguish "for new employees" vs "for experienced employees / managers".
- **Gamification**: Apply everywhere possible — see `gamification.md` for full details.

---

## 10. Visual Style

- **Audience:** Young employees (students and recent graduates).
- **Style:** Modern, fresh, slightly bold. Clean cards, subtle shadows, smooth hover states.
- **Typography:** Use a readable sans-serif (Inter or similar via Google Fonts).
- **Colors:** Define a primary brand color (coffee-inspired warm tones — amber/brown accent), with clean white backgrounds.
- **Safety/compliance content:** Keep visually strict, minimal decoration — no playful elements on mandatory regulatory content.

---

## 11. Analytics Dashboard (HR / Admin only)

Display these metrics (mock data is fine; structure must be real):

- Number of active courses.
- Number of employees currently in onboarding.
- Onboarding completion percentage by department.
- Average onboarding completion time by department.
- % completion of mandatory courses.
- "Problem" lessons / tests (low completion or pass rate).

Filters: by department, role, date range.

---

## 12. Seed Data (fixtures/initial_data.json)

Include seed data for:
- 3 departments (Sales, Marketing, IT).
- 2 roles per department.
- 3 courses (one per department), each with 3 lessons (mix of types).
- 5 knowledge base articles.
- 3 news posts (one pinned).
- Default users (admin, hr_manager, employee).
- Assignment rules for each role.

---

## 13. Deployment and Environment

Create:
- `.env.example` with all required variables.
- `docker-compose.yml` for local dev (PostgreSQL + Redis containers).
- `requirements.txt` pinned versions.

Key environment variables:
```
SECRET_KEY=
DEBUG=True
DATABASE_URL=postgres://...
REDIS_URL=redis://localhost:6379/0
DEFAULT_ADMIN_EMAIL=
DEFAULT_ADMIN_PASSWORD=
DEFAULT_HR_EMAIL=
DEFAULT_HR_PASSWORD=
DEFAULT_EMPLOYEE_EMAIL=
DEFAULT_EMPLOYEE_PASSWORD=
MEDIA_ROOT=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # for dev
```

---

## 14. Implementation Order

Work iteratively. For each step: describe which files you will create, then output the full code.

1. **Project scaffold** — Django project structure, settings, base template, auth pages.
2. **Onboarding module** — models, views, templates, progress tracking.
3. **Course catalog and lesson pages** — including quiz functionality.
4. **Knowledge base and news** — articles, sections, news feed.
5. **Departments and roles** — with learning paths.
6. **Analytics dashboard** — HR metrics with mock data.
7. **Notifications center** — model, topbar bell, notifications page.
8. **Global search** — unified search across all content types.
9. **Gamification layer** — see `gamification.md`.
10. **Admin panel** — Django admin configuration for all models.

Always follow this order and do not skip or simplify steps without an explicit instruction.
