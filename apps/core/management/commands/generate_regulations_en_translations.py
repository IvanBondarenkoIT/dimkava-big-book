"""
Build regulations_en_translations.yaml from RU fields in regulations YAML seeds.

Uses MyMemory free API (no key). Post-processes glossary terms (Shop Seller, Granit, RSG, etc.).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand

REGULATIONS_YAML = Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations.yaml"
COURSE_YAML = Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations_course.yaml"
OUT_PATH = Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations_en_translations.yaml"

# Terms to preserve (placeholders during translation, restored after)
_GLOSSARY_TERMS = [
    "Dim Kava Georgia",
    "Dim Kava",
    "Dom Kava",
    "Shop Seller",
    "Shop-Seller",
    "SHOP-SELLER",
    "Granit",
    "RSG",
    "Z-report",
    "Z-отчёт",
    "Regina",
    "BOG",
    "TBS",
    "Blasercafe",
    "Shop Seller",
]

_PLACEHOLDER_FMT = "⟦G{idx}⟧"


def _protect_glossary(text: str) -> tuple[str, list[tuple[str, str]]]:
    protected = text
    tokens: list[tuple[str, str]] = []
    seen: set[str] = set()
    for idx, term in enumerate(_GLOSSARY_TERMS):
        if term in seen:
            continue
        seen.add(term)
        if term in protected:
            ph = _PLACEHOLDER_FMT.format(idx=idx)
            tokens.append((ph, term))
            protected = protected.replace(term, ph)
    return protected, tokens


def _restore_glossary(text: str, tokens: list[tuple[str, str]]) -> str:
    out = text
    for ph, term in tokens:
        out = out.replace(ph, term)
    return out


def _translate_chunk(text: str, *, src: str = "ru", tgt: str = "en") -> str:
    if not text or not text.strip():
        return ""
    protected, tokens = _protect_glossary(text)
    max_len = 450
    if len(protected) <= max_len:
        parts = [protected]
    else:
        parts = []
        buf = ""
        for line in protected.split("\n"):
            if len(buf) + len(line) + 1 > max_len and buf:
                parts.append(buf)
                buf = line
            else:
                buf = f"{buf}\n{line}" if buf else line
        if buf:
            parts.append(buf)

    translated_parts: list[str] = []
    for part in parts:
        q = urllib.parse.quote(part)
        url = f"https://api.mymemory.translated.net/get?q={q}&langpair={src}|{tgt}"
        req = urllib.request.Request(url, headers={"User-Agent": "dimkava-big-book/1.0"})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    payload = json.loads(resp.read().decode("utf-8", errors="replace"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 5:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        tr = ((payload.get("responseData") or {}).get("translatedText") or "").strip()
        if not tr:
            tr = part
        translated_parts.append(tr)
        time.sleep(1.2)

    merged = "\n".join(translated_parts)
    out = _restore_glossary(merged, tokens)
    # Fix common API mistranslations of protected names
    for wrong, right in (
        ("Regine", "Regina"),
        ("logistician", "logistics staff"),
        ("Shop seller", "Shop Seller"),
    ):
        out = out.replace(wrong, right)
    return out


def _opt_en(options_ru: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for o in options_ru:
        t = _translate_chunk(o.get("text", ""))
        out.append({"text": t, "is_correct": o.get("is_correct", True)})
    return out


class Command(BaseCommand):
    help = "Generate regulations_en_translations.yaml (RU→EN via MyMemory + glossary)"

    def add_arguments(self, parser):
        parser.add_argument("--output", default=str(OUT_PATH))
        parser.add_argument("--articles-only", action="store_true")
        parser.add_argument("--quiz-only", action="store_true")
        parser.add_argument("--slug", default="", help="Translate only this article slug (e.g. reg-31193)")
        parser.add_argument("--initial-wait", type=int, default=0, help="Seconds to wait before starting (rate limit)")

    def handle(self, *args, **options):
        wait = int(options.get("initial_wait") or 0)
        if wait > 0:
            self.stdout.write(f"Waiting {wait}s before API calls...")
            time.sleep(wait)

        out_path = Path(options["output"])
        slug_filter = (options.get("slug") or "").strip()
        regs = yaml.safe_load(REGULATIONS_YAML.read_text(encoding="utf-8")) or {}
        course = yaml.safe_load(COURSE_YAML.read_text(encoding="utf-8")) or {}

        if out_path.exists():
            doc = yaml.safe_load(out_path.read_text(encoding="utf-8")) or {}
        else:
            doc = {}
        doc.setdefault(
            "course",
            {"title_en": "Regulations", "description_en": "Company regulations and standards."},
        )
        doc.setdefault("lessons", {"title_en": "Regulations Quiz"})
        doc.setdefault("articles", {})
        doc.setdefault("quiz_questions", [])

        if not options["quiz_only"]:
            self.stdout.write("Translating articles...")
            for a in regs.get("articles", []):
                slug = a["slug"]
                if slug_filter and slug != slug_filter:
                    continue
                existing = doc["articles"].get(slug) or {}
                if existing.get("title_en") and existing.get("content_en"):
                    self.stdout.write(f"  {slug} (skip, already translated)")
                    continue
                self.stdout.write(f"  {slug}")
                title_en = _translate_chunk(a.get("title_ru", ""))
                content_en = _translate_chunk(a.get("content_ru", ""))
                doc["articles"][slug] = {"title_en": title_en, "content_en": content_en}
                out_path.write_text(
                    yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
                )

        if not options["articles_only"]:
            self.stdout.write("Translating quiz...")
            for course_item in course.get("courses", []):
                if course_item.get("slug") != "regulations":
                    continue
                for lesson in course_item.get("lessons", []):
                    if lesson.get("type") != "quiz":
                        continue
                    for q in lesson.get("questions", []):
                        text_en = _translate_chunk(q.get("text_ru", ""))
                        options_en = _opt_en(q.get("options_ru", []))
                        doc["quiz_questions"].append({"text_en": text_en, "options": options_en})

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Wrote {out_path}"))
