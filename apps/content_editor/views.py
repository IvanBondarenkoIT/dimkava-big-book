"""HR content editor views."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.content_editor.forms import (
    ArticleForm,
    CourseForm,
    LessonForm,
    NewsForm,
    OnboardingModuleForm,
    OnboardingProgramForm,
    OnboardingStepForm,
    QuizCreateForm,
    RoleForm,
    save_quiz_from_post,
)
from apps.content_editor.lesson_create import (
    create_blank_quiz_questions,
    create_blank_test_question,
    next_lesson_order,
)
from apps.content_editor.mixins import ContentEditorRequiredMixin
from apps.courses.models import Course, Lesson
from apps.departments.models import Role
from apps.knowledge_base.models import Article, KBSection
from apps.news.models import NewsPost
from apps.onboarding.models import OnboardingModule, OnboardingProgram, OnboardingStep


class ArticleEditView(ContentEditorRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'content_editor/form.html'
    context_object_name = 'object'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Article,
            section__slug=self.kwargs['section'],
            slug=self.kwargs['slug'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit article')
        ctx['cancel_url'] = reverse(
            'knowledge_base:article',
            kwargs={'section': self.object.section.slug, 'slug': self.object.slug},
        )
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Article saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'knowledge_base:article',
            kwargs={'section': self.object.section.slug, 'slug': self.object.slug},
        )


class ArticleCreateView(ContentEditorRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'content_editor/form.html'

    def get_initial(self):
        initial = super().get_initial()
        section_slug = self.request.GET.get('section')
        if section_slug:
            section = KBSection.objects.filter(slug=section_slug).first()
            if section:
                initial['section'] = section
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('New article')
        ctx['cancel_url'] = reverse('knowledge_base:home')
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Article created.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'knowledge_base:article',
            kwargs={'section': self.object.section.slug, 'slug': self.object.slug},
        )


class CourseEditView(ContentEditorRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'content_editor/form.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit course')
        ctx['cancel_url'] = reverse('courses:detail', kwargs={'slug': self.object.slug})
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('description', _('Description')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Course saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.object.slug})


class CourseCreateView(ContentEditorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'content_editor/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('New course')
        ctx['cancel_url'] = reverse('courses:list')
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('description', _('Description')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Course created.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.object.slug})


class LessonEditView(ContentEditorRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'content_editor/form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit lesson')
        ctx['cancel_url'] = reverse(
            'courses:lesson_detail',
            kwargs={'slug': self.object.course.slug, 'pk': self.object.pk},
        )
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Lesson saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.lesson_type == 'quiz':
            return reverse(
                'content_editor:quiz_edit',
                kwargs={'course_slug': self.object.course.slug, 'pk': self.object.pk},
            )
        return reverse(
            'courses:lesson_detail',
            kwargs={'slug': self.object.course.slug, 'pk': self.object.pk},
        )


class LessonCreateView(ContentEditorRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'content_editor/form.html'

    def get_course(self):
        return get_object_or_404(Course, slug=self.kwargs['course_slug'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Quizzes use QuizCreateView — keep lesson types non-quiz here.
        form.fields['lesson_type'].choices = [
            (value, label)
            for value, label in form.fields['lesson_type'].choices
            if value and value != 'quiz'
        ]
        return form

    def get_initial(self):
        initial = super().get_initial()
        course = self.get_course()
        initial['order'] = next_lesson_order(course)
        initial['lesson_type'] = 'text'
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.get_course()
        ctx['page_title'] = _('New lesson')
        ctx['cancel_url'] = reverse('courses:detail', kwargs={'slug': course.slug})
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        course = self.get_course()
        form.instance.course = course
        if not form.instance.order:
            form.instance.order = next_lesson_order(course)
        messages.success(self.request, _('Lesson created.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'courses:lesson_detail',
            kwargs={'slug': self.object.course.slug, 'pk': self.object.pk},
        )


class QuizCreateView(ContentEditorRequiredMixin, CreateView):
    """Create a quiz lesson under a course, with blank questions for the quiz editor."""

    model = Lesson
    form_class = QuizCreateForm
    template_name = 'content_editor/form.html'

    def get_course(self):
        return get_object_or_404(Course, slug=self.kwargs['course_slug'])

    def get_initial(self):
        initial = super().get_initial()
        course = self.get_course()
        initial['order'] = next_lesson_order(course)
        initial['passing_score'] = 70
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.get_course()
        ctx['page_title'] = _('New quiz')
        ctx['cancel_url'] = reverse('courses:detail', kwargs={'slug': course.slug})
        ctx['i18n_fields'] = [
            ('title', _('Title')),
        ]
        ctx['form_hint'] = _(
            'Enter the quiz title, then continue. Questions, answer options, and the '
            'correct answer key are on the next screen.'
        )
        ctx['submit_label'] = _('Continue to questions')
        return ctx

    def form_valid(self, form):
        course = self.get_course()
        form.instance.course = course
        form.instance.lesson_type = 'quiz'
        if not form.instance.order:
            form.instance.order = next_lesson_order(course)
        if form.instance.passing_score is None:
            form.instance.passing_score = 70
        response = super().form_valid(form)
        create_blank_quiz_questions(self.object, count=3)
        messages.success(self.request, _('Quiz created. Add questions and the answer key.'))
        return response

    def get_success_url(self):
        return reverse(
            'content_editor:quiz_edit',
            kwargs={'course_slug': self.object.course.slug, 'pk': self.object.pk},
        )


class QuizQuestionAddView(ContentEditorRequiredMixin, View):
    """POST: append a blank question to an existing quiz lesson."""

    def post(self, request, course_slug, pk):
        lesson = get_object_or_404(
            Lesson,
            pk=pk,
            course__slug=course_slug,
            lesson_type='quiz',
        )
        create_blank_test_question(lesson)
        messages.success(request, _('Question added.'))
        return redirect(
            'content_editor:quiz_edit',
            course_slug=lesson.course.slug,
            pk=lesson.pk,
        )


class QuizEditView(ContentEditorRequiredMixin, TemplateView):
    template_name = 'content_editor/quiz_form.html'

    @staticmethod
    def _options_for_lang(question, lang: str) -> list:
        from apps.courses.quiz_review import answer_key, has_answer_key

        opts = getattr(question, f'options_{lang}') or question.options_en or question.options or []
        key = answer_key(question) if has_answer_key(question) else set()
        # Mark only the first correct index for radio UI (one checked per group).
        first_correct = min(key) if key else None
        result = []
        for i in range(4):
            if i < len(opts):
                opt = dict(opts[i])
                opt['is_correct'] = first_correct is not None and i == first_correct
                result.append(opt)
            else:
                result.append({'text': '', 'is_correct': False})
        return result

    def get_lesson(self):
        return get_object_or_404(
            Lesson,
            pk=self.kwargs['pk'],
            course__slug=self.kwargs['course_slug'],
            lesson_type='quiz',
        )

    def get_context_data(self, **kwargs):
        from apps.courses.quiz_review import effective_passing_score, has_answer_key

        lesson = self.get_lesson()
        questions = []
        missing_keys = 0
        for q in lesson.questions.order_by('order'):
            if not has_answer_key(q):
                missing_keys += 1
            questions.append({
                'pk': q.pk,
                'has_key': has_answer_key(q),
                'langs': [
                    {
                        'code': 'en',
                        'label': 'English',
                        'text': q.question_text_en or q.question_text,
                        'options': self._options_for_lang(q, 'en'),
                    },
                    {
                        'code': 'ru',
                        'label': 'Русский',
                        'text': q.question_text_ru or '',
                        'options': self._options_for_lang(q, 'ru'),
                    },
                    {
                        'code': 'ka',
                        'label': 'ქართული',
                        'text': q.question_text_ka or '',
                        'options': self._options_for_lang(q, 'ka'),
                    },
                ],
            })
        return {
            **super().get_context_data(**kwargs),
            'lesson': lesson,
            'course': lesson.course,
            'questions': questions,
            'missing_key_count': missing_keys,
            'effective_passing_score': effective_passing_score(lesson),
            'page_title': _('Edit quiz'),
            'cancel_url': reverse('courses:quiz', kwargs={
                'slug': lesson.course.slug,
                'pk': lesson.pk,
            }),
        }

    def post(self, request, *args, **kwargs):
        lesson = self.get_lesson()
        save_quiz_from_post(lesson, request.POST)
        messages.success(request, _('Quiz saved.'))
        return redirect('courses:quiz', slug=lesson.course.slug, pk=lesson.pk)


class NewsEditView(ContentEditorRequiredMixin, UpdateView):
    model = NewsPost
    form_class = NewsForm
    template_name = 'content_editor/form.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit news')
        ctx['cancel_url'] = reverse('news:detail', kwargs={'slug': self.object.slug})
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('News post saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('news:detail', kwargs={'slug': self.object.slug})


class NewsCreateView(ContentEditorRequiredMixin, CreateView):
    model = NewsPost
    form_class = NewsForm
    template_name = 'content_editor/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('New news post')
        ctx['cancel_url'] = reverse('news:list')
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('News post created.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('news:detail', kwargs={'slug': self.object.slug})


class OnboardingProgramEditView(ContentEditorRequiredMixin, UpdateView):
    model = OnboardingProgram
    form_class = OnboardingProgramForm
    template_name = 'content_editor/form.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit onboarding program')
        ctx['cancel_url'] = reverse('onboarding:overview')
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('description', _('Description')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Program saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('onboarding:overview')


class OnboardingModuleEditView(ContentEditorRequiredMixin, UpdateView):
    model = OnboardingModule
    form_class = OnboardingModuleForm
    template_name = 'content_editor/form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit onboarding module')
        ctx['cancel_url'] = reverse(
            'onboarding:module_detail',
            kwargs={'slug': self.object.slug},
        )
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('description', _('Description')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Module saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('onboarding:module_detail', kwargs={'slug': self.object.slug})


class OnboardingStepEditView(ContentEditorRequiredMixin, UpdateView):
    model = OnboardingStep
    form_class = OnboardingStepForm
    template_name = 'content_editor/form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit onboarding step')
        module = self.object.module
        ctx['cancel_url'] = reverse('onboarding:module_detail', kwargs={'slug': module.slug})
        ctx['i18n_fields'] = [
            ('title', _('Title')),
            ('content', _('Content')),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Step saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'onboarding:module_detail',
            kwargs={'slug': self.object.module.slug},
        )


class RoleEditView(ContentEditorRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'content_editor/role_form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit role')
        ctx['cancel_url'] = reverse(
            'departments:detail',
            kwargs={'slug': self.object.department.slug},
        )
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Role saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('departments:detail', kwargs={'slug': self.object.department.slug})
