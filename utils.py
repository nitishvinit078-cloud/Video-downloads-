# utils.py
import os
import requests

def is_youtube_url(url: str) -> bool:
    if not url:
        return False
    u = url.lower()
    return "youtube.com" in u or "youtu.be" in u

def telegram_api_call(bot_token: str, method: str, params=None, files=None):
    """
    Simple wrapper for Telegram Bot API.
    method: e.g. 'sendMessage', 'setWebhook'
    params: dict for query/body
    files: dict for multipart file uploads
    """
    api = f"https://api.telegram.org/bot{bot_token}/{method}"
    try:
        if files:
            resp = requests.post(api, data=params or {}, files=files, timeout=300)
        else:
            resp = requests.post(api, data=params or {}, timeout=30)
        return resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def upload_file_to_telegram(bot_token: str, chat_id: int, file_path: str, caption: str = None):
    """
    Upload as document (generic) or video (if extension suggests).
    Returns response JSON.
    """
    filename = os.path.basename(file_path)
    ext = filename.lower()
    method = "sendDocument"
    field_name = "document"
    if ext.endswith(".mp4") or ext.endswith(".mkv") or ext.endswith(".webm"):
        method = "sendVideo"
        field_name = "video"

    api = f"https://api.telegram.org/bot{bot_token}/{method}"
    try:
        with open(file_path, "rb") as f:
            files = {field_name: (filename, f)}
            data = {"chat_id": str(chat_id)}
            if caption:
                data["caption"] = caption
            resp = requests.post(api, data=data, files=files, timeout=600)
            return resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
