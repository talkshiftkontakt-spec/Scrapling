from __future__ import annotations

import re
from typing import TYPE_CHECKING

from exercise_scraper.extract.domain_rules import match_domain_rule
from exercise_scraper.config import EXERCISE_KEYWORDS_EN, EXERCISE_KEYWORDS_PL
from exercise_scraper.models import Exercise, Language

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response

BLANK_PATTERN = re.compile(r"_{2,}|\.{3}|\(\s*\)|\[\s*\]")
NUMBERED_PATTERN = re.compile(r"^\s*\d+[\.\)]\s+")
NOISE_PATTERN = re.compile(
    r"(cookie|privacy policy|subscribe|newsletter|advertisement|reklama|polityka prywatności)",
    re.IGNORECASE,
)

from exercise_scraper.extract.selectors import EXERCISE_SELECTORS


def detect_language(text: str) -> Language:
    lower = text.lower()
    pl_hits = sum(1 for word in EXERCISE_KEYWORDS_PL if word in lower)
    en_hits = sum(1 for word in EXERCISE_KEYWORDS_EN if word in lower)

    polish_chars = bool(re.search(r"[ąćęłńóśźż]", lower))
    if polish_chars:
        pl_hits += 2

    if pl_hits > en_hits:
        return "pl"
    if en_hits > pl_hits:
        return "en"
    return "unknown"


def classify_exercise_type(text: str) -> str:
    lower = text.lower()
    if BLANK_PATTERN.search(text):
        return "fill_blank"
    if re.search(r"\b(a|b|c|d)\b", lower) and "?" in text:
        return "multiple_choice"
    if any(word in lower for word in ("rewrite", "przetłumacz", "put the verb", "zmień")):
        return "rewrite"
    return "unknown"


def score_exercise(text: str) -> float:
    score = 0.0
    lower = text.lower()

    if NUMBERED_PATTERN.match(text):
        score += 0.3
    if BLANK_PATTERN.search(text):
        score += 0.3
    if any(keyword in lower for keyword in EXERCISE_KEYWORDS_EN | EXERCISE_KEYWORDS_PL):
        score += 0.2
    if 20 <= len(text) <= 500:
        score += 0.2
    if len(text) < 15 or len(text) > 800:
        score -= 0.3
    if NOISE_PATTERN.search(text):
        score -= 0.5

    return max(0.0, min(1.0, score))


def _element_text(node) -> str:
    try:
        return str(node.get_all_text(separator=" ", strip=True))
    except Exception:
        text = getattr(node, "text", "")
        return str(text).strip()


def _page_title(response: "Response") -> str:
    title = response.css("title::text").get()
    return str(title).strip() if title else response.url


def _looks_like_exercise_section(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in EXERCISE_KEYWORDS_EN | EXERCISE_KEYWORDS_PL)


def extract_exercises(
    response: "Response",
    *,
    topic: str,
    min_confidence: float = 0.4,
    domain_rules: dict | None = None,
) -> list[Exercise]:
    source_url = response.url
    source_title = _page_title(response)
    candidates: list[tuple[str, float]] = []
    seen_text: set[str] = set()

    rule = match_domain_rule(source_url, domain_rules)
    selectors = rule.selectors if rule else EXERCISE_SELECTORS
    effective_min = rule.min_confidence if rule and rule.min_confidence is not None else min_confidence

    for selector in selectors:
        for node in response.css(selector):
            text = _element_text(node)
            if not text or text in seen_text:
                continue
            seen_text.add(text)
            confidence = score_exercise(text)
            if confidence >= effective_min:
                candidates.append((text, confidence))

    if not candidates:
        body_chunks = response.css("article, main, #content, .content, .entry-content")
        nodes = body_chunks if body_chunks else [response]
        for container in nodes:
            for paragraph in container.css("p, li"):
                text = _element_text(paragraph)
                if not text or text in seen_text:
                    continue
                if not (_looks_like_exercise_section(text) or BLANK_PATTERN.search(text)):
                    continue
                seen_text.add(text)
                confidence = score_exercise(text)
                if confidence >= effective_min:
                    candidates.append((text, confidence))

    exercises: list[Exercise] = []
    for text, confidence in candidates:
        exercises.append(
            Exercise(
                text=text,
                topic=topic,
                source_url=source_url,
                source_title=source_title,
                exercise_type=classify_exercise_type(text),  # type: ignore[arg-type]
                language=detect_language(text),
                confidence=confidence,
            )
        )

    return exercises


def extract_answer_key(response: "Response") -> str | None:
    for heading in response.css("h1, h2, h3, h4, strong, b"):
        label = _element_text(heading).lower()
        if "answer" in label or "odpowiedz" in label or "klucz" in label:
            sibling_text = _element_text(heading.getparent()) if hasattr(heading, "getparent") else ""
            if sibling_text and len(sibling_text) > len(label):
                return sibling_text
    return None
