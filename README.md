# 104 Job Scraper (Apify Actor)

## 專案介紹 (Project Introduction)
這是一個基於 Python 與 Playwright 開發的 Apify Actor（爬蟲程式），專門用來從 [104 人力銀行](https://www.104.com.tw) 抓取職缺資訊。本專案透過開啓自動化無頭瀏覽器，並執行 JavaScript 渲染與自動向下捲動來載入更多資料，最後利用 BeautifulSoup 解析 HTML 將整理好的職缺資料儲存回 Apify 的 Dataset 中。

## 環境設置 (Environment Setup)

在本地端運行或修改此專案前，需先準備好相關的開發環境套件。

### 1. 安裝 Apify CLI
此專案依賴 Apify CLI 工具來進行本地的開發與測試。請先確保電腦中已安裝 [Node.js](https://nodejs.org/)。
```bash
# 使用 npm 全域安裝 Apify CLI
npm install -g apify-cli
```

### 2. 安裝 Python 依賴套件
專案的爬蟲邏輯使用 Python 開發，請確定環境中為適用的 Python 版本，進入專案目錄後安裝 `requirements.txt` 指定的套件：
```bash
# 建議使用虛擬環境 (Virtual Environment)
pip install -r requirements.txt

# 安裝 Playwright 瀏覽器引擎核心 (必須執行)
playwright install chromium
```

## 使用方法 (Usage)

### 如何執行
在本地端測試時，可使用 Apify CLI 提供的命令來執行程式：
```bash
apify run
```

### 參數設定 (Input Configuration)
你可以透過修改專案的輸入參數來改變搜尋行為。若是透過 Apify 平台，可直接於介面上進行 Input 設定；在本地測試時，可建立或修改 `.actor\INPUT_SCHEMA.json`。若未設定，程式將會帶入預設值：

- `keyword` (字串, 預設為 `'UIUX'`):
  - 欲搜尋的職缺關鍵字，例如 `Python`、`軟體工程師`、`UIUX`。
- `area` (字串, 預設為 `'6001001000,6001002000'`):
  - 限定搜尋的工作地區代碼。預設代碼代表「台北市及新北市」。若有其他地區需求，可參考 104 網站上真實呈現於網址內的 `area` 參數進行修改；如不限制地區可傳入空字串。
- `max_jobs` (整數, 預設為 `30`):
  - 預定要抓取的最大職缺資料筆數。程式會持續向下捲動頁面以讀取更多清單內容，直到列表上顯示的職缺數量達到此條件為止。

## 輸出格式介紹 (Output Format)

爬蟲執行完畢後，抓取到的資料會被推送到 Apify 的 Dataset 中（本地端預設儲存於專案內 `storage/datasets/default/` 目錄下的 JSON 檔案）。每一筆職缺皆為一段 JSON 格式資料，包含以下欄位：

```json
{
  "職務名稱": "UI/UX Designer",
  "職務連結": "https://www.104.com.tw/job/xxxxxx",
  "公司名稱": "某某科技有限公司",
  "公司連結": "https://www.104.com.tw/company/xxxxxx",
  "產業類別": "軟體及網路相關業",
  "工作地點": "台北市信義區",
  "經歷要求": "2年以上",
  "學歷要求": "大學、碩士",
  "薪資待遇": "月薪 50,000~80,000元",
  "職務內容摘要": "負責公司核心產品的 UI/UX 設計與體驗優化...",
  "公司福利": [
    "年終獎金",
    "彈性上下班",
    "零食櫃"
  ],
  "應徵人數": "11~30人應徵"
}
```

- **職務名稱 / 職務連結**：該職位的名稱及 104 詳細頁面連結。
- **公司名稱 / 公司連結**：刊登職缺的企業名稱及其專頁連結。
- **產業類別**：該公司隸屬的產業類型（例如：網際網路相關業）。
- **工作地點 / 經歷要求 / 學歷要求 / 薪資待遇**：標籤區塊中呈現的各項基本條件資訊。
- **職務內容摘要**：職缺列表對應呈現的簡短職務描述。
- **公司福利**：該職缺特地標示的重點福利標籤清單（陣列格式）。
- **應徵人數**：目前該職缺呈現的統計應徵範圍（例如：0~5人應徵、11~30人應徵）。
