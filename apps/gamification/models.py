from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class GamificationProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gamification_profile'
    )
    total_points = models.PositiveIntegerField(default=0, db_index=True)
    level = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Gamification profile')
        verbose_name_plural = _('Gamification profiles')

    def __str__(self):
        return f'{self.user.get_username()} — Level {self.level} ({self.total_points} pts)'


class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=200, blank=True)  # URL or static path; avoids Pillow on ImageField
    is_active = models.BooleanField(default=True)
    is_compliance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Badge')
        verbose_name_plural = _('Badges')

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
        verbose_name = _('User badge')
        verbose_name_plural = _('User badges')
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
        verbose_name = _('Mission')
        verbose_name_plural = _('Missions')
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
        verbose_name = _('Mission step')
        verbose_name_plural = _('Mission steps')
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
        verbose_name = _('User mission progress')
        verbose_name_plural = _('User mission progress')
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
        verbose_name = _('Points log')
        verbose_name_plural = _('Points logs')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.points:+d} [{self.source}]'
