import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse

# 載入 .env 環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from services.ai_service import generate_reply, init_ai

app = FastAPI(title="LINE AI Bot", description="LINE Bot powered by FastAPI and Google Gemini (Improved Edition)")

# 讀取金鑰配置
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "").strip()
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()

parser = None
if CHANNEL_SECRET and CHANNEL_SECRET != "請貼上你的_Channel_Secret":
    parser = WebhookParser(CHANNEL_SECRET)

configuration = None
if CHANNEL_ACCESS_TOKEN and CHANNEL_ACCESS_TOKEN != "請貼上你的_Channel_Access_Token":
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

@app.on_event("startup")
async def startup_event():
    init_ai()
    if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
        logger.warning("⚠️ 請注意：尚未在 .env 設定 LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN！")
    else:
        logger.info("✅ LINE Bot 金鑰設定已就緒。")

@app.get("/")
async def root():
    """健康檢查端點"""
    is_line_ready = bool(CHANNEL_SECRET and CHANNEL_ACCESS_TOKEN)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    is_gemini_ready = bool(gemini_key and gemini_key != "請貼上你的_Gemini_API_Key")
    
    return {
        "status": "online",
        "service": "LINE AI Bot 改善版",
        "version": "2.0.0",
        "line_credentials_configured": is_line_ready,
        "gemini_api_configured": is_gemini_ready,
        "mode": "Gemini AI" if is_gemini_ready else "Echo Test Mode"
    }

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    """接收 LINE Webhook 請求的核心路由（改善版：支援多媒體提示、空白過濾與 /help 指令）"""
    current_secret = os.getenv("LINE_CHANNEL_SECRET", "").strip()
    current_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()

    if not current_secret or not current_token:
        logger.error("缺少 LINE 金鑰，請檢查 .env 檔案設定。")
        raise HTTPException(status_code=500, detail="LINE credentials not configured on server.")

    local_parser = WebhookParser(current_secret)
    local_config = Configuration(access_token=current_token)

    if not x_line_signature:
        logger.warning("收到沒有 X-Line-Signature 的請求。")
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header")

    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        events = local_parser.parse(body_str, x_line_signature)
    except InvalidSignatureError:
        logger.error("簽名驗證失敗 (Invalid Signature)！請確認 Channel Secret 是否正確。")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"解析 Webhook 事件錯誤: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    for event in events:
        if not isinstance(event, MessageEvent):
            continue

        reply_text = ""

        # 情境 A：使用者發送純文字訊息
        if isinstance(event.message, TextMessageContent):
            raw_text = event.message.text
            user_text = raw_text.strip()
            logger.info(f"收到文字訊息: '{raw_text}'")

            # 改善點 1：情境【輸入不完整或純空白】防護檢核
            if not user_text:
                reply_text = (
                    "⚠️ 【輸入提示】您輸入的內容似乎是空的或只有空白字元！\n\n"
                    "請輸入具體的問題或任務，例如：\n"
                    "• 「請幫我寫一封英文請假信」\n"
                    "• 「什麼是機器學習？」\n"
                    "• 輸入「/help」查看更多使用指引。"
                )
            # 改善點 2：內建指令支援 /help 與 /about
            elif user_text.lower() in ["/help", "help", "說明", "幫助"]:
                reply_text = (
                    "🤖 【AI 智慧小助理 - 使用指南】\n\n"
                    "📌 核心功能：\n"
                    "• 自然語言智能對話（由 Google Gemini 驅動）\n"
                    "• 文本翻譯、程式撰寫、概念解說\n\n"
                    "💡 快速指令：\n"
                    "• 輸入「/help」：查看操作說明\n"
                    "• 輸入「/about」：查看系統版本狀態\n"
                    "• 直接輸入任意文字：立即開始與 AI 對話！\n\n"
                    "⚠️ 提醒：目前僅支援文字對話，不支援貼圖、語音與圖片分析。"
                )
            elif user_text.lower() in ["/about", "about", "關於"]:
                reply_text = (
                    "ℹ️ 【LINE AI Bot 系統資訊】\n\n"
                    "• 專案版本：v2.0 課後改善版\n"
                    "• 後端技術：Python FastAPI + line-bot-sdk v3\n"
                    "• AI 模型：Google Gemini 3.8 Flash\n"
                    "• 服務狀態：24小時運行在線"
                )
            # 改善點 3：情境【正常使用】呼叫 AI
            else:
                reply_text = await generate_reply(user_text)

        # 改善點 4：情境【不支援的輸入】（貼圖、照片、語音、影片等）
        else:
            msg_type = type(event.message).__name__
            logger.info(f"收到非文字訊息 (型態: {msg_type})")
            reply_text = (
                "💡 【不支援的訊息格式】\n\n"
                "抱歉！目前小助理只支援「純文字」對話喔！\n"
                "暫時無法解析貼圖、照片、語音訊息或檔案。\n\n"
                "👉 請直接輸入文字提出您的問題，或輸入「/help」查看使用指南。"
            )

        # 統一回覆訊息給使用者
        try:
            with ApiClient(local_config) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )
            logger.info(f"成功回覆訊息 (前30字): {reply_text[:30]}...")
        except Exception as e:
            logger.error(f"LINE 訊息回覆失敗: {e}")

    return JSONResponse(content={"status": "OK"})
