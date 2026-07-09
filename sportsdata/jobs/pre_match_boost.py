from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult
from sportsdata.jobs.odds_snapshot import run_odds_snapshot
from sportsdata.jobs.stats_enrich import run_stats_enrich


def run_pre_match_boost(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    counts = {"selected": 0, "stats_runs": 0, "odds_runs": 0}
    now = datetime.now(tz=UTC)
    horizon = now + timedelta(hours=2)

    try:
        upcoming = storage.list_upcoming_events()
        soon = [
            row
            for row in upcoming
            if datetime.fromisoformat(row["start_time"]) <= horizon
        ]
        counts["selected"] = len(soon)
        if soon:
            run_stats_enrich(storage, config)
            counts["stats_runs"] = 1
            run_odds_snapshot(storage, config)
            counts["odds_runs"] = 1
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="pre_match_boost",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Pre-match boost completed",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="pre_match_boost",
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
