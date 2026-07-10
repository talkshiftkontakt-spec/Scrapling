from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from sportsdata.models import Event, EventStatus, MatchResult, OddsSnapshot, PrematchStats, Sport


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

CREATE TABLE IF NOT EXISTS match_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport TEXT NOT NULL,
    league TEXT NOT NULL,
    home_participant TEXT NOT NULL,
    away_participant TEXT NOT NULL,
    start_time TEXT NOT NULL,
    home_score TEXT,
    away_score TEXT,
    source TEXT NOT NULL,
    stats_payload TEXT NOT NULL DEFAULT '{}',
    xg_payload TEXT NOT NULL DEFAULT '{}',
    odds_payload TEXT NOT NULL DEFAULT '{}',
    external_ids TEXT NOT NULL DEFAULT '{}',
    metadata TEXT NOT NULL DEFAULT '{}',
    dedupe_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_match_results_start_time ON match_results(start_time);
CREATE INDEX IF NOT EXISTS idx_match_results_sport ON match_results(sport);
CREATE INDEX IF NOT EXISTS idx_match_results_league ON match_results(league);

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

    def list_upcoming_events(
        self,
        sport: Sport | None = None,
        *,
        league: str | None = None,
        participant: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM events
            WHERE datetime(start_time) >= datetime('now')
              AND status IN ('scheduled', 'live', 'unknown')
        """
        params: list[Any] = []
        query, params = self._append_event_filters(
            query,
            params,
            sport=sport,
            league=league,
            participant=participant,
            from_date=from_date,
            to_date=to_date,
        )
        query += " ORDER BY start_time ASC"
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_event_dict(row) for row in rows]

    def count_upcoming_events(
        self,
        sport: Sport | None = None,
        *,
        league: str | None = None,
        participant: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        query = """
            SELECT COUNT(*) AS c FROM events
            WHERE datetime(start_time) >= datetime('now')
              AND status IN ('scheduled', 'live', 'unknown')
        """
        params: list[Any] = []
        query, params = self._append_event_filters(
            query,
            params,
            sport=sport,
            league=league,
            participant=participant,
            from_date=from_date,
            to_date=to_date,
        )
        with self.connection() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"])

    @staticmethod
    def _append_event_filters(
        query: str,
        params: list[Any],
        *,
        sport: Sport | None,
        league: str | None,
        participant: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[str, list[Any]]:
        if sport is not None:
            query += " AND sport = ?"
            params.append(sport.value)
        if league:
            query += " AND league LIKE ?"
            params.append(f"%{league}%")
        if participant:
            query += " AND (home_participant LIKE ? OR away_participant LIKE ?)"
            params.extend([f"%{participant}%", f"%{participant}%"])
        if from_date is not None:
            query += " AND datetime(start_time) >= datetime(?)"
            params.append(from_date.isoformat())
        if to_date is not None:
            query += " AND datetime(start_time) <= datetime(?)"
            params.append(to_date.isoformat())
        return query, params

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

    def upsert_match_result(self, result: MatchResult) -> int:
        now = datetime.now(tz=UTC).isoformat()
        payload = {
            "sport": result.sport.value,
            "league": result.league,
            "home_participant": result.home_participant,
            "away_participant": result.away_participant,
            "start_time": result.start_time.isoformat(),
            "home_score": result.home_score,
            "away_score": result.away_score,
            "source": result.source,
            "stats_payload": json.dumps(result.stats_payload),
            "xg_payload": json.dumps(result.xg_payload),
            "odds_payload": json.dumps(result.odds_payload),
            "external_ids": json.dumps(result.external_ids),
            "metadata": json.dumps(result.metadata),
            "dedupe_key": result.dedupe_key,
            "created_at": now,
            "updated_at": now,
        }
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO match_results (
                    sport, league, home_participant, away_participant, start_time,
                    home_score, away_score, source, stats_payload, xg_payload,
                    odds_payload, external_ids, metadata, dedupe_key, created_at, updated_at
                ) VALUES (
                    :sport, :league, :home_participant, :away_participant, :start_time,
                    :home_score, :away_score, :source, :stats_payload, :xg_payload,
                    :odds_payload, :external_ids, :metadata, :dedupe_key, :created_at, :updated_at
                )
                ON CONFLICT(dedupe_key) DO UPDATE SET
                    home_score = excluded.home_score,
                    away_score = excluded.away_score,
                    stats_payload = CASE
                        WHEN excluded.stats_payload IN ('{}', '{"groups": []}')
                        THEN match_results.stats_payload
                        ELSE excluded.stats_payload
                    END,
                    xg_payload = excluded.xg_payload,
                    odds_payload = excluded.odds_payload,
                    external_ids = excluded.external_ids,
                    metadata = excluded.metadata,
                    updated_at = excluded.updated_at
                """,
                payload,
            )
            row = conn.execute(
                "SELECT id FROM match_results WHERE dedupe_key = ?",
                (result.dedupe_key,),
            ).fetchone()
            return int(row["id"])

    def list_match_results(
        self,
        *,
        sport: Sport | None = None,
        league: str | None = None,
        participant: str | None = None,
        source: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        has_stats: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM match_results WHERE 1=1"
        params: list[Any] = []
        query, params = self._append_match_result_filters(
            query,
            params,
            sport=sport,
            league=league,
            participant=participant,
            source=source,
            from_date=from_date,
            to_date=to_date,
            has_stats=has_stats,
        )
        query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._decode_match_result_row(row) for row in rows]

    def count_match_results_filtered(
        self,
        *,
        sport: Sport | None = None,
        league: str | None = None,
        participant: str | None = None,
        source: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        has_stats: bool | None = None,
    ) -> int:
        query = "SELECT COUNT(*) AS c FROM match_results WHERE 1=1"
        params: list[Any] = []
        query, params = self._append_match_result_filters(
            query,
            params,
            sport=sport,
            league=league,
            participant=participant,
            source=source,
            from_date=from_date,
            to_date=to_date,
            has_stats=has_stats,
        )
        with self.connection() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"])

    @staticmethod
    def _append_match_result_filters(
        query: str,
        params: list[Any],
        *,
        sport: Sport | None,
        league: str | None,
        participant: str | None,
        source: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        has_stats: bool | None,
    ) -> tuple[str, list[Any]]:
        if sport is not None:
            query += " AND sport = ?"
            params.append(sport.value)
        if league:
            query += " AND league LIKE ?"
            params.append(f"%{league}%")
        if participant:
            query += " AND (home_participant LIKE ? OR away_participant LIKE ?)"
            params.extend([f"%{participant}%", f"%{participant}%"])
        if source:
            query += " AND source = ?"
            params.append(source)
        if from_date is not None:
            query += " AND datetime(start_time) >= datetime(?)"
            params.append(from_date.isoformat())
        if to_date is not None:
            query += " AND datetime(start_time) <= datetime(?)"
            params.append(to_date.isoformat())
        if has_stats is True:
            query += " AND stats_payload LIKE '%\"groups\":%' AND stats_payload NOT IN ('{}', '{\"groups\": []}')"
        elif has_stats is False:
            query += " AND (stats_payload = '{}' OR stats_payload NOT LIKE '%\"groups\":%')"
        return query, params

    @staticmethod
    def _decode_match_result_row(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        for key in ("stats_payload", "xg_payload", "odds_payload", "external_ids", "metadata"):
            item[key] = json.loads(item[key])
        return item

    def list_match_results_missing_stats(
        self,
        *,
        source: str = "flashscore",
        sport: Sport | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM match_results
            WHERE source = ?
              AND (
                stats_payload = '{}'
                OR stats_payload = '{"groups": []}'
                OR stats_payload NOT LIKE '%"groups":%'
              )
        """
        params: list[Any] = [source]
        if sport is not None:
            query += " AND sport = ?"
            params.append(sport.value)
        query += " ORDER BY start_time DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            for key in ("stats_payload", "xg_payload", "odds_payload", "external_ids", "metadata"):
                item[key] = json.loads(item[key])
            if self._stats_payload_has_groups(item.get("stats_payload", {})):
                continue
            results.append(item)
        return results

    @staticmethod
    def _stats_payload_has_groups(stats_payload: object) -> bool:
        if not isinstance(stats_payload, dict):
            return False
        groups = stats_payload.get("groups")
        return isinstance(groups, list) and len(groups) > 0

    def update_match_result_stats(self, result_id: int, stats_payload: dict[str, Any]) -> None:
        now = datetime.now(tz=UTC).isoformat()
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE match_results
                SET stats_payload = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(stats_payload), now, result_id),
            )

    def count_match_results_with_stats(
        self,
        *,
        sport: Sport | None = None,
        source: str | None = None,
    ) -> int:
        query = """
            SELECT COUNT(*) AS c FROM match_results
            WHERE stats_payload LIKE '%"groups":%'
              AND stats_payload NOT IN ('{}', '{"groups": []}')
        """
        params: list[Any] = []
        if sport is not None:
            query += " AND sport = ?"
            params.append(sport.value)
        if source is not None:
            query += " AND source = ?"
            params.append(source)
        with self.connection() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"])

    def count_match_results(self, sport: Sport | None = None) -> int:
        query = "SELECT COUNT(*) AS c FROM match_results"
        params: list[Any] = []
        if sport is not None:
            query += " WHERE sport = ?"
            params.append(sport.value)
        with self.connection() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"])

    def get_match_result(self, result_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM match_results WHERE id = ?", (result_id,)).fetchone()
        if row is None:
            return None
        return self._decode_match_result_row(row)

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
