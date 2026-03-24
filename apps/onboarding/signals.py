"""Onboarding signals — for gamification, notifications, etc."""
import django.dispatch

onboarding_step_completed = django.dispatch.Signal()
onboarding_module_completed = django.dispatch.Signal()
