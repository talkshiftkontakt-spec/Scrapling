from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sportsdata.api.schemas import PaginatedResponse, SummaryResponse
from sportsdata.api.settings import ApiSettings
from sportsdata.config import PipelineConfig
from sportsdata.models import Sport
from sportsdata.pipeline import SportsDataPipeline


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _paginate(items: list[dict[str, Any]], *, total: int, limit: int, offset: int) -> dict[str, Any]:
    payload = PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
    )
    return payload.model_dump()


def create_app(config: PipelineConfig | None = None, api_settings: ApiSettings | None = None):
    try:
        from fastapi import Depends, FastAPI, Header, HTTPException, Query
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install sportsdata extra: pip install 'scrapling[sportsdata]'") from exc

    settings = api_settings or ApiSettings()
    app = FastAPI(
        title="SportsData API",
        version="1.0.0",
        description="Football and tennis data API for upcoming fixtures, prematch stats, and played match history.",
    )
    pipeline = SportsDataPipeline(config)
    dashboard_dir = Path(__file__).resolve().parent.parent / "dashboard"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
        if not settings.require_api_key and not settings.api_key:
            return
        expected = settings.api_key
        if not expected:
            return
        if x_api_key != expected:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

    app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

    @app.get("/health")
    def health() -> dict:
        return pipeline.health()

    @app.get("/summary", response_model=SummaryResponse)
    def summary(_: None = Depends(verify_api_key)) -> SummaryResponse:
        health = pipeline.health()
        return SummaryResponse(
            timestamp=health["timestamp"],
            db_path=health["db_path"],
            upcoming_events=health["upcoming_events"],
            match_results_total=health["match_results"],
            match_results_football=health["match_results_football"],
            match_results_tennis=health["match_results_tennis"],
            tennis_with_stats=pipeline.storage.count_match_results_with_stats(sport=Sport.TENNIS),
            football_with_stats=pipeline.storage.count_match_results_with_stats(sport=Sport.FOOTBALL),
            failed_jobs=health["failed_jobs"],
        )

    @app.get("/upcoming")
    def upcoming(
        sport: str | None = None,
        league: str | None = None,
        participant: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = Query(default=None, ge=1),
        offset: int = Query(default=0, ge=0),
        _: None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        sport_enum = Sport(sport) if sport else None
        page_size = settings.page_size(limit)
        rows = pipeline.storage.list_upcoming_events(
            sport_enum,
            league=league,
            participant=participant,
            from_date=_parse_datetime(from_date),
            to_date=_parse_datetime(to_date),
            limit=page_size,
            offset=offset,
        )
        total = pipeline.storage.count_upcoming_events(
            sport_enum,
            league=league,
            participant=participant,
            from_date=_parse_datetime(from_date),
            to_date=_parse_datetime(to_date),
        )
        payload = []
        for row in rows:
            event_id = row["id"]
            payload.append(
                {
                    **row,
                    "prematch_stats": pipeline.storage.latest_prematch_stats(event_id),
                    "odds": pipeline.storage.list_odds_for_event(event_id),
                }
            )
        return _paginate(payload, total=total, limit=page_size, offset=offset)

    @app.get("/events/{event_id}")
    def get_event(event_id: int, _: None = Depends(verify_api_key)) -> dict:
        row = pipeline.storage.get_event(event_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return {
            **row,
            "prematch_stats": pipeline.storage.latest_prematch_stats(event_id),
            "odds": pipeline.storage.list_odds_for_event(event_id),
        }

    @app.get("/results")
    def list_results(
        sport: str | None = None,
        league: str | None = None,
        participant: str | None = None,
        source: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        has_stats: bool | None = None,
        limit: int | None = Query(default=None, ge=1),
        offset: int = Query(default=0, ge=0),
        _: None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        sport_enum = Sport(sport) if sport else None
        page_size = settings.page_size(limit)
        filters = {
            "sport": sport_enum,
            "league": league,
            "participant": participant,
            "source": source,
            "from_date": _parse_datetime(from_date),
            "to_date": _parse_datetime(to_date),
            "has_stats": has_stats,
        }
        rows = pipeline.storage.list_match_results(
            **filters,
            limit=page_size,
            offset=offset,
        )
        total = pipeline.storage.count_match_results_filtered(**filters)
        return _paginate(rows, total=total, limit=page_size, offset=offset)

    @app.get("/results/{result_id}")
    def get_result(result_id: int, _: None = Depends(verify_api_key)) -> dict:
        row = pipeline.storage.get_match_result(result_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return row

    @app.post("/jobs/{job_name}")
    def run_job(job_name: str, _: None = Depends(verify_api_key)) -> dict:
        mapping = {
            "fixtures_sync": pipeline.run_fixtures_sync,
            "stats_enrich": pipeline.run_stats_enrich,
            "odds_snapshot": pipeline.run_odds_snapshot,
            "pre_match_boost": pipeline.run_pre_match_boost,
            "results_sync": pipeline.run_results_sync,
            "history_import": pipeline.run_history_import,
            "stats_backfill": lambda: pipeline.run_stats_backfill(sport=Sport.TENNIS),
            "backfill": pipeline.run_backfill,
            "all": pipeline.run_all,
        }
        if job_name not in mapping:
            raise HTTPException(status_code=404, detail="Unknown job")
        result = mapping[job_name]()
        if isinstance(result, list):
            return {"results": [item.to_dict() for item in result]}
        return result.to_dict()

    @app.get("/")
    def root():
        return FileResponse(dashboard_dir / "index.html")

    return app


def main() -> None:
    import os
    import uvicorn

    port = int(os.getenv("SPORTSDATA_PORT", "8080"))
    host = os.getenv("SPORTSDATA_HOST", "0.0.0.0")
    uvicorn.run("sportsdata.api.server:create_app", factory=True, host=host, port=port)


if __name__ == "__main__":
    main()
