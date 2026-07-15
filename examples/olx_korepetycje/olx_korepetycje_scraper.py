"""
OLX.pl — publiczne ogłoszenia korepetycji (KorepetycjeRadar)

Legalny monitor publicznych ogłoszeń: korepetytorzy i osoby szukające korep.
Bez zbierania prywatnych danych poza tym, co jest w publicznym ogłoszeniu.

Użycie:
    python examples/olx_korepetycje/olx_korepetycje_scraper.py
    python examples/olx_korepetycje/olx_korepetycje_scraper.py --subject matematyka --city krakow
    python examples/olx_korepetycje/olx_korepetycje_scraper.py --subject angielski --type lead
    python examples/olx_korepetycje/olx_korepetycje_scraper.py --subject fizyka --max-pages 3 --output leads.json
"""

from __future__ import annotations

import argparse
import logging
import re
from urllib.parse import urlencode, urljoin

from scrapling.spiders import Request, Response, Spider
from scrapling.spiders.result import ItemList

OLX_BASE = "https://www.olx.pl"

# Słowa kluczowe: kto SZUKA korepetytora (lead dla platformy / korepetytorów)
LEAD_KEYWORDS = (
    "szukam korepety",
    "szukam nauczyciel",
    "szukam lektora",
    "potrzebuję korepety",
    "potrzebuje korepety",
    "poszukuję korepety",
    "poszukuje korepety",
    "szukam korep",
    "szukam pomocy",
    "pilnie szukam",
)

# Ogłoszenia-wabiki / nie na temat
SKIP_TITLE_KEYWORDS = (
    "tajna fajna",
    "testowe ogłoszenie",
)

SUBJECT_ALIASES: dict[str, str] = {
    "matma": "matematyka",
    "math": "matematyka",
    "ang": "angielski",
    "english": "angielski",
    "niem": "niemiecki",
    "deutsch": "niemiecki",
    "inf": "informatyka",
    "it": "informatyka",
    "programowanie": "informatyka",
}


def normalize_subject(subject: str) -> str:
    key = subject.strip().lower()
    return SUBJECT_ALIASES.get(key, key)


def normalize_city(city: str | None) -> str | None:
    if not city:
        return None
    return city.strip().lower().replace("ł", "l").replace("ó", "o").replace("ą", "a")


def build_search_url(
    *,
    subject: str = "korepetycje",
    city: str | None = None,
    page: int | None = None,
    sort_newest: bool = False,
) -> str:
    subject_slug = normalize_subject(subject)
    query = f"q-korepetycje-{subject_slug}" if subject_slug != "korepetycje" else "q-korepetycje"

    if city:
        path = f"/{normalize_city(city)}/{query}/"
    else:
        path = f"/oferty/{query}/"

    params: dict[str, str | int] = {}
    if sort_newest:
        params["search[order]"] = "created_at:desc"
    if page and page > 1:
        params["page"] = page

    if params:
        return f"{OLX_BASE}{path}?{urlencode(params)}"
    return f"{OLX_BASE}{path}"


def build_lead_search_url(
    *,
    city: str | None = None,
    page: int | None = None,
    sort_newest: bool = False,
) -> str:
    """Osobne wyszukiwanie OLX pod ogłoszenia „szukam korepetytora”."""
    if city:
        path = f"/{normalize_city(city)}/q-szukam-korepetytora/"
    else:
        path = "/oferty/q-szukam-korepetytora/"

    params: dict[str, str | int] = {}
    if sort_newest:
        params["search[order]"] = "created_at:desc"
    if page and page > 1:
        params["page"] = page

    if params:
        return f"{OLX_BASE}{path}?{urlencode(params)}"
    return f"{OLX_BASE}{path}"


def parse_price_pln(raw: str | None) -> float | None:
    if not raw:
        return None
    lowered = raw.lower().replace("\xa0", " ")
    if "zamieni" in lowered or "za darmo" in lowered:
        return None
    match = re.search(r"([\d]+(?:[.,]\d+)?)", lowered)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def classify_listing(title: str) -> str:
    """lead = szuka korepetytora, offer = oferuje korepetycje, unknown = niepewne."""
    lower = title.lower()
    if any(keyword in lower for keyword in LEAD_KEYWORDS):
        return "lead"
    if any(
        phrase in lower
        for phrase in (
            "korepetycje z",
            "korepetycje ",
            "oferuję korepety",
            "oferuje korepety",
            "prowadzę korepety",
            "prowadze korepety",
            "nauczę",
            "naucze ",
            "lektor ",
            "korepetytor",
            "zajęcia z",
            "zajecia z",
        )
    ):
        return "offer"
    return "unknown"


def is_relevant_listing(title: str | None) -> bool:
    if not title:
        return False
    lower = title.lower()
    if any(keyword in lower for keyword in SKIP_TITLE_KEYWORDS):
        return False
    if "korepety" in lower or "naucz" in lower or "lektor" in lower or "matura" in lower:
        return True
    return "szukam" in lower and any(
        word in lower for word in ("nauczyciel", "pomocy", "lektora", "tutora")
    )


class OlxKorepetycjeSpider(Spider):
    """Spider OLX: publiczne ogłoszenia korepetycji."""

    name = "olx_korepetycje"
    logging_level = logging.INFO

    def __init__(
        self,
        *,
        subject: str = "korepetycje",
        city: str | None = None,
        listing_type: str | None = None,
        max_price: int | None = None,
        min_price: int | None = None,
        max_pages: int = 2,
        sort_newest: bool = True,
        include_lead_search: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.subject = normalize_subject(subject)
        self.city = normalize_city(city)
        self.listing_type = listing_type
        self.max_price = max_price
        self.min_price = min_price
        self.max_pages = max_pages
        self.sort_newest = sort_newest
        self.include_lead_search = include_lead_search
        self._pages_seen = 0
        self.concurrent_requests = 2
        self.download_delay = 1.0
        self.start_urls = [
            build_search_url(subject=self.subject, city=self.city, sort_newest=sort_newest),
        ]
        if include_lead_search:
            self.start_urls.append(
                # Bez sortowania po dacie — OLX lepiej pokazuje prawdziwe „szukam”
                build_lead_search_url(city=self.city, sort_newest=False),
            )

    async def start_requests(self):
        for url in self.start_urls:
            yield Request(url, sid=self._session_manager.default_session_id)

    async def parse(self, response: Response):
        self._pages_seen += 1

        for card in response.css('[data-cy="l-card"]'):
            title = (card.css("h4::text").get() or card.css("h6::text").get() or "").strip()
            if not is_relevant_listing(title):
                continue

            price_raw = card.css('[data-testid="ad-price"]::text').get()
            price = parse_price_pln(price_raw)
            kind = classify_listing(title)

            if self.listing_type and kind != self.listing_type:
                continue
            if self.min_price is not None and (price is None or price < self.min_price):
                continue
            if self.max_price is not None and price is not None and price > self.max_price:
                continue

            href = card.css("a::attr(href)").get()
            location = (card.css('[data-testid="location-date"]::text').get() or "").strip()
            listing_id = card.attrib.get("id")

            yield {
                "id": listing_id,
                "title": title,
                "listing_type": kind,
                "subject": self.subject,
                "city_filter": self.city,
                "price_pln": price,
                "price_raw": (price_raw or "").strip(),
                "location": location,
                "url": urljoin(OLX_BASE, href) if href else None,
            }

        if self._pages_seen >= self.max_pages:
            return

        next_link = response.css('[data-testid="pagination-forward"]::attr(href)').get()
        if next_link:
            yield response.follow(next_link)


def scrape_korepetycje(
    *,
    subject: str = "korepetycje",
    city: str | None = None,
    listing_type: str | None = None,
    max_price: int | None = None,
    min_price: int | None = None,
    max_pages: int = 2,
    sort_newest: bool = True,
    include_lead_search: bool = True,
) -> list[dict]:
    result = OlxKorepetycjeSpider(
        subject=subject,
        city=city,
        listing_type=listing_type,
        max_price=max_price,
        min_price=min_price,
        max_pages=max_pages,
        sort_newest=sort_newest,
        include_lead_search=include_lead_search,
    ).start()
    by_id: dict[str, dict] = {}
    for item in result.items:
        listing_id = item.get("id")
        if listing_id:
            by_id[listing_id] = item
    return list(by_id.values())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrapuj publiczne ogłoszenia korepetycji z OLX.pl",
    )
    parser.add_argument(
        "--subject",
        default="korepetycje",
        help="Przedmiot: matematyka, angielski, fizyka, chemia... (domyślnie: wszystkie)",
    )
    parser.add_argument(
        "--city",
        default=None,
        help="Miasto OLX: krakow, warszawa, wroclaw... (domyślnie: cała Polska)",
    )
    parser.add_argument(
        "--type",
        dest="listing_type",
        choices=["lead", "offer", "unknown"],
        default=None,
        help="lead = szuka korepetytora, offer = oferuje korepetycje",
    )
    parser.add_argument("--max-price", type=int, default=None, help="Maks. stawka w PLN")
    parser.add_argument("--min-price", type=int, default=None, help="Min. stawka w PLN")
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--output", default="korepetycje.json")
    parser.add_argument(
        "--oldest-first",
        action="store_true",
        help="Wyłącz sortowanie po dacie (domyślnie: najnowsze pierwsze)",
    )
    parser.add_argument(
        "--no-lead-search",
        action="store_true",
        help="Nie skanuj osobno wyszukiwania „szukam korepetytora”",
    )
    args = parser.parse_args()

    where = args.city or "cała Polska"
    type_label = args.listing_type or "wszystkie"
    print(f"\n📚 KorepetycjeRadar — OLX")
    print(f"   Przedmiot: {args.subject} | Miasto: {where} | Typ: {type_label}")
    print(f"   Stron: {args.max_pages}\n")

    items = scrape_korepetycje(
        subject=args.subject,
        city=args.city,
        listing_type=args.listing_type,
        max_price=args.max_price,
        min_price=args.min_price,
        max_pages=args.max_pages,
        sort_newest=not args.oldest_first,
        include_lead_search=not args.no_lead_search,
    )

    leads = sum(1 for i in items if i["listing_type"] == "lead")
    offers = sum(1 for i in items if i["listing_type"] == "offer")

    print(f"{'=' * 60}")
    print(f"Znaleziono : {len(items)} ogłoszeń (lead: {leads}, offer: {offers})")
    print(f"{'=' * 60}\n")

    for index, item in enumerate(items[:15], 1):
        price = item.get("price_pln")
        price_label = f"{price:.0f} zł/h" if price is not None else (item.get("price_raw") or "—")
        kind_icon = {"lead": "🎯 LEAD", "offer": "👨‍🏫 OFERTA", "unknown": "❓"}.get(
            item["listing_type"], "?"
        )
        title = (item.get("title") or "?")[:52]
        location = (item.get("location") or "?")[:38]
        print(f"{index:>2}. [{kind_icon}] {price_label:>10} | {title}")
        print(f"    📍 {location}")
        print(f"    🔗 {item.get('url')}\n")

    if len(items) > 15:
        print(f"... i {len(items) - 15} więcej w pliku {args.output}\n")

    ItemList(items).to_json(args.output, indent=True)
    print(f"✅ Zapisano {len(items)} ogłoszeń → {args.output}")


if __name__ == "__main__":
    main()
