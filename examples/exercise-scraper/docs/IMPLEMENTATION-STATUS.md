# Implementation status vs multi-agent plan

Last updated: 2026-07-11

## Done in this branch

| Phase | Item | Status |
|-------|------|--------|
| 0 | CLI + API + UI | ✅ |
| 0 | Basic validator + top N | ✅ |
| 0 | Configurable `--top-n` / API `top_exercises` | ✅ |
| 0 | Save rejected exercises (`exercises_rejected.json`) | ✅ |
| 0 | Stronger junk/nav filtering | ✅ |
| 1 | `config/grammar_taxonomy.yaml` (20 topics) | ✅ |
| 1 | Corpus folder layout `grammar-corpus/grammar/<level>/<topic>/` | ✅ |
| 1 | Topic validators: **all 19** registered for 20 taxonomy topics | ✅ |
| 1 | Validation pipeline + `validation_report.json` | ✅ |
| 2 | `config/domain_rules.yaml` (9 domains) | ✅ |
| 2 | Domain-aware extraction in spider | ✅ |
| 2 | Corpus orchestrator (`corpus run-topic`, `run-all`) | ✅ |
| 2 | API: `GET /api/corpus/topics`, `POST .../run`, `POST /api/corpus/run-all` | ✅ |
| 3 | Google Drive sync module (`drive/sync.py`, `--sync-drive`) | ✅ |
| 3 | `GET /api/drive/status` + setup doc + UI banner | ✅ |
| 4 | `config/dictionary_taxonomy.yaml` + wordlists A1/A2/B1 | ✅ |
| 4 | Dictionary scraper (`dictionary/` package) | ✅ |
| 4 | API `GET/POST /api/dictionary/tracks` | ✅ |
| 4 | UI `/dictionary` — słówka | ✅ |
| 2 | Grammar categories: tenses (8) + structures (12) | ✅ |
| 2 | Corpus index dedup (`corpus/index.py`) | ✅ |
| 9 | Tests (**32** passing) | ✅ |
| 9 | Frontend corpus UI (`/corpus`) | ✅ |

## Web UI

- **`/`** — wyszukiwanie z opcjonalnym `topic_id`, top N, Google Drive
- **`/corpus`** — czasy (8) i struktury (12), batch, postęp
- **`/dictionary`** — słówka A1/A2/B1, ćwiczenia leksykalne
- **`/jobs/[id]`** — szczegóły zadania, źródła, ćwiczenia

## Output files per topic run

```
grammar-corpus/grammar/A2/past-simple/
├── exercises.json              # top N (backward compatible)
├── exercises_top3.json         # same as above, explicit name
├── exercises_validated.json    # all passed validation
├── exercises_rejected.json     # failed validation
├── validation_report.json
├── sources.json
├── manifest.json
├── report.txt
└── pages/
```

## CLI quick reference

```bash
# Single topic with taxonomy + validators
exercise-scraper scrape "Past Simple" --topic-id past-simple --top-n 3

# List taxonomy
exercise-scraper corpus topics

# One corpus topic
exercise-scraper corpus run-topic past-simple --top-n 5

# Batch (use low --max-pages)
exercise-scraper corpus run-all --limit 3 --max-pages 5

# Google Drive (after setting env vars)
exercise-scraper corpus run-topic past-simple --sync-drive
```

## Google Drive

See **[GOOGLE-DRIVE-SETUP.md](GOOGLE-DRIVE-SETUP.md)**. Status endpoint: `GET /api/drive/status`. UI shows a banner when not configured.

```bash
export GOOGLE_DRIVE_ROOT_FOLDER_ID=your_folder_id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
pip install -e "examples/exercise-scraper[drive]"
```

## Still to add (next)

| Priority | Item |
|----------|------|
| Low | LLM validator for edge cases |
| Low | PDF exercise extraction |
| Low | Export to Google Sheets |
| Low | Rozszerzyć listy słówek (C1/C2) |
