from __future__ import annotations

import json
from pathlib import Path

import pytest

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.matching.names import participants_match, similarity
from sportsdata.models import Event, EventStatus, OddsSnapshot, Sport
from sportsdata.sources.flashscore import FlashscoreClient


def test_participants_match_handles_aliases() -> None:
    assert participants_match("Manchester United", "Fulham", "Man United", "Fulham")
    assert participants_match("Arsenal", "Coventry", "Arsenal", "Coventry")


def test_similarity_is_normalized() -> None:
    assert similarity("Tottenham Hotspur", "Tottenham") > 0.8


def test_flashscore_parse_embedded_feed() -> None:
    sample = "initialFeeds['fixtures'] = { data: `SA÷1¬~ZA÷ENGLAND: Premier League¬~AA÷abc123¬AD÷1787338800¬AE÷Arsenal¬AF÷Chelsea¬AB÷1¬` };"
    feed = FlashscoreClient.parse_embedded_feed(sample)
    assert feed is not None
    rows = FlashscoreClient.parse_feed(feed)
    assert rows[0]["AE"] == "Arsenal"


def test_flashscore_parse_feed_extracts_match() -> None:
    sample = "¬~ZA÷ENGLAND: Premier League¬ZB÷1¬~AA÷abc123¬AD÷1787338800¬AE÷Arsenal¬AF÷Chelsea¬AB÷1¬"
    rows = FlashscoreClient.parse_feed(sample)
    assert len(rows) == 1
    assert rows[0]["AE"] == "Arsenal"


def test_tennis_league_filter_excludes_itf_and_doubles() -> None:
    client = FlashscoreClient(PipelineConfig())
    assert client._is_relevant_tennis_league("ATP - SINGLES: Wimbledon (United Kingdom), grass")
    assert not client._is_relevant_tennis_league("ITF MEN - SINGLES: M15 Bucharest (Romania), clay")
    assert not client._is_relevant_tennis_league("ATP - DOUBLES: Wimbledon (United Kingdom), grass")


def test_storage_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    storage = Storage(db_path)
    event = Event(
        sport=Sport.FOOTBALL,
        league="ENGLAND: Premier League",
        home_participant="Arsenal",
        away_participant="Chelsea",
        start_time=__import__("datetime").datetime(2026, 8, 21, 20, 0, tzinfo=__import__("datetime").UTC),
        status=EventStatus.SCHEDULED,
        external_ids={"flashscore": "abc123"},
    )
    event_id = storage.upsert_event(event)
    rows = storage.list_upcoming_events(sport=Sport.FOOTBALL)
    assert rows
    assert rows[0]["id"] == event_id

    snapshot = OddsSnapshot(
        event_id=event_id,
        bookmaker="understat_model",
        market="1x2",
        selection="Arsenal",
        odds_decimal=1.55,
        scraped_at=__import__("datetime").datetime.now(tz=__import__("datetime").UTC),
    )
    storage.save_odds_snapshot(snapshot)
    odds = storage.list_odds_for_event(event_id)
    assert odds[0]["bookmaker"] == "understat_model"


def test_match_result_dedupe_key() -> None:
    from datetime import UTC, datetime

    from sportsdata.models import MatchResult, Sport

    result = MatchResult(
        sport=Sport.FOOTBALL,
        league="ENGLAND: Premier League",
        home_participant="Arsenal",
        away_participant="Chelsea",
        start_time=datetime(2024, 8, 21, 20, 0, tzinfo=UTC),
        home_score="2",
        away_score="1",
        source="understat",
        xg_payload={"home_xg": 1.8, "away_xg": 0.9},
    )
    assert "understat" in result.dedupe_key
    assert "arsenal" in result.dedupe_key


    pytest.importorskip("curl_cffi")
    config = PipelineConfig(days_ahead=1)
    client = FlashscoreClient(config)
    football = client.fetch_upcoming(Sport.FOOTBALL)
    tennis = client.fetch_upcoming(Sport.TENNIS)
    assert isinstance(football, list)
    assert isinstance(tennis, list)
