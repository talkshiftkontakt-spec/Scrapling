"""
OLX iPhone watcher — automatyczne monitorowanie nowych ogłoszeń.

Co robi:
  1. Co N minut odpytuje OLX (ten sam spider co olx_iphone_scraper.py)
  2. Porównuje z zapisanymi ID ogłoszeń (plik stanu)
  3. Przy nowych ogłoszeniach: wypisuje w terminal + opcjonalnie Telegram

Użycie — pętla w tle na własnym komputerze:
    python examples/olx_iphones/olx_iphone_watcher.py
    python examples/olx_iphones/olx_iphone_watcher.py --interval 10 --max-price 700

Telegram (opcjonalnie):
    export TELEGRAM_BOT_TOKEN="123:ABC..."
    export TELEGRAM_CHAT_ID="twoje_chat_id"
    python examples/olx_iphones/olx_iphone_watcher.py

Cron — jedno sprawdzenie co 15 min (bez pętli):
    */15 * * * * cd /sciezka/do/Scrapling && python3 examples/olx_iphones/olx_iphone_watcher.py --once >> olx_watcher.log 2>&1

systemd — ciągła praca po restarcie maszyny (patrz komentarz na końcu pliku).
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

# Import względem katalogu examples/olx_iphones
sys.path.insert(0, str(Path(__file__).resolve().parent))

from olx_iphone_scraper import scrape_iphones

DEFAULT_STATE = Path(__file__).resolve().parent / ".olx_iphone_state.json"


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"seen_ids": [], "history": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def format_listing(item: dict) -> str:
    price = item.get("price_pln")
    price_label = f"{price:.0f} zł" if price is not None else item.get("price_raw", "?")
    return (
        f"💰 {price_label} | {item.get('condition', '?')}\n"
        f"📱 {item.get('title', '?')}\n"
        f"📍 {item.get('location', '?')}\n"
        f"🔗 {item.get('url', '?')}"
    )


def send_telegram(message: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": message, "disable_web_page_preview": "false"},
    ).encode()
    request = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status == 200
    except urllib.error.URLError as exc:
        print(f"⚠️  Telegram error: {exc}", file=sys.stderr)
        return False


def notify_new_listings(new_items: list[dict]) -> None:
    for item in new_items:
        text = format_listing(item)
        print(f"\n🆕 NOWE OGŁOSZENIE\n{text}\n")
        send_telegram(f"🆕 Nowy iPhone na OLX\n\n{text}")


def run_check(
    *,
    max_price: int,
    min_price: int,
    max_pages: int,
    state_path: Path,
    notify_on_first_run: bool,
) -> int:
    """Jedno sprawdzenie. Zwraca liczbę nowych ogłoszeń."""
    state = load_state(state_path)
    seen_ids: set[str] = set(state.get("seen_ids", []))
    first_run = len(seen_ids) == 0

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Skanuję OLX ({min_price}–{max_price} zł)...")
    items = scrape_iphones(max_price=max_price, min_price=min_price, max_pages=max_pages)

    new_items = [item for item in items if item.get("id") and item["id"] not in seen_ids]

    if first_run and not notify_on_first_run:
        print(f"   Pierwsze uruchomienie: zapisuję {len(items)} ogłoszeń bez alertów.")
        new_items = []

    if new_items:
        notify_new_listings(new_items)
    elif first_run and not notify_on_first_run:
        pass  # komunikat już wydrukowany wyżej
    else:
        print(f"   Brak nowych ({len(items)} ogłoszeń teraz, {len(seen_ids)} znanych wcześniej).")

    for item in items:
        if item.get("id"):
            seen_ids.add(item["id"])

    state["seen_ids"] = sorted(seen_ids)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["last_count"] = len(items)
    state["history"] = (state.get("history") or [])[-99:]
    state["history"].append(
        {
            "at": state["last_run"],
            "total": len(items),
            "new": len(new_items),
        },
    )
    save_state(state_path, state)
    return len(new_items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatyczny watcher tanich iPhone'ów na OLX")
    parser.add_argument("--max-price", type=int, default=1000)
    parser.add_argument("--min-price", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Minuty między sprawdzeniami w trybie pętli (domyślnie: 15)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Jedno sprawdzenie i wyjście (do crona)",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE,
        help="Plik z zapamiętanymi ID ogłoszeń",
    )
    parser.add_argument(
        "--notify-on-first-run",
        action="store_true",
        help="Wyślij alerty już przy pierwszym uruchomieniu",
    )
    args = parser.parse_args()

    telegram_ready = bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))
    print("🤖 OLX iPhone Watcher")
    print(f"   Filtr: {args.min_price}–{args.max_price} zł | stron: {args.max_pages}")
    print(f"   Stan: {args.state_file}")
    print(f"   Telegram: {'✅ włączony' if telegram_ready else '❌ wyłączony (ustaw TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)'}")

    if args.once:
        new_count = run_check(
            max_price=args.max_price,
            min_price=args.min_price,
            max_pages=args.max_pages,
            state_path=args.state_file,
            notify_on_first_run=args.notify_on_first_run,
        )
        sys.exit(0 if new_count >= 0 else 1)

    print(f"   Tryb: pętla co {args.interval} min (Ctrl+C = stop)\n")
    try:
        while True:
            run_check(
                max_price=args.max_price,
                min_price=args.min_price,
                max_pages=args.max_pages,
                state_path=args.state_file,
                notify_on_first_run=args.notify_on_first_run,
            )
            print(f"   💤 Czekam {args.interval} min...\n")
            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        print("\n👋 Watcher zatrzymany.")


if __name__ == "__main__":
    main()

# --- systemd (opcjonalnie) ---
# Plik: ~/.config/systemd/user/olx-iphone-watcher.service
#
# [Unit]
# Description=OLX iPhone watcher (Scrapling)
# After=network-online.target
#
# [Service]
# Type=simple
# WorkingDirectory=/sciezka/do/Scrapling
# Environment=TELEGRAM_BOT_TOKEN=...
# Environment=TELEGRAM_CHAT_ID=...
# ExecStart=/usr/bin/python3 examples/olx_iphones/olx_iphone_watcher.py --interval 15 --max-price 800
# Restart=on-failure
#
# [Install]
# WantedBy=default.target
#
# Włączenie:
#   systemctl --user daemon-reload
#   systemctl --user enable --now olx-iphone-watcher.service
