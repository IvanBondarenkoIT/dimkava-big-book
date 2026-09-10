"""Course views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView

from .models import LessonRating, UserProgress
from .selectors import get_course_detail, get_courses_for_user, get_lesson_for_user
from .services import mark_lesson_complete, save_quiz_result, record_quiz_attempt
from .quiz_review import effective_passing_score, grade_quiz_submission


class CourseListView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = get_courses_for_user(self.request.user)
        return context


class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = get_course_detail(self.kwargs['slug'], self.request.user)
        if not data:
            context['course'] = None
            context['lessons'] = []
            return context
        context['course'] = data['course']
        context['lessons'] = data['lessons']
        context['course_slug'] = data['course'].slug
        from apps.comments.services import comments_context_for
        context.update(comments_context_for(data['course'], self.request.user))
        return context


class LessonDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/lesson_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = get_lesson_for_user(
            self.kwargs['slug'],
            self.kwargs['pk'],
            self.request.user,
        )
        if not data:
            context['course'] = None
            context['lesson'] = None
            return context
        context['course'] = data['course']
        context['lesson'] = data['lesson']
        context['course_slug'] = data['course'].slug
        context['completed'] = data['completed']
        context['rating'] = data.get('rating')
        context['rating_comment'] = data.get('rating_comment', '')
        return context


class MarkLessonCompleteView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        data = get_lesson_for_user(slug, pk, request.user)
        if not data or not data.get('lesson'):
            return redirect('courses:list')
        lesson = data['lesson']
        mark_lesson_complete(request.user, lesson)
        return redirect('courses:lesson_detail', slug=slug, pk=pk)


class QuizView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/quiz.html'

    def _get_quiz_lesson(self, slug, pk, user):
        data = get_lesson_for_user(slug, pk, user)
        if not data or not data.get('lesson'):
            return None
        lesson = data['lesson']
        if lesson.lesson_type != 'quiz':
            return None
        return lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self._get_quiz_lesson(
            self.kwargs['slug'], self.kwargs['pk'], self.request.user,
        )
        if not lesson:
            context['course'] = None
            context['lesson'] = None
            context['questions'] = []
            context['course_slug'] = self.kwargs['slug']
            context['passing_score'] = 70
            context['quiz_locked'] = False
            context['existing_quiz_score'] = None
            return context
        questions = list(lesson.questions.all().order_by('order'))
        progress = UserProgress.objects.filter(user=self.request.user, lesson=lesson).first()
        quiz_locked = bool(progress and progress.candidate_quiz_locked)
        context['course'] = lesson.course
        context['lesson'] = lesson
        context['questions'] = questions
        context['course_slug'] = lesson.course.slug
        context['passing_score'] = effective_passing_score(lesson)
        context['quiz_locked'] = quiz_locked
        context['existing_quiz_score'] = progress.quiz_score if progress else None
        return context

    def get(self, request, *args, **kwargs):
        lesson = self._get_quiz_lesson(kwargs['slug'], kwargs['pk'], request.user)
        if not lesson:
            return redirect('courses:list')
        return super().get(request, *args, **kwargs)

    def post(self, request, slug, pk):
        lesson = self._get_quiz_lesson(slug, pk, request.user)
        if not lesson:
            return redirect('courses:list')
        progress = UserProgress.objects.filter(user=request.user, lesson=lesson).first()
        if progress and progress.candidate_quiz_locked:
            messages.error(request, _('Retake is locked. Ask HR to review and unlock this quiz.'))
            return redirect('courses:detail', slug=slug)
        passing = effective_passing_score(lesson)
        total = lesson.questions.count()
        if total == 0:
            return redirect('courses:detail', slug=slug)

        score, quiz_answers = grade_quiz_submission(lesson, request.POST)
        save_quiz_result(request.user, lesson, score, passing, quiz_answers=quiz_answers)
        progress = UserProgress.objects.get(user=request.user, lesson=lesson)
        record_quiz_attempt(progress)
        return redirect('courses:detail', slug=slug)


class RateLessonView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        data = get_lesson_for_user(slug, pk, request.user)
        if not data or not data.get('lesson'):
            return redirect('courses:detail', slug=slug)
        lesson = data['lesson']

        try:
            rating = int(request.POST.get('rating') or 0)
        except ValueError:
            rating = 0
        comment = (request.POST.get('comment') or '').strip()
        if rating < 1 or rating > 5:
            return redirect('courses:lesson_detail', slug=slug, pk=pk)

        LessonRating.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'rating': rating, 'comment': comment},
        )
        return redirect('courses:lesson_detail', slug=slug, pk=pk)
