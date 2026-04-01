"""Load courses from YAML seed."""
import yaml
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.courses.models import Course, Lesson, TestQuestion

DEFAULT_PATH = Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'courses_seed.yaml'


class Command(BaseCommand):
    help = 'Load courses from courses_seed.yaml'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DEFAULT_PATH), help='Path to YAML')
        parser.add_argument(
            '--auto-translate-draft',
            action='store_true',
            help='Fill missing ka/ru values with EN draft placeholders for HR review',
        )

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

        auto_draft = bool(options.get('auto_translate_draft'))
        for c in data.get('courses', []):
            title_en = self._loc(c, 'title', 'en', c.get('title', ''))
            desc_en = self._loc(c, 'description', 'en', c.get('description', ''))
            title_ka = self._loc(c, 'title', 'ka', '')
            title_ru = self._loc(c, 'title', 'ru', '')
            desc_ka = self._loc(c, 'description', 'ka', '')
            desc_ru = self._loc(c, 'description', 'ru', '')
            if auto_draft:
                title_ka = title_ka or self._draft(title_en, 'ka')
                title_ru = title_ru or self._draft(title_en, 'ru')
                desc_ka = desc_ka or self._draft(desc_en, 'ka')
                desc_ru = desc_ru or self._draft(desc_en, 'ru')
            course, _ = Course.objects.update_or_create(
                slug=c['slug'],
                defaults={
                    'title': title_en,
                    'title_en': title_en,
                    'title_ka': title_ka,
                    'title_ru': title_ru,
                    'description': desc_en,
                    'description_en': desc_en,
                    'description_ka': desc_ka,
                    'description_ru': desc_ru,
                    'level': c.get('level', 'beginner'),
                    'estimated_minutes': c.get('estimated_minutes', 0),
                    'image': c.get('image', ''),
                    'status': 'published',
                }
            )
            for l in c.get('lessons', []):
                lesson_title_en = self._loc(l, 'title', 'en', l.get('title', ''))
                lesson_title_ka = self._loc(l, 'title', 'ka', '')
                lesson_title_ru = self._loc(l, 'title', 'ru', '')
                lesson_content_en = self._loc(l, 'content', 'en', l.get('content', ''))
                lesson_content_ka = self._loc(l, 'content', 'ka', '')
                lesson_content_ru = self._loc(l, 'content', 'ru', '')
                if auto_draft:
                    lesson_title_ka = lesson_title_ka or self._draft(lesson_title_en, 'ka')
                    lesson_title_ru = lesson_title_ru or self._draft(lesson_title_en, 'ru')
                    lesson_content_ka = lesson_content_ka or self._draft(lesson_content_en, 'ka')
                    lesson_content_ru = lesson_content_ru or self._draft(lesson_content_en, 'ru')
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    order=l.get('order', 0),
                    defaults={
                        'title': lesson_title_en,
                        'title_en': lesson_title_en,
                        'title_ka': lesson_title_ka,
                        'title_ru': lesson_title_ru,
                        'lesson_type': l.get('type', 'text'),
                        'content': lesson_content_en,
                        'content_en': lesson_content_en,
                        'content_ka': lesson_content_ka,
                        'content_ru': lesson_content_ru,
                        'estimated_minutes': l.get('minutes', 0),
                        'passing_score': l.get('passing_score'),
                    }
                )
                if lesson.lesson_type == 'quiz':
                    for i, q in enumerate(l.get('questions', [])):
                        q_en = self._loc(q, 'text', 'en', q.get('text', ''))
                        q_ka = self._loc(q, 'text', 'ka', '')
                        q_ru = self._loc(q, 'text', 'ru', '')
                        options_en = q.get('options_en') or q.get('options') or []
                        options_ka = q.get('options_ka') or []
                        options_ru = q.get('options_ru') or []
                        if auto_draft and options_en:
                            options_ka = options_ka or [
                                {'text': self._draft(opt.get('text', ''), 'ka'), 'is_correct': opt.get('is_correct', False)}
                                for opt in options_en
                            ]
                            options_ru = options_ru or [
                                {'text': self._draft(opt.get('text', ''), 'ru'), 'is_correct': opt.get('is_correct', False)}
                                for opt in options_en
                            ]
                        TestQuestion.objects.update_or_create(
                            lesson=lesson,
                            order=i,
                            defaults={
                                'question_text': q_en,
                                'question_text_en': q_en,
                                'question_text_ka': q_ka or (self._draft(q_en, 'ka') if auto_draft else ''),
                                'question_text_ru': q_ru or (self._draft(q_en, 'ru') if auto_draft else ''),
                                'options': options_en,
                                'options_en': options_en,
                                'options_ka': options_ka,
                                'options_ru': options_ru,
                            }
                        )
            self.stdout.write(self.style.SUCCESS(f'Course: {course.title}'))

        self.stdout.write(self.style.SUCCESS('Courses loaded.'))
