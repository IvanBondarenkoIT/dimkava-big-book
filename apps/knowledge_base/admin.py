"""Knowledge base admin."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Article, KBSection


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0
    ordering = ['title']


@admin.register(KBSection)
class KBSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'icon']
    search_fields = ['title', 'slug']
    inlines = [ArticleInline]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title_display',
        'section',
        'slug',
        'status_display',
        'stale_indicator',
        'responsible_editor',
        'review_required_after_days',
        'updated_at',
    ]
    list_filter = ['status', 'section', 'responsible_editor']
    search_fields = ['title', 'slug', 'content']
    autocomplete_fields = ['responsible_editor']
    list_editable = ['responsible_editor', 'review_required_after_days']

    @admin.display(description='Status')
    def status_display(self, obj):
        label = obj.get_status_display()
        if obj.status == 'draft':
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
        if obj.status == 'draft':
            return format_html('<span style="color:#b45309;font-weight:800;">{}</span>', title)
        return title
