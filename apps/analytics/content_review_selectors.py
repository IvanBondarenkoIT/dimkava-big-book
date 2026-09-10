"""Selectors for HR content review dashboard."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewItem:
    kind: str  # 'course' | 'article'
    title: str
    status: str
    is_stale: bool
    updated_at: object
    responsible_editor: object
    edit_url: str
    admin_url: str
    view_url: str


def get_content_to_review(*, stale_only: bool = False):
    """
    Returns dict with lists for template.
    Items included when:
      - stale_only=True: only is_stale
      - else: is_stale OR status indicates review/draft (course: review, article: draft)
    """
    from django.urls import reverse
    from django.utils import timezone

    from apps.courses.models import Course
    from apps.knowledge_base.models import Article

    def want_course(c: Course) -> bool:
        if stale_only:
            return bool(c.is_stale)
        return bool(c.is_stale or c.status == 'review')

    def want_article(a: Article) -> bool:
        if stale_only:
            return bool(a.is_stale)
        return bool(a.is_stale or a.status == 'draft')

    courses = [c for c in Course.objects.all().select_related('responsible_editor') if want_course(c)]
    articles = [a for a in Article.objects.all().select_related('responsible_editor', 'section') if want_article(a)]

    def course_item(c: Course) -> ReviewItem:
        return ReviewItem(
            kind='course',
            title=c.title,
            status=c.status,
            is_stale=bool(c.is_stale),
            updated_at=c.updated_at,
            responsible_editor=c.responsible_editor,
            edit_url=reverse('content_editor:course_edit', kwargs={'slug': c.slug}),
            admin_url=reverse('admin:courses_course_change', args=[c.pk]),
            view_url=reverse('courses:detail', kwargs={'slug': c.slug}),
        )

    def article_item(a: Article) -> ReviewItem:
        return ReviewItem(
            kind='article',
            title=a.title,
            status=a.status,
            is_stale=bool(a.is_stale),
            updated_at=a.updated_at,
            responsible_editor=a.responsible_editor,
            edit_url=reverse(
                'content_editor:article_edit',
                kwargs={'section': a.section.slug, 'slug': a.slug},
            ),
            admin_url=reverse('admin:knowledge_base_article_change', args=[a.pk]),
            view_url=reverse('knowledge_base:article', kwargs={'section': a.section.slug, 'slug': a.slug}),
        )

    items = [*map(course_item, courses), *map(article_item, articles)]
    items.sort(key=lambda x: (0 if x.is_stale else 1, x.updated_at or timezone.now()))

    return {
        'items': items,
        'counts': {
            'total': len(items),
            'stale': sum(1 for i in items if i.is_stale),
            'courses': sum(1 for i in items if i.kind == 'course'),
            'articles': sum(1 for i in items if i.kind == 'article'),
        },
        'stale_only': stale_only,
    }
