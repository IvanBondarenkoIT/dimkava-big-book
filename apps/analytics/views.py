"""Analytics views — HR/Admin only."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from .permissions import user_can_view_analytics
from .content_review_selectors import get_content_to_review
from .selectors import get_analytics_metrics


class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metrics'] = get_analytics_metrics()
        return context


class ContentReviewView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/content_review.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stale_only = self.request.GET.get('stale_only') in ('1', 'true', 'yes')
        context.update(get_content_to_review(stale_only=stale_only))
        return context
