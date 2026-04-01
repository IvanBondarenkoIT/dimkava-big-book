"""Profile dashboard selectors (metrics + progress + badges)."""
from django.db.models import Count, F, Q, Sum
from django.utils.translation import gettext_lazy as _


def _courses_queryset_for_user(user):
    from apps.courses.models import Course

    qs = Course.objects.filter(status='published')
    profile = getattr(user, 'profile', None)
    if profile and profile.is_candidate:
        qs = qs.filter(visible_for_candidates=True)
    return qs


def get_profile_dashboard_context(user) -> dict:
    from apps.courses.models import Lesson
    from apps.gamification.models import GamificationProfile, UserBadge

    courses_qs = _courses_queryset_for_user(user)

    # Course is done only when all required lessons are completed.
    completed_courses = (
        courses_qs.annotate(
            required_total=Count('lessons', filter=Q(lessons__is_required=True), distinct=True),
            required_done=Count(
                'lessons',
                filter=Q(lessons__is_required=True, lessons__progress__user=user, lessons__progress__is_completed=True),
                distinct=True,
            ),
        )
        .filter(required_total__gt=0, required_done__gte=F('required_total'))
        .count()
    )

    lessons_qs = Lesson.objects.filter(progress__user=user, progress__is_completed=True).distinct()
    profile = getattr(user, 'profile', None)
    if profile and profile.is_candidate:
        lessons_qs = lessons_qs.filter(visible_for_candidates=True, course__visible_for_candidates=True)

    total_minutes = lessons_qs.aggregate(v=Sum('estimated_minutes'))['v'] or 0
    hours_spent = round(total_minutes / 60.0)

    gp = GamificationProfile.objects.filter(user=user).first()
    total_points = gp.total_points if gp else 0
    skill_level = min(10.0, round(total_points / 100.0, 1))

    certificates_count = UserBadge.objects.filter(user=user, badge__is_compliance=True).count()

    levels = ['beginner', 'intermediate', 'manager']
    level_titles = {
        'beginner': _('Beginner track'),
        'intermediate': _('Intermediate track'),
        'manager': _('Manager track'),
    }
    certification_progress = []
    for level in levels:
        level_courses = courses_qs.filter(level=level)
        total = level_courses.count()
        done = (
            level_courses.annotate(
                required_total=Count('lessons', filter=Q(lessons__is_required=True), distinct=True),
                required_done=Count(
                    'lessons',
                    filter=Q(lessons__is_required=True, lessons__progress__user=user, lessons__progress__is_completed=True),
                    distinct=True,
                ),
            )
            .filter(required_total__gt=0, required_done__gte=F('required_total'))
            .count()
        )
        pct = int((done / total) * 100) if total else 0
        certification_progress.append(
            {
                'level': level,
                'title': level_titles[level],
                'completed': done,
                'total': total,
                'progress_pct': pct,
            }
        )

    badge_showcase = list(
        UserBadge.objects.filter(user=user)
        .select_related('badge')
        .order_by('-awarded_at')[:8]
    )

    return {
        'courses_done': completed_courses,
        'hours_spent': hours_spent,
        'skill_level': skill_level,
        'certificates_count': certificates_count,
        'certification_progress': certification_progress,
        'badge_showcase': badge_showcase,
    }

