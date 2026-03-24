"""Notification signal handlers."""
from django.dispatch import receiver

from apps.courses.signals import lesson_completed, quiz_passed

from .services import notify_lesson_completed, notify_quiz_passed


@receiver(lesson_completed)
def on_lesson_completed(sender, user, lesson, **kwargs):
    notify_lesson_completed(user, lesson)


@receiver(quiz_passed)
def on_quiz_passed(sender, user, lesson, score, **kwargs):
    notify_quiz_passed(user, lesson, score)
