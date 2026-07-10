from __future__ import annotations

from datetime import UTC, datetime

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.matching.names import participants_match
from sportsdata.models import JobRunResult, OddsSnapshot, Sport
from sportsdata.sources.oddsportal import OddsPortalClient
from sportsdata.sources.understat import UnderstatClient


def run_odds_snapshot(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    oddsportal = OddsPortalClient(config)
    understat = UnderstatClient(config)
    counts = {"events": 0, "snapshots": 0, "linked": 0}

    try:
        upcoming = storage.list_upcoming_events()
        counts["events"] = len(upcoming)
        discovered = (
            oddsportal.discover_h2h_events(max_links=config.odds_h2h_limit)
            if config.enable_oddsportal
            else []
        )

        for row in upcoming:
            event = storage.event_from_row(row)
            if event.id is None:
                continue

            matched_payload = None
            for item in discovered:
                event_data = item["event_data"]
                if participants_match(
                    event.home_participant,
                    event.away_participant,
                    str(event_data.get("home", "")),
                    str(event_data.get("away", "")),
                ):
                    matched_payload = event_data
                    storage.merge_external_id(event.id, "oddsportal", str(event_data.get("id", "")))
                    counts["linked"] += 1
                    break

            snapshots: list[OddsSnapshot] = []
            if matched_payload is not None:
                snapshots.extend(oddsportal.snapshots_from_event_data(event.id, matched_payload))

            if event.sport is Sport.FOOTBALL and config.enable_understat:
                snapshots.extend(_understat_model_odds(event.id, event, understat))

            for snapshot in snapshots:
                if snapshot.odds_decimal <= 0 and snapshot.bookmaker != "oddsportal_raw":
                    continue
                storage.save_odds_snapshot(snapshot)
                counts["snapshots"] += 1

        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="odds_snapshot",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Odds snapshots stored",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="odds_snapshot",
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


def _understat_model_odds(event_id: int, event, understat: UnderstatClient) -> list[OddsSnapshot]:
    now = datetime.now(tz=UTC)
    upcoming_rows = understat.upcoming_from_league(event.league)
    for row in upcoming_rows:
        if not participants_match(
            event.home_participant,
            event.away_participant,
            str(row.get("home", "")),
            str(row.get("away", "")),
        ):
            continue
        forecast = row.get("forecast") or {}
        return OddsPortalClient._forecast_snapshots(
            event_id=event_id,
            home=event.home_participant,
            away=event.away_participant,
            forecast=forecast,
            scraped_at=now,
            source="understat_model",
        )

    home_metrics = understat.team_xg(event.league, event.home_participant)
    away_metrics = understat.team_xg(event.league, event.away_participant)
    home_xg = home_metrics.get("xg")
    away_xg = away_metrics.get("xg")
    if home_xg is None or away_xg is None or home_xg <= 0 or away_xg <= 0:
        return []

    total = home_xg + away_xg
    forecast = {
        "w": (home_xg / total) * 0.72,
        "d": 0.28,
        "l": (away_xg / total) * 0.72,
    }
    return OddsPortalClient._forecast_snapshots(
        event_id=event_id,
        home=event.home_participant,
        away=event.away_participant,
        forecast=forecast,
        scraped_at=now,
        source="understat_model",
    )
