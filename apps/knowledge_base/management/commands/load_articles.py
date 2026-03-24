"""Load articles from sops_and_standards.yaml."""
import yaml
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.knowledge_base.models import Article, KBSection

DEFAULT_PATH = Path(settings.BASE_DIR) / 'input' / 'hr docs' / 'content' / 'sops_and_standards.yaml'


class Command(BaseCommand):
    help = 'Load knowledge base sections and articles from sops_and_standards.yaml'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DEFAULT_PATH), help='Path to YAML')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        for s in data.get('sections', []):
            section, _ = KBSection.objects.update_or_create(
                slug=s['slug'],
                defaults={
                    'title': s['title'],
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
                    'title': a['title'],
                    'status': a.get('status', 'published'),
                    'content': a.get('content', ''),
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  Article: {article.title}'))

        self.stdout.write(self.style.SUCCESS('Articles loaded.'))
