#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="${1:-100}"
DISCOVER_BATCH="${DISCOVER_BATCH:-120}"
CAPTURE_BATCH="${CAPTURE_BATCH:-10}"

set -a
source .env
set +a
export PATH="$HOME/.local/bin:$PATH"

accepted_count() {
  curl -sf "http://127.0.0.1:${PORT:-3001}/stats" | python3 -c "import json,sys; print(json.load(sys.stdin).get('accepted', 0))"
}

pending_capture_count() {
  curl -sf "http://127.0.0.1:${PORT:-3001}/ingestion/pending-capture?limit=1" | python3 -c "import json,sys; data=json.load(sys.stdin); print(len(data))"
}

echo "==> Target: ${TARGET} accepted references"

current="$(accepted_count)"
echo "==> Current accepted: ${current}"

if [ "$current" -lt "$TARGET" ]; then
  echo "==> Discovering up to ${DISCOVER_BATCH} websites"
  python3 -m ingestion.scrapling.run discover --limit "$DISCOVER_BATCH"
fi

while [ "$(accepted_count)" -lt "$TARGET" ]; do
  pending="$(pending_capture_count)"
  if [ "$pending" -eq 0 ]; then
    echo "==> No pending captures left; discovering more"
    python3 -m ingestion.scrapling.run discover --limit "$DISCOVER_BATCH"
    pending="$(pending_capture_count)"
    if [ "$pending" -eq 0 ]; then
      echo "==> Discovery returned no new pending websites; stopping"
      break
    fi
  fi

  echo "==> Capturing batch (${CAPTURE_BATCH}) | accepted $(accepted_count)/${TARGET}"
  python3 -m ingestion.scrapling.run capture --limit "$CAPTURE_BATCH" || true

  echo "==> Processing batch (${CAPTURE_BATCH})"
  npm run process:pending --workspace @design-intelligence/worker -- "$CAPTURE_BATCH" || true

  current="$(accepted_count)"
  echo "==> Progress: ${current}/${TARGET} accepted"
done

echo "==> Done"
curl -sf "http://127.0.0.1:${PORT:-3001}/stats"
echo
