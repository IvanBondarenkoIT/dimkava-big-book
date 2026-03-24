from django.views.generic import TemplateView


class NewsListView(TemplateView):
    template_name = 'news/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news'] = [
            {'slug': 'welcome-2024', 'title': 'Welcome to 2024!', 'date': 'Jan 15, 2024', 'tag': 'general', 'pinned': True},
            {'slug': 'new-course', 'title': 'New Course: Latte Art Basics', 'date': 'Jan 10, 2024', 'tag': 'training', 'pinned': False},
        ]
        return context


class NewsDetailView(TemplateView):
    template_name = 'news/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_title'] = 'Welcome to 2024!'
        context['news_date'] = 'Jan 15, 2024'
        return context
