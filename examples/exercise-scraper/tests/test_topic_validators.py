from __future__ import annotations

from exercise_scraper.models import Exercise
from exercise_scraper.taxonomy import load_grammar_taxonomy
from exercise_scraper.validation.registry import get_validator, registered_validator_names
from exercise_scraper.validation.topics import catalog


def test_all_taxonomy_validators_registered() -> None:
    taxonomy = load_grammar_taxonomy()
    registered = set(registered_validator_names())
    for topic in taxonomy.topics:
        for validator_name in topic.validators:
            assert validator_name in registered, f"Missing validator: {validator_name}"


def test_present_simple_accepts_exercise() -> None:
    exercise = Exercise(
        text="1. She ___ (work) in a bank every day.",
        topic="Present Simple",
        source_url="https://example.test",
        exercise_type="fill_blank",
        confidence=0.8,
        language="en",
    )
    passed, _, _ = catalog.validate_present_simple(exercise)
    assert passed is True


def test_modals_accepts_exercise() -> None:
    exercise = Exercise(
        text="2. You ___ (must) wear a seatbelt.",
        topic="Modals",
        source_url="https://example.test",
        exercise_type="fill_blank",
        confidence=0.8,
        language="en",
    )
    passed, _, _ = get_validator("modals")(exercise)
    assert passed is True


def test_articles_rejects_menu() -> None:
    exercise = Exercise(
        text="Home | Menu | Subscribe",
        topic="Articles",
        source_url="https://example.test",
        confidence=0.9,
    )
    passed, _, _ = catalog.validate_articles(exercise)
    assert passed is False


def test_conditionals_accepts_if_clause() -> None:
    exercise = Exercise(
        text="1. If it rains, we ___ (stay) at home.",
        topic="Conditionals",
        source_url="https://example.test",
        exercise_type="fill_blank",
        confidence=0.8,
        language="en",
    )
    passed, _, _ = catalog.validate_conditionals(exercise)
    assert passed is True


def test_drive_status_detail_shape() -> None:
    from exercise_scraper.drive.sync import drive_status_detail

    status = drive_status_detail()
    assert "configured" in status
    assert "package_installed" in status
