from __future__ import annotations

from pathlib import Path

import pytest

from exercise_scraper.extract.heuristics import detect_language, extract_exercises, score_exercise
from exercise_scraper.models import content_hash
from exercise_scraper.exporters.writer import deduplicate_exercises
from exercise_scraper.queries import build_queries

FIXTURES = Path(__file__).parent / "fixtures"


from scrapling.parser import Selector


class FakeResponse(Selector):
    def __init__(self, html: str, url: str = "https://example.com/exercises") -> None:
        super().__init__(content=html, url=url)
        self.status = 200


@pytest.fixture
def en_response() -> FakeResponse:
    html = (FIXTURES / "past_simple_en.html").read_text(encoding="utf-8")
    return FakeResponse(html, url="https://example.com/past-simple-en")


@pytest.fixture
def pl_response() -> FakeResponse:
    html = (FIXTURES / "past_simple_pl.html").read_text(encoding="utf-8")
    return FakeResponse(html, url="https://example.com/past-simple-pl")


def test_build_queries_both_languages() -> None:
    pairs = build_queries("Past Simple", "both", limit_per_lang=3)
    assert len(pairs) == 6
    assert any("ćwiczenia" in query for query, _ in pairs)
    assert any("exercises" in query for query, _ in pairs)


def test_score_exercise_detects_blanks() -> None:
    text = "1. She ___ (go) to school yesterday."
    assert score_exercise(text) >= 0.4


def test_extract_exercises_en(en_response: FakeResponse) -> None:
    exercises = extract_exercises(en_response, topic="Past Simple", min_confidence=0.4)
    assert len(exercises) >= 2
    assert any("go" in ex.text for ex in exercises)
    assert all(ex.language in ("en", "unknown") for ex in exercises)


def test_extract_exercises_pl(pl_response: FakeResponse) -> None:
    exercises = extract_exercises(pl_response, topic="Past Simple", min_confidence=0.4)
    assert len(exercises) >= 2
    assert any("Wczoraj" in ex.text or "kupić" in ex.text for ex in exercises)
    assert any(ex.language == "pl" for ex in exercises)


def test_detect_language() -> None:
    assert detect_language("Uzupełnij zdania wczoraj") == "pl"
    assert detect_language("Fill in the blanks with the correct verb") == "en"


def test_deduplicate_exercises() -> None:
    from exercise_scraper.models import Exercise

    first = Exercise(text="1. Test ___", topic="T", source_url="https://a.test")
    second = Exercise(text="1. Test ___", topic="T", source_url="https://b.test")
    assert first.id == second.id
    assert len(deduplicate_exercises([first, second])) == 1


def test_content_hash_stable() -> None:
    assert content_hash("Hello   World") == content_hash("hello world")
