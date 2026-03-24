"""Notification creation helpers."""
from django.urls import reverse

from .models import Notification


def notify_lesson_completed(user, lesson):
    """Create notification when user completes a lesson."""
    link = reverse('courses:lesson_detail', kwargs={'slug': lesson.course.slug, 'pk': lesson.pk})
    Notification.objects.create(
        user=user,
        type='lesson_completed',
        text=f'You completed: {lesson.title}',
        link=link,
    )


def notify_quiz_passed(user, lesson, score):
    """Create notification when user passes a quiz."""
    link = reverse('courses:lesson_detail', kwargs={'slug': lesson.course.slug, 'pk': lesson.pk})
    Notification.objects.create(
        user=user,
        type='quiz_passed',
        text=f'Quiz passed: {lesson.title} ({score}%)',
        link=link,
    )
