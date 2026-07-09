from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Sport(str, Enum):
    FOOTBALL = "football"
    TENNIS = "tennis"


class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class Event:
    sport: Sport
    league: str
    home_participant: str
    away_participant: str
    start_time: datetime
    status: EventStatus = EventStatus.SCHEDULED
    home_score: str | None = None
    away_score: str | None = None
    external_ids: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: int | None = None

    @property
    def dedupe_key(self) -> str:
        return "|".join(
            [
                self.sport.value,
                self.league.lower().strip(),
                self.home_participant.lower().strip(),
                self.away_participant.lower().strip(),
                self.start_time.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["sport"] = self.sport.value
        data["status"] = self.status.value
        data["start_time"] = self.start_time.isoformat()
        return data


@dataclass
class PrematchStats:
    event_id: int
    scraped_at: datetime
    home_form_last5: list[dict[str, Any]] = field(default_factory=list)
    away_form_last5: list[dict[str, Any]] = field(default_factory=list)
    h2h: list[dict[str, Any]] = field(default_factory=list)
    home_season_xg: float | None = None
    away_season_xg: float | None = None
    home_season_xga: float | None = None
    away_season_xga: float | None = None
    home_ranking: int | None = None
    away_ranking: int | None = None
    surface: str | None = None
    surface_stats: dict[str, Any] = field(default_factory=dict)
    injuries: dict[str, Any] = field(default_factory=dict)
    raw_payload: dict[str, Any] = field(default_factory=dict)
    id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scraped_at"] = self.scraped_at.isoformat()
        return data


@dataclass
class OddsSnapshot:
    event_id: int
    bookmaker: str
    market: str
    selection: str
    odds_decimal: float
    scraped_at: datetime
    is_opening: bool = False
    is_closing: bool = False
    handicap: float | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)
    id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scraped_at"] = self.scraped_at.isoformat()
        return data


@dataclass
class JobRunResult:
    job_name: str
    started_at: datetime
    finished_at: datetime
    success: bool
    message: str
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["finished_at"] = self.finished_at.isoformat()
        return data
