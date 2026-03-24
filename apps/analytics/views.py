from django.views.generic import TemplateView


class AnalyticsDashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metrics'] = {
            'active_courses': 12,
            'onboarding_in_progress': 5,
            'completion_rate': 78,
        }
        return context
