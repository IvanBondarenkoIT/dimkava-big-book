from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .selectors import get_gamification_dashboard_context, get_leaderboard


class GamificationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gamification/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_gamification_dashboard_context(self.request.user))
        return ctx


class LeaderboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gamification/leaderboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_leaderboard(top_n=10, current_user=self.request.user))
        return ctx
