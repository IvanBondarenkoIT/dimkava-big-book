"""Remove legacy tg-* regulation articles created by the old Telegram import."""

from django.core.management.base import BaseCommand

from apps.knowledge_base.models import Article, KBSection


class Command(BaseCommand):
    help = "Delete regulations section articles with slug tg-* (old per-message import)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List slugs that would be deleted without deleting",
        )

    def handle(self, *args, **options):
        dry_run = bool(options["dry_run"])
        try:
            section = KBSection.objects.get(slug="regulations")
        except KBSection.DoesNotExist:
            self.stdout.write(self.style.WARNING("Section 'regulations' not found — nothing to clean."))
            return

        qs = Article.objects.filter(section=section, slug__startswith="tg-")
        slugs = list(qs.values_list("slug", flat=True))
        if not slugs:
            self.stdout.write(self.style.SUCCESS("No tg-* articles in regulations section."))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Would delete {len(slugs)} article(s):"))
            for s in slugs:
                self.stdout.write(f"  - {s}")
            return

        deleted, _ = qs.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} object(s) ({len(slugs)} tg-* articles in regulations).")
        )
