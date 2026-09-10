"""Tests for HR content editor."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.courses.models import Course, Lesson
from apps.knowledge_base.models import Article, KBSection

User = get_user_model()


class ContentEditorPermissionsTest(TestCase):
    def setUp(self):
        self.section = KBSection.objects.create(slug='proc', title='Procedures', order=0)
        self.article = Article.objects.create(
            section=self.section,
            slug='test-article',
            title='Test',
            title_en='Test EN',
            title_ru='Тест RU',
            content_ru='Содержание',
            status='published',
        )
        self.employee = User.objects.create_user(username='emp', password='test')
        self.hr = User.objects.create_user(username='hr', password='test')
        hr_group, _ = Group.objects.get_or_create(name='hr_manager')
        self.hr.groups.add(hr_group)
        self.edit_url = reverse(
            'content_editor:article_edit',
            kwargs={'section': self.section.slug, 'slug': self.article.slug},
        )

    def test_employee_cannot_access_edit(self):
        self.client.login(username='emp', password='test')
        resp = self.client.get(self.edit_url)
        self.assertEqual(resp.status_code, 403)

    def test_employee_cannot_access_create(self):
        self.client.login(username='emp', password='test')
        resp = self.client.get(reverse('content_editor:article_create'))
        self.assertEqual(resp.status_code, 403)

    def test_employee_cannot_access_course_create(self):
        self.client.login(username='emp', password='test')
        resp = self.client.get(reverse('content_editor:course_create'))
        self.assertEqual(resp.status_code, 403)

    def test_hr_can_access_edit(self):
        self.client.login(username='hr', password='test')
        resp = self.client.get(self.edit_url)
        self.assertEqual(resp.status_code, 200)

    def test_hr_save_syncs_legacy_title(self):
        self.client.login(username='hr', password='test')
        resp = self.client.post(self.edit_url, {
            'section': self.section.pk,
            'slug': self.article.slug,
            'status': 'published',
            'title_en': 'Updated EN',
            'title_ru': 'Обновлено RU',
            'title_ka': '',
            'content_en': 'Body EN',
            'content_ru': 'Тело RU',
            'content_ka': '',
            'review_required_after_days': 180,
        })
        self.assertEqual(resp.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated EN')
        self.assertEqual(self.article.title_en, 'Updated EN')
        self.assertEqual(self.article.content_ru, 'Тело RU')


class QuizEditViewTest(TestCase):
    def setUp(self):
        self.hr = User.objects.create_user(username='hr2', password='test')
        hr_group, _ = Group.objects.get_or_create(name='hr_manager')
        self.hr.groups.add(hr_group)
        course = Course.objects.create(
            title='Regulations',
            slug='regulations',
            status='published',
        )
        self.lesson = Lesson.objects.create(
            course=course,
            title='Quiz',
            order=1,
            lesson_type='quiz',
            passing_score=70,
        )
        self.edit_url = reverse(
            'content_editor:quiz_edit',
            kwargs={'course_slug': 'regulations', 'pk': self.lesson.pk},
        )

    def test_hr_can_open_quiz_edit(self):
        self.client.login(username='hr2', password='test')
        resp = self.client.get(self.edit_url)
        self.assertEqual(resp.status_code, 200)

    def test_save_preserves_answer_key_when_correct_missing(self):
        from apps.content_editor.forms import parse_quiz_options

        previous = [
            {'text': 'A', 'is_correct': False},
            {'text': 'B', 'is_correct': True},
        ]
        # No q_1_correct in POST — must keep index 1.
        post = {
            'q_1_opt0_en': 'A',
            'q_1_opt1_en': 'B',
        }
        opts = parse_quiz_options(post, 'q_1', 'en', previous=previous)
        self.assertEqual([o['is_correct'] for o in opts], [False, True])


class OnboardingEditorTests(TestCase):
    def setUp(self):
        from apps.onboarding.models import OnboardingModule, OnboardingProgram, OnboardingStep

        self.employee = User.objects.create_user(username='emp-ob', password='test')
        self.hr = User.objects.create_user(username='hr-ob', password='test')
        hr_group, _ = Group.objects.get_or_create(name='hr_manager')
        self.hr.groups.add(hr_group)
        program = OnboardingProgram.objects.create(slug='ob-edit', title='Onboarding')
        self.module = OnboardingModule.objects.create(
            program=program, slug='week-1', title='Week 1', order=0,
        )
        self.step = OnboardingStep.objects.create(
            module=self.module, order=1, title='Step 1', content='Body',
        )

    def test_employee_cannot_edit_onboarding_step(self):
        self.client.login(username='emp-ob', password='test')
        resp = self.client.get(reverse('content_editor:onboarding_step_edit', kwargs={'pk': self.step.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_hr_can_open_module_and_step_edit(self):
        self.client.login(username='hr-ob', password='test')
        module_url = reverse('content_editor:onboarding_module_edit', kwargs={'pk': self.module.pk})
        step_url = reverse('content_editor:onboarding_step_edit', kwargs={'pk': self.step.pk})
        self.assertEqual(self.client.get(module_url).status_code, 200)
        self.assertEqual(self.client.get(step_url).status_code, 200)

    def test_hr_save_step_redirects_to_module_detail(self):
        self.client.login(username='hr-ob', password='test')
        url = reverse('content_editor:onboarding_step_edit', kwargs={'pk': self.step.pk})
        resp = self.client.post(url, {
            'title_en': 'Step EN',
            'title_ru': 'Шаг RU',
            'title_ka': 'ნაბიჯი',
            'content_en': 'EN body',
            'content_ru': 'RU body',
            'content_ka': 'KA body',
            'order': 1,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('onboarding:module_detail', kwargs={'slug': self.module.slug}))
        self.step.refresh_from_db()
        self.assertEqual(self.step.title, 'Step EN')
        self.assertEqual(self.step.title_ka, 'ნაბიჯი')


class LessonQuizCreateTests(TestCase):
    def setUp(self):
        self.employee = User.objects.create_user(username='emp-lq', password='test')
        self.hr = User.objects.create_user(username='hr-lq', password='test')
        hr_group, _ = Group.objects.get_or_create(name='hr_manager')
        self.hr.groups.add(hr_group)
        self.course = Course.objects.create(
            title='Autumn promotions',
            slug='autumn-promotions',
            status='draft',
        )
        self.lesson_create_url = reverse(
            'content_editor:lesson_create',
            kwargs={'course_slug': self.course.slug},
        )
        self.quiz_create_url = reverse(
            'content_editor:quiz_create',
            kwargs={'course_slug': self.course.slug},
        )

    def _lesson_post(self, **overrides):
        data = {
            'title_en': 'Welcome',
            'title_ru': 'Добро пожаловать',
            'title_ka': '',
            'content_en': 'Body EN',
            'content_ru': 'Тело RU',
            'content_ka': '',
            'order': 1,
            'lesson_type': 'text',
            'video_url': '',
            'estimated_minutes': 5,
            'is_required': 'on',
            'passing_score': '',
        }
        data.update(overrides)
        return data

    def test_employee_cannot_create_lesson_or_quiz(self):
        self.client.login(username='emp-lq', password='test')
        self.assertEqual(self.client.get(self.lesson_create_url).status_code, 403)
        self.assertEqual(self.client.get(self.quiz_create_url).status_code, 403)

    def test_hr_creates_lesson_with_order(self):
        Lesson.objects.create(
            course=self.course,
            title='Existing',
            order=1,
            lesson_type='text',
        )
        self.client.login(username='hr-lq', password='test')
        resp = self.client.post(self.lesson_create_url, self._lesson_post(order=2))
        self.assertEqual(resp.status_code, 302)
        lesson = Lesson.objects.get(course=self.course, order=2)
        self.assertEqual(lesson.course_id, self.course.pk)
        self.assertEqual(lesson.lesson_type, 'text')
        self.assertEqual(lesson.title, 'Welcome')
        self.assertEqual(
            resp.url,
            reverse('courses:lesson_detail', kwargs={'slug': self.course.slug, 'pk': lesson.pk}),
        )

    def test_hr_creates_quiz_with_blank_questions(self):
        self.client.login(username='hr-lq', password='test')
        resp = self.client.post(
            self.quiz_create_url,
            self._lesson_post(
                title_en='Promo quiz',
                title_ru='Квиз акций',
                lesson_type='quiz',
                order=1,
                passing_score=70,
                content_en='',
                content_ru='',
            ),
        )
        self.assertEqual(resp.status_code, 302)
        quiz = Lesson.objects.get(course=self.course, lesson_type='quiz')
        self.assertGreaterEqual(quiz.questions.count(), 1)
        self.assertEqual(
            resp.url,
            reverse(
                'content_editor:quiz_edit',
                kwargs={'course_slug': self.course.slug, 'pk': quiz.pk},
            ),
        )
        edit_resp = self.client.get(resp.url)
        self.assertEqual(edit_resp.status_code, 200)

    def test_hr_adds_quiz_question(self):
        quiz = Lesson.objects.create(
            course=self.course,
            title='Quiz',
            order=1,
            lesson_type='quiz',
            passing_score=70,
        )
        from apps.content_editor.lesson_create import create_blank_test_question

        create_blank_test_question(quiz)
        before = quiz.questions.count()
        add_url = reverse(
            'content_editor:quiz_question_add',
            kwargs={'course_slug': self.course.slug, 'pk': quiz.pk},
        )
        self.client.login(username='hr-lq', password='test')
        resp = self.client.post(add_url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(quiz.questions.count(), before + 1)
