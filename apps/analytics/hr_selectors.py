"""HR-focused selectors for site UI (not Django admin)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateRow:
    profile_id: int
    user_id: int
    email: str
    phone: str
    email_verified_at: object
    assigned_onboarding_program: object
    onboarding_progress_pct: int
    last_login: object


def get_candidate_rows():
    from django.contrib.auth import get_user_model

    from apps.accounts.models import UserProfile
    from apps.onboarding.selectors import get_onboarding_overview_for_user

    User = get_user_model()
    profiles = (
        UserProfile.objects.filter(user_type='candidate')
        .select_related('user', 'assigned_onboarding_program')
        .order_by('-user__date_joined')
    )

    rows: list[CandidateRow] = []
    for p in profiles:
        # Keep it simple: selector already exists; N+1 is OK for small HR lists.
        _program, _modules, progress, _mentor, _feedback = get_onboarding_overview_for_user(p.user)
        rows.append(
            CandidateRow(
                profile_id=p.pk,
                user_id=p.user_id,
                email=p.user.email or p.user.username,
                phone=p.phone,
                email_verified_at=p.email_verified_at,
                assigned_onboarding_program=p.assigned_onboarding_program,
                onboarding_progress_pct=progress,
                last_login=p.user.last_login,
            )
        )
    return rows

