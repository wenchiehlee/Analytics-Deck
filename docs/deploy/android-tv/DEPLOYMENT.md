# HomeAssistant on Android TV: 10-Foot Frosted HUD 完整部署指南

本指南提供將 **UX-Deck 10-Foot 客廳毛玻璃 HUD（Card 7）** 完整部署至真實客廳 **Android TV (1F / 2F)** 與 **Home Assistant** 的標準作業程序。

---

## 📐 10 英呎電視介面設計準則

| 設計維度 | 規範標準 | 理由與效益 |
| :--- | :--- | :--- |
| **觀看距離** | 3 ~ 4 公尺客廳沙發視角 | 標題 `20pt` (約 26~32px)，內文 `16pt`，高對比白字配深色毛玻璃 |
| **字體體系** | `Zen Maru Gothic` (日雜圓體 700) + `Comfortaa` | 溫暖柔和、視覺親和力高，搭配彩色 3D Emoji（🔔, 🧺, 🐾） |
| **停駐位置** | 螢幕右上角 (`position: 0` = TopRight) | 完全避開中央視線主體與底部電影字幕條（零視覺干擾） |
| **背景透光度** | 60% 透光 Cyber Dark Slate (`#660f172a` / 40% 不透明) | 兼顧文字極高辨識度與電視畫面穿透感 |
| **象徵吉祥物** | 客廳守護靈犬 🐕 (`#icon-sentinel-tv`) | 暖心赤柴金琥珀色 (`#d97706`)，守護居家安防與生活進度 |
| **邊角效果** | **18px ~ 24px 平滑真圓角** (透過 Solution B 實現) | 圓角外部 100% 透明無白框，極致客廳美感 |

---

## 🚀 兩大實體部署方案選擇

### 方案 B（首選推薦）：極致美感 18px 圓角透明 HUD (Solution B)
- **技術原理**：透過 32-bit RGBA 透明 PNG 預渲染技術，PiPup 設定 `backgroundColor: "#00000000"`（100% 全透明底）。
- **優勢**：
  - **100% 杜絕 Android WebView 預設白畫布產生的白框瑕疵**。
  - 真正實現 **18px 平滑圓角**、**柔和發光邊框**、**日雜圓體** 與 **赤柴吉祥物 🐕**。
  - 本地快取預渲染 PNG，零延遲瞬間彈出。

### 方案 A：極簡原生直角 Scrim (Mode A)
- **技術原理**：直接使用 PiPup 原生 TextView 與背景色彩值 `#660f172a`。
- **優勢**：零外部依賴、純文字即時傳遞。受限於 Android 原生限制為俐落的 90° 直角。

---

## 🛠️ 完整部署步驟

### 步驟 1：部署靜態資源至 Home Assistant `/config/www/`

將本目錄下的 `www/` 內所有檔案（包含 `huds/` 7 大情境 PNG、`sentinel_icon.png`、`animal-icons.svg`）複製至 Home Assistant：

```bash
# 在 Home Assistant 伺服器 (Synology NAS / Linux) 執行：
mkdir -p /config/www/ux-deck/
cp -r ./deploy/android-tv/www/* /config/www/ux-deck/
```

> 驗證確認：在瀏覽器造訪 `http://<YOUR_HA_IP>:8123/local/ux-deck/huds/doorbell.png`，確認能正常顯示透明圓角 HUD。

---

### 步驟 2：配置 Home Assistant `rest_command`

在 Home Assistant 的 `configuration.yaml` 中確認已配置兩台電視的 PiPup 端點：

```yaml
rest_command:
  pipup_notify_1f:
    url: "http://192.168.31.232:7979/notify"
    method: POST
    content_type: "application/json"
    payload: "{{ payload_json }}"

  pipup_notify_2f:
    url: "http://192.168.31.215:7979/notify"
    method: POST
    content_type: "application/json"
    payload: "{{ payload_json }}"
```

重載 Home Assistant 設定：**開發者工具** -> **YAML** -> **重新載入 REST 命令**。

---

### 步驟 3：部署 7 大生活情境自動化規則 (Automations)

將 [`deploy/android-tv/automations/tv_notifications.yaml`](./automations/tv_notifications.yaml) 內的自動化設定納入 `/config/automations.yaml`：

1. **玄關門鈴** (`binary_sensor.front_door_doorbell`) ➔ `doorbell.png` (15秒)
2. **洗衣完成** (`sensor.xi_yi_ji_status == 'complete'`) ➔ `washer_done.png` (25秒)
3. **洗衣進度** (`sensor.xi_yi_ji_status == 'running'`) ➔ `washer_running.png` (15秒)
4. **乾衣完成** (`sensor.gan_yi_ji_status == 'complete'`) ➔ `dryer_done.png` (25秒)
5. **日程提醒** (`calendar.timetree_schedule`) ➔ `calendar.png` (20秒)
6. **設備電量** (`sensor.nightlight_battery < 10`) ➔ `battery_low.png` (20秒)
7. **外送到達** (`sensor.foodpanda_order_status == 'arrived'`) ➔ `delivery.png` (30秒)

---

### 步驟 4：實體電視指令驗證 (Testing & Verification)

您可以在終端機透過 PowerShell 或 curl 直接推播測試 1F 客廳電視 (`192.168.31.232`)：

#### 測試 1：門鈴訪客情境 (Solution B 圓角毛玻璃)
```powershell
$body = @{
    duration = 15
    position = 0
    backgroundColor = "#00000000"
    title = ""
    message = ""
    media = @{
        image = @{
            uri = "http://192.168.31.101:8123/local/ux-deck/huds/doorbell.png"
            width = 480
        }
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://192.168.31.232:7979/notify" -Method Post -ContentType "application/json" -Body $body
```

#### 測試 2：洗衣完成情境
```powershell
$body = @{
    duration = 15
    position = 0
    backgroundColor = "#00000000"
    title = ""
    message = ""
    media = @{
        image = @{
            uri = "http://192.168.31.101:8123/local/ux-deck/huds/washer_done.png"
            width = 480
        }
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://192.168.31.232:7979/notify" -Method Post -ContentType "application/json" -Body $body
```

#### 測試 3：今日行事曆日程提醒 (Calendar Schedule HUD)
```powershell
$body = @{
    duration = 20
    position = 0
    backgroundColor = "#00000000"
    title = ""
    message = ""
    media = @{
        image = @{
            uri = "http://192.168.31.101:8123/local/ux-deck/huds/calendar.png"
            width = 480
        }
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://192.168.31.232:7979/notify" -Method Post -ContentType "application/json" -Body $body
```

---

## ❓ 為什麼 1F 客廳電視看不到行事曆日程？排查與修復手冊

若您在 1F Android TV 沒看到日程推播或看板，請依照以下三點檢查：

### 1. 觸發時機問題（已升級自動化）
- **原先問題**：舊版自動化規則僅設定 `at: "08:00:00"`（早上 8 點單次觸發）。若 08:00 時電視處於關機/待機狀態，或是您在 08:00 後才開啟電視，電視將不會收到任何日程。
- **最新解法**：已更新 [`tv_notifications.yaml`](./automations/tv_notifications.yaml)，加入三重智慧觸發：
  1. ⏰ **晨間固定 08:00 晨報**。
  2. 📺 **上午時段（07:00 ~ 12:00）電視開機時主動推播** (`media_player.android_tv_1f` 由 `off` 變 `on`)。
  3. 🔔 **日曆行程即將開始前 15 分鐘動態提醒** (`platform: calendar`, `event: start`, `offset: -00:15:00`)。

### 2. 實體電視與網路連線驗證
- **測試命令**：直接在電腦 PowerShell 執行上述【測試 3】，如果 1F 電視右上角立即彈出透明圓角日曆卡片，表示 PiPup 服務正常、HA 圖片路徑正確（`http://192.168.31.101:8123/local/ux-deck/huds/calendar.png`）。
- **PiPup 權限**：若電視沒反應，請確認 Android TV 上 PiPup App 已取得 **Display over other apps (顯示在其他應用程式上層)** 權限，且背景無被系統電池最佳化殺除。

### 3. 客廳大螢幕儀表板看板 (Lovelace View)
- 若您是在電視瀏覽器或 HA 看板中尋找日曆，請確認 [`dashboards/tv_dashboard.yaml`](./dashboards/tv_dashboard.yaml) 已載入最新的 10-foot 高對比家庭日程卡片模組。

---

## 📂 檔案目錄架構 (Directory Layout)

```
UX-Deck/deploy/android-tv/
├── DEPLOYMENT.md                  # 本部署手冊
├── simulator.html                 # 本地 D-pad 互動模擬器
├── automations/
│   └── tv_notifications.yaml     # 7 大生活情境自動化範本
├── dashboards/
│   └── tv_dashboard.yaml         # 客廳大螢幕 Lovelace 儀表板
├── themes/
│   └── tv_frosted_hud.yaml       # 客廳毛玻璃深色主題
└── www/                          # 部署至 HA /config/www/ux-deck/ 的靜態資產
    ├── sentinel_icon.png         # 客廳守護犬 🐕 高清圖示
    ├── animal-icons.svg          # 向量圖示庫
    ├── tv-popup.css              # 電視 Toast 樣式表
    └── huds/                     # 7 大情境透明圓角 PNG
        ├── doorbell.png          # 🔔 訪客叮咚
        ├── washer_done.png       # 🧺 洗衣完成
        ├── washer_running.png    # ⏱️ 洗衣運轉中
        ├── dryer_done.png        # 👕 乾衣完成
        ├── calendar.png          # 📅 今日行程
        ├── battery_low.png       # 🪫 設備電量警告
        └── delivery.png          # 🛵 外送到達
```
