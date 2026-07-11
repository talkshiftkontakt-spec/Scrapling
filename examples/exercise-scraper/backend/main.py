from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.store import start_dictionary_job, start_job, store
from exercise_scraper.corpus.orchestrator import run_corpus_batch, run_corpus_topic
from exercise_scraper.service import ScrapeRequest, run_scrape
from exercise_scraper.taxonomy import load_grammar_taxonomy

app = FastAPI(title="Exercise Scraper API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
    <!doctype html>
    <html lang="pl">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Exercise Scraper API</title>
        <style>
          body {
            font-family: Arial, Helvetica, sans-serif;
            margin: 0;
            padding: 40px 24px;
            background: #f7f2e9;
            color: #221d19;
          }
          main {
            max-width: 760px;
            margin: 0 auto;
            background: #fffdf8;
            border: 1px solid #dccfbe;
            border-radius: 18px;
            padding: 28px;
          }
          code {
            background: #f1e8da;
            padding: 2px 8px;
            border-radius: 999px;
          }
          a {
            color: #a84632;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>Exercise Scraper API działa</h1>
          <p>To jest backend. Główny interfejs otwórz pod <code>http://localhost:3000</code>.</p>
          <p>Przydatne endpointy:</p>
          <ul>
            <li><a href="/api/health">/api/health</a></li>
            <li><a href="/docs">/docs</a></li>
            <li><a href="/api/jobs">/api/jobs</a></li>
          </ul>
        </main>
      </body>
    </html>
    """


@app.get("/health")
def health_alias() -> dict[str, str]:
    return {"status": "ok"}


class CreateJobBody(BaseModel):
    topic: str = Field(min_length=2, max_length=120)
    lang: str = Field(default="both", pattern="^(pl|en|both)$")
    provider: str = Field(default="duckduckgo", pattern="^(duckduckgo|serpapi)$")
    max_pages: int = Field(default=15, ge=1, le=60)
    topic_en: str | None = None
    topic_pl: str | None = None
    topic_id: str | None = None
    top_exercises: int = Field(default=3, ge=1, le=100)
    sync_drive: bool = False


class CorpusRunBody(BaseModel):
    lang: str = Field(default="both", pattern="^(pl|en|both)$")
    provider: str = Field(default="duckduckgo", pattern="^(duckduckgo|serpapi)$")
    max_pages: int = Field(default=15, ge=1, le=60)
    top_exercises: int = Field(default=3, ge=1, le=100)
    sync_drive: bool = False


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/jobs")
def list_jobs(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return {"jobs": store.list_jobs(limit=limit)}


@app.post("/api/jobs", status_code=201)
def create_job(body: CreateJobBody) -> dict:
    job = store.create_job({**body.model_dump(), "topic_id": body.topic_id})
    request = ScrapeRequest(
        topic=body.topic,
        lang=body.lang,  # type: ignore[arg-type]
        provider=body.provider,  # type: ignore[arg-type]
        max_pages=body.max_pages,
        topic_en=body.topic_en,
        topic_pl=body.topic_pl,
        topic_id=body.topic_id,
        top_exercises=body.top_exercises,
        use_corpus_layout=bool(body.topic_id),
        sync_drive=body.sync_drive,
    )
    if body.topic_id:
        entry = load_grammar_taxonomy().get(body.topic_id)
        if entry:
            request.validator_names = entry.validators
            request.topic_en = entry.primary_en
            request.topic_pl = entry.primary_pl
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


class DictionaryRunBody(BaseModel):
    provider: str = Field(default="duckduckgo", pattern="^(duckduckgo|serpapi)$")
    max_pages: int = Field(default=12, ge=1, le=40)
    top_exercises: int = Field(default=5, ge=1, le=50)


@app.get("/api/dictionary/tracks")
def list_dictionary_tracks() -> dict:
    from exercise_scraper.dictionary.taxonomy import load_dictionary_tracks, load_wordlist

    tracks = load_dictionary_tracks()
    return {
        "tracks": [
            {
                "id": track.id,
                "level": track.level,
                "language_pair": track.language_pair,
                "description": track.description,
                "word_count": len(load_wordlist(track.wordlist)) if track.wordlist else 0,
            }
            for track in tracks
        ]
    }


@app.post("/api/dictionary/tracks/{track_id}/run", status_code=201)
def run_dictionary_track_endpoint(track_id: str, body: DictionaryRunBody) -> dict:
    from exercise_scraper.dictionary.service import DictionaryRunRequest
    from exercise_scraper.dictionary.taxonomy import get_dictionary_track

    track = get_dictionary_track(track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Unknown dictionary track")

    job = store.create_job(
        {
            "topic": track.description,
            "lang": "both",
            "provider": body.provider,
            "max_pages": body.max_pages,
            "topic_id": track.id,
        }
    )
    request = DictionaryRunRequest(
        track_id=track.id,
        provider=body.provider,  # type: ignore[arg-type]
        max_pages=body.max_pages,
        top_exercises=body.top_exercises,
    )
    start_dictionary_job(job["id"], request)
    return {"job": store.get_job(job["id"]), "track_id": track_id}


@app.get("/api/jobs/{job_id}/vocabulary")
def get_job_vocabulary(job_id: str, limit: int = Query(default=200, ge=1, le=500)) -> dict:
    _ensure_job(job_id)
    items = store.list_vocabulary_exercises(job_id, limit=limit)
    return {"exercises": items, "total": len(items)}


@app.get("/api/drive/status")
def drive_status() -> dict:
    from exercise_scraper.drive.sync import drive_status_detail

    return drive_status_detail()


@app.get("/api/corpus/validators")
def list_validators() -> dict:
    from exercise_scraper.validation.registry import registered_validator_names

    return {"validators": registered_validator_names()}


@app.get("/api/corpus/topics")
def list_corpus_topics() -> dict:
    taxonomy = load_grammar_taxonomy()
    return {
        "topics": [
            {
                "id": topic.id,
                "level": topic.level,
                "category": topic.grammar_category,
                "en": topic.en,
                "pl": topic.pl,
                "validators": topic.validators,
            }
            for topic in taxonomy.topics
        ]
    }


@app.post("/api/corpus/topics/{topic_id}/run", status_code=201)
def run_corpus_topic_endpoint(topic_id: str, body: CorpusRunBody) -> dict:
    taxonomy = load_grammar_taxonomy()
    topic = taxonomy.get(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Unknown topic_id")

    job = store.create_job(
        {
            "topic": topic.primary_en,
            "lang": body.lang,
            "provider": body.provider,
            "max_pages": body.max_pages,
            "topic_id": topic.id,
        }
    )
    request = ScrapeRequest(
        topic=topic.primary_en,
        lang=body.lang,  # type: ignore[arg-type]
        provider=body.provider,  # type: ignore[arg-type]
        max_pages=body.max_pages,
        topic_en=topic.primary_en,
        topic_pl=topic.primary_pl,
        topic_id=topic.id,
        top_exercises=body.top_exercises,
        use_corpus_layout=True,
        validator_names=topic.validators,
        sync_drive=body.sync_drive,
    )
    start_job(job["id"], request)
    return {"job": store.get_job(job["id"]), "topic_id": topic_id}


@app.post("/api/corpus/run-all", status_code=201)
def run_corpus_all(body: CorpusRunBody, limit: int = Query(default=20, ge=1, le=50)) -> dict:
    taxonomy = load_grammar_taxonomy()
    jobs: list[dict] = []
    for topic in taxonomy.topics[:limit]:
        job = store.create_job(
            {
                "topic": topic.primary_en,
                "lang": body.lang,
                "provider": body.provider,
                "max_pages": body.max_pages,
                "topic_id": topic.id,
            }
        )
        request = ScrapeRequest(
            topic=topic.primary_en,
            lang=body.lang,  # type: ignore[arg-type]
            provider=body.provider,  # type: ignore[arg-type]
            max_pages=body.max_pages,
            topic_en=topic.primary_en,
            topic_pl=topic.primary_pl,
            topic_id=topic.id,
            top_exercises=body.top_exercises,
            use_corpus_layout=True,
            validator_names=topic.validators,
            sync_drive=body.sync_drive,
        )
        start_job(job["id"], request)
        jobs.append({"job_id": job["id"], "topic_id": topic.id})
    return {"queued": len(jobs), "jobs": jobs}
