#!/usr/bin/env python3
"""Re-capture clean hero screenshots as high-quality PNG for Cursor vision."""

from __future__ import annotations

from pathlib import Path

from scrapling.fetchers import DynamicSession

OUT = Path("/workspace/research/szafapilot-visual-design/download-pack/07-screenshots-REAL-PNG")
OUT.mkdir(parents=True, exist_ok=True)

# Priority references for Szafapilot anti-slop direction
TARGETS = [
    ("linear", "https://linear.app"),
    ("attio", "https://attio.com"),
    ("notion", "https://www.notion.so"),
    ("cursor", "https://cursor.com"),
    ("ramp", "https://ramp.com"),
    ("granola", "https://www.granola.ai"),
    ("raycast", "https://www.raycast.com"),
    ("framer", "https://www.framer.com"),
    ("supabase", "https://supabase.com"),
    ("vercel", "https://vercel.com"),
    ("intercom", "https://www.intercom.com"),
    ("relume", "https://www.relume.io"),
    ("clay", "https://www.clay.com"),
    ("lovable", "https://lovable.dev"),
    ("zapier", "https://zapier.com"),
    ("make", "https://www.make.com"),
    ("shopify", "https://www.shopify.com"),
    ("mercury", "https://mercury.com"),
    ("loom", "https://www.loom.com"),
    ("figma", "https://www.figma.com"),
    ("airtable", "https://www.airtable.com"),
    ("retool", "https://retool.com"),
    ("webflow", "https://webflow.com"),
    ("stripe", "https://stripe.com"),
    ("partiful", "https://partiful.com"),
    ("arc", "https://arc.net"),
]


def make_action(name: str):
    def page_action(page):
        page.set_viewport_size({"width": 1440, "height": 900})

        # Aggressive dismiss: cookies, modals, promo overlays
        selectors = [
            'button:has-text("Accept all")',
            'button:has-text("Accept All")',
            'button:has-text("Accept")',
            'button:has-text("Got it")',
            'button:has-text("Allow all")',
            'button:has-text("I agree")',
            'button:has-text("Continue")',
            'button:has-text("Reject all")',
            'button:has-text("Reject All")',
            '[aria-label="Close"]',
            'button[aria-label="Close"]',
            'button:has-text("Close")',
            '[data-testid="close"]',
            '.modal button:has-text("×")',
        ]
        for _ in range(3):
            closed = False
            for sel in selectors:
                try:
                    loc = page.locator(sel)
                    n = loc.count()
                    for i in range(min(n, 3)):
                        item = loc.nth(i)
                        if item.is_visible():
                            item.click(timeout=1200)
                            closed = True
                            page.wait_for_timeout(400)
                except Exception:
                    pass
            if not closed:
                break
            page.wait_for_timeout(300)

        # Escape key for lingering overlays
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            page.keyboard.press("Escape")
        except Exception:
            pass

        page.wait_for_timeout(1800)

        # Viewport hero
        vp = OUT / f"{name}-hero.png"
        page.screenshot(path=str(vp), full_page=False, type="png")

        # Longer strip (useful for section rhythm) — cap height
        scroll_h = page.evaluate(
            "() => Math.min(document.documentElement.scrollHeight, 3600)"
        )
        w = page.evaluate("() => window.innerWidth")
        full = OUT / f"{name}-long.png"
        try:
            page.screenshot(
                path=str(full),
                full_page=False,
                type="png",
                clip={"x": 0, "y": 0, "width": w, "height": scroll_h},
            )
        except Exception:
            page.screenshot(path=str(full), full_page=True, type="png")

        print(f"  saved {vp.name} ({vp.stat().st_size // 1024}KB) + {full.name}", flush=True)

    return page_action


def main() -> None:
    print(f"Capturing {len(TARGETS)} sites -> {OUT}", flush=True)
    with DynamicSession(headless=True, network_idle=True, timeout=45000) as session:
        for name, url in TARGETS:
            print(f">>> {name} {url}", flush=True)
            try:
                session.fetch(
                    url,
                    page_action=make_action(name),
                    network_idle=True,
                    wait=2000,
                    timeout=45000,
                    google_search=True,
                )
            except Exception as e:
                print(f"  FAIL {name}: {e}", flush=True)
    print("done", flush=True)
    print("count", len(list(OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
