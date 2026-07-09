from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from sportsdata.config import DEFAULT_DB_PATH, PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.jobs.backfill import run_backfill
from sportsdata.jobs.fixtures_sync import run_fixtures_sync
from sportsdata.jobs.odds_snapshot import run_odds_snapshot
from sportsdata.jobs.pre_match_boost import run_pre_match_boost
from sportsdata.jobs.stats_enrich import run_stats_enrich
from sportsdata.models import JobRunResult, Sport


class SportsDataPipeline:
    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.storage = Storage(self.config.db_path)

    def run_fixtures_sync(self) -> JobRunResult:
        return run_fixtures_sync(self.storage, self.config)

    def run_stats_enrich(self) -> JobRunResult:
        return run_stats_enrich(self.storage, self.config)

    def run_odds_snapshot(self) -> JobRunResult:
        return run_odds_snapshot(self.storage, self.config)

    def run_pre_match_boost(self) -> JobRunResult:
        return run_pre_match_boost(self.storage, self.config)

    def run_backfill(self) -> JobRunResult:
        return run_backfill(self.storage, self.config)

    def run_all(self) -> list[JobRunResult]:
        results = [
            self.run_fixtures_sync(),
            self.run_stats_enrich(),
            self.run_odds_snapshot(),
            self.run_backfill(),
        ]
        return results

    def export_upcoming_json(self, output_path: Path, sport: Sport | None = None) -> int:
        rows = self.storage.list_upcoming_events(sport=sport)
        enriched = []
        for row in rows:
            event_id = row["id"]
            enriched.append(
                {
                    **row,
                    "prematch_stats": self.storage.latest_prematch_stats(event_id),
                    "odds": self.storage.list_odds_for_event(event_id),
                }
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
        return len(enriched)

    def health(self) -> dict:
        upcoming = self.storage.list_upcoming_events()
        failed_jobs = self.storage.latest_failed_jobs()
        return {
            "status": "ok" if not failed_jobs else "degraded",
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "db_path": str(self.config.db_path),
            "upcoming_events": len(upcoming),
            "failed_jobs": failed_jobs,
        }
