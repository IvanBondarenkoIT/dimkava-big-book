"""Access control for HR content editor views."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from apps.core.permissions import user_can_edit_content


class ContentEditorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return user_can_edit_content(self.request.user)
