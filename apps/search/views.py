from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .selectors import global_search


class SearchResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'search/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = (self.request.GET.get('q') or '').strip()
        context['query'] = query
        type_filter = self.request.GET.get('type', 'all')
        context['type_filter'] = type_filter
        results = global_search(query, self.request.user) if query else []
        if type_filter != 'all':
            results = [r for r in results if r.type == type_filter]
        context['results'] = results
        context['filter_chips'] = [
            ('all', 'All'),
            ('course', 'Courses'),
            ('lesson', 'Lessons'),
            ('article', 'Articles'),
            ('news', 'News'),
            ('role', 'Roles'),
        ]
        return context
