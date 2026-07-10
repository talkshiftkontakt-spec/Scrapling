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
        records = []
        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            discovered = provider.discover()
            records.extend(discovered)
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
            try:
                artifact = self.capture_service.capture(website_id=website_id, url=url)
                response = self.api_client.submit_screenshot(artifact)
                results.append({"websiteId": website_id, "url": url, "status": "captured", "response": response})
            except Exception as exc:  # noqa: BLE001 - surface per-site failures in batch output
                results.append({"websiteId": website_id, "url": url, "status": "failed", "error": str(exc)})

        return results

    def capture_website(self, website_id: str, url: str) -> dict[str, object]:
        artifact = self.capture_service.capture(website_id=website_id, url=url)
        return self.api_client.submit_screenshot(artifact)
