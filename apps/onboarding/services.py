"""Onboarding business logic."""
from django.db import transaction
from django.utils import timezone

from .models import OnboardingProgress, OnboardingStep
from .signals import onboarding_step_completed, onboarding_module_completed


def mark_step_complete(user, step: OnboardingStep) -> bool:
    """
    Mark a step as complete for the user. Idempotent — returns True if newly completed.
    Emits onboarding_step_completed, and onboarding_module_completed when module is finished.
    """
    if not isinstance(step, OnboardingStep):
        step = OnboardingStep.objects.get(pk=step)
    with transaction.atomic():
        progress, created = OnboardingProgress.objects.get_or_create(
            user=user,
            step=step,
            defaults={'completed_at': timezone.now()}
        )
    if created:
        onboarding_step_completed.send(sender=OnboardingProgress, user=user, step=step, progress=progress)
        _check_module_completed(user, step.module)
    return created


def _check_module_completed(user, module):
    """If user completed all steps in module, emit onboarding_module_completed."""
    total = module.steps.count()
    completed = OnboardingProgress.objects.filter(user=user, step__module=module).count()
    if total > 0 and completed >= total:
        onboarding_module_completed.send(sender=OnboardingProgress, user=user, module=module)
