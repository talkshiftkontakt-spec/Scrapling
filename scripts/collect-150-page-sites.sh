#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TARGET="${1:-150}"
WORKERS="${2:-12}"
BATCH="${3:-3}"

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

needs_pages_count() {
  psql "$DATABASE_URL" -tAc "
    SELECT COUNT(*) FROM websites w
    JOIN screenshots s ON s.website_id = w.id
    WHERE NOT EXISTS (SELECT 1 FROM page_screenshots ps WHERE ps.website_id = w.id)
      AND COALESCE((w.metadata->>'pageCaptureFailures')::int, 0) < 3
      AND w.processing_status IN ('captured', 'accepted', 'analyzed');
  "
}

pending_capture_count() {
  curl -sf "${INGESTION_API_URL}/ingestion/pending-capture?limit=250" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
}

discovered_count() {
  curl -sf "${INGESTION_API_URL}/stats" | python3 -c "import json,sys; print(json.load(sys.stdin).get('discovered', 0))"
}

echo "==> Target: ${TARGET} websites with per-page screenshots"
echo "==> Current: $(page_sites_count) sites, $(page_shots_count) total page shots"

# Start parallel page-capture workers
for worker in $(seq 1 "$WORKERS"); do
  SESSION="page-capture-worker-${worker}"
  tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
  tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export CAPTURE_MODE=viewport MAX_PAGES_PER_SITE=6 PAGE_CAPTURE_TIMEOUT_MS=60000 && while true; do python3 -m ingestion.scrapling.run recapture-missing --limit $BATCH || true; sleep 1; done" C-m
done

# Capture worker for newly discovered sites (per-page from first capture)
SESSION="new-site-capture-worker"
tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export CAPTURE_MODE=viewport MAX_PAGES_PER_SITE=6 && while true; do python3 -m ingestion.scrapling.run capture --limit 2 || true; sleep 2; done" C-m

echo "==> Started ${WORKERS} recapture workers + 1 new-site capture worker"

while [ "$(page_sites_count)" -lt "$TARGET" ]; do
  current="$(page_sites_count)"
  shots="$(page_shots_count)"
  needs="$(needs_pages_count)"
  pending="$(pending_capture_count)"
  discovered="$(discovered_count)"

  echo "==> Progress: ${current}/${TARGET} sites | ${shots} shots | ${needs} legacy need pages | ${pending} pending capture | ${discovered} discovered"

  if [ "$pending" -lt 15 ] && [ "$discovered" -lt 30 ]; then
    echo "==> Discovering more websites..."
    python3 -m ingestion.scrapling.run discover --limit 80 || true
  fi

  if [ "$needs" -eq 0 ] && [ "$pending" -eq 0 ] && [ "$discovered" -lt 5 ]; then
    echo "==> Discovering additional batch..."
    python3 -m ingestion.scrapling.run discover --limit 100 || true
    if [ "$(pending_capture_count)" -eq 0 ]; then
      echo "==> No more sites available from providers"
      break
    fi
  fi

  sleep 60
done

echo "==> Finished: $(page_sites_count) sites with page screenshots, $(page_shots_count) total shots"
psql "$DATABASE_URL" -c "SELECT COUNT(DISTINCT website_id) AS sites, COUNT(*) AS shots FROM page_screenshots;"
