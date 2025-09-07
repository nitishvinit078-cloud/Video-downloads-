import logging
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from utils import download_youtube_video, download_instagram_post

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def start_command(update: Update, context) -> None:
    """Sends a welcome message."""
    await update.message.reply_text("Hello! 👋 Send me a YouTube or Instagram video link, and I will download it for you.")

async def handle_message(update: Update, context) -> None:
    """Handles incoming messages and routes them."""
    user_message = update.message.text
    
    if "youtube.com" in user_message or "youtu.be" in user_message:
        await update.message.reply_text("I've detected a YouTube link. Downloading...")
        file_path = await download_youtube_video(user_message, "downloads/")
        
        if file_path and os.path.exists(file_path):
            await update.message.reply_video(video=open(file_path, 'rb'), caption="YouTube Video Downloaded ✅")
            os.remove(file_path)
        else:
            await update.message.reply_text("Sorry, I could not download that YouTube video. It might be a private video or an issue with the link.")
            
    elif "instagram.com" in user_message:
        await update.message.reply_text("I've detected an Instagram link. Processing...")
        file_path = await download_instagram_post(user_message, "downloads/")
        
        if file_path and os.path.exists(file_path):
            if file_path.endswith('.mp4'):
                await update.message.reply_video(video=open(file_path, 'rb'), caption="Instagram Video Downloaded ✅")
            elif file_path.endswith('.jpg'):
                await update.message.reply_photo(photo=open(file_path, 'rb'), caption="Instagram Image Downloaded ✅")
            os.remove(file_path)
        else:
            await update.message.reply_text("Sorry, I could not download that Instagram post. It might be a private account or an unsupported post.")
    
    else:
        await update.message.reply_text("I only support YouTube and Instagram links. Please send a valid link.")

def main() -> None:
    """Starts the bot."""
    PORT = int(os.environ.get('PORT', 8443))
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url="https://telegram-video-downloader-bot.onrender.com/" + TELEGRAM_BOT_TOKEN
    )

if __name__ == "__main__":
    main()
