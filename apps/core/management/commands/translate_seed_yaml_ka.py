"""
Fill missing *_ka fields in HR YAML seeds using DeepL (Georgian).

Requires DEEPL_AUTH_KEY in environment or .env (see apps.core.services.deepl_translate).

Usage:
  python manage.py translate_seed_yaml_ka
  python manage.py translate_seed_yaml_ka --only onboarding
  python manage.py translate_seed_yaml_ka --dry-run
"""
from pathlib import Path

import yaml
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from apps.core.services.deepl_translate import translate_texts

BASE = Path(settings.BASE_DIR) / "input" / "hr docs" / "content"
CHUNK = 35

PATHS = {
    "onboarding": BASE / "onboarding_training_plan.yaml",
    "news": BASE / "news_seed.yaml",
    "sops": BASE / "sops_and_standards.yaml",
    "courses": BASE / "courses_seed.yaml",
}


def _en_title(d: dict) -> str:
    return (d.get("title_en") or d.get("title") or "").strip()


def _en_desc(d: dict) -> str:
    return (d.get("description_en") or d.get("description") or "").strip()


def _en_content(d: dict) -> str:
    return (d.get("content_en") or d.get("content") or "").strip()


def _missing_ka(val) -> bool:
    return not (val or "").strip()


def _batch_translate_strings(strings: list[str]) -> list[str]:
    out: list[str] = []
    for i in range(0, len(strings), CHUNK):
        chunk = strings[i : i + CHUNK]
        out.extend(translate_texts(texts=chunk, target_lang="ka"))
    while len(out) < len(strings):
        out.append("")
    return out[: len(strings)]


def _dump(path: Path, data) -> None:
    path.write_text(
        yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        ),
        encoding="utf-8",
    )


class Command(BaseCommand):
    help = "Translate EN fields in seed YAML files to Georgian (*_ka) via DeepL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            choices=["all", "onboarding", "news", "sops", "courses"],
            default="all",
            help="Which seed file to process.",
        )
        parser.add_argument("--dry-run", action="store_true", help="Count fields only, do not write files.")

    def handle(self, *args, **options):
        only = options["only"]
        dry_run = bool(options["dry_run"])

        if not dry_run:
            try:
                translate_texts(texts=[], target_lang="ka")
            except ImproperlyConfigured as e:
                raise CommandError(str(e)) from e

        targets = list(PATHS.keys()) if only == "all" else [only]
        total = 0

        for name in targets:
            path = PATHS[name]
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"Skip (missing): {path}"))
                continue
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            texts: list[str] = []
            setters: list = []

            def add(d: dict, key: str, en: str) -> None:
                if not en or not _missing_ka(d.get(key)):
                    return
                texts.append(en)
                setters.append((d, key))

            if name == "onboarding":
                prog = data.get("program") or {}
                add(prog, "title_ka", _en_title(prog))
                add(prog, "description_ka", _en_desc(prog))
                for mod in data.get("modules") or []:
                    add(mod, "title_ka", _en_title(mod))
                    add(mod, "description_ka", _en_desc(mod))
                    for step in mod.get("steps") or []:
                        add(step, "title_ka", _en_title(step))
                        add(step, "content_ka", _en_content(step))

            elif name == "news":
                for post in data.get("posts") or []:
                    add(post, "title_ka", _en_title(post))
                    add(post, "content_ka", _en_content(post))

            elif name == "sops":
                for sec in data.get("sections") or []:
                    add(sec, "title_ka", _en_title(sec))
                for art in data.get("articles") or []:
                    add(art, "title_ka", _en_title(art))
                    add(art, "content_ka", _en_content(art))

            elif name == "courses":
                for course in data.get("courses") or []:
                    add(course, "title_ka", _en_title(course))
                    add(course, "description_ka", _en_desc(course))
                    for lesson in course.get("lessons") or []:
                        add(lesson, "title_ka", _en_title(lesson))
                        add(lesson, "content_ka", _en_content(lesson))
                        if lesson.get("type") != "quiz":
                            continue
                        for q in lesson.get("questions") or []:
                            q_en = (q.get("text_en") or q.get("text") or "").strip()
                            add(q, "text_ka", q_en)
                            opts_en = q.get("options_en") or q.get("options") or []
                            if not opts_en:
                                continue
                            opts_ka = q.get("options_ka")
                            if not opts_ka or len(opts_ka) < len(opts_en):
                                q["options_ka"] = [
                                    {"text": "", "is_correct": o.get("is_correct", False)} for o in opts_en
                                ]
                                opts_ka = q["options_ka"]
                            for j, oen in enumerate(opts_en):
                                txt = (oen.get("text") or "").strip()
                                if not txt:
                                    continue
                                if (opts_ka[j].get("text") or "").strip():
                                    continue
                                texts.append(txt)
                                setters.append(("opt", q, j))

            n = len(texts)
            total += n
            self.stdout.write(self.style.NOTICE(f"{name}: {n} field(s) to translate"))
            if dry_run or not texts:
                continue

            translated = _batch_translate_strings(texts)
            for (target, tr) in zip(setters, translated):
                tr = (tr or "").strip()
                if not tr:
                    continue
                if target[0] == "opt":
                    _, qd, j = target
                    qd["options_ka"][j]["text"] = tr
                    qd["options_ka"][j]["is_correct"] = (qd.get("options_en") or qd.get("options") or [])[
                        j
                    ].get("is_correct", False)
                else:
                    d, key = target
                    d[key] = tr

            _dump(path, data)
            self.stdout.write(self.style.SUCCESS(f"{name}: wrote {path}"))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY-RUN total fields: {total}"))
