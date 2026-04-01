"""Knowledge base selectors."""
from .models import Article, KBSection


def get_sections():
    """Return all wiki sections for home page."""
    return list(KBSection.objects.all())


def get_section_with_articles(section_slug):
    """Return section and its published articles, or None."""
    try:
        section = KBSection.objects.get(slug=section_slug)
    except KBSection.DoesNotExist:
        return None
    articles = list(section.articles.filter(status='published').order_by('title_en', 'title'))
    return {'section': section, 'articles': articles}


def get_article(section_slug, article_slug):
    """Return article by section slug and article slug, or None."""
    try:
        return Article.objects.select_related('section').get(
            section__slug=section_slug,
            slug=article_slug,
            status='published',
        )
    except Article.DoesNotExist:
        return None
