# wenchiehlee.quickconnect.to 部署指南 (Synology NAS & Private Cloud DevOps)

## 吉祥物意象
- **吉祥物**：裝甲穿山甲 🛡️ (Armored Pangolin Shield)
- **Symbol ID**：`#icon-pangolin-shield`
- **定位**：私人雲端堡壘、硬體級安全守護、防護屏障與極致穩健的 24/7 DevOps 服務。

## 部署內容
1. **主題樣式檔**：`docs/stylesheets/nas-theme.css`（原生導航磨砂藥丸按鈕、穿山甲徽章微光、Cyber Slate & Synology Blue 調性）
2. **範本覆寫**：
   - `docs/overrides/partials/logo.html`（以向量 SVG `<use href="#icon-pangolin-shield"/>` 取代傳統 `w-red.png`，桌面與行動端皆支援）
   - `docs/overrides/partials/header.html`（無縫整合進 Material for MkDocs 原生導航列的 `🏠 主題首頁` 跨端點導航膠囊）
   - `docs/overrides/main.html`（全域注入 `#icon-pangolin-shield` SVG 定義與 `nas-theme.css` 連結）
3. **Favicon 向量圖標**：`docs/assets/images/pangolin-favicon.svg` 與高解析 `docs/assets/images/pangolin-favicon.png`
4. **配置文件**：`mkdocs.yml`（啟用 `favicon: assets/images/pangolin-favicon.png`，更新 palette 為 light-blue/cyan，並在 `extra_css:` 中加入 `stylesheets/nas-theme.css`）

## 驗證方式
- 本地驗證：已通過 `mkdocs build --clean` 構建成功（30 秒內全站靜態頁產出完成）。
- 遠端部署：推送至 `main` 分支後透過 `.github/workflows/mkdocs-deploy-synology.yml` 自動將產出物同步發布至 Synology Web Station。
