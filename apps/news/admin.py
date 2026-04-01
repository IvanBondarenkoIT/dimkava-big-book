"""News admin."""
from django.contrib import admin
from .models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'tag', 'pinned', 'published_at']
    list_filter = ['pinned', 'tag']
    search_fields = ['title', 'title_en', 'title_ka', 'title_ru', 'content', 'content_en', 'content_ka', 'content_ru', 'slug']
    fieldsets = (
        (None, {'fields': ('slug', 'tag', 'pinned', 'published_at')}),
        ('English', {'fields': ('title_en', 'content_en')}),
        ('Georgian', {'fields': ('title_ka', 'content_ka')}),
        ('Russian', {'fields': ('title_ru', 'content_ru')}),
        ('Legacy/Fallback', {'fields': ('title', 'content')}),
    )
