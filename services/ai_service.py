import os
import logging

logger = logging.getLogger(__name__)

_client = None

def init_ai():
    global _client
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "請貼上你的_Gemini_API_Key":
        logger.warning("未偵測到 GEMINI_API_KEY，將以 Echo（鸚鵡學舌）模式運作。")
        return None

    # 優先使用官方最新 google.genai SDK
    try:
        from google import genai
        _client = genai.Client(api_key=api_key)
        logger.info("Google GenAI Client 初始化成功！")
        return _client
    except Exception as e:
        logger.warning(f"google.genai 初始化失敗，嘗試相容模組: {e}")

    # 次選舊版相容 google.generativeai
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        _client = legacy_genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Google GenerativeAI Legacy 初始化成功！")
        return _client
    except Exception as e:
        logger.error(f"Gemini 初始化失敗: {e}")
        return None

async def generate_reply(user_message: str) -> str:
    """接收使用者文字訊息，呼叫 Gemini 生成回應；若未設定金鑰則回傳 Echo 訊息"""
    global _client
    if _client is None:
        _client = init_ai()

    # 若無設定 Gemini API Key，預設為 Echo 測試模式
    if _client is None:
        return (
            f"【機器人回應】\n"
            f"收到您的訊息：{user_message}\n\n"
            f"💡 提示：若要啟用 AI 智慧問答，請在專案的 .env 檔案中填入 GEMINI_API_KEY！"
        )

    try:
        # 判斷是最新 google.genai 還是 legacy
        if hasattr(_client, "models"):
            response = _client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_message
            )
            reply_text = response.text.strip()
        else:
            response = _client.generate_content(
                contents=user_message,
                generation_config={"max_output_tokens": 1500}
            )
            reply_text = response.text.strip()

        # LINE 單則訊息文字上限為 5000 字元，超過做適當截斷
        if len(reply_text) > 4900:
            reply_text = reply_text[:4900] + "\n...(回答過長已截斷)"
        return reply_text
    except Exception as e:
        logger.error(f"Gemini API 調用錯誤: {e}")
        return f"抱歉，AI 暫時無法處理您的請求（錯誤原因：{str(e)}）"
