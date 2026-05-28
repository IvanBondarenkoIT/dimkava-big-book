"""Load articles from YAML seed(s)."""
import yaml
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.knowledge_base.models import Article, KBSection

DEFAULT_PATH = Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'sops_and_standards.yaml'
EXTRA_DEFAULT_PATHS = [
    # Optional: generated/maintained separately to keep sops_and_standards.yaml manageable.
    Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'regulations.yaml',
]


class Command(BaseCommand):
    help = 'Load knowledge base sections and articles from YAML seeds'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DEFAULT_PATH), help='Path to YAML')
        parser.add_argument(
            '--extra-path',
            action='append',
            default=[],
            help='Optional extra YAML path(s) to merge (can be passed multiple times)',
        )
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
        primary = Path(options['path'])
        paths: list[Path] = [primary]
        paths.extend([p for p in EXTRA_DEFAULT_PATHS if p.exists()])
        for p in options.get('extra_path') or []:
            paths.append(Path(p))

        data: dict = {'sections': [], 'articles': []}
        for path in paths:
            if not path.exists():
                self.stdout.write(self.style.WARNING(f'Skipping missing YAML: {path}'))
                continue
            with open(path, encoding='utf-8') as f:
                part = yaml.safe_load(f) or {}
            data['sections'].extend(part.get('sections', []) or [])
            data['articles'].extend(part.get('articles', []) or [])

        auto_draft = bool(options.get('auto_translate_draft'))
        for s in data.get('sections', []):
            title_en = self._loc(s, 'title', 'en', s.get('title', ''))
            title_ka = self._loc(s, 'title', 'ka', '')
            title_ru = self._loc(s, 'title', 'ru', '')
            if auto_draft:
                title_ka = title_ka or self._draft(title_en, 'ka')
                title_ru = title_ru or self._draft(title_en, 'ru')
            section, _ = KBSection.objects.update_or_create(
                slug=s['slug'],
                defaults={
                    'title': title_en,
                    'title_en': title_en,
                    'title_ka': title_ka,
                    'title_ru': title_ru,
                    'icon': s.get('icon', ''),
                    'order': s.get('order', 0),
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Section: {section.title}'))

        section_map = {s.slug: s for s in KBSection.objects.all()}

        for a in data.get('articles', []):
            section_slug = a.get('section')
            if not section_slug or section_slug not in section_map:
                self.stdout.write(self.style.WARNING(
                    f'Skipping article {a.get("slug")} — unknown section {section_slug}'
                ))
                continue
            section = section_map[section_slug]
            article, _ = Article.objects.update_or_create(
                section=section,
                slug=a['slug'],
                defaults={
                    'title': self._loc(a, 'title', 'en', a.get('title', '')),
                    'title_en': self._loc(a, 'title', 'en', a.get('title', '')),
                    'title_ka': self._loc(a, 'title', 'ka', '') or (self._draft(self._loc(a, 'title', 'en', a.get('title', '')), 'ka') if auto_draft else ''),
                    'title_ru': self._loc(a, 'title', 'ru', '') or (self._draft(self._loc(a, 'title', 'en', a.get('title', '')), 'ru') if auto_draft else ''),
                    'status': a.get('status', 'published'),
                    'content': self._loc(a, 'content', 'en', a.get('content', '')),
                    'content_en': self._loc(a, 'content', 'en', a.get('content', '')),
                    'content_ka': self._loc(a, 'content', 'ka', '') or (self._draft(self._loc(a, 'content', 'en', a.get('content', '')), 'ka') if auto_draft else ''),
                    'content_ru': self._loc(a, 'content', 'ru', '') or (self._draft(self._loc(a, 'content', 'en', a.get('content', '')), 'ru') if auto_draft else ''),
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  Article: {article.title}'))

        self.stdout.write(self.style.SUCCESS('Articles loaded.'))
