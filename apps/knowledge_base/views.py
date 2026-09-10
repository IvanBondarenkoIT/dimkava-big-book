"""Knowledge base views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .selectors import get_article, get_section_with_articles, get_sections


class KnowledgeBaseHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'knowledge_base/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sections = get_sections()
        context['sections'] = [
            {'slug': s.slug, 'title': s.localized_title, 'icon': s.icon or 'folder'}
            for s in sections
        ]
        return context


class SectionView(LoginRequiredMixin, TemplateView):
    template_name = 'knowledge_base/section.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = get_section_with_articles(self.kwargs['section'])
        if not data:
            context['section_title'] = None
            context['section_slug'] = self.kwargs['section']
            context['articles'] = []
            return context
        context['section'] = data['section']
        context['section_title'] = data['section'].localized_title
        context['section_slug'] = data['section'].slug
        context['articles'] = [
            {'slug': a.slug, 'title': a.localized_title} for a in data['articles']
        ]
        return context


class ArticleView(LoginRequiredMixin, TemplateView):
    template_name = 'knowledge_base/article.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = get_article(self.kwargs['section'], self.kwargs['slug'])
        if article is None:
            from django.http import Http404
            raise Http404('Article not found')
        context['article'] = article
        context['article_title'] = article.localized_title
        context['section_slug'] = article.section.slug
        context['section_title'] = article.section.localized_title
        from apps.comments.services import comments_context_for
        context.update(comments_context_for(article, self.request.user))
        return context
