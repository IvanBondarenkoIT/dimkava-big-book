"""Dashboard / home context helpers (base.md §9 — where to start)."""
from django.urls import reverse


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
