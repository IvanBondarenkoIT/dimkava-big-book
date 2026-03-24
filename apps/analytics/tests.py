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
