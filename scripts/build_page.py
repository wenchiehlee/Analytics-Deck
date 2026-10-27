#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_page.py
Generates the complete, standalone index.html for Analytics-Deck.
Reads data/endpoints.json and data/svg_symbols.html.
Ensures 100% visual and color tone consistency with UX-Deck (White Basis, Atmosphere Gradients, Card Shadows).
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ENDPOINTS_JSON = DATA_DIR / "endpoints.json"
SYMBOLS_FILE = DATA_DIR / "svg_symbols.html"
OUTPUT_HTML = BASE_DIR / "index.html"
DOCS_DIR = BASE_DIR / "docs"
DOCS_HTML = DOCS_DIR / "index.html"

def generate_card_html(ep: dict) -> str:
    analytics = ep.get("analytics", {})
    views = analytics.get("views_total", 0)
    views_formatted = f"{views:,}"
    active_30d = analytics.get("active_users_30d", "0")
    category = analytics.get("category", "docs")
    
    ga4 = analytics.get("ga4", {})
    ga4_url = ga4.get("dashboard_url", "https://analytics.google.com/analytics/web/")
    
    amp = analytics.get("amplitude", {})
    amp_enabled = amp.get("enabled", False)
    amp_status = amp.get("status", "planned")
    amp_url = amp.get("dashboard_url", "#")
    amp_label = "Amplitude events" if amp_enabled else "Amplitude (規劃中)"

    symbol_id = ep.get("symbol_id", "")
    inline_svg = ep.get("inline_svg_html", "")

    # Map symbol_id to exact icon class in UX-Deck
    icon_class = f"ux-icon ux-icon-xl"
    if symbol_id:
        slug = symbol_id.replace("icon-", "").split("-")[0]
        if slug == "docker":
            icon_class += " ux-icon-docker"
        else:
            icon_class += f" ux-icon-{slug}"
        icon_markup = f"""<svg class="{icon_class}">
          <use href="#{symbol_id}"></use>
        </svg>"""
    elif inline_svg:
        icon_markup = inline_svg
    else:
        icon_markup = f"""<svg class="{icon_class}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
        </svg>"""

    card_class = ep.get("card_class", "card-deer")
    lucide_wrapper = ep.get("lucide_wrapper_class", "wrapper-deer")

    card_html = f"""
    <div class="mascot-card {card_class}" data-category="{category}">
      <div class="mascot-duo-stage">
        <a href="{ep.get('showcase_url', '#')}" class="emblem-tile" target="_blank" rel="noopener noreferrer" title="查看此專案的色彩、字體與介面展示 ↗">
          <img src="{ep.get('emblem_src', '')}" alt="{ep.get('emblem_alt', '')}" class="emblem-thumb">
          <span class="badge-role-tag emblem-tag">🏛️ 官方紋章</span>
        </a>
        <div class="duo-divider">
          <span class="duo-arrow">⇄</span>
        </div>
        <a href="{ep.get('live_url', '#')}" class="lucide-tile {lucide_wrapper}" target="_blank" rel="noopener noreferrer" title="造訪 {ep.get('project')} ↗">
          {icon_markup}
          <span class="badge-role-tag lucide-tag">⚡ 介面線性</span>
        </a>
      </div>

      <div class="mascot-name">{ep.get('name', '')}</div>
      <div class="mascot-project">{ep.get('project', '')}</div>
      <div class="mascot-desc">
        {ep.get('desc_html', '')}
      </div>

      <!-- TELEMETRY POD (端點數據觀測艙) -->
      <div class="telemetry-pod">
        <div class="telemetry-stat-card">
          <div class="telemetry-stat-item">
            <span class="stat-label">本站訪問量</span>
            <strong class="stat-val stat-views">{views_formatted}</strong>
          </div>
          <div class="stat-divider"></div>
          <div class="telemetry-stat-item">
            <span class="stat-label">30D 月活躍</span>
            <strong class="stat-val stat-users">{active_30d}</strong>
          </div>
        </div>

        <div class="telemetry-actions">
          <a href="{ga4_url}" class="telemetry-btn btn-ga" target="_blank" rel="noopener noreferrer" title="開啟 Google Analytics 4 主控台報表 ↗">
            <svg class="btn-dot-icon" viewBox="0 0 8 8" width="6" height="6"><circle cx="4" cy="4" r="3" fill="currentColor"/></svg>
            <span>Google Analytics</span>
            <span class="btn-arrow">↗</span>
          </a>

          {'<a href="' + amp_url + '" class="telemetry-btn btn-amplitude" target="_blank" rel="noopener noreferrer" title="開啟 Amplitude 自訂事件儀表板 ↗">' if amp_enabled else '<span class="telemetry-btn btn-amplitude-disabled" title="此端點尚未配置 Amplitude 事件追蹤">' }
            <svg class="btn-dot-icon" viewBox="0 0 8 8" width="6" height="6"><circle cx="4" cy="4" r="3" fill="currentColor"/></svg>
            <span>{amp_label}</span>
            { '<span class="btn-arrow">↗</span></a>' if amp_enabled else '</span>' }
        </div>
      </div>
    </div>
"""
    return card_html

def build_index_html():
    if not ENDPOINTS_JSON.exists():
        print(f"[!] Error: {ENDPOINTS_JSON} not found!")
        return

    with open(ENDPOINTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    symbols_html = ""
    if SYMBOLS_FILE.exists():
        with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
            symbols_html = f.read()

    endpoints = data.get("endpoints", [])
    meta = data.get("metadata", {})
    last_sync = meta.get("last_sync_local", "每日 4 次自動同步中")

    cards_html = "\n".join([generate_card_html(ep) for ep in endpoints])

    template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analytics-Deck · 全端點數據觀測中樞</title>
  
  <!-- Favicon (Identical to UX-Deck) -->
  <link rel="icon" type="image/svg+xml" href="./favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="./favicon.png">
  <link rel="shortcut icon" href="./favicon.ico">

  <!-- Google Fonts (Exact UX-Deck Typography Stack) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=LXGW+WenKai+TC:wght@300;400;700&family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@400;600;700;900&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Quicksand:wght@500;600;700&family=Zen+Maru+Gothic:wght@500;700&display=swap" rel="stylesheet">

  <!-- Tokens CSS -->
  <link rel="stylesheet" href="./tokens/tokens.css">

  <style>
    /* ==========================================================================
       UX-Deck Aligned Design System & Color Tone
       White Basis & Crisp Light Theme Palette with Radial Atmosphere Gradients
       ========================================================================== */
    :root {{
      --bg-studio: #ffffff;
      --bg-subtle: #f8fafc;
      --surface-card: #ffffff;
      --surface-elevated: #f1f5f9;
      --border-light: #e2e8f0;
      --border-subtle: #edf2f7;
      --border-hover: #cbd5e1;
      
      --text-main: #0f172a;       /* Slate 900 */
      --text-muted: #475569;      /* Slate 600 */
      --text-dim: #94a3b8;        /* Slate 400 */

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
      --shadow-card: 0 4px 16px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
      --shadow-hover: 0 12px 28px -4px rgba(15, 23, 42, 0.08), 0 4px 10px -2px rgba(15, 23, 42, 0.04);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-studio);
      color: var(--text-main);
      font-family: "Noto Sans TC", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      padding: 3.5rem 1.75rem 6rem;
      min-height: 100vh;
      background-image: 
        radial-gradient(circle at 10% 8%, rgba(56, 189, 248, 0.04) 0%, transparent 35%),
        radial-gradient(circle at 90% 15%, rgba(139, 92, 246, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 50% 95%, rgba(13, 148, 136, 0.03) 0%, transparent 45%);
      background-attachment: fixed;
    }}

    .container {{
      max-width: 1280px;
      margin: 0 auto;
    }}

    /* Studio Header (Identical to UX-Deck) */
    header {{
      margin-bottom: 3rem;
      border-bottom: 1px solid var(--border-light);
      padding-bottom: 2.25rem;
      display: flex;
      flex-direction: column;
      gap: 1.15rem;
    }}

    .header-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #eff6ff;
      color: #2563eb;
      border: 1px solid #bfdbfe;
      padding: 5px 14px;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 700;
      width: fit-content;
      letter-spacing: 0.04em;
    }}

    h1 {{
      font-size: 2.5rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      line-height: 1.25;
      color: #0f172a;
      font-family: "Plus Jakarta Sans", "Noto Sans TC", sans-serif;
    }}

    .subtitle {{
      color: var(--text-muted);
      font-size: 1.125rem;
      max-width: 920px;
      line-height: 1.65;
    }}

    /* Telemetry Navigation Strip */
    .telemetry-nav-strip {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      margin-top: 0.5rem;
    }}

    .live-url-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 9999px;
      padding: 6px 14px;
      font-size: 0.82rem;
      font-weight: 600;
      color: #0f172a;
      text-decoration: none;
      transition: all 0.2s ease;
    }}

    .live-url-pill:hover {{
      background: #f1f5f9;
      border-color: #cbd5e1;
    }}

    .pill-pulse {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Category Filter Tabs */
    .filter-bar {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 2.5rem;
    }}

    .filter-btn {{
      background: #ffffff;
      border: 1px solid var(--border-light);
      border-radius: 9999px;
      padding: 6px 16px;
      font-size: 0.85rem;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .filter-btn:hover {{
      background: #f8fafc;
      color: #0f172a;
      border-color: #cbd5e1;
    }}

    .filter-btn.active {{
      background: #0f172a;
      color: #ffffff;
      border-color: #0f172a;
    }}

    /* Mascot Icons Standard Styling (From UX-Deck) */
    .ux-icon {{
      display: inline-block;
      width: 24px;
      height: 24px;
      vertical-align: middle;
      flex-shrink: 0;
      stroke-width: 1.6;
      stroke: currentColor;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
      transition: all 0.25s cubic-bezier(0.2, 0, 0, 1);
    }}
    .ux-icon-xl {{ width: 50px; height: 50px; }}

    /* Mascot Brand Colors & Hover Animations (Identical to UX-Deck) */
    .ux-icon-deer {{ color: #0d9488; }}
    .ux-icon-deer:hover {{ transform: translateY(-3px) scale(1.08); color: #0f766e; }}

    .ux-icon-falcon {{ color: #ea580c; }}
    .ux-icon-falcon:hover {{ transform: rotate(-6deg) scale(1.1); color: #c2410c; }}

    .ux-icon-whale {{ color: #9333ea; }}
    .ux-icon-whale:hover {{ transform: translateY(-3px) rotate(3deg); color: #7e22ce; }}

    .ux-icon-docker {{ color: #2496ed; }}
    .ux-icon-docker:hover {{ transform: translateY(-3px) scale(1.08); color: #0877c9; }}

    .ux-icon-bull {{ color: #dc2626; }}
    .ux-icon-bull:hover {{ transform: translateY(-3px) scale(1.1); color: #b91c1c; }}

    .ux-icon-bear {{ color: #16a34a; }}
    .ux-icon-bear:hover {{ transform: translateY(3px) scale(1.08); color: #15803d; }}

    .ux-icon-sentinel {{ color: #d97706; }}
    .ux-icon-sentinel:hover {{ transform: scale(1.12); color: #b45309; }}

    .ux-icon-pangolin {{ color: #0284c7; }}
    .ux-icon-pangolin:hover {{ transform: scale(1.12); color: #0369a1; }}

    .ux-icon-owl {{ color: #059669; }}
    .ux-icon-owl:hover {{ transform: translateY(-3px) scale(1.1); color: #047857; }}

    .ux-icon-eagle {{ color: #22a553; }}
    .ux-icon-eagle:hover {{ transform: translateY(-3px) scale(1.08); color: #166534; filter: drop-shadow(0 0 8px rgba(34, 165, 83, 0.45)); }}

    .ux-icon-swan {{ color: #0f172a; }}
    .ux-icon-swan:hover {{ transform: translateY(-3px) scale(1.08); color: #ef4444; filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.6)); }}

    .ux-icon-squirrel {{ color: #8b5cf6; }}
    .ux-icon-squirrel:hover {{ transform: translateY(-3px) scale(1.1); color: #7c3aed; filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.45)); }}

    .ux-icon-rabbit {{ color: #059669; }}
    .ux-icon-rabbit:hover {{ transform: translateY(-3px) scale(1.08); color: #047857; }}

    /* Mascot Wrappers (Pastel Brand Tones from UX-Deck) */
    .wrapper-deer {{ background: #f0fdfa; border: 1px solid #ccfbf1; }}
    .wrapper-falcon {{ background: #fff7ed; border: 1px solid #fed7aa; }}
    .wrapper-whale {{ background: #faf5ff; border: 1px solid #f3e8ff; }}
    .wrapper-docker-whale {{ background: #eff8ff; border: 1px solid #b8e1ff; }}
    .wrapper-bull {{ background: #fef2f2; border: 1px solid #fee2e2; }}
    .wrapper-bear {{ background: #f0fdf4; border: 1px solid #dcfce7; }}
    .wrapper-sentinel {{ background: #fffbeb; border: 1px solid #fde68a; }}
    .wrapper-pangolin {{ background: #f0f9ff; border: 1px solid #bae6fd; }}
    .wrapper-owl {{ background: #ecfdf5; border: 1px solid #a7f3d0; }}
    .wrapper-eagle {{ background: #f0fdf4; border: 1px solid #bbf7d0; }}
    .wrapper-swan {{ background: #0f172a; border: 1px solid #334155; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15); }}
    .wrapper-swan .ux-icon-swan {{ color: #ffffff; }}
    .wrapper-squirrel {{ background: #f5f3ff; border: 1px solid #ddd6fe; }}
    .wrapper-rabbit {{ background: #ecfdf5; border: 1px solid #a7f3d0; }}

    /* Mascot Grid (White Card Basis from UX-Deck) */
    .mascot-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3.5rem;
    }}

    .mascot-card {{
      background: var(--surface-card);
      border: 1px solid var(--border-light);
      border-radius: 18px;
      padding: 2rem 1.5rem 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      transition: all 0.25s ease;
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-card);
    }}

    .mascot-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: transparent;
      transition: all 0.25s ease;
    }}

    .mascot-card:hover {{
      transform: translateY(-5px);
      border-color: var(--border-hover);
      box-shadow: var(--shadow-hover);
    }}

    /* Card Hover Top Strips (UX-Deck Brand Colors) */
    .mascot-card.card-deer:hover::before {{ background: #0d9488; }}
    .mascot-card.card-falcon:hover::before {{ background: #ea580c; }}
    .mascot-card.card-whale:hover::before {{ background: #9333ea; }}
    .mascot-card.card-docker-whale:hover::before {{ background: #2496ed; }}
    .mascot-card.card-bull:hover::before {{ background: #dc2626; }}
    .mascot-card.card-bear:hover::before {{ background: #16a34a; }}
    .mascot-card.card-sentinel:hover::before {{ background: #d97706; }}
    .mascot-card.card-pangolin:hover::before {{ background: #0284c7; }}
    .mascot-card.card-owl:hover::before {{ background: #059669; }}
    .mascot-card.card-eagle:hover::before {{ background: #22a553; }}
    .mascot-card.card-swan:hover::before {{ background: #0f172a; }}
    .mascot-card.card-squirrel:hover::before {{ background: #8b5cf6; }}
    .mascot-card.card-rabbit:hover::before {{ background: #059669; }}

    /* Mascot Duo Stage (Exact UX-Deck Specs) */
    .mascot-duo-stage {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      margin-bottom: 1.15rem;
    }}

    .emblem-tile {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 8px 10px 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-decoration: none;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
      transition: all 0.25s ease;
      width: 110px;
      height: 115px;
      justify-content: space-between;
      flex-shrink: 0;
    }}

    .emblem-tile:hover {{
      transform: translateY(-3px) scale(1.03);
      border-color: #cbd5e1;
      box-shadow: 0 8px 20px -2px rgba(15, 23, 42, 0.08);
    }}

    .emblem-thumb {{
      width: 78px;
      height: 78px;
      object-fit: contain;
    }}

    .duo-divider {{
      display: flex;
      align-items: center;
      justify-content: center;
      color: #94a3b8;
      font-weight: 700;
      font-size: 1.1rem;
    }}

    .lucide-tile {{
      border-radius: 16px;
      padding: 8px 10px 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-decoration: none;
      transition: all 0.25s ease;
      width: 110px;
      height: 115px;
      justify-content: space-between;
      flex-shrink: 0;
    }}

    .lucide-tile:hover {{
      transform: translateY(-3px) scale(1.03);
      box-shadow: 0 8px 20px -2px rgba(15, 23, 42, 0.08);
    }}

    .badge-role-tag {{
      font-size: 0.68rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
      letter-spacing: 0.02em;
    }}

    .badge-role-tag.emblem-tag {{
      background: #f8fafc;
      color: #475569;
      border: 1px solid #e2e8f0;
    }}

    .badge-role-tag.lucide-tag {{
      background: rgba(255, 255, 255, 0.9);
      color: #334155;
      border: 1px solid rgba(0, 0, 0, 0.06);
    }}

    /* Mascot Info */
    .mascot-name {{
      font-weight: 700;
      font-size: 1.2rem;
      margin-bottom: 0.35rem;
      color: #0f172a;
    }}

    .mascot-project {{
      font-size: 0.82rem;
      color: #64748b;
      background: #f1f5f9;
      padding: 3px 12px;
      border-radius: 9999px;
      margin-bottom: 0.85rem;
      font-weight: 500;
      display: inline-block;
    }}

    .mascot-desc {{
      font-size: 0.875rem;
      color: #475569;
      line-height: 1.6;
      margin-bottom: 1.25rem;
      min-height: 54px;
      text-align: left;
      width: 100%;
    }}

    /* ==========================================================================
       Telemetry Pod (端點觀測艙 - 精緻對齊 UX-Deck 輕量卡片風格)
       ========================================================================== */
    .telemetry-pod {{
      width: 100%;
      margin-top: auto;
      background: #f8fafc;
      border: 1px solid #edf2f7;
      border-radius: 14px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .telemetry-stat-card {{
      display: flex;
      align-items: center;
      justify-content: space-around;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 8px 10px;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
    }}

    .telemetry-stat-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
    }}

    .stat-label {{
      font-size: 0.68rem;
      font-weight: 600;
      color: #64748b;
      letter-spacing: 0.02em;
    }}

    .stat-val {{
      font-family: "JetBrains Mono", monospace;
      font-weight: 700;
      font-size: 1rem;
      line-height: 1.2;
    }}

    .stat-views {{
      color: #0284c7; /* Brand Blue from UX-Deck */
    }}

    .stat-users {{
      color: #0f172a;
    }}

    .stat-divider {{
      width: 1px;
      height: 24px;
      background: #e2e8f0;
    }}

    /* Telemetry Action Buttons */
    .telemetry-actions {{
      display: flex;
      gap: 8px;
    }}

    .telemetry-btn {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 7px 10px;
      border-radius: 8px;
      font-size: 0.74rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      white-space: nowrap;
    }}

    .btn-dot-icon {{
      flex-shrink: 0;
    }}

    .btn-arrow {{
      font-size: 0.75rem;
      opacity: 0.8;
      transition: transform 0.15s ease;
    }}

    .telemetry-btn:hover .btn-arrow {{
      transform: translate(1px, -1px);
    }}

    /* Google Analytics Button (Crisp Emerald Green) */
    .btn-ga {{
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
    }}

    .btn-ga:hover {{
      background: #d1fae5;
      color: #065f46;
      border-color: #6ee7b7;
      box-shadow: 0 2px 6px rgba(16, 185, 129, 0.15);
    }}

    /* Amplitude Button (Crisp Royal Violet) */
    .btn-amplitude {{
      background: #faf5ff;
      color: #7c3aed;
      border: 1px solid #e9d5ff;
    }}

    .btn-amplitude:hover {{
      background: #f3e8ff;
      color: #6d28d9;
      border-color: #c4b5fd;
      box-shadow: 0 2px 6px rgba(124, 58, 237, 0.15);
    }}

    .btn-amplitude-disabled {{
      background: #f1f5f9;
      color: #94a3b8;
      border: 1px solid #e2e8f0;
      cursor: not-allowed;
      opacity: 0.85;
    }}

    /* Studio Footer */
    footer {{
      margin-top: 4rem;
      border-top: 1px solid var(--border-light);
      padding-top: 2.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      color: var(--text-dim);
      font-size: 0.85rem;
    }}

    footer a {{
      color: #0284c7;
      text-decoration: none;
      font-weight: 600;
    }}

    footer a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <!-- SVG Symbols Definition (From UX-Deck) -->
  {symbols_html}

  <div class="container">
    
    <!-- STUDIO HEADER (Aligned with UX-Deck) -->
    <header>
      <div class="header-badge">🏛️ Modern Emblem × ⚡ Lucide 雙軌體系 · 全端點遙測</div>
      <h1>Analytics-Deck</h1>
      <div class="subtitle">
        以極簡白底（White Basis）為視覺根基，結合十三隻專案象徵幾何吉祥物與全端點觀測艙。以 Google Analytics 4（Property: <code>p463673189</code>）作為全域流量基底，融合 Amplitude 事件行為觀測，落實「宏觀品牌勳章 × 微觀線性介面 × 實時數據監測」之完整閉環。
      </div>

      <div class="telemetry-nav-strip">
        <span class="live-url-pill">
          <span class="pill-pulse"></span> 數據同步：每日 4 次（每 6 小時排程）
        </span>
        <a href="https://analytics.google.com/analytics/web/#/a333479515p463673189/reports/intelligenthome?params=_u..nav%3Dmaui%26_u..realtimeTimePeriod%3D5&collectionId=user" target="_blank" rel="noopener noreferrer" class="live-url-pill" title="開啟 GA4 主控台 ↗">
          📈 GA4 總覽：Property <code>p463673189</code> ↗
        </a>
        <a href="https://wenchiehlee-ux.github.io/UX-Deck/" target="_blank" rel="noopener noreferrer" class="live-url-pill" title="造訪 UX-Deck 品牌設計中心 ↗">
          🎨 造訪 UX-Deck ↗
        </a>
        <span class="live-url-pill" style="margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748b;">
          最後同步：{last_sync}
        </span>
      </div>
    </header>

    <!-- CATEGORY FILTER BUTTONS -->
    <div class="filter-bar">
      <button class="filter-btn active" data-filter="all">全部端點 ({len(endpoints)})</button>
      <button class="filter-btn" data-filter="docs">生活日誌與知識庫</button>
      <button class="filter-btn" data-filter="saas">SaaS 與應用工具</button>
      <button class="filter-btn" data-filter="fintech">投資與量化研報</button>
      <button class="filter-btn" data-filter="infra">基礎設施與 NAS</button>
    </div>

    <!-- MASCOT CARDS GRID -->
    <div class="mascot-grid">
      {cards_html}
    </div>

    <!-- STUDIO FOOTER -->
    <footer>
      <div>Analytics-Deck · 全端點數據觀測中樞 · 品牌系統同源於 <a href="https://wenchiehlee-ux.github.io/UX-Deck/" target="_blank">UX-Deck</a></div>
      <div style="font-size: 0.78rem;">數據管道：GA4 Data API 每日 4 次自動定時快照 · 零延遲純靜態展示</div>
    </footer>

  </div>

  <script>
    // Client-side Category Filter
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        
        document.querySelectorAll('.mascot-card').forEach(card => {{
          if (filter === 'all' || card.dataset.category === filter) {{
            card.style.display = 'flex';
          }} else {{
            card.style.display = 'none';
          }}
        }});
      }});
    }});
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)

    # Also build to docs/ for GitHub Pages deployment
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DOCS_HTML, "w", encoding="utf-8") as f:
        f.write(template)

    # Sync docs/data/endpoints.json
    (DOCS_DIR / "data").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENDPOINTS_JSON, DOCS_DIR / "data" / "endpoints.json")

    print(f"[✓] Successfully built {OUTPUT_HTML} and {DOCS_HTML} ({len(template):,} bytes) with {len(endpoints)} cards.")

if __name__ == "__main__":
    build_index_html()
