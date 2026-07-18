# Szafapilot Visual Design Research

Pure visual/UI research corpus produced with Scrapling (no copywriting, no redesign).

## Primary deliverable

- [`VISUAL_DESIGN_RESEARCH.md`](./VISUAL_DESIGN_RESEARCH.md) — full report, pattern library, trends, and five visual directions

## Data

| Path | Contents |
|---|---|
| `screenshots/` | Compressed JPEG viewport + full-page captures for 30 sites |
| `raw/` | Per-site design-token JSON |
| `crawl-summary.json` | Crawl success matrix |
| `design-token-aggregate.json` | Cross-site font/theme/H1/radius aggregate |
| `crawl_visual_research.py` | Scrapling crawler used for this study |

## Reproduce

```bash
pip install -e ".[fetchers]"
scrapling install --force
cd research/szafapilot-visual-design
python3 crawl_visual_research.py
```
