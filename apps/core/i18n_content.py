"""Shared helpers for multilingual HR content editing."""
from __future__ import annotations

import re

from django.db.models import Q


def build_text_icontains_q(base_name: str, query: str) -> Q:
    """OR icontains across legacy + EN/RU/KA fields (ASCII-friendly DB prefilter)."""
    q = Q()
    for suffix in ('', '_en', '_ru', '_ka'):
        field = f'{base_name}{suffix}'
        q |= Q(**{f'{field}__icontains': query})
    return q


def obj_matches_i18n_text(instance, base_names: tuple[str, ...], query: str) -> bool:
    """
    Case-insensitive match across i18n text fields (works for Cyrillic on SQLite).
    Uses casefold() — «Задача» matches «задача».
    """
    needle = query.strip().casefold()
    if not needle:
        return False
    for base in base_names:
        for suffix in ('', '_en', '_ru', '_ka'):
            key = f'{base}{suffix}' if suffix else base
            val = getattr(instance, key, None)
            if val and needle in str(val).casefold():
                return True
    return False


def obj_matches_plain_text(instance, field_names: tuple[str, ...], query: str) -> bool:
    """Case-insensitive match on single-language fields (e.g. Role)."""
    needle = query.strip().casefold()
    if not needle:
        return False
    for name in field_names:
        val = getattr(instance, name, None)
        if val and needle in str(val).casefold():
            return True
    return False


def pick_i18n_value(instance, base: str) -> str:
    """Prefer EN, then RU, then KA, then legacy base field."""
    for suffix in ('_en', '_ru', '_ka', ''):
        key = f'{base}{suffix}' if suffix else base
        val = getattr(instance, key, '') or ''
        if val:
            return val
    return ''


def sync_legacy_fields(instance, field_map: dict[str, str]) -> None:
    """
    Copy i18n fields into legacy columns (load_* compatibility, search fallback).
    field_map: {'title': 'title', 'content': 'content'} — base name without locale suffix.
    """
    for legacy, base in field_map.items():
        setattr(instance, legacy, pick_i18n_value(instance, base))


def sync_question_legacy(question) -> None:
    sync_legacy_fields(question, {'question_text': 'question_text'})
    opts = (
        question.options_en
        or question.options_ru
        or question.options_ka
        or question.options
        or []
    )
    question.options = opts
    if not question.options_en:
        question.options_en = opts


def slugify_underscore(text: str, *, max_length: int = 120) -> str:
    if not text:
        return ''
    s = text.strip().lower()
    s = re.sub(r'[\s\-]+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:max_length] if s else ''


def ensure_unique_slug(model_class, slug: str, *, exclude_pk=None, max_length: int = 120, **filters):
    """Append _2, _3, … until slug is unique within filters."""
    base = slug[:max_length]
    candidate = base
    n = 2
    qs = model_class.objects.filter(**filters)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=candidate).exists():
        suffix = f'_{n}'
        candidate = f'{base[: max_length - len(suffix)]}{suffix}'
        n += 1
    return candidate
