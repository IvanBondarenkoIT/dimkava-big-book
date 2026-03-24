"""Load onboarding program from YAML. Run after migrate."""
import yaml
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.onboarding.models import OnboardingProgram, OnboardingModule, OnboardingStep


DEFAULT_YAML_PATH = Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'onboarding_training_plan.yaml'


class Command(BaseCommand):
    help = 'Load onboarding program from onboarding_training_plan.yaml'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, default=str(DEFAULT_YAML_PATH), help='Path to YAML file')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        program_data = data['program']
        program, created = OnboardingProgram.objects.update_or_create(
            slug=program_data['slug'],
            defaults={
                'title': program_data['title'],
                'role': program_data.get('role', ''),
                'estimated_days': program_data.get('estimated_days', 90),
                'description': program_data.get('description', ''),
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Program: {program.title}'))

        for module_data in data.get('modules', []):
            module, _ = OnboardingModule.objects.update_or_create(
                program=program,
                slug=module_data['slug'],
                defaults={
                    'title': module_data['title'],
                    'order': module_data.get('order', 0),
                    'estimated_minutes': module_data.get('estimated_minutes', 0),
                    'description': module_data.get('description', ''),
                }
            )
            for step_data in module_data.get('steps', []):
                OnboardingStep.objects.update_or_create(
                    module=module,
                    order=step_data.get('order', 0),
                    defaults={
                        'title': step_data['title'],
                        'content': step_data.get('content', ''),
                    }
                )
            self.stdout.write(f'  Module: {module.title} ({module.steps.count()} steps)')

        self.stdout.write(self.style.SUCCESS('Onboarding loaded.'))
