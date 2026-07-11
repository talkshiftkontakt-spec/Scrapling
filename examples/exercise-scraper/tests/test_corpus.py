from __future__ import annotations

from exercise_scraper.models import Exercise
from exercise_scraper.taxonomy import load_grammar_taxonomy
from exercise_scraper.validation.pipeline import run_validation_pipeline
from exercise_scraper.validation.topics.past_simple import validate_past_simple
from exercise_scraper.validation.topics.present_perfect import validate_present_perfect


def test_taxonomy_loads_twenty_topics() -> None:
    taxonomy = load_grammar_taxonomy()
    assert len(taxonomy.topics) == 20
    assert taxonomy.get("past-simple") is not None
    assert taxonomy.get("present-perfect") is not None


def test_past_simple_rejects_menu_text() -> None:
    exercise = Exercise(
        text="Home | Subscribe | PDF downloads of all lessons",
        topic="Past Simple",
        source_url="https://example.test",
        confidence=0.9,
    )
    passed, _, reasons = validate_past_simple(exercise)
    assert passed is False
    assert any("nav" in reason or "reject" in reason for reason in reasons)


def test_past_simple_accepts_real_task() -> None:
    exercise = Exercise(
        text="1. She ___ (go) to school yesterday.",
        topic="Past Simple",
        source_url="https://example.test",
        exercise_type="fill_blank",
        confidence=0.8,
        language="en",
    )
    passed, _, _ = validate_past_simple(exercise)
    assert passed is True


def test_present_perfect_accepts_marker_task() -> None:
    exercise = Exercise(
        text="2. They have ___ (live) here since 2010.",
        topic="Present Perfect",
        source_url="https://example.test",
        exercise_type="fill_blank",
        confidence=0.8,
        language="en",
    )
    passed, _, _ = validate_present_perfect(exercise)
    assert passed is True


def test_pipeline_filters_junk_and_keeps_top_n() -> None:
    exercises = [
        Exercise(
            text="1. She ___ (go) to school yesterday.",
            topic="Past Simple",
            source_url="https://a.test",
            exercise_type="fill_blank",
            confidence=0.85,
            language="en",
        ),
        Exercise(
            text="2. They ___ (watch) TV last night.",
            topic="Past Simple",
            source_url="https://b.test",
            exercise_type="fill_blank",
            confidence=0.82,
            language="en",
        ),
        Exercise(
            text="3. We ___ (buy) milk yesterday.",
            topic="Past Simple",
            source_url="https://c.test",
            exercise_type="fill_blank",
            confidence=0.8,
            language="en",
        ),
        Exercise(
            text="Home | Menu | Subscribe",
            topic="Past Simple",
            source_url="https://noise.test",
            confidence=0.95,
            language="unknown",
        ),
    ]
    result = run_validation_pipeline(
        exercises,
        topic_id="past-simple",
        validator_names=["past_simple"],
        top_n=2,
    )
    assert result.raw_total == 4
    assert len(result.rejected) >= 1
    assert len(result.top) == 2
    assert all("subscribe" not in ex.text.lower() for ex in result.top)
