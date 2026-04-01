from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Iterable

from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class DeepLConfig:
    auth_key: str
    api_url: str


def get_deepl_config() -> DeepLConfig:
    auth_key = (os.environ.get("DEEPL_AUTH_KEY") or "").strip()
    if not auth_key:
        try:
            from decouple import config as decouple_config

            auth_key = (decouple_config("DEEPL_AUTH_KEY", default="") or "").strip()
        except ImportError:
            pass
    if not auth_key:
        raise ImproperlyConfigured(
            "DEEPL_AUTH_KEY is not set. Add it to .env to enable live auto-translation."
        )
    api_url = (os.environ.get("DEEPL_API_URL") or "").strip()
    if not api_url:
        try:
            from decouple import config as decouple_config

            api_url = (decouple_config("DEEPL_API_URL", default="") or "").strip()
        except ImportError:
            api_url = ""
    if not api_url:
        api_url = "https://api-free.deepl.com/v2/translate"
    return DeepLConfig(auth_key=auth_key, api_url=api_url)


def _deepl_target_lang(lang: str) -> str:
    lang = (lang or "").strip().lower()
    if lang == "ru":
        return "RU"
    if lang == "ka":
        return "KA"
    raise ValueError(f"Unsupported target language: {lang!r}")


def translate_texts(*, texts: Iterable[str], target_lang: str, source_lang: str = "EN") -> list[str]:
    """
    Translate a batch of texts using DeepL.
    Requires DEEPL_AUTH_KEY in environment.
    """
    cfg = get_deepl_config()
    target = _deepl_target_lang(target_lang)

    texts_list = list(texts)
    if not texts_list:
        return []

    # DeepL expects repeated "text" params; we use application/x-www-form-urlencoded.
    params = [("target_lang", target), ("source_lang", source_lang)]
    for t in texts_list:
        params.append(("text", t))

    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        cfg.api_url,
        method="POST",
        data=data,
        headers={
            "Authorization": f"DeepL-Auth-Key {cfg.auth_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    payload = json.loads(raw)
    translations = payload.get("translations") or []
    out = []
    for tr in translations:
        out.append((tr or {}).get("text") or "")
    # Preserve length; DeepL should match 1:1, but keep safe fallback.
    if len(out) != len(texts_list):
        out = (out + [""] * len(texts_list))[: len(texts_list)]
    return out

