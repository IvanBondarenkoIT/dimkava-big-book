from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.courses.selectors import get_active_ilp_context_for_user


class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_name'] = user.get_full_name() or user.username
        context['role'] = _get_role_display(user)
        context['ilp'] = get_active_ilp_context_for_user(user)
        return context


def _get_role_display(user):
    """Display role from groups (employee, hr_manager, admin)."""
    if user.is_superuser:
        return 'Admin'
    if user.groups.filter(name='hr_manager').exists():
        return 'HR / Director'
    if user.groups.filter(name='employee').exists():
        return 'Employee'
    return 'User'
