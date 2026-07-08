from __future__ import annotations

import json
import re
from pathlib import Path

from exercise_scraper.models import Exercise

QUESTION_PATTERN = re.compile(r"\?|___|\.{3}|\([^)]+\)")
SOLUTION_PATTERN = re.compile(r"\b(answer|odpowied|solution|klucz)\b", re.IGNORECASE)
NAV_PATTERN = re.compile(r"\b(home|menu|subscribe|cookie|newsletter|login|sign up)\b", re.IGNORECASE)
VERB_PATTERN = re.compile(r"\b(go|went|watch|watched|buy|bought|be|was|were|did|do)\b", re.IGNORECASE)


def validate_exercise(exercise: Exercise) -> Exercise:
    score = exercise.confidence * 0.45
    reasons: list[str] = []
    text = exercise.text.strip()
    lower = text.lower()

    if 25 <= len(text) <= 220:
        score += 0.15
        reasons.append("good-length")
    elif len(text) > 350:
        score -= 0.15
        reasons.append("too-long")
    else:
        score -= 0.05
        reasons.append("short")

    if QUESTION_PATTERN.search(text):
        score += 0.15
        reasons.append("exercise-shape")

    if exercise.exercise_type != "unknown":
        score += 0.1
        reasons.append(f"typed-{exercise.exercise_type}")

    if exercise.language != "unknown":
        score += 0.05
        reasons.append(f"lang-{exercise.language}")

    if VERB_PATTERN.search(text):
        score += 0.1
        reasons.append("grammar-signal")

    if SOLUTION_PATTERN.search(text):
        score -= 0.2
        reasons.append("answer-block")

    if NAV_PATTERN.search(lower):
        score -= 0.35
        reasons.append("navigation-noise")

    if exercise.answers:
        score += 0.05
        reasons.append("has-answers")

    exercise.validation_score = max(0.0, min(1.0, round(score, 4)))
    exercise.validation_reasons = reasons
    return exercise


def rank_exercises(exercises: list[Exercise]) -> list[Exercise]:
    validated = [validate_exercise(exercise) for exercise in exercises]
    return sorted(
        validated,
        key=lambda exercise: (
            exercise.validation_score,
            exercise.confidence,
            -len(exercise.text),
        ),
        reverse=True,
    )


def select_top_exercises(exercises: list[Exercise], limit: int = 3) -> list[Exercise]:
    ranked = rank_exercises(exercises)
    selected: list[Exercise] = []
    seen_sources: set[str] = set()

    for exercise in ranked:
        if len(selected) >= limit:
            break
        source_key = exercise.source_url.split("/")[2] if "/" in exercise.source_url else exercise.source_url
        if source_key in seen_sources and len(ranked) > limit:
            continue
        seen_sources.add(source_key)
        selected.append(exercise)

    if len(selected) < min(limit, len(ranked)):
        selected_ids = {exercise.id for exercise in selected}
        for exercise in ranked:
            if exercise.id in selected_ids:
                continue
            selected.append(exercise)
            selected_ids.add(exercise.id)
            if len(selected) >= limit:
                break

    return selected


def validate_file(input_path: Path, output_path: Path | None = None, limit: int = 3) -> dict:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    exercises = [Exercise(**item) for item in payload]
    ranked = rank_exercises(exercises)
    top = select_top_exercises(ranked, limit=limit)
    report = {
        "input": str(input_path),
        "total": len(exercises),
        "selected": len(top),
        "top": [exercise.to_dict() for exercise in top],
    }
    if output_path:
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
