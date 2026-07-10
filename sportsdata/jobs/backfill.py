from __future__ import annotations

from datetime import UTC, datetime

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult
from sportsdata.sources.football_data_uk import FootballDataUkClient


def run_backfill(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    client = FootballDataUkClient(config)
    counts = {"rows": 0}

    try:
        rows = client.import_all(seasons=config.football_data_seasons)
        for row in rows:
            storage.save_historical_match(row)
        counts["rows"] = len(rows)
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="backfill",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Historical football-data.co.uk rows imported",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="backfill",
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
