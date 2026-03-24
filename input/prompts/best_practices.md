# Best Practices — LMS & Onboarding Portal Extension Prompt

> **Apply this after `base.md` and `gamification.md`.** Do not break existing architecture — extend it with new entities, pages, and admin enhancements.

---

## 1. Mentorship Module

Add a mentorship layer to onboarding:

### Models

```python
# apps/onboarding/models.py

class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    title = models.CharField(max_length=100)             # e.g. "Senior Barista"
    contact_info = models.TextField(blank=True)          # Slack handle, phone, etc.
    responsibility_area = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Mentor: {self.user.get_full_name()}"


class MentorAssignment(models.Model):
    mentee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_assignment')
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)


class MentorSession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('day_1', 'First Day'),
        ('week_1', 'End of First Week'),
        ('probation_end', 'End of Probation Period'),
        ('custom', 'Custom'),
    ]
    assignment = models.ForeignKey(MentorAssignment, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    scheduled_date = models.DateField()
    checklist_topics = models.JSONField(default=list)    # ["Introduce to team", "Review values", ...]
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)                 # Short comment after the meeting

    def __str__(self):
        return f"{self.get_session_type_display()} — {self.assignment.mentee.get_full_name()}"
```

### UI Block

Add a "Your Mentor" block to the onboarding page:
- Mentor's name, title, contact info, area of responsibility.
- List of scheduled sessions with status (upcoming / completed).
- For each session: checklist of topics, date, "Mark as done" button + comment field.

---

## 2. Individual Learning Plans (ILP)

### Models

```python
# apps/courses/models.py (or a dedicated apps/ilp/ app)

class IndividualLearningPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_plans')
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_ilps')
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ILPItem(models.Model):
    plan = models.ForeignKey(IndividualLearningPlan, on_delete=models.CASCADE, related_name='items')
    content_type = models.CharField(max_length=20, choices=[('course', 'Course'), ('lesson', 'Lesson'), ('article', 'Article')])
    object_slug = models.CharField(max_length=100)     # References existing content by slug
    title = models.CharField(max_length=200)           # Cached for display
    is_required = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
```

### UI

On the user profile page, add a "My Learning Plan" block with:
- Overall progress bar.
- List of items with status (completed / pending) and deadline.
- "Next up" highlighted item.

HR/admin can create and assign ILPs via Django admin.

---

## 3. Automated Program Assignment

### Model

```python
# apps/accounts/models.py

class AssignmentRule(models.Model):
    """
    When a user is created with matching role + department, automatically
    assign them the specified onboarding program and required courses.
    """
    role_name = models.CharField(max_length=100, blank=True)      # Match by role name (or blank = any)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    onboarding_program_slug = models.CharField(max_length=100, blank=True)
    required_course_slugs = models.JSONField(default=list)        # ["barista-basics", "safety-101"]
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Rule: {self.role_name or 'Any role'} / {self.department or 'Any dept'}"
```

### Logic

In `apps/accounts/signals.py`, on `post_save` for User (when `created=True`):
1. Find matching `AssignmentRule` by role + department.
2. Auto-assign onboarding program.
3. Auto-enroll in required courses.

This is mock logic for now — mark with `# TODO: connect to real enrollment model`.

### Admin UI

In Django admin for `AssignmentRule`: list display with role, department, course count, active status. Easy to edit.

---

## 4. Notification Center

### Model

Already defined in `base.md`. Use it as-is.

### Behavior

Trigger notifications automatically:
- New course published → notify employees in the relevant department.
- Lesson deadline approaching (3 days) → notify the assigned user.
- Onboarding not completed after 3 days → reminder notification.
- Badge earned → notification with badge name and icon.

For now, create notifications synchronously in the same request. Mark with `# TODO: move to Celery task` for each trigger.

### Architecture Note

Add to the `Notification` model:
```python
external_channel = models.CharField(
    max_length=20,
    choices=[('none','None'),('email','Email'),('slack','Slack')],
    default='none'
)
# When external_channel != 'none', a future Celery task will route it externally.
# No real integration needed now — the field makes the migration path clear.
```

---

## 5. Content Lifecycle (Workflow)

Add status and staleness tracking to courses and articles:

### Already in base.md

Courses and Articles already have `status = draft / review / published` and `updated_at`.

### Add to both models

```python
responsible_editor = models.ForeignKey(
    User, null=True, blank=True, on_delete=models.SET_NULL,
    related_name='%(class)s_responsible'
)
review_required_after_days = models.PositiveIntegerField(default=180)  # 6 months default

@property
def is_stale(self) -> bool:
    """Returns True if content hasn't been updated in review_required_after_days."""
    if not self.updated_at:
        return False
    from django.utils import timezone
    delta = timezone.now() - self.updated_at
    return delta.days > self.review_required_after_days
```

### Admin UI

In `CourseAdmin` and `ArticleAdmin`:
- Add `list_filter` for `status` and `responsible_editor`.
- Add a custom `list_display` column `stale_indicator` that shows a ⚠️ icon if `is_stale` is True.
- Visual highlight for stale or `review` status items (use `get_list_display_links` or CSS class injection).

---

## 6. Analytics Dashboard

### Already in base.md

The analytics dashboard is defined there. Extend it with these additional metrics:

- Average onboarding completion time per department (in days).
- % of employees who completed all mandatory courses.
- "Problem content" table: lessons and quizzes with completion rate < 50% — sortable by completion rate.
- Filters: department, role, date range (last 30 / 90 / 365 days).

All data can be mock. Build the view and template context structure so it's ready to swap mock for real DB aggregations.

---

## 7. Global Search

### Model / Logic

No new model needed. Implement a `SearchResult` dataclass and a `global_search(query: str, user) -> list[SearchResult]` function in `apps/search/selectors.py`.

```python
@dataclass
class SearchResult:
    type: str          # "course", "lesson", "article", "news", "role"
    title: str
    url: str
    snippet: str       # Short excerpt (max 150 chars)
    department: str    # Optional, for filtering
    tags: list[str]
```

Search across:
- Course titles and descriptions
- Lesson titles
- Article titles and content
- News titles and body
- Role titles

Use Django's `Q` objects and `__icontains` for now. Mark with `# TODO: replace with PostgreSQL full-text search` for production.

### UI

- `SearchBar` component in topbar (in `base.html`) — submits GET to `/search/?q=...`.
- `/search/` page shows results grouped by type with filter chips (All / Courses / Articles / News).

---

## 8. Employee Feedback

### Models

```python
# apps/courses/models.py

class LessonRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')


class OnboardingFeedback(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    format_rating = models.PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')])
    unclear_parts = models.TextField(blank=True)
    missing_topics = models.TextField(blank=True)
    overall_comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
```

### UI

- After completing onboarding, show a short feedback survey modal (3 fields, all optional).
- On lesson pages, show a star rating widget below lesson content. Optional comment field expands on click.

### Admin

`LessonRatingAdmin`: list_display = lesson, average rating, count. Filter by lesson, department, date range.

---

## 9. Future Integration Hooks

These are already structurally present — document them explicitly as TODOs in code:

### In `UserProfile`

```python
crm_id = models.CharField(max_length=100, blank=True)    # TODO: populate from CRM on sync
hris_id = models.CharField(max_length=100, blank=True)   # TODO: populate from HR system on sync
```

### Django Signals as Webhook Events

In each app, define these signals and emit them at the right moment. No external call needed now — just the signal infrastructure:

```python
# apps/courses/signals.py
course_completed = Signal()       # args: user, course
# apps/onboarding/signals.py
onboarding_completed = Signal()   # args: user
# apps/gamification/signals.py
badge_earned = Signal()           # args: user, badge
```

Mark each with:
```python
# TODO: Connect this signal to a webhook dispatcher task (Celery) when external integrations are needed.
```

---

## 10. Onboarding "Where to Start" Flow

Ensure a clear next-step logic throughout onboarding:

- After each onboarding module is completed → show a "Next: [module name] →" button.
- After all onboarding is complete → show "Great work! Your next step: [first recommended course]" with a clear CTA button.
- On the home dashboard, show an "Onboarding in progress" banner if the user hasn't completed onboarding yet.
- After all mandatory courses are done → suggest role-specific elective courses.

This is a UI/template-level concern. Implement it in the onboarding views' context and template logic.
