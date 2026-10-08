from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from apps.courses.selectors import get_courses_for_user

from .selectors import get_home_achievement_snapshot, get_where_to_start_hint


def _safe_redirect_url(request, next_url: str) -> str:
    """Allow only relative same-site paths (block open redirects)."""
    candidate = (next_url or '').strip() or '/'
    if candidate.startswith('//'):
        return '/'
    if url_has_allowed_host_and_scheme(
        url=candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    if candidate.startswith('/') and not candidate.startswith('//'):
        return candidate
    return '/'


def set_language(request):
    """
    GET language switch (allowlisted codes only).
    Avoids CSRF failures on the language selector after HTTPS cutover.
    """
    lang_code = (request.GET.get('language') or '').strip()
    next_url = _safe_redirect_url(request, request.GET.get('next') or '/')
    allowed = {code for code, _name in settings.LANGUAGES}

    response = HttpResponseRedirect(next_url)
    if lang_code in allowed:
        translation.activate(lang_code)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=getattr(settings, 'LANGUAGE_COOKIE_AGE', 60 * 60 * 24 * 365),
            path=getattr(settings, 'LANGUAGE_COOKIE_PATH', '/'),
            domain=getattr(settings, 'LANGUAGE_COOKIE_DOMAIN', None),
            secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
            httponly=getattr(settings, 'LANGUAGE_COOKIE_HTTPONLY', False),
            samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', 'Lax'),
        )
    return response


def csrf_failure(request, reason=''):
    """Friendly page instead of raw Django 403 CSRF HTML."""
    referer = request.META.get('HTTP_REFERER') or '/'
    return render(
        request,
        'core/csrf_failure.html',
        {
            'reason': reason,
            'next_url': _safe_redirect_url(request, referer),
        },
        status=403,
    )


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
