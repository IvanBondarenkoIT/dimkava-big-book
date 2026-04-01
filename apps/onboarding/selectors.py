"""Onboarding data selectors — for views."""
from .models import OnboardingFeedback, OnboardingProgram, OnboardingProgress


def _program_for_user(user):
    """Prefer program assigned by AssignmentRule; else first program."""
    profile = getattr(user, 'profile', None)
    if profile and profile.assigned_onboarding_program_id:
        program = profile.assigned_onboarding_program
    else:
        program = OnboardingProgram.objects.order_by('id').first()
    if program and profile and profile.is_candidate and not program.visible_for_candidates:
        return OnboardingProgram.objects.filter(visible_for_candidates=True).order_by('id').first()
    return program


def get_onboarding_overview_for_user(user):
    """
    Return program, modules with status for user, and overall progress %.
    Uses assigned program from UserProfile when set; otherwise first program.
    """
    program = _program_for_user(user)
    if not program:
        return (
            None,
            [],
            0,
            {'show': False, 'mentor': None, 'sessions': []},
            {'rating': None, 'comment': ''},
        )

    modules_data = []
    total_steps = 0
    completed_steps = 0

    for module in program.modules.all().order_by('order'):
        steps_count = module.steps.count()
        done = OnboardingProgress.objects.filter(user=user, step__module=module).count()
        total_steps += steps_count
        completed_steps += done

        if steps_count == 0:
            status = 'not_started'
        elif done >= steps_count:
            status = 'completed'
        elif done > 0:
            status = 'in_progress'
        else:
            status = 'not_started'

        modules_data.append({
            'slug': module.slug,
            'title': module.localized_title,
            'status': status,
            'minutes': module.estimated_minutes,
            'steps_done': done,
            'steps_total': steps_count,
        })

    progress = int((completed_steps / total_steps * 100)) if total_steps else 0
    mentor_block = get_mentor_block_for_user(user)
    feedback = OnboardingFeedback.objects.filter(user=user, program=program).first() if program else None

    public_feedback = []
    if program:
        from django.db.models import OuterRef, Subquery
        from apps.gamification.models import UserBadge

        latest_badge_name = Subquery(
            UserBadge.objects.filter(user_id=OuterRef('user_id'))
            .select_related('badge')
            .order_by('-awarded_at')
            .values('badge__name')[:1]
        )
        latest_badge_icon = Subquery(
            UserBadge.objects.filter(user_id=OuterRef('user_id'))
            .select_related('badge')
            .order_by('-awarded_at')
            .values('badge__icon')[:1]
        )

        qs = (
            OnboardingFeedback.objects.filter(program=program, status=OnboardingFeedback.Status.APPROVED)
            .select_related('user')
            .annotate(latest_badge_name=latest_badge_name, latest_badge_icon=latest_badge_icon)
            .order_by('-updated_at')[:12]
        )
        for fb in qs:
            u = fb.user
            profile = getattr(u, 'profile', None)
            public_feedback.append(
                {
                    'user_name': profile.get_public_username() if profile else (u.get_full_name() or u.get_username()),
                    'user_username': u.get_username(),
                    'rating': fb.rating,
                    'comment': fb.comment,
                    'updated_at': fb.updated_at,
                    'badge_name': getattr(fb, 'latest_badge_name', None),
                    'badge_icon': getattr(fb, 'latest_badge_icon', None),
                }
            )

    feedback_block = {
        'rating': feedback.rating if feedback else None,
        'comment': feedback.comment if feedback else '',
        'public_feedback': public_feedback,
    }
    return program, modules_data, progress, mentor_block, feedback_block


def get_module_for_user(module_slug, user):
    """Return module with steps and completion status for user."""
    program = _program_for_user(user)
    if not program:
        return None
    module = program.modules.filter(slug=module_slug).first()
    if not module:
        return None

    completed_ids = set(
        OnboardingProgress.objects.filter(user=user, step__module=module).values_list('step_id', flat=True)
    )
    steps_data = []
    for step in module.steps.all().order_by('order'):
        steps_data.append({
            'id': step.id,
            'title': step.localized_title,
            'content': step.localized_content,
            'completed': step.id in completed_ids,
        })
    return {
        'module': module,
        'steps': steps_data,
    }


def get_mentor_block_for_user(user):
    """
    Mentor context for onboarding overview.
    Returns a dict:
      - show: bool
      - mentor: {...} | None
      - sessions: [{...}]
    """
    from .models import MentorAssignment

    assignment = MentorAssignment.objects.select_related('mentor', 'mentor__user').filter(mentee=user).first()
    if not assignment or not assignment.mentor or not assignment.mentor.is_active:
        return {'show': False, 'mentor': None, 'sessions': []}

    sessions = list(
        assignment.sessions.order_by('scheduled_date', 'id').values(
            'id',
            'session_type',
            'scheduled_date',
            'is_completed',
            'completed_at',
            'notes',
        )
    )

    mentor = assignment.mentor
    return {
        'show': True,
        'mentor': {
            'name': mentor.user.get_full_name() or mentor.user.get_username(),
            'title': mentor.title,
            'contact_info': mentor.contact_info,
            'responsibility_area': mentor.responsibility_area,
        },
        'sessions': sessions,
    }
