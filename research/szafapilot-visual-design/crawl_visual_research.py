#!/usr/bin/env python3
"""Aggressive visual design research crawler powered by Scrapling.

Uses sync page_action (DynamicSession / StealthySession) to capture
screenshots and extract design-system signals from modern product sites.
"""

from __future__ import annotations

import json
import re
import traceback
from pathlib import Path
from typing import Any

from scrapling.fetchers import DynamicSession, StealthySession

ROOT = Path(__file__).resolve().parent
SCREENSHOTS = ROOT / "screenshots"
RAW = ROOT / "raw"
ARTIFACTS = Path("/opt/cursor/artifacts/szafapilot-visual-research")

SCREENSHOTS.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)

TARGETS: list[dict[str, str]] = [
    {"name": "stripe", "url": "https://stripe.com", "category": "premium-saas"},
    {"name": "linear", "url": "https://linear.app", "category": "premium-saas"},
    {"name": "notion", "url": "https://www.notion.so", "category": "premium-saas"},
    {"name": "vercel", "url": "https://vercel.com", "category": "premium-saas"},
    {"name": "attio", "url": "https://attio.com", "category": "premium-saas"},
    {"name": "mercury", "url": "https://mercury.com", "category": "premium-saas"},
    {"name": "ramp", "url": "https://ramp.com", "category": "premium-saas"},
    {"name": "intercom", "url": "https://www.intercom.com", "category": "premium-saas"},
    {"name": "supabase", "url": "https://supabase.com", "category": "premium-saas"},
    {"name": "framer", "url": "https://www.framer.com", "category": "premium-saas"},
    {"name": "webflow", "url": "https://webflow.com", "category": "premium-saas"},
    {"name": "relume", "url": "https://www.relume.io", "category": "premium-saas"},
    {"name": "perplexity", "url": "https://www.perplexity.ai", "category": "ai-native"},
    {"name": "clay", "url": "https://www.clay.com", "category": "ai-native"},
    {"name": "cursor", "url": "https://cursor.com", "category": "ai-native"},
    {"name": "lovable", "url": "https://lovable.dev", "category": "ai-native"},
    {"name": "granola", "url": "https://www.granola.ai", "category": "ai-native"},
    {"name": "raycast", "url": "https://www.raycast.com", "category": "ai-native"},
    {"name": "loom", "url": "https://www.loom.com", "category": "ai-native"},
    {"name": "zapier", "url": "https://zapier.com", "category": "automation"},
    {"name": "make", "url": "https://www.make.com", "category": "automation"},
    {"name": "retool", "url": "https://retool.com", "category": "automation"},
    {"name": "airtable", "url": "https://www.airtable.com", "category": "automation"},
    {"name": "shopify", "url": "https://www.shopify.com", "category": "ecommerce"},
    {"name": "partiful", "url": "https://partiful.com", "category": "marketplace"},
    {"name": "canva", "url": "https://www.canva.com", "category": "ecommerce"},
    {"name": "arc", "url": "https://arc.net", "category": "chrome-extension"},
    {"name": "raycast-store", "url": "https://www.raycast.com/store", "category": "chrome-extension"},
    {"name": "datadog", "url": "https://www.datadoghq.com", "category": "dashboard"},
    {"name": "figma", "url": "https://www.figma.com", "category": "dashboard"},
]

EXTRACT_DESIGN_JS = r"""
() => {
  const abs = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: (el.className && typeof el.className === 'string')
        ? el.className.trim().split(/\s+/).slice(0, 8)
        : [],
      text: (el.innerText || '').trim().slice(0, 180).replace(/\s+/g, ' '),
      top: Math.round(r.top + window.scrollY),
      left: Math.round(r.left),
      width: Math.round(r.width),
      height: Math.round(r.height),
    };
  };

  const styleOf = (el) => {
    if (!el) return null;
    const s = getComputedStyle(el);
    return {
      color: s.color,
      backgroundColor: s.backgroundColor,
      backgroundImage: s.backgroundImage,
      fontFamily: s.fontFamily,
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      lineHeight: s.lineHeight,
      letterSpacing: s.letterSpacing,
      borderRadius: s.borderRadius,
      boxShadow: s.boxShadow,
      border: s.border,
      padding: s.padding,
      margin: s.margin,
      display: s.display,
      gap: s.gap,
      maxWidth: s.maxWidth,
      textTransform: s.textTransform,
    };
  };

  const colorCounts = {};
  const fontCounts = {};
  const radiusCounts = {};
  const shadowSamples = [];
  const els = Array.from(document.querySelectorAll('body *')).slice(0, 2500);
  for (const el of els) {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    for (const c of [s.color, s.backgroundColor, s.borderColor]) {
      if (!c || c === 'rgba(0, 0, 0, 0)' || c === 'transparent') continue;
      colorCounts[c] = (colorCounts[c] || 0) + 1;
    }
    const ff = s.fontFamily.split(',')[0].replace(/["']/g, '').trim();
    if (ff) fontCounts[ff] = (fontCounts[ff] || 0) + 1;
    if (s.borderRadius && s.borderRadius !== '0px') {
      radiusCounts[s.borderRadius] = (radiusCounts[s.borderRadius] || 0) + 1;
    }
    if (s.boxShadow && s.boxShadow !== 'none' && shadowSamples.length < 20) {
      shadowSamples.push(s.boxShadow);
    }
  }

  const topN = (obj, n = 12) =>
    Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, n)
      .map(([value, count]) => ({ value, count }));

  const header = document.querySelector('header, [role="banner"], nav');
  const footer = document.querySelector('footer, [role="contentinfo"]');
  const main = document.querySelector('main') || document.body;
  const sections = Array.from(
    document.querySelectorAll('main > section, main > div, body > section, body > div > section, [data-section], section')
  ).slice(0, 40).map((el, i) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    const h = el.querySelector('h1,h2,h3');
    return {
      index: i,
      tag: el.tagName.toLowerCase(),
      classes: (el.className && typeof el.className === 'string')
        ? el.className.trim().split(/\s+/).slice(0, 6)
        : [],
      top: Math.round(r.top + window.scrollY),
      height: Math.round(r.height),
      width: Math.round(r.width),
      backgroundColor: s.backgroundColor,
      backgroundImage: s.backgroundImage !== 'none' ? s.backgroundImage.slice(0, 200) : null,
      heading: h ? (h.innerText || '').trim().slice(0, 120) : null,
      headingTag: h ? h.tagName.toLowerCase() : null,
      childCount: el.children.length,
    };
  });

  const headings = Array.from(document.querySelectorAll('h1,h2,h3'))
    .slice(0, 30)
    .map((h) => ({
      tag: h.tagName.toLowerCase(),
      text: (h.innerText || '').trim().slice(0, 140),
      style: styleOf(h),
      box: abs(h),
    }));

  const buttons = Array.from(
    document.querySelectorAll('a, button, [role="button"]')
  ).filter((el) => {
    const r = el.getBoundingClientRect();
    return r.width > 40 && r.height > 20 && r.top < window.innerHeight * 1.5;
  }).slice(0, 25).map((el) => ({
    text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 80),
    href: el.getAttribute('href'),
    style: styleOf(el),
    box: abs(el),
  }));

  const cards = Array.from(document.querySelectorAll('[class*="card" i], [class*="Card"], article'))
    .slice(0, 15)
    .map((el) => ({ style: styleOf(el), box: abs(el) }));

  const images = Array.from(document.querySelectorAll('img, video, canvas'))
    .slice(0, 20)
    .map((el) => ({
      tag: el.tagName.toLowerCase(),
      src: el.currentSrc || el.src || el.getAttribute('src') || null,
      alt: el.getAttribute('alt'),
      box: abs(el),
    }));

  const navLinks = Array.from(
    document.querySelectorAll('header a, nav a, [role="navigation"] a')
  ).slice(0, 30).map((a) => (a.innerText || '').trim()).filter(Boolean);

  const cssVars = {};
  try {
    const sheets = Array.from(document.styleSheets);
    for (const sheet of sheets.slice(0, 30)) {
      let rules;
      try { rules = sheet.cssRules; } catch (e) { continue; }
      if (!rules) continue;
      for (const rule of Array.from(rules).slice(0, 400)) {
        if (!rule.style) continue;
        for (let i = 0; i < rule.style.length; i++) {
          const prop = rule.style[i];
          if (prop && prop.startsWith('--')) {
            const val = rule.style.getPropertyValue(prop).trim();
            if (val && !cssVars[prop]) cssVars[prop] = val.slice(0, 120);
          }
        }
      }
    }
  } catch (e) {}

  const bodyStyle = styleOf(document.body);
  const htmlStyle = styleOf(document.documentElement);
  const bg = bodyStyle.backgroundColor || '';
  const rgb = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  let luminance = null;
  let themeGuess = 'unknown';
  if (rgb) {
    const [r, g, b] = rgb.slice(1).map(Number);
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
    themeGuess = luminance < 0.45 ? 'dark' : 'light';
  }

  return {
    url: location.href,
    title: document.title,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
      scrollHeight: document.documentElement.scrollHeight,
    },
    themeGuess,
    luminance,
    bodyStyle,
    htmlStyle,
    header: { box: abs(header), style: styleOf(header), navLinks },
    footer: { box: abs(footer), style: styleOf(footer) },
    main: { box: abs(main) },
    sections,
    headings,
    buttons,
    cards,
    images,
    colors: topN(colorCounts, 18),
    fonts: topN(fontCounts, 12),
    radii: topN(radiusCounts, 12),
    shadows: [...new Set(shadowSamples)].slice(0, 12),
    cssVars: Object.fromEntries(Object.entries(cssVars).slice(0, 80)),
    metaTheme: (document.querySelector('meta[name="theme-color"]') || {}).content || null,
  };
}
"""


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-")


def make_page_action(name: str, out: dict[str, Any]):
    """Sync Playwright page_action for DynamicSession / StealthySession."""

    def page_action(page):
        try:
            page.set_viewport_size({"width": 1440, "height": 900})
        except Exception:
            pass

        for sel in [
            'button:has-text("Accept")',
            'button:has-text("Accept all")',
            'button:has-text("Accept All")',
            'button:has-text("Got it")',
            'button:has-text("Allow all")',
            'button:has-text("I agree")',
            '[aria-label="Close"]',
        ]:
            try:
                loc = page.locator(sel).first
                if loc.count() > 0 and loc.is_visible():
                    loc.click(timeout=1500)
                    break
            except Exception:
                pass

        page.wait_for_timeout(1500)

        vp_path = SCREENSHOTS / f"{name}-viewport.png"
        full_path = SCREENSHOTS / f"{name}-full.png"
        art_vp = ARTIFACTS / f"{name}-viewport.png"
        art_full = ARTIFACTS / f"{name}-full.png"

        try:
            page.screenshot(path=str(vp_path), full_page=False, type="png")
            art_vp.write_bytes(vp_path.read_bytes())
            out["viewport_screenshot"] = str(vp_path)
            out["artifact_viewport"] = str(art_vp)
        except Exception as e:
            out["viewport_error"] = str(e)

        try:
            scroll_h = page.evaluate("() => document.documentElement.scrollHeight")
            if scroll_h and scroll_h < 12000:
                page.screenshot(path=str(full_path), full_page=True, type="png")
            else:
                metrics = page.evaluate(
                    "() => ({ w: window.innerWidth, h: Math.min(document.documentElement.scrollHeight, 8000) })"
                )
                page.screenshot(
                    path=str(full_path),
                    full_page=False,
                    type="png",
                    clip={"x": 0, "y": 0, "width": metrics["w"], "height": metrics["h"]},
                )
            art_full.write_bytes(full_path.read_bytes())
            out["full_screenshot"] = str(full_path)
            out["artifact_full"] = str(art_full)
        except Exception as e:
            out["full_error"] = str(e)

        try:
            # Stealthy/Patchright may need isolated_context=False for DOM globals
            try:
                design = page.evaluate(EXTRACT_DESIGN_JS, isolated_context=False)
            except TypeError:
                design = page.evaluate(EXTRACT_DESIGN_JS)
            out["design"] = design
        except Exception as e:
            out["design_error"] = str(e)

        try:
            snippet_js = """() => {
              const clip = (el, n=4000) => el ? el.outerHTML.slice(0, n) : null;
              return {
                headerHtml: clip(document.querySelector('header, [role="banner"]'), 5000),
                heroHtml: clip(
                  document.querySelector('h1')?.closest('section,div') || document.querySelector('main > *:first-child'),
                  6000
                ),
                footerHtml: clip(document.querySelector('footer'), 4000),
              };
            }"""
            try:
                out["snippets"] = page.evaluate(snippet_js, isolated_context=False)
            except TypeError:
                out["snippets"] = page.evaluate(snippet_js)
        except Exception as e:
            out["snippets_error"] = str(e)

    return page_action


def crawl_one(session, target: dict[str, str], stealth: bool = False) -> dict[str, Any]:
    name = slugify(target["name"])
    result: dict[str, Any] = {
        "name": name,
        "url": target["url"],
        "category": target["category"],
        "stealth": stealth,
        "ok": False,
    }
    try:
        page_action = make_page_action(name, result)
        kwargs: dict[str, Any] = {
            "page_action": page_action,
            "network_idle": True,
            "wait": 1500,
            "timeout": 45000,
            "google_search": True,
        }
        if stealth:
            kwargs["solve_cloudflare"] = True
            kwargs["timeout"] = 60000
        response = session.fetch(target["url"], **kwargs)
        result["status"] = getattr(response, "status", None)
        result["final_url"] = getattr(response, "url", target["url"])
        try:
            result["html_signals"] = {
                "h1_count": len(response.css("h1")),
                "h2_count": len(response.css("h2")),
                "section_count": len(response.css("section")),
                "nav_count": len(response.css("nav")),
                "button_count": len(response.css("button")),
                "img_count": len(response.css("img")),
                "footer_count": len(response.css("footer")),
            }
        except Exception as e:
            result["html_signals_error"] = str(e)
        result["ok"] = bool(result.get("viewport_screenshot") or result.get("design"))
    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()[-2000:]

    (RAW / f"{name}.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    return result


def main() -> None:
    results: list[dict[str, Any]] = []

    print(f"Crawling {len(TARGETS)} targets with DynamicSession...")
    with DynamicSession(headless=True, network_idle=True, timeout=45000) as session:
        for i, target in enumerate(TARGETS, 1):
            print(f"[{i}/{len(TARGETS)}] {target['name']} -> {target['url']}", flush=True)
            result = crawl_one(session, target, stealth=False)
            results.append(result)
            print(
                f"  ok={result.get('ok')} status={result.get('status')} "
                f"shots={bool(result.get('viewport_screenshot'))} "
                f"design={bool(result.get('design'))}",
                flush=True,
            )

    failed = [r for r in results if not r.get("ok") or not r.get("design")]
    if failed:
        print(f"\nRetrying {len(failed)} with StealthySession...", flush=True)
        retry_map = {
            r["name"]: next(t for t in TARGETS if slugify(t["name"]) == r["name"])
            for r in failed
        }
        with StealthySession(
            headless=True, network_idle=True, timeout=60000, solve_cloudflare=True
        ) as session:
            for name, target in retry_map.items():
                print(f"[stealth] {name} -> {target['url']}", flush=True)
                result = crawl_one(session, target, stealth=True)
                for idx, old in enumerate(results):
                    if old["name"] == name:
                        results[idx] = result
                        break
                print(
                    f"  ok={result.get('ok')} status={result.get('status')} "
                    f"shots={bool(result.get('viewport_screenshot'))} "
                    f"design={bool(result.get('design'))}",
                    flush=True,
                )

    summary = {
        "total": len(results),
        "ok": sum(1 for r in results if r.get("ok")),
        "with_design": sum(1 for r in results if r.get("design")),
        "with_viewport": sum(1 for r in results if r.get("viewport_screenshot")),
        "sites": [
            {
                "name": r["name"],
                "url": r["url"],
                "category": r["category"],
                "ok": r.get("ok"),
                "theme": (r.get("design") or {}).get("themeGuess"),
                "fonts": [f["value"] for f in ((r.get("design") or {}).get("fonts") or [])[:5]],
                "viewport_screenshot": r.get("viewport_screenshot"),
                "full_screenshot": r.get("full_screenshot"),
                "error": r.get("error") or r.get("design_error") or r.get("viewport_error"),
            }
            for r in results
        ],
    }
    (ROOT / "crawl-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (ARTIFACTS / "crawl-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nDone.", flush=True)
    print(json.dumps({k: summary[k] for k in ("total", "ok", "with_design", "with_viewport")}, indent=2))


if __name__ == "__main__":
    main()
