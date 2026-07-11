#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TARGET="${1:-500}"
WORKERS="${2:-40}"
BATCH="${3:-2}"
NEW_SITE_WORKERS="${4:-16}"
DISCOVER_WORKERS="${5:-6}"

set -a
# shellcheck disable=SC1091
source .env 2>/dev/null || true
set +a

export CAPTURE_MODE=viewport
export MAX_PAGES_PER_SITE="${MAX_PAGES_PER_SITE:-6}"
export PAGE_CAPTURE_TIMEOUT_MS="${PAGE_CAPTURE_TIMEOUT_MS:-60000}"
export INGESTION_API_URL="${INGESTION_API_URL:-http://127.0.0.1:3101}"
export PATH="${HOME}/.local/bin:${PATH}"

page_sites_count() {
  psql "$DATABASE_URL" -tAc "SELECT COUNT(DISTINCT website_id) FROM page_screenshots;"
}

page_shots_count() {
  psql "$DATABASE_URL" -tAc "SELECT COUNT(*) FROM page_screenshots;"
}

pending_capture_count() {
  curl -sf "${INGESTION_API_URL}/ingestion/pending-capture?limit=500" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
}

total_websites_count() {
  psql "$DATABASE_URL" -tAc "SELECT COUNT(*) FROM websites;"
}

echo "==> Target: ${TARGET} websites with per-page screenshots"
echo "==> Current: $(page_sites_count) sites | $(page_shots_count) shots | $(total_websites_count) total websites in DB"

# Scale workers
bash "$ROOT/scripts/scale-scrape-workers.sh" "$WORKERS" "$BATCH" "$NEW_SITE_WORKERS" "$DISCOVER_WORKERS"

echo "==> Bulk discover kickoff (up to 400 new sites)"
python3 -m ingestion.scrapling.run discover --limit 400 || true

while [ "$(page_sites_count)" -lt "$TARGET" ]; do
  current="$(page_sites_count)"
  shots="$(page_shots_count)"
  pending="$(pending_capture_count)"
  total="$(total_websites_count)"
  gap=$((TARGET - current))

  echo "==> Progress: ${current}/${TARGET} page sites | ${shots} shots | ${pending} pending capture | ${total} websites in DB | need ${gap} more"

  if [ "$pending" -lt 20 ]; then
    discover_batch=$((gap < 150 ? gap + 50 : 200))
    echo "==> Discovering ${discover_batch} more websites..."
    python3 -m ingestion.scrapling.run discover --limit "$discover_batch" || true
    pending="$(pending_capture_count)"
    if [ "$pending" -eq 0 ] && [ "$total" -lt "$((TARGET + 50))" ]; then
      echo "==> Providers exhausted at ${total} websites — trying another discover pass"
      python3 -m ingestion.scrapling.run discover --limit 300 || true
    fi
    if [ "$pending" -eq 0 ] && [ "$(page_sites_count)" -ge "$((TARGET - 5))" ]; then
      echo "==> Near target and no pending captures — done"
      break
    fi
    if [ "$pending" -eq 0 ] && [ "$(total_websites_count)" -eq "$total" ]; then
      sleep 120
      pending="$(pending_capture_count)"
      if [ "$pending" -eq 0 ]; then
        echo "==> No new sites discovered — stopping orchestrator"
        break
      fi
    fi
  fi

  sleep 45
done

echo "==> Finished: $(page_sites_count) sites | $(page_shots_count) shots"
psql "$DATABASE_URL" -c "SELECT COUNT(DISTINCT website_id) AS sites, COUNT(*) AS shots FROM page_screenshots;"
