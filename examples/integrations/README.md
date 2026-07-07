# Scrapling integrations for your projects

Ready-to-copy integrations connecting **Scrapling** with three repos from `talkshiftkontakt-spec`:

| Project | Folder | What it does |
|---------|--------|--------------|
| [OpenShorts](https://github.com/talkshiftkontakt-spec/openshorts) | `openshorts/` | Scrape product URLs before Gemini UGC script generation |
| [marketingskills](https://github.com/talkshiftkontakt-spec/marketingskills) | `marketingskills/` | Self-hosted competitor profiling (Firecrawl alternative) |
| [ai-website-cloner](https://github.com/talkshiftkontakt-spec/ai-website-cloner-template) | `ai-website-cloner/` | Preflight check before clone workflow |

## Apply to your forks

Each subfolder has **standalone files** plus a `patches/` directory with `git format-patch` output. Apply on branch `cursor/scrapling-integration-f0cc`:

```bash
# Example — OpenShorts
git clone https://github.com/talkshiftkontakt-spec/openshorts.git
cd openshorts
git checkout -b cursor/scrapling-integration-f0cc
git am /path/to/Scrapling/examples/integrations/openshorts/patches/*.patch
```

### 1. OpenShorts

Patches: `openshorts/patches/` (2 commits — Scrapling scraper + README note)

**Test:** `python scripts/test_scrapling_scrape.py https://www.lingology.pl`

### 2. marketingskills

Patches: `marketingskills/patches/` (2 commits — Scrapling skill + gitignore)

**Test:** `python scripts/scrape-competitor-scrapling.py https://www.lingology.pl --slug lingology`

### 3. ai-website-cloner

Patches: `ai-website-cloner/patches/` (1 commit — preflight script + docs)

**Test:** `python scripts/scrapling-preflight.py https://www.lingology.pl`

## Lingology / TutorApp promo flow (OpenShorts)

1. Deploy OpenShorts with Scrapling integration merged
2. Open **AI Shorts** → paste `https://www.lingology.pl` or TutorApp URL
3. Scrapling extracts copy → Gemini writes script → fal.ai renders video

## Dependencies

```bash
pip install "scrapling[fetchers]>=0.4.10"
scrapling install   # only for JS-heavy sites (DynamicFetcher)
```
