from __future__ import annotations

import re

from exercise_scraper.dictionary.models import VocabularyExercise, WordEntry
from exercise_scraper.models import Exercise, content_hash
from exercise_scraper.validation.topics.base import reject_navigation

BLANK_PATTERN = re.compile(r"_{2,}|\.{3}|\(\s*\)|\[\s*\]")
TRANSLATION_PATTERN = re.compile(
    r"(\btranslate\b|\bprzetłumacz\b|\bmatch\b|\b\d+[\.\)]\s+\w+.*[-–—])",
    re.IGNORECASE,
)


def score_vocabulary_exercise(text: str, word: WordEntry) -> float:
    score = 0.0
    lower = text.lower()
    en = word.en.lower()
    pl = word.pl.lower()

    if en in lower or pl in lower:
        score += 0.35
    if BLANK_PATTERN.search(text):
        score += 0.25
    if TRANSLATION_PATTERN.search(text):
        score += 0.2
    if 15 <= len(text) <= 300:
        score += 0.15
    if len(text) < 10:
        score -= 0.3
    return max(0.0, min(1.0, score))


def match_word_in_text(text: str, words: list[WordEntry]) -> WordEntry | None:
    lower = text.lower()
    for word in words:
        if word.en.lower() in lower or word.pl.lower() in lower:
            return word
    return None


def exercise_to_vocabulary(
    exercise: Exercise,
    *,
    track_id: str,
    level: str,
    words: list[WordEntry],
) -> VocabularyExercise | None:
    matched = match_word_in_text(exercise.text, words)
    if matched is None:
        return None

    score = score_vocabulary_exercise(exercise.text, matched)
    if score < 0.4:
        return None

    return VocabularyExercise(
        id=content_hash(exercise.text),
        text=exercise.text,
        track_id=track_id,
        level=level,
        matched_word=matched.en,
        matched_translation=matched.pl,
        source_url=exercise.source_url,
        source_title=exercise.source_title,
        language=exercise.language,
        exercise_type="translation",
        confidence=exercise.confidence,
        validation_score=score,
    )


def validate_vocabulary_exercise(exercise: VocabularyExercise) -> VocabularyExercise:
    nav = reject_navigation(exercise.text)
    reasons: list[str] = []
    score = exercise.validation_score

    if nav and not nav.passed:
        exercise.validation_score = 0.0
        exercise.validation_reasons = nav.reasons + ["vocab-reject"]
        return exercise

    if exercise.matched_word.lower() in exercise.text.lower():
        score += 0.1
        reasons.append("vocab-word-present")
    if BLANK_PATTERN.search(exercise.text) or TRANSLATION_PATTERN.search(exercise.text):
        score += 0.1
        reasons.append("vocab-exercise-shape")

    exercise.validation_score = max(0.0, min(1.0, round(score, 4)))
    exercise.validation_reasons = reasons
    return exercise


def rank_vocabulary_exercises(exercises: list[VocabularyExercise]) -> list[VocabularyExercise]:
    validated = [validate_vocabulary_exercise(item) for item in exercises]
    return sorted(
        [item for item in validated if item.validation_score >= 0.45],
        key=lambda item: (item.validation_score, item.confidence),
        reverse=True,
    )


def select_top_vocabulary(
    exercises: list[VocabularyExercise],
    *,
    limit: int = 5,
) -> list[VocabularyExercise]:
    ranked = rank_vocabulary_exercises(exercises)
    selected: list[VocabularyExercise] = []
    seen_words: set[str] = set()

    for exercise in ranked:
        if len(selected) >= limit:
            break
        key = exercise.matched_word.lower()
        if key in seen_words and len(ranked) > limit:
            continue
        seen_words.add(key)
        selected.append(exercise)

    if len(selected) < min(limit, len(ranked)):
        seen_ids = {item.id for item in selected}
        for exercise in ranked:
            if exercise.id in seen_ids:
                continue
            selected.append(exercise)
            if len(selected) >= limit:
                break

    return selected
