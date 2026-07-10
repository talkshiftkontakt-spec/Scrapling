from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    replacements = {
        "manchester united": "man united",
        "manchester city": "man city",
        "nottingham forest": "nottingham",
        "tottenham hotspur": "tottenham",
        "wolverhampton wanderers": "wolves",
        "brighton and hove albion": "brighton",
        "newcastle united": "newcastle",
    }
    return replacements.get(value, value)


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_name(left), normalize_name(right)).ratio()


def best_match(query: str, candidates: list[str], *, threshold: float = 0.72) -> str | None:
    best_name: str | None = None
    best_score = 0.0
    for candidate in candidates:
        score = similarity(query, candidate)
        if score > best_score:
            best_score = score
            best_name = candidate
    if best_score >= threshold:
        return best_name
    return None


def participants_match(home_a: str, away_a: str, home_b: str, away_b: str) -> bool:
    direct = similarity(home_a, home_b) >= 0.72 and similarity(away_a, away_b) >= 0.72
    swapped = similarity(home_a, away_b) >= 0.72 and similarity(away_a, home_b) >= 0.72
    return direct or swapped
