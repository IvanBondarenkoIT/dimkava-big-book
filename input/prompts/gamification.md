# Gamification Subsystem — Extension Prompt

> **Apply this after `base.md`.** Do not rewrite existing architecture — extend it by adding the `gamification` Django app.

---

## Role

You are a senior backend engineer and Django expert. Add a clean, robust gamification layer to the existing internal training portal. The gamification system must be modular, testable, and production-ready.

---

## High-Level Goals

- Add a dedicated `gamification` Django app.
- Keep core business logic in a service layer (pure functions, no HTTP dependencies).
- Provide template context and/or API data to power an engaging UI (progress bars, missions, badges, levels).
- Keep "serious" content (safety, compliance, legal) visually minimal — award points quietly, no silly text.

---

## 1. App Structure

```
apps/gamification/
├── __init__.py
├── models.py
├── services.py           # Pure business logic: points, levels, badges, missions
├── selectors.py          # Complex DB queries (leaderboard, dashboard context)
├── signals.py            # Hooks into existing training completion events
├── serializers.py        # DRF serializers (if DRF is used) OR context builders
├── views.py              # Dashboard and leaderboard views
├── urls.py
├── admin.py
└── tests/
    ├── test_services.py
    └── test_models.py
```

---

## 2. Models

### GamificationProfile
One-to-one with `User`. Auto-created on user creation via signal.

```python
class GamificationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gamification_profile')
    total_points = models.PositiveIntegerField(default=0, db_index=True)
    level = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — Level {self.level} ({self.total_points} pts)"
```

### Badge

```python
class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)  # e.g. "ONBOARDING_COMPLETE"
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', blank=True)
    is_active = models.BooleanField(default=True)
    is_compliance = models.BooleanField(default=False)  # If True: awarded quietly, no celebration UI
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
```

### UserBadge

```python
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)  # e.g. mission code or source

    class Meta:
        unique_together = ('user', 'badge')  # Idempotent: no duplicate badges

    def __str__(self):
        return f"{self.user} earned {self.badge.code}"
```

### Mission

```python
class Mission(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_mandatory = models.BooleanField(default=False)  # Mandatory = compliance/safety treatment
    estimated_minutes = models.PositiveIntegerField()
    bonus_points = models.PositiveIntegerField(default=0)  # Awarded on completion
    completion_badge = models.ForeignKey(Badge, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.code})"
```

### MissionStep

```python
class MissionStep(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    # Link to existing content — use slug reference, not hard FK (extension point)
    module_slug = models.CharField(max_length=100)
    module_type = models.CharField(max_length=50, choices=[
        ('lesson', 'Lesson'),
        ('onboarding_module', 'Onboarding Module'),
        ('article', 'Knowledge Base Article'),
        ('quiz', 'Quiz'),
    ])
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ('mission', 'order')

    def __str__(self):
        return f"{self.mission.code} — Step {self.order}: {self.title}"

    def get_absolute_url(self):
        # TODO: Map module_type + module_slug to actual URL once all app URLs are finalized
        # e.g. lesson → /courses/<course_slug>/lessons/<id>/
        raise NotImplementedError("Wire this up to URL resolver")
```

### UserMissionProgress

```python
class UserMissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed_step_slugs = models.JSONField(default=list)  # List of completed module_slugs
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'mission')

    def __str__(self):
        status = "✓" if self.is_completed else f"{len(self.completed_step_slugs)} steps"
        return f"{self.user} — {self.mission.code} [{status}]"
```

### PointsLog

```python
class PointsLog(models.Model):
    SOURCE_CHOICES = [
        ('LESSON', 'Lesson Completed'),
        ('QUIZ', 'Quiz Passed'),
        ('MISSION', 'Mission Completed'),
        ('ONBOARDING', 'Onboarding Step'),
        ('BADGE', 'Badge Awarded'),
        ('MANUAL', 'Manual Award'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_log')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    reference = models.CharField(max_length=100, blank=True)  # e.g. lesson slug or mission code
    points = models.IntegerField()  # Can be negative for corrections
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} +{self.points} [{self.source}]"
```

---

## 3. Level System (configurable)

Define in `services.py` as a constant — easy to adjust later:

```python
LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 100),
    (3, 300),
    (4, 700),
    (5, 1500),
    (6, 3000),
    (7, 6000),
]
# Level names to display in UI:
LEVEL_NAMES = {
    1: "Newcomer",
    2: "Barista",
    3: "Specialist",
    4: "Expert",
    5: "Senior Expert",
    6: "Mentor",
    7: "Legend",
}
```

---

## 4. Service Layer (`services.py`)

All functions must be:
- Independent from HTTP (no `request` object).
- Wrapped in `django.db.transaction.atomic()` where they write multiple rows.
- Easy to call from views, signals, and management commands.
- Fully type-hinted.

```python
from typing import Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import GamificationProfile, Badge, UserBadge, Mission, UserMissionProgress, PointsLog

User = get_user_model()


def calculate_level(total_points: int) -> int:
    """Return the level number for a given points total."""
    ...


def get_level_progress(total_points: int) -> dict:
    """
    Return a dict with:
    - current_level (int)
    - level_name (str)
    - points_in_current_level (int)
    - points_needed_for_next_level (int)
    - percent_to_next_level (float 0-100)
    Used directly in template context.
    """
    ...


@transaction.atomic
def award_points(
    user: User,
    amount: int,
    source: str,
    reference: str = "",
    note: str = "",
) -> GamificationProfile:
    """
    Add `amount` points to user's profile.
    Log to PointsLog.
    Recalculate and save level.
    Return updated GamificationProfile.
    """
    ...


@transaction.atomic
def award_badge(
    user: User,
    badge_code: str,
    reason: str = "",
) -> Optional[UserBadge]:
    """
    Award badge by code. Idempotent — silently returns None if already awarded.
    Badge must be active.
    Returns UserBadge instance or None.
    """
    ...


@transaction.atomic
def update_mission_progress(
    user: User,
    mission_code: str,
    completed_step_slug: str,
) -> UserMissionProgress:
    """
    Mark a step (by module_slug) as completed in the user's mission progress.
    If all required steps are done:
    - Mark mission as completed.
    - Award bonus_points if any.
    - Award completion_badge if configured.
    Return updated UserMissionProgress.
    """
    ...


def get_or_create_profile(user: User) -> GamificationProfile:
    """Get or create GamificationProfile for a user."""
    profile, _ = GamificationProfile.objects.get_or_create(user=user)
    return profile
```

---

## 5. Selectors (`selectors.py`)

Complex queries live here, not in views:

```python
def get_gamification_dashboard_context(user) -> dict:
    """
    Return all data needed for the gamification dashboard template:
    - profile (total_points, level, level_name, percent_to_next_level)
    - missions: list of active missions with per-user progress data
    - recent_badges: last 5 earned badges
    - leaderboard_rank: user's rank in the leaderboard
    """
    ...


def get_leaderboard(top_n: int = 10, current_user=None) -> dict:
    """
    Return:
    - top_users: list of top N users by total_points
      (only expose: display_name (first name + last initial), level, total_points)
    - current_user_entry: always include current user even if outside top N
    Uses select_related for efficiency.
    """
    ...
```

---

## 6. Signals (`signals.py`)

Hook into existing training events. Keep signal handlers thin — call service functions, don't put logic inside handlers.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

# Custom signal emitted by the courses app when a lesson is completed
# TODO: Wire this signal in courses/services.py when a UserProgress is marked complete
lesson_completed = Signal()  # providing_args: ['user', 'lesson']

# Custom signal emitted when a quiz is passed
quiz_passed = Signal()       # providing_args: ['user', 'lesson', 'score']

# Custom signal emitted when onboarding module is completed
onboarding_module_completed = Signal()  # providing_args: ['user', 'module']


@receiver(lesson_completed)
def on_lesson_completed(sender, user, lesson, **kwargs):
    """Award points and update mission progress when a lesson is completed."""
    from .services import award_points, update_mission_progress
    award_points(user, amount=10, source='LESSON', reference=lesson.slug)
    # TODO: Determine which mission(s) this lesson belongs to and call update_mission_progress


@receiver(quiz_passed)
def on_quiz_passed(sender, user, lesson, score, **kwargs):
    """Award bonus points for passing a quiz. Award badge if score >= 90%."""
    from .services import award_points, award_badge
    award_points(user, amount=20, source='QUIZ', reference=lesson.slug)
    if score >= 90:
        award_badge(user, badge_code='QUIZ_MASTER', reason=f"Scored {score}% on {lesson.title}")


@receiver(post_save, sender='auth.User')
def create_gamification_profile(sender, instance, created, **kwargs):
    """Auto-create GamificationProfile when a new User is created."""
    if created:
        from .services import get_or_create_profile
        get_or_create_profile(instance)
```

---

## 7. Views and URLs

For this server-rendered project, implement CBVs that render templates:

```
/dashboard/         → Gamification dashboard (level, missions, badges)
/leaderboard/       → Top 10 + current user rank
```

These views use `selectors.get_gamification_dashboard_context()` to build context — no ad-hoc queries in views.

---

## 8. Template Context for UI

The `get_gamification_dashboard_context()` selector must return data structured for direct use in templates:

```python
{
    "profile": {
        "total_points": 350,
        "level": 3,
        "level_name": "Specialist",
        "percent_to_next_level": 62.5,
    },
    "missions": [
        {
            "title": "Complete Onboarding",
            "description": "...",
            "estimated_minutes": 45,
            "is_mandatory": True,
            "total_steps": 5,
            "completed_steps": 3,
            "percent_complete": 60.0,
            "is_completed": False,
            "steps": [
                {
                    "title": "Meet your team",
                    "module_slug": "meet-your-team",
                    "url": "/onboarding/meet-your-team/",
                    "is_done": True,
                }
            ]
        }
    ],
    "recent_badges": [
        {"name": "First Lesson", "icon_url": "...", "awarded_at": "2024-03-01"}
    ],
    "leaderboard_rank": 7,
}
```

---

## 9. Leaderboard Privacy

Only expose safe fields in the leaderboard:
- `display_name`: First name + last name initial (e.g., "Ivan K.")
- `level`: integer
- `level_name`: string
- `total_points`: integer

Never expose email, full last name, or internal IDs.

---

## 10. Admin Configuration

```python
# admin.py

@admin.register(GamificationProfile)
class GamificationProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'level', 'updated_at']
    search_fields = ['user__email', 'user__first_name']
    readonly_fields = ['total_points', 'level']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'is_compliance']
    list_filter = ['is_active', 'is_compliance']
    search_fields = ['code', 'name']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'awarded_at', 'reason']
    list_filter = ['badge']
    search_fields = ['user__email', 'badge__code']


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'is_mandatory', 'is_active', 'bonus_points']
    list_filter = ['is_mandatory', 'is_active']
    inlines = [MissionStepInline]


@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'mission', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'mission']
    search_fields = ['user__email']


@admin.register(PointsLog)
class PointsLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'source', 'reference', 'created_at']
    list_filter = ['source']
    search_fields = ['user__email', 'reference']
    readonly_fields = ['user', 'points', 'source', 'reference', 'note', 'created_at']
```

---

## 11. Safety / Compliance Content Rule

This is a **business rule enforced at the UI layer:**

- Missions with `is_mandatory=True` OR content with a compliance/safety tag must receive minimal gamification UI.
- Award points and badges in the backend as normal.
- In templates: check `mission.is_mandatory` — if `True`, skip celebratory animations, confetti, or bold "You earned X points!" banners. Show a simple quiet confirmation instead.
- Same logic applies to badges with `is_compliance=True`.

---

## 12. Test Coverage Required

Write unit tests in `tests/test_services.py` covering:

- `calculate_level()` — test all threshold boundaries.
- `get_level_progress()` — test percent calculation.
- `award_points()` — test points are added, level recalculated, PointsLog entry created.
- `award_badge()` — test badge awarded, test idempotency (no duplicate), test inactive badge is not awarded.
- `update_mission_progress()` — test step completion, test mission completion trigger, test bonus points and badge.

Use `pytest-django` or Django's `TestCase`. Mock no more than necessary — test against a real test database.

---

## 13. Extension Points (TODOs)

Mark these clearly in the code with `# TODO:` comments:

- `MissionStep.get_absolute_url()` — wire to actual URL resolver once all app URLs are defined.
- `on_lesson_completed` signal handler — map lesson slug to missions after missions are populated.
- Time-bound leaderboards — `PointsLog.created_at` is already there; add date filtering to leaderboard query when needed.
- External points events — `PointsLog.source` field is ready to accept new source types without migration.
