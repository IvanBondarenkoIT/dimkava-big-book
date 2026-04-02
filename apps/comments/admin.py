from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'user', 'content_type', 'object_id', 'created_at', 'moderated_at', 'moderated_by']
    list_filter = ['status', 'content_type']
    search_fields = ['text', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'moderated_by']
    ordering = ['-created_at']
    actions = ['approve_comments', 'reject_comments']

    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset):
        for c in queryset:
            c.approve(by_user=request.user)

    @admin.action(description=_('Reject selected comments'))
    def reject_comments(self, request, queryset):
        for c in queryset:
            c.reject(by_user=request.user)

