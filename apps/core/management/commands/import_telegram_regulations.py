"""
Import regulations + quiz from a Telegram JSON export.

Input:  data/input/result.json (Telegram export)
Output:
  - input/hr docs/content/regulations.yaml  (KB sections + articles)
  - input/hr docs/content/regulations_course.yaml (course + quiz)

One regulation = one article (slug reg-<ru_message_id>) with RU + KA fields.
EN fields are left empty for apply_regulations_en_translations or manual edit.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand


TELEGRAM_DEFAULT_PATH = Path(settings.BASE_DIR) / "data" / "input" / "result.json"
REGLAMENTS_TXT_PATH = Path(settings.BASE_DIR) / "data" / "input" / "reglaments.txt"
_RE_TXT_HEADER = re.compile(r"^\[[\d.]+\s+\d+:\d{2}\]\s+Nini.*?HR:\s*(.*)$", re.MULTILINE)
REGULATIONS_YAML_PATH = Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations.yaml"
REGULATIONS_COURSE_YAML_PATH = (
    Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations_course.yaml"
)
EN_TRANSLATIONS_PATH = (
    Path(settings.BASE_DIR) / "input" / "hr docs" / "content" / "regulations_en_translations.yaml"
)


def _norm_text(value: Any) -> str:
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
        l = re.sub(r"^[^A-Za-zА-Яа-яა-ჰ0-9]+", "", l).strip()
        if l:
            return l[:200]
    return "Regulations"


def _normalize_title_key(text: str) -> str:
    title = _first_title_line(text).lower()
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"[^\w\sა-ჰа-яё]", "", title, flags=re.IGNORECASE)
    return title.strip()


def _is_regulation_text(text: str) -> bool:
    if text.strip().startswith("📝 ТЕСТ"):
        return False
    low = text.lower()
    return (
        ("регламент" in low)
        or ("правила" in low)
        or ("შინაგანაწეს" in low)
        or ("რეგლამენტ" in low)
    )


@dataclass
class RegMessage:
    message_id: int
    text: str
    reply_to: int | None = None


@dataclass
class RegulationPair:
    ru_id: int
    ru_text: str
    ka_id: int | None = None
    ka_text: str = ""
    match_method: str = "none"
    match_confidence: float = 0.0


def _pair_regulations(ru_msgs: list[RegMessage], ka_msgs: list[RegMessage]) -> list[RegulationPair]:
    ru_by_id = {m.message_id: m for m in ru_msgs}
    ka_by_id = {m.message_id: m for m in ka_msgs}

    pairs: list[RegulationPair] = [
        RegulationPair(ru_id=m.message_id, ru_text=m.text) for m in ru_msgs
    ]
    pair_by_ru = {p.ru_id: p for p in pairs}
    used_ka: set[int] = set()

    # 1) Direct reply_to_message_id
    for km in ka_msgs:
        reply = km.reply_to
        if reply and reply in pair_by_ru and km.message_id not in used_ka:
            p = pair_by_ru[reply]
            if p.ka_id is None:
                p.ka_id = km.message_id
                p.ka_text = km.text
                p.match_method = "reply"
                p.match_confidence = 1.0
                used_ka.add(km.message_id)

    # 2) Fuzzy match for remaining KA
    unmatched_ka = [km for km in ka_msgs if km.message_id not in used_ka]
    for km in unmatched_ka:
        ka_key = _normalize_title_key(km.text)
        best_ru: RegulationPair | None = None
        best_score = 0.0
        for p in pairs:
            if p.ka_id is not None:
                continue
            ru_key = _normalize_title_key(p.ru_text)
            if not ru_key or not ka_key:
                continue
            score = SequenceMatcher(None, ru_key, ka_key).ratio()
            if score > best_score:
                best_score = score
                best_ru = p
        if best_ru and best_score >= 0.35:
            best_ru.ka_id = km.message_id
            best_ru.ka_text = km.text
            best_ru.match_method = "fuzzy"
            best_ru.match_confidence = round(best_score, 3)
            used_ka.add(km.message_id)

    return sorted(pairs, key=lambda p: p.ru_id)


def _load_txt_ka_messages(path: Path) -> list[RegMessage]:
    """Parse KA regulation blocks from DimKava HR .txt export."""
    text = path.read_text(encoding="utf-8")
    matches = list(_RE_TXT_HEADER.finditer(text))
    out: list[RegMessage] = []
    for i, m in enumerate(matches):
        header_line = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        full = f"{header_line}\n{body}".strip() if body else header_line
        if not full or full.startswith("📝"):
            continue
        if _detect_lang(full) != "ka":
            continue
        low = full.lower()
        if not (
            _is_regulation_text(full)
            or "რეგლამენტ" in low
            or "წეს" in low
            or "შინაგან" in low
        ):
            continue
        out.append(RegMessage(message_id=900_000 + i, text=full))
    return out


def _keyword_ka_score(ru_text: str, ka_text: str) -> float:
    """Topic-based RU↔KA score when titles differ (e.g. HR .txt export)."""
    ru_l = ru_text.lower()
    ka_l = ka_text.lower()
    rules: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        (("прием", "товар"), ("მიღებ",)),
        (("стажер",), ("სტაჟიორ",)),
        (("рассроч",), ("განვადებ",)),
        (("планов", "продаж"), ("გეგმ",)),
        (("shop-seller",), ("shop-seller", "სალარო")),
        (("касс",), ("სალარო",)),
        (("инвентар",), ("ინვენტარ",)),
    ]
    for ru_parts, ka_parts in rules:
        if all(p in ru_l for p in ru_parts) and all(p in ka_l for p in ka_parts):
            return 0.85
    return 0.0


def _supplement_ka_pairs(pairs: list[RegulationPair], extra_ka: list[RegMessage]) -> int:
    """Fill missing KA on telegram-derived pairs using .txt export."""
    supplemented = 0
    used_ka_ids: set[int] = {p.ka_id for p in pairs if p.ka_id}
    for km in extra_ka:
        if km.message_id in used_ka_ids:
            continue
        ka_key = _normalize_title_key(km.text)
        best_p: RegulationPair | None = None
        best_score = 0.0
        for p in pairs:
            if p.ka_text:
                continue
            ru_key = _normalize_title_key(p.ru_text)
            score = 0.0
            if ru_key and ka_key:
                score = SequenceMatcher(None, ru_key, ka_key).ratio()
            score = max(score, _keyword_ka_score(p.ru_text, km.text))
            if score > best_score:
                best_score = score
                best_p = p
        if best_p and best_score >= 0.25:
            best_p.ka_id = km.message_id
            best_p.ka_text = km.text
            best_p.match_method = "txt_fuzzy"
            best_p.match_confidence = round(best_score, 3)
            used_ka_ids.add(km.message_id)
            supplemented += 1
    return supplemented


def _mk_unified_article(pair: RegulationPair) -> dict[str, Any]:
    slug = f"reg-{pair.ru_id}"
    title_ru = _first_title_line(pair.ru_text)
    title_ka = _first_title_line(pair.ka_text) if pair.ka_text else ""
    article: dict[str, Any] = {
        "slug": slug,
        "section": "regulations",
        "status": "published",
        "title_ru": title_ru,
        "content_ru": pair.ru_text,
        "title_ka": title_ka,
        "content_ka": pair.ka_text,
        "title_en": "",
        "content_en": "",
        "source_ru_id": pair.ru_id,
        "source_ka_id": pair.ka_id,
        "match_method": pair.match_method,
        "match_confidence": pair.match_confidence,
    }
    return article


def _apply_en_to_articles(articles: list[dict[str, Any]], en_map: dict[str, Any]) -> None:
    for article in articles:
        slug = article.get("slug", "")
        block = en_map.get(slug) or en_map.get("articles", {}).get(slug)
        if not block:
            continue
        if block.get("title_en"):
            article["title_en"] = block["title_en"]
        if block.get("content_en"):
            article["content_en"] = block["content_en"]


def _apply_en_to_course(course_doc: dict[str, Any], en_data: dict[str, Any]) -> None:
    course_en = en_data.get("course") or {}
    lessons_en = en_data.get("lessons") or {}
    quiz_en = en_data.get("quiz_questions") or []

    for course in course_doc.get("courses", []):
        if course.get("slug") != "regulations":
            continue
        for key in ("title_en", "description_en"):
            if course_en.get(key):
                course[key] = course_en[key]
        for lesson in course.get("lessons", []):
            if lesson.get("type") != "quiz":
                continue
            for key in ("title_en",):
                if lessons_en.get(key):
                    lesson[key] = lessons_en[key]
            questions = lesson.get("questions", [])
            for idx, q in enumerate(questions):
                if idx >= len(quiz_en):
                    continue
                block = quiz_en[idx]
                if block.get("text_en"):
                    q["text_en"] = block["text_en"]
                if block.get("options"):
                    q["options"] = block["options"]


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
            if _re_ru_q.match(lines[j]):
                break
            j += 1
        if qtext and len(opts) >= 2:
            out.append(QuizQuestion(number=num, text=qtext, options=opts[:4]))
        i = j
    return out


def _parse_ka_quiz(text: str) -> dict[int, QuizQuestion]:
    cleaned = text.replace("**", "")
    qq = _parse_ru_quiz(cleaned)
    return {q.number: q for q in qq}


def _opt_yaml(options: list[str]) -> list[dict[str, Any]]:
    return [{"text": o, "is_correct": True} for o in options[:4]]


class Command(BaseCommand):
    help = "Generate KB Regulations + Regulations Quiz YAML from Telegram export"

    def add_arguments(self, parser):
        parser.add_argument("--input", default=str(TELEGRAM_DEFAULT_PATH), help="Path to Telegram result.json")
        parser.add_argument("--out-regulations", default=str(REGULATIONS_YAML_PATH), help="Output KB YAML path")
        parser.add_argument("--out-course", default=str(REGULATIONS_COURSE_YAML_PATH), help="Output course YAML path")
        parser.add_argument(
            "--en-translations",
            default=str(EN_TRANSLATIONS_PATH),
            help="Optional YAML with EN title/content for articles and quiz",
        )
        parser.add_argument(
            "--skip-en",
            action="store_true",
            help="Do not merge EN translations file even if present",
        )
        parser.add_argument(
            "--txt-ka",
            default=str(REGLAMENTS_TXT_PATH),
            help="Optional HR .txt export to supplement missing KA (empty to skip)",
        )

    def handle(self, *args, **options):
        in_path = Path(options["input"])
        out_regs = Path(options["out_regulations"])
        out_course = Path(options["out_course"])
        en_path = Path(options["en_translations"])

        if not in_path.exists():
            self.stdout.write(self.style.ERROR(f"Input not found: {in_path}"))
            return

        data = json.loads(in_path.read_text(encoding="utf-8"))
        messages = data.get("messages", [])

        ru_regs: list[RegMessage] = []
        ka_regs: list[RegMessage] = []
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

            if not _is_regulation_text(text):
                continue

            lang = _detect_lang(text)
            reply_to = m.get("reply_to_message_id")
            if not isinstance(reply_to, int):
                reply_to = None
            if lang == "ru":
                ru_regs.append(RegMessage(message_id=mid, text=text, reply_to=reply_to))
            elif lang == "ka":
                ka_regs.append(RegMessage(message_id=mid, text=text, reply_to=reply_to))

        pairs = _pair_regulations(ru_regs, ka_regs)

        txt_ka = (options.get("txt_ka") or "").strip()
        txt_supplemented = 0
        if txt_ka:
            txt_path = Path(txt_ka)
            if txt_path.exists():
                txt_supplemented = _supplement_ka_pairs(pairs, _load_txt_ka_messages(txt_path))
            else:
                self.stdout.write(self.style.WARNING(f"txt-ka not found: {txt_path}"))

        articles = [_mk_unified_article(p) for p in pairs]

        reply_count = sum(1 for p in pairs if p.match_method == "reply")
        fuzzy_count = sum(1 for p in pairs if p.match_method == "fuzzy")
        txt_fuzzy_count = sum(1 for p in pairs if p.match_method == "txt_fuzzy")
        no_ka = sum(1 for p in pairs if not p.ka_text)

        en_data: dict[str, Any] = {}
        if not options["skip_en"] and en_path.exists():
            en_data = yaml.safe_load(en_path.read_text(encoding="utf-8")) or {}
            _apply_en_to_articles(articles, en_data)

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
            "articles": articles,
        }

        out_regs.parent.mkdir(parents=True, exist_ok=True)
        out_regs.write_text(yaml.safe_dump(kb_doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote regulations KB YAML: {out_regs} "
                f"(articles: {len(articles)}, reply: {reply_count}, fuzzy: {fuzzy_count}, "
                f"txt_ka: {txt_supplemented}+{txt_fuzzy_count}, ru_only: {no_ka})"
            )
        )

        ru_questions = _parse_ru_quiz(ru_test_text) if ru_test_text else []
        ka_map = _parse_ka_quiz(ka_test_text) if ka_test_text else {}

        questions_yaml: list[dict[str, Any]] = []
        for q in ru_questions:
            ka_q = ka_map.get(q.number)
            opts = q.options[:4]
            opt_yaml = _opt_yaml(opts)
            q_yaml: dict[str, Any] = {
                "text_ru": q.text,
                "text_en": "",
                "text_ka": (ka_q.text if ka_q else ""),
                "options_ru": opt_yaml,
                "options": [],
                "options_ka": _opt_yaml(ka_q.options[:4] if ka_q else []),
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

        if en_data:
            _apply_en_to_course(course_doc, en_data)
            # Fill options from EN when provided
            quiz_en = en_data.get("quiz_questions") or []
            for lesson in course_doc["courses"][0]["lessons"]:
                if lesson.get("type") != "quiz":
                    continue
                for idx, q in enumerate(lesson.get("questions", [])):
                    if idx < len(quiz_en) and quiz_en[idx].get("options"):
                        q["options"] = quiz_en[idx]["options"]
                    elif q.get("options_ru") and not q.get("options"):
                        q["options"] = q["options_ru"]

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
