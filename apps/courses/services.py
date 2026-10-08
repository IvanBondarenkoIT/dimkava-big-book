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


def save_quiz_result(
    user,
    lesson: Lesson,
    score: int | None,
    passing_score: int = 70,
    *,
    quiz_answers: dict | None = None,
) -> bool:
    """
    Save quiz score and mark lesson complete if passed.
    score=None means no gradable questions (survey); stored as 0.
    Returns True if passed.
    """
    if not isinstance(lesson, Lesson):
        lesson = Lesson.objects.get(pk=lesson)
    stored_score = 0 if score is None else int(score)
    passed = stored_score >= passing_score
    defaults = {
        'is_completed': passed,
        'completed_at': timezone.now(),
        'quiz_score': stored_score,
    }
    if quiz_answers is not None:
        defaults['quiz_answers'] = quiz_answers
    with transaction.atomic():
        progress, _ = UserProgress.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults=defaults,
        )
    if passed:
        quiz_passed.send(sender=UserProgress, user=user, lesson=lesson, score=stored_score)
    return passed


def record_quiz_attempt(progress: UserProgress) -> None:
    """Increment attempt counter and lock until HR unlocks retake."""
    if not progress.lesson or progress.lesson.lesson_type != 'quiz':
        return
    progress.quiz_attempts_count = (progress.quiz_attempts_count or 0) + 1
    progress.candidate_quiz_locked = True
    progress.save(update_fields=['quiz_attempts_count', 'candidate_quiz_locked'])


def unlock_quiz_retake(progress: UserProgress, *, by_user) -> None:
    """Allow this user to submit the quiz again (HR/admin action)."""
    if not progress.lesson or progress.lesson.lesson_type != 'quiz':
        return
    progress.candidate_quiz_locked = False
    progress.candidate_retake_unlocked_at = timezone.now()
    progress.candidate_retake_unlocked_by = by_user
    progress.save(
        update_fields=[
            'candidate_quiz_locked',
            'candidate_retake_unlocked_at',
            'candidate_retake_unlocked_by',
        ]
    )


def unlock_candidate_quiz_retake(progress: UserProgress, *, by_user) -> None:
    """Backward-compatible alias."""
    unlock_quiz_retake(progress, by_user=by_user)
