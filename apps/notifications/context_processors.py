"""Notification context processors."""


def unread_notifications_count(request):
    """Add unread_notifications_count to template context."""
    count = 0
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    return {'unread_notifications_count': count}
