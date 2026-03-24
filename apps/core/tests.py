"""
Smoke tests — проверка, что все страницы открываются без ошибок.
При изменении шаблонов, URL или views запускать: python manage.py test apps.core.tests
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, Client, override_settings
from django.urls import reverse

User = get_user_model()


class PageSmokeTests(TestCase):
    """Проход по всем страницам — если что-то сломается, тест упадёт."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test@dimkava.ge', password='testpass')
        hr_group, _ = Group.objects.get_or_create(name='hr_manager')
        self.user.groups.add(hr_group)
        self.client.login(username='test@dimkava.ge', password='testpass')
        # Seed data for smoke tests
        from django.core.management import call_command
        call_command('load_courses', verbosity=0)
        call_command('load_articles', verbosity=0)
        call_command('load_news', verbosity=0)
        call_command('load_departments', verbosity=0)

    def test_home(self):
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        r = self.client.get('/login/')
        self.assertEqual(r.status_code, 200)

    def test_profile_redirect_when_anonymous(self):
        self.client.logout()
        r = self.client.get(reverse('accounts:profile'))
        self.assertEqual(r.status_code, 302)

    def test_profile(self):
        r = self.client.get(reverse('accounts:profile'))
        self.assertEqual(r.status_code, 200)

    def test_courses_list(self):
        r = self.client.get(reverse('courses:list'))
        self.assertEqual(r.status_code, 200)

    def test_courses_detail(self):
        r = self.client.get(reverse('courses:detail', kwargs={'slug': 'espresso-basics'}))
        self.assertEqual(r.status_code, 200)

    def test_lesson_detail(self):
        r = self.client.get(
            reverse('courses:lesson_detail', kwargs={'slug': 'espresso-basics', 'pk': 1})
        )
        self.assertEqual(r.status_code, 200)

    def test_quiz(self):
        from apps.courses.models import Lesson
        quiz_lesson = Lesson.objects.filter(course__slug='espresso-basics', lesson_type='quiz').first()
        if not quiz_lesson:
            self.skipTest('No quiz lesson in seed')
        r = self.client.get(
            reverse('courses:quiz', kwargs={'slug': 'espresso-basics', 'pk': quiz_lesson.pk})
        )
        self.assertEqual(r.status_code, 200)

    def test_onboarding_overview(self):
        r = self.client.get(reverse('onboarding:overview'))
        self.assertEqual(r.status_code, 200)

    def test_onboarding_module_detail(self):
        r = self.client.get(
            reverse('onboarding:module_detail', kwargs={'slug': 'day-1'})
        )
        self.assertEqual(r.status_code, 200)

    def test_knowledge_base_home(self):
        r = self.client.get(reverse('knowledge_base:home'))
        self.assertEqual(r.status_code, 200)

    def test_knowledge_base_section(self):
        r = self.client.get(
            reverse('knowledge_base:section', kwargs={'section': 'procedures'})
        )
        self.assertEqual(r.status_code, 200)

    def test_knowledge_base_article(self):
        r = self.client.get(
            reverse('knowledge_base:article', kwargs={'section': 'procedures', 'slug': 'daily-checklist'})
        )
        self.assertEqual(r.status_code, 200)

    def test_news_list(self):
        r = self.client.get(reverse('news:list'))
        self.assertEqual(r.status_code, 200)

    def test_news_detail(self):
        r = self.client.get(
            reverse('news:detail', kwargs={'slug': 'welcome-2024'})
        )
        self.assertEqual(r.status_code, 200)

    def test_departments_list(self):
        r = self.client.get(reverse('departments:list'))
        self.assertEqual(r.status_code, 200)

    def test_departments_detail(self):
        r = self.client.get(
            reverse('departments:detail', kwargs={'slug': 'retail-store'})
        )
        self.assertEqual(r.status_code, 200)

    def test_analytics_dashboard(self):
        r = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_notifications_list(self):
        r = self.client.get(reverse('notifications:list'))
        self.assertEqual(r.status_code, 200)

    def test_search_results(self):
        r = self.client.get(reverse('search:results'))
        self.assertEqual(r.status_code, 200)

    def test_search_results_with_query(self):
        r = self.client.get(reverse('search:results') + '?q=coffee')
        self.assertEqual(r.status_code, 200)

    def test_admin_login(self):
        r = self.client.get('/admin/')
        self.assertIn(r.status_code, (200, 302))

    def test_logout(self):
        """Logout via POST redirects to login."""
        self.client.login(username='test@dimkava.ge', password='testpass')
        r = self.client.post('/logout/')
        self.assertEqual(r.status_code, 302)

    def test_password_reset(self):
        r = self.client.get(reverse('password_reset'))
        self.assertEqual(r.status_code, 200)

    def test_login_post_success(self):
        r = self.client.post('/login/', {'username': 'test@dimkava.ge', 'password': 'testpass'})
        self.assertEqual(r.status_code, 302)

    @override_settings(DEBUG=False)
    def test_404_page(self):
        """Проверяем, что кастомный 404 рендерится."""
        r = self.client.get('/nonexistent-page-xyz/')
        self.assertEqual(r.status_code, 404)
