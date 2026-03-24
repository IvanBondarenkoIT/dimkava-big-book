"""News admin."""
from django.contrib import admin
from .models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'tag', 'pinned', 'published_at']
    list_filter = ['pinned', 'tag']
