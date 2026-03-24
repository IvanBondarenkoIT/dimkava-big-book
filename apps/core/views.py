from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.courses.selectors import get_courses_for_user


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = get_courses_for_user(self.request.user)
        context['courses'] = courses
        active = next((c for c in courses if 0 < c['progress'] < 100), courses[0] if courses else None)
        context['active_course'] = active or {'slug': '', 'title': 'No courses', 'category': '', 'progress': 0, 'image': ''}
        context['achievements'] = []
        return context
