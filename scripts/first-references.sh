#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

set -a
source .env
set +a

echo "==> Starting Postgres + Qdrant"
docker compose up -d

echo "==> Installing Node dependencies"
npm install

echo "==> Running database migrations"
npm run db:migrate --workspace @design-intelligence/database

echo "==> Building platform"
npm run build

echo "==> Installing Python ingestion dependencies"
python3 -m pip install -r ingestion/requirements.txt
python3 -m pip install -e ".[fetchers]"
scrapling install || true

mkdir -p "$DESIGN_LIBRARY_PATH/Screenshots" "$DESIGN_LIBRARY_PATH/Thumbnails"

cat <<'EOF'

Next steps (3 terminals):

Terminal 1 — API:
  set -a && source .env && set +a && npm run dev:api

Terminal 2 — Discover + capture:
  set -a && source .env && set +a
  python3 -m ingestion.scrapling.run discover --limit 30
  python3 -m ingestion.scrapling.run capture --limit 10

Terminal 3 — Analyze + score:
  set -a && source .env && set +a
  npm run process:pending --workspace @design-intelligence/worker -- 10

View accepted references:
  curl "http://127.0.0.1:3001/references?status=accepted&limit=20"

EOF
