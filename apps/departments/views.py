from django.views.generic import TemplateView


class DepartmentListView(TemplateView):
    template_name = 'departments/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = [
            {'slug': 'retail-store', 'name': 'Retail Store'},
            {'slug': 'marketing', 'name': 'Marketing'},
            {'slug': 'it', 'name': 'IT'},
        ]
        return context


class DepartmentDetailView(TemplateView):
    template_name = 'departments/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department_name'] = 'Retail Store'
        context['roles'] = [
            {'title': 'Manager Consultant', 'description': 'Front-line sales and service.'},
        ]
        return context
