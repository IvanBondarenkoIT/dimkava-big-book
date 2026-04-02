"""Onboarding admin."""
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import (
    Mentor,
    MentorAssignment,
    MentorSession,
    OnboardingFeedback,
    OnboardingModule,
    OnboardingProgram,
    OnboardingProgress,
    OnboardingStep,
)


class OnboardingStepInline(admin.TabularInline):
    model = OnboardingStep
    extra = 0
    ordering = ['order']


class OnboardingModuleInline(admin.TabularInline):
    model = OnboardingModule
    extra = 0
    ordering = ['order']
    show_change_link = True


@admin.register(OnboardingProgram)
class OnboardingProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'estimated_days', 'created_at']
    search_fields = ['title', 'title_en', 'title_ka', 'title_ru', 'slug', 'role']
    inlines = [OnboardingModuleInline]
    fieldsets = (
        (None, {'fields': ('slug', 'role', 'visible_for_candidates', 'estimated_days')}),
        ('English', {'fields': ('title_en', 'description_en')}),
        ('Georgian', {'fields': ('title_ka', 'description_ka')}),
        ('Russian', {'fields': ('title_ru', 'description_ru')}),
        ('Legacy/Fallback', {'fields': ('title', 'description')}),
    )


@admin.register(OnboardingModule)
class OnboardingModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'program', 'order', 'estimated_minutes', 'steps_count']
    list_filter = ['program']
    search_fields = ['title', 'title_en', 'title_ka', 'title_ru', 'slug', 'program__title', 'program__title_en', 'program__title_ka', 'program__title_ru']
    inlines = [OnboardingStepInline]
    ordering = ['program', 'order']
    fieldsets = (
        (None, {'fields': ('program', 'slug', 'order', 'estimated_minutes')}),
        ('English', {'fields': ('title_en', 'description_en')}),
        ('Georgian', {'fields': ('title_ka', 'description_ka')}),
        ('Russian', {'fields': ('title_ru', 'description_ru')}),
        ('Legacy/Fallback', {'fields': ('title', 'description')}),
    )

    def steps_count(self, obj):
        return obj.steps.count()
    steps_count.short_description = _('Steps')


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'program_title', 'order']
    list_filter = ['module__program']
    search_fields = [
        'title', 'title_en', 'title_ka', 'title_ru',
        'content', 'content_en', 'content_ka', 'content_ru',
        'module__title', 'module__title_en', 'module__title_ka', 'module__title_ru',
        'module__program__title', 'module__program__title_en', 'module__program__title_ka', 'module__program__title_ru',
    ]
    autocomplete_fields = ['module']
    ordering = ['module', 'order']
    fieldsets = (
        (None, {'fields': ('module', 'order')}),
        ('English', {'fields': ('title_en', 'content_en')}),
        ('Georgian', {'fields': ('title_ka', 'content_ka')}),
        ('Russian', {'fields': ('title_ru', 'content_ru')}),
        ('Legacy/Fallback', {'fields': ('title', 'content')}),
    )

    @admin.display(description=_('Program'))
    def program_title(self, obj):
        return obj.module.program.title


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'step', 'completed_at']
    list_filter = ['completed_at']
    search_fields = ['user__username', 'user__email', 'step__title']
    autocomplete_fields = ['user', 'step']


class MentorSessionInline(admin.TabularInline):
    model = MentorSession
    extra = 0
    ordering = ['scheduled_date', 'id']


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'responsibility_area', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username', 'user__email', 'title', 'responsibility_area']
    autocomplete_fields = ['user']


@admin.register(MentorAssignment)
class MentorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'mentor', 'assigned_at']
    list_filter = ['assigned_at']
    search_fields = ['mentee__username', 'mentee__email', 'mentor__user__username', 'mentor__user__email']
    autocomplete_fields = ['mentee', 'mentor']
    inlines = [MentorSessionInline]


@admin.register(MentorSession)
class MentorSessionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'session_type', 'scheduled_date', 'is_completed', 'completed_at']
    list_filter = ['session_type', 'is_completed']
    search_fields = ['assignment__mentee__username', 'assignment__mentee__email', 'notes']
    autocomplete_fields = ['assignment']


@admin.register(OnboardingFeedback)
class OnboardingFeedbackAdmin(admin.ModelAdmin):
    list_display = ['program', 'user', 'rating', 'status', 'updated_at', 'moderated_at', 'moderated_by']
    list_filter = ['status', 'rating', 'program']
    search_fields = ['program__title', 'user__username', 'user__email', 'comment']
    autocomplete_fields = ['program', 'user']
    actions = ['approve_feedback', 'reject_feedback']

    @admin.action(description=_('Approve selected onboarding feedback'))
    def approve_feedback(self, request, queryset):
        queryset.update(
            status=OnboardingFeedback.Status.APPROVED,
            moderated_at=timezone.now(),
            moderated_by=request.user,
        )

    @admin.action(description=_('Reject selected onboarding feedback'))
    def reject_feedback(self, request, queryset):
        queryset.update(
            status=OnboardingFeedback.Status.REJECTED,
            moderated_at=timezone.now(),
            moderated_by=request.user,
        )
