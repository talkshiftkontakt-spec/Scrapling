from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from scrapling.fetchers import DynamicFetcher

from ingestion.scrapling.contracts import ScreenshotArtifactRecord
from ingestion.scrapling.drive import GoogleDriveStorage


class ScreenshotCaptureService:
    def __init__(self, drive_storage: GoogleDriveStorage | None = None) -> None:
        self.drive_storage = drive_storage or GoogleDriveStorage()

    def capture(self, website_id: str, url: str) -> ScreenshotArtifactRecord:
        with TemporaryDirectory(prefix="design-intelligence-") as temp_dir:
            temp_dir_path = Path(temp_dir)
            screenshot_path = temp_dir_path / "screenshot.png"
            thumbnail_path = temp_dir_path / "thumbnail.png"
            captured: dict[str, int] = {"width": 1440, "height": 4000}

            def page_action(page) -> None:
                page.set_viewport_size({"width": 1440, "height": 1600})
                page.evaluate(
                    """
                    async () => {
                      await new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 600;
                        const timer = setInterval(() => {
                          const scrollHeight = document.body.scrollHeight;
                          window.scrollBy(0, distance);
                          totalHeight += distance;
                          if (totalHeight >= scrollHeight) {
                            clearInterval(timer);
                            resolve();
                          }
                        }, 150);
                      });
                    }
                    """
                )
                page.screenshot(path=str(screenshot_path), full_page=True)

            DynamicFetcher.fetch(
                url,
                headless=True,
                network_idle=True,
                timeout=45000,
                page_action=page_action,
                disable_resources=False,
            )

            screenshot_bytes = screenshot_path.read_bytes()
            thumbnail_path.write_bytes(screenshot_bytes)
            checksum = hashlib.sha256(screenshot_bytes).hexdigest()
            screenshot_upload = self.drive_storage.upload_file(screenshot_path, "Screenshots")
            thumbnail_upload = self.drive_storage.upload_file(thumbnail_path, "Thumbnails")

            return ScreenshotArtifactRecord(
                website_id=website_id,
                screenshot_drive_file_id=screenshot_upload.file_id,
                screenshot_drive_url=screenshot_upload.web_url,
                thumbnail_drive_file_id=thumbnail_upload.file_id,
                thumbnail_drive_url=thumbnail_upload.web_url,
                width=captured["width"],
                height=captured["height"],
                checksum_sha256=checksum,
                metadata={"sourceUrl": url},
            )
