"""Knowledge base: sections and articles."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class KBSection(models.Model):
    """Wiki section (e.g. Procedures, Service Standards)."""
    slug = models.SlugField(unique=True, max_length=80)
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=40, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Article(models.Model):
    """Article in a knowledge base section."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    section = models.ForeignKey(
        KBSection, on_delete=models.CASCADE, related_name='articles'
    )
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    content = models.TextField(blank=True)
    responsible_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='article_responsible',
    )
    review_required_after_days = models.PositiveIntegerField(default=180)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['section', 'title']
        unique_together = [('section', 'slug')]

    def __str__(self):
        return f'{self.section.title} — {self.title}'

    @property
    def is_stale(self) -> bool:
        if not self.updated_at:
            return False
        delta = timezone.now() - self.updated_at
        return delta.days > self.review_required_after_days
