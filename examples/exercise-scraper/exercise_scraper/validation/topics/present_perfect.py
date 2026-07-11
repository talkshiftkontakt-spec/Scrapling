from __future__ import annotations

import re

from exercise_scraper.models import Exercise
from exercise_scraper.validation.topics.base import BLANK_PATTERN, reject_navigation, require_exercise_shape

PP_MARKERS = re.compile(
    r"\b(ever|never|already|yet|just|since|for|recently|lately|so far|up to now)\b",
    re.IGNORECASE,
)
PP_FORM = re.compile(
    r"\b(has|have|had)\s+(\w+ed|\w+en|been|gone|done|seen|written|taken|broken)\b",
    re.IGNORECASE,
)


def validate_present_perfect(exercise: Exercise) -> tuple[bool, float, list[str]]:
    text = exercise.text.strip()
    nav = reject_navigation(text)
    if nav and not nav.passed:
        return nav.passed, nav.score_delta, nav.reasons

    lower = text.lower()
    reasons: list[str] = []
    score = 0.0

    if PP_MARKERS.search(lower):
        score += 0.15
        reasons.append("pp-marker")
    if PP_FORM.search(text):
        score += 0.2
        reasons.append("pp-have-participle")
    if BLANK_PATTERN.search(text) and ("have" in lower or "has" in lower or "___" in text):
        score += 0.15
        reasons.append("pp-blank-with-aux")

    if "present perfect" in lower and len(text) < 60:
        score -= 0.15
        reasons.append("heading-not-exercise")

    if score >= 0.15:
        shape = require_exercise_shape(text, grammar_reason="present-perfect-match")
        if shape.passed:
            return True, score + shape.score_delta, reasons + shape.reasons
    return False, -0.2, reasons + ["present-perfect-reject"]
