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
