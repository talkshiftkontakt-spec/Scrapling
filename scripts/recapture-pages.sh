#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

set -a
# shellcheck disable=SC1091
source .env 2>/dev/null || true
set +a

LIMIT="${1:-10}"
STATUS="${2:-captured}"

export INGESTION_API_URL="${INGESTION_API_URL:-http://127.0.0.1:3101}"
export CAPTURE_MODE=viewport
export MAX_PAGES_PER_SITE="${MAX_PAGES_PER_SITE:-6}"

echo "Re-capturing per-page desktop/mobile screenshots (limit=$LIMIT, status=$STATUS)…"
python3 -m ingestion.scrapling.run recapture --limit "$LIMIT" --status "$STATUS"
