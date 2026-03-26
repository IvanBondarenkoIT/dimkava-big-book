"""Onboarding admin."""
from django.contrib import admin
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
    search_fields = ['title', 'slug', 'role']
    inlines = [OnboardingModuleInline]


@admin.register(OnboardingModule)
class OnboardingModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'program', 'order', 'estimated_minutes', 'steps_count']
    list_filter = ['program']
    search_fields = ['title', 'slug', 'program__title']
    inlines = [OnboardingStepInline]
    ordering = ['program', 'order']

    def steps_count(self, obj):
        return obj.steps.count()
    steps_count.short_description = 'Steps'


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'program_title', 'order']
    list_filter = ['module__program']
    search_fields = ['title', 'content', 'module__title', 'module__program__title']
    autocomplete_fields = ['module']
    ordering = ['module', 'order']

    @admin.display(description='Program')
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
    list_display = ['program', 'user', 'rating', 'updated_at']
    list_filter = ['rating', 'program']
    search_fields = ['program__title', 'user__username', 'user__email', 'comment']
    autocomplete_fields = ['program', 'user']
