from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

Language = Literal["pl", "en", "unknown"]
ExerciseType = Literal["fill_blank", "multiple_choice", "rewrite", "unknown"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def content_hash(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str = ""
    query: str = ""


@dataclass
class Exercise:
    text: str
    topic: str
    source_url: str
    source_title: str = ""
    answers: str | None = None
    exercise_type: ExerciseType = "unknown"
    language: Language = "unknown"
    confidence: float = 0.0
    validation_score: float = 0.0
    validation_reasons: list[str] = field(default_factory=list)
    id: str = ""
    extracted_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if isinstance(self.extracted_at, str):
            self.extracted_at = datetime.fromisoformat(self.extracted_at)
        if not self.id:
            self.id = content_hash(self.text)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["extracted_at"] = self.extracted_at.isoformat()
        return data


@dataclass
class SourcePage:
    url: str
    title: str
    exercise_count: int
    language: Language
    status: int | None = None
    error: str | None = None


@dataclass
class CrawlManifest:
    query: str
    lang_mode: str
    output_dir: str
    started_at: datetime = field(default_factory=_utc_now)
    finished_at: datetime | None = None
    urls_found: int = 0
    urls_scraped: int = 0
    urls_failed: int = 0
    exercises_total: int = 0
    exercises_pl: int = 0
    exercises_en: int = 0
    exercises_unknown: int = 0
    sources: list[dict[str, Any]] = field(default_factory=list)
    queries_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        return data
