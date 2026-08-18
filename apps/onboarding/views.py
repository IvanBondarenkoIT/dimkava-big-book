from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .models import OnboardingFeedback, OnboardingStep
from .selectors import get_module_for_user, get_onboarding_overview_for_user
from .services import mark_step_complete


class OverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'onboarding/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program, modules, progress, mentor_block, feedback_block = get_onboarding_overview_for_user(self.request.user)
        context['program'] = program
        context['modules'] = modules
        context['progress'] = progress
        context['mentor_block'] = mentor_block
        context['feedback'] = feedback_block
        return context


class ModuleDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'onboarding/module_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        data = get_module_for_user(slug, self.request.user)
        if not data:
            context['module'] = None
            context['steps'] = []
            return context
        context['module'] = data['module']
        context['steps'] = data['steps']
        return context


class MarkStepCompleteView(LoginRequiredMixin, View):
    """POST to mark a step complete. Only steps in the user's visible program."""

    def post(self, request, step_id):
        step = get_object_or_404(OnboardingStep.objects.select_related('module'), pk=step_id)
        data = get_module_for_user(step.module.slug, request.user)
        if not data or not data.get('module') or data['module'].pk != step.module_id:
            return redirect('onboarding:overview')
        allowed_ids = {s['id'] for s in data.get('steps') or []}
        if step.pk not in allowed_ids:
            return redirect('onboarding:overview')
        mark_step_complete(request.user, step)
        return redirect('onboarding:module_detail', slug=step.module.slug)


class SubmitFeedbackView(LoginRequiredMixin, View):
    def post(self, request):
        program, _modules, _progress, _mentor, _feedback = get_onboarding_overview_for_user(request.user)
        if not program:
            return redirect('onboarding:overview')

        existing = OnboardingFeedback.objects.filter(user=request.user, program=program).first()
        try:
            rating = int(request.POST.get('rating') or 0)
        except ValueError:
            rating = 0
        comment = (request.POST.get('comment') or '').strip()
        if rating < 1 or rating > 5:
            # If user only updated comment (or UI didn't send rating), keep previous rating.
            if existing and 1 <= existing.rating <= 5:
                rating = existing.rating
            else:
                messages.error(request, 'Please select a rating from 1 to 5.')
                return redirect('onboarding:overview')

        OnboardingFeedback.objects.update_or_create(
            user=request.user,
            program=program,
            defaults={'rating': rating, 'comment': comment, 'status': OnboardingFeedback.Status.PENDING},
        )
        messages.success(request, 'Feedback saved.')
        return redirect('onboarding:overview')
