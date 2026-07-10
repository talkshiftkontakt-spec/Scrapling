from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DriveUploadResult:
    file_id: str
    web_url: str


class GoogleDriveStorage:
    """Thin placeholder around Google Drive upload flow.

    The implementation is intentionally dependency-light in this repository state.
    Integrators should wire it to a service account or OAuth flow before production use.
    """

    def __init__(self, root_folder: str = "DesignLibrary") -> None:
        self.root_folder = root_folder

    def upload_file(self, file_path: Path, remote_folder: str) -> DriveUploadResult:
        normalized_folder = remote_folder.strip("/")
        file_id = f"{normalized_folder}:{file_path.name}"
        web_url = f"https://drive.google.com/file/d/{file_id}/view"
        return DriveUploadResult(file_id=file_id, web_url=web_url)
