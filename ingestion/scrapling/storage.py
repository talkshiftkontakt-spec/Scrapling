from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class UploadResult:
    file_id: str
    web_url: str


class LocalAssetStorage:
    def __init__(self, root: str | Path, static_base_url: str) -> None:
        self.root = Path(root)
        self.static_base_url = static_base_url.rstrip("/")

    def upload_file(self, file_path: Path, remote_folder: str, filename: str | None = None) -> UploadResult:
        folder = remote_folder.strip("/")
        destination_dir = self.root / folder
        destination_dir.mkdir(parents=True, exist_ok=True)
        target_name = filename or file_path.name
        destination = destination_dir / target_name
        shutil.copy2(file_path, destination)
        file_id = f"local:{folder}/{target_name}"
        web_url = f"{self.static_base_url}/{folder}/{target_name}"
        return UploadResult(file_id=file_id, web_url=web_url)


def create_storage() -> LocalAssetStorage:
    root = os.environ.get("DESIGN_LIBRARY_PATH", "./DesignLibrary")
    static_base = os.environ.get("STATIC_BASE_URL", "http://127.0.0.1:3001/static")
    return LocalAssetStorage(root=root, static_base_url=static_base)
