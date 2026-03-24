from django.conf import settings
from django.db import models


class GamificationProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gamification_profile'
    )
    total_points = models.PositiveIntegerField(default=0, db_index=True)
    level = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.get_username()} — Level {self.level} ({self.total_points} pts)'


class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', blank=True)
    is_active = models.BooleanField(default=True)
    is_compliance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.code})'


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges'
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [('user', 'badge')]

    def __str__(self):
        return f'{self.user} earned {self.badge.code}'


class Mission(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_mandatory = models.BooleanField(default=False)
    estimated_minutes = models.PositiveIntegerField()
    bonus_points = models.PositiveIntegerField(default=0)
    completion_badge = models.ForeignKey(
        Badge, null=True, blank=True, on_delete=models.SET_NULL, related_name='missions'
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} ({self.code})'


class MissionStep(models.Model):
    MODULE_TYPES = [
        ('lesson', 'Lesson'),
        ('onboarding_module', 'Onboarding Module'),
        ('article', 'Knowledge Base Article'),
        ('quiz', 'Quiz'),
    ]
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    module_slug = models.CharField(max_length=100)
    module_type = models.CharField(max_length=50, choices=MODULE_TYPES)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = [('mission', 'order')]

    def __str__(self):
        return f'{self.mission.code} — Step {self.order}: {self.title}'


class UserMissionProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed_step_slugs = models.JSONField(default=list)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('user', 'mission')]

    def __str__(self):
        status = '✓' if self.is_completed else f'{len(self.completed_step_slugs)} steps'
        return f'{self.user} — {self.mission.code} [{status}]'


class PointsLog(models.Model):
    SOURCE_CHOICES = [
        ('LESSON', 'Lesson Completed'),
        ('QUIZ', 'Quiz Passed'),
        ('MISSION', 'Mission Completed'),
        ('ONBOARDING', 'Onboarding Step'),
        ('BADGE', 'Badge Awarded'),
        ('MANUAL', 'Manual Award'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_log'
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    points = models.IntegerField()
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.points:+d} [{self.source}]'
