from django.dispatch import receiver

from apps.courses.signals import lesson_completed, quiz_passed

from .services import award_points

POINTS_LESSON = 10
POINTS_QUIZ = 15


@receiver(lesson_completed)
def on_lesson_completed_gamification(sender, user, lesson, **kwargs):
    if not user or not user.is_authenticated:
        return
    award_points(
        user,
        POINTS_LESSON,
        'LESSON',
        reference=str(lesson.pk),
        note=lesson.title[:200],
    )


@receiver(quiz_passed)
def on_quiz_passed_gamification(sender, user, lesson, score, **kwargs):
    if not user or not user.is_authenticated:
        return
    award_points(
        user,
        POINTS_QUIZ,
        'QUIZ',
        reference=str(lesson.pk),
        note=f'{lesson.title[:150]} ({score}%)',
    )
