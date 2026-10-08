"""Aggregated pending work for HR Task Stack."""
from __future__ import annotations

from dataclasses import dataclass

from django.urls import reverse
from django.utils.translation import gettext as _


@dataclass(frozen=True)
class TaskStackItem:
    kind: str
    title: str
    subtitle: str
    url: str
    created_at: object


def get_hr_task_stack(*, limit: int = 50) -> list[TaskStackItem]:
    from apps.comments.models import Comment
    from apps.courses.models import UserProgress
    from apps.courses.quiz_review import effective_passing_score
    from apps.onboarding.models import OnboardingFeedback

    items: list[TaskStackItem] = []

    for c in (
        Comment.objects.filter(status=Comment.Status.PENDING)
        .select_related('user', 'user__profile')
        .order_by('-created_at')[:limit]
    ):
        profile = getattr(c.user, 'profile', None)
        name = profile.get_public_username() if profile else (c.user.email or c.user.username)
        items.append(
            TaskStackItem(
                kind='comment',
                title=_('Comment to moderate'),
                subtitle=f'{name}: {c.text[:80]}',
                url=reverse('analytics:comment_moderation'),
                created_at=c.created_at,
            )
        )

    for fb in (
        OnboardingFeedback.objects.filter(status=OnboardingFeedback.Status.PENDING)
        .select_related('user', 'user__profile', 'program')
        .order_by('-updated_at')[:limit]
    ):
        profile = getattr(fb.user, 'profile', None)
        name = profile.get_public_username() if profile else (fb.user.email or fb.user.username)
        items.append(
            TaskStackItem(
                kind='feedback',
                title=_('Onboarding feedback to moderate'),
                subtitle=f'{name} · {fb.program}',
                url=reverse('analytics:onboarding_feedback_moderation'),
                created_at=fb.updated_at,
            )
        )

    for p in (
        UserProgress.objects.filter(
            lesson__lesson_type='quiz',
            quiz_score__isnull=False,
            candidate_quiz_locked=True,
        )
        .select_related('user', 'user__profile', 'lesson', 'lesson__course')
        .order_by('-completed_at')[:limit]
    ):
        passing = effective_passing_score(p.lesson)
        score = p.quiz_score or 0
        if score >= passing:
            continue
        profile = getattr(p.user, 'profile', None)
        name = profile.get_public_username() if profile else (p.user.email or p.user.username)
        items.append(
            TaskStackItem(
                kind='quiz',
                title=_('Failed quiz — review / unlock'),
                subtitle=f'{name} · {p.lesson.localized_title} · {score}%',
                url=reverse(
                    'analytics:quiz_results_detail',
                    kwargs={'lesson_id': p.lesson_id, 'user_id': p.user_id},
                ),
                created_at=p.completed_at,
            )
        )

    items.sort(key=lambda i: i.created_at or 0, reverse=True)
    return items[:limit]


def get_hr_task_stack_counts() -> dict[str, int]:
    stack = get_hr_task_stack(limit=200)
    return {
        'total': len(stack),
        'comments': sum(1 for i in stack if i.kind == 'comment'),
        'feedback': sum(1 for i in stack if i.kind == 'feedback'),
        'quizzes': sum(1 for i in stack if i.kind == 'quiz'),
    }
