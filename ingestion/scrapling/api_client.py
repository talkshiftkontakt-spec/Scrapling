from __future__ import annotations

import json
from urllib import request
from typing import Any

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord, ScreenshotArtifactRecord


class IngestionApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def submit_discovered_websites(self, records: list[DiscoveredWebsiteRecord]) -> dict[str, Any]:
        payload = [record.to_payload() for record in records]
        return self._post_json("/ingestion/discovered-websites", payload)

    def submit_screenshot(self, artifact: ScreenshotArtifactRecord) -> dict[str, Any]:
        return self._post_json("/ingestion/screenshots", artifact.to_payload())

    def _post_json(self, path: str, payload: Any) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")

        if not content:
            return {}
        return json.loads(content)
