"""
KorepetycjeRadar — automatyczny watcher ogłoszeń korepetycji na OLX.

Powiadamia o NOWYCH publicznych ogłoszeniach (lead = ktoś szuka korepetytora).

Użycie:
    python examples/olx_korepetycje/olx_korepetycje_watcher.py --subject matematyka --city krakow
    python examples/olx_korepetycje/olx_korepetycje_watcher.py --type lead --interval 10

Telegram:
    export TELEGRAM_BOT_TOKEN="..."
    export TELEGRAM_CHAT_ID="..."
    python examples/olx_korepetycje/olx_korepetycje_watcher.py --subject angielski --type lead

Cron (co 15 min):
    */15 * * * * cd /sciezka/Scrapling && python3 examples/olx_korepetycje/olx_korepetycje_watcher.py --once --type lead --subject matematyka --city warszawa
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from olx_korepetycje_scraper import scrape_korepetycje

DEFAULT_STATE = Path(__file__).resolve().parent / ".korepetycje_state.json"


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"seen_ids": [], "history": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def format_listing(item: dict) -> str:
    kind = {
        "lead": "🎯 SZUKA KOREPETYTORA",
        "offer": "👨‍🏫 OFERUJE KOREPETYCJE",
        "unknown": "📋 OGŁOSZENIE",
    }.get(item.get("listing_type", ""), "📋")
    price = item.get("price_pln")
    price_label = f"{price:.0f} zł" if price is not None else (item.get("price_raw") or "brak ceny")
    return (
        f"{kind}\n"
        f"📚 {item.get('subject', '?')} | {item.get('location', '?')}\n"
        f"💰 {price_label}\n"
        f"📝 {item.get('title', '?')}\n"
        f"🔗 {item.get('url', '?')}"
    )


def send_telegram(message: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    request = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status == 200
    except urllib.error.URLError as exc:
        print(f"⚠️  Telegram: {exc}", file=sys.stderr)
        return False


def notify_new_listings(new_items: list[dict], *, subject: str, city: str | None) -> None:
    header = f"📚 Nowe ogłoszenie: {subject}"
    if city:
        header += f" ({city})"
    for item in new_items:
        text = format_listing(item)
        print(f"\n🆕 {text}\n")
        send_telegram(f"{header}\n\n{text}")


def run_check(
    *,
    subject: str,
    city: str | None,
    listing_type: str | None,
    max_price: int | None,
    min_price: int | None,
    max_pages: int,
    state_path: Path,
    notify_on_first_run: bool,
    leads_only_alert: bool,
    include_lead_search: bool,
) -> int:
    state = load_state(state_path)
    seen_ids: set[str] = set(state.get("seen_ids", []))
    first_run = len(seen_ids) == 0

    where = city or "cała PL"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Skan: {subject} | {where}")

    items = scrape_korepetycje(
        subject=subject,
        city=city,
        listing_type=listing_type,
        max_price=max_price,
        min_price=min_price,
        max_pages=max_pages,
        sort_newest=True,
        include_lead_search=include_lead_search,
    )

    new_items = [item for item in items if item.get("id") and item["id"] not in seen_ids]

    if leads_only_alert:
        new_items = [item for item in new_items if item.get("listing_type") == "lead"]

    if first_run and not notify_on_first_run:
        print(f"   Pierwsze uruchomienie: zapisuję {len(items)} ogłoszeń bez alertów.")
        new_items = []

    if new_items:
        notify_new_listings(new_items, subject=subject, city=city)
    elif not (first_run and not notify_on_first_run):
        print(f"   Brak nowych ({len(items)} teraz, {len(seen_ids)} znanych wcześniej).")

    for item in items:
        if item.get("id"):
            seen_ids.add(item["id"])

    state["seen_ids"] = sorted(seen_ids)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["config"] = {"subject": subject, "city": city, "listing_type": listing_type}
    state["history"] = (state.get("history") or [])[-99:]
    state["history"].append(
        {"at": state["last_run"], "total": len(items), "new": len(new_items)},
    )
    save_state(state_path, state)
    return len(new_items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watcher ogłoszeń korepetycji OLX")
    parser.add_argument("--subject", default="matematyka")
    parser.add_argument("--city", default=None)
    parser.add_argument("--type", dest="listing_type", choices=["lead", "offer", "unknown"], default=None)
    parser.add_argument("--max-price", type=int, default=None)
    parser.add_argument("--min-price", type=int, default=None)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--interval", type=int, default=15, help="Minuty między skanami")
    parser.add_argument("--once", action="store_true", help="Jedno sprawdzenie (cron)")
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--notify-on-first-run", action="store_true")
    parser.add_argument(
        "--oldest-first",
        action="store_true",
        help="Domyślnie: najnowsze pierwsze. Ta flaga wyłącza sortowanie po dacie.",
    )
    parser.add_argument(
        "--no-lead-search",
        action="store_true",
        help="Nie skanuj wyszukiwania „szukam korepetytora”",
    )
    args = parser.parse_args()

    leads_only = not args.all_types_alert
    telegram = bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))

    print("📚 KorepetycjeRadar Watcher")
    print(f"   {args.subject} | {args.city or 'cała Polska'} | typ: {args.listing_type or 'wszystkie'}")
    print(f"   Alerty: {'tylko leady' if leads_only else 'lead + oferta'}")
    print(f"   Telegram: {'✅' if telegram else '❌ (ustaw TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)'}")

    def do_check() -> int:
        return run_check(
            subject=args.subject,
            city=args.city,
            listing_type=args.listing_type,
            max_price=args.max_price,
            min_price=args.min_price,
            max_pages=args.max_pages,
            state_path=args.state_file,
            notify_on_first_run=args.notify_on_first_run,
            leads_only_alert=leads_only,
            include_lead_search=not args.no_lead_search,
        )

    if args.once:
        do_check()
        return

    print(f"   Pętla co {args.interval} min (Ctrl+C = stop)\n")
    try:
        while True:
            do_check()
            print(f"   💤 Czekam {args.interval} min...\n")
            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        print("\n👋 Watcher zatrzymany.")


if __name__ == "__main__":
    main()
