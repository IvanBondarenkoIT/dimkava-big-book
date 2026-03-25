"""Accounts app tests."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.departments.models import Department, Role
from apps.onboarding.models import OnboardingProgram

from .models import AssignmentRule
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

    @patch('apps.accounts.management.commands.create_default_users.get_var')
    def test_creates_hr_user_as_staff(self, mock_get_var):
        def get_var_impl(name, default=None):
            vals = {
                'DEFAULT_HR_EMAIL': 'hr@test.dimkava.ge',
                'DEFAULT_HR_PASSWORD': 'hrpass123',
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
