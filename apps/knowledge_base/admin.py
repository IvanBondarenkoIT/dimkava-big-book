"""Knowledge base admin."""
from django.contrib import admin
from .models import Article, KBSection


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0
    ordering = ['title']


@admin.register(KBSection)
class KBSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'icon']
    inlines = [ArticleInline]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'slug', 'status', 'updated_at']
    list_filter = ['status', 'section']
