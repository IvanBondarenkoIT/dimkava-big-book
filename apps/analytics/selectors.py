"""Analytics metrics selectors."""
from django.contrib.auth import get_user_model
from django.db.models import Count, F, Min, Max, Q

from apps.courses.models import Course, Lesson, UserProgress
from apps.onboarding.models import OnboardingProgress, OnboardingProgram, OnboardingStep

User = get_user_model()


def get_analytics_metrics():
    """Return HR analytics metrics."""
    metrics = {
        'active_courses': Course.objects.filter(status='published').count(),
        'onboarding_in_progress': 0,
        'onboarding_completion_rate': 0,
        'avg_onboarding_days': None,
        'course_completion_rate': 0,
        'total_users': User.objects.filter(is_superuser=False).count(),
    }

    program = OnboardingProgram.objects.first()
    if program:
        total_steps = OnboardingStep.objects.filter(module__program=program).count()
        if total_steps > 0:
            progress_by_user = (
                OnboardingProgress.objects.filter(step__module__program=program)
                .values('user_id')
                .annotate(
                    done=Count('id'),
                    first=Min('completed_at'),
                    last=Max('completed_at'),
                )
            )
            users_started = list(progress_by_user)
            users_completed = [r for r in users_started if (r['done'] or 0) >= total_steps]

            metrics['onboarding_in_progress'] = len(users_started) - len(users_completed)
            metrics['onboarding_completion_rate'] = (
                int(len(users_completed) / len(users_started) * 100) if users_started else 0
            )

            days_list = []
            for r in users_completed:
                if r['first'] and r['last']:
                    days_list.append((r['last'] - r['first']).days)
            if days_list:
                metrics['avg_onboarding_days'] = int(sum(days_list) / len(days_list))

    # Course completion: % of non-admin users who completed at least one full course
    if metrics['total_users'] > 0:
        courses = (
            Course.objects.filter(status='published')
            .annotate(
                total_lessons=Count('lessons', distinct=True),
                done_lessons=Count(
                    'lessons',
                    filter=Q(lessons__progress__is_completed=True, lessons__progress__user__is_superuser=False),
                    distinct=True,
                ),
            )
            .filter(total_lessons__gt=0)
            .values('id', 'total_lessons')
        )
        # For each user, count if any course is fully completed.
        user_course_done = (
            UserProgress.objects.filter(is_completed=True, user__is_superuser=False, lesson__course__status='published')
            .values('user_id', 'lesson__course_id')
            .annotate(done=Count('id'))
        )
        totals = {c['id']: c['total_lessons'] for c in courses}
        completed_users = set()
        for row in user_course_done:
            total = totals.get(row['lesson__course_id'])
            if total and row['done'] >= total:
                completed_users.add(row['user_id'])
        metrics['course_completion_rate'] = int(len(completed_users) / metrics['total_users'] * 100)

    return metrics
