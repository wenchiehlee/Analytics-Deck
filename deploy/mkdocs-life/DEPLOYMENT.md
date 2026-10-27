# mkdocs-life 部署指南 (Warm Editorial & Mindful Journal)

## 吉祥物意象
- **吉祥物**：林鹿寧靜冥想 (Scandinavian Forest Deer 🦌)
- **Symbol ID**：`#icon-deer-life`
- **定位**：優雅從容、沉思反饋、暖白紙感 editorial 閱讀美學

## 部署內容
1. **主題樣式檔**：`docs/stylesheets/life-theme.css`（原生導航磨砂藥丸按鈕、靈鹿徽章微光、暖白紙感排版）
2. **範本覆寫**：`docs/overrides/partials/header.html`（無縫整合進 Material for MkDocs 原生導航列，避免外掛 Banner 干擾）與 `docs/overrides/main.html`
3. **配置文件**：`mkdocs.yml`（在 `extra_css:` 中啟用 `stylesheets/life-theme.css`）

## 驗證方式
- 本地驗證：已通過 `mkdocs build` 與 Playwright 桌面/行動版雙重視覺驗證。
- 遠端部署：推送至 `main` 分支後透過 GitHub Actions 自動發布至 GitHub Pages。
