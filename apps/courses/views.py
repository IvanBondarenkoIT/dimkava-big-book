from django.views.generic import TemplateView


class CourseListView(TemplateView):
    template_name = 'courses/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = [
            {'slug': 'espresso-basics', 'title': 'The Art of Espresso', 'category': 'Espresso', 'progress': 65},
            {'slug': 'v60-brewing', 'title': 'V60 Precision Brewing', 'category': 'Brewing', 'progress': 20},
            {'slug': 'coffee-origin', 'title': 'Coffee Origin & Processing', 'category': 'Chemistry', 'progress': 0},
        ]
        return context


class CourseDetailView(TemplateView):
    template_name = 'courses/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs.get('slug', 'espresso-basics')
        context['course_title'] = 'The Art of Espresso'
        context['lessons'] = [
            {'id': 1, 'title': 'Dialing In Basics', 'duration': '15 min', 'completed': True},
            {'id': 2, 'title': 'Tamping Technique', 'duration': '10 min', 'completed': True},
            {'id': 3, 'title': 'Milk Texturing', 'duration': '20 min', 'completed': False},
        ]
        return context


class LessonDetailView(TemplateView):
    template_name = 'courses/lesson_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson_title'] = 'Mastering the Espresso Machine'
        context['duration'] = '5 min'
        return context


class QuizView(TemplateView):
    template_name = 'courses/quiz.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_num'] = 1
        context['total_questions'] = 12
        return context
