from __future__ import annotations

import re
from dataclasses import dataclass

from exercise_scraper.models import Exercise

BLANK_PATTERN = re.compile(r"_{2,}|\.{3}|\(\s*[^)]+\s*\)")
NUMBERED_PATTERN = re.compile(r"^\s*\d+[\.\):\-]\s+")
NAV_PATTERN = re.compile(
    r"\b(menu|subscribe|cookie|newsletter|login|sign up|privacy policy|"
    r"all lessons|pdf download|worksheets? page|next page|previous page)\b",
    re.IGNORECASE,
)
HOME_MENU_PATTERN = re.compile(r"(^|\|)\s*home\s*(\||$)", re.IGNORECASE)
PAGE_LABEL_PATTERN = re.compile(
    r"^(home|menu|exercises?|grammar|worksheets?|lessons?)(\s*\||\s*[-–—]\s*)",
    re.IGNORECASE,
)
MULTI_PIPE_PATTERN = re.compile(r"\s*\|\s*")


@dataclass
class TopicValidation:
    passed: bool
    score_delta: float
    reasons: list[str]


def reject_navigation(text: str) -> TopicValidation | None:
    lower = text.lower().strip()
    if NAV_PATTERN.search(lower):
        return TopicValidation(False, -0.5, ["topic-nav-noise"])
    if HOME_MENU_PATTERN.search(lower):
        return TopicValidation(False, -0.5, ["topic-nav-noise"])
    if PAGE_LABEL_PATTERN.match(lower):
        return TopicValidation(False, -0.5, ["topic-page-label"])
    if lower.count("|") >= 2 and MULTI_PIPE_PATTERN.search(text):
        return TopicValidation(False, -0.45, ["topic-menu-pipe"])
    if len(lower) < 20 and not BLANK_PATTERN.search(text) and not NUMBERED_PATTERN.match(text):
        return TopicValidation(False, -0.3, ["topic-too-short"])
    return None


def require_exercise_shape(text: str, *, grammar_reason: str) -> TopicValidation:
    nav = reject_navigation(text)
    if nav:
        return nav
    if BLANK_PATTERN.search(text) or NUMBERED_PATTERN.match(text):
        return TopicValidation(True, 0.15, [grammar_reason, "topic-exercise-shape"])
    return TopicValidation(False, -0.25, ["topic-missing-shape"])
