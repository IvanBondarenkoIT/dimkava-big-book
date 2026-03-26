"""Accounts admin: User with profile inline, AssignmentRule."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import AssignmentRule, UserProfile
from .services import convert_candidate_to_employee


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False
    fk_name = 'user'
    autocomplete_fields = ['department', 'role', 'assigned_onboarding_program']
    readonly_fields = ['email_verified_at']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'profile_user_type',
        'profile_email_verified_at',
        'last_login',
        'date_joined',
    ]

    @admin.display(description='User type')
    def profile_user_type(self, obj):
        profile = getattr(obj, 'profile', None)
        return getattr(profile, 'user_type', '')

    @admin.display(description='Email verified at')
    def profile_email_verified_at(self, obj):
        profile = getattr(obj, 'profile', None)
        return getattr(profile, 'email_verified_at', None)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'user_type',
        'phone',
        'email_verified_at',
        'department',
        'role',
        'assigned_onboarding_program',
        'onboarding_progress_pct',
        'last_login',
    ]
    list_filter = ['user_type', 'department', 'role', 'assigned_onboarding_program']
    search_fields = ['user__username', 'user__email', 'phone']
    autocomplete_fields = ['user', 'department', 'role', 'assigned_onboarding_program']

    @admin.display(description='Last login')
    def last_login(self, obj):
        return obj.user.last_login

    @admin.display(description='Onboarding %')
    def onboarding_progress_pct(self, obj):
        from apps.onboarding.selectors import get_onboarding_overview_for_user

        _program, _modules, progress, _mentor, _feedback = get_onboarding_overview_for_user(obj.user)
        return progress

    actions = ['convert_to_employee', 'mark_email_verified']

    @admin.action(description='Mark email as verified (candidates)')
    def mark_email_verified(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(email_verified_at=timezone.now())
        self.message_user(request, f'Marked {updated} profile(s) as email verified.')

    @admin.action(description='Convert selected candidates to employees')
    def convert_to_employee(self, request, queryset):
        for profile in queryset.select_related('user'):
            convert_candidate_to_employee(profile.user)


@admin.register(AssignmentRule)
class AssignmentRuleAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'role_name',
        'department',
        'onboarding_program_slug',
        'course_count',
        'is_active',
    ]
    list_filter = ['is_active', 'department']
    search_fields = ['role_name', 'onboarding_program_slug']

    @admin.display(description='Courses')
    def course_count(self, obj):
        return len(obj.required_course_slugs or [])


if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.register(User, UserAdmin)
