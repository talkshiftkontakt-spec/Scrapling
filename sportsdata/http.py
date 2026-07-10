from __future__ import annotations

import re
import time
from typing import Any

from scrapling.fetchers import Fetcher

try:
    from curl_cffi import requests as curl_requests
except ImportError:  # pragma: no cover - optional at import time
    curl_requests = None  # type: ignore[assignment]


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


class HttpClient:
    """HTTP helper using curl_cffi when available, otherwise Scrapling Fetcher."""

    def __init__(self, delay_seconds: float = 0.35) -> None:
        self.delay_seconds = delay_seconds
        self._last_request_at = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request_at = time.monotonic()

    def get_text(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        impersonate: str = "chrome120",
        retries: int = 3,
    ) -> str:
        last_error: Exception | None = None
        for attempt in range(retries):
            self._throttle()
            merged = {**DEFAULT_HEADERS, **(headers or {})}
            try:
                if curl_requests is not None:
                    response = curl_requests.get(
                        url, headers=merged, impersonate=impersonate, timeout=30
                    )
                    if response.status_code == 429 and attempt < retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                    return response.text

                response = Fetcher.get(url, headers=merged, stealthy_headers=True, timeout=30)
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                return response.text
            except Exception as exc:
                last_error = exc
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Failed to fetch {url}")

    def get_json(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        impersonate: str = "chrome120",
    ) -> Any:
        text = self.get_text(url, headers=headers, impersonate=impersonate)
        import json

        return json.loads(text)


def extract_flashscore_fsign(html: str, fallback: str = "SW9D1eZo") -> str:
    patterns = (
        r'"feed_sign"\s*:\s*"([^"]+)"',
        r"feed_sign['\"]?\s*[:=]\s*['\"]([^'\"]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return fallback
