from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from exercise_scraper.config import Settings
from exercise_scraper.service import ScrapeRequest, run_scrape

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "jobs.db"
OUTPUT_DIR = DATA_DIR / "output"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    lang TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    max_pages INTEGER NOT NULL,
                    topic_id TEXT,
                    status TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    progress_json TEXT NOT NULL,
                    manifest_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    finished_at TEXT
                )
                """
            )
            columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()}
            if "topic_id" not in columns:
                conn.execute("ALTER TABLE jobs ADD COLUMN topic_id TEXT")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS exercises (
                    id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    language TEXT NOT NULL,
                    exercise_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source_url TEXT NOT NULL,
                    source_title TEXT NOT NULL,
                    answers TEXT,
                    extracted_at TEXT NOT NULL,
                    PRIMARY KEY (job_id, id),
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS job_urls (
                    job_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    query TEXT NOT NULL,
                    PRIMARY KEY (job_id, url),
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vocabulary_exercises (
                    id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    track_id TEXT NOT NULL,
                    matched_word TEXT NOT NULL,
                    matched_translation TEXT NOT NULL,
                    language TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    validation_score REAL NOT NULL,
                    source_url TEXT NOT NULL,
                    extracted_at TEXT NOT NULL,
                    PRIMARY KEY (job_id, id),
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )
                """
            )
            conn.commit()

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        job_id = str(uuid.uuid4())
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, topic, lang, provider, max_pages, topic_id, status, phase,
                    progress_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    payload["topic"],
                    payload["lang"],
                    payload["provider"],
                    payload["max_pages"],
                    payload.get("topic_id"),
                    "queued",
                    "queued",
                    json.dumps({"message": "Waiting to start"}),
                    now,
                    now,
                ),
            )
            conn.commit()
        return self.get_job(job_id)

    def update_job(self, job_id: str, **fields: Any) -> None:
        fields["updated_at"] = _utc_now()
        columns = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [job_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE jobs SET {columns} WHERE id = ?", values)
            conn.commit()

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return self._row_to_job(row)

    def list_jobs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_job(row) for row in rows]

    def save_urls(self, job_id: str, urls: list[dict[str, str]]) -> None:
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO job_urls (job_id, url, title, query) VALUES (?, ?, ?, ?)",
                [(job_id, item["url"], item.get("title", ""), item.get("query", "")) for item in urls],
            )
            conn.commit()

    def list_urls(self, job_id: str) -> list[dict[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT url, title, query FROM job_urls WHERE job_id = ? ORDER BY url",
                (job_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_exercises(self, job_id: str, exercises: list[dict[str, Any]]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO exercises (
                    id, job_id, text, topic, language, exercise_type, confidence,
                    source_url, source_title, answers, extracted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item["id"],
                        job_id,
                        item["text"],
                        item["topic"],
                        item["language"],
                        item["exercise_type"],
                        item["confidence"],
                        item["source_url"],
                        item["source_title"],
                        item.get("answers"),
                        item["extracted_at"],
                    )
                    for item in exercises
                ],
            )
            conn.commit()

    def list_exercises(
        self,
        job_id: str,
        *,
        language: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM exercises WHERE job_id = ?"
        params: list[Any] = [job_id]
        if language and language != "all":
            query += " AND language = ?"
            params.append(language)
        query += " ORDER BY confidence DESC, rowid ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def count_exercises(self, job_id: str, language: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM exercises WHERE job_id = ?"
        params: list[Any] = [job_id]
        if language and language != "all":
            query += " AND language = ?"
            params.append(language)
        with self._connect() as conn:
            return int(conn.execute(query, params).fetchone()[0])

    def save_vocabulary_exercises(self, job_id: str, exercises: list[dict[str, Any]]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO vocabulary_exercises (
                    id, job_id, text, track_id, matched_word, matched_translation,
                    language, confidence, validation_score, source_url, extracted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item["id"],
                        job_id,
                        item["text"],
                        item["track_id"],
                        item["matched_word"],
                        item["matched_translation"],
                        item["language"],
                        item["confidence"],
                        item["validation_score"],
                        item["source_url"],
                        item["extracted_at"],
                    )
                    for item in exercises
                ],
            )
            conn.commit()

    def list_vocabulary_exercises(self, job_id: str, limit: int = 200) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM vocabulary_exercises
                WHERE job_id = ?
                ORDER BY validation_score DESC
                LIMIT ?
                """,
                (job_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _row_to_job(row: sqlite3.Row) -> dict[str, Any]:
        job = dict(row)
        job["progress"] = json.loads(job.pop("progress_json"))
        manifest_raw = job.pop("manifest_json")
        job["manifest"] = json.loads(manifest_raw) if manifest_raw else None
        return job


store = JobStore()
_active_lock = threading.Lock()
_active_jobs: set[str] = set()


def start_job(job_id: str, request: ScrapeRequest) -> None:
    with _active_lock:
        if job_id in _active_jobs:
            return
        _active_jobs.add(job_id)

    def worker() -> None:
        try:
            store.update_job(
                job_id,
                status="running",
                phase="searching",
                progress_json=json.dumps({"message": "Searching the web"}),
            )

            def on_progress(phase: str, payload: dict) -> None:
                store.update_job(
                    job_id,
                    phase=phase,
                    progress_json=json.dumps({"phase": phase, **payload}),
                )
                if phase == "urls_found" and "urls" in payload:
                    store.save_urls(job_id, payload["urls"])

            request.output_base = OUTPUT_DIR
            result = run_scrape(request, settings=Settings.from_env(), on_progress=on_progress)
            store.save_urls(job_id, result.search_urls)

            exercise_payload = [exercise.to_dict() for exercise in result.exercises]
            store.save_exercises(job_id, exercise_payload)

            store.update_job(
                job_id,
                status="completed",
                phase="completed",
                manifest_json=json.dumps(result.manifest.to_dict()),
                progress_json=json.dumps(
                    {
                        "phase": "completed",
                        "exercises_total": result.manifest.exercises_total,
                        "exercises_pl": result.manifest.exercises_pl,
                        "exercises_en": result.manifest.exercises_en,
                        "elapsed_seconds": result.elapsed_seconds,
                        "requests_count": result.requests_count,
                        "top_exercises": request.top_exercises,
                        "passed": len(result.validation.passed) if result.validation else None,
                        "rejected": len(result.validation.rejected) if result.validation else None,
                        "output_dir": str(result.output_dir),
                        "drive_sync": result.drive_sync,
                    }
                ),
                finished_at=_utc_now(),
            )
        except Exception as exc:
            store.update_job(
                job_id,
                status="failed",
                phase="failed",
                error=str(exc),
                progress_json=json.dumps({"phase": "failed", "error": str(exc)}),
                finished_at=_utc_now(),
            )
        finally:
            with _active_lock:
                _active_jobs.discard(job_id)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def start_dictionary_job(job_id: str, request) -> None:
    from exercise_scraper.dictionary.service import DictionaryRunRequest, run_dictionary_track

    with _active_lock:
        if job_id in _active_jobs:
            return
        _active_jobs.add(job_id)

    def worker() -> None:
        try:
            store.update_job(
                job_id,
                status="running",
                phase="searching",
                progress_json=json.dumps({"message": "Searching vocabulary sources", "job_kind": "dictionary"}),
            )

            def on_progress(phase: str, payload: dict) -> None:
                store.update_job(
                    job_id,
                    phase=phase,
                    progress_json=json.dumps({"phase": phase, "job_kind": "dictionary", **payload}),
                )
                if phase == "urls_found" and "urls" in payload:
                    store.save_urls(job_id, payload["urls"])

            request.output_base = OUTPUT_DIR
            result = run_dictionary_track(request, settings=Settings.from_env(), on_progress=on_progress)
            store.save_urls(job_id, result.search_urls)
            store.save_vocabulary_exercises(job_id, [item.to_dict() for item in result.exercises_top])

            store.update_job(
                job_id,
                status="completed",
                phase="completed",
                manifest_json=json.dumps(
                    {
                        "track_id": result.track_id,
                        "level": result.level,
                        "output_dir": str(result.output_dir),
                        "words_count": result.words_count,
                        "exercises_raw": result.exercises_raw,
                        "exercises_top": len(result.exercises_top),
                    }
                ),
                progress_json=json.dumps(
                    {
                        "phase": "completed",
                        "job_kind": "dictionary",
                        "track_id": result.track_id,
                        "words_count": result.words_count,
                        "exercises_total": len(result.exercises_top),
                        "output_dir": str(result.output_dir),
                        "elapsed_seconds": result.elapsed_seconds,
                    }
                ),
                finished_at=_utc_now(),
            )
        except Exception as exc:
            store.update_job(
                job_id,
                status="failed",
                phase="failed",
                error=str(exc),
                progress_json=json.dumps({"phase": "failed", "job_kind": "dictionary", "error": str(exc)}),
                finished_at=_utc_now(),
            )
        finally:
            with _active_lock:
                _active_jobs.discard(job_id)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
