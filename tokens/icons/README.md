# UX-Deck Iconography Design System (三維風格動物圖標資產庫（Three-Track Style System）)

本目錄收錄 **UX-Deck 生態系** 跨端點使用之核心向量吉祥物與備選動物圖庫，採用 **三維風格架構（Three-Track Style Architecture）**：

1. **`lucide/`**：**極簡單色線性風格（Minimal Line Art）**
   - 規格：標準 `24×24` 畫布、`1.8px ~ 2.0px` 統一線寬、圓角轉折與端點（Round stroke cap & join）。
   - 適用場景：主導航列（Header / Menubar）、深色 HUD 玻璃面板、Favicon、按鈕與文字並列之微小圖示（16px ~ 32px）。
   - 包含：目前已上線之各端點吉祥物（幾何林鹿、破曉鳥、座頭鯨、守護牛、萌萌鴞、守護貓、客廳柴柴），以及備選庫（白兔、烏龜、松鼠、天鵝、灰犀牛、雄鷹、海豚、雄獅、巨象、駱駝、防禦熊）。

2. **`modern-emblem/`**：**現代商標徽章風格（Modern Emblem Art · 來自 3034.eps）**
   - 規格：完整貝茲曲線色塊填色（CMYK -> RGB 向量填色）、幾何底塊徽章搭配、高對比標誌剪影。
   - 適用場景：Repo 封面大卡（Hero Showcase）、專案介紹大徽章、高解析度彩色 Banner、獨立品牌 Logo 展示。
   - 包含：天鵝 (`emblem-swan.svg`)、杜賓犬 (`emblem-dog.svg`)、灰犀牛 (`emblem-rhino.svg`)、破曉雄鷹 (`emblem-eagle.svg`)、海豚 (`emblem-dolphin.svg`)、雄獅 (`emblem-lion.svg`)、巨象 (`emblem-elephant.svg`)、駱駝 (`emblem-camel.svg`)、防禦熊 (`emblem-bear.svg`)。

---

3. **kawaii-chibi/**：**日系 Q 版萌寵風格（Kawaii Chibi Mascot）**
   - 規格：大頭身比 (1:1)、招牌粉嫩治癒腮紅、柔和深巧克力棕/炭灰圓角粗描邊、透明 PNG/SVG 封裝。
   - 適用場景：友善新功能引導 (Onboarding)、彩蛋、節慶主題、溫馨社群或輔助小精靈展示。
   - 包含：小獅王 (chibi-lion.svg)、長頸鹿 (chibi-giraffe.svg)、小象 (chibi-elephant.svg)、小猴 (chibi-monkey.svg)、小斑馬 (chibi-zebra.svg)、小跳虎 (chibi-tiger.svg)、深灰河馬 (chibi-hippo.svg)、淡藍河馬 (chibi-hippo_lite.svg)。

---

## 📂 檔案目錄架構

```
tokens/icons/
├── README.md                      # 本說明文件
├── animal-icons.svg               # SVG Symbol 集合檔案 (供 HTML <use> 直接引用)
├── lucide/                        # 24 款 Lucide 極簡線性 SVG
│   ├── lucide-deer.svg            # (已使用: mkdocs-life 幾何林鹿)
│   ├── lucide-bird.svg            # (已使用: GoogleAlertManager 破曉鳥)
│   ├── lucide-whale.svg           # (已使用: YoutubeAudio.Fetch 座頭鯨)
│   ├── lucide-docker-whale.svg    # (已使用: Docker-Deck 貨櫃藍鯨)
│   ├── lucide-bull.svg            # (已使用: mkdocs-investment 守護牛)
│   ├── lucide-owl.svg             # (已使用: My-TW-Coverage 萌萌鴞)
│   ├── lucide-cat.svg             # (已使用: NAS 守護貓)
│   ├── lucide-dog.svg             # (已使用: HomeAssistant TV 客廳柴柴)
│   ├── lucide-rabbit.svg          # (已使用/候選: InvestorConference 敏捷白兔)
│   ├── lucide-swan.svg            # (已使用/候選: VIX 黑天鵝)
│   ├── lucide-rhino.svg           # (已使用/候選: VIX 灰犀牛)
│   ├── lucide-eagle.svg           # (已使用/候選: InvestorConference 領航雄鷹)
│   ├── lucide-turtle.svg          # (候選: 防禦玄龜)
│   ├── lucide-squirrel.svg        # (候選: 數據松鼠)
│   ├── lucide-dolphin.svg         # (候選: 靈活海豚)
│   ├── lucide-lion.svg            # (候選: 王者雄獅)
│   ├── lucide-elephant.svg        # (候選: 穩健巨象)
│   ├── lucide-camel.svg           # (候選: 耐力駱駝)
│   └── lucide-bear.svg            # (候選: 防禦巨熊)
│
├── modern-emblem/                 # 3034.eps 與端點專用現代商標徽章 SVG (無太陽版雄鷹)
│   ├── emblem-swan.svg
│   ├── emblem-docker-whale.svg   # Docker-Deck 貨櫃藍鯨
│   ├── emblem-rhino.svg
│   ├── emblem-eagle.svg           # (已剔除背景太陽日輪)
│   ├── emblem-eagle-pure.svg      # (純雄鷹主體向量，無字無太陽)
│   ├── emblem-dog.svg
│   ├── emblem-dolphin.svg
│   ├── emblem-lion.svg
│   ├── emblem-elephant.svg
│   ├── emblem-camel.svg
│   └── emblem-bear.svg
│
└── kawaii-chibi/                  # 8 款日系 Q 版萌系透明圖標 (SVG/PNG)
    ├── chibi-lion.svg / .png
    ├── chibi-giraffe.svg / .png
    ├── chibi-elephant.svg / .png
    ├── chibi-monkey.svg / .png
    ├── chibi-zebra.svg / .png
    ├── chibi-tiger.svg / .png
    ├── chibi-hippo.svg / .png
    └── chibi-hippo_lite.svg / .png
    ├── emblem-swan.svg            # (VIX 黑天鵝徽章)
    ├── emblem-rhino.svg           # (VIX 灰犀牛徽章)
    ├── emblem-eagle.svg           # (InvestorConference 破曉雄鷹徽章)
    ├── emblem-dog.svg             # (杜賓守衛獵犬徽章)
    ├── emblem-dolphin.svg         # (流動性海豚徽章)
    ├── emblem-lion.svg            # (龍頭雄獅徽章)
    ├── emblem-elephant.svg        # (資產巨象徽章)
    ├── emblem-camel.svg           # (耐力駱駝徽章)
    └── emblem-bear.svg            # (抗跌防禦熊徽章)
```

---

## 🎨 快速使用範例

### 1. 引用 Lucide 極簡線性圖標
```html
<img src="tokens/icons/lucide/lucide-deer.svg" width="24" height="24" alt="Life Deer" />
```

### 2. 引用 Modern Emblem 彩色徽章
```html
<img src="tokens/icons/modern-emblem/emblem-rhino.svg" width="120" height="90" alt="VIX Rhino" />
```
