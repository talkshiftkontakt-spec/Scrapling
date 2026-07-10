# Implementation status vs multi-agent plan

Last updated: 2026-07-10

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
| 1 | Topic validators: `past_simple`, `present_perfect` + generic fallback | ✅ |
| 1 | Validation pipeline + `validation_report.json` | ✅ |
| 2 | `config/domain_rules.yaml` (9 domains) | ✅ |
| 2 | Domain-aware extraction in spider | ✅ |
| 2 | Corpus orchestrator (`corpus run-topic`, `run-all`) | ✅ |
| 2 | API: `GET /api/corpus/topics`, `POST .../run`, `POST /api/corpus/run-all` | ✅ |
| 3 | Google Drive sync module (`drive/sync.py`, `--sync-drive`) | ✅ (needs credentials) |
| 4 | `config/dictionary_taxonomy.yaml` stub | ✅ |
| 9 | Tests (21 passing) | ✅ |
| 9 | Frontend corpus UI (`/corpus`) | ✅ |

## Web UI

- **`/`** — wyszukiwanie z opcjonalnym `topic_id`, top N, Google Drive
- **`/corpus`** — siatka 20 tematów, batch, śledzenie postępu
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

## Google Drive env vars

```bash
export GOOGLE_DRIVE_ROOT_FOLDER_ID=your_folder_id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
pip install -e "examples/exercise-scraper[drive]"
```

## Still to add (next)

| Priority | Item |
|----------|------|
| High | More topic validators (present_continuous, articles, modals, …) |
| High | Frontend UI for corpus topics + batch run |
| Medium | SQLite corpus index (topic, hash, score) across runs |
| Medium | Cross-crawl dedup in batch mode |
| Medium | Dictionary scraper package (separate from grammar) |
| Low | LLM validator for edge cases |
| Low | PDF exercise extraction |
| Low | Export to Google Sheets |
