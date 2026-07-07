from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

BLOCKED_DOMAINS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "facebook.com",
        "www.facebook.com",
        "twitter.com",
        "x.com",
        "instagram.com",
        "www.instagram.com",
        "reddit.com",
        "www.reddit.com",
        "pinterest.com",
        "www.pinterest.com",
        "tiktok.com",
        "www.tiktok.com",
    }
)

EXERCISE_KEYWORDS_EN = frozenset(
    {
        "exercise",
        "exercises",
        "worksheet",
        "practice",
        "fill in",
        "complete the",
        "answer key",
        "grammar",
    }
)

EXERCISE_KEYWORDS_PL = frozenset(
    {
        "ćwiczenie",
        "ćwiczenia",
        "zadanie",
        "zadania",
        "uzupełnij",
        "przetłumacz",
        "odpowiedzi",
        "klucz odpowiedzi",
        "gramatyka",
        "test",
    }
)


@dataclass
class Settings:
    serpapi_key: str | None
    max_pages: int
    download_delay: float
    min_confidence: float
    results_per_query: int
    queries_per_lang: int
    user_agent: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            serpapi_key=os.getenv("SERPAPI_KEY"),
            max_pages=int(os.getenv("EXERCISE_SCRAPER_MAX_PAGES", "40")),
            download_delay=float(os.getenv("EXERCISE_SCRAPER_DELAY", "1.5")),
            min_confidence=float(os.getenv("EXERCISE_SCRAPER_MIN_CONFIDENCE", "0.4")),
            results_per_query=int(os.getenv("EXERCISE_SCRAPER_RESULTS_PER_QUERY", "10")),
            queries_per_lang=int(os.getenv("EXERCISE_SCRAPER_QUERIES_PER_LANG", "5")),
            user_agent=os.getenv(
                "EXERCISE_SCRAPER_USER_AGENT",
                "ExerciseScraper/0.1 (+https://github.com/D4Vinci/Scrapling; educational use)",
            ),
        )
