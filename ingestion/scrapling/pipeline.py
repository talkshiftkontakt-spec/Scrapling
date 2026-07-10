from __future__ import annotations

from ingestion.scrapling.api_client import IngestionApiClient
from ingestion.scrapling.capture import ScreenshotCaptureService
from ingestion.scrapling.providers import ALL_PROVIDERS


class DesignIngestionPipeline:
    def __init__(self, api_base_url: str) -> None:
        self.api_client = IngestionApiClient(api_base_url)
        self.capture_service = ScreenshotCaptureService()

    def discover_all(self) -> dict[str, object]:
        records = []
        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            records.extend(provider.discover())
        return self.api_client.submit_discovered_websites(records)

    def capture_website(self, website_id: str, url: str) -> dict[str, object]:
        artifact = self.capture_service.capture(website_id=website_id, url=url)
        return self.api_client.submit_screenshot(artifact)
