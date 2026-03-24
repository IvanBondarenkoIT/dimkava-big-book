"""Accounts app tests."""
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

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
