"""Notification model."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_course', 'New Course'),
        ('deadline', 'Deadline'),
        ('onboarding', 'Onboarding Reminder'),
        ('news', 'News'),
        ('badge', 'Badge Earned'),
        ('lesson_completed', 'Lesson Completed'),
        ('quiz_passed', 'Quiz Passed'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    text = models.CharField(max_length=500)
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.text[:50]}'
