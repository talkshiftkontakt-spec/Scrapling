from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

from sportsdata.config import UNDERSTAT_LEAGUES, PipelineConfig
from sportsdata.http import HttpClient
from sportsdata.matching.names import best_match


class UnderstatClient:
    BASE_URL = "https://understat.com"

    def __init__(self, config: PipelineConfig, http: HttpClient | None = None) -> None:
        self.config = config
        self.http = http or HttpClient(delay_seconds=config.request_delay_seconds)
        self._cache: dict[str, dict[str, Any]] = {}

    def _league_code(self, league_name: str) -> str | None:
        league_lower = league_name.lower()
        for pattern, code in UNDERSTAT_LEAGUES.items():
            if pattern.lower() == league_lower:
                return code
        return None

    def fetch_league_data(self, league_code: str, season: str | None = None) -> dict[str, Any]:
        season = season or self.config.understat_season
        cache_key = f"{league_code}:{season}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        url = f"{self.BASE_URL}/getLeagueData/{league_code}/{season}"
        try:
            data = self.http.get_json(
                url,
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{self.BASE_URL}/league/{league_code}/{season}",
                },
            )
        except Exception:
            return {}
        if not isinstance(data, dict):
            return {}
        self._cache[cache_key] = data
        return data

    def _team_from_data(self, data: dict[str, Any], team_name: str) -> dict[str, Any] | None:
        teams = data.get("teams", {})
        if not isinstance(teams, dict):
            return None
        titles = [str(team.get("title", "")) for team in teams.values()]
        matched_title = best_match(team_name, titles)
        if matched_title is None:
            team_lower = team_name.lower()
            for team in teams.values():
                title = str(team.get("title", ""))
                if title.lower() in team_lower or team_lower in title.lower():
                    return team
            return None
        for team in teams.values():
            if str(team.get("title", "")) == matched_title:
                return team
        return None

    def team_xg(self, league_name: str, team_name: str, season: str | None = None) -> dict[str, float | None]:
        season = season or self.config.understat_season
        code = self._league_code(league_name)
        if code is None:
            return {"xg": None, "xga": None}

        data = self.fetch_league_data(code, season=season)
        team = self._team_from_data(data, team_name)
        if team is None:
            return {"xg": None, "xga": None}
        history = team.get("history") or []
        if not history:
            return {"xg": None, "xga": None}
        xg_values = [float(item.get("xG", 0)) for item in history if item.get("xG") is not None]
        xga_values = [float(item.get("xGA", 0)) for item in history if item.get("xGA") is not None]
        if not xg_values:
            return {"xg": None, "xga": None}
        return {
            "xg": round(sum(xg_values) / len(xg_values), 4),
            "xga": round(sum(xga_values) / len(xga_values), 4) if xga_values else None,
        }

    def upcoming_from_league(self, league_name: str, season: str | None = None) -> list[dict[str, Any]]:
        season = season or self.config.understat_season
        code = self._league_code(league_name)
        if code is None:
            return []

        data = self.fetch_league_data(code, season=season)
        if not data:
            return []
        upcoming: list[dict[str, Any]] = []
        now = datetime.now(tz=UTC)
        for row in data.get("dates", []):
            if row.get("isResult"):
                continue
            dt_raw = row.get("datetime")
            if not dt_raw:
                continue
            start_time = datetime.strptime(dt_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            if start_time < now:
                continue
            upcoming.append(
                {
                    "datetime": start_time.isoformat(),
                    "home": row.get("h", {}).get("title"),
                    "away": row.get("a", {}).get("title"),
                    "forecast": row.get("forecast"),
                    "xG": row.get("xG"),
                }
            )
        return upcoming

    @staticmethod
    def parse_embedded_dates(html: str) -> list[dict[str, Any]]:
        match = re.search(r"datesData\s*=\s*JSON\.parse\('(.+?)'\)", html)
        if not match:
            return []
        payload = json.loads(match.group(1).encode().decode("unicode_escape"))
        return payload if isinstance(payload, list) else []
