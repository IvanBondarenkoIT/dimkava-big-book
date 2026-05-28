"""
Import regulations + quiz from a Telegram JSON export.

Input:  data/input/result.json (Telegram export)
Output:
  - input/hr docs/content/regulations.yaml  (KB sections + articles)
  - input/hr docs/content/regulations_course.yaml (course + quiz)

This command is designed to be safe and repeatable:
  - It only writes the two output YAML files (does not touch DB).
  - The existing loaders (load_articles/load_courses) remain the source of truth.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand


TELEGRAM_DEFAULT_PATH = Path(settings.BASE_DIR) / "data" / "input" / "result.json"
REGULATIONS_YAML_PATH = Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations.yaml"
REGULATIONS_COURSE_YAML_PATH = (
    Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations_course.yaml"
)


def _norm_text(value: Any) -> str:
    """Telegram 'text' can be a string or an array of entities (dicts)."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        out: list[str] = []
        for part in value:
            if isinstance(part, str):
                out.append(part)
            elif isinstance(part, dict):
                t = part.get("text", "")
                if part.get("type") == "bold" and t:
                    out.append(f"**{t}**")
                else:
                    out.append(t)
        return "".join(out)
    return ""


_re_ka = re.compile(r"[ა-ჰ]")
_re_ru = re.compile(r"[А-Яа-яЁё]")


def _detect_lang(text: str) -> str:
    if _re_ka.search(text):
        return "ka"
    if _re_ru.search(text):
        return "ru"
    return "other"


def _first_title_line(text: str) -> str:
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        # Trim common emoji/prefix noise
        l = re.sub(r"^[^A-Za-zА-Яа-яა-ჰ0-9]+", "", l).strip()
        if l:
            return l[:200]
    return "Regulations"


def _mk_article(msg_id: int, lang: str, title: str, content: str) -> dict[str, Any]:
    # We keep slug stable and fully deterministic.
    slug = f"tg-{msg_id}"
    base: dict[str, Any] = {
        "slug": slug,
        "section": "regulations",
        "status": "published",
        # EN is filled with the best available source text to avoid blank UI.
        # Proper English translation can be iterated later.
        "title_en": title if lang != "other" else "Regulations",
        "content_en": content,
        "title_ru": "",
        "content_ru": "",
        "title_ka": "",
        "content_ka": "",
        "source_message_id": msg_id,
    }
    if lang == "ru":
        base["title_ru"] = title
        base["content_ru"] = content
    elif lang == "ka":
        base["title_ka"] = title
        base["content_ka"] = content
    return base


@dataclass(frozen=True)
class QuizQuestion:
    number: int
    text: str
    options: list[str]


_re_ru_q = re.compile(r"^\s*(\d+)\.\s+(.*)$")
_re_opt = re.compile(r"^\s*([ABCD])\)\s+(.*)$")


def _parse_ru_quiz(text: str) -> list[QuizQuestion]:
    lines = [l.rstrip() for l in text.splitlines()]
    out: list[QuizQuestion] = []
    i = 0
    while i < len(lines):
        m = _re_ru_q.match(lines[i])
        if not m:
            i += 1
            continue
        num = int(m.group(1))
        qtext = m.group(2).strip()
        opts: list[str] = []
        j = i + 1
        while j < len(lines):
            mm = _re_opt.match(lines[j])
            if mm:
                opts.append(mm.group(2).strip())
                j += 1
                continue
            # Next question starts
            if _re_ru_q.match(lines[j]):
                break
            j += 1
        if qtext and len(opts) >= 2:
            out.append(QuizQuestion(number=num, text=qtext, options=opts[:4]))
        i = j
    return out


def _parse_ka_quiz(text: str) -> dict[int, QuizQuestion]:
    # Georgian test is structured with bold question lines like "1. ...", options on next lines.
    # We'll reuse the RU parser logic by stripping bold markers and using same regexes where possible.
    cleaned = text.replace("**", "")
    qq = _parse_ru_quiz(cleaned)
    return {q.number: q for q in qq}


class Command(BaseCommand):
    help = "Generate KB Regulations + Regulations Quiz YAML from Telegram export"

    def add_arguments(self, parser):
        parser.add_argument("--input", default=str(TELEGRAM_DEFAULT_PATH), help="Path to Telegram result.json")
        parser.add_argument("--out-regulations", default=str(REGULATIONS_YAML_PATH), help="Output KB YAML path")
        parser.add_argument("--out-course", default=str(REGULATIONS_COURSE_YAML_PATH), help="Output course YAML path")

    def handle(self, *args, **options):
        in_path = Path(options["input"])
        out_regs = Path(options["out_regulations"])
        out_course = Path(options["out_course"])

        if not in_path.exists():
            self.stdout.write(self.style.ERROR(f"Input not found: {in_path}"))
            return

        data = json.loads(in_path.read_text(encoding="utf-8"))
        messages = data.get("messages", [])

        # Extract regulations-like messages (RU/KA)
        regs: list[dict[str, Any]] = []
        ru_test_text = ""
        ka_test_text = ""

        for m in messages:
            if m.get("type") != "message":
                continue
            mid = m.get("id")
            if not isinstance(mid, int):
                continue
            text = _norm_text(m.get("text", "")).strip()
            if not text:
                continue

            if text.strip().startswith("📝 ТЕСТ ПО РЕГЛАМЕНТАМ"):
                ru_test_text = text
                continue
            if ("ბლოკი" in text) and ("A)" in text and "B)" in text and "C)" in text and "D)" in text):
                ka_test_text = text
                continue

            low = text.lower()
            if ("регламент" in low) or ("правила" in low) or ("შინაგანაწეს" in low) or ("რეგლამენტ" in low):
                lang = _detect_lang(text)
                title = _first_title_line(text)
                regs.append(_mk_article(mid, lang, title, text))

        # Build KB YAML
        kb_doc: dict[str, Any] = {
            "sections": [
                {
                    "slug": "regulations",
                    "title_en": "Regulations",
                    "title_ru": "Регламенты",
                    "title_ka": "შინაგანაწესები",
                    "icon": "shield-check",
                    "order": 90,
                }
            ],
            "articles": regs,
        }

        out_regs.parent.mkdir(parents=True, exist_ok=True)
        out_regs.write_text(yaml.safe_dump(kb_doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Wrote regulations KB YAML: {out_regs} (articles: {len(regs)})"))

        # Build Course YAML with a quiz lesson
        ru_questions = _parse_ru_quiz(ru_test_text) if ru_test_text else []
        ka_map = _parse_ka_quiz(ka_test_text) if ka_test_text else {}

        questions_yaml: list[dict[str, Any]] = []
        for q in ru_questions:
            ka_q = ka_map.get(q.number)
            opts = q.options[:4]
            # We do not have an official answer key in the Telegram export.
            # To keep the quiz usable (completion flow) we mark all options as correct and set passing_score=0.
            opt_yaml = [{"text": o, "is_correct": True} for o in opts]
            q_yaml: dict[str, Any] = {
                "text_ru": q.text,
                "text_en": q.text,  # temporary: EN shows RU text until manual translation pass
                "text_ka": (ka_q.text if ka_q else ""),
                "options_ru": opt_yaml,
                "options": opt_yaml,  # EN/base
                "options_ka": ([{"text": o, "is_correct": True} for o in (ka_q.options[:4] if ka_q else [])]),
            }
            questions_yaml.append(q_yaml)

        course_doc: dict[str, Any] = {
            "courses": [
                {
                    "slug": "regulations",
                    "title_en": "Regulations",
                    "title_ru": "Регламенты",
                    "title_ka": "შინაგანაწესები",
                    "description_en": "Company regulations and standards.",
                    "description_ru": "Регламенты и стандарты компании.",
                    "description_ka": "კომპანიის შინაგანაწესები და სტანდარტები.",
                    "level": "beginner",
                    "estimated_minutes": 30,
                    "image": "",
                    "lessons": [
                        {
                            "order": 1,
                            "title_en": "Regulations Quiz",
                            "title_ru": "Тест по регламентам",
                            "title_ka": "შინაგანაწესების ტესტი",
                            "type": "quiz",
                            "minutes": 15,
                            "passing_score": 0,
                            "questions": questions_yaml,
                        }
                    ],
                }
            ]
        }

        out_course.parent.mkdir(parents=True, exist_ok=True)
        out_course.write_text(
            yaml.safe_dump(course_doc, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote regulations course YAML: {out_course} (questions: {len(questions_yaml)})"
            )
        )

