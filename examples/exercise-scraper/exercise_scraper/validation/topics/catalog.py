from __future__ import annotations

import re

from exercise_scraper.models import Exercise
from exercise_scraper.validation.topics import past_simple, present_perfect
from exercise_scraper.validation.topics.helpers import validate_with_signals

# --- Tenses ---

_PRESENT_SIMPLE_MARKERS = [
    re.compile(r"\b(every|always|usually|often|sometimes|never|on mondays?)\b", re.I),
    re.compile(r"\b(he|she|it)\s+\w+s\b", re.I),
]
_PRESENT_SIMPLE_FORMS = [
    re.compile(r"\b(do|does|don't|doesn't)\s+\w+", re.I),
]


def validate_present_simple(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="present-simple",
        marker_patterns=_PRESENT_SIMPLE_MARKERS,
        form_patterns=_PRESENT_SIMPLE_FORMS,
        heading_phrases=["present simple"],
    )


_CONTINUOUS_MARKERS = [
    re.compile(r"\b(now|at the moment|currently|right now|look!|listen!)\b", re.I),
]
_CONTINUOUS_FORMS = [
    re.compile(r"\b(am|is|are|was|were)\s+\w+ing\b", re.I),
    re.compile(r"\b___\s+\w+ing\b"),
]


def validate_present_continuous(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="present-continuous",
        marker_patterns=_CONTINUOUS_MARKERS,
        form_patterns=_CONTINUOUS_FORMS,
        heading_phrases=["present continuous", "present progressive"],
    )


def validate_past_continuous(exercise: Exercise) -> tuple[bool, float, list[str]]:
    past_markers = [re.compile(r"\b(yesterday|last night|while|when|at \d|all day)\b", re.I)]
    return validate_with_signals(
        exercise,
        grammar_reason="past-continuous",
        marker_patterns=_CONTINUOUS_MARKERS + past_markers,
        form_patterns=[re.compile(r"\b(was|were)\s+\w+ing\b", re.I)],
        heading_phrases=["past continuous"],
    )


_PAST_PERFECT_MARKERS = [
    re.compile(r"\b(already|just|never|before|by the time|after)\b", re.I),
]
_PAST_PERFECT_FORMS = [
    re.compile(r"\b(had)\s+(\w+ed|\w+en|been|gone|done|seen)\b", re.I),
]


def validate_past_perfect(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="past-perfect",
        marker_patterns=_PAST_PERFECT_MARKERS,
        form_patterns=_PAST_PERFECT_FORMS,
        heading_phrases=["past perfect"],
    )


_FUTURE_MARKERS = [
    re.compile(r"\b(tomorrow|next week|next year|soon|later|in the future)\b", re.I),
]
_FUTURE_FORMS = [
    re.compile(r"\b(will|won't|shall|'ll)\s+\w+", re.I),
]


def validate_future_simple(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="future-simple",
        marker_patterns=_FUTURE_MARKERS,
        form_patterns=_FUTURE_FORMS,
        heading_phrases=["future simple"],
    )


_GOING_TO_MARKERS = [
    re.compile(r"\b(going to|gonna)\b", re.I),
    re.compile(r"\b(tomorrow|next week|plan|intend)\b", re.I),
]


def validate_going_to(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="going-to",
        marker_patterns=_GOING_TO_MARKERS,
        form_patterns=[re.compile(r"\b(am|is|are)\s+going\s+to\b", re.I)],
        heading_phrases=["going to"],
    )


# --- Structures ---

_MODAL_MARKERS = [
    re.compile(r"\b(can|could|may|might|must|should|ought to|have to|need to)\b", re.I),
]


def validate_modals(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="modals",
        marker_patterns=_MODAL_MARKERS,
        heading_phrases=["modal verbs"],
    )


_ARTICLE_MARKERS = [
    re.compile(r"\b(a|an|the)\s+___\b", re.I),
    re.compile(r"___\s+(apple|hour|university|sun|best)\b", re.I),
    re.compile(r"\b(article|a/an|the)\b", re.I),
]


def validate_articles(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="articles",
        marker_patterns=_ARTICLE_MARKERS,
        heading_phrases=["articles a an the"],
    )


_COMPARATIVE_MARKERS = [
    re.compile(r"\b(more|most|less|least|than|as \w+ as)\b", re.I),
    re.compile(r"\b\w+(er|est)\b", re.I),
]


def validate_comparatives(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="comparatives",
        marker_patterns=_COMPARATIVE_MARKERS,
        heading_phrases=["comparatives", "superlatives"],
    )


_PASSIVE_MARKERS = [
    re.compile(r"\b(by\s+\w+|passive)\b", re.I),
]
_PASSIVE_FORMS = [
    re.compile(r"\b(am|is|are|was|were|been|being)\s+(\w+ed|\w+en)\b", re.I),
]


def validate_passive_voice(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="passive-voice",
        marker_patterns=_PASSIVE_MARKERS,
        form_patterns=_PASSIVE_FORMS,
        heading_phrases=["passive voice"],
    )


_REPORTED_MARKERS = [
    re.compile(r"\b(said|told|asked|explained|reported|that)\b", re.I),
    re.compile(r"\b(he|she|they)\s+(was|were|had|would|could)\b", re.I),
]


def validate_reported_speech(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="reported-speech",
        marker_patterns=_REPORTED_MARKERS,
        heading_phrases=["reported speech", "indirect speech"],
    )


_CONDITIONAL_MARKERS = [
    re.compile(r"\b(if|unless|when)\b.*\b(will|would|had|were)\b", re.I),
    re.compile(r"\b(would|could|might)\s+\w+\s+if\b", re.I),
    re.compile(r"\bif\b.+___", re.I),
]


def validate_conditionals(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="conditionals",
        marker_patterns=_CONDITIONAL_MARKERS,
        heading_phrases=["conditional"],
    )


_RELATIVE_MARKERS = [
    re.compile(r"\b(who|which|that|whose|whom|where)\b", re.I),
    re.compile(r",\s*who\b", re.I),
]


def validate_relative_clauses(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="relative-clauses",
        marker_patterns=_RELATIVE_MARKERS,
        heading_phrases=["relative clause"],
    )


_GERUND_MARKERS = [
    re.compile(r"\b(gerund|infinitive|to \w+|___ing|___ to)\b", re.I),
    re.compile(r"\b(enjoy|mind|avoid|decide|hope|want)\s+(\w+ing|to)\b", re.I),
]


def validate_gerunds_infinitives(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="gerunds-infinitives",
        marker_patterns=_GERUND_MARKERS,
        heading_phrases=["gerund", "infinitive"],
    )


_PREPOSITION_MARKERS = [
    re.compile(r"\b(in|on|at|by|for|from|to|with|about|between|under|over)\s+___\b", re.I),
    re.compile(r"___\s+(in|on|at|Monday|night|the morning)\b", re.I),
    re.compile(r"\b(preposition|przyimek)\b", re.I),
]


def validate_prepositions(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="prepositions",
        marker_patterns=_PREPOSITION_MARKERS,
        heading_phrases=["prepositions"],
    )


_TAG_MARKERS = [
    re.compile(r",\s*(isn't|aren't|wasn't|weren't|don't|doesn't|didn't|won't|can't|couldn't|haven't|hasn't)\b", re.I),
    re.compile(r"\b(isn't it|aren't they|don't you|won't he)\b", re.I),
]


def validate_question_tags(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="question-tags",
        marker_patterns=_TAG_MARKERS,
        heading_phrases=["question tags"],
    )


_PHRASAL_MARKERS = [
    re.compile(
        r"\b(give up|look after|take off|put on|get up|turn on|find out|look for|"
        r"run out|carry on|break down|set up|pick up|go on)\b",
        re.I,
    ),
    re.compile(r"\b(phrasal verb|czasownik frazowy)\b", re.I),
]


def validate_phrasal_verbs(exercise: Exercise) -> tuple[bool, float, list[str]]:
    return validate_with_signals(
        exercise,
        grammar_reason="phrasal-verbs",
        marker_patterns=_PHRASAL_MARKERS,
        heading_phrases=["phrasal verbs"],
    )


# Re-export dedicated validators
validate_past_simple = past_simple.validate_past_simple
validate_present_perfect = present_perfect.validate_present_perfect
