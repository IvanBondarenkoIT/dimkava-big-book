from django.views.generic import TemplateView


class SearchResultsView(TemplateView):
    template_name = 'search/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['results'] = []  # Dummy empty
        return context
