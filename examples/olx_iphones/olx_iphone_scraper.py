"""
OLX.pl — tanie iPhone'y (przykład Scrapling Spider)

Wyszukuje ogłoszenia iPhone na OLX, filtruje po cenie i eksporuje do JSON.

Użycie:
    python examples/olx_iphones/olx_iphone_scraper.py
    python examples/olx_iphones/olx_iphone_scraper.py --max-price 800 --max-pages 3
    python examples/olx_iphones/olx_iphone_scraper.py --output moje_iphony.json
"""

from __future__ import annotations

import argparse
import re
from urllib.parse import urlencode, urljoin

from scrapling.spiders import Request, Response, Spider
from scrapling.spiders.result import ItemList

OLX_BASE = "https://www.olx.pl"
OLX_IPHONE_PATH = (
    "/elektronika/telefony/smartfony-telefony-komorkowe/q-iphone/"
)

# Ogłoszenia-wabiki OLX (1 zł) i inne śmieciowe tytuły
SKIP_TITLE_KEYWORDS = (
    "pudełko",
    "pudelko",
    "wymiana za",
    "odkup urządzeń",
    "odkup urzadzen",
    "tajna fajna",
    "etui",
    "szkło",
    "szklo",
    "kabel",
    "ładowark",
    "ladowark",
)


def build_search_url(
    *,
    max_price: int,
    min_price: int = 0,
    page: int | None = None,
) -> str:
    params: dict[str, str | int] = {
        "search[filter_float_price:to]": max_price,
        "search[order]": "filter_float_price:asc",
    }
    if min_price > 0:
        params["search[filter_float_price:from]"] = min_price
    if page and page > 1:
        params["page"] = page

    return f"{OLX_BASE}{OLX_IPHONE_PATH}?{urlencode(params)}"


def parse_price_pln(raw: str | None) -> float | None:
    if not raw:
        return None
    lowered = raw.lower().replace("\xa0", " ")
    if "zamieni" in lowered:
        return None
    match = re.search(r"([\d]+(?:[.,]\d+)?)", lowered)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def is_iphone_listing(title: str | None, price: float | None, min_price: float) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    if "iphone" not in title_lower and "iphon" not in title_lower:
        return False
    if any(keyword in title_lower for keyword in SKIP_TITLE_KEYWORDS):
        return False
    if price is None or price < min_price:
        return False
    return True


class OlxIphoneSpider(Spider):
    """Spider OLX: tanie iPhone'y posortowane rosnąco po cenie."""

    name = "olx_iphones"

    def __init__(
        self,
        *,
        max_price: int = 1000,
        min_price: int = 100,
        max_pages: int = 2,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.max_price = max_price
        self.min_price = min_price
        self.max_pages = max_pages
        self._pages_seen = 0
        self.concurrent_requests = 2
        self.download_delay = 1.0
        self.start_urls = [build_search_url(max_price=self.max_price, min_price=0)]

    async def start_requests(self):
        for url in self.start_urls:
            yield Request(url, sid=self._session_manager.default_session_id)

    async def parse(self, response: Response):
        self._pages_seen += 1

        for card in response.css('[data-cy="l-card"]'):
            title = (card.css("h4::text").get() or card.css("h6::text").get() or "").strip()
            price_raw = card.css('[data-testid="ad-price"]::text').get()
            price = parse_price_pln(price_raw)

            if not is_iphone_listing(title, price, self.min_price):
                continue
            if price is not None and price > self.max_price:
                continue

            href = card.css("a::attr(href)").get()
            location = (card.css('[data-testid="location-date"]::text').get() or "").strip()
            image = card.css("img::attr(src)").get()
            listing_id = card.attrib.get("id")

            # Stan: pierwszy krótki tag tekstowy pod ceną (Używane / Nowe / Uszkodzone)
            condition = None
            for text in card.css("::text").getall():
                cleaned = text.strip()
                if cleaned in ("Używane", "Nowe", "Uszkodzone"):
                    condition = cleaned
                    break

            yield {
                "id": listing_id,
                "title": title,
                "price_pln": price,
                "price_raw": (price_raw or "").strip(),
                "condition": condition,
                "location": location,
                "url": urljoin(OLX_BASE, href) if href else None,
                "image": image,
            }

        if self._pages_seen >= self.max_pages:
            return

        next_link = response.css('[data-testid="pagination-forward"]::attr(href)').get()
        if next_link:
            yield response.follow(next_link)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrapuj tanie iPhone'y z OLX.pl (Scrapling Spider)",
    )
    parser.add_argument(
        "--max-price",
        type=int,
        default=1000,
        help="Maksymalna cena w PLN (domyślnie: 1000)",
    )
    parser.add_argument(
        "--min-price",
        type=int,
        default=100,
        help="Minimalna cena w PLN — odfiltrowuje wabiki 1–2 zł (domyślnie: 100)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=2,
        help="Ile stron wyników przeszukać (domyślnie: 2)",
    )
    parser.add_argument(
        "--output",
        default="olx_iphones.json",
        help="Plik wyjściowy JSON (domyślnie: olx_iphones.json)",
    )
    args = parser.parse_args()

    print(f"\n🔍 Szukam iPhone'ów na OLX: {args.min_price}–{args.max_price} zł")
    print(f"   Stron: {args.max_pages} | Sortowanie: cena rosnąco\n")

    result = OlxIphoneSpider(
        max_price=args.max_price,
        min_price=args.min_price,
        max_pages=args.max_pages,
    ).start()

    items = sorted(result.items, key=lambda x: x.get("price_pln") or float("inf"))

    print(f"{'=' * 60}")
    print(f"Znaleziono : {len(items)} ogłoszeń")
    print(f"Requesty   : {result.stats.requests_count}")
    print(f"Czas       : {result.stats.elapsed_seconds:.1f}s")
    print(f"{'=' * 60}\n")

    for index, item in enumerate(items[:20], 1):
        price = item.get("price_pln")
        price_label = f"{price:.0f} zł" if price is not None else item.get("price_raw", "?")
        condition = item.get("condition") or "?"
        location = (item.get("location") or "?")[:40]
        title = (item.get("title") or "?")[:55]
        print(f"{index:>2}. {price_label:>8} | {condition:10} | {title}")
        print(f"    📍 {location}")
        print(f"    🔗 {item.get('url')}\n")

    if len(items) > 20:
        print(f"... i {len(items) - 20} więcej w pliku {args.output}\n")

    ItemList(items).to_json(args.output, indent=True)
    print(f"✅ Zapisano {len(items)} ogłoszeń → {args.output}")


if __name__ == "__main__":
    main()
