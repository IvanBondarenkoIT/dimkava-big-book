"""Template helpers for candidate UI."""


def candidate_ui(request):
    """
    candidate_ui is None (full UI), 'unverified' (email not confirmed), or 'verified' (candidate, confirmed).
    """
    if not request.user.is_authenticated:
        return {'candidate_ui': None}
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.is_candidate:
        return {'candidate_ui': None}
    if not profile.is_email_verified:
        return {'candidate_ui': 'unverified'}
    return {'candidate_ui': 'verified'}


def hr_ui(request):
    """Expose a single boolean for HR/admin-only UI entry points."""
    if not request.user.is_authenticated:
        return {'hr_ui': False}
    if request.user.is_superuser:
        return {'hr_ui': True}
    return {'hr_ui': request.user.groups.filter(name='hr_manager').exists()}
