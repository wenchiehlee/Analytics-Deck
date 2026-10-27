# 🌲 My-TW-Coverage 落地整合指南 (Deployment Guide)

本目錄提供 **My-TW-Coverage (台股個股深度調研雷達)** 的開箱即用前端樣式與設計元件套件。

---

## 📁 目錄結構

```text
deploy/tw-coverage/
├── DEPLOYMENT.md                  # 本落地指南
├── mkdocs.yml.snippet             # Material for MkDocs 設定範本
├── stylesheets/
│   └── extra.css                  # 個股調研評價卡、買賣評級膠囊、估值矩陣專用樣式
├── assets/
│   └── owl-mascot.svg             # 拍拍翅萌萌鴞 (Chubby Flapping Owlet 🦉) SVG Sprite
└── snippets/
    └── report-card-snippet.html   # Markdown 可直接引用的個股卡片 HTML 範本
```

---

## 🚀 快速安裝步驟 (3 步驟落地)

### 步驟 1：複製樣式表
將 `deploy/tw-coverage/stylesheets/extra.css` 複製至目標專案目錄：
```bash
# 複製樣式至目標專案
cp deploy/tw-coverage/stylesheets/extra.css ../My-TW-Coverage/docs/stylesheets/extra.css
```

### 步驟 2：引入吉祥物圖示
將 `deploy/tw-coverage/assets/owl-mascot.svg` 複製至目標專案的圖片/資源目錄：
```bash
cp deploy/tw-coverage/assets/owl-mascot.svg ../My-TW-Coverage/docs/assets/owl-mascot.svg
```

### 步驟 3：在 MkDocs 設定中啟用
在目標專案的 `mkdocs.yml` 加入：
```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: emerald
      accent: amber

extra_css:
  - stylesheets/extra.css
```

---

## 💡 如何在 Markdown 筆記中引用個股卡片

直接在各篇個股調研報告（如 `docs/stocks/2330.md`）上方貼入 [report-card-snippet.html](file:///C:/Users/WJLEE/SynologyDrive/NAS/github.com/UX-Deck/deploy/tw-coverage/snippets/report-card-snippet.html) 中的 HTML 結構：

- **評級類別**：
  - `tw-rating-buy`：`BUY ↗ 強力買進`
  - `tw-rating-outperform`：`OUTPERFORM ↗ 優於大盤`
  - `tw-rating-hold`：`HOLD → 維持中立`
  - `tw-rating-reduce`：`REDUCE ↘ 減碼觀望`
- **等寬數字**：現價、目標價、PER 與 EPS 會自動套用 `JetBrains Mono` 嚴格等寬對齊。
