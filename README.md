# 📊 Analytics-Deck · 全端點數據觀測中樞

> **落實「宏觀品牌勳章 × 微觀線性介面 × 實時數據監測」之完整閉環**  
> 承襲 [UX-Deck](https://wenchiehlee-ux.github.io/UX-Deck/) 的十三隻專案象徵幾何吉祥物（Settled Geometric Mascots），為全生態系 13 個入口端點提供統一的 **流量遙測 (GA4)** 與 **產品行為觀測 (Amplitude)** 儀表板。

---

## 🌟 核心特色 (Core Features)

1. **同源視覺體系 (100% Aligned with UX-Deck)**：
   - 完整繼承極簡白底（White Basis）與 13 隻幾何吉祥物雙軌舞台（Modern Emblem 官方勳章 × Lucide 介面線性圖標）。
   - 保留各站點的原站連結與 Showcase 原貌。

2. **雙軌端點遙測艙 (Dual-Metric Telemetry Pod)**：
   - 👁️ **全站累積瀏覽量 (Lifetime Views)**：如 `20,595 次`（對齊歷史數據，取代舊有第三方計數器）。
   - 👥 **30 天月活躍訪客 (30-Day Active Users)**：如 `1.2k 月活`，掌握最新真實讀者活力。

3. **雙分析引擎整合 (GA4 × Amplitude)**：
   - 🟢 **Google Analytics (GA4)**：直達核心主控台 Property [`p463673189`](https://analytics.google.com/analytics/web/#/a333479515p463673189/reports/intelligenthome?params=_u..nav%3Dmaui%26_u..realtimeTimePeriod%3D5&collectionId=user)，以統一架構管理全生態系流量。
   - 🟣 **Amplitude Events**：專為 SaaS 與互動型工具端點（如 GoogleAlertManager、YoutubeAudio.Fetch 等）量身打造，支援漸進式點亮事件漏斗。

4. **每日 4 次自動同步 (4 Renewals / Day)**：
   - 透過 GitHub Actions 排程（`cron: "0 */6 * * *"`，每 6 小時一次），自動透過 GA4 Data API 抓取最新數據並寫入 `data/endpoints.json`，實現 **0 延遲純靜態展示**。

5. **極簡擴充性 (Easy Expansion via CLI)**：
   - 當 `../UX-Deck` 新增第 14、15 隻吉祥物時，僅需執行單一指令即可自動同步圖標資產並智能合併配置檔。

---

## 🐾 目前納管的 13 隻幾何吉祥物端點

| # | 吉祥物 | 專案名稱 (Project) | 類型 | 預設 GA4 / Telemetry | Amplitude |
|---|---|---|---|---|---|
| **1** | **幾何林鹿 🦌** | `mkdocs-life` (生活日誌) | Docs | `20,595` 累計 · `1.2k` 月活 | 規劃中 |
| **2** | **破曉警報鳥 🐦** | `GoogleAlertManager` (SaaS) | SaaS | `1,580` 累計 · `380` 月活 | 🟢 啟用中 |
| **3** | **聲波座頭鯨 🐋** | `YoutubeAudio.Fetch` (Podcast 萃取) | SaaS | `1,580` 累計 · `380` 月活 | 🟢 啟用中 |
| **4** | **貨櫃藍鯨 🐳** | `Docker-Deck` (映像目錄) | Infra | `1,580` 累計 · `380` 月活 | 規劃中 |
| **5** | **幾何狂牛 🐂** | `mkdocs-investment` (多頭攻堅) | Fintech | `1,580` 累計 · `380` 月活 | 規劃中 |
| **6** | **北歐守護熊 🐻** | `mkdocs-investment` (防禦避險) | Fintech | `1,580` 累計 · `380` 月活 | 規劃中 |
| **7** | **客廳小管家 柴柴 🐕**| `HomeAssistant` (Android TV) | Infra | `1,580` 累計 · `380` 月活 | 規劃中 |
| **8** | **敏捷守護貓 🐱** | `wenchiehlee.synology.me` (NAS) | Infra | `1,580` 累計 · `380` 月活 | 規劃中 |
| **9** | **拍拍翅萌萌鴞 🦉** | `My-TW-Coverage` (台股覆蓋) | Fintech | `1,580` 累計 · `380` 月活 | 規劃中 |
| **10**| **領航雄鷹 🦅** | `InvestorConference` (法說會庫) | Fintech | `1,580` 累計 · `380` 月活 | 規劃中 |
| **11**| **幾何黑天鵝 🦢** | `VIX` (全球黑天鵝雷達) | Fintech | `1,580` 累計 · `380` 月活 | 規劃中 |
| **12**| **採集松鼠 🐿️** | `Synology-Photo-Tagger` (相片標籤) | SaaS | `1,580` 累計 · `380` 月活 | 🟢 啟用中 |
| **13**| **敏捷白兔 🐇** | `Skill-Deck` (共享技能庫) | Docs | `1,580` 累計 · `380` 月活 | 規劃中 |

---

## 🛠️ 開發與維護指南 (CLI Operations)

### 1. 當 UX-Deck 增加新吉祥物時（一鍵同步）
```bash
python scripts/sync_from_ux_deck.py
```
- 自動拷貝 `../UX-Deck/tokens/` 內新增加的 SVG 勳章與線性圖標。
- 提取最新的 SVG Symbol 定義。
- 安全合併 `data/endpoints.json`（保留所有已配置的流量數據與 GA 設定，僅補充新端點）。
- 自動重新生成 `index.html`。

### 2. 本地抓取最新 GA4 數據
```bash
# 乾跑模式 (刷新時間戳並維持快照)
python scripts/fetch_analytics.py --dry-run

# 線上正式模式 (需配置 GA4 服務帳戶環境變數)
export GA4_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
python scripts/fetch_analytics.py
```

### 3. 本地手動編譯靜態頁面
```bash
python scripts/build_page.py
```

---

## 📂 檔案目錄架構 (Directory Tree)

```
Analytics-Deck/
├── .github/
│   └── workflows/
│       └── renew-analytics.yml    # 每日 4 次自動更新 GA4 數據的工作流
├── data/
│   ├── endpoints.json             # 核心配置：13 個端點與流量遙測數據庫
│   └── svg_symbols.html           # 12+ 款幾何吉祥物 Lucide 向量 Symbol 庫
├── scripts/
│   ├── build_page.py              # 靜態 HTML 生成器
│   ├── fetch_analytics.py         # GA4 Data API 每日定時抓取腳本
│   └── sync_from_ux_deck.py       # 從同層 UX-Deck 一鍵無損同步腳本
├── tokens/
│   ├── favicons/                  # 端點圖標
│   ├── icons/
│   │   ├── lucide/                # 微觀介面線性 SVG
│   │   └── modern-emblem/         # 宏觀品牌紋章 SVG
│   ├── design-tokens.json         # 設計 Token 規格
│   └── tokens.css                 # 樣式定義
├── favicon.svg / .ico / .png      # 站點圖標
├── index.html                     # 獨立展示主頁（含分類篩選與觀測艙）
├── LICENSE                        # MIT License
└── README.md                      # 本說明文件
```
