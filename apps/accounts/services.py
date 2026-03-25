"""Assignment rules: match profile to rules and set program / course slugs."""
from django.db import transaction

from .models import AssignmentRule, UserProfile


def sync_user_groups_from_profile(user) -> None:
    """
    Keep Django auth Group membership aligned with UserProfile.user_type.
    Intended for HR/admin workflows; not a security boundary on its own.
    """
    from django.contrib.auth.models import Group

    profile = getattr(user, 'profile', None)
    if not profile:
        return

    candidate_group, _ = Group.objects.get_or_create(name='candidate')
    employee_group, _ = Group.objects.get_or_create(name='employee')

    if profile.is_candidate:
        user.groups.add(candidate_group)
        user.groups.remove(employee_group)
    else:
        user.groups.add(employee_group)
        user.groups.remove(candidate_group)


@transaction.atomic
def convert_candidate_to_employee(user, *, department=None, role=None) -> None:
    profile = getattr(user, 'profile', None)
    if profile is None:
        return

    updates = []
    if profile.user_type != 'employee':
        profile.user_type = 'employee'
        updates.append('user_type')
    if department is not None and profile.department_id != getattr(department, 'id', department):
        profile.department_id = getattr(department, 'id', department)
        updates.append('department')
    if role is not None and profile.role_id != getattr(role, 'id', role):
        profile.role_id = getattr(role, 'id', role)
        updates.append('role')
    if updates:
        profile.save(update_fields=updates)

    sync_user_groups_from_profile(user)
    apply_assignment_rules(user)


def _rule_matches_profile(rule: AssignmentRule, profile: UserProfile) -> bool:
    if rule.department_id:
        if profile.department_id != rule.department_id:
            return False
    if rule.role_name:
        if not profile.role_id:
            return False
        if profile.role.title.strip() != rule.role_name.strip():
            return False
    return True


def find_matching_rule(profile: UserProfile) -> AssignmentRule | None:
    """First active rule that matches department + role_name constraints."""
    for rule in AssignmentRule.objects.filter(is_active=True).order_by('id'):
        if _rule_matches_profile(rule, profile):
            return rule
    return None


@transaction.atomic
def apply_assignment_rules(user) -> None:
    """
    Apply matching AssignmentRule to the user's profile (if any).

    TODO: connect required_course_slugs to real enrollment / UserProgress
    (best_practices §3 — mock assignment path until product rules are defined).
    """
    profile = getattr(user, 'profile', None)
    if profile is None:
        return
    rule = find_matching_rule(profile)
    if not rule:
        return

    from apps.onboarding.models import OnboardingProgram

    updates = []
    if rule.onboarding_program_slug:
        prog = OnboardingProgram.objects.filter(slug=rule.onboarding_program_slug).first()
        if prog and profile.assigned_onboarding_program_id != prog.id:
            profile.assigned_onboarding_program = prog
            updates.append('assigned_onboarding_program')

    slugs = list(rule.required_course_slugs or [])
    if profile.pending_course_slugs != slugs:
        profile.pending_course_slugs = slugs
        updates.append('pending_course_slugs')

    if updates:
        profile.save(update_fields=updates)
