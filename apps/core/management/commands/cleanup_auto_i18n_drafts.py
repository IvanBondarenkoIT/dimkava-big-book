import re

from django.core.management.base import BaseCommand


AUTO_PREFIX_RE = re.compile(r"^\[AUTO-(ru|ka)\]\s*")


class Command(BaseCommand):
    help = "Remove [AUTO-ru]/[AUTO-ka] draft prefixes from localized content fields."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually write changes to DB (default: dry-run).",
        )

    def _clean(self, value: str) -> str:
        if not value:
            return value
        return AUTO_PREFIX_RE.sub("", value).strip()

    def handle(self, *args, **options):
        apply = bool(options["apply"])

        # Local imports keep app loading fast and avoid unnecessary model imports.
        from apps.courses.models import Course
        from apps.knowledge_base.models import Article
        from apps.news.models import NewsPost
        from apps.onboarding.models import OnboardingModule

        touched = []

        def maybe_update(obj, fields):
            changed = {}
            for f in fields:
                old = getattr(obj, f, "")
                new = self._clean(old)
                if new != old:
                    changed[f] = (old, new)
                    setattr(obj, f, new)
            if changed:
                if apply:
                    obj.save(update_fields=list(changed.keys()))
                touched.append((obj.__class__.__name__, getattr(obj, "pk", None), changed))

        for c in Course.objects.all():
            maybe_update(c, ["title_ru", "title_ka", "description_ru", "description_ka"])
        for m in OnboardingModule.objects.all():
            maybe_update(m, ["title_ru", "title_ka", "description_ru", "description_ka"])
        for a in Article.objects.all():
            maybe_update(a, ["title_ru", "title_ka", "content_ru", "content_ka"])
        for n in NewsPost.objects.all():
            maybe_update(n, ["title_ru", "title_ka", "content_ru", "content_ka"])

        self.stdout.write(self.style.SUCCESS(f"{'Applied' if apply else 'Dry-run'}: {len(touched)} objects would change"))
        for model, pk, changed in touched[:30]:
            keys = ", ".join(sorted(changed.keys()))
            self.stdout.write(f"- {model} pk={pk}: {keys}")
        if len(touched) > 30:
            self.stdout.write(f"... and {len(touched) - 30} more")

