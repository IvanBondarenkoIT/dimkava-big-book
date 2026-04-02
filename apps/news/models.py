"""News and announcements."""
from django.db import models
from django.utils.translation import get_language, pgettext, gettext_lazy as _


class NewsPost(models.Model):
    """Single news post or announcement."""
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, default='')
    title_ka = models.CharField(max_length=255, blank=True, default='')
    title_ru = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True)
    content_en = models.TextField(blank=True, default='')
    content_ka = models.TextField(blank=True, default='')
    content_ru = models.TextField(blank=True, default='')
    tag = models.CharField(max_length=40, blank=True)
    pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('News post')
        verbose_name_plural = _('News posts')
        ordering = ['-pinned', '-published_at']

    def __str__(self):
        return self.title

    @property
    def localized_title(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'title_{lang}', '') or self.title_en or self.title

    @property
    def localized_content(self) -> str:
        lang = (get_language() or 'en').split('-')[0]
        return getattr(self, f'content_{lang}', '') or self.content_en or self.content

    @property
    def localized_tag(self) -> str:
        """Human-readable tag for current locale (seed uses short codes: general, training)."""
        key = (self.tag or '').strip().lower()
        if key == 'general':
            return pgettext('news_post_tag', 'General')
        if key == 'training':
            return pgettext('news_post_tag', 'Training')
        return self.tag
