"""User profile and automated assignment rules (best_practices §3)."""
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Department/role and content assigned by AssignmentRule."""
    USER_TYPE_CHOICES = [
        ('candidate', 'Candidate'),
        ('employee', 'Employee'),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='employee')
    phone = models.CharField(max_length=40, blank=True)
    department = models.ForeignKey(
        'departments.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_profiles',
    )
    role = models.ForeignKey(
        'departments.Role',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_profiles',
    )
    assigned_onboarding_program = models.ForeignKey(
        'onboarding.OnboardingProgram',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_users',
    )
    pending_course_slugs = models.JSONField(default=list, blank=True)
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when the user confirms their email (required for candidates before learning access).',
    )

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'

    def __str__(self):
        return f'Profile: {self.user}'

    @property
    def is_candidate(self) -> bool:
        return self.user_type == 'candidate'

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None


class AssignmentRule(models.Model):
    """
    When a user's profile matches role + department, assign onboarding program
    and record required course slugs (enrollment wiring is TODO).
    """
    role_name = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        'departments.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assignment_rules',
    )
    onboarding_program_slug = models.CharField(max_length=100, blank=True)
    required_course_slugs = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'Rule: {self.role_name or "Any role"} / {self.department or "Any dept"}'
