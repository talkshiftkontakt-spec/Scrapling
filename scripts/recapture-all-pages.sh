#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WORKERS="${1:-4}"
BATCH="${2:-2}"

set -a
# shellcheck disable=SC1091
source .env 2>/dev/null || true
set +a

export CAPTURE_MODE=viewport
export MAX_PAGES_PER_SITE="${MAX_PAGES_PER_SITE:-5}"
export INGESTION_API_URL="${INGESTION_API_URL:-http://127.0.0.1:3101}"

for worker in $(seq 1 "$WORKERS"); do
  SESSION="page-capture-worker-${worker}"
  tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
  tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export CAPTURE_MODE=viewport MAX_PAGES_PER_SITE=5 && while true; do python3 -m ingestion.scrapling.run recapture-missing --limit $BATCH || true; sleep 3; done" C-m
  echo "Started $SESSION"
done

echo "Page capture workers running. Check: tmux -f /exec-daemon/tmux.portal.conf ls"
