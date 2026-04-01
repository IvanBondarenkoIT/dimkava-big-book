import re
from itertools import islice

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured

from apps.core.services.deepl_translate import translate_texts


AUTO_PREFIX_RE = re.compile(r"^\[AUTO-(ru|ka)\]\s*", re.IGNORECASE)


def _strip_auto_prefix(value: str) -> str:
    if not value:
        return value
    return AUTO_PREFIX_RE.sub("", value).strip()


def _needs_translation(value: str, lang: str) -> bool:
    if not value:
        return True
    v = value.strip()
    return v.lower().startswith(f"[auto-{lang}]")


class Command(BaseCommand):
    help = "Translate EN content into RU/KA fields using DeepL (requires DEEPL_AUTH_KEY)."

    def add_arguments(self, parser):
        parser.add_argument("--lang", choices=["ru", "ka"], required=True, help="Target language to fill.")
        parser.add_argument("--apply", action="store_true", help="Write translations to DB (default: dry-run).")
        parser.add_argument("--limit", type=int, default=200, help="Max objects to translate per model.")

    def handle(self, *args, **options):
        lang = options["lang"]
        apply = bool(options["apply"])
        limit = int(options["limit"] or 0)

        try:
            # Validate config early.
            translate_texts(texts=[], target_lang=lang)
        except ImproperlyConfigured as e:
            raise CommandError(str(e)) from e

        # Local imports avoid app load side effects.
        from apps.courses.models import Course, Lesson, TestQuestion
        from apps.knowledge_base.models import Article
        from apps.news.models import NewsPost
        from apps.onboarding.models import OnboardingModule

        stats = {
            "Course": 0,
            "Lesson": 0,
            "TestQuestion": 0,
            "OnboardingModule": 0,
            "Article": 0,
            "NewsPost": 0,
        }

        def translate_model(qs, *, fields_map: list[tuple[str, str]]):
            """
            fields_map: list of (source_en_field, target_lang_field)
            """
            nonlocal stats

            # Collect candidates.
            objs = list(islice(qs.iterator(), limit))
            if not objs:
                return

            # For each field pair translate in batches.
            for src_field, dst_field in fields_map:
                candidates = []
                for obj in objs:
                    dst_val = getattr(obj, dst_field, "") or ""
                    if not _needs_translation(dst_val, lang):
                        continue
                    src_val = getattr(obj, src_field, "") or ""
                    src_val = _strip_auto_prefix(src_val)
                    if not src_val:
                        continue
                    candidates.append((obj, src_val))

                if not candidates:
                    continue

                # Batch translate for rate efficiency.
                texts = [t for _obj, t in candidates]
                translated = translate_texts(texts=texts, target_lang=lang)

                for (obj, _src), tr in zip(candidates, translated):
                    tr = (tr or "").strip()
                    if not tr:
                        continue
                    setattr(obj, dst_field, tr)
                    if apply:
                        obj.save(update_fields=[dst_field])
                    stats[obj.__class__.__name__] += 1

        # Courses
        translate_model(
            Course.objects.all().order_by("id"),
            fields_map=[
                ("title_en", f"title_{lang}"),
                ("description_en", f"description_{lang}"),
            ],
        )

        # Lessons (course content)
        translate_model(
            Lesson.objects.all().order_by("id"),
            fields_map=[
                ("title_en", f"title_{lang}"),
                ("content_en", f"content_{lang}"),
            ],
        )

        # Quiz questions/options: translate question text only (options are JSON; keep manual for now)
        translate_model(
            TestQuestion.objects.all().order_by("id"),
            fields_map=[
                ("question_text_en", f"question_text_{lang}"),
            ],
        )

        # Onboarding
        translate_model(
            OnboardingModule.objects.all().order_by("id"),
            fields_map=[
                ("title_en", f"title_{lang}"),
                ("description_en", f"description_{lang}"),
            ],
        )

        # Knowledge base
        translate_model(
            Article.objects.all().order_by("id"),
            fields_map=[
                ("title_en", f"title_{lang}"),
                ("content_en", f"content_{lang}"),
            ],
        )

        # News
        translate_model(
            NewsPost.objects.all().order_by("id"),
            fields_map=[
                ("title_en", f"title_{lang}"),
                ("content_en", f"content_{lang}"),
            ],
        )

        mode = "APPLIED" if apply else "DRY-RUN"
        self.stdout.write(self.style.SUCCESS(f"{mode}: translated fields written: {stats}"))

