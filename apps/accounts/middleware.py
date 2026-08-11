"""Restrict candidate accounts: internal sections.

Email confirmation is optional: we send a link, but do not block learning.
"""
import json
import time
from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.utils import translation


DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / 'debug-0cafc2.log'


def _debug_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # region agent log
    payload = {
        'sessionId': '0cafc2',
        'runId': run_id,
        'hypothesisId': hypothesis_id,
        'location': location,
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000),
    }
    with DEBUG_LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(payload, ensure_ascii=False) + '\n')
    # endregion


def _is_allowed_for_candidate(path: str) -> bool:
    # Learning + minimal account endpoints only. Anything else is forbidden by default.
    allowed_prefixes = (
        '/',
        '/courses',
        '/onboarding',
        '/profile',
        '/accounts/confirm-email',
        '/accounts/email-pending',
        '/accounts/resend-verification',
        '/login',
        '/logout',
        '/password-reset',
        '/i18n',
        '/admin',  # Django admin will still enforce staff-only; keep this for predictable behavior.
    )
    allowed_exact = (
        '/favicon.ico',
    )
    if path in allowed_exact:
        return True
    for p in allowed_prefixes:
        if path == p or path.startswith(p + '/'):
            return True
    return False


class CandidateRestrictionsMiddleware:
    """Candidates: block employee-only apps (wiki/news/etc)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return self.get_response(request)
        if user.is_staff or user.is_superuser:
            return self.get_response(request)

        profile = getattr(user, 'profile', None)
        if not profile or not profile.is_candidate:
            return self.get_response(request)

        path = request.path
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        if not _is_allowed_for_candidate(path):
            raise PermissionDenied('This section is available to employees only.')

        return self.get_response(request)


class I18nDebugMiddleware:
    """Runtime diagnostics for mixed-language UI reports."""

    def __init__(self, get_response):
        self.get_response = get_response
        self._markers = [
            'Where to start',
            'Welcome back',
            'Continue Learning',
            'Course Progress',
            'Resume Lesson',
            'View all',
            'Current Streak',
            'Points',
            'Start here',
            'Recommended for You',
            'Recent Badges',
            'View All Achievements',
            "You're in the top",
            'Finish your onboarding',
            'Open onboarding',
            'Newcomer',
            'coffee',
            'dashboard',
            'menu_book',
            'person_add',
            'auto_stories',
            'feed',
            'person',
            'verified_user',
            'search',
            'notifications',
            'local_fire_department',
            'military_tech',
            'beginner',
        ]

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        language = translation.get_language() or ''
        path = request.path

        if 'text/html' not in content_type:
            return response
        if language.split('-')[0] not in ('ru', 'ka'):
            return response

        try:
            body = response.content.decode(getattr(response, 'charset', 'utf-8') or 'utf-8', errors='ignore')
        except Exception:
            body = ''

        marker_hits = [m for m in self._markers if m in body]
        _debug_log(
            run_id='pre-fix',
            hypothesis_id='H1_H2_H3_H4',
            location='apps/accounts/middleware.py:I18nDebugMiddleware.__call__',
            message='i18n response diagnostics',
            data={
                'path': path,
                'language': language,
                'cookie_language': request.COOKIES.get('django_language'),
                'content_type': content_type,
                'marker_hits': marker_hits,
                'marker_hits_count': len(marker_hits),
            },
        )
        return response
