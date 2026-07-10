from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from PIL import Image
from scrapling.fetchers import DynamicFetcher

from ingestion.scrapling.contracts import PageScreenshotArtifactRecord, ScreenshotArtifactRecord
from ingestion.scrapling.page_discovery import DiscoveredPage, discover_pages_in_browser
from ingestion.scrapling.storage import create_storage
from ingestion.scrapling.url_resolver import resolve_capture_url

Image.MAX_IMAGE_PIXELS = 300_000_000

DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_VIEWPORT = {"width": 390, "height": 844}
MAX_PAGES_PER_SITE = int(os.environ.get("MAX_PAGES_PER_SITE", "6"))
PAGE_CAPTURE_TIMEOUT_MS = int(os.environ.get("PAGE_CAPTURE_TIMEOUT_MS", "45000"))


@dataclass(slots=True)
class WebsiteCaptureResult:
    primary: ScreenshotArtifactRecord
    pages: list[PageScreenshotArtifactRecord]


def slug_for_path(page_path: str) -> str:
    if page_path == "/":
        return "home"
    slug = re.sub(r"[^a-z0-9]+", "-", page_path.strip("/").lower()).strip("-")
    return slug or "page"


def is_valid_page(page) -> bool:
    title = (page.title() or "").lower()
    if "404" in title or "not found" in title or "page introuvable" in title:
        return False
    try:
        response = page.evaluate(
            """
            () => {
              const body = document.body?.innerText?.toLowerCase() ?? '';
              if (body.includes('404') && body.includes('not found')) return false;
              return true;
            }
            """
        )
        return bool(response)
    except Exception:
        return True


class ScreenshotCaptureService:
    def __init__(self) -> None:
        self.storage = create_storage()

    def capture(self, website_id: str, url: str, source: str | None = None) -> ScreenshotArtifactRecord:
        result = self.capture_website_pages(website_id=website_id, url=url, source=source)
        return result.primary

    def capture_website_pages(
        self,
        website_id: str,
        url: str,
        source: str | None = None,
    ) -> WebsiteCaptureResult:
        capture_url = resolve_capture_url(url, source)
        page_artifacts: list[PageScreenshotArtifactRecord] = []
        primary_artifact: ScreenshotArtifactRecord | None = None

        with TemporaryDirectory(prefix="design-intelligence-pages-") as temp_dir:
            temp_dir_path = Path(temp_dir)

            def page_action(page) -> None:
                nonlocal primary_artifact
                page.set_viewport_size(DESKTOP_VIEWPORT)
                page.goto(capture_url, wait_until="networkidle", timeout=PAGE_CAPTURE_TIMEOUT_MS)

                discovered_pages = discover_pages_in_browser(page, capture_url, max_pages=MAX_PAGES_PER_SITE)
                if not discovered_pages:
                    discovered_pages = [
                        DiscoveredPage(page_url=capture_url, page_path="/", page_type="home", priority=0)
                    ]
                viewports = [
                    ("desktop", DESKTOP_VIEWPORT),
                    ("mobile", MOBILE_VIEWPORT),
                ]

                for discovered in discovered_pages:
                    for viewport_name, viewport_size in viewports:
                        artifact = self._capture_single_page(
                            page=page,
                            website_id=website_id,
                            discovered=discovered,
                            viewport_name=viewport_name,
                            viewport_size=viewport_size,
                            temp_dir_path=temp_dir_path,
                            catalog_url=url,
                        )
                        if artifact is None:
                            continue
                        page_artifacts.append(artifact)

                        if (
                            primary_artifact is None
                            and discovered.page_path == "/"
                            and viewport_name == "desktop"
                        ):
                            primary_artifact = self._to_primary_screenshot(artifact, page_count=len(discovered_pages))

            DynamicFetcher.fetch(
                capture_url,
                headless=True,
                network_idle=True,
                timeout=PAGE_CAPTURE_TIMEOUT_MS * max(2, MAX_PAGES_PER_SITE * 2),
                page_action=page_action,
                disable_resources=False,
            )

        if not page_artifacts:
            raise RuntimeError(f"No page screenshots were created for {capture_url}")

        if primary_artifact is None:
            primary_artifact = self._to_primary_screenshot(page_artifacts[0], page_count=max(1, len(page_artifacts) // 2))

        primary_artifact.metadata["pageScreenshotCount"] = len(page_artifacts)
        return WebsiteCaptureResult(primary=primary_artifact, pages=page_artifacts)

    def _capture_single_page(
        self,
        page,
        website_id: str,
        discovered: DiscoveredPage,
        viewport_name: str,
        viewport_size: dict[str, int],
        temp_dir_path: Path,
        catalog_url: str,
    ) -> PageScreenshotArtifactRecord | None:
        page.set_viewport_size(viewport_size)
        response = page.goto(discovered.page_url, wait_until="networkidle", timeout=PAGE_CAPTURE_TIMEOUT_MS)
        if response is not None and response.status >= 400 and discovered.page_path != "/":
            return None
        if discovered.page_path != "/" and not is_valid_page(page):
            return None
        page_title = page.title() or discovered.page_path

        slug = slug_for_path(discovered.page_path)
        screenshot_name = f"{slug}.png"
        thumbnail_name = f"{slug}-thumb.png"
        screenshot_path = temp_dir_path / viewport_name / screenshot_name
        thumbnail_path = temp_dir_path / viewport_name / thumbnail_name
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)

        page.screenshot(path=str(screenshot_path), full_page=False)

        if not screenshot_path.exists():
            raise RuntimeError(f"Screenshot was not created for {discovered.page_url} ({viewport_name})")

        with Image.open(screenshot_path) as image:
            width, height = image.size
            image.thumbnail((480, 900))
            image.save(thumbnail_path, format="PNG", optimize=True)

        screenshot_bytes = screenshot_path.read_bytes()
        checksum = hashlib.sha256(screenshot_bytes).hexdigest()

        remote_folder = f"PageScreenshots/{website_id}/{viewport_name}"
        thumb_folder = f"PageThumbnails/{website_id}/{viewport_name}"
        screenshot_upload = self.storage.upload_file(screenshot_path, remote_folder, screenshot_name)
        thumbnail_upload = self.storage.upload_file(thumbnail_path, thumb_folder, thumbnail_name)

        metadata: dict[str, Any] = {
            "sourceUrl": discovered.page_url,
            "catalogUrl": catalog_url,
            "storageMode": "local",
            "captureMode": "viewport",
            "viewport": viewport_name,
            "pagePath": discovered.page_path,
            "pageType": discovered.page_type,
        }

        return PageScreenshotArtifactRecord(
            website_id=website_id,
            page_url=discovered.page_url,
            page_path=discovered.page_path,
            page_title=page_title,
            page_type=discovered.page_type,
            viewport=viewport_name,
            viewport_width=viewport_size["width"],
            viewport_height=viewport_size["height"],
            screenshot_drive_file_id=screenshot_upload.file_id,
            screenshot_drive_url=screenshot_upload.web_url,
            thumbnail_drive_file_id=thumbnail_upload.file_id,
            thumbnail_drive_url=thumbnail_upload.web_url,
            width=width,
            height=height,
            checksum_sha256=checksum,
            metadata=metadata,
        )

    def _to_primary_screenshot(
        self,
        page_artifact: PageScreenshotArtifactRecord,
        page_count: int,
    ) -> ScreenshotArtifactRecord:
        website_id = page_artifact.website_id
        slug = slug_for_path(page_artifact.page_path)
        screenshot_name = f"{website_id}.png"
        thumbnail_name = f"{website_id}-thumb.png"

        screenshot_upload = self.storage.upload_file(
            Path(self.storage.root) / f"PageScreenshots/{website_id}/{page_artifact.viewport}/{slug}.png",
            "Screenshots",
            screenshot_name,
        )
        thumbnail_upload = self.storage.upload_file(
            Path(self.storage.root) / f"PageThumbnails/{website_id}/{page_artifact.viewport}/{slug}-thumb.png",
            "Thumbnails",
            thumbnail_name,
        )

        return ScreenshotArtifactRecord(
            website_id=website_id,
            screenshot_drive_file_id=screenshot_upload.file_id,
            screenshot_drive_url=screenshot_upload.web_url,
            thumbnail_drive_file_id=thumbnail_upload.file_id,
            thumbnail_drive_url=thumbnail_upload.web_url,
            width=page_artifact.width,
            height=page_artifact.height,
            checksum_sha256=page_artifact.checksum_sha256,
            metadata={
                **page_artifact.metadata,
                "primaryPagePath": page_artifact.page_path,
                "pageScreenshotCount": page_count * 2,
            },
        )
