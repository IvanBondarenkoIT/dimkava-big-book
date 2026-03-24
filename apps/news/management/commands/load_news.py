"""Load news posts from news_seed.yaml."""
import yaml
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.news.models import NewsPost

DEFAULT_PATH = Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'news_seed.yaml'


def parse_dt(s: str):
    """Parse 'YYYY-MM-DD HH:MM:SS' to timezone-aware datetime."""
    from datetime import datetime
    naive = datetime.strptime(s.strip(), '%Y-%m-%d %H:%M:%S')
    return timezone.make_aware(naive) if timezone.is_naive(naive) else naive


class Command(BaseCommand):
    help = 'Load news posts from news_seed.yaml'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DEFAULT_PATH), help='Path to YAML')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        for p in data.get('posts', []):
            pub_at = p.get('published_at')
            if isinstance(pub_at, str):
                pub_at = parse_dt(pub_at)
            NewsPost.objects.update_or_create(
                slug=p['slug'],
                defaults={
                    'title': p['title'],
                    'content': p.get('content', ''),
                    'tag': p.get('tag', ''),
                    'pinned': p.get('pinned', False),
                    'published_at': pub_at,
                }
            )
            self.stdout.write(self.style.SUCCESS(f'News: {p["title"]}'))

        self.stdout.write(self.style.SUCCESS('News loaded.'))
