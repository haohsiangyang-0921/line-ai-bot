# LINE AI Bot (FastAPI + Google Gemini)

這是一個基於 **FastAPI** 與 **Google Gemini AI**（亦支援 Echo 測試模式）的 LINE 智慧聊天機器人專案。

---

## 專案目錄結構

```
line-ai-bot/
├── .env                  # 請在此填入您的 LINE 與 Gemini 金鑰
├── .env.example          # 金鑰範本
├── main.py               # FastAPI 主應用與 Webhook 路由 (/callback)
├── requirements.txt      # 專案相依套件
├── run_server.bat        # 點擊啟動 FastAPI 伺服器 (Port 8000)
├── run_ngrok.bat         # 點擊啟動 ngrok 公開穿透 (產生 Webhook 網址)
└── services/
    ├── ai_service.py     # 處理 Google Gemini 對話生成
    └── line_service.py   # LINE 訊息互動邏輯
```

---

## 使用步驟

### 步驟 1：填寫金鑰 (`.env`)

開啟 [`.env`](file:///c:/Users/yangh/OneDrive/Desktop/line-ai-bot/.env)，填入取得的金鑰：

```env
LINE_CHANNEL_SECRET=你的Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的Channel_Access_Token
GEMINI_API_KEY=你的Gemini_API_Key
```

> 💡 **提示**：若暫時還沒申請 `GEMINI_API_KEY`，可先留空，機器人會自動以 **Echo 鸚鵡學舌模式** 運作（回傳你剛說的話）。

---

### 步驟 2：啟動伺服器

雙擊執行 [`run_server.bat`](file:///c:/Users/yangh/OneDrive/Desktop/line-ai-bot/run_server.bat)，或在終端機輸入：

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload
```

---

### 步驟 3：啟動 ngrok 並複製 Webhook 網址

雙擊執行 [`run_ngrok.bat`](file:///c:/Users/yangh/OneDrive/Desktop/line-ai-bot/run_ngrok.bat)。
畫面中會出現一串以 `https://` 開頭的轉發網址，例如：
`https://a1b2-c3d4.ngrok-free.app`

加上 `/callback` 即為您的 Webhook URL：
👉 **`https://a1b2-c3d4.ngrok-free.app/callback`**

---

### 步驟 4：設定 LINE Developers

1. 登入 [LINE Developers Console](https://developers.line.biz/)。
2. 進入您的頻道 -> **Messaging API** 分頁。
3. 找到 **Webhook URL**，點擊 **Edit** 填入步驟 3 的網址並按 **Update**。
4. 將 **Use webhook** 開關**開啟**。
5. 點擊 **Verify**，顯示 Success 即可！
6. 用手機 LINE 掃描該頁面的 QR Code 加入機器人好友，傳送訊息進行實測！
