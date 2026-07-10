from __future__ import annotations

from dataclasses import dataclass, field

from exercise_scraper.models import Exercise
from exercise_scraper.validation.quality import rank_exercises, select_top_exercises
from exercise_scraper.validation.registry import get_validators


@dataclass
class ValidationPipelineResult:
    raw_total: int
    passed: list[Exercise] = field(default_factory=list)
    rejected: list[Exercise] = field(default_factory=list)
    ranked: list[Exercise] = field(default_factory=list)
    top: list[Exercise] = field(default_factory=list)
    topic_id: str | None = None
    validator_names: list[str] = field(default_factory=list)

    def to_report(self, *, top_n: int) -> dict:
        return {
            "topic_id": self.topic_id,
            "validators": self.validator_names,
            "raw_total": self.raw_total,
            "passed_count": len(self.passed),
            "rejected_count": len(self.rejected),
            "top_n": top_n,
            "top_count": len(self.top),
            "pass_rate": round(len(self.passed) / self.raw_total, 4) if self.raw_total else 0.0,
            "rejection_reasons": _summarize_rejections(self.rejected),
            "top_scores": [
                {
                    "id": exercise.id,
                    "validation_score": exercise.validation_score,
                    "reasons": exercise.validation_reasons,
                }
                for exercise in self.top
            ],
        }


def _summarize_rejections(rejected: list[Exercise]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for exercise in rejected:
        for reason in exercise.validation_reasons:
            if reason.startswith("topic-") or reason.endswith("-reject"):
                counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def apply_topic_validators(
    exercise: Exercise,
    validators: list,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    topic_score_delta = 0.0
    any_passed = False

    for validator in validators:
        passed, delta, topic_reasons = validator(exercise)
        reasons.extend(topic_reasons)
        topic_score_delta += delta
        if passed:
            any_passed = True

    if validators and not any_passed:
        return False, reasons + ["topic-validator-failed"]

    exercise.validation_score = max(0.0, min(1.0, exercise.validation_score + topic_score_delta))
    exercise.validation_reasons = list(dict.fromkeys(exercise.validation_reasons + reasons))
    return True, exercise.validation_reasons


def run_validation_pipeline(
    exercises: list[Exercise],
    *,
    topic_id: str | None = None,
    validator_names: list[str] | None = None,
    top_n: int = 3,
    min_generic_score: float = 0.35,
) -> ValidationPipelineResult:
    validators = get_validators(validator_names or [])
    ranked_generic = rank_exercises(exercises)

    passed: list[Exercise] = []
    rejected: list[Exercise] = []

    for exercise in ranked_generic:
        if exercise.validation_score < min_generic_score:
            exercise.validation_reasons.append("generic-score-below-threshold")
            rejected.append(exercise)
            continue

        ok, _ = apply_topic_validators(exercise, validators)
        if ok:
            passed.append(exercise)
        else:
            rejected.append(exercise)

    ranked_passed = sorted(
        passed,
        key=lambda ex: (ex.validation_score, ex.confidence, -len(ex.text)),
        reverse=True,
    )
    top = select_top_exercises(ranked_passed, limit=top_n)

    return ValidationPipelineResult(
        raw_total=len(exercises),
        passed=passed,
        rejected=rejected,
        ranked=ranked_passed,
        top=top,
        topic_id=topic_id,
        validator_names=validator_names or [],
    )
