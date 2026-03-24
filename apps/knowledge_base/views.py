from django.views.generic import TemplateView


class KnowledgeBaseHomeView(TemplateView):
    template_name = 'knowledge_base/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = [
            {'slug': 'procedures', 'title': 'Procedures & Checklists', 'icon': 'checklist'},
            {'slug': 'service-standards', 'title': 'Service Standards', 'icon': 'star'},
            {'slug': 'company-info', 'title': 'Company Information', 'icon': 'building'},
            {'slug': 'training', 'title': 'Training & Qualification', 'icon': 'graduation-cap'},
        ]
        return context


class SectionView(TemplateView):
    template_name = 'knowledge_base/section.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_slug'] = self.kwargs.get('section', 'procedures')
        context['section_title'] = 'Procedures & Checklists'
        context['articles'] = [
            {'slug': 'daily-checklist', 'title': 'Daily Checklist — Morning to Close'},
            {'slug': 'weekly-checklist', 'title': 'Weekly Checklist'},
        ]
        return context


class ArticleView(TemplateView):
    template_name = 'knowledge_base/article.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article_title'] = 'Daily Checklist — Morning to Close'
        return context
