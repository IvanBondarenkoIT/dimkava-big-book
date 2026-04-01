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
        parser.add_argument('--auto-translate-draft', action='store_true')

    @staticmethod
    def _loc(data: dict, key: str, lang: str, default: str = '') -> str:
        direct = data.get(f'{key}_{lang}')
        if direct:
            return direct
        nested = data.get(key)
        if isinstance(nested, dict):
            return nested.get(lang) or nested.get('en') or default
        if lang == 'en' and isinstance(nested, str):
            return nested
        return default

    @staticmethod
    def _draft(value: str, lang: str) -> str:
        return f'[AUTO-{lang}] {value}' if value else ''

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        program_data = data['program']
        auto_draft = bool(options.get('auto_translate_draft'))
        title_en = self._loc(program_data, 'title', 'en', program_data.get('title', ''))
        desc_en = self._loc(program_data, 'description', 'en', program_data.get('description', ''))
        title_ka = self._loc(program_data, 'title', 'ka', '')
        title_ru = self._loc(program_data, 'title', 'ru', '')
        desc_ka = self._loc(program_data, 'description', 'ka', '')
        desc_ru = self._loc(program_data, 'description', 'ru', '')
        if auto_draft:
            title_ka = title_ka or self._draft(title_en, 'ka')
            title_ru = title_ru or self._draft(title_en, 'ru')
            desc_ka = desc_ka or self._draft(desc_en, 'ka')
            desc_ru = desc_ru or self._draft(desc_en, 'ru')
        program, created = OnboardingProgram.objects.update_or_create(
            slug=program_data['slug'],
            defaults={
                'title': title_en,
                'title_en': title_en,
                'title_ka': title_ka,
                'title_ru': title_ru,
                'role': program_data.get('role', ''),
                'estimated_days': program_data.get('estimated_days', 90),
                'description': desc_en,
                'description_en': desc_en,
                'description_ka': desc_ka,
                'description_ru': desc_ru,
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Program: {program.title}'))

        for module_data in data.get('modules', []):
            module_title_en = self._loc(module_data, 'title', 'en', module_data.get('title', ''))
            module_title_ka = self._loc(module_data, 'title', 'ka', '')
            module_title_ru = self._loc(module_data, 'title', 'ru', '')
            module_desc_en = self._loc(module_data, 'description', 'en', module_data.get('description', ''))
            module_desc_ka = self._loc(module_data, 'description', 'ka', '')
            module_desc_ru = self._loc(module_data, 'description', 'ru', '')
            if auto_draft:
                module_title_ka = module_title_ka or self._draft(module_title_en, 'ka')
                module_title_ru = module_title_ru or self._draft(module_title_en, 'ru')
                module_desc_ka = module_desc_ka or self._draft(module_desc_en, 'ka')
                module_desc_ru = module_desc_ru or self._draft(module_desc_en, 'ru')
            module, _ = OnboardingModule.objects.update_or_create(
                program=program,
                slug=module_data['slug'],
                defaults={
                    'title': module_title_en,
                    'title_en': module_title_en,
                    'title_ka': module_title_ka,
                    'title_ru': module_title_ru,
                    'order': module_data.get('order', 0),
                    'estimated_minutes': module_data.get('estimated_minutes', 0),
                    'description': module_desc_en,
                    'description_en': module_desc_en,
                    'description_ka': module_desc_ka,
                    'description_ru': module_desc_ru,
                }
            )
            for step_data in module_data.get('steps', []):
                step_title_en = self._loc(step_data, 'title', 'en', step_data.get('title', ''))
                step_title_ka = self._loc(step_data, 'title', 'ka', '')
                step_title_ru = self._loc(step_data, 'title', 'ru', '')
                step_content_en = self._loc(step_data, 'content', 'en', step_data.get('content', ''))
                step_content_ka = self._loc(step_data, 'content', 'ka', '')
                step_content_ru = self._loc(step_data, 'content', 'ru', '')
                if auto_draft:
                    step_title_ka = step_title_ka or self._draft(step_title_en, 'ka')
                    step_title_ru = step_title_ru or self._draft(step_title_en, 'ru')
                    step_content_ka = step_content_ka or self._draft(step_content_en, 'ka')
                    step_content_ru = step_content_ru or self._draft(step_content_en, 'ru')
                OnboardingStep.objects.update_or_create(
                    module=module,
                    order=step_data.get('order', 0),
                    defaults={
                        'title': step_title_en,
                        'title_en': step_title_en,
                        'title_ka': step_title_ka,
                        'title_ru': step_title_ru,
                        'content': step_content_en,
                        'content_en': step_content_en,
                        'content_ka': step_content_ka,
                        'content_ru': step_content_ru,
                    }
                )
            self.stdout.write(f'  Module: {module.title} ({module.steps.count()} steps)')

        self.stdout.write(self.style.SUCCESS('Onboarding loaded.'))
