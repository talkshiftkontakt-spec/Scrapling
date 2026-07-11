from __future__ import annotations

from exercise_scraper.models import SearchResult
from exercise_scraper.search.base import SearchProvider


class SerpApiProvider(SearchProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def search(self, query: str, *, num: int = 10) -> list[SearchResult]:
        try:
            from serpapi import GoogleSearch
        except ImportError as exc:
            raise RuntimeError(
                "SerpAPI provider requires `pip install exercise-scraper[search]`"
            ) from exc

        payload = GoogleSearch(
            {
                "q": query,
                "api_key": self._api_key,
                "num": num,
                "engine": "google",
            }
        ).get_dict()

        results: list[SearchResult] = []
        for item in payload.get("organic_results", []):
            link = item.get("link")
            if not link:
                continue
            results.append(
                SearchResult(
                    url=link,
                    title=item.get("title", ""),
                    snippet=item.get("snippet", ""),
                    query=query,
                )
            )
        return results
