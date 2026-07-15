#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LIMIT="${1:-150}"
WORKERS="${2:-4}"

set -a
source .env
set +a
export PATH="$HOME/.local/bin:$PATH"
export CAPTURE_MODE=fullpage

echo "==> Re-capturing up to ${LIMIT} references as FULL PAGE screenshots"
echo "==> CAPTURE_MODE=${CAPTURE_MODE}"

SESSION="recapture-fullpage"
tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-zsh}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION:0.0" "cd $ROOT && set -a && source .env && set +a && export PATH=\"\$HOME/.local/bin:\$PATH\" && export CAPTURE_MODE=fullpage && python3 -m ingestion.scrapling.run recapture --limit $LIMIT --status accepted 2>&1 | tee /tmp/recapture-fullpage.log" C-m

echo "==> Recapture running in tmux session: $SESSION"
echo "==> Log: /tmp/recapture-fullpage.log"
echo "==> Tail: tail -f /tmp/recapture-fullpage.log"
