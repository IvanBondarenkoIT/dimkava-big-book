"""Comment submit views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import View

from .services import resolve_comment_target, submit_comment


class SubmitCommentView(LoginRequiredMixin, View):
    def post(self, request):
        app_label = (request.POST.get('app_label') or '').strip()
        model = (request.POST.get('model') or '').strip()
        object_id = request.POST.get('object_id') or ''
        next_url = (request.POST.get('next') or '/').strip() or '/'
        text = request.POST.get('text') or ''

        if not object_id.isdigit():
            messages.error(request, _('Could not save comment.'))
            return redirect(next_url)

        obj = resolve_comment_target(app_label, model, int(object_id))
        if obj is None:
            messages.error(request, _('Could not save comment.'))
            return redirect(next_url)

        try:
            submit_comment(user=request.user, obj=obj, text=text)
        except ValueError:
            messages.error(request, _('Please write a comment before submitting.'))
            return redirect(next_url)

        messages.success(
            request,
            _('Comment submitted. It will appear after HR approval.'),
        )
        return redirect(next_url)
