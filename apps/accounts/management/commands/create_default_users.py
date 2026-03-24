"""Create default users (admin, hr, employee) from env vars. Run after migrate."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from decouple import config

User = get_user_model()


def get_var(name, default=None):
    try:
        return config(name, default=default)
    except Exception:
        return default


class Command(BaseCommand):
    help = 'Create default users from DEFAULT_* env vars'

    def add_arguments(self, parser):
        parser.add_argument('--update', action='store_true', help='Update passwords if users exist')

    def handle(self, *args, **options):
        update = options['update']
        created = 0
        updated = 0

        users_config = [
            ('admin', 'DEFAULT_ADMIN_EMAIL', 'DEFAULT_ADMIN_PASSWORD', ['admin']),
            ('hr', 'DEFAULT_HR_EMAIL', 'DEFAULT_HR_PASSWORD', ['hr_manager']),
            ('employee', 'DEFAULT_EMPLOYEE_EMAIL', 'DEFAULT_EMPLOYEE_PASSWORD', ['employee']),
        ]

        for role, email_var, password_var, group_names in users_config:
            email = get_var(email_var)
            password = get_var(password_var)
            if not email or not password:
                self.stdout.write(self.style.WARNING(f'Skipping {role}: {email_var} or {password_var} not set'))
                continue

            user, user_created = User.objects.get_or_create(
                username=email,
                defaults={'email': email, 'is_staff': role == 'admin', 'is_superuser': role == 'admin'}
            )
            if user_created:
                user.set_password(password)
                user.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created user: {email} ({role})'))
            elif update:
                user.set_password(password)
                user.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'Updated password: {email}'))
            else:
                self.stdout.write(f'User exists: {email}')

            for name in group_names:
                grp, _ = Group.objects.get_or_create(name=name)
                user.groups.add(grp)

        self.stdout.write(self.style.SUCCESS(f'Done. Created: {created}, Updated: {updated}'))
