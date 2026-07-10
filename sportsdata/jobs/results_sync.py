from __future__ import annotations

from datetime import UTC, datetime

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.jobs.flashscore_results import save_flashscore_events
from sportsdata.models import JobRunResult, Sport
from sportsdata.sources.flashscore import FlashscoreClient


def run_results_sync(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    flashscore = FlashscoreClient(config)
    counts: dict[str, int] = {"with_stats": 0}

    try:
        for sport in (Sport.FOOTBALL, Sport.TENNIS):
            finished_events = flashscore.fetch_recent_results(sport)
            save_flashscore_events(storage, flashscore, finished_events, counts=counts)

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
