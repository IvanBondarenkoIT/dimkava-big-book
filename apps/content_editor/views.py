"""HR content editor views."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.content_editor.forms import (
    ArticleForm,
    CourseForm,
    LessonForm,
    NewsForm,
    OnboardingModuleForm,
    OnboardingProgramForm,
    OnboardingStepForm,
    RoleForm,
    save_quiz_from_post,
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
        return reverse(
            'courses:lesson_detail',
            kwargs={'slug': self.object.course.slug, 'pk': self.object.pk},
        )


class QuizEditView(ContentEditorRequiredMixin, TemplateView):
    template_name = 'content_editor/quiz_form.html'

    @staticmethod
    def _options_for_lang(question, lang: str) -> list:
        opts = getattr(question, f'options_{lang}') or question.options_en or question.options or []
        result = []
        for i in range(4):
            if i < len(opts):
                result.append(opts[i])
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
        lesson = self.get_lesson()
        questions = []
        for q in lesson.questions.order_by('order'):
            questions.append({
                'pk': q.pk,
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
            kwargs={'module_slug': self.object.slug},
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
        return reverse('onboarding:module_detail', kwargs={'module_slug': self.object.slug})


class OnboardingStepEditView(ContentEditorRequiredMixin, UpdateView):
    model = OnboardingStep
    form_class = OnboardingStepForm
    template_name = 'content_editor/form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit onboarding step')
        module = self.object.module
        ctx['cancel_url'] = reverse('onboarding:module_detail', kwargs={'module_slug': module.slug})
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
            kwargs={'module_slug': self.object.module.slug},
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
