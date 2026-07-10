from __future__ import annotations

import os

from ingestion.scrapling.api_client import IngestionApiClient
from ingestion.scrapling.capture import ScreenshotCaptureService
from ingestion.scrapling.providers import ALL_PROVIDERS


class DesignIngestionPipeline:
    def __init__(self, api_base_url: str | None = None) -> None:
        self.api_client = IngestionApiClient(api_base_url or os.environ.get("INGESTION_API_URL", "http://127.0.0.1:3001"))
        self.capture_service = ScreenshotCaptureService()

    def discover_all(self, limit: int = 50) -> dict[str, object]:
        records: list = []
        seen_urls: set[str] = set()

        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            for discovered in provider.discover():
                if discovered.url in seen_urls:
                    continue
                seen_urls.add(discovered.url)
                records.append(discovered)
                if len(records) >= limit:
                    break
            if len(records) >= limit:
                break

        trimmed = records[:limit]
        return self.api_client.submit_discovered_websites(trimmed)

    def capture_batch(self, limit: int = 10) -> list[dict[str, object]]:
        pending = self.api_client.get_pending_capture(limit)
        results: list[dict[str, object]] = []

        for item in pending:
            website_id = item["websiteId"]
            url = item["canonicalUrl"]
            source = item.get("source")
            try:
                artifact = self.capture_service.capture(website_id=website_id, url=url, source=source)
                response = self.api_client.submit_screenshot(artifact)
                results.append({"websiteId": website_id, "url": url, "status": "captured", "response": response})
            except Exception as exc:  # noqa: BLE001 - surface per-site failures in batch output
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
                artifact = self.capture_service.capture(website_id=website_id, url=url, source=source)
                response = self.api_client.submit_screenshot(artifact)
                results.append({"websiteId": website_id, "url": url, "status": "recaptured", "response": response})
            except Exception as exc:  # noqa: BLE001
                results.append({"websiteId": website_id, "url": url, "status": "failed", "error": str(exc)})

        return results

    def capture_website(self, website_id: str, url: str) -> dict[str, object]:
        artifact = self.capture_service.capture(website_id=website_id, url=url)
        return self.api_client.submit_screenshot(artifact)
