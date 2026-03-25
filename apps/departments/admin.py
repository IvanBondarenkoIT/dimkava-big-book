"""Departments admin."""
from django.contrib import admin
from .models import Department, Role


class RoleInline(admin.TabularInline):
    model = Role
    extra = 0
    ordering = ['order']
    filter_horizontal = ['required_courses', 'recommended_courses']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    inlines = [RoleInline]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'order']
    list_filter = ['department']
    search_fields = ['title', 'department__name']
    filter_horizontal = ['required_courses', 'recommended_courses']
