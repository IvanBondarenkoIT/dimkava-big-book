"""Analytics views — HR/Admin only."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from .permissions import user_can_view_analytics
from .content_review_selectors import get_content_to_review
from .hr_selectors import get_candidate_rows
from .selectors import get_analytics_metrics


class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metrics'] = get_analytics_metrics()
        return context


class ContentReviewView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/content_review.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stale_only = self.request.GET.get('stale_only') in ('1', 'true', 'yes')
        context.update(get_content_to_review(stale_only=stale_only))
        return context


class HRHubView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/hr_hub.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)


class CandidatesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/candidates.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates'] = get_candidate_rows()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        profile_id = request.POST.get('profile_id')
        if not action or not profile_id:
            return redirect('analytics:candidates')

        from apps.accounts.models import UserProfile
        from apps.accounts.services import convert_candidate_to_employee

        p = UserProfile.objects.select_related('user').filter(pk=profile_id, user_type='candidate').first()
        if not p:
            return redirect('analytics:candidates')

        if action == 'mark_email_verified':
            if p.email_verified_at is None:
                p.email_verified_at = timezone.now()
                p.save(update_fields=['email_verified_at'])
        elif action == 'convert_to_employee':
            convert_candidate_to_employee(p.user)

        return redirect('analytics:candidates')


class VisibilityView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/visibility.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.courses.models import Course, Lesson
        from apps.onboarding.models import OnboardingProgram

        context['programs'] = OnboardingProgram.objects.all().order_by('title')
        context['courses'] = Course.objects.all().order_by('title')
        context['lessons'] = Lesson.objects.select_related('course').all().order_by('course__title', 'order')
        return context

    def post(self, request, *args, **kwargs):
        target = request.POST.get('target')
        obj_id = request.POST.get('id')
        value = request.POST.get('value') in ('1', 'true', 'yes', 'on')
        if not target or not obj_id:
            return redirect('analytics:visibility')

        if target == 'program':
            from apps.onboarding.models import OnboardingProgram
            OnboardingProgram.objects.filter(pk=obj_id).update(visible_for_candidates=value)
        elif target == 'course':
            from apps.courses.models import Course
            Course.objects.filter(pk=obj_id).update(visible_for_candidates=value)
        elif target == 'lesson':
            from apps.courses.models import Lesson
            Lesson.objects.filter(pk=obj_id).update(visible_for_candidates=value)

        return redirect('analytics:visibility')


class CommentModerationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/comment_moderation.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.comments.models import Comment

        context['pending_comments'] = (
            Comment.objects.filter(status=Comment.Status.PENDING)
            .select_related('user', 'moderated_by', 'content_type')
            .order_by('-created_at')
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        comment_id = request.POST.get('comment_id')
        if not action or not comment_id:
            return redirect('analytics:comment_moderation')

        from apps.comments.models import Comment

        c = Comment.objects.filter(pk=comment_id, status=Comment.Status.PENDING).first()
        if not c:
            return redirect('analytics:comment_moderation')

        if action == 'approve':
            c.approve(by_user=request.user)
        elif action == 'reject':
            c.reject(by_user=request.user)

        return redirect('analytics:comment_moderation')
