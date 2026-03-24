"""Course views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .models import Course, Lesson, TestQuestion
from .selectors import get_course_detail, get_courses_for_user, get_lesson_for_user
from .services import mark_lesson_complete, save_quiz_result


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
        return context


class MarkLessonCompleteView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        lesson = get_object_or_404(Lesson, course__slug=slug, pk=pk)
        mark_lesson_complete(request.user, lesson)
        return redirect('courses:lesson_detail', slug=slug, pk=pk)


class QuizView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/quiz.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(
            Lesson,
            course__slug=self.kwargs['slug'],
            pk=self.kwargs['pk'],
            lesson_type='quiz',
        )
        questions = list(lesson.questions.all().order_by('order'))
        context['course'] = lesson.course
        context['lesson'] = lesson
        context['questions'] = questions
        context['course_slug'] = lesson.course.slug
        context['passing_score'] = lesson.passing_score or 70
        return context

    def post(self, request, slug, pk):
        lesson = get_object_or_404(
            Lesson,
            course__slug=slug,
            pk=pk,
            lesson_type='quiz',
        )
        passing = lesson.passing_score or 70
        total = lesson.questions.count()
        if total == 0:
            return redirect('courses:detail', slug=slug)

        correct = 0
        for q in lesson.questions.all().order_by('order'):
            key = f'q_{q.id}'
            val = request.POST.get(key)
            # options are 0-based indices; is_correct at that index
            for i, opt in enumerate(q.options):
                if opt.get('is_correct') and str(i) == val:
                    correct += 1
                    break

        score = int((correct / total) * 100) if total else 0
        save_quiz_result(request.user, lesson, score, passing)
        return redirect('courses:detail', slug=slug)
