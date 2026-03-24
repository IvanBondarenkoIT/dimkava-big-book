"""Onboarding admin."""
from django.contrib import admin
from .models import OnboardingProgram, OnboardingModule, OnboardingStep, OnboardingProgress


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
    inlines = [OnboardingModuleInline]


@admin.register(OnboardingModule)
class OnboardingModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'program', 'order', 'estimated_minutes', 'steps_count']
    list_filter = ['program']
    inlines = [OnboardingStepInline]
    ordering = ['program', 'order']

    def steps_count(self, obj):
        return obj.steps.count()
    steps_count.short_description = 'Steps'


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'step', 'completed_at']
    list_filter = ['completed_at']
