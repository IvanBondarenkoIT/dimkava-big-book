"""Course selectors — for views."""
from .models import Course, Lesson, UserProgress


def get_courses_for_user(user):
    """List courses with progress for user."""
    courses = Course.objects.filter(status='published').prefetch_related('lessons')
    result = []
    for c in courses:
        total = c.lessons.count()
        done = UserProgress.objects.filter(user=user, lesson__course=c, is_completed=True).count()
        progress = int((done / total * 100)) if total else 0
        result.append({
            'slug': c.slug,
            'title': c.title,
            'description': c.description,
            'level': c.level,
            'category': c.level,
            'lessons_count': total,
            'progress': progress,
            'image': c.image or '',
        })
    return result


def get_course_detail(course_slug, user):
    """Course with lessons and completion status."""
    course = Course.objects.filter(slug=course_slug, status='published').first()
    if not course:
        return None
    lessons = []
    for l in course.lessons.all().order_by('order'):
        prog = UserProgress.objects.filter(user=user, lesson=l).first()
        lessons.append({
            'id': l.id,
            'title': l.title,
            'lesson_type': l.lesson_type,
            'estimated_minutes': l.estimated_minutes,
            'completed': prog.is_completed if prog else False,
            'quiz_score': prog.quiz_score if prog else None,
        })
    return {'course': course, 'lessons': lessons}


def get_lesson_for_user(course_slug, lesson_id, user):
    """Lesson with completion status."""
    course = Course.objects.filter(slug=course_slug, status='published').first()
    if not course:
        return None
    lesson = course.lessons.filter(pk=lesson_id).first()
    if not lesson:
        return None
    prog = UserProgress.objects.filter(user=user, lesson=lesson).first()
    return {
        'course': course,
        'lesson': lesson,
        'completed': prog.is_completed if prog else False,
    }
