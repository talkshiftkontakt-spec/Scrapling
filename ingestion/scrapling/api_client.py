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

    def submit_page_screenshots(
        self,
        website_id: str,
        pages: list[Any],
        primary_screenshot: Any | None = None,
    ) -> dict[str, Any]:
        payload = {
            "websiteId": website_id,
            "pages": [page.to_payload() if hasattr(page, "to_payload") else page for page in pages],
        }
        if primary_screenshot is not None:
            payload["primaryScreenshot"] = (
                primary_screenshot.to_payload()
                if hasattr(primary_screenshot, "to_payload")
                else primary_screenshot
            )
        return self._post_json("/ingestion/page-screenshots", payload)

    def list_page_screenshots(self, website_id: str) -> list[dict[str, Any]]:
        return self._get_json(f"/references/{website_id}/pages")

    def mark_website_status(self, website_id: str, status: str) -> dict[str, Any]:
        return self._post_json(f"/ingestion/mark-status/{website_id}", {"status": status})

    def record_page_capture_failure(self, website_id: str, error: str) -> dict[str, Any]:
        return self._post_json(f"/ingestion/page-capture-failure/{website_id}", {"error": error})

    def list_references(self, status: str = "accepted", limit: int = 200) -> list[dict[str, object]]:
        return self._get_json(f"/references?status={status}&limit={limit}")

    def get_known_urls(self) -> list[str]:
        payload = self._get_json("/ingestion/known-urls")
        if isinstance(payload, dict):
            return payload.get("urls", [])
        return []

    def get_pending_capture(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._get_json(f"/ingestion/pending-capture?limit={limit}")

    def get_needs_page_capture(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._get_json(f"/ingestion/needs-page-capture?limit={limit}")

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
