"""Course signals — for gamification, notifications."""
import django.dispatch

lesson_completed = django.dispatch.Signal()
quiz_passed = django.dispatch.Signal()
