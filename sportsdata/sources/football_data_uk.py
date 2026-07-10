from __future__ import annotations

import csv
import io
from typing import Any

from sportsdata.config import FOOTBALL_DATA_LEAGUE_FILES, FOOTBALL_DATA_SEASONS, FOOTBALL_DATA_URLS, PipelineConfig
from sportsdata.http import HttpClient


class FootballDataUkClient:
    def __init__(self, config: PipelineConfig, http: HttpClient | None = None) -> None:
        self.config = config
        self.http = http or HttpClient(delay_seconds=config.request_delay_seconds)

    def download_league_csv(self, league_code: str, season: str | None = None) -> str:
        if season is None:
            url = FOOTBALL_DATA_URLS[league_code]
        else:
            file_code = FOOTBALL_DATA_LEAGUE_FILES[league_code]
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{file_code}.csv"
        return self.http.get_text(url)

    def parse_csv_rows(self, csv_text: str, league_code: str, season: str | None = None) -> list[dict[str, Any]]:
        reader = csv.DictReader(io.StringIO(csv_text))
        rows: list[dict[str, Any]] = []
        for row in reader:
            odds_payload = {
                key: row.get(key)
                for key in row.keys()
                if key.startswith(("B365", "BW", "BF", "PS", "WH", "1XB", "Max", "Avg", "BFE"))
            }
            stats_payload = {
                key: row.get(key)
                for key in (
                    "HS",
                    "AS",
                    "HST",
                    "AST",
                    "HF",
                    "AF",
                    "HC",
                    "AC",
                    "HY",
                    "AY",
                    "HR",
                    "AR",
                )
            }
            rows.append(
                {
                    "source": "football-data.co.uk",
                    "league_code": league_code,
                    "season": season,
                    "match_date": row.get("Date"),
                    "home_team": row.get("HomeTeam"),
                    "away_team": row.get("AwayTeam"),
                    "home_goals": _safe_int(row.get("FTHG")),
                    "away_goals": _safe_int(row.get("FTAG")),
                    "result": row.get("FTR"),
                    "odds_payload": odds_payload,
                    "stats_payload": stats_payload,
                }
            )
        return rows

    def import_all(self, seasons: tuple[str, ...] | None = None) -> list[dict[str, Any]]:
        imported: list[dict[str, Any]] = []
        season_list = seasons or FOOTBALL_DATA_SEASONS
        for season in season_list:
            for league_code in FOOTBALL_DATA_LEAGUE_FILES:
                try:
                    csv_text = self.download_league_csv(league_code, season=season)
                    imported.extend(self.parse_csv_rows(csv_text, league_code, season=season))
                except Exception:
                    continue
        return imported


def _safe_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None
