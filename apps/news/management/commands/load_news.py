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

        auto_draft = bool(options.get('auto_translate_draft'))
        for p in data.get('posts', []):
            pub_at = p.get('published_at')
            if isinstance(pub_at, str):
                pub_at = parse_dt(pub_at)
            title_en = self._loc(p, 'title', 'en', p.get('title', ''))
            content_en = self._loc(p, 'content', 'en', p.get('content', ''))
            title_ka = self._loc(p, 'title', 'ka', '')
            title_ru = self._loc(p, 'title', 'ru', '')
            content_ka = self._loc(p, 'content', 'ka', '')
            content_ru = self._loc(p, 'content', 'ru', '')
            if auto_draft:
                title_ka = title_ka or self._draft(title_en, 'ka')
                title_ru = title_ru or self._draft(title_en, 'ru')
                content_ka = content_ka or self._draft(content_en, 'ka')
                content_ru = content_ru or self._draft(content_en, 'ru')
            NewsPost.objects.update_or_create(
                slug=p['slug'],
                defaults={
                    'title': title_en,
                    'title_en': title_en,
                    'title_ka': title_ka,
                    'title_ru': title_ru,
                    'content': content_en,
                    'content_en': content_en,
                    'content_ka': content_ka,
                    'content_ru': content_ru,
                    'tag': p.get('tag', ''),
                    'pinned': p.get('pinned', False),
                    'published_at': pub_at,
                }
            )
            self.stdout.write(self.style.SUCCESS(f'News: {p["title"]}'))

        self.stdout.write(self.style.SUCCESS('News loaded.'))
