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
