"""Analytics views — HR/Admin only."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from .permissions import user_can_view_analytics
from .content_review_selectors import get_content_to_review
from .hr_selectors import get_candidate_rows, get_quiz_catalog_rows, get_quiz_taker_rows
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


class OnboardingFeedbackModerationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/onboarding_feedback_moderation.html'

    def test_func(self):
        return user_can_view_analytics(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Q
        from apps.onboarding.models import OnboardingFeedback

        program_id = (self.request.GET.get('program') or '').strip()
        rating = (self.request.GET.get('rating') or '').strip()
        q = (self.request.GET.get('q') or '').strip()

        pending_qs = (
            OnboardingFeedback.objects.filter(status=OnboardingFeedback.Status.PENDING)
            .select_related('user', 'program', 'moderated_by')
            .order_by('-updated_at', '-id')
        )
        if program_id.isdigit():
            pending_qs = pending_qs.filter(program_id=int(program_id))
        if rating.isdigit():
            pending_qs = pending_qs.filter(rating=int(rating))
        if q:
            pending_qs = pending_qs.filter(
                Q(user__username__icontains=q)
                | Q(user__email__icontains=q)
                | Q(comment__icontains=q)
                | Q(program__title__icontains=q)
            )

        context['pending_feedback'] = pending_qs
        context['program_filter'] = program_id
        context['rating_filter'] = rating
        context['query_filter'] = q
        context['program_options'] = (
            OnboardingFeedback.objects.filter(status=OnboardingFeedback.Status.PENDING)
            .select_related('program')
            .values('program_id', 'program__title')
            .order_by('program__title')
            .distinct()
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        feedback_id = request.POST.get('feedback_id')
        if not action or not feedback_id:
            return redirect('analytics:onboarding_feedback_moderation')

        from apps.onboarding.models import OnboardingFeedback

        fb = OnboardingFeedback.objects.filter(pk=feedback_id, status=OnboardingFeedback.Status.PENDING).first()
        if not fb:
            return redirect('analytics:onboarding_feedback_moderation')

        if action == 'approve':
            fb.approve(by_user=request.user)
        elif action == 'reject':
            fb.reject(by_user=request.user)

        return redirect('analytics:onboarding_feedback_moderation')


class _HRQuizMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return user_can_view_analytics(self.request.user)


class QuizResultsListView(_HRQuizMixin, TemplateView):
    template_name = 'analytics/quiz_results_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        context['query_filter'] = q
        context['quizzes'] = get_quiz_catalog_rows(q=q)
        return context


class QuizResultsTakersView(_HRQuizMixin, TemplateView):
    template_name = 'analytics/quiz_results_takers.html'

    def get_context_data(self, **kwargs):
        from apps.courses.models import Lesson

        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(
            Lesson.objects.select_related('course'),
            pk=self.kwargs['lesson_id'],
            lesson_type='quiz',
        )
        candidates_only = self.request.GET.get('candidates') in ('1', 'true', 'yes')
        failed_only = self.request.GET.get('failed') in ('1', 'true', 'yes')
        locked_only = self.request.GET.get('locked') in ('1', 'true', 'yes')
        context['lesson'] = lesson
        from apps.courses.quiz_review import effective_passing_score

        context['passing_score'] = effective_passing_score(lesson)
        context['candidates_only'] = candidates_only
        context['failed_only'] = failed_only
        context['locked_only'] = locked_only
        context['takers'] = get_quiz_taker_rows(
            lesson,
            candidates_only=candidates_only,
            failed_only=failed_only,
            locked_only=locked_only,
        )
        return context


class QuizResultsDetailView(_HRQuizMixin, TemplateView):
    template_name = 'analytics/quiz_results_detail.html'

    def _get_progress(self):
        from django.contrib.auth import get_user_model

        from apps.courses.models import Lesson, UserProgress

        User = get_user_model()
        lesson = get_object_or_404(
            Lesson.objects.select_related('course'),
            pk=self.kwargs['lesson_id'],
            lesson_type='quiz',
        )
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        progress = get_object_or_404(
            UserProgress.objects.select_related(
                'user', 'user__profile', 'lesson', 'candidate_retake_unlocked_by'
            ),
            lesson=lesson,
            user=user,
            quiz_score__isnull=False,
        )
        return lesson, user, progress

    def get_context_data(self, **kwargs):
        from apps.courses.quiz_review import (
            build_quiz_review_rows,
            effective_passing_score,
            summarize_review_rows,
        )

        context = super().get_context_data(**kwargs)
        lesson, user, progress = self._get_progress()
        passing = effective_passing_score(lesson)
        profile = getattr(user, 'profile', None)
        has_stored_answers = bool(progress.quiz_answers)
        review_rows = build_quiz_review_rows(
            lesson,
            progress.quiz_answers if has_stored_answers else None,
        )
        summary = summarize_review_rows(review_rows)

        context['lesson'] = lesson
        context['result_user'] = user
        context['progress'] = progress
        context['passing_score'] = passing
        context['passed'] = (progress.quiz_score or 0) >= passing
        context['is_candidate'] = bool(profile and profile.is_candidate)
        context['display_name'] = (
            profile.get_public_username() if profile else (user.email or user.username)
        )
        context['has_stored_answers'] = has_stored_answers
        context['review_rows'] = review_rows
        context['correct_count'] = summary['correct_count']
        context['wrong_count'] = summary['wrong_count']
        context['answered_count'] = summary['answered_count']
        context['unanswered_count'] = summary['unanswered_count']
        context['question_count'] = summary['question_count']
        context['missing_key_count'] = summary['missing_key_count']
        context['quiz_edit_url'] = reverse(
            'content_editor:quiz_edit',
            kwargs={'course_slug': lesson.course.slug, 'pk': lesson.pk},
        )
        return context

    def post(self, request, *args, **kwargs):
        from apps.courses.services import unlock_quiz_retake

        lesson, user, progress = self._get_progress()
        if (
            request.POST.get('action') == 'unlock'
            and progress.lesson.lesson_type == 'quiz'
            and progress.candidate_quiz_locked
        ):
            unlock_quiz_retake(progress, by_user=request.user)
            messages.success(
                request,
                _('Retake allowed. Attempts so far: %(count)s.') % {
                    'count': progress.quiz_attempts_count,
                },
            )
        return redirect(
            'analytics:quiz_results_detail',
            lesson_id=lesson.pk,
            user_id=user.pk,
        )
