"""Course selectors — for views."""
from django.utils.translation import gettext as _

from .models import Course, IndividualLearningPlan, Lesson, LessonRating, UserProgress


def _course_level_label(level: str) -> str:
    return {
        'beginner': _('Beginner'),
        'intermediate': _('Intermediate'),
        'manager': _('Manager'),
    }.get(level, level)


def get_courses_for_user(user):
    """List courses with progress for user.

    If AssignmentRule left pending_course_slugs on the profile, restrict the
    catalog to those published courses (assigned enrollment path).
    """
    courses = Course.objects.filter(status='published')
    profile = getattr(user, 'profile', None)
    if profile and profile.is_candidate:
        courses = courses.filter(visible_for_candidates=True)
    assigned = list(getattr(profile, 'pending_course_slugs', None) or []) if profile else []
    if assigned:
        courses = courses.filter(slug__in=assigned)
    courses = courses.prefetch_related('lessons')
    result = []
    for c in courses:
        total = c.lessons.count()
        done = UserProgress.objects.filter(user=user, lesson__course=c, is_completed=True).count()
        progress = int((done / total * 100)) if total else 0
        result.append({
            'slug': c.slug,
            'title': c.localized_title,
            'description': c.localized_description,
            'level': c.level,
            'category': c.level,
            'category_label': _course_level_label(c.level),
            'lessons_count': total,
            'progress': progress,
            'image': c.image or '',
        })
    return result


def get_course_detail(course_slug, user):
    """Course with lessons and completion status."""
    qs = Course.objects.filter(slug=course_slug, status='published')
    profile = getattr(user, 'profile', None)
    if profile and profile.is_candidate:
        qs = qs.filter(visible_for_candidates=True)
    assigned = list(getattr(profile, 'pending_course_slugs', None) or []) if profile else []
    if assigned and course_slug not in assigned:
        return None
    course = qs.first()
    if not course:
        return None
    lessons = []
    lesson_qs = course.lessons.all().order_by('order')
    if profile and profile.is_candidate:
        lesson_qs = lesson_qs.filter(visible_for_candidates=True)
    for l in lesson_qs:
        prog = UserProgress.objects.filter(user=user, lesson=l).first()
        lessons.append({
            'id': l.id,
            'title': l.localized_title,
            'lesson_type': l.lesson_type,
            'estimated_minutes': l.estimated_minutes,
            'completed': prog.is_completed if prog else False,
            'quiz_score': prog.quiz_score if prog else None,
        })
    return {'course': course, 'lessons': lessons}


def get_lesson_for_user(course_slug, lesson_id, user):
    """Lesson with completion status."""
    qs = Course.objects.filter(slug=course_slug, status='published')
    profile = getattr(user, 'profile', None)
    if profile and profile.is_candidate:
        qs = qs.filter(visible_for_candidates=True)
    assigned = list(getattr(profile, 'pending_course_slugs', None) or []) if profile else []
    if assigned and course_slug not in assigned:
        return None
    course = qs.first()
    if not course:
        return None
    lesson_qs = course.lessons.filter(pk=lesson_id)
    if profile and profile.is_candidate:
        lesson_qs = lesson_qs.filter(visible_for_candidates=True)
    lesson = lesson_qs.first()
    if not lesson:
        return None
    prog = UserProgress.objects.filter(user=user, lesson=lesson).first()
    rating = LessonRating.objects.filter(user=user, lesson=lesson).first()
    return {
        'course': course,
        'lesson': lesson,
        'completed': prog.is_completed if prog else False,
        'rating': rating.rating if rating else None,
        'rating_comment': rating.comment if rating else '',
    }


def get_active_ilp_context_for_user(user):
    """
    Minimal ILP context for profile page.
    Returns {'has_plan': bool, ...}.
    """
    plan = (
        IndividualLearningPlan.objects.filter(user=user, is_active=True)
        .prefetch_related('items')
        .order_by('-created_at', 'id')
        .first()
    )
    if not plan:
        return {'has_plan': False}

    items = list(
        plan.items.all().order_by('order', 'id').values(
            'id',
            'title',
            'content_type',
            'object_slug',
            'is_required',
            'deadline',
            'is_completed',
            'order',
        )
    )
    total = len(items)
    completed = sum(1 for i in items if i['is_completed'])
    progress = int((completed / total) * 100) if total else 0
    next_up = next((i for i in items if not i['is_completed']), None)

    return {
        'has_plan': True,
        'title': plan.title,
        'deadline': plan.deadline,
        'progress': progress,
        'total_items': total,
        'completed_items': completed,
        'next_up': next_up,
        'items': items,
    }
