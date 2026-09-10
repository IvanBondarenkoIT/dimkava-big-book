"""HR-focused selectors for site UI (not Django admin)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateRow:
    profile_id: int
    user_id: int
    public_username: str
    email: str
    phone: str
    email_verified_at: object
    assigned_onboarding_program: object
    onboarding_progress_pct: int
    last_login: object


def get_candidate_rows():
    from django.contrib.auth import get_user_model

    from apps.accounts.models import UserProfile
    from apps.onboarding.selectors import get_onboarding_overview_for_user

    User = get_user_model()
    profiles = (
        UserProfile.objects.filter(user_type='candidate')
        .select_related('user', 'assigned_onboarding_program')
        .order_by('-user__date_joined')
    )

    rows: list[CandidateRow] = []
    for p in profiles:
        # Keep it simple: selector already exists; N+1 is OK for small HR lists.
        _program, _modules, progress, _mentor, _feedback = get_onboarding_overview_for_user(p.user)
        rows.append(
            CandidateRow(
                profile_id=p.pk,
                user_id=p.user_id,
                public_username=p.get_public_username(),
                email=p.user.email or p.user.username,
                phone=p.phone,
                email_verified_at=p.email_verified_at,
                assigned_onboarding_program=p.assigned_onboarding_program,
                onboarding_progress_pct=progress,
                last_login=p.user.last_login,
            )
        )
    return rows


def _display_name(user) -> str:
    profile = getattr(user, 'profile', None)
    if profile:
        return profile.get_public_username()
    return user.email or user.username


def _passing_score(lesson) -> int:
    from apps.courses.quiz_review import effective_passing_score

    return effective_passing_score(lesson)


@dataclass(frozen=True)
class QuizCatalogRow:
    lesson_id: int
    course_title: str
    lesson_title: str
    passing_score: int
    attempted: int
    passed: int
    failed: int
    locked: int


@dataclass(frozen=True)
class QuizTakerRow:
    user_id: int
    display_name: str
    email: str
    is_candidate: bool
    quiz_score: int
    passed: bool
    attempts: int
    locked: bool
    completed_at: object


def get_quiz_catalog_rows(*, q: str = '') -> list[QuizCatalogRow]:
    from django.db.models import Q

    from apps.courses.models import Lesson, UserProgress

    lessons = (
        Lesson.objects.filter(lesson_type='quiz')
        .select_related('course')
        .order_by('course__title', 'order', 'id')
    )
    needle = (q or '').strip()
    if needle:
        lessons = lessons.filter(
            Q(title__icontains=needle)
            | Q(title_en__icontains=needle)
            | Q(title_ru__icontains=needle)
            | Q(title_ka__icontains=needle)
            | Q(course__title__icontains=needle)
        )

    rows: list[QuizCatalogRow] = []
    for lesson in lessons:
        passing = _passing_score(lesson)
        progress = UserProgress.objects.filter(lesson=lesson, quiz_score__isnull=False)
        attempted = progress.count()
        passed = progress.filter(quiz_score__gte=passing).count()
        rows.append(
            QuizCatalogRow(
                lesson_id=lesson.pk,
                course_title=lesson.course.localized_title,
                lesson_title=lesson.localized_title,
                passing_score=passing,
                attempted=attempted,
                passed=passed,
                failed=attempted - passed,
                locked=progress.filter(candidate_quiz_locked=True).count(),
            )
        )
    return rows


def get_quiz_taker_rows(
    lesson,
    *,
    candidates_only: bool = False,
    failed_only: bool = False,
    locked_only: bool = False,
) -> list[QuizTakerRow]:
    from apps.courses.models import UserProgress

    passing = _passing_score(lesson)
    qs = (
        UserProgress.objects.filter(lesson=lesson, quiz_score__isnull=False)
        .select_related('user', 'user__profile')
    )
    if candidates_only:
        qs = qs.filter(user__profile__user_type='candidate')
    if locked_only:
        qs = qs.filter(candidate_quiz_locked=True)

    rows: list[QuizTakerRow] = []
    for p in qs:
        score = p.quiz_score or 0
        passed = score >= passing
        if failed_only and passed:
            continue
        profile = getattr(p.user, 'profile', None)
        rows.append(
            QuizTakerRow(
                user_id=p.user_id,
                display_name=_display_name(p.user),
                email=p.user.email or p.user.username,
                is_candidate=bool(profile and profile.is_candidate),
                quiz_score=score,
                passed=passed,
                attempts=p.quiz_attempts_count or 0,
                locked=bool(p.candidate_quiz_locked),
                completed_at=p.completed_at,
            )
        )
    rows.sort(key=lambda r: (r.passed, not r.locked, r.display_name.lower()))
    return rows

