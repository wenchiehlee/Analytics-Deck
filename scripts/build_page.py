#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_page.py
Generates the complete, standalone index.html for Analytics-Deck.
Reads data/endpoints.json and data/svg_symbols.html.
Ensures 100% visual, layout, and endpoint consistency with UX-Deck.
Supports Plan A Smart Conditional Endpoints (3 buttons when pages==live, 4 buttons when pages!=live).
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
    views = analytics.get("views_total")
    if views is None or views == "" or views == "---":
        views_formatted = "---"
    elif isinstance(views, (int, float)):
        views_formatted = f"{views:,}"
    else:
        views_formatted = str(views)

    active = analytics.get("active_users_30d")
    if active is None or active == "" or active == "---":
        active_30d = "---"
    else:
        active_30d = str(active)

    category = analytics.get("category", "docs")
    
    ga4 = analytics.get("ga4", {})
    ga4_url = ga4.get("dashboard_url", "https://analytics.google.com/analytics/web/")
    
    amp = analytics.get("amplitude", {})
    amp_enabled = amp.get("enabled", False)
    amp_status = amp.get("status", "planned")
    amp_url = amp.get("dashboard_url", "#")
    amp_label = "Amplitude" if amp_enabled else "Amplitude (規劃中)"

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

    emblem_href = ep.get("emblem_href") or ep.get("emblem_src", "")
    lucide_href = ep.get("lucide_href") or ep.get("live_url", "#")

    # Smart Conditional Endpoints (Plan A)
    showcase_url = ep.get("showcase_url", "./showcases.html")
    repo_url = ep.get("repo_url", "#")
    pages_url = ep.get("pages_url", "")
    live_url = ep.get("live_url", "#")
    separate_live = ep.get("separate_live", False) or (bool(pages_url) and pages_url != live_url)

    ep_count_class = "ep-count-4" if separate_live else "ep-count-3"

    pages_button_html = ""
    if separate_live and pages_url:
        pages_button_html = f"""
        <a class="endpoint-pill ep-pages" href="{pages_url}" rel="noopener noreferrer" target="_blank" title="🚀 造訪 GitHub Pages 靜態專案頁 ↗">
          <span class="ep-icon">🚀</span>
          <span class="ep-label">Pages</span>
        </a>"""

    repo_title = "📦 前往 GitHub 原始碼儲存庫 ↗"
    live_title = "🌐 造訪線上正式站點 ↗"
    if "tail28f10" in live_url:
        live_title = "🌐 前往 Tailscale 私網即時 Web 服務 ↗"
    elif "synology.me" in live_url:
        live_title = "🌐 前往 Synology NAS 登入入口 ↗"
    elif "YoutubeAudio" in live_url or "channel=" in live_url:
        live_title = "🌐 造訪線上音訊播放正式站點 ↗"
    elif "dockers" in live_url:
        live_title = "🌐 前往 Docker 映像與容器目錄 ↗"
    elif "pages" in live_url or "github.io" in live_url:
        live_title = "🌐 造訪線上正式站點 (GitHub Pages) ↗"

    card_html = f"""
    <div class="mascot-card {card_class}" data-category="{category}">
      <div class="mascot-duo-stage">
        <a href="{emblem_href}" class="emblem-tile" target="_blank" rel="noopener noreferrer" title="查看官方紋章向量 SVG 原始碼 ↗">
          <img src="{ep.get('emblem_src', '')}" alt="{ep.get('emblem_alt', '')}" class="emblem-thumb">
          <span class="badge-role-tag emblem-tag">🏛️ 官方紋章</span>
        </a>
        <div class="duo-divider">
          <span class="duo-arrow">⇄</span>
        </div>
        <a href="{lucide_href}" class="lucide-tile {lucide_wrapper}" target="_blank" rel="noopener noreferrer" title="查看線性圖標向量 SVG 原始碼 ↗">
          {icon_markup}
          <span class="badge-role-tag lucide-tag">⚡ 介面線性</span>
        </a>
      </div>

      <div class="mascot-name">{ep.get('name', '')}</div>
      <div class="mascot-project">{ep.get('project', '')}</div>
      <div class="mascot-desc">
        {ep.get('desc_html', '')}
      </div>

      <!-- SMART CONDITIONAL ENDPOINTS (PLAN A) -->
      <div class="card-endpoints {ep_count_class}">
        <a class="endpoint-pill ep-showcase" href="{showcase_url}" rel="noopener noreferrer" target="_blank" title="🎨 查看 UX-Deck 設計展示（色彩光譜、字體與元件）">
          <span class="ep-icon">🎨</span>
          <span class="ep-label">Showcase</span>
        </a>
        <a class="endpoint-pill ep-repo" href="{repo_url}" rel="noopener noreferrer" target="_blank" title="{repo_title}">
          <span class="ep-icon">📦</span>
          <span class="ep-label">Repo</span>
        </a>{pages_button_html}
        <a class="endpoint-pill ep-live" href="{live_url}" rel="noopener noreferrer" target="_blank" title="{live_title}">
          <span class="ep-icon">🌐</span>
          <span class="ep-label">Live</span>
        </a>
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

    <footer class="deck-family-footer">
      
      <!-- STRICT 7 CARDS IN ONE ROW -->
      <div class="deck-cards-row">

        <!-- 1. UX-Deck -->
        <article class="deck-card theme-ux">
          <div class="deck-card-head">
            <span class="deck-avatar">🦌</span>
            <span class="deck-card-title">UX-Deck</span>
            <span class="deck-tag">Design</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">幾何吉祥物</span>
              <span class="stat-val">13 Mascots</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">涵蓋端點</span>
              <span class="stat-val">9+ Hubs · AA</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee-ux.github.io/UX-Deck/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee-ux/UX-Deck" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

        <!-- 2. Skill-Deck -->
        <article class="deck-card theme-skill">
          <div class="deck-card-head">
            <span class="deck-avatar">🐇</span>
            <span class="deck-card-title">Skill-Deck</span>
            <span class="deck-tag">Registry</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">收錄技能</span>
              <span class="stat-val">60+ Skills</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">分類 / 下游</span>
              <span class="stat-val">8 Cats · 8+</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee.github.io/skills/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee/skills" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

        <!-- 3. Analytics-Deck -->
        <article class="deck-card theme-analytics">
          <div class="deck-card-head">
            <span class="deck-avatar">📊</span>
            <span class="deck-card-title">Analytics-Deck</span>
            <span class="deck-tag">Telemetry</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">全站累積</span>
              <span class="stat-val">20.5k Views</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">觀測 / 頻率</span>
              <span class="stat-val">13 Pods · 4x/D</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee.github.io/Analytics-Deck/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee/Analytics-Deck" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

        <!-- 4. Pipeline-Deck -->
        <article class="deck-card theme-pipeline">
          <div class="deck-card-head">
            <span class="deck-avatar">⚙️</span>
            <span class="deck-card-title">Pipeline-Deck</span>
            <span class="deck-tag">Workflow</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">自動化架構</span>
              <span class="stat-val">CI/CD Engine</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">排程調度</span>
              <span class="stat-val">GitOps · Actions</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee.github.io/Pipeline-Deck/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee/Pipeline-Deck" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

        <!-- 5. Data-Deck -->
        <article class="deck-card theme-data">
          <div class="deck-card-head">
            <span class="deck-avatar">📈</span>
            <span class="deck-card-title">Data-Deck</span>
            <span class="deck-tag">Finance</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">核心管線</span>
              <span class="stat-val">89 Pipelines</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">個股 / 來源</span>
              <span class="stat-val">1,735 · 16 Src</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee-money.github.io/biztrends.TW/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee-money/biztrends.TW" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

        <!-- 6. Llm-Deck -->
        <article class="deck-card theme-llm">
          <div class="deck-card-head">
            <span class="deck-avatar">🧠</span>
            <span class="deck-card-title">Llm-Deck</span>
            <span class="deck-tag">Inference</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">總調用量</span>
              <span class="stat-val">25k+ Calls</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">路由 / 提供</span>
              <span class="stat-val">3 Provider · AI</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee.github.io/llm/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee/llm" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

        <!-- 7. Docker-Deck -->
        <article class="deck-card theme-docker">
          <div class="deck-card-head">
            <span class="deck-avatar">🐳</span>
            <span class="deck-card-title">Docker-Deck</span>
            <span class="deck-tag">Catalog</span>
          </div>
          <div class="deck-numbers-compact">
            <div class="stat-line">
              <span class="stat-lbl">正式映像</span>
              <span class="stat-val">3 Images</span>
            </div>
            <div class="stat-line">
              <span class="stat-lbl">累計拉取</span>
              <span class="stat-val">3,600+ Pulls</span>
            </div>
          </div>
          <div class="deck-actions-compact">
            <a href="https://wenchiehlee.github.io/dockers/" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-portal">
              <span>Portal</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </a>
            <a href="https://github.com/wenchiehlee/dockers" target="_blank" rel="noopener noreferrer" class="deck-btn deck-btn-repo">
              <span>Repo</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
          </div>
        </article>

      </div>

    </footer>

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
