"""Analytics metrics selectors."""
from django.contrib.auth import get_user_model
from django.db.models import Count, Min, Max

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
            users_started = set(
                OnboardingProgress.objects.filter(step__module__program=program)
                .values_list('user_id', flat=True)
                .distinct()
            )
            users_completed = []
            for uid in users_started:
                done = OnboardingProgress.objects.filter(
                    user_id=uid, step__module__program=program
                ).count()
                if done >= total_steps:
                    users_completed.append(uid)

            metrics['onboarding_in_progress'] = len(users_started) - len(users_completed)
            metrics['onboarding_completion_rate'] = (
                int(len(users_completed) / len(users_started) * 100) if users_started else 0
            )

            # Avg days to complete (first step -> last step)
            days_list = []
            for uid in users_completed:
                agg = OnboardingProgress.objects.filter(
                    user_id=uid, step__module__program=program
                ).aggregate(first=Min('completed_at'), last=Max('completed_at'))
                if agg['first'] and agg['last']:
                    days_list.append((agg['last'] - agg['first']).days)
            if days_list:
                metrics['avg_onboarding_days'] = int(sum(days_list) / len(days_list))

    # Course completion: % of non-admin users who completed at least one full course
    if metrics['total_users'] > 0:
        courses = list(Course.objects.filter(status='published').prefetch_related('lessons'))
        completed_any = 0
        for u in User.objects.filter(is_superuser=False):
            for c in courses:
                total = c.lessons.count()
                if total and UserProgress.objects.filter(
                    user=u, lesson__course=c, is_completed=True
                ).count() >= total:
                    completed_any += 1
                    break
        metrics['course_completion_rate'] = int(completed_any / metrics['total_users'] * 100)

    return metrics
