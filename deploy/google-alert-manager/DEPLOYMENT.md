# GoogleAlertManager 部署指南 (SaaS Signal Intelligence)

## 吉祥物意象
- **吉祥物**：銳眼遊隼雷達 (Peregrine Radar Falcon 🦅)
- **Symbol ID**：`#icon-falcon-radar`
- **定位**：高空雷達偵察、關鍵信號鎖定、剔除資訊雜訊

## 部署內容
1. **主題樣式檔**：`gam-theme.css`
2. **入口檔案更新**：`index.html`（注入頂部常駐 Header、吉祥物徽章、跨專案導航按鈕、利多/利空分析結論 Callout 容器）

## 驗證方式
- 本地預覽：`python -m http.server 8767`
- 遠端 GitHub Pages 自動構建發布：推送至 `main` 分支後自動發布。
