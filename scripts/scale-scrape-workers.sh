#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WORKERS="${1:-28}"
BATCH="${2:-2}"
NEW_SITE_WORKERS="${3:-6}"
DISCOVER_WORKERS="${4:-2}"

set -a
# shellcheck disable=SC1091
source .env 2>/dev/null || true
set +a

export CAPTURE_MODE=viewport
export MAX_PAGES_PER_SITE="${MAX_PAGES_PER_SITE:-6}"
export PAGE_CAPTURE_TIMEOUT_MS="${PAGE_CAPTURE_TIMEOUT_MS:-60000}"
export INGESTION_API_URL="${INGESTION_API_URL:-http://127.0.0.1:3101}"
export PATH="${HOME}/.local/bin:${PATH}"

echo "==> Scaling to ${WORKERS} page-recapture workers (batch ${BATCH})"

for worker in $(seq 1 "$WORKERS"); do
  SESSION="page-capture-worker-${worker}"
  tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
  tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export CAPTURE_MODE=viewport MAX_PAGES_PER_SITE=6 PAGE_CAPTURE_TIMEOUT_MS=60000 && while true; do python3 -m ingestion.scrapling.run recapture-missing --limit $BATCH || true; sleep 1; done" C-m
done

for worker in $(seq 1 "$NEW_SITE_WORKERS"); do
  SESSION="new-site-capture-worker-${worker}"
  tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
  tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export CAPTURE_MODE=viewport MAX_PAGES_PER_SITE=6 && while true; do python3 -m ingestion.scrapling.run capture --limit 1 || true; sleep 2; done" C-m
done

for worker in $(seq 1 "$DISCOVER_WORKERS"); do
  SESSION="discover-worker-${worker}"
  tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
  tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && while true; do python3 -m ingestion.scrapling.run discover --limit 50 --provider landbook || true; python3 -m ingestion.scrapling.run discover --limit 30 --provider awwwards || true; sleep 20; done" C-m
done

# Legacy single worker name cleanup
tmux -f /exec-daemon/tmux.portal.conf kill-session -t new-site-capture-worker 2>/dev/null || true

echo "==> Started ${WORKERS} recapture + ${NEW_SITE_WORKERS} new-site + ${DISCOVER_WORKERS} discover workers"
tmux -f /exec-daemon/tmux.portal.conf ls | rg "page-capture|new-site|discover-worker" | wc -l
