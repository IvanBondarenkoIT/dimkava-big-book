"""Analytics tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.analytics.selectors import get_analytics_metrics

User = get_user_model()


class AnalyticsSelectorsTests(TestCase):
    """Unit tests for analytics selectors."""

    def test_get_analytics_metrics_empty(self):
        """Metrics with no data."""
        m = get_analytics_metrics()
        self.assertEqual(m['active_courses'], 0)
        self.assertEqual(m['onboarding_in_progress'], 0)
        self.assertEqual(m['onboarding_completion_rate'], 0)
        self.assertIsNone(m['avg_onboarding_days'])
        self.assertEqual(m['course_completion_rate'], 0)
        self.assertEqual(m['total_users'], 0)

    def test_get_analytics_metrics_with_courses(self):
        """Active courses count."""
        from apps.courses.models import Course
        Course.objects.create(slug='test', title='Test', status='published')
        Course.objects.create(slug='draft', title='Draft', status='draft')
        m = get_analytics_metrics()
        self.assertEqual(m['active_courses'], 1)


class ContentReviewAccessTests(TestCase):
    def test_hr_can_open_content_review(self):
        hr = User.objects.create_user(username='hr@test.local', password='x')
        from django.contrib.auth.models import Group
        hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])

        self.client.login(username='hr@test.local', password='x')
        resp = self.client.get(reverse('analytics:content_review'))
        self.assertEqual(resp.status_code, 200)

    def test_regular_user_cannot_open_content_review(self):
        u = User.objects.create_user(username='u@test.local', password='x')
        self.client.login(username='u@test.local', password='x')
        resp = self.client.get(reverse('analytics:content_review'))
        self.assertEqual(resp.status_code, 403)


class HRHubAccessTests(TestCase):
    def test_hr_can_open_hr_hub_and_candidates(self):
        hr = User.objects.create_user(username='hr@test.local', password='x')
        from django.contrib.auth.models import Group
        hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])

        self.client.login(username='hr@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:hr_hub')).status_code, 200)
        self.assertEqual(self.client.get(reverse('analytics:candidates')).status_code, 200)

    def test_regular_user_cannot_open_hr_hub(self):
        u = User.objects.create_user(username='u@test.local', password='x')
        self.client.login(username='u@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:hr_hub')).status_code, 403)


class HRToolsAccessTests(TestCase):
    def setUp(self):
        self.hr = User.objects.create_user(username='hr@test.local', password='x')
        from django.contrib.auth.models import Group
        self.hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])
        self.u = User.objects.create_user(username='u@test.local', password='x')

    def test_hr_can_open_visibility_and_comments(self):
        self.client.login(username='hr@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:visibility')).status_code, 200)
        self.assertEqual(self.client.get(reverse('analytics:comment_moderation')).status_code, 200)

    def test_regular_user_cannot_open_visibility(self):
        self.client.login(username='u@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:visibility')).status_code, 403)
