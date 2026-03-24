"""Departments selectors."""
from .models import Department, Role


def get_departments():
    """Return all departments with role count."""
    return list(
        Department.objects.prefetch_related('roles').all()
    )


def get_department_detail(slug):
    """Return department with roles and their required/recommended courses."""
    try:
        dept = Department.objects.prefetch_related(
            'roles__required_courses',
            'roles__recommended_courses',
        ).get(slug=slug)
    except Department.DoesNotExist:
        return None
    roles_data = []
    for role in dept.roles.all():
        roles_data.append({
            'role': role,
            'required': list(role.required_courses.filter(status='published')),
            'recommended': list(role.recommended_courses.filter(status='published')),
        })
    return {'department': dept, 'roles': roles_data}
