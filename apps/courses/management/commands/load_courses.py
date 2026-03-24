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

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        for c in data.get('courses', []):
            course, _ = Course.objects.update_or_create(
                slug=c['slug'],
                defaults={
                    'title': c['title'],
                    'description': c.get('description', ''),
                    'level': c.get('level', 'beginner'),
                    'estimated_minutes': c.get('estimated_minutes', 0),
                    'image': c.get('image', ''),
                    'status': 'published',
                }
            )
            for l in c.get('lessons', []):
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    order=l.get('order', 0),
                    defaults={
                        'title': l['title'],
                        'lesson_type': l.get('type', 'text'),
                        'content': l.get('content', ''),
                        'estimated_minutes': l.get('minutes', 0),
                        'passing_score': l.get('passing_score'),
                    }
                )
                if lesson.lesson_type == 'quiz':
                    for i, q in enumerate(l.get('questions', [])):
                        TestQuestion.objects.update_or_create(
                            lesson=lesson,
                            order=i,
                            defaults={
                                'question_text': q['text'],
                                'options': q.get('options', []),
                            }
                        )
            self.stdout.write(self.style.SUCCESS(f'Course: {course.title}'))

        self.stdout.write(self.style.SUCCESS('Courses loaded.'))
