from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.store import start_job, store
from exercise_scraper.service import ScrapeRequest

app = FastAPI(title="Exercise Scraper API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateJobBody(BaseModel):
    topic: str = Field(min_length=2, max_length=120)
    lang: str = Field(default="both", pattern="^(pl|en|both)$")
    provider: str = Field(default="duckduckgo", pattern="^(duckduckgo|serpapi)$")
    max_pages: int = Field(default=15, ge=1, le=60)
    topic_en: str | None = None
    topic_pl: str | None = None


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/jobs")
def list_jobs(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return {"jobs": store.list_jobs(limit=limit)}


@app.post("/api/jobs", status_code=201)
def create_job(body: CreateJobBody) -> dict:
    job = store.create_job(body.model_dump())
    request = ScrapeRequest(
        topic=body.topic,
        lang=body.lang,  # type: ignore[arg-type]
        provider=body.provider,  # type: ignore[arg-type]
        max_pages=body.max_pages,
        topic_en=body.topic_en,
        topic_pl=body.topic_pl,
    )
    start_job(job["id"], request)
    return {"job": store.get_job(job["id"])}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    try:
        return {"job": store.get_job(job_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@app.get("/api/jobs/{job_id}/urls")
def get_job_urls(job_id: str) -> dict:
    _ensure_job(job_id)
    return {"urls": store.list_urls(job_id)}


@app.get("/api/jobs/{job_id}/exercises")
def get_job_exercises(
    job_id: str,
    language: str = Query(default="all", pattern="^(all|pl|en|unknown)$"),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    _ensure_job(job_id)
    exercises = store.list_exercises(job_id, language=None if language == "all" else language, limit=limit, offset=offset)
    total = store.count_exercises(job_id, language=None if language == "all" else language)
    return {"exercises": exercises, "total": total, "limit": limit, "offset": offset}


def _ensure_job(job_id: str) -> None:
    try:
        store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
