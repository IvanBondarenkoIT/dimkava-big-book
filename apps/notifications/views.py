"""Notifications views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.request.user.notifications.filter(is_read=False).count()
        return context


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """Mark all notifications as read."""

    def post(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return redirect('notifications:list')


class MarkNotificationReadView(LoginRequiredMixin, View):
    """Mark one notification as read and redirect to its link."""

    def get(self, request, pk):
        n = get_object_or_404(Notification, pk=pk, user=request.user)
        n.is_read = True
        n.save(update_fields=['is_read'])
        return redirect(n.link) if n.link else redirect('notifications:list')
