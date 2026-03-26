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
