"""
Smoke tests — проверка, что все страницы открываются без ошибок.
При изменении шаблонов, URL или views запускать: python manage.py test apps.core.tests
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils import translation

User = get_user_model()


class PageSmokeTests(TestCase):
    """Проход по всем страницам — если что-то сломается, тест упадёт."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@dimkava.ge',
            email='test@dimkava.ge',
            password='testpass',
        )
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

    def test_home_shows_where_to_start_banner(self):
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Where to start')

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

    def test_notifications_mark_read_redirects(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            user=self.user, type='news', text='Test',
            link='/courses/', is_read=False
        )
        r = self.client.get(reverse('notifications:mark_read', kwargs={'pk': n.pk}))
        self.assertEqual(r.status_code, 302)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

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

    def test_password_reset_post_sends_email(self):
        from django.core import mail

        r = self.client.post(reverse('password_reset'), {'email': 'test@dimkava.ge'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('password', mail.outbox[0].subject.lower())

    def test_login_post_success(self):
        r = self.client.post('/login/', {'username': 'test@dimkava.ge', 'password': 'testpass'})
        self.assertEqual(r.status_code, 302)

    @override_settings(DEBUG=False)
    def test_404_page(self):
        """Проверяем, что кастомный 404 рендерится."""
        r = self.client.get('/nonexistent-page-xyz/')
        self.assertEqual(r.status_code, 404)


class HomeAchievementSnapshotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='snapshot@test.dimkava.ge', password='testpass')
        self.peer = User.objects.create_user(username='peer@test.dimkava.ge', password='testpass')
        self.client.login(username='snapshot@test.dimkava.ge', password='testpass')

    def test_home_snapshot_selector_calculates_points_streak_and_percentile(self):
        from apps.gamification.models import PointsLog
        from apps.gamification.services import get_or_create_profile
        from apps.core.selectors import get_home_achievement_snapshot

        today = timezone.now()
        yesterday = today - timedelta(days=1)

        get_or_create_profile(self.user)
        get_or_create_profile(self.peer)

        p1 = PointsLog.objects.create(user=self.user, source='TEST', points=120)
        p2 = PointsLog.objects.create(user=self.user, source='TEST', points=80)
        p3 = PointsLog.objects.create(user=self.peer, source='TEST', points=50)
        PointsLog.objects.filter(pk=p1.pk).update(created_at=today)
        PointsLog.objects.filter(pk=p2.pk).update(created_at=yesterday)
        PointsLog.objects.filter(pk=p3.pk).update(created_at=today)

        profile = self.user.gamification_profile
        profile.total_points = 200
        profile.save(update_fields=['total_points'])

        snapshot = get_home_achievement_snapshot(self.user)
        self.assertEqual(snapshot['total_points'], 200)
        self.assertEqual(snapshot['current_streak_days'], 2)
        self.assertEqual(snapshot['top_percentile_this_week'], 50)
        self.assertTrue(snapshot['role_title'])

    def test_home_renders_dynamic_snapshot_values(self):
        from apps.gamification.models import PointsLog
        from apps.gamification.services import get_or_create_profile

        profile = get_or_create_profile(self.user)
        profile.total_points = 2450
        profile.save(update_fields=['total_points'])
        PointsLog.objects.create(user=self.user, source='TEST', points=150)
        PointsLog.objects.create(user=self.peer, source='TEST', points=50)

        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Welcome back')
        self.assertContains(r, '2450')
        self.assertContains(r, '#1 of 2')

    def test_home_snapshot_defaults_when_user_has_no_activity(self):
        from apps.core.selectors import get_home_achievement_snapshot

        snapshot = get_home_achievement_snapshot(self.user)
        self.assertEqual(snapshot['current_streak_days'], 0)
        self.assertEqual(snapshot['total_points'], 0)
        self.assertEqual(snapshot['top_percentile_this_week'], 100)
        self.assertTrue(snapshot['role_title'])

    def test_home_snapshot_percentile_for_top_user(self):
        from apps.gamification.models import PointsLog
        from apps.core.selectors import get_home_achievement_snapshot

        PointsLog.objects.create(user=self.user, source='TEST', points=300)
        PointsLog.objects.create(user=self.peer, source='TEST', points=100)

        snapshot = get_home_achievement_snapshot(self.user)
        self.assertEqual(snapshot['top_percentile_this_week'], 50)

    def test_home_snapshot_percentile_tie_uses_same_rank_bucket(self):
        from apps.gamification.models import PointsLog
        from apps.core.selectors import get_home_achievement_snapshot

        another = User.objects.create_user(username='another@test.dimkava.ge', password='testpass')
        PointsLog.objects.create(user=self.user, source='TEST', points=100)
        PointsLog.objects.create(user=self.peer, source='TEST', points=100)
        PointsLog.objects.create(user=another, source='TEST', points=100)

        s1 = get_home_achievement_snapshot(self.user)
        s2 = get_home_achievement_snapshot(self.peer)
        s3 = get_home_achievement_snapshot(another)
        self.assertEqual(s1['top_percentile_this_week'], s2['top_percentile_this_week'])
        self.assertEqual(s2['top_percentile_this_week'], s3['top_percentile_this_week'])


class I18nSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='i18n@test.dimkava.ge',
            email='i18n@test.dimkava.ge',
            password='testpass',
        )
        self.client.login(username='i18n@test.dimkava.ge', password='testpass')

    def test_set_language_endpoint_updates_session(self):
        response = self.client.post('/i18n/setlang/', {'language': 'ru', 'next': '/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies.get('django_language').value, 'ru')

    def test_course_selector_uses_localized_title(self):
        from apps.courses.models import Course
        from apps.courses.selectors import get_courses_for_user

        Course.objects.create(
            slug='i18n-course',
            title='English Title',
            title_en='English Title',
            title_ru='Русский заголовок',
            description='English Desc',
            description_en='English Desc',
            description_ru='Русское описание',
            level='beginner',
            status='published',
        )

        with translation.override('ru'):
            rows = get_courses_for_user(self.user)
        matched = [r for r in rows if r['slug'] == 'i18n-course'][0]
        self.assertEqual(matched['title'], 'Русский заголовок')
        self.assertEqual(matched['description'], 'Русское описание')


class HomeProfileIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hp@test.dimkava.ge', password='testpass')
        self.peer = User.objects.create_user(username='hppeer@test.dimkava.ge', password='testpass')
        self.client.login(username='hp@test.dimkava.ge', password='testpass')

    def test_home_and_profile_render_and_share_points_context(self):
        from apps.gamification.models import PointsLog
        from apps.gamification.services import get_or_create_profile

        profile = get_or_create_profile(self.user)
        profile.total_points = 300
        profile.save(update_fields=['total_points'])

        PointsLog.objects.create(user=self.user, source='TEST', points=200)
        PointsLog.objects.create(user=self.peer, source='TEST', points=10)

        home = self.client.get(reverse('core:home'))
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, 'Welcome back')
        self.assertContains(home, 'Specialist')
        self.assertContains(home, '300')

        prof = self.client.get(reverse('accounts:profile'))
        self.assertEqual(prof.status_code, 200)
        self.assertContains(prof, 'Courses done')
        self.assertContains(prof, 'Skill level')
        self.assertContains(prof, '3.0')

    def test_home_and_profile_pages_are_stable_with_seeded_content(self):
        from django.core.management import call_command

        call_command('load_courses', verbosity=0)
        call_command('load_onboarding', verbosity=0)

        r1 = self.client.get(reverse('core:home'))
        r2 = self.client.get(reverse('accounts:profile'))
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
