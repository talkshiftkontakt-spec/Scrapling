from __future__ import annotations

from exercise_scraper.queries import build_queries
from exercise_scraper.search import collect_urls, is_blocked_url, normalize_url
from exercise_scraper.search.base import SearchProvider
from exercise_scraper.models import SearchResult


class StubProvider(SearchProvider):
    def __init__(self, mapping: dict[str, list[SearchResult]]) -> None:
        self._mapping = mapping

    def search(self, query: str, *, num: int = 10) -> list[SearchResult]:
        return self._mapping.get(query, [])[:num]


def test_normalize_url_strips_trailing_slash() -> None:
    assert normalize_url("https://Example.com/path/") == "https://example.com/path"


def test_is_blocked_url() -> None:
    assert is_blocked_url("https://www.youtube.com/watch?v=1")
    assert not is_blocked_url("https://perfect-english-grammar.com/past-simple.html")


def test_collect_urls_dedup_and_limit() -> None:
    provider = StubProvider(
        {
            "Past Simple exercises": [
                SearchResult(url="https://site-a.test/one", title="A"),
                SearchResult(url="https://site-a.test/one/", title="A duplicate"),
                SearchResult(url="https://site-b.test/two", title="B"),
            ],
            "Past Simple worksheet": [
                SearchResult(url="https://site-c.test/three", title="C"),
            ],
        }
    )
    queries = build_queries("Past Simple", "en", limit_per_lang=2)
    results = collect_urls(provider, queries, max_pages=2, results_per_query=5)
    assert len(results) == 2
    urls = {result.url for result in results}
    assert "https://site-a.test/one" in urls
