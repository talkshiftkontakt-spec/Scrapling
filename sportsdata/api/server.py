from __future__ import annotations

from pathlib import Path

from sportsdata.config import PipelineConfig
from sportsdata.db.storage import Storage
from sportsdata.models import Sport
from sportsdata.pipeline import SportsDataPipeline


def create_app(config: PipelineConfig | None = None):
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install sportsdata extra: pip install 'scrapling[sportsdata]'") from exc

    app = FastAPI(title="SportsData API", version="0.1.0")
    pipeline = SportsDataPipeline(config)
    dashboard_dir = Path(__file__).resolve().parent / "dashboard"

    app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

    @app.get("/health")
    def health() -> dict:
        return pipeline.health()

    @app.get("/upcoming")
    def upcoming(sport: str | None = None) -> list[dict]:
        sport_enum = Sport(sport) if sport else None
        rows = pipeline.storage.list_upcoming_events(sport=sport_enum)
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
        return payload

    @app.get("/events/{event_id}")
    def get_event(event_id: int) -> dict:
        row = pipeline.storage.get_event(event_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return {
            **row,
            "prematch_stats": pipeline.storage.latest_prematch_stats(event_id),
            "odds": pipeline.storage.list_odds_for_event(event_id),
        }

    @app.get("/results")
    def list_results(sport: str | None = None, league: str | None = None, limit: int = 50) -> list[dict]:
        sport_enum = Sport(sport) if sport else None
        return pipeline.storage.list_match_results(sport=sport_enum, league=league, limit=limit)

    @app.get("/results/{result_id}")
    def get_result(result_id: int) -> dict:
        row = pipeline.storage.get_match_result(result_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return row

    @app.post("/jobs/{job_name}")
    def run_job(job_name: str) -> dict:
        mapping = {
            "fixtures_sync": pipeline.run_fixtures_sync,
            "stats_enrich": pipeline.run_stats_enrich,
            "odds_snapshot": pipeline.run_odds_snapshot,
            "pre_match_boost": pipeline.run_pre_match_boost,
            "results_sync": pipeline.run_results_sync,
            "history_import": pipeline.run_history_import,
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
    import uvicorn

    uvicorn.run("sportsdata.api.server:create_app", factory=True, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
