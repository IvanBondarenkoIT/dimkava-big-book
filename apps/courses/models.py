"""Course, Lesson, Quiz models."""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('manager', 'Manager'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('published', 'Published'),
    ]
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, default='')
    title_ka = models.CharField(max_length=255, blank=True, default='')
    title_ru = models.CharField(max_length=255, blank=True, default='')
    slug = models.SlugField(unique=True, max_length=120)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    estimated_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    visible_for_candidates = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True, default='')
    description_ka = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')
    image = models.URLField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_courses'
    )
    responsible_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_responsible',
    )
    review_required_after_days = models.PositiveIntegerField(default=180)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def localized_title(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'title_{lang}', '') or self.title_en or self.title

    @property
    def localized_description(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'description_{lang}', '') or self.description_en or self.description

    @property
    def is_stale(self) -> bool:
        if not self.updated_at:
            return False
        delta = timezone.now() - self.updated_at
        return delta.days > self.review_required_after_days


class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('file', 'File'),
        ('quiz', 'Quiz'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, default='')
    title_ka = models.CharField(max_length=255, blank=True, default='')
    title_ru = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='text')
    content = models.TextField(blank=True)
    content_en = models.TextField(blank=True, default='')
    content_ka = models.TextField(blank=True, default='')
    content_ru = models.TextField(blank=True, default='')
    video_url = models.URLField(blank=True)
    estimated_minutes = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    passing_score = models.PositiveIntegerField(null=True, blank=True)  # For quiz: 0-100
    visible_for_candidates = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['course', 'order']
        unique_together = [('course', 'order')]

    def __str__(self):
        return f'{self.course.title} — {self.title}'

    @property
    def localized_title(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'title_{lang}', '') or self.title_en or self.title

    @property
    def localized_content(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'content_{lang}', '') or self.content_en or self.content


class TestQuestion(models.Model):
    """Multiple choice question for quiz lessons. options: [{"text": "...", "is_correct": true}, ...]"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_text_en = models.TextField(blank=True, default='')
    question_text_ka = models.TextField(blank=True, default='')
    question_text_ru = models.TextField(blank=True, default='')
    options = models.JSONField(default=list)  # [{"text": "...", "is_correct": true}, ...]
    options_en = models.JSONField(default=list, blank=True)
    options_ka = models.JSONField(default=list, blank=True)
    options_ru = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Test question')
        verbose_name_plural = _('Test questions')
        ordering = ['lesson', 'order']
        unique_together = [('lesson', 'order')]

    def __str__(self):
        return self.question_text[:50]

    @property
    def localized_question_text(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'question_text_{lang}', '') or self.question_text_en or self.question_text

    @property
    def localized_options(self):
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'options_{lang}', None) or self.options_en or self.options


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    quiz_score = models.PositiveIntegerField(null=True, blank=True)  # 0-100
    quiz_attempts_count = models.PositiveIntegerField(default=0)
    candidate_quiz_locked = models.BooleanField(default=False)
    candidate_retake_unlocked_at = models.DateTimeField(null=True, blank=True)
    candidate_retake_unlocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='candidate_quiz_unlock_actions',
    )
    quiz_answers = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _('User progress')
        verbose_name_plural = _('User progress')
        unique_together = [('user', 'lesson')]

    def __str__(self):
        return f'{self.user} — {self.lesson}'


class IndividualLearningPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_plans',
    )
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_ilps',
    )
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Individual learning plan')
        verbose_name_plural = _('Individual learning plans')
        ordering = ['-created_at', 'id']

    def __str__(self):
        return f'ILP: {self.user} — {self.title}'


class ILPItem(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('article', 'Article'),
    ]
    plan = models.ForeignKey(IndividualLearningPlan, on_delete=models.CASCADE, related_name='items')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    object_slug = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    is_required = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('ILP item')
        verbose_name_plural = _('ILP items')
        ordering = ['order', 'id']

    def __str__(self):
        return f'ILPItem: {self.title}'


class LessonRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_ratings')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Lesson rating')
        verbose_name_plural = _('Lesson ratings')
        unique_together = [('user', 'lesson')]
        ordering = ['-updated_at', '-id']

    def __str__(self):
        return f'LessonRating: {self.lesson} — {self.rating}/5'
