from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from sportsdata.models import Event, EventStatus, OddsSnapshot, PrematchStats, Sport


SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport TEXT NOT NULL,
    league TEXT NOT NULL,
    home_participant TEXT NOT NULL,
    away_participant TEXT NOT NULL,
    start_time TEXT NOT NULL,
    status TEXT NOT NULL,
    home_score TEXT,
    away_score TEXT,
    external_ids TEXT NOT NULL DEFAULT '{}',
    metadata TEXT NOT NULL DEFAULT '{}',
    dedupe_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_stats_prematch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    scraped_at TEXT NOT NULL,
    home_form_last5 TEXT NOT NULL DEFAULT '[]',
    away_form_last5 TEXT NOT NULL DEFAULT '[]',
    h2h TEXT NOT NULL DEFAULT '[]',
    home_season_xg REAL,
    away_season_xg REAL,
    home_season_xga REAL,
    away_season_xga REAL,
    home_ranking INTEGER,
    away_ranking INTEGER,
    surface TEXT,
    surface_stats TEXT NOT NULL DEFAULT '{}',
    injuries TEXT NOT NULL DEFAULT '{}',
    raw_payload TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(event_id) REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    bookmaker TEXT NOT NULL,
    market TEXT NOT NULL,
    selection TEXT NOT NULL,
    odds_decimal REAL NOT NULL,
    scraped_at TEXT NOT NULL,
    is_opening INTEGER NOT NULL DEFAULT 0,
    is_closing INTEGER NOT NULL DEFAULT 0,
    handicap REAL,
    raw_payload TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(event_id) REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS job_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    success INTEGER NOT NULL,
    message TEXT NOT NULL,
    counts TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS historical_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    league_code TEXT NOT NULL,
    match_date TEXT,
    home_team TEXT,
    away_team TEXT,
    home_goals INTEGER,
    away_goals INTEGER,
    result TEXT,
    odds_payload TEXT NOT NULL DEFAULT '{}',
    stats_payload TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);
CREATE INDEX IF NOT EXISTS idx_events_sport ON events(sport);
CREATE INDEX IF NOT EXISTS idx_odds_event_id ON odds_snapshots(event_id);
CREATE INDEX IF NOT EXISTS idx_stats_event_id ON event_stats_prematch(event_id);
"""


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def upsert_event(self, event: Event) -> int:
        now = datetime.now(tz=UTC).isoformat()
        payload = {
            "sport": event.sport.value,
            "league": event.league,
            "home_participant": event.home_participant,
            "away_participant": event.away_participant,
            "start_time": event.start_time.isoformat(),
            "status": event.status.value,
            "home_score": event.home_score,
            "away_score": event.away_score,
            "external_ids": json.dumps(event.external_ids),
            "metadata": json.dumps(event.metadata),
            "dedupe_key": event.dedupe_key,
            "created_at": now,
            "updated_at": now,
        }
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO events (
                    sport, league, home_participant, away_participant, start_time, status,
                    home_score, away_score, external_ids, metadata, dedupe_key, created_at, updated_at
                ) VALUES (
                    :sport, :league, :home_participant, :away_participant, :start_time, :status,
                    :home_score, :away_score, :external_ids, :metadata, :dedupe_key, :created_at, :updated_at
                )
                ON CONFLICT(dedupe_key) DO UPDATE SET
                    status = excluded.status,
                    home_score = excluded.home_score,
                    away_score = excluded.away_score,
                    external_ids = excluded.external_ids,
                    metadata = excluded.metadata,
                    updated_at = excluded.updated_at
                """,
                payload,
            )
            row = conn.execute(
                "SELECT id FROM events WHERE dedupe_key = ?",
                (event.dedupe_key,),
            ).fetchone()
            return int(row["id"])

    def merge_external_id(self, event_id: int, key: str, value: str) -> None:
        with self.connection() as conn:
            row = conn.execute("SELECT external_ids FROM events WHERE id = ?", (event_id,)).fetchone()
            if row is None:
                return
            external_ids = json.loads(row["external_ids"])
            external_ids[key] = value
            conn.execute(
                "UPDATE events SET external_ids = ?, updated_at = ? WHERE id = ?",
                (json.dumps(external_ids), datetime.now(tz=UTC).isoformat(), event_id),
            )

    def reconcile_past_events(self, *, grace_hours: int = 3) -> int:
        cutoff = (datetime.now(tz=UTC) - timedelta(hours=grace_hours)).isoformat()
        now = datetime.now(tz=UTC).isoformat()
        with self.connection() as conn:
            cursor = conn.execute(
                """
                UPDATE events
                SET status = 'finished', updated_at = ?
                WHERE datetime(start_time) < datetime(?)
                  AND status IN ('scheduled', 'unknown')
                """,
                (now, cutoff),
            )
            return cursor.rowcount

    def list_upcoming_events(self, sport: Sport | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM events
            WHERE datetime(start_time) >= datetime('now')
              AND status IN ('scheduled', 'live', 'unknown')
        """
        params: list[Any] = []
        if sport is not None:
            query += " AND sport = ?"
            params.append(sport.value)
        query += " ORDER BY start_time ASC"
        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_event_dict(row) for row in rows]

    def get_event(self, event_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        return self._row_to_event_dict(row) if row else None

    def save_prematch_stats(self, stats: PrematchStats) -> int:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO event_stats_prematch (
                    event_id, scraped_at, home_form_last5, away_form_last5, h2h,
                    home_season_xg, away_season_xg, home_season_xga, away_season_xga,
                    home_ranking, away_ranking, surface, surface_stats, injuries, raw_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    stats.event_id,
                    stats.scraped_at.isoformat(),
                    json.dumps(stats.home_form_last5),
                    json.dumps(stats.away_form_last5),
                    json.dumps(stats.h2h),
                    stats.home_season_xg,
                    stats.away_season_xg,
                    stats.home_season_xga,
                    stats.away_season_xga,
                    stats.home_ranking,
                    stats.away_ranking,
                    stats.surface,
                    json.dumps(stats.surface_stats),
                    json.dumps(stats.injuries),
                    json.dumps(stats.raw_payload),
                ),
            )
            row = conn.execute("SELECT last_insert_rowid() AS id").fetchone()
            return int(row["id"])

    def latest_prematch_stats(self, event_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM event_stats_prematch
                WHERE event_id = ?
                ORDER BY scraped_at DESC
                LIMIT 1
                """,
                (event_id,),
            ).fetchone()
        if row is None:
            return None
        data = dict(row)
        for key in ("home_form_last5", "away_form_last5", "h2h", "surface_stats", "injuries", "raw_payload"):
            data[key] = json.loads(data[key])
        return data

    def save_odds_snapshot(self, snapshot: OddsSnapshot) -> int:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO odds_snapshots (
                    event_id, bookmaker, market, selection, odds_decimal, scraped_at,
                    is_opening, is_closing, handicap, raw_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.event_id,
                    snapshot.bookmaker,
                    snapshot.market,
                    snapshot.selection,
                    snapshot.odds_decimal,
                    snapshot.scraped_at.isoformat(),
                    int(snapshot.is_opening),
                    int(snapshot.is_closing),
                    snapshot.handicap,
                    json.dumps(snapshot.raw_payload),
                ),
            )
            row = conn.execute("SELECT last_insert_rowid() AS id").fetchone()
            return int(row["id"])

    def list_odds_for_event(self, event_id: int) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM odds_snapshots
                WHERE event_id = ?
                ORDER BY scraped_at DESC, bookmaker ASC, market ASC
                """,
                (event_id,),
            ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["raw_payload"] = json.loads(item["raw_payload"])
            results.append(item)
        return results

    def record_job_run(
        self,
        job_name: str,
        started_at: datetime,
        finished_at: datetime,
        success: bool,
        message: str,
        counts: dict[str, int],
    ) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO job_runs (job_name, started_at, finished_at, success, message, counts)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    job_name,
                    started_at.isoformat(),
                    finished_at.isoformat(),
                    int(success),
                    message,
                    json.dumps(counts),
                ),
            )

    def latest_failed_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM job_runs
                WHERE success = 0
                ORDER BY finished_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_historical_match(self, row: dict[str, Any]) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO historical_matches (
                    source, league_code, match_date, home_team, away_team,
                    home_goals, away_goals, result, odds_payload, stats_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["source"],
                    row["league_code"],
                    row.get("match_date"),
                    row.get("home_team"),
                    row.get("away_team"),
                    row.get("home_goals"),
                    row.get("away_goals"),
                    row.get("result"),
                    json.dumps(row.get("odds_payload", {})),
                    json.dumps(row.get("stats_payload", {})),
                ),
            )

    @staticmethod
    def _row_to_event_dict(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["external_ids"] = json.loads(data["external_ids"])
        data["metadata"] = json.loads(data["metadata"])
        return data

    def event_from_row(self, row: dict[str, Any]) -> Event:
        return Event(
            id=row["id"],
            sport=Sport(row["sport"]),
            league=row["league"],
            home_participant=row["home_participant"],
            away_participant=row["away_participant"],
            start_time=datetime.fromisoformat(row["start_time"]),
            status=EventStatus(row["status"]),
            home_score=row.get("home_score"),
            away_score=row.get("away_score"),
            external_ids=row.get("external_ids", {}),
            metadata=row.get("metadata", {}),
        )
