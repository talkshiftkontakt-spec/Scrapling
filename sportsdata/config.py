from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_DB_PATH = Path("data/sportsdata.db")
DEFAULT_DAYS_AHEAD = 45
DEFAULT_TENNIS_DAYS_AHEAD = 14

FOOTBALL_LEAGUE_PATTERNS: tuple[str, ...] = (
    "ENGLAND: Premier League",
    "SPAIN: LaLiga",
    "ITALY: Serie A",
    "GERMANY: Bundesliga",
    "FRANCE: Ligue 1",
    "POLAND: Ekstraklasa",
    "POLAND: 1. Liga",
    "EUROPE: Champions League",
    "EUROPE: Europa League",
    "EUROPE: Conference League",
    "WORLD: World Cup",
)

FLASHSCORE_FOOTBALL_LEAGUE_URLS: dict[str, str] = {
    "ENGLAND: Premier League": "https://www.flashscore.com/football/england/premier-league/fixtures/",
    "SPAIN: LaLiga": "https://www.flashscore.com/football/spain/laliga/fixtures/",
    "ITALY: Serie A": "https://www.flashscore.com/football/italy/serie-a/fixtures/",
    "GERMANY: Bundesliga": "https://www.flashscore.com/football/germany/bundesliga/fixtures/",
    "FRANCE: Ligue 1": "https://www.flashscore.com/football/france/ligue-1/fixtures/",
    "POLAND: Ekstraklasa": "https://www.flashscore.com/football/poland/ekstraklasa/fixtures/",
    "POLAND: 1. Liga": "https://www.flashscore.com/football/poland/division-1/fixtures/",
    "EUROPE: Champions League": "https://www.flashscore.com/football/europe/champions-league/fixtures/",
    "EUROPE: Europa League": "https://www.flashscore.com/football/europe/europa-league/fixtures/",
    "EUROPE: Conference League": "https://www.flashscore.com/football/europe/conference-league/fixtures/",
    "WORLD: World Cup": "https://www.flashscore.com/football/world/world-cup/fixtures/",
}

TENNIS_TOUR_PATTERNS: tuple[str, ...] = (
    "ATP",
    "WTA",
    "CHALLENGER",
    "GRAND SLAM",
    "WIMBLEDON",
    "ROLAND GARROS",
    "FRENCH OPEN",
    "US OPEN",
    "AUSTRALIAN OPEN",
)

UNDERSTAT_LEAGUES: dict[str, str] = {
    "ENGLAND: Premier League": "EPL",
    "SPAIN: LaLiga": "La_Liga",
    "ITALY: Serie A": "Serie_A",
    "GERMANY: Bundesliga": "Bundesliga",
    "FRANCE: Ligue 1": "Ligue_1",
}

FOOTBALL_DATA_URLS: dict[str, str] = {
    "premier-league": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "championship": "https://www.football-data.co.uk/mmz4281/2425/E1.csv",
    "la-liga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "serie-a": "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    "bundesliga": "https://www.football-data.co.uk/mmz4281/2425/D1.csv",
    "ligue-1": "https://www.football-data.co.uk/mmz4281/2425/F1.csv",
}

FOOTBALL_DATA_SEASONS: tuple[str, ...] = ("2425", "2324", "2223", "2122", "2021")

FOOTBALL_DATA_LEAGUE_FILES: dict[str, str] = {
    "premier-league": "E0",
    "championship": "E1",
    "la-liga": "SP1",
    "serie-a": "I1",
    "bundesliga": "D1",
    "ligue-1": "F1",
    "scotland-premiership": "SC0",
    "netherlands-eredivisie": "N1",
    "belgium-pro-league": "B1",
    "portugal-liga": "P1",
    "turkey-super-lig": "T1",
    "greece-super-league": "G1",
}

UNDERSTAT_SEASONS: tuple[str, ...] = ("2021", "2022", "2023", "2024", "2025")

FLASHSCORE_FOOTBALL_ARCHIVE_URLS: dict[str, str] = {
    "WORLD: World Cup 2026": "https://www.flashscore.com/football/world/world-cup/",
    "WORLD: World Cup 2022": "https://www.flashscore.com/football/world/world-cup-2022/",
    "WORLD: World Cup 2018": "https://www.flashscore.com/football/world/world-cup-2018/",
    "EUROPE: Euro 2024": "https://www.flashscore.com/football/europe/euro-2024/",
    "EUROPE: Euro 2020": "https://www.flashscore.com/football/europe/euro-2020/",
}

FLASHSCORE_TENNIS_GRAND_SLAM_URLS: dict[str, str] = {
    "ATP - SINGLES: Australian Open": "https://www.flashscore.com/tennis/atp-singles/australian-open/",
    "ATP - SINGLES: French Open": "https://www.flashscore.com/tennis/atp-singles/french-open/",
    "ATP - SINGLES: Wimbledon": "https://www.flashscore.com/tennis/atp-singles/wimbledon/",
    "ATP - SINGLES: US Open": "https://www.flashscore.com/tennis/atp-singles/us-open/",
    "WTA - SINGLES: Australian Open": "https://www.flashscore.com/tennis/wta-singles/australian-open/",
    "WTA - SINGLES: French Open": "https://www.flashscore.com/tennis/wta-singles/french-open/",
    "WTA - SINGLES: Wimbledon": "https://www.flashscore.com/tennis/wta-singles/wimbledon/",
    "WTA - SINGLES: US Open": "https://www.flashscore.com/tennis/wta-singles/us-open/",
}

TENNIS_HISTORY_TOUR_PATTERNS: tuple[str, ...] = (
    "ATP",
    "WTA",
    "CHALLENGER",
    "GRAND SLAM",
    "WIMBLEDON",
    "ROLAND GARROS",
    "FRENCH OPEN",
    "US OPEN",
    "AUSTRALIAN OPEN",
)

TENNIS_CRAWL_TOURS: tuple[str, ...] = (
    "atp-singles",
    "wta-singles",
    "challenger-men-singles",
    "challenger-women-singles",
)

ODDSPORTAL_LEAGUE_URLS: dict[str, str] = {
    "premier-league": "https://www.oddsportal.com/football/england/premier-league/",
    "la-liga": "https://www.oddsportal.com/football/spain/laliga/",
    "serie-a": "https://www.oddsportal.com/football/italy/serie-a/",
    "bundesliga": "https://www.oddsportal.com/football/germany/bundesliga/",
    "ligue-1": "https://www.oddsportal.com/football/france/ligue-1/",
    "champions-league": "https://www.oddsportal.com/football/europe/champions-league/",
    "europa-league": "https://www.oddsportal.com/football/europe/europa-league/",
    "tennis-atp": "https://www.oddsportal.com/tennis/",
    "tennis-wta": "https://www.oddsportal.com/tennis/",
}

BETCLIC_BOOKMAKER_NAMES: tuple[str, ...] = (
    "Betclic",
    "Betclic.pl",
    "Betclic.fr",
    "betclic",
)


@dataclass
class PipelineConfig:
    db_path: Path = DEFAULT_DB_PATH
    days_ahead: int = DEFAULT_DAYS_AHEAD
    tennis_days_ahead: int = DEFAULT_TENNIS_DAYS_AHEAD
    football_league_patterns: tuple[str, ...] = FOOTBALL_LEAGUE_PATTERNS
    tennis_tour_patterns: tuple[str, ...] = TENNIS_TOUR_PATTERNS
    tennis_exclude_patterns: tuple[str, ...] = ("DOUBLES", "ITF", "BOYS", "GIRLS")
    target_bookmakers: tuple[str, ...] = BETCLIC_BOOKMAKER_NAMES
    flashscore_fsign: str | None = None
    request_delay_seconds: float = 0.4
    stats_batch_size: int = 0
    stats_max_age_hours: int = 12
    odds_h2h_limit: int = 30
    enable_sofascore: bool = True
    enable_understat: bool = True
    enable_oddsportal: bool = True
    oddsportal_league_urls: dict[str, str] = field(default_factory=lambda: dict(ODDSPORTAL_LEAGUE_URLS))
    flashscore_football_league_urls: dict[str, str] = field(
        default_factory=lambda: dict(FLASHSCORE_FOOTBALL_LEAGUE_URLS)
    )
    understat_season: str = "2025"
    understat_seasons: tuple[str, ...] = UNDERSTAT_SEASONS
    results_lookback_days: int = 90
    tennis_results_lookback_days: int = 90
    football_data_seasons: tuple[str, ...] = FOOTBALL_DATA_SEASONS
    flashscore_football_archive_urls: dict[str, str] = field(
        default_factory=lambda: dict(FLASHSCORE_FOOTBALL_ARCHIVE_URLS)
    )
    flashscore_tennis_grand_slam_urls: dict[str, str] = field(
        default_factory=lambda: dict(FLASHSCORE_TENNIS_GRAND_SLAM_URLS)
    )
    tennis_history_tour_patterns: tuple[str, ...] = TENNIS_HISTORY_TOUR_PATTERNS
    tennis_history_exclude_patterns: tuple[str, ...] = ("DOUBLES", "BOYS", "GIRLS")
    tennis_crawl_tours: tuple[str, ...] = TENNIS_CRAWL_TOURS
    tennis_probe_wta_from_atp_slugs: bool = True
    tennis_results_use_homepage_tournaments: bool = True
    crawl_tennis_tournaments: bool = True
    archive_fetch_stats: bool = True
    archive_stats_limit: int = 300
    tennis_archive_stats_limit: int = 500
