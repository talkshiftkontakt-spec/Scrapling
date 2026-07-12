from __future__ import annotations

import os
from urllib.parse import urlparse

from ingestion.scrapling.api_client import IngestionApiClient
from ingestion.scrapling.capture import ScreenshotCaptureService
from ingestion.scrapling.providers import ALL_PROVIDERS


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    parsed = parsed._replace(fragment="")
    normalized = parsed.geturl()
    if normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


class DesignIngestionPipeline:
    def __init__(self, api_base_url: str | None = None) -> None:
        self.api_client = IngestionApiClient(api_base_url or os.environ.get("INGESTION_API_URL", "http://127.0.0.1:3101"))
        self.capture_service = ScreenshotCaptureService()

    def discover_all(self, limit: int = 50, provider: str | None = None) -> dict[str, object]:
        known_urls = set(self.api_client.get_known_urls())
        records: list = []
        seen_urls: set[str] = set()

        provider_classes = ALL_PROVIDERS
        if provider:
            provider_classes = [cls for cls in ALL_PROVIDERS if cls().slug == provider]
            if not provider_classes:
                raise ValueError(f"Unknown provider: {provider}")

        for provider_cls in provider_classes:
            provider_instance = provider_cls()
            for discovered in provider_instance.discover():
                normalized = normalize_url(discovered.url)
                if discovered.url in seen_urls or normalized in known_urls:
                    continue
                seen_urls.add(discovered.url)
                records.append(discovered)
                if len(records) >= limit:
                    break
            if len(records) >= limit:
                break

        trimmed = records[:limit]
        if not trimmed:
            return {"accepted": 0, "records": [], "skippedKnown": len(known_urls)}

        return self.api_client.submit_discovered_websites(trimmed)

    def _capture_and_persist(self, website_id: str, url: str, source: str | None = None) -> dict[str, object]:
        result = self.capture_service.capture_website_pages(website_id=website_id, url=url, source=source)
        page_response = self.api_client.submit_page_screenshots(
            website_id=website_id,
            pages=result.pages,
            primary_screenshot=result.primary,
        )
        return {
            "websiteId": website_id,
            "url": url,
            "pageCount": len(result.pages),
            "response": page_response,
        }

    def capture_batch(self, limit: int = 10) -> list[dict[str, object]]:
        pending = self.api_client.get_pending_capture(limit)
        results: list[dict[str, object]] = []

        for item in pending:
            website_id = item["websiteId"]
            url = item["canonicalUrl"]
            source = item.get("source")
            try:
                capture_result = self._capture_and_persist(website_id=website_id, url=url, source=source)
                results.append({**capture_result, "status": "captured"})
            except Exception as exc:  # noqa: BLE001
                self.api_client.mark_website_status(website_id, "failed")
                results.append({"websiteId": website_id, "url": url, "status": "failed", "error": str(exc)})

        return results

    def recapture_batch(self, limit: int = 10, status: str = "accepted") -> list[dict[str, object]]:
        references = self.api_client.list_references(status=status, limit=limit)
        results: list[dict[str, object]] = []

        for item in references:
            website_id = item["websiteId"]
            url = item["canonicalUrl"]
            source = item.get("source")
            try:
                capture_result = self._capture_and_persist(website_id=website_id, url=url, source=source)
                results.append({**capture_result, "status": "recaptured"})
            except Exception as exc:  # noqa: BLE001
                self.api_client.record_page_capture_failure(website_id, str(exc))
                results.append({"websiteId": website_id, "url": url, "status": "failed", "error": str(exc)})

        return results

    def recapture_missing_pages(self, limit: int = 10) -> list[dict[str, object]]:
        pending = self.api_client.get_needs_page_capture(limit)
        results: list[dict[str, object]] = []

        for item in pending:
            website_id = item["websiteId"]
            url = item["canonicalUrl"]
            source = item.get("source")
            try:
                capture_result = self._capture_and_persist(website_id=website_id, url=url, source=source)
                results.append({**capture_result, "status": "recaptured"})
            except Exception as exc:  # noqa: BLE001
                self.api_client.record_page_capture_failure(website_id, str(exc))
                results.append({"websiteId": website_id, "url": url, "status": "failed", "error": str(exc)})

        return results

    def capture_website(self, website_id: str, url: str) -> dict[str, object]:
        return self._capture_and_persist(website_id=website_id, url=url)
