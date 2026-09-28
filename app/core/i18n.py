import json
from functools import lru_cache
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
CONTENT_DIR = LOCALES_DIR / "content"

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"en", "nl", "de"}
LANGUAGE_COOKIE_NAME = "lang"


@lru_cache
def _load_translations(language: str) -> dict[str, str]:
    path = CONTENT_DIR / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_language(preferred: str | None) -> str:
    if preferred:
        candidate = preferred.strip().lower()[:2]
        if candidate in SUPPORTED_LANGUAGES:
            return candidate
    return DEFAULT_LANGUAGE


def translate(language: str, key: str, **kwargs: object) -> str:
    messages = _load_translations(language)
    message = messages.get(key) or _load_translations(DEFAULT_LANGUAGE).get(key, key)
    return message.format(**kwargs) if kwargs else message


@lru_cache
def load_content_translations(code: str) -> dict[str, str]:
    path = CONTENT_DIR / f"{code}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
