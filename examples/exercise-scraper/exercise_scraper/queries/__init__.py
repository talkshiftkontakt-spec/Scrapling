from __future__ import annotations

from typing import Literal

from exercise_scraper.queries.en import build_en_queries
from exercise_scraper.queries.pl import build_pl_queries

LangMode = Literal["pl", "en", "both"]


def build_queries(
    topic: str,
    lang: LangMode,
    *,
    topic_en: str | None = None,
    topic_pl: str | None = None,
    limit_per_lang: int = 5,
) -> list[tuple[str, str]]:
    """Return (query, language_tag) pairs."""
    pairs: list[tuple[str, str]] = []

    if lang in ("en", "both"):
        en_topic = topic_en or topic
        for query in build_en_queries(en_topic, limit=limit_per_lang):
            pairs.append((query, "en"))

    if lang in ("pl", "both"):
        pl_topic = topic_pl or topic
        for query in build_pl_queries(pl_topic, limit=limit_per_lang):
            pairs.append((query, "pl"))

    return pairs
