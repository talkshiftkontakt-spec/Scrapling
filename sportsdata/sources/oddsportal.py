from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

from sportsdata.config import PipelineConfig
from sportsdata.http import HttpClient
from sportsdata.models import OddsSnapshot


class OddsPortalClient:
    BASE_URL = "https://www.oddsportal.com"

    def __init__(self, config: PipelineConfig, http: HttpClient | None = None) -> None:
        self.config = config
        self.http = http or HttpClient(delay_seconds=config.request_delay_seconds)
        self._bookmakers: dict[str, dict[str, Any]] | None = None

    def _headers(self, *, ajax: bool = False) -> dict[str, str]:
        headers = {"Referer": f"{self.BASE_URL}/"}
        if ajax:
            headers["x-requested-with"] = "XMLHttpRequest"
            headers["Accept"] = "application/json, text/plain, */*"
        return headers

    def fetch_bookmakers(self) -> dict[str, dict[str, Any]]:
        if self._bookmakers is not None:
            return self._bookmakers

        page = self.http.get_text(f"{self.BASE_URL}/matches/football/", headers=self._headers())
        match = re.search(r"/res/x/bookies-\d+-\d+\.js", page)
        if not match:
            self._bookmakers = {}
            return self._bookmakers

        bookies_url = urljoin(self.BASE_URL, match.group(0))
        script = self.http.get_text(bookies_url, headers=self._headers())
        payload_match = re.search(r"bookmakersData=(\{.*?\});", script)
        if not payload_match:
            self._bookmakers = {}
            return self._bookmakers

        self._bookmakers = json.loads(payload_match.group(1))
        return self._bookmakers

    def betclic_bookmaker_ids(self) -> list[str]:
        bookmakers = self.fetch_bookmakers()
        ids: list[str] = []
        for bookmaker_id, meta in bookmakers.items():
            web_name = str(meta.get("WebName", ""))
            if any(target.lower() in web_name.lower() for target in self.config.target_bookmakers):
                ids.append(str(bookmaker_id))
        return ids

    def list_h2h_links(self, league_url: str) -> list[str]:
        try:
            html = self.http.get_text(league_url, headers=self._headers())
        except Exception:
            return []
        links = sorted(set(re.findall(r'(/football/h2h/[^"\']+)', html)))
        return [urljoin(self.BASE_URL, link) for link in links]

    def parse_event_data(self, html: str) -> dict[str, Any] | None:
        marker = '"eventData":'
        idx = html.find(marker)
        if idx < 0:
            return None
        sub = html[idx + len(marker) :]
        depth = 0
        for index, char in enumerate(sub):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(sub[: index + 1])
                    except json.JSONDecodeError:
                        return None
        return None

    def fetch_event_data(self, h2h_url: str) -> dict[str, Any] | None:
        try:
            html = self.http.get_text(h2h_url, headers=self._headers())
        except Exception:
            return None
        return self.parse_event_data(html)

    def fetch_match_feed_payload(self, event_data: dict[str, Any]) -> str | None:
        event_id = event_data.get("id")
        version_id = event_data.get("versionId", 1)
        sport_id = event_data.get("sportId", 1)
        xhash = event_data.get("xhash")
        if not event_id or not xhash:
            return None
        feed_url = (
            f"https://fb.oddsportal.com/feed/match-event/"
            f"{version_id}-{sport_id}-{event_id}-1-2-{xhash}"
        )
        try:
            return self.http.get_text(feed_url, headers=self._headers(ajax=True))
        except Exception:
            return None

    def snapshots_from_event_data(self, event_id: int, event_data: dict[str, Any]) -> list[OddsSnapshot]:
        now = datetime.now(tz=UTC)
        snapshots: list[OddsSnapshot] = []
        home = str(event_data.get("home", "home"))
        away = str(event_data.get("away", "away"))
        encode_id = str(event_data.get("id", ""))

        feed_payload = self.fetch_match_feed_payload(event_data)
        if feed_payload:
            snapshots.append(
                OddsSnapshot(
                    event_id=event_id,
                    bookmaker="oddsportal_raw",
                    market="feed_payload",
                    selection="encrypted",
                    odds_decimal=0.0,
                    scraped_at=now,
                    raw_payload={"payload": feed_payload[:5000], "encode_id": encode_id},
                )
            )

        community = (
            event_data.get("predictionData", {})
            .get("communityData", {})
            .get("count", {})
        )
        for key, count in community.items():
            snapshots.append(
                OddsSnapshot(
                    event_id=event_id,
                    bookmaker="oddsportal_community",
                    market="prediction_count",
                    selection=key,
                    odds_decimal=float(count),
                    scraped_at=now,
                    raw_payload={"encode_id": encode_id},
                )
            )

        snapshots.extend(
            self._forecast_snapshots(
                event_id=event_id,
                home=home,
                away=away,
                forecast=event_data.get("predictionData", {}).get("forecast"),
                scraped_at=now,
                source="oddsportal_meta",
            )
        )
        return snapshots

    @staticmethod
    def _forecast_snapshots(
        *,
        event_id: int,
        home: str,
        away: str,
        forecast: dict[str, Any] | None,
        scraped_at: datetime,
        source: str,
    ) -> list[OddsSnapshot]:
        if not forecast:
            return []
        mapping = {
            "home": ("1x2", home, forecast.get("w") or forecast.get("home")),
            "draw": ("1x2", "draw", forecast.get("d") or forecast.get("draw")),
            "away": ("1x2", away, forecast.get("l") or forecast.get("away")),
        }
        snapshots: list[OddsSnapshot] = []
        for _, (market, selection, probability) in mapping.items():
            if probability in (None, "", 0, "0"):
                continue
            try:
                prob = float(probability)
            except (TypeError, ValueError):
                continue
            if prob <= 0:
                continue
            snapshots.append(
                OddsSnapshot(
                    event_id=event_id,
                    bookmaker=source,
                    market=market,
                    selection=selection,
                    odds_decimal=round(1 / prob, 3),
                    scraped_at=scraped_at,
                    raw_payload={"probability": prob},
                )
            )
        return snapshots

    def discover_h2h_events(self, *, max_links: int = 20) -> list[dict[str, Any]]:
        discovered: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        for league_url in self.config.oddsportal_league_urls.values():
            for h2h_url in self.list_h2h_links(league_url):
                if h2h_url in seen_urls:
                    continue
                seen_urls.add(h2h_url)
                if len(discovered) >= max_links:
                    return discovered
                event_data = self.fetch_event_data(h2h_url)
                if event_data is None:
                    continue
                discovered.append(
                    {
                        "h2h_url": h2h_url,
                        "event_data": event_data,
                    }
                )
        return discovered
