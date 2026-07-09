from __future__ import annotations

from datetime import UTC, datetime

from sportsdata.config import PipelineConfig, UNDERSTAT_LEAGUES
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult, MatchResult, Sport
from sportsdata.sources.football_data_uk import FootballDataUkClient
from sportsdata.sources.understat import UnderstatClient


def _parse_football_data_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def run_history_import(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    understat = UnderstatClient(config)
    football_data = FootballDataUkClient(config)
    counts = {"understat": 0, "football_data": 0}

    try:
        for league_name in UNDERSTAT_LEAGUES:
            for season in config.understat_seasons:
                for row in understat.played_matches(league_name, season=season):
                    start_time = row["start_time"]
                    result = MatchResult(
                        sport=Sport.FOOTBALL,
                        league=league_name,
                        home_participant=str(row.get("home", "")),
                        away_participant=str(row.get("away", "")),
                        start_time=start_time,
                        home_score=str(row.get("home_goals", "")),
                        away_score=str(row.get("away_goals", "")),
                        source="understat",
                        xg_payload={
                            "home_xg": row.get("home_xg"),
                            "away_xg": row.get("away_xg"),
                            "season": season,
                            "league_code": row.get("league_code"),
                        },
                        metadata={"understat_id": row.get("understat_id"), "forecast": row.get("forecast")},
                        external_ids={"understat": str(row.get("understat_id", ""))},
                    )
                    storage.upsert_match_result(result)
                    counts["understat"] += 1

        csv_rows = football_data.import_all(seasons=config.football_data_seasons)
        for row in csv_rows:
            start_time = _parse_football_data_date(row.get("match_date"))
            if start_time is None:
                continue
            league_label = f"FOOTBALL-DATA:{row['league_code']}:{row.get('season', '')}"
            result = MatchResult(
                sport=Sport.FOOTBALL,
                league=league_label,
                home_participant=str(row.get("home_team", "")),
                away_participant=str(row.get("away_team", "")),
                start_time=start_time,
                home_score=str(row.get("home_goals", "")),
                away_score=str(row.get("away_goals", "")),
                source="football-data.co.uk",
                stats_payload=row.get("stats_payload", {}),
                odds_payload=row.get("odds_payload", {}),
                metadata={"result": row.get("result"), "season": row.get("season")},
            )
            storage.upsert_match_result(result)
            storage.save_historical_match(row)
            counts["football_data"] += 1

        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="history_import",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Historical match results imported",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="history_import",
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
