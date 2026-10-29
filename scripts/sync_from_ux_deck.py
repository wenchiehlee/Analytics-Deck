#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/sync_from_ux_deck.py
Sync mascot cards and assets from ../UX-Deck into Analytics-Deck.

Features:
1. Copies newly added modern emblems and lucide SVG icons from ../UX-Deck/tokens/.
2. Parses the 13+ mascot cards from ../UX-Deck/index.html.
3. Merges them into data/endpoints.json:
   - Preserves all configured analytics data (views_total, active_users_30d, ga4 settings, amplitude settings).
   - Updates brand text, mascot names, descriptions, and URLs from UX-Deck.
   - Adds new endpoints with pending analytics templates if detected.
4. Extracts SVG symbols from UX-Deck/index.html into data/svg_symbols.html for easy embedding.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import re
import json
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
UX_DECK_DIR = BASE_DIR.parent / "UX-Deck"
DATA_DIR = BASE_DIR / "data"
TOKENS_DIR = BASE_DIR / "tokens"
ENDPOINTS_JSON = DATA_DIR / "endpoints.json"
SYMBOLS_FILE = DATA_DIR / "svg_symbols.html"

MASTER_GA4_URL = "https://analytics.google.com/analytics/web/#/a333479515p463673189/reports/intelligenthome?params=_u..nav%3Dmaui%26_u..realtimeTimePeriod%3D5&collectionId=user"
MASTER_GA4_ACCOUNT = "333479515"
MASTER_GA4_PROPERTY = "463673189"

def sync_assets():
    """Copy SVG icons, favicons, and css from UX-Deck."""
    if not UX_DECK_DIR.exists():
        print(f"[!] Warning: UX-Deck directory not found at {UX_DECK_DIR}")
        return

    print(f"[*] Syncing design tokens and icons from {UX_DECK_DIR}...")
    
    # Ensure local dirs exist
    (TOKENS_DIR / "icons" / "modern-emblem").mkdir(parents=True, exist_ok=True)
    (TOKENS_DIR / "icons" / "lucide").mkdir(parents=True, exist_ok=True)
    (TOKENS_DIR / "favicons").mkdir(parents=True, exist_ok=True)

    # Copy tokens.css and design-tokens.json
    for filename in ["tokens.css", "design-tokens.json"]:
        src = UX_DECK_DIR / "tokens" / filename
        if src.exists():
            shutil.copy2(src, TOKENS_DIR / filename)

    # Copy modern emblems
    src_emblems = UX_DECK_DIR / "tokens" / "icons" / "modern-emblem"
    if src_emblems.exists():
        for f in src_emblems.glob("*.svg"):
            shutil.copy2(f, TOKENS_DIR / "icons" / "modern-emblem" / f.name)

    # Copy lucide icons
    src_lucide = UX_DECK_DIR / "tokens" / "icons" / "lucide"
    if src_lucide.exists():
        for f in src_lucide.glob("*.svg"):
            shutil.copy2(f, TOKENS_DIR / "icons" / "lucide" / f.name)

    # Copy favicons
    src_fav = UX_DECK_DIR / "tokens" / "favicons"
    if src_fav.exists():
        for f in src_fav.glob("*.*"):
            shutil.copy2(f, TOKENS_DIR / "favicons" / f.name)

    for fav in ["favicon.svg", "favicon.png", "favicon.ico"]:
        src = UX_DECK_DIR / fav
        if src.exists():
            shutil.copy2(src, BASE_DIR / fav)
            shutil.copy2(src, BASE_DIR / "docs" / fav)

    # Mirror showcases.html to root and docs/
    showcases_file = UX_DECK_DIR / "showcases.html"
    if showcases_file.exists():
        shutil.copy2(showcases_file, BASE_DIR / "showcases.html")
        shutil.copy2(showcases_file, BASE_DIR / "docs" / "showcases.html")

    # Mirror deploy/ directory if exists
    deploy_dir = UX_DECK_DIR / "deploy"
    if deploy_dir.exists():
        for target in [BASE_DIR / "deploy", BASE_DIR / "docs" / "deploy"]:
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(deploy_dir, target)

    # Mirror tokens to docs/tokens for GitHub Pages
    docs_tokens = BASE_DIR / "docs" / "tokens"
    if docs_tokens.exists():
        shutil.rmtree(docs_tokens)
    shutil.copytree(TOKENS_DIR, docs_tokens)

    print("[✓] Assets successfully synced to tokens/ and docs/tokens/.")

def extract_symbols(soup: BeautifulSoup):
    """Extract SVG symbol tags defined in UX-Deck/index.html."""
    symbols = soup.find_all("symbol")
    symbol_defs = []
    for s in symbols:
        symbol_defs.append(str(s))
    
    if symbol_defs:
        combined = '<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">\n' + "\n".join(symbol_defs) + "\n</svg>"
        SYMBOLS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SYMBOLS_FILE, "w", encoding="utf-8") as f:
            f.write(combined)
        print(f"[✓] Extracted {len(symbol_defs)} SVG symbols to {SYMBOLS_FILE}")

def parse_mascot_cards(html_content: str):
    """Parse mascot cards from UX-Deck HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    extract_symbols(soup)

    mascot_grid = soup.find("div", class_="mascot-grid")
    if not mascot_grid:
        print("[!] Error: .mascot-grid not found in UX-Deck HTML!")
        return []

    cards = mascot_grid.find_all("div", class_="mascot-card", recursive=False)
    print(f"[*] Found {len(cards)} mascot cards in UX-Deck.")

    endpoints = []
    for idx, card in enumerate(cards, start=1):
        classes = card.get("class", [])
        card_class = " ".join([c for c in classes if c != "mascot-card"])

        # Duo stage
        duo_stage = card.find("div", class_="mascot-duo-stage")
        emblem_a = duo_stage.find("a", class_="emblem-tile") if duo_stage else None
        lucide_a = duo_stage.find("a", class_="lucide-tile") if duo_stage else None

        showcase_url = emblem_a.get("href", "") if emblem_a else ""
        if showcase_url.startswith("./showcases.html") or showcase_url.startswith("showcases.html"):
            anchor = showcase_url.split("#")[-1] if "#" in showcase_url else ""
            showcase_url = f"https://wenchiehlee-ux.github.io/UX-Deck/showcases.html#{anchor}" if anchor else "https://wenchiehlee-ux.github.io/UX-Deck/showcases.html"
        emblem_img = emblem_a.find("img") if emblem_a else None
        emblem_src = emblem_img.get("src", "") if emblem_img else ""
        emblem_alt = emblem_img.get("alt", "") if emblem_img else ""

        live_url = lucide_a.get("href", "") if lucide_a else ""
        if "github.com/wenchiehlee/dockers" in live_url:
            live_url = "https://wenchiehlee.github.io/dockers/"
        lucide_wrapper_class = " ".join([c for c in (lucide_a.get("class", []) if lucide_a else []) if c != "lucide-tile"])

        # Check if lucide has inline svg or use ref
        lucide_svg = lucide_a.find("svg") if lucide_a else None
        use_tag = lucide_svg.find("use") if lucide_svg else None
        symbol_id = use_tag.get("href", "").replace("#", "") if use_tag else ""
        inline_svg_html = str(lucide_svg) if lucide_svg and not use_tag else ""

        name_el = card.find("div", class_="mascot-name")
        name = name_el.get_text(strip=True) if name_el else f"端點 {idx}"

        proj_el = card.find("div", class_="mascot-project")
        project = proj_el.get_text(strip=True) if proj_el else ""

        desc_el = card.find("div", class_="mascot-desc")
        desc_html = desc_el.decode_contents().strip() if desc_el else ""

        # Derive slug ID
        # Extract id from showcase_url (e.g. ./showcases.html#mkdocs-life -> mkdocs-life)
        slug_id = ""
        if "#" in showcase_url:
            slug_id = showcase_url.split("#")[-1]
        elif card_class:
            slug_id = card_class.replace("card-", "")
        else:
            slug_id = f"endpoint-{idx}"

        # If duplicate slug (e.g. mkdocs-investment bull vs bear)
        if "bull" in card_class or "bull" in name_el.text:
            slug_id = "mkdocs-investment-bull"
        elif "bear" in card_class or "bear" in name_el.text:
            slug_id = "mkdocs-investment-bear"

        endpoints.append({
            "id": slug_id,
            "order": idx,
            "name": name,
            "project": project,
            "card_class": card_class,
            "lucide_wrapper_class": lucide_wrapper_class,
            "showcase_url": showcase_url,
            "live_url": live_url,
            "emblem_src": emblem_src,
            "emblem_alt": emblem_alt,
            "symbol_id": symbol_id,
            "inline_svg_html": inline_svg_html,
            "desc_html": desc_html
        })

    return endpoints

def merge_with_existing(parsed_endpoints):
    """Merge newly parsed UX-Deck endpoints with local analytics configurations."""
    existing_map = {}
    if ENDPOINTS_JSON.exists():
        try:
            with open(ENDPOINTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("endpoints", []):
                    existing_map[item["id"]] = item
            print(f"[*] Loaded {len(existing_map)} existing endpoints from {ENDPOINTS_JSON.name}")
        except Exception as e:
            print(f"[!] Warning reading existing JSON: {e}")

    merged = []
    for item in parsed_endpoints:
        ep_id = item["id"]
        existing = existing_map.get(ep_id, {})
        
        # Determine archetype
        category = "docs"
        if any(k in ep_id for k in ["alert", "audio", "tagger"]):
            category = "saas"
        elif any(k in ep_id for k in ["tv", "nas", "docker"]):
            category = "infra"
        elif any(k in ep_id for k in ["coverage", "conference", "vix"]):
            category = "fintech"

        # Preserve analytics config or initialize (only mkdocs-life has verified numbers; others start as None/---)
        analytics = existing.get("analytics", {
            "views_total": 20595 if ep_id == "mkdocs-life" else None,
            "active_users_30d": "1.2k" if ep_id == "mkdocs-life" else None,
            "category": category,
            "ga4": {
                "enabled": True,
                "measurement_id": "G-913Z6DSVD2",
                "property_id": MASTER_GA4_PROPERTY,
                "account_id": MASTER_GA4_ACCOUNT,
                "dashboard_url": MASTER_GA4_URL,
                "filter_path": f"/{ep_id}/"
            },
            "amplitude": {
                "enabled": False,
                "status": "planned",
                "project_name": item["project"].split(" ")[0],
                "dashboard_url": ""
            },
            "last_sync": "2026-10-27 12:00:00"
        })

        item["analytics"] = analytics
        merged.append(item)

    result = {
        "metadata": {
            "title": "Analytics-Deck Endpoints Telemetry Registry",
            "source": "UX-Deck (Settled Geometric Mascots)",
            "sync_frequency": "4 renewals per day (every 6 hours)",
            "cron_schedule": "0 */6 * * *",
            "last_deck_sync": "2026-10-27 12:00:00",
            "total_endpoints": len(merged)
        },
        "endpoints": merged
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(ENDPOINTS_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[✓] Successfully merged and wrote {len(merged)} endpoints into {ENDPOINTS_JSON}")
    
    # Auto rebuild index.html
    try:
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        from scripts.build_page import build_index_html
        build_index_html()
    except Exception as e:
        print(f"[!] Warning building index.html: {e}")

def main():
    sync_assets()
    ux_html_path = UX_DECK_DIR / "index.html"
    if not ux_html_path.exists():
        print(f"[!] Error: {ux_html_path} does not exist!")
        return

    with open(ux_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    parsed = parse_mascot_cards(html_content)
    merge_with_existing(parsed)
    print("\n[🎉] Sync completed! You can now run or build index.html.")

if __name__ == "__main__":
    main()
