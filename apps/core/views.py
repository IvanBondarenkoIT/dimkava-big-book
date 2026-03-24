from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_name'] = 'Alex'
        context['progress'] = 85
        context['courses'] = [
            {'slug': 'espresso-basics', 'title': 'The Art of Espresso', 'category': 'Espresso', 'progress': 65},
            {'slug': 'v60-brewing', 'title': 'V60 Precision Brewing', 'category': 'Brewing', 'progress': 20},
        ]
        return context
