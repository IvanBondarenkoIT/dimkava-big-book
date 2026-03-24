"""News and announcements."""
from django.db import models


class NewsPost(models.Model):
    """Single news post or announcement."""
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    tag = models.CharField(max_length=40, blank=True)
    pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pinned', '-published_at']

    def __str__(self):
        return self.title
