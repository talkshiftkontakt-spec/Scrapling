from __future__ import annotations

from sportsdata.db.storage import Storage
from sportsdata.models import Event, MatchResult, Sport
from sportsdata.sources.flashscore import FlashscoreClient


def save_flashscore_events(
    storage: Storage,
    flashscore: FlashscoreClient,
    events: list[Event],
    *,
    counts: dict[str, int],
    fetch_stats: bool = True,
    stats_limit: int | None = None,
) -> None:
    stats_fetched = 0
    for event in events:
        flashscore_id = event.external_ids.get("flashscore", "")
        stats_payload: dict = {}
        if fetch_stats and flashscore_id:
            if stats_limit is None or stats_fetched < stats_limit:
                stats_payload = flashscore.match_statistics_payload(flashscore_id, event.sport)
                stats_fetched += 1
                if stats_payload.get("groups"):
                    counts["with_stats"] = counts.get("with_stats", 0) + 1

        result = MatchResult(
            sport=event.sport,
            league=event.league,
            home_participant=event.home_participant,
            away_participant=event.away_participant,
            start_time=event.start_time,
            home_score=event.home_score,
            away_score=event.away_score,
            source="flashscore",
            stats_payload=stats_payload,
            external_ids=event.external_ids,
            metadata=event.metadata,
        )
        storage.upsert_match_result(result)
        sport_key = event.sport.value
        counts[sport_key] = counts.get(sport_key, 0) + 1
