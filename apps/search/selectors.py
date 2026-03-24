"""Global search across courses, articles, news, roles."""
from dataclasses import dataclass

from django.db.models import Q

from apps.courses.models import Course, Lesson
from apps.departments.models import Role
from apps.knowledge_base.models import Article
from apps.news.models import NewsPost


@dataclass
class SearchResult:
    type: str  # "course", "lesson", "article", "news", "role"
    title: str
    url: str
    snippet: str  # Short excerpt (max 150 chars)
    department: str  # Optional, for filtering
    tags: list[str]


def _excerpt(text: str, max_len: int = 150) -> str:
    """Return truncated text with ... if needed."""
    if not text:
        return ""
    text = " ".join(text.split())
    return (text[: max_len - 3] + "...") if len(text) > max_len else text


# TODO: Replace with PostgreSQL full-text search for better performance at scale.
def global_search(query: str, user) -> list[SearchResult]:
    """
    Search across courses, lessons, articles, news, roles.
    Uses icontains for now; replace with full-text search in production.
    """
    if not query or not query.strip():
        return []

    q = query.strip()
    results: list[SearchResult] = []
    q_obj = Q(title__icontains=q) | Q(description__icontains=q)

    # Courses (published only)
    for obj in Course.objects.filter(q_obj, status="published").select_related()[:10]:
        results.append(
            SearchResult(
                type="course",
                title=obj.title,
                url=f"/courses/{obj.slug}/",
                snippet=_excerpt(obj.description or obj.title),
                department="",
                tags=[obj.level] if obj.level else [],
            )
        )

    # Lessons (within published courses)
    lesson_q = Q(title__icontains=q) | Q(content__icontains=q)
    for lesson in (
        Lesson.objects.filter(lesson_q)
        .select_related("course")
        .filter(course__status="published")[:10]
    ):
        results.append(
            SearchResult(
                type="lesson",
                title=f"{lesson.course.title} — {lesson.title}",
                url=f"/courses/{lesson.course.slug}/lessons/{lesson.pk}/",
                snippet=_excerpt(lesson.content or lesson.title),
                department="",
                tags=[lesson.lesson_type] if lesson.lesson_type else [],
            )
        )

    # Articles (published only)
    article_q = Q(title__icontains=q) | Q(content__icontains=q)
    for obj in (
        Article.objects.filter(article_q, status="published")
        .select_related("section")[:10]
    ):
        results.append(
            SearchResult(
                type="article",
                title=obj.title,
                url=f"/wiki/{obj.section.slug}/{obj.slug}/",
                snippet=_excerpt(obj.content or obj.title),
                department="",
                tags=[obj.section.title] if obj.section else [],
            )
        )

    # News
    news_q = Q(title__icontains=q) | Q(content__icontains=q)
    for obj in NewsPost.objects.filter(news_q)[:10]:
        results.append(
            SearchResult(
                type="news",
                title=obj.title,
                url=f"/news/{obj.slug}/",
                snippet=_excerpt(obj.content or obj.title),
                department="",
                tags=[obj.tag] if obj.tag else [],
            )
        )

    # Roles (title, description)
    role_q = Q(title__icontains=q) | Q(description__icontains=q)
    for obj in Role.objects.filter(role_q).select_related("department")[:10]:
        results.append(
            SearchResult(
                type="role",
                title=obj.title,
                url=f"/departments/{obj.department.slug}/",
                snippet=_excerpt(obj.description or obj.title),
                department=obj.department.name if obj.department else "",
                tags=[],
            )
        )

    return results
