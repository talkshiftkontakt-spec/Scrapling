from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass(slots=True)
class DiscoveredWebsiteRecord:
    website_name: str
    url: str
    source: str
    categories: list[str]
    tags: list[str]
    provider_reference: str
    discovered_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "websiteName": self.website_name,
            "url": self.url,
            "source": self.source,
            "categories": self.categories,
            "tags": self.tags,
            "providerReference": self.provider_reference,
            "discoveredAt": self.discovered_at,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ScreenshotArtifactRecord:
    website_id: str
    screenshot_drive_file_id: str
    screenshot_drive_url: str
    thumbnail_drive_file_id: str
    thumbnail_drive_url: str
    width: int
    height: int
    checksum_sha256: str
    captured_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "websiteId": self.website_id,
            "screenshotDriveFileId": self.screenshot_drive_file_id,
            "screenshotDriveUrl": self.screenshot_drive_url,
            "thumbnailDriveFileId": self.thumbnail_drive_file_id,
            "thumbnailDriveUrl": self.thumbnail_drive_url,
            "width": self.width,
            "height": self.height,
            "checksumSha256": self.checksum_sha256,
            "capturedAt": self.captured_at,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ComponentCropRecord:
    website_id: str
    component_kind: str
    name: str
    drive_file_id: str
    drive_url: str
    thumbnail_drive_url: str | None
    bbox: dict[str, int]
    summary: str
    design_keywords: list[str]
    embedding_input: str
    confidence: float

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["websiteId"] = payload.pop("website_id")
        payload["componentKind"] = payload.pop("component_kind")
        payload["driveFileId"] = payload.pop("drive_file_id")
        payload["driveUrl"] = payload.pop("drive_url")
        payload["thumbnailDriveUrl"] = payload.pop("thumbnail_drive_url")
        payload["designKeywords"] = payload.pop("design_keywords")
        payload["embeddingInput"] = payload.pop("embedding_input")
        return payload
