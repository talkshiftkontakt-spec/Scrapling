from __future__ import annotations

import json
import os
from pathlib import Path

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def drive_configured() -> bool:
    return bool(
        os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
        and (
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON")
        )
    )


def upload_topic_folder(local_dir: Path, *, topic_id: str, level: str) -> dict:
    """Upload a local topic folder to Google Drive under grammar/<level>/<topic_id>/."""
    if not drive_configured():
        return {
            "uploaded": False,
            "reason": "Drive not configured. Set GOOGLE_DRIVE_ROOT_FOLDER_ID and credentials.",
        }

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        return {
            "uploaded": False,
            "reason": "Install drive extras: pip install exercise-scraper[drive]",
            "error": str(exc),
        }

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON")
    if creds_json and not creds_path:
        creds_path = str(local_dir.parent / ".drive_credentials.json")
        Path(creds_path).write_text(creds_json, encoding="utf-8")

    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=DRIVE_SCOPES,
    )
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    root_id = os.environ["GOOGLE_DRIVE_ROOT_FOLDER_ID"]

    grammar_id = _ensure_folder(service, root_id, "grammar")
    level_id = _ensure_folder(service, grammar_id, level)
    topic_folder_id = _ensure_folder(service, level_id, topic_id)

    uploaded_files: list[dict[str, str]] = []
    for path in sorted(local_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        rel = path.relative_to(local_dir).as_posix()
        media = MediaFileUpload(str(path), resumable=True)
        metadata = {"name": path.name, "parents": [topic_folder_id]}
        existing = _find_child_by_name(service, topic_folder_id, path.name)
        if existing:
            file = (
                service.files()
                .update(fileId=existing, media_body=media, fields="id, webViewLink")
                .execute()
            )
        else:
            file = service.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
        uploaded_files.append({"path": rel, "file_id": file["id"], "url": file.get("webViewLink", "")})

    manifest = {
        "uploaded": True,
        "topic_id": topic_id,
        "level": level,
        "drive_folder_id": topic_folder_id,
        "files": uploaded_files,
    }
    manifest_path = local_dir / "drive_sync.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _ensure_folder(service, parent_id: str, name: str) -> str:
    existing = _find_child_by_name(service, parent_id, name)
    if existing:
        return existing
    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def _find_child_by_name(service, parent_id: str, name: str) -> str | None:
    query = (
        f"name = '{name.replace(chr(39), '')}' and '{parent_id}' in parents and trashed = false"
    )
    response = service.files().list(q=query, fields="files(id)", pageSize=1).execute()
    files = response.get("files", [])
    return files[0]["id"] if files else None
