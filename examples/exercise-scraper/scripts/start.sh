#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! python3 -c "import uvicorn, fastapi" 2>/dev/null; then
  echo "Brak zależności API. Uruchom:"
  echo "  pip install -e . && pip install -e \"examples/exercise-scraper[api]\""
  exit 1
fi

if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "Brak node_modules. Uruchom:"
  echo "  cd examples/exercise-scraper/frontend && npm install"
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export API_URL="${API_URL:-http://127.0.0.1:8000}"

echo "Uruchamiam API na porcie 8000..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

sleep 1
if ! curl -sf http://127.0.0.1:8000/api/health >/dev/null; then
  echo "API nie wystartowało. Sprawdź logi powyżej."
  exit 1
fi

echo "Uruchamiam UI na porcie 3000..."
cd "$ROOT/frontend"
exec npm run dev -- --hostname 0.0.0.0 --port 3000
