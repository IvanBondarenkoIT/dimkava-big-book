"""Departments views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .selectors import get_department_detail, get_departments


class DepartmentListView(LoginRequiredMixin, TemplateView):
    template_name = 'departments/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = [
            {'slug': d.slug, 'name': d.name, 'role_count': d.roles.count()}
            for d in get_departments()
        ]
        return context


class DepartmentDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'departments/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = get_department_detail(self.kwargs['slug'])
        if not data:
            context['department'] = None
            context['department_name'] = self.kwargs['slug']
            context['roles'] = []
            return context
        context['department'] = data['department']
        context['department_name'] = data['department'].name
        context['roles'] = data['roles']
        return context
