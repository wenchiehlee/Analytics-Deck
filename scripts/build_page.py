#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_page.py
Generates the complete, standalone index.html for Analytics-Deck.
Reads data/endpoints.json and data/svg_symbols.html.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
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

    if symbol_id:
        icon_markup = f"""<svg class="ux-icon ux-icon-xl ux-icon-{symbol_id.replace('icon-', '').split('-')[0]}">
          <use href="#{symbol_id}"></use>
        </svg>"""
    elif inline_svg:
        icon_markup = inline_svg
    else:
        icon_markup = """<svg class="ux-icon ux-icon-xl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
        </svg>"""

    card_class = ep.get("card_class", "card-deer")
    lucide_wrapper = ep.get("lucide_wrapper_class", "wrapper-deer")

    card_html = f"""
    <div class="mascot-card {card_class}" data-category="{category}">
      <div class="mascot-duo-stage">
        <a href="{ep.get('showcase_url', '#')}" class="emblem-tile" target="_blank" rel="noopener noreferrer" title="查看 {ep.get('name')} 的品牌紋章展示 ↗">
          <img src="{ep.get('emblem_src', '')}" alt="{ep.get('emblem_alt', '')}" class="emblem-thumb">
          <span class="badge-role-tag emblem-tag">🏛️ 官方紋章</span>
        </a>
        <div class="duo-divider">
          <span class="duo-arrow">⇄</span>
        </div>
        <a href="{ep.get('live_url', '#')}" class="lucide-tile {lucide_wrapper}" target="_blank" rel="noopener noreferrer" title="造訪 {ep.get('project')} 原站 ↗">
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
        <div class="telemetry-header">
          <span class="telemetry-badge">📊 端點觀測數據</span>
          <span class="telemetry-category-pill pill-{category}">{category.upper()}</span>
        </div>
        <div class="telemetry-stat-card">
          <div class="telemetry-stat-item">
            <span class="stat-icon">👁️</span>
            <div class="stat-meta">
              <span class="stat-label">本站訪問量</span>
              <strong class="stat-val highlight">{views_formatted}</strong>
            </div>
          </div>
          <div class="stat-divider"></div>
          <div class="telemetry-stat-item">
            <span class="stat-icon">👥</span>
            <div class="stat-meta">
              <span class="stat-label">30D 月活躍</span>
              <strong class="stat-val">{active_30d}</strong>
            </div>
          </div>
        </div>

        <div class="telemetry-actions">
          <a href="{ga4_url}" class="telemetry-btn btn-ga" target="_blank" rel="noopener noreferrer" title="開啟 Google Analytics 4 主控台報表 ↗">
            <svg class="btn-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/>
            </svg>
            <span>Google Analytics</span>
          </a>

          {'<a href="' + amp_url + '" class="telemetry-btn btn-amplitude" target="_blank" rel="noopener noreferrer" title="開啟 Amplitude 自訂事件儀表板 ↗">' if amp_enabled else '<span class="telemetry-btn btn-amplitude-disabled" title="此端點尚未配置 Amplitude 事件追蹤">' }
            <svg class="btn-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
            </svg>
            <span>{amp_label}</span>
          {'</a>' if amp_enabled else '</span>'}
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
  
  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="./favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="./favicon.png">
  <link rel="shortcut icon" href="./favicon.ico">

  <!-- Design Tokens -->
  <link rel="stylesheet" href="./tokens/tokens.css">

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Noto+Sans+TC:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

  <style>
    /* Baseline Reset & Palette Alignment (Inherited from UX-Deck White Basis) */
    :root {{
      --deck-bg: #f8fafc;
      --card-bg: #ffffff;
      --border-subtle: #e2e8f0;
      --border-accent: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --ga-color: #059669;
      --ga-bg: #ecfdf5;
      --ga-border: #a7f3d0;
      --amp-color: #7c3aed;
      --amp-bg: #f5f3ff;
      --amp-border: #ddd6fe;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--deck-bg);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      padding-bottom: 5rem;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem;
    }}

    /* Header Section */
    .deck-header {{
      background: #ffffff;
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 2.5rem 2rem;
      margin-bottom: 2rem;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
    }}

    .deck-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 12px;
    }}

    .deck-logo-badge {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, #0284c7, #2563eb);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 24px;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
    }}

    .deck-title {{
      font-size: 1.85rem;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.02em;
    }}

    .deck-subtitle {{
      color: var(--text-muted);
      font-size: 1rem;
      max-width: 860px;
      line-height: 1.65;
      margin-bottom: 1.5rem;
    }}

    .deck-meta-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      padding-top: 1.25rem;
      border-top: 1px solid var(--border-subtle);
    }}

    .meta-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: #f1f5f9;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 600;
      color: #334155;
    }}

    .meta-chip.chip-sync {{
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
    }}

    .meta-chip.chip-ga {{
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
    }}

    .pulse-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Filter Bar */
    .filter-bar {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 2rem;
    }}

    .filter-btn {{
      background: #ffffff;
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 8px 16px;
      font-size: 0.88rem;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .filter-btn:hover {{
      background: #f8fafc;
      border-color: #cbd5e1;
    }}

    .filter-btn.active {{
      background: #0f172a;
      color: #ffffff;
      border-color: #0f172a;
    }}

    /* Mascot Grid Layout */
    .mascot-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
      gap: 1.5rem;
    }}

    .mascot-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}

    .mascot-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      border-color: #cbd5e1;
    }}

    /* Duo Stage (From UX-Deck) */
    .mascot-duo-stage {{
      display: flex;
      align-items: center;
      justify-content: space-around;
      background: #f8fafc;
      border: 1px solid #f1f5f9;
      border-radius: 12px;
      padding: 12px 8px;
      margin-bottom: 14px;
    }}

    .emblem-tile, .lucide-tile {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      padding: 6px;
      border-radius: 8px;
      transition: transform 0.15s ease;
    }}

    .emblem-tile:hover, .lucide-tile:hover {{
      transform: scale(1.05);
    }}

    .emblem-thumb {{
      width: 58px;
      height: 58px;
      object-fit: contain;
    }}

    .ux-icon {{
      width: 50px;
      height: 50px;
      stroke-width: 1.8;
    }}

    .badge-role-tag {{
      font-size: 0.68rem;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }}

    .emblem-tag {{
      background: #f1f5f9;
      color: #475569;
    }}

    .lucide-tag {{
      background: #eff6ff;
      color: #2563eb;
    }}

    .duo-arrow {{
      color: #94a3b8;
      font-size: 1.1rem;
    }}

    /* Mascot Info */
    .mascot-name {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 2px;
    }}

    .mascot-project {{
      font-size: 0.85rem;
      color: #2563eb;
      font-weight: 600;
      margin-bottom: 8px;
    }}

    .mascot-desc {{
      font-size: 0.83rem;
      color: #475569;
      line-height: 1.5;
      margin-bottom: 14px;
      min-height: 48px;
    }}

    /* Telemetry Pod (觀測艙) */
    .telemetry-pod {{
      margin-top: auto;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 12px;
    }}

    .telemetry-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}

    .telemetry-badge {{
      font-size: 0.72rem;
      font-weight: 700;
      color: #64748b;
      letter-spacing: 0.03em;
    }}

    .telemetry-category-pill {{
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }}

    .pill-docs {{ background: #e0f2fe; color: #0369a1; }}
    .pill-saas {{ background: #f3e8ff; color: #7e22ce; }}
    .pill-fintech {{ background: #fef3c7; color: #b45309; }}
    .pill-infra {{ background: #f1f5f9; color: #475569; }}

    .telemetry-stat-card {{
      display: flex;
      align-items: center;
      justify-content: space-around;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 8px 6px;
      margin-bottom: 10px;
    }}

    .telemetry-stat-item {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .stat-icon {{
      font-size: 1.1rem;
    }}

    .stat-meta {{
      display: flex;
      flex-direction: column;
    }}

    .stat-label {{
      font-size: 0.68rem;
      color: #64748b;
      font-weight: 500;
    }}

    .stat-val {{
      font-size: 0.95rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: #0f172a;
    }}

    .stat-val.highlight {{
      color: #0284c7;
    }}

    .stat-divider {{
      width: 1px;
      height: 24px;
      background: #e2e8f0;
    }}

    /* Action Buttons */
    .telemetry-actions {{
      display: flex;
      gap: 6px;
    }}

    .telemetry-btn {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 6px 8px;
      border-radius: 6px;
      font-size: 0.73rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.15s ease;
    }}

    .btn-ga {{
      background: var(--ga-bg);
      color: var(--ga-color);
      border: 1px solid var(--ga-border);
    }}

    .btn-ga:hover {{
      background: #d1fae5;
    }}

    .btn-amplitude {{
      background: var(--amp-bg);
      color: var(--amp-color);
      border: 1px solid var(--amp-border);
    }}

    .btn-amplitude:hover {{
      background: #ede9fe;
    }}

    .btn-amplitude-disabled {{
      background: #f1f5f9;
      color: #94a3b8;
      border: 1px solid #e2e8f0;
      cursor: not-allowed;
    }}

    /* Footer */
    .deck-footer {{
      margin-top: 3.5rem;
      text-align: center;
      padding-top: 2rem;
      border-top: 1px solid var(--border-subtle);
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    .deck-footer a {{
      color: #0284c7;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>

  <!-- SVG Symbols Definition -->
  {symbols_html}

  <div class="container">
    
    <!-- HEADER -->
    <header class="deck-header">
      <div class="deck-brand">
        <div class="deck-logo-badge">📊</div>
        <div>
          <h1 class="deck-title">Analytics-Deck · 全端點數據觀測中樞</h1>
        </div>
      </div>
      <p class="deck-subtitle">
        以極簡白底（White Basis）為視覺根基，結合十三隻專案象徵幾何吉祥物與全端點觀測艙。以 Google Analytics 4（Property: <code>p463673189</code>）作為全域流量基底，融合 Amplitude 事件行為觀測，落實「宏觀品牌勳章 × 微觀線性介面 × 實時數據監測」之完整閉環。
      </p>

      <div class="deck-meta-strip">
        <span class="meta-chip chip-sync">
          <span class="pulse-dot"></span> 數據同步：每日 4 次（每 6 小時排程）
        </span>
        <span class="meta-chip chip-ga">
          📈 GA4 總覽：Property <code>p463673189</code>
        </span>
        <span class="meta-chip">
          🐾 納管端點：共 {len(endpoints)} 隻幾何吉祥物
        </span>
        <span class="meta-chip" style="margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">
          最後同步時間：{last_sync}
        </span>
      </div>
    </header>

    <!-- FILTER BUTTONS -->
    <div class="filter-bar">
      <button class="filter-btn active" data-filter="all">🌟 全部端點 ({len(endpoints)})</button>
      <button class="filter-btn" data-filter="docs">📚 生活日誌與文檔</button>
      <button class="filter-btn" data-filter="saas">⚡ SaaS 與應用工具</button>
      <button class="filter-btn" data-filter="fintech">📈 投資與量化研報</button>
      <button class="filter-btn" data-filter="infra">🖥️ 基礎設施與 NAS</button>
    </div>

    <!-- MASCOT CARDS GRID -->
    <div class="mascot-grid">
      {cards_html}
    </div>

    <!-- FOOTER -->
    <footer class="deck-footer">
      <p>Analytics-Deck · 全端點遙測中樞 · 品牌系統同源於 <a href="../UX-Deck/index.html" target="_blank">UX-Deck</a></p>
      <p style="margin-top: 4px; font-size: 0.78rem;">數據管道：GA4 Data API 每日 4 次自動定時抓取並快照 · 零延遲靜態展示</p>
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
    import shutil
    shutil.copy2(ENDPOINTS_JSON, DOCS_DIR / "data" / "endpoints.json")

    print(f"[✓] Successfully built {OUTPUT_HTML} and {DOCS_HTML} ({len(template):,} bytes) with {len(endpoints)} cards.")

if __name__ == "__main__":
    build_index_html()
