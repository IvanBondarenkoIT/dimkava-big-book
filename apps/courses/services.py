"""Course business logic."""
from django.db import transaction
from django.utils import timezone

from .models import Lesson, UserProgress
from .signals import lesson_completed, quiz_passed


def mark_lesson_complete(user, lesson: Lesson) -> bool:
    """Mark a lesson as complete. Idempotent."""
    if not isinstance(lesson, Lesson):
        lesson = Lesson.objects.get(pk=lesson)
    with transaction.atomic():
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            created = True
    if created:
        lesson_completed.send(sender=UserProgress, user=user, lesson=lesson)
    return created


def save_quiz_result(user, lesson: Lesson, score: int, passing_score: int = 70) -> bool:
    """
    Save quiz score and mark lesson complete if passed.
    Returns True if passed.
    """
    if not isinstance(lesson, Lesson):
        lesson = Lesson.objects.get(pk=lesson)
    passed = score >= passing_score
    with transaction.atomic():
        progress, _ = UserProgress.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'is_completed': passed,
                'completed_at': timezone.now() if passed else None,
                'quiz_score': score,
            }
        )
    if passed:
        quiz_passed.send(sender=UserProgress, user=user, lesson=lesson, score=score)
    return passed
