# scraper/chaldal.py
#
# Scrapes food prices from Chaldal.com.
# Chaldal is a JS-rendered SPA, so we use Playwright (headless Chromium).
#
# Each scrape_food() call:
#   1. Opens the Chaldal search page for a query
#   2. Waits for product cards to load
#   3. Extracts the first result's name, price, and weight
#   4. Normalises to price-per-kg (or price-per-piece for eggs)
#
# Returns a dict: { "price_per_kg": float, "price_per_piece": float|None,
#                   "product_name": str, "raw_price": float, "raw_weight": str }
# Returns None if scraping fails.

import re
import time

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from config import CHALDAL_BASE, SCRAPER_TIMEOUT, SCRAPER_HEADLESS


def scrape_food(query: str, food_key: str) -> dict | None:
    """
    Search Chaldal for `query` and return pricing info.
    Returns None on any failure.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print(f"  [Chaldal] Playwright not installed — skipping '{query}'")
        return None

    url = f"{CHALDAL_BASE}/search?q={query.replace(' ', '%20')}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=SCRAPER_HEADLESS)
            page    = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            })

            print(f"  [Chaldal] Fetching: {url}")
            page.goto(url, timeout=SCRAPER_TIMEOUT * 1000)

            # Wait for product cards to appear
            try:
                page.wait_for_selector("div.product", timeout=10_000)
            except PlaywrightTimeout:
                print(f"  [Chaldal] No products found for '{query}'")
                browser.close()
                return None

            # Small extra wait for lazy-loaded prices
            time.sleep(1.5)

            # Grab the first product card
            card = page.query_selector("div.product")
            if not card:
                browser.close()
                return None

            # Product name
            name_el   = card.query_selector("div.name, h4, .productName")
            name_text = name_el.inner_text().strip() if name_el else query

            # Price — Chaldal shows it as "৳ 120" or "120.00"
            price_el   = card.query_selector("div.price, span.price, .productPrice")
            price_text = price_el.inner_text().strip() if price_el else ""
            raw_price  = _parse_number(price_text)

            # Weight/quantity — e.g. "1 kg", "500 gm", "12 pcs"
            weight_el  = card.query_selector("div.subText, div.weight, .unitSize, span.unit")
            weight_text= weight_el.inner_text().strip() if weight_el else ""

            browser.close()

            if raw_price is None:
                print(f"  [Chaldal] Could not parse price for '{query}'")
                return None

            result = _normalise(food_key, name_text, raw_price, weight_text)
            if result:
                print(f"  [Chaldal] ✓ {name_text} | ৳{raw_price} / {weight_text or '?'}")
            return result

    except Exception as e:
        print(f"  [Chaldal] Error scraping '{query}': {e}")
        return None


def _parse_number(text: str) -> float | None:
    """Extract first float from a string like '৳ 120.00' or '120'."""
    text = text.replace("৳", "").replace(",", "").strip()
    match = re.search(r"[\d]+\.?[\d]*", text)
    return float(match.group()) if match else None


def _normalise(food_key: str, name: str, price: float, weight_str: str) -> dict | None:
    """
    Convert raw price + weight string into price-per-kg (or price-per-piece).
    weight_str examples: "1 kg", "500 gm", "500 g", "12 pcs", "1 litre", "1L"
    """
    ws = weight_str.lower().strip()

    # ── Eggs: price per piece ────────────────────────────────────────────────
    if food_key == "egg":
        pieces = _extract_pieces(ws)
        if pieces:
            return {
                "price_per_piece": round(price / pieces, 2),
                "price_per_kg":    None,
                "price_per_litre": None,
                "product_name":    name,
                "raw_price":       price,
                "raw_weight":      weight_str,
                "source":          "chaldal",
            }

    # ── Milk / liquids: price per litre ──────────────────────────────────────
    if food_key == "milk":
        litres = _extract_litres(ws)
        if litres:
            return {
                "price_per_litre": round(price / litres, 2),
                "price_per_kg":    None,
                "price_per_piece": None,
                "product_name":    name,
                "raw_price":       price,
                "raw_weight":      weight_str,
                "source":          "chaldal",
            }

    # ── Everything else: price per kg ────────────────────────────────────────
    kg = _extract_kg(ws)
    if kg:
        return {
            "price_per_kg":    round(price / kg, 2),
            "price_per_litre": None,
            "price_per_piece": None,
            "product_name":    name,
            "raw_price":       price,
            "raw_weight":      weight_str,
            "source":          "chaldal",
        }

    # Could not parse weight — return None so fallback price is used
    return None


def _extract_kg(ws: str) -> float | None:
    """Return kg quantity from strings like '1 kg', '500 gm', '500 g', '250g'."""
    # Match "500 gm" / "500 g" / "500g"
    m = re.search(r"([\d.]+)\s*(?:gm|gram|g)\b", ws)
    if m:
        return float(m.group(1)) / 1000

    # Match "1 kg" / "1.5 kg" / "1kg"
    m = re.search(r"([\d.]+)\s*kg", ws)
    if m:
        return float(m.group(1))

    return None


def _extract_pieces(ws: str) -> float | None:
    """Return piece count from '12 pcs', '6 pieces', '1 piece'."""
    m = re.search(r"([\d.]+)\s*(?:pcs|piece|pieces|pc)\b", ws)
    return float(m.group(1)) if m else None


def _extract_litres(ws: str) -> float | None:
    """Return litre quantity from '1 litre', '500 ml', '1L'."""
    m = re.search(r"([\d.]+)\s*(?:ml|millilitre)\b", ws)
    if m:
        return float(m.group(1)) / 1000

    m = re.search(r"([\d.]+)\s*(?:litre|liter|l)\b", ws)
    if m:
        return float(m.group(1))

    return None