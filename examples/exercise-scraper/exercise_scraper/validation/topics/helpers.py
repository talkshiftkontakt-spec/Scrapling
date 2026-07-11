from __future__ import annotations

import re

from exercise_scraper.models import Exercise
from exercise_scraper.validation.topics.base import (
    BLANK_PATTERN,
    reject_navigation,
    require_exercise_shape,
)


def validate_with_signals(
    exercise: Exercise,
    *,
    grammar_reason: str,
    marker_patterns: list[re.Pattern[str]],
    form_patterns: list[re.Pattern[str]] | None = None,
    min_score: float = 0.15,
    heading_phrases: list[str] | None = None,
) -> tuple[bool, float, list[str]]:
    text = exercise.text.strip()
    nav = reject_navigation(text)
    if nav and not nav.passed:
        return nav.passed, nav.score_delta, nav.reasons

    lower = text.lower()
    reasons: list[str] = []
    score = 0.0

    for pattern in marker_patterns:
        if pattern.search(text):
            score += 0.12
            reasons.append(f"{grammar_reason}-marker")

    for pattern in form_patterns or []:
        if pattern.search(text):
            score += 0.15
            reasons.append(f"{grammar_reason}-form")

    if BLANK_PATTERN.search(text):
        score += 0.12
        reasons.append(f"{grammar_reason}-blank")

    for phrase in heading_phrases or []:
        if phrase in lower and len(text) < 70:
            score -= 0.15
            reasons.append("heading-not-exercise")
            break

    if score >= min_score:
        shape = require_exercise_shape(text, grammar_reason=grammar_reason)
        if shape.passed:
            return True, score + shape.score_delta, list(dict.fromkeys(reasons + shape.reasons))

    return False, -0.2, reasons + [f"{grammar_reason}-reject"]
