"""Onboarding models — program, modules, steps, progress."""
from django.conf import settings
from django.db import models


class OnboardingProgram(models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=80, blank=True)
    estimated_days = models.PositiveIntegerField(default=90)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class OnboardingModule(models.Model):
    program = models.ForeignKey(OnboardingProgram, on_delete=models.CASCADE, related_name='modules')
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['program', 'order']
        unique_together = [('program', 'slug')]

    def __str__(self):
        return f'{self.program.title} — {self.title}'


class OnboardingStep(models.Model):
    module = models.ForeignKey(OnboardingModule, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ['module', 'order']
        unique_together = [('module', 'order')]

    def __str__(self):
        return self.title


class OnboardingProgress(models.Model):
    """Tracks which steps a user has completed."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding_progress')
    step = models.ForeignKey(OnboardingStep, on_delete=models.CASCADE, related_name='progress')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'step')]

    def __str__(self):
        return f'{self.user} — {self.step}'
