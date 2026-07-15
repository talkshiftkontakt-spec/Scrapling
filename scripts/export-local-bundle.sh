#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="${ROOT}/export"
STAMP="$(date +%Y%m%d-%H%M%S)"
BUNDLE="${EXPORT_DIR}/design-bundle-${STAMP}.tar.gz"

mkdir -p "${EXPORT_DIR}"

echo "==> Dumping PostgreSQL..."
pg_dump "${DATABASE_URL:?DATABASE_URL is required}" --no-owner --no-acl \
  -f "${EXPORT_DIR}/design_intelligence.sql"

echo "==> Writing manifest..."
{
  echo "created_at=${STAMP}"
  echo "branch=$(git -C "${ROOT}" branch --show-current 2>/dev/null || echo unknown)"
  echo "commit=$(git -C "${ROOT}" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "page_screenshots=$(find "${ROOT}/DesignLibrary/PageScreenshots" -name '*.png' 2>/dev/null | wc -l | tr -d ' ')"
  echo "design_library_bytes=$(du -sb "${ROOT}/DesignLibrary" 2>/dev/null | cut -f1)"
} > "${EXPORT_DIR}/manifest.txt"

echo "==> Creating archive (this can take several minutes)..."
tar --warning=no-file-changed -czf "${BUNDLE}" \
  -C "${ROOT}" \
  DesignLibrary \
  export/design_intelligence.sql \
  export/manifest.txt \
  .env.example || [[ -f "${BUNDLE}" ]]

ln -sfn "$(basename "${BUNDLE}")" "${EXPORT_DIR}/design-bundle-latest.tar.gz"

echo ""
echo "Bundle ready:"
ls -lh "${BUNDLE}"
echo ""
echo "Download from the cloud agent, then on your computer:"
echo "  mkdir -p ~/design && cd ~/design"
echo "  git clone -b cursor/design-intelligence-platform-0f66 https://github.com/talkshiftkontakt-spec/scrapling.git ."
echo "  tar -xzf /path/to/$(basename "${BUNDLE}")"
echo "  cp .env.example .env"
echo "  bash scripts/setup-local-from-bundle.sh"
