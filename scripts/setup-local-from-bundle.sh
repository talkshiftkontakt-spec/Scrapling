#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "==> Starting PostgreSQL (Docker)..."
docker compose up -d postgres

echo "==> Waiting for database..."
for _ in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U design -d design_intelligence >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "==> Running migrations..."
npm run db:migrate

if [[ -f export/design_intelligence.sql ]]; then
  echo "==> Restoring database snapshot..."
  docker compose exec -T postgres psql -U design -d design_intelligence < export/design_intelligence.sql
else
  echo "No export/design_intelligence.sql found — skipping restore."
fi

echo "==> Installing dependencies..."
npm install

echo "==> Building database package..."
npm run build --workspace @design-intelligence/database

echo ""
echo "Local setup complete."
echo "  API:       npm run dev:api        -> http://localhost:3101"
echo "  Dashboard: npm run dev:dashboard  -> http://localhost:3100"
echo ""
if [[ -d DesignLibrary/PageScreenshots ]]; then
  SHOTS="$(find DesignLibrary/PageScreenshots -name '*.png' | wc -l | tr -d ' ')"
  echo "Screenshots on disk: ${SHOTS} PNG files under DesignLibrary/PageScreenshots/"
else
  echo "No DesignLibrary yet — run capture workers or import a bundle archive."
fi
