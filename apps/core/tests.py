"""
Smoke tests — проверка, что все страницы открываются без ошибок.
При изменении шаблонов, URL или views запускать: python manage.py test apps.core.tests
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse


class PageSmokeTests(TestCase):
    """Проход по всем страницам — если что-то сломается, тест упадёт."""

    def setUp(self):
        self.client = Client()

    def test_home(self):
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        r = self.client.get('/login/')
        self.assertEqual(r.status_code, 200)

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
        r = self.client.get(
            reverse('courses:quiz', kwargs={'slug': 'espresso-basics', 'pk': 1})
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

    def test_logout_redirect(self):
        r = self.client.get('/logout/')
        self.assertEqual(r.status_code, 302)

    @override_settings(DEBUG=False)
    def test_404_page(self):
        """Проверяем, что кастомный 404 рендерится."""
        r = self.client.get('/nonexistent-page-xyz/')
        self.assertEqual(r.status_code, 404)
