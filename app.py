# app.py
import os
import threading
import tempfile
import shutil
from flask import Flask, request, jsonify
from downloader import download_and_send
from utils import telegram_api_call

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Please set TELEGRAM_BOT_TOKEN environment variable")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # optional, e.g. https://your-service.onrender.com/webhook

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "YT Telegram Downloader - alive"

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """
    Call this once to set Telegram webhook to your Render URL (if WEBHOOK_URL provided).
    Or call manually:
    https://api.telegram.org/bot<token>/setWebhook?url=https://your-service/webhook
    """
    url = WEBHOOK_URL
    if not url:
        return jsonify({"ok": False, "error": "WEBHOOK_URL not set in env"}), 400

    resp = telegram_api_call(BOT_TOKEN, "setWebhook", params={"url": url})
    return jsonify(resp)

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Telegram will POST updates here.
    We quickly acknowledge then process download in background thread.
    """
    update = request.get_json(force=True)
    # minimal safety checks
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat", {})
    text = message.get("text", "") or ""

    chat_id = chat.get("id")
    if not chat_id:
        return jsonify({"ok": False, "error": "no chat id"}), 200

    # handle commands
    if text.startswith("/start"):
        telegram_api_call(BOT_TOKEN, "sendMessage", params={
            "chat_id": chat_id,
            "text": "Hi! Send a YouTube link and I'll download and send the file back (use responsibly)."
        })
        return jsonify({"ok": True}), 200

    if not text.startswith("http"):
        telegram_api_call(BOT_TOKEN, "sendMessage", params={
            "chat_id": chat_id,
            "text": "Please send a valid YouTube link (starts with http...)."
        })
        return jsonify({"ok": True}), 200

    # Acknowledge and start background download
    telegram_api_call(BOT_TOKEN, "sendMessage", params={
        "chat_id": chat_id,
        "text": "Request received — starting download. You will get the file when ready."
    })

    # background thread
    t = threading.Thread(target=download_and_send, args=(BOT_TOKEN, chat_id, text))
    t.daemon = True
    t.start()

    return jsonify({"ok": True}), 200

# Health endpoint for Render
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

if __name__ == "__main__":
    # optional: auto-set webhook on start if WEBHOOK_URL provided
    if WEBHOOK_URL:
        try:
            telegram_api_call(BOT_TOKEN, "setWebhook", params={"url": WEBHOOK_URL})
            print("Webhook set to", WEBHOOK_URL)
        except Exception as e:
            print("Failed to set webhook:", e)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
