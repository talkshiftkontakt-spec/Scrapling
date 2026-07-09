from __future__ import annotations

from datetime import UTC, datetime

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult, Sport
from sportsdata.sources.flashscore import FlashscoreClient


def run_fixtures_sync(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    client = FlashscoreClient(config)
    counts = {"football": 0, "tennis": 0}

    try:
        for sport in (Sport.FOOTBALL, Sport.TENNIS):
            events = client.fetch_upcoming(sport)
            for event in events:
                storage.upsert_event(event)
            counts[sport.value] = len(events)
        finished = datetime.now(tz=UTC)
        return JobRunResult(
            job_name="fixtures_sync",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Fixtures synchronized from Flashscore",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="fixtures_sync",
            started_at=started,
            finished_at=finished,
            success=False,
            message=str(exc),
            counts=counts,
        )
        storage.record_job_run(
            result.job_name,
            result.started_at,
            result.finished_at,
            result.success,
            result.message,
            result.counts,
        )
        raise
    else:
        storage.record_job_run(
            "fixtures_sync",
            started,
            finished,
            True,
            "Fixtures synchronized from Flashscore",
            counts,
        )
