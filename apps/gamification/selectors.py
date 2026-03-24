from django.contrib.auth import get_user_model

from .models import GamificationProfile, Mission, UserBadge, UserMissionProgress
from .services import get_level_progress, get_or_create_profile

User = get_user_model()


def get_gamification_dashboard_context(user) -> dict:
    profile = get_or_create_profile(user)
    lp = get_level_progress(profile.total_points)
    missions = Mission.objects.filter(is_active=True).prefetch_related('steps')
    mission_data = []
    for m in missions:
        prog, _ = UserMissionProgress.objects.get_or_create(user=user, mission=m)
        mission_data.append(
            {
                'mission': m,
                'progress': prog,
                'steps_total': m.steps.count(),
                'steps_done': len(prog.completed_step_slugs),
            }
        )
    recent_badges = (
        UserBadge.objects.filter(user=user)
        .select_related('badge')
        .order_by('-awarded_at')[:5]
    )
    rank = (
        GamificationProfile.objects.filter(total_points__gt=profile.total_points).count() + 1
    )
    return {
        'profile': profile,
        'level_progress': lp,
        'missions': mission_data,
        'recent_badges': recent_badges,
        'leaderboard_rank': rank,
    }


def get_leaderboard(top_n: int = 10, current_user=None) -> dict:
    qs = (
        GamificationProfile.objects.select_related('user')
        .order_by('-total_points', 'user_id')[:top_n]
    )
    top_users = []
    for gp in qs:
        u = gp.user
        name = u.get_full_name() or u.get_username()
        if u.first_name and u.last_name:
            display_name = f'{u.first_name} {u.last_name[0]}.'
        else:
            display_name = name[:40]
        top_users.append(
            {
                'user_id': u.id,
                'display_name': display_name,
                'level': gp.level,
                'total_points': gp.total_points,
            }
        )
    current_user_entry = None
    if current_user and current_user.is_authenticated:
        gp = get_or_create_profile(current_user)
        u = current_user
        name = u.get_full_name() or u.get_username()
        if u.first_name and u.last_name:
            display_name = f'{u.first_name} {u.last_name[0]}.'
        else:
            display_name = name[:40]
        rank = GamificationProfile.objects.filter(total_points__gt=gp.total_points).count() + 1
        current_user_entry = {
            'user_id': u.id,
            'display_name': display_name,
            'level': gp.level,
            'total_points': gp.total_points,
            'rank': rank,
        }
    return {'top_users': top_users, 'current_user_entry': current_user_entry}
