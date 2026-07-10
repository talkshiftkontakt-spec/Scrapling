from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

from sportsdata.config import PipelineConfig
from sportsdata.http import HttpClient


class SofaScoreClient:
    """Best-effort SofaScore client. Falls back gracefully when API is blocked."""

    BASE_WWW = "https://www.sofascore.com"
    BASE_API = "https://api.sofascore.com/api/v1"

    def __init__(self, config: PipelineConfig, http: HttpClient | None = None) -> None:
        self.config = config
        self.http = http or HttpClient(delay_seconds=config.request_delay_seconds)

    def _api_headers(self) -> dict[str, str]:
        return {
            "Referer": f"{self.BASE_WWW}/",
            "Origin": self.BASE_WWW,
            "Accept": "application/json",
        }

    def _safe_get_json(self, url: str) -> dict[str, Any] | None:
        try:
            return self.http.get_json(url, headers=self._api_headers())
        except Exception:
            return None

    def search(self, query: str) -> dict[str, Any] | None:
        return self._safe_get_json(f"{self.BASE_API}/search/all?q={query}")

    def scheduled_football(self, day: datetime) -> dict[str, Any] | None:
        day_str = day.strftime("%Y-%m-%d")
        return self._safe_get_json(f"{self.BASE_API}/sport/football/scheduled-events/{day_str}")

    def scheduled_tennis_tournaments(self, day: datetime, page: int = 0) -> dict[str, Any] | None:
        day_str = day.strftime("%Y-%m-%d")
        return self._safe_get_json(
            f"{self.BASE_API}/sport/tennis/scheduled-tournaments/{day_str}/page/{page}"
        )

    def event_h2h(self, event_id: int) -> dict[str, Any] | None:
        return self._safe_get_json(f"{self.BASE_API}/event/{event_id}/h2h")

    def event_team_streaks(self, event_id: int) -> dict[str, Any] | None:
        return self._safe_get_json(f"{self.BASE_API}/event/{event_id}/team-streaks")

    def parse_match_page(self, url: str) -> dict[str, Any]:
        html = self.http.get_text(url, headers={"Referer": self.BASE_WWW})
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
        if not match:
            return {}
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return {}

    def enrich_event(self, home: str, away: str, sport: str = "football") -> dict[str, Any]:
        payload: dict[str, Any] = {"home": home, "away": away, "sport": sport, "source": "sofascore"}
        search = self.search(home)
        if not search:
            payload["available"] = False
            return payload

        payload["available"] = True
        payload["search"] = search

        events = []
        for key in ("events", "teams", "players", "uniqueTournaments"):
            value = search.get(key)
            if isinstance(value, list):
                events.extend(value)
        payload["candidates"] = events[:10]
        return payload
