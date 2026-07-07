# Scrapling

Self-hosted Python web scraping framework (fetchers + spiders + optional MCP). Use when you want **Firecrawl-like page extraction without API cost**, especially for competitor homepages, pricing, and feature pages.

## Capabilities

| Integration | Available | Notes |
|-------------|-----------|-------|
| API | - | Library, not SaaS |
| MCP | ✓ | `scrapling[ai]` — see Scrapling docs |
| CLI | ✓ | `scrapling extract get <url>` |
| SDK | ✓ | `pip install "scrapling[fetchers]"` |

## Authentication

None for public pages. Optional proxies via `ProxyRotator` for rate limits.

## Setup

```bash
pip install "scrapling[fetchers]"
scrapling install   # browsers — only for DynamicFetcher / StealthyFetcher
```

## Core Operations

### Scrape a single page (fast HTTP)

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get("https://competitor.com/pricing", stealthy_headers=True)
title = page.css("title::text").get()
headings = page.css("h1::text, h2::text").getall()
body_text = page.get_all_text(ignore_tags=("script", "style"))
```

### Scrape JS-heavy pages (SPAs)

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    "https://competitor.com",
    headless=True,
    network_idle=True,
)
markdown-ish = page.get_all_text(ignore_tags=("nav", "footer", "script", "style"))
```

### Multi-page competitor crawl

```python
from scrapling.spiders import Spider, Response

class CompetitorSpider(Spider):
    name = "competitor"
    start_urls = ["https://competitor.com/"]
    concurrent_requests = 2
    download_delay = 1.0

    async def parse(self, response: Response):
        if response.url.count("/") <= 3:  # shallow pages only
            yield {
                "url": response.url,
                "title": response.css("title::text").get(),
                "h1": response.css("h1::text").getall(),
            }
        for href in response.css('a[href*="/pricing"]::attr(href), a[href*="/features"]::attr(href)').getall()[:5]:
            yield response.follow(href)
```

Save output to `competitor-profiles/raw/<slug>/<date>/scrapes/` as markdown.

## When to Use (vs Firecrawl / Browserbase)

| Situation | Tool |
|-----------|------|
| Static marketing site, no API budget | **Scrapling Fetcher** |
| React/Framer pricing page | **Scrapling DynamicFetcher** |
| Cloudflare / heavy bot protection | **Scrapling StealthyFetcher** |
| Managed API, zero ops | Firecrawl |
| Login / form interaction | Browserbase |

## Compliance

Same rules as Firecrawl:

- Scrape **competitor public marketing pages** only
- Do **not** scrape LinkedIn, Google Maps, G2 listing pages at scale
- Respect robots.txt when doing crawls (`Spider(robots_txt_obey=True)`)

## Used By Skills

- competitor-profiling (self-hosted scrape alternative)
- seo-audit (JSON-LD in JS via DynamicFetcher)
- programmatic-seo (comparison page research)
