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
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from services.ai_service import generate_reply, init_ai

app = FastAPI(title="LINE AI Bot", description="LINE Bot powered by FastAPI and Google Gemini")

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
        "service": "LINE AI Bot",
        "line_credentials_configured": is_line_ready,
        "gemini_api_configured": is_gemini_ready,
        "mode": "Gemini AI" if is_gemini_ready else "Echo Test Mode"
    }

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    """接收 LINE Webhook 請求的核心路由"""
    # 重新讀取（方便使用者更新 .env 後不必重啟）
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
        # 只處理使用者發送的純文字訊息
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            user_text = event.message.text
            logger.info(f"收到來自使用者訊息: {user_text}")

            # 呼叫 AI 服務取得回答
            reply_text = await generate_reply(user_text)

            # 回覆訊息給 LINE 使用者
            try:
                with ApiClient(local_config) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=reply_text)]
                        )
                    )
                logger.info(f"成功回覆訊息: {reply_text[:30]}...")
            except Exception as e:
                logger.error(f"LINE 訊息回覆失敗: {e}")

    return JSONResponse(content={"status": "OK"})
