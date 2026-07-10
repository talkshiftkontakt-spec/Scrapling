from __future__ import annotations

import re

from exercise_scraper.models import Exercise
from exercise_scraper.validation.topics.base import BLANK_PATTERN, reject_navigation, require_exercise_shape

PAST_MARKERS = re.compile(
    r"\b(yesterday|last (week|month|year|night|summer|monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday)|ago|in \d{4}|when i was)\b",
    re.IGNORECASE,
)
PAST_VERB_HINT = re.compile(
    r"\b(went|did|was|were|had|said|took|made|came|saw|got|knew|thought|brought|bought|"
    r"left|felt|put|found|told|became|gave)\b",
    re.IGNORECASE,
)


def validate_past_simple(exercise: Exercise) -> tuple[bool, float, list[str]]:
    text = exercise.text.strip()
    nav = reject_navigation(text)
    if nav and not nav.passed:
        return nav.passed, nav.score_delta, nav.reasons

    lower = text.lower()
    reasons: list[str] = []
    score = 0.0

    if BLANK_PATTERN.search(text):
        score += 0.2
        reasons.append("past-blank-or-verb-slot")
    if PAST_MARKERS.search(lower):
        score += 0.15
        reasons.append("past-time-marker")
    if PAST_VERB_HINT.search(lower):
        score += 0.1
        reasons.append("past-verb-signal")
    if "past simple" in lower or "simple past" in lower:
        score -= 0.1
        reasons.append("heading-not-exercise")

    if score >= 0.15:
        shape = require_exercise_shape(text, grammar_reason="past-simple-match")
        if shape.passed:
            return True, score + shape.score_delta, reasons + shape.reasons
    return False, -0.2, reasons + ["past-simple-reject"]
