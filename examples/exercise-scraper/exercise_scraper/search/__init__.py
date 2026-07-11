from __future__ import annotations

from urllib.parse import urlparse

from exercise_scraper.config import BLOCKED_DOMAINS, Settings
from exercise_scraper.models import SearchResult
from exercise_scraper.search.base import SearchProvider
from exercise_scraper.search.duckduckgo import DuckDuckGoProvider, DEFAULT_SEARCH_USER_AGENT
from exercise_scraper.search.serpapi import SerpApiProvider


def get_provider(provider: str, settings: Settings) -> SearchProvider:
    if provider == "serpapi":
        if not settings.serpapi_key:
            raise ValueError("SERPAPI_KEY is required for provider=serpapi")
        return SerpApiProvider(settings.serpapi_key)
    if provider == "duckduckgo":
        return DuckDuckGoProvider(DEFAULT_SEARCH_USER_AGENT)
    raise ValueError(f"Unknown search provider: {provider}")


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return f"{parsed.scheme}://{parsed.netloc.lower()}{path}"


def is_blocked_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host in BLOCKED_DOMAINS or f"www.{host}" in BLOCKED_DOMAINS


def collect_urls(
    provider: SearchProvider,
    queries: list[tuple[str, str]],
    *,
    max_pages: int,
    results_per_query: int,
) -> list[SearchResult]:
    seen: set[str] = set()
    collected: list[SearchResult] = []

    for query, _lang_tag in queries:
        try:
            batch = provider.search(query, num=results_per_query)
        except Exception:
            continue

        for result in batch:
            if is_blocked_url(result.url):
                continue
            key = normalize_url(result.url)
            if key in seen:
                continue
            seen.add(key)
            result.query = query
            collected.append(result)
            if len(collected) >= max_pages:
                return collected

    return collected
