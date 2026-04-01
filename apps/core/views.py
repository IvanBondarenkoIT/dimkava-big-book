from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from apps.courses.selectors import get_courses_for_user

from .selectors import get_home_achievement_snapshot, get_where_to_start_hint


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        courses = get_courses_for_user(user)
        context['courses'] = courses
        active = next((c for c in courses if 0 < c['progress'] < 100), courses[0] if courses else None)
        context['active_course'] = active or {
            'slug': '',
            'title': _('No courses'),
            'category': '',
            'category_label': '',
            'progress': 0,
            'image': '',
        }
        context['achievements'] = []
        context['where_to_start'] = get_where_to_start_hint(user)
        context['home_snapshot'] = get_home_achievement_snapshot(user)
        return context
