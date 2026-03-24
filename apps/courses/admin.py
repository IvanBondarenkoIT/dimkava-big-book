"""Courses admin."""
from django.contrib import admin
from .models import Course, Lesson, TestQuestion, UserProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    ordering = ['order']


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'level', 'status', 'estimated_minutes']
    list_filter = ['status', 'level']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'estimated_minutes']
    list_filter = ['lesson_type']
    inlines = [TestQuestionInline]


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'quiz_score', 'completed_at']
