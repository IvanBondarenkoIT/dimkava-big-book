from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Badge, Mission, MissionStep
from .services import (
    award_badge,
    award_points,
    calculate_level,
    get_or_create_profile,
    update_mission_progress,
)

User = get_user_model()


class GamificationServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gamer', password='test')

    def test_get_or_create_profile(self):
        p = get_or_create_profile(self.user)
        self.assertEqual(p.total_points, 0)
        self.assertEqual(p.level, 1)

    def test_calculate_level(self):
        self.assertEqual(calculate_level(0), 1)
        self.assertEqual(calculate_level(100), 2)
        self.assertEqual(calculate_level(700), 4)

    def test_award_points_updates_level(self):
        award_points(self.user, 150, 'MANUAL', reference='test')
        p = get_or_create_profile(self.user)
        self.assertEqual(p.total_points, 150)
        self.assertEqual(p.level, 2)

    def test_award_badge_idempotent(self):
        Badge.objects.create(
            code='TEST_BADGE',
            name='Test',
            description='d',
            is_active=True,
        )
        b1 = award_badge(self.user, 'TEST_BADGE')
        self.assertIsNotNone(b1)
        b2 = award_badge(self.user, 'TEST_BADGE')
        self.assertIsNone(b2)

    def test_mission_complete(self):
        m = Mission.objects.create(
            code='M1',
            title='Mission',
            description='d',
            estimated_minutes=10,
            bonus_points=50,
            is_active=True,
        )
        MissionStep.objects.create(
            mission=m,
            order=1,
            title='Step',
            module_slug='step1',
            module_type='lesson',
            is_required=True,
        )
        update_mission_progress(self.user, 'M1', 'step1')
        p = get_or_create_profile(self.user)
        self.assertEqual(p.total_points, 50)
