"""Onboarding models — program, modules, steps, progress."""
from django.conf import settings
from django.db import models


class OnboardingProgram(models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=80, blank=True)
    visible_for_candidates = models.BooleanField(default=False)
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


class Mentor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_profile')
    title = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True)
    responsibility_area = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['user_id']

    def __str__(self):
        return f'Mentor: {self.user.get_username()}'


class MentorAssignment(models.Model):
    mentee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_assignment')
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.mentee.get_username()} → {self.mentor or "Unassigned"}'


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
    checklist_topics = models.JSONField(default=list, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['scheduled_date', 'id']

    def __str__(self):
        return f'{self.get_session_type_display()} — {self.assignment.mentee.get_username()}'


class OnboardingFeedback(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding_feedback')
    program = models.ForeignKey(OnboardingProgram, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_onboarding_feedback',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'program')]
        ordering = ['-updated_at', '-id']

    def __str__(self):
        return f'OnboardingFeedback: {self.program} — {self.rating}/5'

    def approve(self, *, by_user) -> None:
        from django.utils import timezone

        self.status = self.Status.APPROVED
        self.moderated_at = timezone.now()
        self.moderated_by = by_user
        self.save(update_fields=['status', 'moderated_at', 'moderated_by'])

    def reject(self, *, by_user) -> None:
        from django.utils import timezone

        self.status = self.Status.REJECTED
        self.moderated_at = timezone.now()
        self.moderated_by = by_user
        self.save(update_fields=['status', 'moderated_at', 'moderated_by'])
