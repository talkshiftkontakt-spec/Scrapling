from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from exercise_scraper.models import SearchResult
from exercise_scraper.search.base import SearchProvider

DEFAULT_SEARCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class DuckDuckGoProvider(SearchProvider):
    """HTML-based DuckDuckGo search (no API key required)."""

    def __init__(self, user_agent: str, timeout: float = 20.0) -> None:
        self._headers = {"User-Agent": user_agent}
        self._timeout = timeout

    def search(self, query: str, *, num: int = 10) -> list[SearchResult]:
        results: list[SearchResult] = []
        with httpx.Client(headers=self._headers, timeout=self._timeout, follow_redirects=True) as client:
            response = client.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query, "b": ""},
            )
            response.raise_for_status()
            html = response.text

        for match in re.finditer(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            raw_url, raw_title = match.group(1), match.group(2)
            url = self._normalize_result_url(raw_url)
            if not url:
                continue
            title = re.sub(r"<[^>]+>", "", raw_title).strip()
            results.append(SearchResult(url=url, title=title, query=query))
            if len(results) >= num:
                break

        return results

    @staticmethod
    def _normalize_result_url(raw_url: str) -> str | None:
        if raw_url.startswith("//"):
            raw_url = f"https:{raw_url}"

        parsed = urlparse(raw_url)
        if "duckduckgo.com" in parsed.netloc and parsed.path == "/l/":
            target = parse_qs(parsed.query).get("uddg", [None])[0]
            if target:
                return unquote(target)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return raw_url
        return None
