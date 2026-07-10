from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from sportsdata.config import PipelineConfig
from sportsdata.http import HttpClient, extract_flashscore_fsign
from sportsdata.models import Event, EventStatus, Sport


FLASHSCORE_STATUS_MAP = {
    "1": EventStatus.SCHEDULED,
    "2": EventStatus.LIVE,
    "3": EventStatus.FINISHED,
    "4": EventStatus.CANCELLED,
    "5": EventStatus.UNKNOWN,
}


class FlashscoreClient:
  BASE_FEED = "https://global.flashscore.ninja/2/x/feed"
  BASE_SITE = "https://www.flashscore.com"
  TENNIS_TOUR_URL_PATTERN = re.compile(
      r'href="(/tennis/(?:atp-singles|wta-singles|challenger-men-singles|challenger-women-singles)/[^"]+/)"',
      re.IGNORECASE,
  )
  TENNIS_TOURNAMENT_SUBPAGES = frozenset({"draw", "results", "fixtures", "news", "odds", "archive"})

  def __init__(self, config: PipelineConfig, http: HttpClient | None = None) -> None:
      self.config = config
      self.http = http or HttpClient(delay_seconds=config.request_delay_seconds)
      self._fsign = config.flashscore_fsign
      self._h2h_cache: dict[str, list[dict[str, Any]]] = {}
      self._statistics_cache: dict[str, dict[str, Any]] = {}

  @property
  def fsign(self) -> str:
      if self._fsign:
          return self._fsign
      html = self.http.get_text(self.BASE_SITE, headers={"Referer": self.BASE_SITE})
      self._fsign = extract_flashscore_fsign(html)
      return self._fsign

  def _headers(self) -> dict[str, str]:
      return {"x-fsign": self.fsign, "Referer": f"{self.BASE_SITE}/"}

  def fetch_feed(self, path: str) -> str:
      url = f"{self.BASE_FEED}/{path}"
      return self.http.get_text(url, headers=self._headers())

  @staticmethod
  def parse_feed(text: str) -> list[dict[str, str]]:
      blocks: list[dict[str, str]] = []
      current_tournament = ""
      for raw_block in text.split("¬~"):
          fields: dict[str, str] = {}
          for part in raw_block.split("¬"):
              if "÷" not in part:
                  continue
              key, value = part.split("÷", 1)
              if key.startswith("~") and key[1:]:
                  key = key[1:]
              fields[key] = value
          if "ZA" in fields:
              current_tournament = fields["ZA"]
          if "AA" in fields:
              fields.setdefault("ZA", current_tournament)
              blocks.append(fields)
      return blocks

  @staticmethod
  def _parse_start_time(fields: dict[str, str]) -> datetime | None:
      for key in ("AD", "AO"):
          raw = fields.get(key)
          if raw and raw.isdigit():
              return datetime.fromtimestamp(int(raw), tz=UTC)
      return None

  @staticmethod
  def parse_embedded_feed(html: str) -> str | None:
      for feed_key in ("results", "fixtures"):
          match = re.search(
              rf"initialFeeds\['{feed_key}'\]\s*=\s*\{{\s*data:\s*`([^`]+)`",
              html,
          )
          if match:
              return match.group(1)
      match = re.search(r"data:\s*`(SA÷1[^`]+)`", html)
      return match.group(1) if match else None

  @staticmethod
  def parse_embedded_feeds(html: str) -> list[str]:
      feeds: list[str] = []
      seen: set[str] = set()
      for feed_key in ("results", "fixtures"):
          match = re.search(
              rf"initialFeeds\['{feed_key}'\]\s*=\s*\{{\s*data:\s*`([^`]+)`",
              html,
          )
          if match:
              feed_text = match.group(1)
              if feed_text not in seen:
                  seen.add(feed_text)
                  feeds.append(feed_text)
      fallback = re.search(r"data:\s*`(SA÷1[^`]+)`", html)
      if fallback and fallback.group(1) not in seen:
          feeds.append(fallback.group(1))
      return feeds

  @staticmethod
  def _matches_patterns(league: str, patterns: tuple[str, ...], *, exact: bool = False) -> bool:
      league_lower = league.lower()
      if exact:
          return any(pattern.lower() == league_lower for pattern in patterns)
      return any(pattern.lower() in league_lower for pattern in patterns)

  def _event_from_fields(
      self,
      fields: dict[str, str],
      sport: Sport,
      *,
      skip_pattern_check: bool = False,
  ) -> Event | None:
      start_time = self._parse_start_time(fields)
      if start_time is None:
          return None

      league = fields.get("ZA", "Unknown")
      patterns = (
          self.config.football_league_patterns
          if sport is Sport.FOOTBALL
          else self.config.tennis_tour_patterns
      )
      if not skip_pattern_check and not self._matches_patterns(
          league,
          patterns,
          exact=sport is Sport.FOOTBALL,
      ):
          return None

      status = FLASHSCORE_STATUS_MAP.get(fields.get("AB", ""), EventStatus.UNKNOWN)
      home = fields.get("AE") or fields.get("CX") or ""
      away = fields.get("AF") or ""
      if not home or not away:
          return None

      metadata: dict[str, Any] = {
          "surface": fields.get("KD") or fields.get("KE"),
          "round": fields.get("ER"),
          "country": fields.get("ZY"),
          "home_player_id": fields.get("JA"),
          "away_player_id": fields.get("JB"),
      }
      return Event(
          sport=sport,
          league=league,
          home_participant=home,
          away_participant=away,
          start_time=start_time,
          status=status,
          home_score=fields.get("AG"),
          away_score=fields.get("AH"),
          external_ids={"flashscore": fields["AA"]},
          metadata=metadata,
      )

  def _is_upcoming_event(self, event: Event, *, now: datetime, include_live: bool) -> bool:
      if event.status is EventStatus.FINISHED or event.status is EventStatus.CANCELLED:
          return False
      if event.status is EventStatus.LIVE:
          return include_live
      return event.start_time >= now - timedelta(minutes=10)

  def discover_tennis_tournament_pages(self) -> list[tuple[str, str]]:
      html = self.http.get_text(f"{self.BASE_SITE}/tennis/", headers={"Referer": self.BASE_SITE})
      match = re.search(r"leftMenuTopLeagues\s*=\s*(\{.*?\});", html)
      if not match:
          return []

      tournaments: list[tuple[str, str]] = []
      try:
          data = json.loads(match.group(1))
      except json.JSONDecodeError:
          return []

      for item in data.values():
          title = str(item.get("title", "")).strip()
          url = str(item.get("url", "")).strip()
          if not title or not url:
              continue
          tournaments.append((title, f"{self.BASE_SITE}{url}"))
      return tournaments

  def _is_relevant_tennis_league(self, league: str) -> bool:
      return self._is_relevant_tennis_league_with(
          league,
          self.config.tennis_exclude_patterns,
          self.config.tennis_tour_patterns,
      )

  @staticmethod
  def _is_relevant_tennis_league_with(
      league: str,
      exclude_patterns: tuple[str, ...],
      include_patterns: tuple[str, ...],
  ) -> bool:
      league_upper = league.upper()
      if any(pattern.upper() in league_upper for pattern in exclude_patterns):
          return False
      if "SINGLES" not in league_upper:
          return False
      return any(pattern.upper() in league_upper for pattern in include_patterns)

  def _finished_event_from_fields(
      self,
      fields: dict[str, str],
      sport: Sport,
      *,
      league_name: str | None = None,
  ) -> Event | None:
      home_score = fields.get("AG")
      away_score = fields.get("AH")
      if not home_score or not away_score:
          return None
      status = FLASHSCORE_STATUS_MAP.get(fields.get("AB", ""), EventStatus.UNKNOWN)
      if status not in (EventStatus.FINISHED, EventStatus.LIVE, EventStatus.UNKNOWN):
          return None
      event = self._event_from_fields(fields, sport, skip_pattern_check=True)
      if event is None:
          return None
      event.status = EventStatus.FINISHED
      event.home_score = home_score
      event.away_score = away_score
      if league_name and (not event.league or event.league == "Unknown"):
          event.league = league_name
      return event

  def _parse_finished_from_html(
      self,
      html: str,
      sport: Sport,
      *,
      league_name: str | None = None,
      tennis_filter: bool = False,
  ) -> list[Event]:
      events: list[Event] = []
      seen: set[str] = set()
      for feed_text in self.parse_embedded_feeds(html):
          for fields in self.parse_feed(feed_text):
              event = self._finished_event_from_fields(fields, sport, league_name=league_name)
              if event is None:
                  continue
              if tennis_filter and not self._is_relevant_tennis_league_with(
                  event.league,
                  self.config.tennis_history_exclude_patterns,
                  self.config.tennis_history_tour_patterns,
              ):
                  continue
              if event.dedupe_key in seen:
                  continue
              seen.add(event.dedupe_key)
              events.append(event)
      return events

  def fetch_archive_results(
      self,
      page_url: str,
      league_name: str,
      sport: Sport,
      *,
      tennis_filter: bool = False,
  ) -> list[Event]:
      events: list[Event] = []
      seen: set[str] = set()
      base = page_url.rstrip("/") + "/"
      for suffix in ("draw/", "results/", "", "fixtures/"):
          url = base if not suffix else base + suffix
          try:
              html = self.http.get_text(url, headers={"Referer": self.BASE_SITE})
          except Exception:
              continue
          for event in self._parse_finished_from_html(
              html,
              sport,
              league_name=league_name,
              tennis_filter=tennis_filter,
          ):
              if event.dedupe_key in seen:
                  continue
              seen.add(event.dedupe_key)
              events.append(event)
      events.sort(key=lambda item: item.start_time, reverse=True)
      return events

  def _normalize_tournament_url(self, url: str) -> str | None:
      normalized = url if url.startswith("http") else f"{self.BASE_SITE}{url}"
      normalized = normalized.rstrip("/") + "/"
      if "doubles" in normalized.lower():
          return None
      path = normalized.replace(self.BASE_SITE, "").strip("/")
      parts = path.split("/")
      if len(parts) > 3 and parts[-1] in self.TENNIS_TOURNAMENT_SUBPAGES:
          normalized = f"{self.BASE_SITE}/{'/'.join(parts[:3])}/"
      return normalized

  def discover_tennis_homepage_tournament_urls(self) -> list[str]:
      html = self.http.get_text(f"{self.BASE_SITE}/tennis/", headers={"Referer": self.BASE_SITE})
      seen: set[str] = set()
      urls: list[str] = []
      for match in self.TENNIS_TOUR_URL_PATTERN.finditer(html):
          normalized = self._normalize_tournament_url(match.group(1))
          if normalized and normalized not in seen:
              seen.add(normalized)
              urls.append(normalized)
      return urls

  def discover_all_tennis_tournament_urls(self) -> list[str]:
      seen: set[str] = set()
      urls: list[str] = []

      def add(url: str) -> None:
          normalized = self._normalize_tournament_url(url)
          if normalized and normalized not in seen:
              seen.add(normalized)
              urls.append(normalized)

      for page_url in self.config.flashscore_tennis_grand_slam_urls.values():
          add(page_url)

      for tour in self.config.tennis_crawl_tours:
          for link in self.discover_tennis_tournament_links(tour):
              add(link)

      if self.config.tennis_probe_wta_from_atp_slugs:
          for link in self.discover_tennis_tournament_links("atp-singles"):
              slug = link.rstrip("/").split("/")[-1]
              add(f"{self.BASE_SITE}/tennis/wta-singles/{slug}/")

      for link in self.discover_tennis_homepage_tournament_urls():
          add(link)

      return urls

  def _fetch_finished_from_tournament_urls(
      self,
      tournament_urls: list[str],
      *,
      days_back: int | None = None,
      tennis_filter: bool = True,
  ) -> list[Event]:
      cutoff = (
          datetime.now(tz=UTC) - timedelta(days=days_back)
          if days_back is not None
          else None
      )
      events: list[Event] = []
      seen: set[str] = set()

      for page_url in tournament_urls:
          draw_url = page_url.rstrip("/") + "/draw/"
          try:
              html = self.http.get_text(draw_url, headers={"Referer": self.BASE_SITE})
          except Exception:
              continue
          for event in self._parse_finished_from_html(
              html,
              Sport.TENNIS,
              tennis_filter=tennis_filter,
          ):
              if cutoff is not None and event.start_time < cutoff:
                  continue
              if event.dedupe_key in seen:
                  continue
              seen.add(event.dedupe_key)
              events.append(event)

      events.sort(key=lambda item: item.start_time, reverse=True)
      return events

  def fetch_tennis_finished_results(self, *, days_back: int | None = None) -> list[Event]:
      if days_back is not None and self.config.tennis_results_use_homepage_tournaments:
          tournament_urls = self.discover_tennis_homepage_tournament_urls()
      elif self.config.crawl_tennis_tournaments:
          tournament_urls = self.discover_all_tennis_tournament_urls()
      else:
          tournament_urls = list(self.config.flashscore_tennis_grand_slam_urls.values())
      return self._fetch_finished_from_tournament_urls(
          tournament_urls,
          days_back=days_back,
      )

  def discover_tennis_tournament_links(self, tour: str) -> list[str]:
      html = self.http.get_text(
          f"{self.BASE_SITE}/tennis/{tour}/",
          headers={"Referer": self.BASE_SITE},
      )
      pattern = rf'href="(/tennis/{tour}/[^"]+/)"'
      links = sorted(set(re.findall(pattern, html)))
      return [f"{self.BASE_SITE}{link}" for link in links if "doubles" not in link.lower()]

  def fetch_tennis_tournament_history(self) -> list[Event]:
      return self.fetch_tennis_finished_results(days_back=None)

  def fetch_football_archive_history(self) -> list[Event]:
      events: list[Event] = []
      seen: set[str] = set()
      for league_name, page_url in self.config.flashscore_football_archive_urls.items():
          for event in self.fetch_archive_results(page_url, league_name, Sport.FOOTBALL):
              if event.dedupe_key in seen:
                  continue
              seen.add(event.dedupe_key)
              events.append(event)
      return events

  def fetch_football_upcoming(
      self,
      *,
      days_ahead: int | None = None,
      include_live: bool = True,
  ) -> list[Event]:
      days = days_ahead if days_ahead is not None else self.config.days_ahead
      now = datetime.now(tz=UTC)
      cutoff = now + timedelta(days=days)
      events: list[Event] = []
      seen: set[str] = set()

      for league_name, league_url in self.config.flashscore_football_league_urls.items():
          html = self.http.get_text(league_url, headers={"Referer": self.BASE_SITE})
          feed_text = self.parse_embedded_feed(html)
          if not feed_text:
              continue
          for fields in self.parse_feed(feed_text):
              event = self._event_from_fields(fields, Sport.FOOTBALL, skip_pattern_check=True)
              if event is None:
                  continue
              if event.start_time > cutoff:
                  continue
              if not self._is_upcoming_event(event, now=now, include_live=include_live):
                  continue
              event.league = league_name
              if event.dedupe_key in seen:
                  continue
              seen.add(event.dedupe_key)
              events.append(event)

      events.sort(key=lambda item: item.start_time)
      return events

  def fetch_tennis_upcoming(
      self,
      *,
      days_ahead: int | None = None,
      include_live: bool = True,
  ) -> list[Event]:
      days = days_ahead if days_ahead is not None else self.config.tennis_days_ahead
      now = datetime.now(tz=UTC)
      cutoff = now + timedelta(days=days)
      events: list[Event] = []
      seen: set[str] = set()

      def add_event(event: Event | None) -> None:
          if event is None:
              return
          if event.start_time > cutoff:
              return
          if not self._is_upcoming_event(event, now=now, include_live=include_live):
              return
          if not self._is_relevant_tennis_league(event.league):
              return
          if event.dedupe_key in seen:
              return
          seen.add(event.dedupe_key)
          events.append(event)

      for _title, page_url in self.discover_tennis_tournament_pages():
          html = self.http.get_text(page_url, headers={"Referer": self.BASE_SITE})
          feed_text = self.parse_embedded_feed(html)
          if not feed_text:
              continue
          for fields in self.parse_feed(feed_text):
              add_event(self._event_from_fields(fields, Sport.TENNIS, skip_pattern_check=True))

      for day_offset in range(0, days + 1):
          feed_path = f"f_2_{day_offset}_3_en_1"
          text = self.fetch_feed(feed_path)
          for fields in self.parse_feed(text):
              add_event(self._event_from_fields(fields, Sport.TENNIS))

      events.sort(key=lambda item: item.start_time)
      return events

  def fetch_upcoming(
      self,
      sport: Sport,
      *,
      days_ahead: int | None = None,
      include_live: bool = True,
  ) -> list[Event]:
      if sport is Sport.FOOTBALL:
          return self.fetch_football_upcoming(days_ahead=days_ahead, include_live=include_live)
      return self.fetch_tennis_upcoming(days_ahead=days_ahead, include_live=include_live)

  def fetch_recent_results(
      self,
      sport: Sport,
      *,
      days_back: int | None = None,
  ) -> list[Event]:
      if sport is Sport.TENNIS:
          days = days_back if days_back is not None else self.config.tennis_results_lookback_days
          return self.fetch_tennis_finished_results(days_back=days)

      days = days_back if days_back is not None else self.config.results_lookback_days
      sport_code = "1" if sport is Sport.FOOTBALL else "2"
      events: list[Event] = []
      seen: set[str] = set()

      for day_offset in range(0, days + 1):
          feed_path = f"f_{sport_code}_{day_offset}_3_en_1"
          text = self.fetch_feed(feed_path)
          for fields in self.parse_feed(text):
              status = FLASHSCORE_STATUS_MAP.get(fields.get("AB", ""), EventStatus.UNKNOWN)
              if status is not EventStatus.FINISHED:
                  continue
              home_score = fields.get("AG")
              away_score = fields.get("AH")
              if not home_score or not away_score:
                  continue
              event = self._event_from_fields(fields, sport, skip_pattern_check=True)
              if event is None:
                  continue
              if sport is Sport.FOOTBALL and not self._matches_patterns(
                  event.league,
                  self.config.football_league_patterns,
                  exact=True,
              ):
                  # keep world cup, major leagues, and recognizable tournaments
                  league_upper = event.league.upper()
                  if not any(
                      token in league_upper
                      for token in ("WORLD", "EUROPE", "ENGLAND", "SPAIN", "ITALY", "GERMANY", "FRANCE", "POLAND")
                  ):
                      continue
              event.status = EventStatus.FINISHED
              event.home_score = home_score
              event.away_score = away_score
              if event.dedupe_key in seen:
                  continue
              seen.add(event.dedupe_key)
              events.append(event)

      events.sort(key=lambda item: item.start_time, reverse=True)
      return events

  def match_statistics_payload(self, match_id: str, sport: Sport) -> dict[str, Any]:
      stats = self.fetch_statistics(match_id, sport=sport)
      flat: dict[str, Any] = {"groups": stats.get("groups", [])}
      for group in stats.get("groups", []):
          group_name = str(group.get("name", "unknown")).lower().replace(" ", "_")
          for item in group.get("items", []):
              key = f"{group_name}.{str(item.get('name', '')).lower().replace(' ', '_')}"
              flat[key] = {"home": item.get("home"), "away": item.get("away")}
      return flat

  def fetch_h2h(self, match_id: str, sport: Sport = Sport.FOOTBALL) -> list[dict[str, Any]]:
      cache_key = f"{sport.value}:{match_id}"
      if cache_key in self._h2h_cache:
          return self._h2h_cache[cache_key]

      sport_code = "1" if sport is Sport.FOOTBALL else "2"
      text = self.fetch_feed(f"df_hh_{sport_code}_{match_id}")
      matches: list[dict[str, Any]] = []
      current_side = ""
      for raw_block in text.split("¬~"):
          fields: dict[str, str] = {}
          for part in raw_block.split("¬"):
              if "÷" not in part:
                  continue
              key, value = part.split("÷", 1)
              fields[key] = value
          if "KB" in fields:
              current_side = fields["KB"]
              continue
          if "KJ" in fields and "KK" in fields:
              matches.append(
                  {
                      "context": current_side,
                      "home": fields.get("KJ"),
                      "away": fields.get("KK"),
                      "score": fields.get("KL"),
                      "timestamp": int(fields["KC"]) if fields.get("KC", "").isdigit() else None,
                      "tournament": fields.get("KF"),
                      "surface": fields.get("KD") or fields.get("KE"),
                  }
              )
      self._h2h_cache[cache_key] = matches
      return matches

  def fetch_statistics(self, match_id: str, sport: Sport = Sport.FOOTBALL) -> dict[str, Any]:
      cache_key = f"{sport.value}:{match_id}"
      if cache_key in self._statistics_cache:
          return self._statistics_cache[cache_key]

      sport_code = "1" if sport is Sport.FOOTBALL else "2"
      text = self.fetch_feed(f"df_st_{sport_code}_{match_id}")
      stats: dict[str, Any] = {"groups": []}
      current_group: dict[str, Any] | None = None
      current_stat: dict[str, Any] | None = None
      for raw_block in text.split("¬~"):
          fields: dict[str, str] = {}
          for part in raw_block.split("¬"):
              if "÷" not in part:
                  continue
              key, value = part.split("÷", 1)
              fields[key] = value
          if "SE" in fields:
              stats["period"] = fields["SE"]
          if "SF" in fields:
              current_group = {"name": fields["SF"], "items": []}
              stats["groups"].append(current_group)
          if "SG" in fields and current_group is not None:
              current_stat = {
                  "name": fields["SG"],
                  "home": fields.get("SH"),
                  "away": fields.get("SI"),
              }
              current_group["items"].append(current_stat)
      self._statistics_cache[cache_key] = stats
      return stats

  def h2h_direct_matches(self, h2h: list[dict[str, Any]], home: str, away: str) -> list[dict[str, Any]]:
      home_key = home.split()[0].lower()
      away_key = away.split()[0].lower()
      direct: list[dict[str, Any]] = []
      for item in h2h:
          context = (item.get("context") or "").lower()
          if "head-to-head" not in context and "h2h" not in context:
              continue
          left = (item.get("home") or "").lower()
          right = (item.get("away") or "").lower()
          if home_key in left and away_key in right:
              direct.append(item)
              continue
          if home_key in right and away_key in left:
              direct.append(item)
      return direct

  def form_from_h2h(self, h2h: list[dict[str, Any]], participant: str, limit: int = 5) -> list[dict[str, Any]]:
      participant_lower = participant.lower()
      form: list[dict[str, Any]] = []
      for item in h2h:
          context = (item.get("context") or "").lower()
          if participant_lower not in context:
              continue
          form.append(item)
          if len(form) >= limit:
              break
      return form
