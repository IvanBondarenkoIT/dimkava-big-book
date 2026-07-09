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
