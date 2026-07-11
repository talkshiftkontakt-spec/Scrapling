from __future__ import annotations

from collections.abc import Callable

from exercise_scraper.models import Exercise
from exercise_scraper.validation.topics.base import require_exercise_shape
from exercise_scraper.validation.topics import catalog

TopicValidator = Callable[[Exercise], tuple[bool, float, list[str]]]

_REGISTRY: dict[str, TopicValidator] = {
    "present_simple": catalog.validate_present_simple,
    "past_simple": catalog.validate_past_simple,
    "present_continuous": catalog.validate_present_continuous,
    "past_continuous": catalog.validate_past_continuous,
    "present_perfect": catalog.validate_present_perfect,
    "past_perfect": catalog.validate_past_perfect,
    "future_simple": catalog.validate_future_simple,
    "going_to": catalog.validate_going_to,
    "modals": catalog.validate_modals,
    "articles": catalog.validate_articles,
    "comparatives": catalog.validate_comparatives,
    "passive_voice": catalog.validate_passive_voice,
    "reported_speech": catalog.validate_reported_speech,
    "conditionals": catalog.validate_conditionals,
    "relative_clauses": catalog.validate_relative_clauses,
    "gerunds_infinitives": catalog.validate_gerunds_infinitives,
    "prepositions": catalog.validate_prepositions,
    "question_tags": catalog.validate_question_tags,
    "phrasal_verbs": catalog.validate_phrasal_verbs,
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


def registered_validator_names() -> list[str]:
    return sorted(_REGISTRY.keys())
