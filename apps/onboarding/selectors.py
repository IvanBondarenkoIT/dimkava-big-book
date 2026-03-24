"""Onboarding data selectors — for views."""
from .models import OnboardingProgram, OnboardingModule, OnboardingStep, OnboardingProgress


def get_onboarding_overview_for_user(user):
    """
    Return program, modules with status for user, and overall progress %.
    Uses first program; later can filter by role.
    """
    program = OnboardingProgram.objects.first()
    if not program:
        return None, [], 0

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
            'title': module.title,
            'status': status,
            'minutes': module.estimated_minutes,
            'steps_done': done,
            'steps_total': steps_count,
        })

    progress = int((completed_steps / total_steps * 100)) if total_steps else 0
    return program, modules_data, progress


def get_module_for_user(module_slug, user):
    """Return module with steps and completion status for user."""
    program = OnboardingProgram.objects.first()
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
            'title': step.title,
            'content': step.content,
            'completed': step.id in completed_ids,
        })
    return {
        'module': module,
        'steps': steps_data,
    }
