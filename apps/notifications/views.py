from django.views.generic import TemplateView


class NotificationListView(TemplateView):
    template_name = 'notifications/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = [
            {'text': 'New course available: Latte Art Basics', 'date': '2 hours ago', 'read': False},
            {'text': 'You earned badge: First Extraction', 'date': '1 day ago', 'read': True},
        ]
        return context
