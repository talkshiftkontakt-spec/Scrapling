from __future__ import annotations

from datetime import UTC, datetime

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult, MatchResult, Sport
from sportsdata.sources.flashscore import FlashscoreClient


def run_results_sync(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    flashscore = FlashscoreClient(config)
    counts = {"football": 0, "tennis": 0, "with_stats": 0}

    try:
        for sport in (Sport.FOOTBALL, Sport.TENNIS):
            finished_events = flashscore.fetch_recent_results(sport)
            for event in finished_events:
                flashscore_id = event.external_ids.get("flashscore", "")
                stats_payload: dict = {}
                if flashscore_id:
                    stats_payload = flashscore.match_statistics_payload(flashscore_id, sport)
                    if stats_payload.get("groups"):
                        counts["with_stats"] += 1

                result = MatchResult(
                    sport=sport,
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
                counts[sport.value] += 1

        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="results_sync",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Recent finished matches synced with statistics",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="results_sync",
            started_at=started,
            finished_at=finished,
            success=False,
            message=str(exc),
            counts=counts,
        )
        raise
    finally:
        storage.record_job_run(
            result.job_name,
            result.started_at,
            result.finished_at,
            result.success,
            result.message,
            result.counts,
        )
    return result
