"""Global search across courses, articles, news, roles."""
from dataclasses import dataclass

from apps.core.i18n_content import obj_matches_i18n_text, obj_matches_plain_text
from apps.courses.models import Course, Lesson
from apps.departments.models import Role
from apps.knowledge_base.models import Article
from apps.news.models import NewsPost

_SEARCH_LIMIT = 10


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


def _localized_title(obj) -> str:
    if hasattr(obj, 'localized_title'):
        return obj.localized_title or obj.title
    return getattr(obj, 'title', '')


def _localized_snippet(obj, content_attr: str = 'content') -> str:
    localized = f'localized_{content_attr}'
    if hasattr(obj, localized):
        text = getattr(obj, localized) or ''
    else:
        text = getattr(obj, content_attr, '') or ''
    if not text and content_attr == 'description' and hasattr(obj, 'localized_description'):
        text = obj.localized_description or ''
    return _excerpt(text or _localized_title(obj))


def _take_matching(qs, base_names: tuple[str, ...], query: str, limit: int):
    """Yield up to `limit` objects matching query (case-insensitive, all locales)."""
    n = 0
    for obj in qs:
        if obj_matches_i18n_text(obj, base_names, query):
            yield obj
            n += 1
            if n >= limit:
                return


# TODO: Replace with PostgreSQL full-text search for better performance at scale.
def global_search(query: str, user) -> list[SearchResult]:
    """
    Search across courses, lessons, articles, news, roles.
    Case-insensitive for all languages (including Cyrillic on SQLite).
    """
    if not query or not query.strip():
        return []

    q = query.strip()
    results: list[SearchResult] = []
    profile = getattr(user, 'profile', None)
    is_candidate = bool(profile and getattr(profile, 'is_candidate', False))

    course_qs = Course.objects.filter(status="published")
    if is_candidate:
        course_qs = course_qs.filter(visible_for_candidates=True)
    for obj in _take_matching(course_qs, ('title', 'description'), q, _SEARCH_LIMIT):
        results.append(
            SearchResult(
                type="course",
                title=_localized_title(obj),
                url=f"/courses/{obj.slug}/",
                snippet=_localized_snippet(obj, 'description'),
                department="",
                tags=[obj.level] if obj.level else [],
            )
        )

    lesson_qs = (
        Lesson.objects.select_related("course")
        .filter(course__status="published")
    )
    if is_candidate:
        lesson_qs = lesson_qs.filter(visible_for_candidates=True, course__visible_for_candidates=True)
    for lesson in _take_matching(lesson_qs, ('title', 'content'), q, _SEARCH_LIMIT):
        results.append(
            SearchResult(
                type="lesson",
                title=f"{lesson.course.localized_title} — {lesson.localized_title}",
                url=f"/courses/{lesson.course.slug}/lessons/{lesson.pk}/",
                snippet=_localized_snippet(lesson),
                department="",
                tags=[lesson.lesson_type] if lesson.lesson_type else [],
            )
        )

    if not is_candidate:
        article_qs = Article.objects.filter(status="published").select_related("section")
        for obj in _take_matching(article_qs, ('title', 'content'), q, _SEARCH_LIMIT):
            results.append(
                SearchResult(
                    type="article",
                    title=_localized_title(obj),
                    url=f"/wiki/{obj.section.slug}/{obj.slug}/",
                    snippet=_localized_snippet(obj),
                    department="",
                    tags=[obj.section.title] if obj.section else [],
                )
            )

        news_qs = NewsPost.objects.all()
        for obj in _take_matching(news_qs, ('title', 'content'), q, _SEARCH_LIMIT):
            results.append(
                SearchResult(
                    type="news",
                    title=_localized_title(obj),
                    url=f"/news/{obj.slug}/",
                    snippet=_localized_snippet(obj),
                    department="",
                    tags=[obj.tag] if obj.tag else [],
                )
            )

        role_n = 0
        for obj in Role.objects.select_related("department"):
            if obj_matches_plain_text(obj, ('title', 'description'), q):
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
                role_n += 1
                if role_n >= _SEARCH_LIMIT:
                    break

    return results
