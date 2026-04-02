"""Departments and roles with learning paths."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """Organizational department (e.g. Retail Store, Marketing)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=80)

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """Job role within a department, with learning path (required + recommended courses)."""
    title = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='roles'
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    required_courses = models.ManyToManyField(
        'courses.Course',
        blank=True,
        related_name='required_for_roles',
        help_text='Mandatory courses for this role.',
    )
    recommended_courses = models.ManyToManyField(
        'courses.Course',
        blank=True,
        related_name='recommended_for_roles',
        help_text='Optional but suggested courses.',
    )

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['department', 'order', 'title']

    def __str__(self):
        return f'{self.department.name} — {self.title}'
