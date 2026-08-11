"""Accounts app tests."""
from uuid import uuid4
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.departments.models import Department, Role
from apps.courses.models import Course, Lesson, UserProgress
from apps.gamification.models import Badge, GamificationProfile, UserBadge
from apps.onboarding.models import OnboardingProgram

from .models import AssignmentRule
from .selectors import get_profile_dashboard_context
from .services import convert_candidate_to_employee, find_matching_rule

User = get_user_model()


class CreateDefaultUsersTest(TestCase):
    """Test create_default_users management command."""

    @patch('apps.accounts.management.commands.create_default_users.get_var')
    def test_creates_admin_user(self, mock_get_var):
        def get_var_impl(name, default=None):
            vals = {
                'DEFAULT_ADMIN_EMAIL': 'admin@test.dimkava.ge',
                'DEFAULT_ADMIN_PASSWORD': 'adminpass123',
            }
            return vals.get(name, default)

        mock_get_var.side_effect = get_var_impl
        call_command('create_default_users')
        user = User.objects.get(username='admin@test.dimkava.ge')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('adminpass123'))

    @patch('apps.accounts.management.commands.create_default_users.get_var')
    def test_creates_candidate_user_with_profile_type_and_phone(self, mock_get_var):
        def get_var_impl(name, default=None):
            vals = {
                'DEFAULT_CANDIDATE_EMAIL': 'candidate@test.dimkava.ge',
                'DEFAULT_CANDIDATE_PASSWORD': 'candidatepass123',
                'DEFAULT_CANDIDATE_PHONE': '+995500000000',
            }
            return vals.get(name, default)

        mock_get_var.side_effect = get_var_impl
        call_command('create_default_users')
        user = User.objects.get(username='candidate@test.dimkava.ge')
        self.assertTrue(user.check_password('candidatepass123'))
        self.assertTrue(user.groups.filter(name='candidate').exists())
        self.assertEqual(user.profile.user_type, 'candidate')
        self.assertEqual(user.profile.phone, '+995500000000')
        self.assertIsNotNone(user.profile.email_verified_at)

    @patch('apps.accounts.management.commands.create_default_users.get_var')
    def test_creates_hr_user_as_staff(self, mock_get_var):
        # Avoid hardcoding password-like strings to prevent GitHub secret scanning alerts.
        hr_password = f'hr-test-{uuid4()}'

        def get_var_impl(name, default=None):
            vals = {
                'DEFAULT_HR_EMAIL': 'hr@test.dimkava.ge',
                'DEFAULT_HR_PASSWORD': hr_password,
            }
            return vals.get(name, default)

        mock_get_var.side_effect = get_var_impl
        call_command('create_default_users')
        user = User.objects.get(username='hr@test.dimkava.ge')
        self.assertTrue(user.is_staff)


class LoginViewTest(TestCase):
    """Login page behavior tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='employee@test.dimkava.ge',
            email='employee@test.dimkava.ge',
            password='correct-pass-123',
        )

    def test_invalid_credentials_show_error_message(self):
        response = self.client.post('/login/', {
            'username': self.user.username,
            'password': 'wrong-pass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')


class AssignmentRuleTests(TestCase):
    """AssignmentRule + UserProfile (phase 11.3)."""

    def setUp(self):
        self.dept = Department.objects.create(name='Retail', slug='retail-test-ar')
        self.role = Role.objects.create(title='Barista', department=self.dept, order=0)
        self.program = OnboardingProgram.objects.create(
            slug='assign-test-program',
            title='Assign Test Program',
        )
        self.user = User.objects.create_user(
            username='ruleuser@test.dimkava.ge',
            password='pass12345',
        )
        self.profile = self.user.profile

    def test_rule_matches_department_and_role_name(self):
        AssignmentRule.objects.create(
            role_name='Barista',
            department=self.dept,
            onboarding_program_slug='assign-test-program',
            required_course_slugs=['espresso-basics'],
            is_active=True,
        )
        self.profile.department = self.dept
        self.profile.role = self.role
        self.profile.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.assigned_onboarding_program_id, self.program.id)
        self.assertEqual(self.profile.pending_course_slugs, ['espresso-basics'])

    def test_find_matching_rule_skips_wrong_department(self):
        other = Department.objects.create(name='Other', slug='other-test-ar')
        AssignmentRule.objects.create(
            role_name='Barista',
            department=other,
            onboarding_program_slug='assign-test-program',
            is_active=True,
        )
        self.profile.department = self.dept
        self.profile.role = self.role
        self.profile.save()
        self.assertIsNone(find_matching_rule(self.profile))


class CandidateRegistrationAndEmailTests(TestCase):
    def test_register_candidate_sends_email_and_redirects_home(self):
        r = self.client.post(
            reverse('accounts:register_candidate'),
            {
                'email': 'newcand@test.dimkava.ge',
                'phone': '+995511111111',
                'password1': 'x' * 12,
                'password2': 'x' * 12,
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('core:home'))
        user = User.objects.get(username='newcand@test.dimkava.ge')
        self.assertEqual(user.profile.user_type, 'candidate')
        self.assertIsNone(user.profile.email_verified_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('confirm', mail.outbox[0].body.lower())

    def test_unverified_candidate_can_open_home(self):
        user = User.objects.create_user(username='u1@test.ge', email='u1@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.email_verified_at = None
        user.profile.save()
        self.client.login(username='u1@test.ge', password='pass123456789')
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)

    def test_confirm_email_verifies_and_redirects(self):
        user = User.objects.create_user(username='u2@test.ge', email='u2@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.email_verified_at = None
        user.profile.save()
        from apps.accounts.email_verification import sign_user_id

        token = sign_user_id(user.pk)
        r = self.client.get(reverse('accounts:confirm_email') + f'?token={token}')
        self.assertEqual(r.status_code, 302)
        user.profile.refresh_from_db()
        self.assertIsNotNone(user.profile.email_verified_at)

    def test_verified_candidate_cannot_open_wiki(self):
        user = User.objects.create_user(username='u3@test.ge', email='u3@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.email_verified_at = timezone.now()
        user.profile.save()
        self.client.login(username='u3@test.ge', password='pass123456789')
        r = self.client.get('/wiki/')
        self.assertEqual(r.status_code, 403)

    def test_unverified_candidate_cannot_open_employee_sections(self):
        user = User.objects.create_user(username='u4@test.ge', email='u4@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.email_verified_at = None
        user.profile.save()
        self.client.login(username='u4@test.ge', password='pass123456789')

        for path in ['/wiki/', '/news/', '/departments/', '/analytics/', '/gamification/', '/notifications/', '/search/']:
            r = self.client.get(path)
            self.assertEqual(r.status_code, 403, msg=f'Expected 403 for candidate path {path}')

    def test_candidate_cannot_open_unknown_sections_by_default(self):
        user = User.objects.create_user(username='u4b@test.ge', email='u4b@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.email_verified_at = None
        user.profile.save()
        self.client.login(username='u4b@test.ge', password='pass123456789')

        r = self.client.get('/some-new-internal-tool/')
        self.assertEqual(r.status_code, 403)

    def test_candidate_can_open_courses_and_onboarding(self):
        user = User.objects.create_user(username='u5@test.ge', email='u5@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.email_verified_at = None
        user.profile.save()
        self.client.login(username='u5@test.ge', password='pass123456789')

        r = self.client.get(reverse('courses:list'))
        self.assertEqual(r.status_code, 200)
        r = self.client.get(reverse('onboarding:overview'))
        self.assertEqual(r.status_code, 200)

    def test_candidate_can_set_language_via_get(self):
        user = User.objects.create_user(username='u5i18n@test.ge', email='u5i18n@test.ge', password='pass123456789')
        user.profile.user_type = 'candidate'
        user.profile.save()
        self.client.login(username='u5i18n@test.ge', password='pass123456789')

        r = self.client.get(reverse('core:set_language'), {'language': 'ru', 'next': '/'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.cookies.get('django_language').value, 'ru')

        r = self.client.get('/i18n/setlang/')
        # Django's POST-only setlang returns 405 for GET; candidates must not get PermissionDenied 403.
        self.assertNotEqual(r.status_code, 403)


class CandidateConversionTests(TestCase):
    def test_convert_candidate_to_employee_sets_status_and_groups(self):
        user = User.objects.create_user(username='c@test.ge', password='pass')
        user.profile.user_type = 'candidate'
        user.profile.save()

        convert_candidate_to_employee(user)
        user.refresh_from_db()
        user.profile.refresh_from_db()

        self.assertEqual(user.profile.user_type, 'employee')
        self.assertTrue(user.groups.filter(name='employee').exists())
        self.assertFalse(user.groups.filter(name='candidate').exists())


class SeedDemoContentTests(TestCase):
    @patch('apps.accounts.management.commands.create_default_users.call_command')
    @patch('apps.accounts.management.commands.create_default_users.get_var')
    def test_seeds_demo_content_when_empty(self, mock_get_var, mock_call_command):
        def get_var_impl(name, default=None):
            vals = {
                'DEFAULT_ADMIN_EMAIL': 'admin@test.dimkava.ge',
                'DEFAULT_ADMIN_PASSWORD': 'adminpass123',
            }
            return vals.get(name, default)

        mock_get_var.side_effect = get_var_impl
        call_command('create_default_users')

        called = [c.args[0] for c in mock_call_command.call_args_list]
        # order isn't critical; just ensure all loaders were invoked at least once
        for cmd in ['load_courses', 'load_onboarding', 'load_articles', 'load_news', 'load_departments']:
            self.assertIn(cmd, called)

    @patch('apps.accounts.management.commands.create_default_users.call_command')
    @patch('apps.accounts.management.commands.create_default_users.get_var')
    def test_no_seed_flag_skips_loading(self, mock_get_var, mock_call_command):
        def get_var_impl(name, default=None):
            vals = {
                'DEFAULT_ADMIN_EMAIL': 'admin@test.dimkava.ge',
                'DEFAULT_ADMIN_PASSWORD': 'adminpass123',
            }
            return vals.get(name, default)

        mock_get_var.side_effect = get_var_impl
        call_command('create_default_users', '--no-seed')
        self.assertEqual(mock_call_command.call_count, 0)


class ProfileDashboardSelectorTests(TestCase):
    def test_profile_dashboard_metrics(self):
        user = User.objects.create_user(username='p@test.ge', email='p@test.ge', password='pass')
        GamificationProfile.objects.filter(user=user).update(total_points=840, level=8)

        c1 = Course.objects.create(slug='pc1', title='C1', status='published', level='beginner')
        l11 = Lesson.objects.create(course=c1, title='L1', order=1, lesson_type='text', estimated_minutes=30, is_required=True)
        l12 = Lesson.objects.create(course=c1, title='L2', order=2, lesson_type='text', estimated_minutes=30, is_required=True)
        c2 = Course.objects.create(slug='pc2', title='C2', status='published', level='intermediate')
        l21 = Lesson.objects.create(course=c2, title='L1', order=1, lesson_type='text', estimated_minutes=60, is_required=True)

        UserProgress.objects.create(user=user, lesson=l11, is_completed=True)
        UserProgress.objects.create(user=user, lesson=l12, is_completed=True)
        UserProgress.objects.create(user=user, lesson=l21, is_completed=False)

        compliance = Badge.objects.create(code='COMPL', name='Compliance', description='ok', is_compliance=True)
        regular = Badge.objects.create(code='REG', name='Regular', description='ok', is_compliance=False)
        UserBadge.objects.create(user=user, badge=compliance)
        UserBadge.objects.create(user=user, badge=regular)

        ctx = get_profile_dashboard_context(user)
        self.assertEqual(ctx['courses_done'], 1)
        self.assertEqual(ctx['hours_spent'], 1)
        self.assertEqual(ctx['skill_level'], 8.4)
        self.assertEqual(ctx['certificates_count'], 1)
        self.assertTrue(len(ctx['certification_progress']) >= 3)
        self.assertEqual(len(ctx['badge_showcase']), 2)


class AvatarBadgeSelectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ab@test.ge', email='ab@test.ge', password='pass')
        self.client.login(username='ab@test.ge', password='pass')

    def test_user_can_select_only_earned_badge_for_avatar(self):
        from apps.gamification.models import Badge, UserBadge

        b1 = Badge.objects.create(code='B1', name='B1', description='ok', icon='🏆')
        b2 = Badge.objects.create(code='B2', name='B2', description='ok', icon='🎖️')
        UserBadge.objects.create(user=self.user, badge=b1)

        r = self.client.post(
            reverse('accounts:profile'),
            {
                'action': 'set_avatar_badge',
                'display_badge': str(b2.id),
                'display_badge_placement': 'corner',
            },
        )
        self.assertEqual(r.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertIsNone(self.user.profile.display_badge)

        r = self.client.post(
            reverse('accounts:profile'),
            {
                'action': 'set_avatar_badge',
                'display_badge': str(b1.id),
                'display_badge_placement': 'corner',
            },
            follow=True,
        )
        self.assertEqual(r.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_badge_id, b1.id)

    def test_base_template_renders_selected_badge_icon(self):
        from apps.gamification.models import Badge, UserBadge

        b1 = Badge.objects.create(code='B3', name='B3', description='ok', icon='🏆')
        UserBadge.objects.create(user=self.user, badge=b1)
        self.user.profile.display_badge = b1
        self.user.profile.display_badge_placement = 'corner'
        self.user.profile.save()

        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '🏆')


class PublicUsernameTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='pu@test.ge', email='pu@test.ge', password='pass')
        self.client.login(username='pu@test.ge', password='pass')

    def test_profile_post_updates_public_username(self):
        r = self.client.post(
            reverse('accounts:profile'),
            {'action': 'set_public_username', 'public_username': 'master-barista'},
            follow=True,
        )
        self.assertEqual(r.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.public_username, 'master-barista')
        self.assertContains(r, 'master-barista')
