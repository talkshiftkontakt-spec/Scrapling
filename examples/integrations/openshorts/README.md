# Scrapling + OpenShorts

SaaSShorts (AI UGC videos) uses **Scrapling** to scrape product URLs before Gemini analysis.

## Pipeline

```
Product URL → scrapling_scraper.scrape_website() → analyze_saas() → video script
```

## Scrape modes

Set `SAASSHORTS_SCRAPE_MODE`:

| Mode | When |
|------|------|
| `auto` (default) | Fast `Fetcher`, then `DynamicFetcher` if page looks empty |
| `static` | `Fetcher` only (Docker default — no browser) |
| `dynamic` | Headless browser for React/Framer SPAs |
| `legacy` | Old httpx + BeautifulSoup |

## Quick test

```bash
pip install "scrapling[fetchers]"
# optional for dynamic/auto fallback on SPAs:
scrapling install

python scripts/test_scrapling_scrape.py https://www.lingology.pl
python scripts/test_scrapling_scrape.py https://www.lingology.pl --json
```

## Generate promo for Lingology / TutorApp

1. Start OpenShorts (`docker compose up` or `uvicorn app:app`)
2. Open **AI Shorts** tab
3. Paste URL:
   - `https://www.lingology.pl` — language learning app
   - `https://tutorapp-khaki.vercel.app` — tutoring dashboard
4. Scrapling fetches copy → Gemini writes script → fal.ai renders UGC video

## Docker

Default compose uses `SAASSHORTS_SCRAPE_MODE=static` (lightweight, no Chromium in image).

For full SPA support, build with browser deps — see `Dockerfile.scrapling` (optional).
