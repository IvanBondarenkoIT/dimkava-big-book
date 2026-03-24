"""Load departments and roles from YAML seed."""
import yaml
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.courses.models import Course
from apps.departments.models import Department, Role

DEFAULT_PATH = Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'departments_seed.yaml'


class Command(BaseCommand):
    help = 'Load departments and roles from departments_seed.yaml'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DEFAULT_PATH), help='Path to YAML')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        course_slugs = {c.slug: c for c in Course.objects.all()}

        for d in data.get('departments', []):
            dept, _ = Department.objects.update_or_create(
                slug=d['slug'],
                defaults={'name': d['name']}
            )
            self.stdout.write(self.style.SUCCESS(f'Department: {dept.name}'))

            for r in d.get('roles', []):
                role, _ = Role.objects.update_or_create(
                    department=dept,
                    title=r['title'],
                    defaults={
                        'description': r.get('description', ''),
                        'order': r.get('order', 0),
                    }
                )
                # Set M2M by slug
                required = [course_slugs[s] for s in r.get('required_courses', []) if s in course_slugs]
                recommended = [course_slugs[s] for s in r.get('recommended_courses', []) if s in course_slugs]
                role.required_courses.set(required)
                role.recommended_courses.set(recommended)
                self.stdout.write(self.style.SUCCESS(f'  Role: {role.title}'))

        self.stdout.write(self.style.SUCCESS('Departments loaded.'))
