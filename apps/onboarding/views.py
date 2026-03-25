from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .models import OnboardingStep
from .selectors import get_module_for_user, get_onboarding_overview_for_user
from .services import mark_step_complete


class OverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'onboarding/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program, modules, progress, mentor_block = get_onboarding_overview_for_user(self.request.user)
        context['program'] = program
        context['modules'] = modules
        context['progress'] = progress
        context['mentor_block'] = mentor_block
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
    """POST to mark a step complete. Redirects back to module."""

    def post(self, request, step_id):
        step = get_object_or_404(OnboardingStep, pk=step_id)
        mark_step_complete(request.user, step)
        return redirect('onboarding:module_detail', slug=step.module.slug)
