"""Dashboard / home context helpers (base.md §9 — where to start)."""
import math
from datetime import timedelta

from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone


def get_where_to_start_hint(user):
    """
    One primary CTA: onboarding first if incomplete, else in-progress course, else catalog.
    """
    from apps.courses.selectors import get_courses_for_user
    from apps.onboarding.selectors import get_onboarding_overview_for_user

    program, _modules, progress_pct, _mentor_block, _feedback_block = get_onboarding_overview_for_user(user)
    if program and progress_pct < 100:
        return {
            'show': True,
            'title': 'Start here',
            'body': 'Finish your onboarding track before moving to courses.',
            'url': reverse('onboarding:overview'),
            'cta': 'Open onboarding',
            'variant': 'primary',
        }

    courses = get_courses_for_user(user)
    for c in courses:
        prog = c.get('progress') or 0
        if 0 < prog < 100:
            return {
                'show': True,
                'title': 'Next step',
                'body': f'Continue where you left off: {c["title"]}.',
                'url': reverse('courses:detail', kwargs={'slug': c['slug']}),
                'cta': 'Resume course',
                'variant': 'primary',
            }

    if courses:
        return {
            'show': True,
            'title': 'Explore courses',
            'body': 'Pick a course from the catalog to build your skills.',
            'url': reverse('courses:list'),
            'cta': 'Browse catalog',
            'variant': 'secondary',
        }

    return {'show': False}


def get_home_achievement_snapshot(user):
    """
    Profile-like snapshot for home dashboard:
    - role_title (gamification level name)
    - current_streak (consecutive active days)
    - total_points
    - top_percentile_this_week
    """
    from apps.courses.models import UserProgress
    from apps.gamification.models import PointsLog
    from apps.gamification.services import get_level_progress, get_or_create_profile
    from apps.onboarding.models import OnboardingProgress

    gp = get_or_create_profile(user)
    total_points = gp.total_points
    role_title = get_level_progress(total_points).get('level_name', 'Learner')

    # Activity streak from completed learning + points logs.
    activity_dates = set(
        d for d in UserProgress.objects.filter(user=user, is_completed=True, completed_at__isnull=False).values_list('completed_at__date', flat=True) if d
    )
    activity_dates.update(
        d for d in OnboardingProgress.objects.filter(user=user).values_list('completed_at__date', flat=True) if d
    )
    activity_dates.update(
        d for d in PointsLog.objects.filter(user=user).values_list('created_at__date', flat=True) if d
    )

    today = timezone.localdate()
    streak = 0
    day = today
    while day in activity_dates:
        streak += 1
        day = day - timedelta(days=1)

    # Weekly percentile by points gained this week.
    start_of_week = today - timedelta(days=today.weekday())
    weekly_points_qs = (
        PointsLog.objects.filter(created_at__date__gte=start_of_week)
        .values('user_id')
        .annotate(total=Sum('points'))
        .order_by('-total', 'user_id')
    )
    weekly = list(weekly_points_qs)
    if not weekly:
        top_percentile = 100
        weekly_rank = 1
        weekly_learners = 1
    else:
        totals = {row['user_id']: row['total'] or 0 for row in weekly}
        current_total = totals.get(user.id, 0)
        weekly_rank = 1 + sum(1 for t in totals.values() if t > current_total)
        weekly_learners = len(weekly)
        top_percentile = max(1, min(100, int(math.ceil(weekly_rank / weekly_learners * 100))))

    return {
        'role_title': role_title,
        'current_streak_days': streak,
        'total_points': total_points,
        'top_percentile_this_week': top_percentile,
        'weekly_rank': weekly_rank,
        'weekly_learners': weekly_learners,
    }
