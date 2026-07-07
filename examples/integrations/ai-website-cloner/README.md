# Scrapling preflight (optional)

Before `/clone-website`, run:

```bash
pip install "scrapling[fetchers]"
python scripts/scrapling-preflight.py https://target-site.com
```

If the page is a thin SPA shell (< 400 chars text), retry:

```bash
scrapling install
python scripts/scrapling-preflight.py https://target-site.com --dynamic
```

Use results to decide whether browser MCP alone is enough or asset download needs `FetcherSession`.
