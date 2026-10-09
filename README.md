# 🤖 LINE AI 智慧對話小助理 (改善版)

一個整合 **FastAPI**、**line-bot-sdk v3** 與 **Google Gemini 3.8 Flash** 的智慧 LINE 官方帳號機器人。具備即時 AI 問答、輸入防呆檢驗、不支援訊息友善導引與內建指令系統。

---

## 📌 專題介紹
* **專題名稱**：LINE AI 智慧對話小助理 (改善版)
* **使用對象**：學生、自學者與一般 LINE 使用者。
* **想解決的問題**：
  * 使用者需要隨時隨地查閱資訊、撰寫範本、翻譯或解題，但切換外部 AI App 繁瑣。
  * 透過 LINE 這個人人日常都在使用的通訊軟體，直接獲得 Gemini 大語言模型的即時協助。
  * 解決傳統聊天機器人面對無效輸入或貼圖時「已讀不回」或報錯崩潰的痛點。

---

## ✨ 核心功能與改善版特色

### 1. 核心功能
* **AI 智慧問答**：串接 Google 最新 `gemini-3.8-flash` 模型，提供快速且準確的繁體中文問答。
* **簽名安全檢驗**：使用 LINE 官方 `WebhookParser` 進行 HMAC-SHA256 簽章比對，防止偽造 Webhook 請求。
* **雙模式自動備援**：若未填入 Gemini API Key，系統自動切換為 Echo（鸚鵡學舌）測試模式，不中斷服務。

### 2. 改善版新增功能 (v2.0 改進亮點)
* **💡 不支援輸入友善導引**：當使用者傳送貼圖、照片、語音或檔案時，不再靜默無聲，而是主動提示「目前僅支援文字對話」並導引提問方式。
* **⚠️ 空白與無效輸入檢核**：過濾使用者誤觸發送的純空格或無效空字元，提醒補充具體問題。
* **📖 內建指令系統**：支援 `/help`（功能與指令說明）與 `/about`（系統運行狀態）。

---

## 🧪 實際測試結果 (三種情境)

| 測試情境 | 使用者輸入內容 | 預期回覆結果 | 實際測試結果 |
| :--- | :--- | :--- | :--- |
| **情境 1：正常使用** | 「請用繁體中文解釋什麼是 API，並舉生活中的例子。」 | Gemini 3.8 Flash 產出結構清晰、繁體中文且生動的生活比喻（如餐廳服務生）。 | **通過** ✅：回覆流暢完整，約 1.5 秒內完成回覆。 |
| **情境 2：輸入不完整** | `   `（連打三個空白鍵發送） | 系統攔截空白，提示「輸入內容為空白」，引導使用者輸入具體問題與範例。 | **通過** ✅：成功攔截，回傳友善提示與引導範例。 |
| **情境 3：不支援的輸入** | 發送熊大貼圖或照片一張 | 系統捕捉到非文字型態事件，回傳提示「目前僅支援純文字對話」並提示 `/help`。 | **通過** ✅：成功識別非文字事件，回傳引導提示，不再已讀不回。 |

---

## ⚙️ 快速安裝與設定指南

### 1. 複製專案與安裝依賴
```bash
git clone https://github.com/haohsiangyang-0921/line-ai-bot.git
cd line-ai-bot
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### 2. 環境變數配置 (`.env`)
複製 `.env.example` 為 `.env`，並填入以下金鑰：
```env
# 請於 LINE Developers Console 取得
LINE_CHANNEL_SECRET=your_line_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here

# 請於 Google AI Studio (https://aistudio.google.com/) 免費取得
GEMINI_API_KEY=your_gemini_api_key_here
```
> ⚠️ **安全性提醒**：`.env` 已列入 `.gitignore`，切勿將真實金鑰推播至公開儲存庫。

### 3. 本機啟動
* 伺服器啟動：雙擊執行 `run_server.bat`（或執行 `uvicorn main:app --port 8000 --reload`）
* 穿透工具：雙擊執行 `run_ngrok.bat`
* 背景無窗執行：雙擊執行 `一鍵隱藏啟動.vbs`

---

## 🚧 已知限制與未來展望
1. **多輪對話記憶**：目前為單次問答無狀態（Stateless）模式，下一階段預計導入 SQLite / Redis 快取最近 5 輪上下文。
2. **多模態影像識別**：預計整合 Gemini Vision API，使機器人具備解讀使用者上傳照片與圖表的能力。
