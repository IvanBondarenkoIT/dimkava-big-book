from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Badge, GamificationProfile, Mission, PointsLog, UserBadge, UserMissionProgress

User = get_user_model()

LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 100),
    (3, 300),
    (4, 700),
    (5, 1500),
    (6, 3000),
    (7, 6000),
]

LEVEL_NAMES = {
    1: _('Newcomer'),
    2: _('Barista'),
    3: _('Specialist'),
    4: _('Expert'),
    5: _('Senior Expert'),
    6: _('Mentor'),
    7: _('Legend'),
}


def calculate_level(total_points: int) -> int:
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS:
        if total_points >= threshold:
            level = lvl
    return level


def get_level_progress(total_points: int) -> dict:
    current_level = calculate_level(total_points)
    next_threshold = None
    for lvl, threshold in LEVEL_THRESHOLDS:
        if lvl == current_level + 1:
            next_threshold = threshold
            break
    prev_threshold = 0
    for lvl, threshold in LEVEL_THRESHOLDS:
        if lvl == current_level:
            prev_threshold = threshold
            break
    level_name = LEVEL_NAMES.get(current_level, str(current_level))
    if next_threshold is None:
        return {
            'current_level': current_level,
            'level_name': level_name,
            'points_in_current_level': total_points - prev_threshold,
            'points_needed_for_next_level': 0,
            'percent_to_next_level': 100.0,
        }
    span = next_threshold - prev_threshold
    in_level = total_points - prev_threshold
    pct = (in_level / span * 100) if span else 0.0
    return {
        'current_level': current_level,
        'level_name': level_name,
        'points_in_current_level': in_level,
        'points_needed_for_next_level': next_threshold - total_points,
        'percent_to_next_level': min(100.0, max(0.0, pct)),
    }


def get_or_create_profile(user: User) -> GamificationProfile:
    profile, _ = GamificationProfile.objects.get_or_create(user=user)
    return profile


@transaction.atomic
def award_points(
    user: User,
    amount: int,
    source: str,
    reference: str = '',
    note: str = '',
) -> GamificationProfile:
    profile = get_or_create_profile(user)
    profile.total_points = max(0, profile.total_points + amount)
    profile.level = calculate_level(profile.total_points)
    profile.save()
    PointsLog.objects.create(
        user=user,
        source=source,
        reference=reference,
        points=amount,
        note=note,
    )
    return profile


@transaction.atomic
def award_badge(user: User, badge_code: str, reason: str = '') -> Optional[UserBadge]:
    try:
        badge = Badge.objects.get(code=badge_code, is_active=True)
    except Badge.DoesNotExist:
        return None
    ub, created = UserBadge.objects.get_or_create(
        user=user,
        badge=badge,
        defaults={'reason': reason},
    )
    if not created:
        return None
    return ub


@transaction.atomic
def update_mission_progress(
    user: User,
    mission_code: str,
    completed_step_slug: str,
) -> UserMissionProgress:
    mission = Mission.objects.prefetch_related('steps').get(code=mission_code, is_active=True)
    progress, _ = UserMissionProgress.objects.get_or_create(user=user, mission=mission)
    was_completed = progress.is_completed
    slugs = list(progress.completed_step_slugs)
    if completed_step_slug not in slugs:
        slugs.append(completed_step_slug)
    progress.completed_step_slugs = slugs
    required = [s.module_slug for s in mission.steps.all() if s.is_required]
    done = set(slugs)
    all_required_done = bool(required) and all(s in done for s in required)
    if all_required_done and not was_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        if mission.bonus_points:
            award_points(
                user,
                mission.bonus_points,
                'MISSION',
                reference=mission.code,
                note='Mission bonus',
            )
        if mission.completion_badge_id:
            award_badge(user, mission.completion_badge.code, reason=mission.code)
    progress.save()
    return progress


