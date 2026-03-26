"""Create default users (admin, hr, employee, candidate) from env vars.

Optionally seeds demo content if DB is empty.
Run after migrate.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.utils import timezone
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
        parser.add_argument(
            '--no-seed',
            action='store_true',
            help='Do not auto-load demo content (load_courses/load_onboarding/...).',
        )

    def handle(self, *args, **options):
        update = options['update']
        seed = not options['no_seed']
        created = 0
        updated = 0

        # Ensure HR group has the right admin permissions.
        self._ensure_hr_permissions()

        users_config = [
            ('admin', 'DEFAULT_ADMIN_EMAIL', 'DEFAULT_ADMIN_PASSWORD', ['admin']),
            ('hr', 'DEFAULT_HR_EMAIL', 'DEFAULT_HR_PASSWORD', ['hr_manager']),
            ('employee', 'DEFAULT_EMPLOYEE_EMAIL', 'DEFAULT_EMPLOYEE_PASSWORD', ['employee']),
            ('candidate', 'DEFAULT_CANDIDATE_EMAIL', 'DEFAULT_CANDIDATE_PASSWORD', ['candidate']),
        ]

        for role, email_var, password_var, group_names in users_config:
            email = get_var(email_var)
            password = get_var(password_var)
            if not email or not password:
                self.stdout.write(self.style.WARNING(f'Skipping {role}: {email_var} or {password_var} not set'))
                continue

            user, user_created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'is_staff': role in ('admin', 'hr'),
                    'is_superuser': role == 'admin',
                }
            )
            if user_created:
                user.set_password(password)
                user.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created user: {email} ({role})'))
            elif update:
                user.set_password(password)
                # Ensure correct flags on update as well.
                if role in ('admin', 'hr') and not user.is_staff:
                    user.is_staff = True
                if role == 'admin' and not user.is_superuser:
                    user.is_superuser = True
                user.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'Updated password: {email}'))
            else:
                self.stdout.write(f'User exists: {email}')

            for name in group_names:
                grp, _ = Group.objects.get_or_create(name=name)
                user.groups.add(grp)

            # Set user profile type/fields when available.
            profile = getattr(user, 'profile', None)
            if profile is not None:
                update_fields = []
                desired_type = 'candidate' if role == 'candidate' else 'employee'
                if getattr(profile, 'user_type', None) != desired_type:
                    profile.user_type = desired_type
                    update_fields.append('user_type')
                if role == 'candidate':
                    phone = get_var('DEFAULT_CANDIDATE_PHONE', default='')
                    if phone and getattr(profile, 'phone', '') != phone:
                        profile.phone = phone
                        update_fields.append('phone')
                    # Seed candidate must access learning without going through email flow.
                    if getattr(profile, 'email_verified_at', None) is None:
                        profile.email_verified_at = timezone.now()
                        update_fields.append('email_verified_at')
                if update_fields:
                    profile.save(update_fields=update_fields)

        self.stdout.write(self.style.SUCCESS(f'Done. Created: {created}, Updated: {updated}'))

        if seed:
            self._seed_demo_content_if_empty()

    def _ensure_hr_permissions(self):
        """
        Give hr_manager enough permissions to use Django admin for content + candidates.
        We intentionally grant view/add/change (no delete) for safety.
        """
        hr_group, _ = Group.objects.get_or_create(name='hr_manager')

        app_labels = [
            'accounts',
            'courses',
            'onboarding',
            'knowledge_base',
            'news',
            'departments',
            'notifications',
            'gamification',
        ]
        models_ct = ContentType.objects.filter(app_label__in=app_labels)
        perms = Permission.objects.filter(
            content_type__in=models_ct,
            codename__regex=r'^(view|add|change)_',
        )
        hr_group.permissions.add(*perms)

    def _seed_demo_content_if_empty(self):
        """
        Dev convenience: load YAML demo content when the DB is empty.
        Each loader is idempotent-ish for empty DB; we only trigger when base tables are empty.
        """
        # Import lazily so command works before migrations in edge cases.
        from apps.courses.models import Course
        from apps.departments.models import Department
        from apps.knowledge_base.models import KBSection
        from apps.news.models import NewsPost
        from apps.onboarding.models import OnboardingProgram

        did = False

        if Course.objects.count() == 0:
            call_command('load_courses', verbosity=0)
            did = True
        if OnboardingProgram.objects.count() == 0:
            call_command('load_onboarding', verbosity=0)
            did = True
        if KBSection.objects.count() == 0:
            call_command('load_articles', verbosity=0)
            did = True
        if NewsPost.objects.count() == 0:
            call_command('load_news', verbosity=0)
            did = True
        # departments depends on courses existing for role learning paths
        if Department.objects.count() == 0:
            call_command('load_departments', verbosity=0)
            did = True

        if did:
            self.stdout.write(self.style.SUCCESS('Demo content: ensured (loaded missing datasets).'))
        else:
            self.stdout.write('Demo content: already present (skipped).')
