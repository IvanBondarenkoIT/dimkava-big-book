from django.views.generic import TemplateView


class OverviewView(TemplateView):
    template_name = 'onboarding/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['progress'] = 25
        context['modules'] = [
            {'slug': 'day-1', 'title': 'Day 1', 'status': 'completed', 'minutes': 30},
            {'slug': 'days-2-3', 'title': 'Days 2–3', 'status': 'in_progress', 'minutes': 120},
            {'slug': 'week-1', 'title': 'Week 1', 'status': 'not_started', 'minutes': 240},
            {'slug': 'week-2', 'title': 'Week 2', 'status': 'not_started', 'minutes': 300},
        ]
        return context


class ModuleDetailView(TemplateView):
    template_name = 'onboarding/module_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_slug'] = self.kwargs.get('slug', 'day-1')
        context['module_title'] = 'Day 1 — Getting Started'
        return context
