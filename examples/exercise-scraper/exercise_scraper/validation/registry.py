from __future__ import annotations

from collections.abc import Callable

from exercise_scraper.models import Exercise
from exercise_scraper.validation.topics import past_simple, present_perfect
from exercise_scraper.validation.topics.base import require_exercise_shape

TopicValidator = Callable[[Exercise], tuple[bool, float, list[str]]]

_REGISTRY: dict[str, TopicValidator] = {
    "past_simple": past_simple.validate_past_simple,
    "present_perfect": present_perfect.validate_present_perfect,
}


def _generic_grammar_validator(exercise: Exercise) -> tuple[bool, float, list[str]]:
    shape = require_exercise_shape(exercise.text, grammar_reason="generic-grammar")
    return shape.passed, shape.score_delta, shape.reasons


def get_validator(name: str) -> TopicValidator:
    return _REGISTRY.get(name, _generic_grammar_validator)


def get_validators(names: list[str]) -> list[TopicValidator]:
    if not names:
        return [_generic_grammar_validator]
    return [get_validator(name) for name in names]
