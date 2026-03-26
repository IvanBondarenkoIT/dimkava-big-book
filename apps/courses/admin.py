"""Courses admin."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Course, ILPItem, IndividualLearningPlan, Lesson, LessonRating, TestQuestion, UserProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    ordering = ['order']


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title_display',
        'slug',
        'level',
        'status_display',
        'stale_indicator',
        'responsible_editor',
        'review_required_after_days',
        'estimated_minutes',
    ]
    list_filter = ['status', 'level', 'responsible_editor']
    search_fields = ['title', 'slug', 'description']
    autocomplete_fields = ['author', 'responsible_editor']
    inlines = [LessonInline]
    list_editable = ['responsible_editor', 'review_required_after_days']

    @admin.display(description='Status')
    def status_display(self, obj):
        label = obj.get_status_display()
        if obj.status == 'review':
            return format_html('<strong style="color:#b45309;">{}</strong>', label)
        return label

    @admin.display(description='Stale')
    def stale_indicator(self, obj):
        if obj.is_stale:
            return format_html(
                '<span title="Not updated within {} days">⚠️</span>',
                obj.review_required_after_days,
            )
        return '—'

    @admin.display(description='Title')
    def title_display(self, obj):
        title = obj.title
        if obj.is_stale:
            return format_html('<span style="color:#b91c1c;font-weight:800;">⚠️ {}</span>', title)
        if obj.status == 'review':
            return format_html('<span style="color:#b45309;font-weight:800;">{}</span>', title)
        return title


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'estimated_minutes']
    list_filter = ['lesson_type']
    search_fields = ['title', 'course__title']
    inlines = [TestQuestionInline]


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['short_question', 'lesson', 'course_title', 'order']
    list_filter = ['lesson__course']
    search_fields = ['question_text', 'lesson__title', 'lesson__course__title']
    autocomplete_fields = ['lesson']
    ordering = ['lesson', 'order']

    @admin.display(description='Question')
    def short_question(self, obj):
        text = obj.question_text.strip()
        if len(text) <= 80:
            return text
        return text[:80] + '…'

    @admin.display(description='Course')
    def course_title(self, obj):
        return obj.lesson.course.title


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'quiz_score', 'completed_at']
    list_filter = ['is_completed']
    autocomplete_fields = ['user', 'lesson']


class ILPItemInline(admin.TabularInline):
    model = ILPItem
    extra = 0
    ordering = ['order', 'id']


@admin.register(IndividualLearningPlan)
class IndividualLearningPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_active', 'deadline', 'created_at', 'items_count']
    list_filter = ['is_active']
    search_fields = ['title', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'created_by']
    inlines = [ILPItemInline]

    @admin.display(description='Items')
    def items_count(self, obj):
        return obj.items.count()


@admin.register(ILPItem)
class ILPItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'plan', 'content_type', 'object_slug', 'is_required', 'is_completed', 'deadline', 'order']
    list_filter = ['content_type', 'is_required', 'is_completed']
    search_fields = ['title', 'object_slug', 'plan__title', 'plan__user__username', 'plan__user__email']
    autocomplete_fields = ['plan']


@admin.register(LessonRating)
class LessonRatingAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'user', 'rating', 'updated_at']
    list_filter = ['rating']
    search_fields = ['lesson__title', 'lesson__course__title', 'user__username', 'user__email', 'comment']
    autocomplete_fields = ['lesson', 'user']
