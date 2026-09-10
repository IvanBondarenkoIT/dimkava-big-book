"""Model forms for HR content editing."""
from django import forms
from django.utils import timezone

from apps.core.i18n_content import (
    ensure_unique_slug,
    slugify_underscore,
    sync_legacy_fields,
    sync_question_legacy,
)
from apps.courses.models import Course, Lesson, TestQuestion
from apps.departments.models import Role
from apps.knowledge_base.models import Article, KBSection
from apps.news.models import NewsPost
from apps.onboarding.models import OnboardingModule, OnboardingProgram, OnboardingStep

INPUT_CLASS = (
    'w-full rounded-lg bg-surface-container-lowest border border-outline-variant/20 '
    'px-3 py-2 text-sm text-on-surface'
)
TEXTAREA_CLASS = INPUT_CLASS + ' font-mono text-xs min-h-[12rem]'
SLUG_CLASS = INPUT_CLASS + ' font-mono'


def _style_fields(form: forms.ModelForm) -> None:
    for name, field in form.fields.items():
        if isinstance(field.widget, forms.Textarea):
            field.widget.attrs.setdefault('class', TEXTAREA_CLASS)
        elif isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.setdefault('class', 'rounded border-outline-variant/30')
        else:
            field.widget.attrs.setdefault('class', INPUT_CLASS)


class SlugOnCreateMixin:
    """Auto-generate slug on create; keep readonly on edit unless change_slug is checked."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['slug'].widget.attrs['readonly'] = True
            self.fields['slug'].help_text = 'Slug is fixed after creation (check below to change).'
            self.fields['change_slug'] = forms.BooleanField(
                required=False,
                label='Change slug',
                widget=forms.CheckboxInput(attrs={'class': 'rounded border-outline-variant/30'}),
            )
        else:
            self.fields['slug'].required = False
            self.fields['slug'].help_text = 'Leave blank to auto-generate from English title.'

    def clean(self):
        cleaned = super().clean()
        slug = (cleaned.get('slug') or '').strip()
        change = cleaned.get('change_slug', False)
        if self.instance and self.instance.pk and not change:
            cleaned['slug'] = self.instance.slug
        elif not slug:
            title = cleaned.get('title_en') or cleaned.get('title_ru') or ''
            cleaned['slug'] = slugify_underscore(title)
        else:
            cleaned['slug'] = slug
        return cleaned


class ArticleForm(SlugOnCreateMixin, forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'section', 'slug', 'status',
            'title_en', 'title_ru', 'title_ka',
            'content_en', 'content_ru', 'content_ka',
            'review_required_after_days',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'content': 'content'})
        if not obj.pk:
            obj.slug = ensure_unique_slug(
                Article, obj.slug, section=obj.section,
            )
        if commit:
            obj.save()
        return obj


class CourseForm(SlugOnCreateMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'slug', 'status', 'level', 'estimated_minutes', 'visible_for_candidates',
            'title_en', 'title_ru', 'title_ka',
            'description_en', 'description_ru', 'description_ka',
            'image', 'review_required_after_days',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        desc_hint = (
            'Short course summary only — not quiz questions. '
            'Use Add quiz on the course page for questions and answers.'
        )
        for name in ('description_en', 'description_ru', 'description_ka'):
            field = self.fields[name]
            field.help_text = desc_hint
            field.widget.attrs['class'] = INPUT_CLASS + ' text-sm min-h-[4.5rem]'
            field.widget.attrs['rows'] = 3

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'description': 'description'})
        if not obj.pk:
            obj.slug = ensure_unique_slug(Course, obj.slug)
        if commit:
            obj.save()
        return obj


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'title_en', 'title_ru', 'title_ka',
            'content_en', 'content_ru', 'content_ka',
            'order', 'lesson_type', 'video_url', 'estimated_minutes',
            'is_required', 'passing_score', 'visible_for_candidates',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'content': 'content'})
        if commit:
            obj.save()
        return obj


class QuizCreateForm(forms.ModelForm):
    """Minimal create step — questions are edited on QuizEditView after save."""

    class Meta:
        model = Lesson
        fields = [
            'title_en', 'title_ru', 'title_ka',
            'passing_score', 'order',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        self.fields['order'].widget = forms.HiddenInput()
        self.fields['passing_score'].required = False
        self.fields['passing_score'].help_text = 'Percent needed to pass (0–100). Default 70.'

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.lesson_type = 'quiz'
        if obj.passing_score is None:
            obj.passing_score = 70
        sync_legacy_fields(obj, {'title': 'title', 'content': 'content'})
        if commit:
            obj.save()
        return obj


class NewsForm(SlugOnCreateMixin, forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = [
            'slug', 'tag', 'pinned', 'published_at',
            'title_en', 'title_ru', 'title_ka',
            'content_en', 'content_ru', 'content_ka',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        if not self.instance.pk and not self.initial.get('published_at'):
            self.initial['published_at'] = timezone.now()

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'content': 'content'})
        if not obj.pk:
            obj.slug = ensure_unique_slug(NewsPost, obj.slug)
        if commit:
            obj.save()
        return obj


class OnboardingProgramForm(SlugOnCreateMixin, forms.ModelForm):
    class Meta:
        model = OnboardingProgram
        fields = [
            'slug', 'role', 'visible_for_candidates', 'estimated_days',
            'title_en', 'title_ru', 'title_ka',
            'description_en', 'description_ru', 'description_ka',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'description': 'description'})
        if not obj.pk:
            obj.slug = ensure_unique_slug(OnboardingProgram, obj.slug)
        if commit:
            obj.save()
        return obj


class OnboardingModuleForm(forms.ModelForm):
    class Meta:
        model = OnboardingModule
        fields = [
            'title_en', 'title_ru', 'title_ka',
            'description_en', 'description_ru', 'description_ka',
            'order', 'estimated_minutes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'description': 'description'})
        if commit:
            obj.save()
        return obj


class OnboardingStepForm(forms.ModelForm):
    class Meta:
        model = OnboardingStep
        fields = [
            'title_en', 'title_ru', 'title_ka',
            'content_en', 'content_ru', 'content_ka',
            'order',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_legacy_fields(obj, {'title': 'title', 'content': 'content'})
        if commit:
            obj.save()
        return obj


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['title', 'description', 'order', 'required_courses', 'recommended_courses']
        widgets = {
            'required_courses': forms.SelectMultiple(attrs={'class': INPUT_CLASS, 'size': 8}),
            'recommended_courses': forms.SelectMultiple(attrs={'class': INPUT_CLASS, 'size': 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        self.fields['required_courses'].queryset = Course.objects.order_by('title')
        self.fields['recommended_courses'].queryset = Course.objects.order_by('title')


def parse_quiz_options(
    post,
    prefix: str,
    lang: str,
    *,
    previous: list | None = None,
) -> list[dict]:
    """Build options JSON from POST. Preserve prior key if _correct is missing."""
    correct_raw = post.get(f'{prefix}_correct')
    previous = previous or []
    previous_key = {
        i for i, opt in enumerate(previous) if opt.get('is_correct')
    }
    options = []
    for i in range(4):
        text = (post.get(f'{prefix}_opt{i}_{lang}') or '').strip()
        if not text and i >= len(previous):
            continue
        if correct_raw is None or correct_raw == '':
            is_correct = i in previous_key
        else:
            is_correct = str(i) == str(correct_raw)
        if text or is_correct or i < len(previous):
            options.append({
                'text': text if text else (previous[i].get('text', '') if i < len(previous) else ''),
                'is_correct': is_correct,
            })
    # Drop trailing empty options that are not marked correct
    while options and not options[-1].get('text') and not options[-1].get('is_correct'):
        options.pop()
    return options


def save_quiz_from_post(lesson: Lesson, post) -> None:
    """Persist quiz title, passing score, and questions from POST without wiping answer keys."""
    previous_title = lesson.title
    lesson.title_en = (post.get('title_en') or '').strip()
    lesson.title_ru = (post.get('title_ru') or '').strip()
    lesson.title_ka = (post.get('title_ka') or '').strip()
    sync_legacy_fields(lesson, {'title': 'title'})
    if not lesson.title:
        lesson.title = previous_title or 'Quiz'

    question_ids = [int(x) for x in post.getlist('question_ids') if x.isdigit()]
    for qid in question_ids:
        prefix = f'q_{qid}'
        try:
            question = TestQuestion.objects.get(pk=qid, lesson=lesson)
        except TestQuestion.DoesNotExist:
            continue
        question.question_text_en = post.get(f'{prefix}_text_en', '')
        question.question_text_ru = post.get(f'{prefix}_text_ru', '')
        question.question_text_ka = post.get(f'{prefix}_text_ka', '')
        question.options_en = parse_quiz_options(
            post, prefix, 'en', previous=question.options_en or question.options or [],
        )
        question.options_ru = parse_quiz_options(
            post, prefix, 'ru', previous=question.options_ru or [],
        )
        question.options_ka = parse_quiz_options(
            post, prefix, 'ka', previous=question.options_ka or [],
        )
        sync_question_legacy(question)
        question.save()

    update_fields = ['title', 'title_en', 'title_ru', 'title_ka']
    passing = post.get('passing_score', '').strip()
    if passing.isdigit():
        lesson.passing_score = int(passing)
        update_fields.append('passing_score')
    lesson.save(update_fields=update_fields)
