from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool


class SummaryResponse(BaseModel):
    timestamp: str
    db_path: str
    upcoming_events: int
    match_results_total: int
    match_results_football: int
    match_results_tennis: int
    tennis_with_stats: int
    football_with_stats: int
    failed_jobs: list[dict[str, Any]] = Field(default_factory=list)
