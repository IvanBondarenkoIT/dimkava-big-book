"""Restrict candidate accounts: internal sections.

Email confirmation is optional: we send a link, but do not block learning.
"""
from django.core.exceptions import PermissionDenied


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
        '/comments',
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
