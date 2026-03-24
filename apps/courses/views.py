from django.views.generic import TemplateView


class CourseListView(TemplateView):
    template_name = 'courses/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = [
            {'slug': 'espresso-basics', 'title': 'The Art of Espresso', 'description': 'Master the fundamentals of extraction, puck prep, and sensory analysis.', 'category': 'Espresso', 'progress': 65, 'lessons_count': 3, 'image': 'https://images.unsplash.com/photo-1510972527921-ce03766a1cf1?q=80&w=800&auto=format&fit=crop'},
            {'slug': 'v60-brewing', 'title': 'V60 Precision Brewing', 'description': 'Learn the chemistry of pour-over and how to manipulate variables for clarity.', 'category': 'Brewing', 'progress': 20, 'lessons_count': 2, 'image': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=800&auto=format&fit=crop'},
            {'slug': 'coffee-origin', 'title': 'Coffee Origin & Processing', 'description': 'Explore how terroir and processing methods affect the final cup profile.', 'category': 'Chemistry', 'progress': 0, 'lessons_count': 0, 'image': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?q=80&w=800&auto=format&fit=crop'},
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
        context['course_slug'] = self.kwargs.get('slug', 'espresso-basics')
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
