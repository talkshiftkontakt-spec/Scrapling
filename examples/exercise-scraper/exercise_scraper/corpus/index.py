from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from exercise_scraper.models import content_hash

DEFAULT_DB = Path("output") / "grammar-corpus" / "manifests" / "corpus_index.db"


class CorpusIndex:
    """Cross-run deduplication index for grammar exercises and vocabulary."""

    def __init__(self, db_path: Path = DEFAULT_DB) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS corpus_entries (
                    text_hash TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    topic_key TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    validation_score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (kind, topic_key, text_hash)
                )
                """
            )
            conn.commit()

    def has_seen(self, *, kind: str, topic_key: str, text: str) -> bool:
        digest = content_hash(text)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM corpus_entries WHERE kind = ? AND topic_key = ? AND text_hash = ?",
                (kind, topic_key, digest),
            ).fetchone()
        return row is not None

    def register(
        self,
        *,
        kind: str,
        topic_key: str,
        text: str,
        source_url: str,
        validation_score: float,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        digest = content_hash(text)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO corpus_entries
                (text_hash, kind, topic_key, source_url, validation_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (digest, kind, topic_key, source_url, validation_score, now),
            )
            conn.commit()

    def filter_unseen(
        self,
        items: list,
        *,
        kind: str,
        topic_key: str,
        text_attr: str = "text",
    ) -> list:
        unseen: list = []
        for item in items:
            text = getattr(item, text_attr)
            if not self.has_seen(kind=kind, topic_key=topic_key, text=text):
                unseen.append(item)
        return unseen

    def count(self, *, kind: str | None = None, topic_key: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM corpus_entries WHERE 1=1"
        params: list[str] = []
        if kind:
            query += " AND kind = ?"
            params.append(kind)
        if topic_key:
            query += " AND topic_key = ?"
            params.append(topic_key)
        with self._connect() as conn:
            return int(conn.execute(query, params).fetchone()[0])
