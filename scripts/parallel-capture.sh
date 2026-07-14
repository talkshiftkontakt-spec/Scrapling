#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WORKERS="${1:-3}"
BATCH="${2:-3}"

set -a
source .env
set +a
export PATH="$HOME/.local/bin:$PATH"

for worker in $(seq 1 "$WORKERS"); do
  SESSION="capture-worker-${worker}"
  tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
  tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export PATH=\"\$HOME/.local/bin:\$PATH\" && while true; do python3 -m ingestion.scrapling.run capture --limit $BATCH || true; sleep 2; done" C-m
  echo "Started $SESSION"
done

SESSION="process-worker"
tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && while true; do npm run process:pending --workspace @design-intelligence/worker -- 20 || true; sleep 5; done" C-m
echo "Started $SESSION"
