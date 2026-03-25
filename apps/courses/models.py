"""Course, Lesson, Quiz models."""
from django.conf import settings
from django.db import models
from django.utils import timezone


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
    slug = models.SlugField(unique=True, max_length=120)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    estimated_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    visible_for_candidates = models.BooleanField(default=False)
    description = models.TextField(blank=True)
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
        ordering = ['title']

    def __str__(self):
        return self.title

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
    order = models.PositiveIntegerField(default=0)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='text')
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    estimated_minutes = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    passing_score = models.PositiveIntegerField(null=True, blank=True)  # For quiz: 0-100
    visible_for_candidates = models.BooleanField(default=False)

    class Meta:
        ordering = ['course', 'order']
        unique_together = [('course', 'order')]

    def __str__(self):
        return f'{self.course.title} — {self.title}'


class TestQuestion(models.Model):
    """Multiple choice question for quiz lessons. options: [{"text": "...", "is_correct": true}, ...]"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField(default=list)  # [{"text": "...", "is_correct": true}, ...]
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['lesson', 'order']
        unique_together = [('lesson', 'order')]

    def __str__(self):
        return self.question_text[:50]


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    quiz_score = models.PositiveIntegerField(null=True, blank=True)  # 0-100

    class Meta:
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
        ordering = ['order', 'id']

    def __str__(self):
        return f'ILPItem: {self.title}'
