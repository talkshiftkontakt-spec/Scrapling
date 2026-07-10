from __future__ import annotations

import json
from typing import Any
from urllib import request


class IngestionApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def submit_discovered_websites(self, records: list[Any]) -> dict[str, Any]:
        payload = [record.to_payload() if hasattr(record, "to_payload") else record for record in records]
        return self._post_json("/ingestion/discovered-websites", payload)

    def submit_screenshot(self, artifact: Any) -> dict[str, Any]:
        payload = artifact.to_payload() if hasattr(artifact, "to_payload") else artifact
        return self._post_json("/ingestion/screenshots", payload)

    def mark_website_status(self, website_id: str, status: str) -> dict[str, Any]:
        return self._post_json(f"/ingestion/mark-status/{website_id}", {"status": status})

    def get_pending_capture(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._get_json(f"/ingestion/pending-capture?limit={limit}")

    def _get_json(self, path: str) -> Any:
        req = request.Request(f"{self.base_url}{path}", method="GET")
        with request.urlopen(req, timeout=60) as response:
            content = response.read().decode("utf-8")
        return json.loads(content) if content else []

    def _post_json(self, path: str, payload: Any) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=120) as response:
            content = response.read().decode("utf-8")

        if not content:
            return {}
        return json.loads(content)
