from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import JobRunResult, PrematchStats, Sport
from sportsdata.sources.flashscore import FlashscoreClient
from sportsdata.sources.sofascore import SofaScoreClient
from sportsdata.sources.understat import UnderstatClient


def run_stats_enrich(storage: Storage, config: PipelineConfig) -> JobRunResult:
    started = datetime.now(tz=UTC)
    flashscore = FlashscoreClient(config)
    understat = UnderstatClient(config)
    sofascore = SofaScoreClient(config)
    counts = {"events": 0, "stats_saved": 0, "sofascore_hits": 0}
    result: JobRunResult | None = None

    try:
        upcoming = storage.list_upcoming_events()
        counts["events"] = len(upcoming)
        processed = 0
        max_age = timedelta(hours=config.stats_max_age_hours)
        for row in upcoming:
            if config.stats_batch_size > 0 and processed >= config.stats_batch_size:
                break
            event = storage.event_from_row(row)
            existing = storage.latest_prematch_stats(event.id or 0)
            if existing and event.id is not None:
                scraped_at = datetime.fromisoformat(existing["scraped_at"])
                if datetime.now(tz=UTC) - scraped_at < max_age:
                    processed += 1
                    continue
            flashscore_id = event.external_ids.get("flashscore")
            h2h: list[dict] = []
            home_form: list[dict] = []
            away_form: list[dict] = []
            match_statistics: dict = {}
            if flashscore_id:
                h2h = flashscore.fetch_h2h(flashscore_id, sport=event.sport)
                home_form = flashscore.form_from_h2h(h2h, event.home_participant)
                away_form = flashscore.form_from_h2h(h2h, event.away_participant)
                match_statistics = flashscore.fetch_statistics(flashscore_id, sport=event.sport)
                if event.sport is Sport.TENNIS:
                    h2h = flashscore.h2h_direct_matches(
                        h2h,
                        event.home_participant,
                        event.away_participant,
                    )

            home_xg = away_xg = home_xga = away_xga = None
            if event.sport is Sport.FOOTBALL and config.enable_understat:
                home_metrics = understat.team_xg(event.league, event.home_participant)
                away_metrics = understat.team_xg(event.league, event.away_participant)
                home_xg = home_metrics.get("xg")
                home_xga = home_metrics.get("xga")
                away_xg = away_metrics.get("xg")
                away_xga = away_metrics.get("xga")

            sofa_payload = {}
            if config.enable_sofascore:
                sofa_payload = sofascore.enrich_event(
                    event.home_participant,
                    event.away_participant,
                    sport=event.sport.value,
                )
                if sofa_payload.get("available"):
                    counts["sofascore_hits"] += 1

            stats = PrematchStats(
                event_id=event.id or 0,
                scraped_at=datetime.now(tz=UTC),
                home_form_last5=home_form,
                away_form_last5=away_form,
                h2h=h2h,
                home_season_xg=home_xg,
                away_season_xg=away_xg,
                home_season_xga=home_xga,
                away_season_xga=away_xga,
                surface=event.metadata.get("surface"),
                surface_stats={"sofascore": sofa_payload, "flashscore": match_statistics},
                injuries={},
                raw_payload={
                    "flashscore_id": flashscore_id,
                    "player_ids": {
                        "home": event.metadata.get("home_player_id"),
                        "away": event.metadata.get("away_player_id"),
                    },
                },
            )
            if event.id is not None:
                storage.save_prematch_stats(stats)
                counts["stats_saved"] += 1
            processed += 1

        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="stats_enrich",
            started_at=started,
            finished_at=finished,
            success=True,
            message="Prematch stats enriched",
            counts=counts,
        )
    except Exception as exc:
        finished = datetime.now(tz=UTC)
        result = JobRunResult(
            job_name="stats_enrich",
            started_at=started,
            finished_at=finished,
            success=False,
            message=str(exc),
            counts=counts,
        )
        raise
    finally:
        if result is not None:
            storage.record_job_run(
                result.job_name,
                result.started_at,
                result.finished_at,
                result.success,
                result.message,
                result.counts,
            )
    return result
