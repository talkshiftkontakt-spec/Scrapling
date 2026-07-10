from __future__ import annotations

import hashlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from scrapling.fetchers import DynamicFetcher

from ingestion.scrapling.contracts import ScreenshotArtifactRecord
from ingestion.scrapling.storage import create_storage
from ingestion.scrapling.url_resolver import resolve_capture_url

# Full-page design screenshots can exceed Pillow's default bomb threshold.
Image.MAX_IMAGE_PIXELS = 300_000_000

MAX_CAPTURE_HEIGHT_PX = 14_000
VIEWPORT_CAPTURE = os.environ.get("CAPTURE_MODE", "viewport").lower() != "fullpage"


class ScreenshotCaptureService:
    def __init__(self) -> None:
        self.storage = create_storage()

    def capture(self, website_id: str, url: str, source: str | None = None) -> ScreenshotArtifactRecord:
        capture_url = resolve_capture_url(url, source)
        with TemporaryDirectory(prefix="design-intelligence-") as temp_dir:
            temp_dir_path = Path(temp_dir)
            screenshot_path = temp_dir_path / f"{website_id}.png"
            thumbnail_path = temp_dir_path / f"{website_id}-thumb.png"
            dimensions = {"width": 1440, "height": 900}

            def page_action(page) -> None:
                page.set_viewport_size({"width": 1440, "height": 900})
                if VIEWPORT_CAPTURE:
                    page.screenshot(path=str(screenshot_path), full_page=False)
                    return

                page.evaluate(
                    f"""
                    async () => {{
                      const maxHeight = {MAX_CAPTURE_HEIGHT_PX};
                      await new Promise((resolve) => {{
                        let totalHeight = 0;
                        const distance = 800;
                        const timer = setInterval(() => {{
                          const scrollHeight = Math.min(document.body.scrollHeight, maxHeight);
                          window.scrollBy(0, distance);
                          totalHeight += distance;
                          if (totalHeight >= scrollHeight) {{
                            clearInterval(timer);
                            resolve();
                          }}
                        }}, 100);
                      }});
                    }}
                    """
                )
                page.screenshot(path=str(screenshot_path), full_page=True)

            DynamicFetcher.fetch(
                capture_url,
                headless=True,
                network_idle=True,
                timeout=30000,
                page_action=page_action,
                disable_resources=False,
            )

            if not screenshot_path.exists():
                raise RuntimeError(f"Screenshot was not created for {capture_url}")

            with Image.open(screenshot_path) as image:
                dimensions["width"], dimensions["height"] = image.size
                image.thumbnail((480, 1200))
                image.save(thumbnail_path, format="PNG", optimize=True)

            screenshot_bytes = screenshot_path.read_bytes()
            checksum = hashlib.sha256(screenshot_bytes).hexdigest()
            screenshot_upload = self.storage.upload_file(screenshot_path, "Screenshots", f"{website_id}.png")
            thumbnail_upload = self.storage.upload_file(thumbnail_path, "Thumbnails", f"{website_id}-thumb.png")

            return ScreenshotArtifactRecord(
                website_id=website_id,
                screenshot_drive_file_id=screenshot_upload.file_id,
                screenshot_drive_url=screenshot_upload.web_url,
                thumbnail_drive_file_id=thumbnail_upload.file_id,
                thumbnail_drive_url=thumbnail_upload.web_url,
                width=dimensions["width"],
                height=dimensions["height"],
                checksum_sha256=checksum,
                metadata={"sourceUrl": capture_url, "catalogUrl": url, "storageMode": "local"},
            )
