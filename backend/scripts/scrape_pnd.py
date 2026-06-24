"""
Scrape pre-negotiated deals from pnd.leasehackr.com for Washington state.

Run locally (requires Playwright + Chromium):
    pip install playwright
    playwright install chromium
    python scripts/scrape_pnd.py

Output: prints JSON to stdout; redirect to a file or pipe into the seed updater.
The site uses client-side JS for state selection so we need a real browser.
"""
from __future__ import annotations

import json
import sys
import time

TARGET_MAKES = {"kia", "hyundai"}
TARGET_MODELS = {"ev9", "ioniq 9", "ioniq9", "carnival"}
WA_STATE = "Washington"


def scrape(headless: bool = True) -> list[dict]:
    from playwright.sync_api import sync_playwright

    deals: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print("[pnd] Navigating to pnd.leasehackr.com …", file=sys.stderr)
        page.goto("https://pnd.leasehackr.com", timeout=30_000)
        page.wait_for_load_state("networkidle", timeout=20_000)

        # ── Find and set the state/location selector ──────────────────────────
        # Try common selector patterns for a state dropdown
        state_selected = False
        for selector in [
            "select[name*='state']",
            "select[id*='state']",
            "select[placeholder*='state' i]",
            "[data-testid*='state']",
            "button:has-text('State')",
            "button:has-text('Location')",
        ]:
            try:
                if page.locator(selector).count() > 0:
                    el = page.locator(selector).first
                    tag = el.evaluate("el => el.tagName.toLowerCase()")
                    if tag == "select":
                        el.select_option(label=WA_STATE)
                        state_selected = True
                        print(f"[pnd] Selected state via <select> ({selector})", file=sys.stderr)
                        break
                    elif tag == "button":
                        el.click()
                        page.wait_for_load_state("networkidle", timeout=5_000)
                        # Look for Washington in the dropdown that appeared
                        wa_opt = page.locator(f"text={WA_STATE}").first
                        if wa_opt.count() > 0:
                            wa_opt.click()
                            state_selected = True
                            print(f"[pnd] Clicked Washington in dropdown", file=sys.stderr)
                            break
            except Exception:
                continue

        if not state_selected:
            # Try clicking any element that mentions "state" and then pick Washington
            print("[pnd] Could not find state selector via standard patterns — trying text search", file=sys.stderr)
            for text in ["State", "Location", "Filter"]:
                try:
                    btn = page.get_by_text(text, exact=True).first
                    if btn.is_visible():
                        btn.click()
                        time.sleep(1)
                        wa = page.get_by_text(WA_STATE, exact=True).first
                        if wa.is_visible():
                            wa.click()
                            state_selected = True
                            break
                except Exception:
                    continue

        if state_selected:
            page.wait_for_load_state("networkidle", timeout=10_000)
            time.sleep(2)  # let results render
        else:
            print("[pnd] WARNING: Could not select Washington — scraping all visible deals", file=sys.stderr)

        # ── Intercept any in-page JSON API calls (for reference) ──────────────
        # Dump the HTML so we can inspect the deal card structure if needed
        html = page.content()
        with open("/tmp/pnd_page.html", "w") as f:
            f.write(html)
        print("[pnd] Saved page HTML to /tmp/pnd_page.html", file=sys.stderr)

        page.screenshot(path="/tmp/pnd_screenshot.png", full_page=True)
        print("[pnd] Screenshot saved to /tmp/pnd_screenshot.png", file=sys.stderr)

        # ── Extract deal cards ────────────────────────────────────────────────
        # Common patterns for deal cards on Leasehackr PND
        card_selectors = [
            "[class*='deal']",
            "[class*='card']",
            "article",
            "li[class*='listing']",
        ]
        cards_found = 0
        for sel in card_selectors:
            cards = page.locator(sel).all()
            if cards:
                print(f"[pnd] Found {len(cards)} elements matching '{sel}'", file=sys.stderr)
                cards_found = len(cards)
                for card in cards:
                    try:
                        text = card.inner_text()
                        # Filter to target vehicles
                        text_lower = text.lower()
                        if not any(m in text_lower for m in TARGET_MODELS):
                            continue
                        if not any(mk in text_lower for mk in TARGET_MAKES):
                            continue
                        deals.append({
                            "raw_text": text,
                            "selector": sel,
                            "html": card.inner_html(),
                        })
                    except Exception:
                        continue
                if deals:
                    break

        if not cards_found:
            print("[pnd] No deal cards found — check /tmp/pnd_page.html for page structure", file=sys.stderr)

        browser.close()

    return deals


def main():
    headless = "--show" not in sys.argv
    results = scrape(headless=headless)

    if not results:
        print("[]")
        print("[pnd] No matching deals found. Inspect /tmp/pnd_page.html to adjust selectors.", file=sys.stderr)
        return

    print(json.dumps(results, indent=2))
    print(f"\n[pnd] Found {len(results)} matching deals.", file=sys.stderr)


if __name__ == "__main__":
    main()
