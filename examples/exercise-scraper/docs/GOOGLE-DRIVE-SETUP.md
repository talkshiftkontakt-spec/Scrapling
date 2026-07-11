# Google Drive setup

Sync uploads each completed topic folder to Google Drive under:

```
<GOOGLE_DRIVE_ROOT_FOLDER_ID>/
└── grammar/
    └── <level>/
        └── <topic_id>/
            ├── exercises.json
            ├── exercises_validated.json
            └── ...
```

## 1. Create a Google Cloud project

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (e.g. `grammar-corpus`)
3. Enable **Google Drive API**

## 2. Service account (recommended for server/CLI)

1. **IAM & Admin → Service accounts → Create**
2. Create a JSON key and download it
3. Share your Drive root folder with the service account email (`...@....iam.gserviceaccount.com`) as **Editor**

## 3. Environment variables

```bash
pip install -e "examples/exercise-scraper[drive]"

export GOOGLE_DRIVE_ROOT_FOLDER_ID="your_folder_id_from_drive_url"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

Alternative (inline JSON, e.g. cloud deploy):

```bash
export GOOGLE_DRIVE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

## 4. Find folder ID

Open the folder in Google Drive. The URL looks like:

```
https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz
```

Use `1AbCdEfGhIjKlMnOpQrStUvWxYz` as `GOOGLE_DRIVE_ROOT_FOLDER_ID`.

## 5. Run with sync

**CLI:**

```bash
exercise-scraper corpus run-topic past-simple --sync-drive
```

**UI:** enable **Sync Google Drive** on `/corpus` or the search form.

**API:** `"sync_drive": true` in `POST /api/corpus/topics/{id}/run`.

## 6. Verify status

```bash
curl http://localhost:8000/api/drive/status
```

Or check the Drive status banner in the web UI on `/corpus`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Drive not configured` | Set both `GOOGLE_DRIVE_ROOT_FOLDER_ID` and credentials |
| `Install drive extras` | `pip install -e "examples/exercise-scraper[drive]"` |
| `403` / file not found | Share the root folder with the service account email |
| Upload succeeds but folder empty | Check `drive_sync.json` in the local topic output folder |
