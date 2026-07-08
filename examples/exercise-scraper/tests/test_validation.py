from __future__ import annotations

from pathlib import Path

from exercise_scraper.models import Exercise
from exercise_scraper.validation.quality import rank_exercises, select_top_exercises, validate_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_rank_exercises_prefers_real_tasks() -> None:
    exercises = [
        Exercise(text="Home | Subscribe | Newsletter", topic="Past Simple", source_url="https://noise.test"),
        Exercise(text="1. She ___ (go) to school yesterday.", topic="Past Simple", source_url="https://a.test", exercise_type="fill_blank", confidence=0.8, language="en"),
        Exercise(text="2. They ___ (watch) TV last night.", topic="Past Simple", source_url="https://b.test", exercise_type="fill_blank", confidence=0.75, language="en"),
    ]
    ranked = rank_exercises(exercises)
    assert ranked[0].source_url != "https://noise.test"
    assert ranked[-1].source_url == "https://noise.test"


def test_select_top_exercises_returns_three() -> None:
    exercises = [
        Exercise(text="1. She ___ (go) to school yesterday.", topic="Past Simple", source_url="https://a.test", exercise_type="fill_blank", confidence=0.8, language="en"),
        Exercise(text="2. They ___ (watch) TV last night.", topic="Past Simple", source_url="https://b.test", exercise_type="fill_blank", confidence=0.78, language="en"),
        Exercise(text="3. We ___ (buy) milk yesterday.", topic="Past Simple", source_url="https://c.test", exercise_type="fill_blank", confidence=0.76, language="en"),
        Exercise(text="Menu Home Subscribe", topic="Past Simple", source_url="https://d.test", confidence=0.9, language="unknown"),
    ]
    top = select_top_exercises(exercises, limit=3)
    assert len(top) == 3
    assert all("subscribe" not in exercise.text.lower() for exercise in top)


def test_validate_file_outputs_top_three(tmp_path: Path) -> None:
    input_path = tmp_path / "exercises.json"
    output_path = tmp_path / "validated.json"
    fixture_payload = [
        Exercise(text="1. She ___ (go) to school yesterday.", topic="Past Simple", source_url="https://a.test", exercise_type="fill_blank", confidence=0.8, language="en").to_dict(),
        Exercise(text="2. They ___ (watch) TV last night.", topic="Past Simple", source_url="https://b.test", exercise_type="fill_blank", confidence=0.78, language="en").to_dict(),
        Exercise(text="3. We ___ (buy) milk yesterday.", topic="Past Simple", source_url="https://c.test", exercise_type="fill_blank", confidence=0.76, language="en").to_dict(),
        Exercise(text="Home | Subscribe | Newsletter", topic="Past Simple", source_url="https://noise.test", confidence=0.95, language="unknown").to_dict(),
    ]
    input_path.write_text(__import__("json").dumps(fixture_payload), encoding="utf-8")

    report = validate_file(input_path, output_path, limit=3)
    assert report["selected"] == 3
    assert output_path.exists()
