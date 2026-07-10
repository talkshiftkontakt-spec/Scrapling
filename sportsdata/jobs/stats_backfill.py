from __future__ import annotations

import json
from datetime import UTC, datetime

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult, Sport
from sportsdata.sources.flashscore import FlashscoreClient


def _stats_has_groups(stats_payload: object) -> bool:
    if not isinstance(stats_payload, dict):
        return False
    groups = stats_payload.get("groups")
    return isinstance(groups, list) and len(groups) > 0


def run_stats_backfill(
    storage: Storage,
    config: PipelineConfig,
    *,
    sport: Sport | None = None,
) -> JobRunResult:
    started = datetime.now(tz=UTC)
    flashscore = FlashscoreClient(config)
    counts: dict[str, int] = {
        "candidates": 0,
        "with_stats": 0,
        "still_empty": 0,
        "skipped_no_id": 0,
        "errors": 0,
    }
    result: JobRunResult | None = None

    try:
        batch_limit = config.stats_backfill_batch_size
        if batch_limit <= 0:
            batch_limit = None

        rows = storage.list_match_results_missing_stats(
            source="flashscore",
            sport=sport,
            limit=batch_limit,
        )
        counts["candidates"] = len(rows)

        for row in rows:
            external_ids = row.get("external_ids", {})
            if isinstance(external_ids, str):
                external_ids = json.loads(external_ids)
            flashscore_id = external_ids.get("flashscore")
            if not flashscore_id:
                counts["skipped_no_id"] += 1
                continue

            row_sport = Sport(row["sport"])
            try:
                stats_payload = flashscore.match_statistics_payload(flashscore_id, row_sport)
            except Exception:
                counts["errors"] += 1
                continue

            if _stats_has_groups(stats_payload):
                storage.update_match_result_stats(int(row["id"]), stats_payload)
                counts["with_stats"] += 1
            else:
                counts["still_empty"] += 1

        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="stats_backfill",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Match statistics backfilled for flashscore results",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="stats_backfill",
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
