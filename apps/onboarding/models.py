"""Onboarding models — program, modules, steps, progress."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language


class OnboardingProgram(models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, default='')
    title_ka = models.CharField(max_length=255, blank=True, default='')
    title_ru = models.CharField(max_length=255, blank=True, default='')
    role = models.CharField(max_length=80, blank=True)
    visible_for_candidates = models.BooleanField(default=False)
    estimated_days = models.PositiveIntegerField(default=90)
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True, default='')
    description_ka = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Onboarding program')
        verbose_name_plural = _('Onboarding programs')
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def localized_title(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'title_{lang}', '') or self.title_en or self.title

    @property
    def localized_description(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'description_{lang}', '') or self.description_en or self.description


class OnboardingModule(models.Model):
    program = models.ForeignKey(OnboardingProgram, on_delete=models.CASCADE, related_name='modules')
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, default='')
    title_ka = models.CharField(max_length=255, blank=True, default='')
    title_ru = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True, default='')
    description_ka = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = _('Onboarding module')
        verbose_name_plural = _('Onboarding modules')
        ordering = ['program', 'order']
        unique_together = [('program', 'slug')]

    def __str__(self):
        return f'{self.program.title} — {self.title}'

    @property
    def localized_title(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'title_{lang}', '') or self.title_en or self.title


class OnboardingStep(models.Model):
    module = models.ForeignKey(OnboardingModule, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, default='')
    title_ka = models.CharField(max_length=255, blank=True, default='')
    title_ru = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True)
    content_en = models.TextField(blank=True, default='')
    content_ka = models.TextField(blank=True, default='')
    content_ru = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = _('Onboarding step')
        verbose_name_plural = _('Onboarding steps')
        ordering = ['module', 'order']
        unique_together = [('module', 'order')]

    def __str__(self):
        return self.title

    @property
    def localized_title(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'title_{lang}', '') or self.title_en or self.title

    @property
    def localized_content(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'content_{lang}', '') or self.content_en or self.content


class OnboardingProgress(models.Model):
    """Tracks which steps a user has completed."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding_progress')
    step = models.ForeignKey(OnboardingStep, on_delete=models.CASCADE, related_name='progress')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Onboarding progress')
        verbose_name_plural = _('Onboarding progress')
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
        verbose_name = _('Mentor')
        verbose_name_plural = _('Mentors')
        ordering = ['user_id']

    def __str__(self):
        return f'Mentor: {self.user.get_username()}'


class MentorAssignment(models.Model):
    mentee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_assignment')
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mentor assignment')
        verbose_name_plural = _('Mentor assignments')
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
        verbose_name = _('Mentor session')
        verbose_name_plural = _('Mentor sessions')
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
        verbose_name = _('Onboarding feedback')
        verbose_name_plural = _('Onboarding feedback')
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
