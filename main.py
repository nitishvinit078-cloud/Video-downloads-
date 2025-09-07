# main.py
import logging
import os
import re
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, DOWNLOAD_DIRECTORY
from utils import download_youtube_video, download_instagram_post

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def start_command(update: Update, context) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hello! 👋 Send me a YouTube or Instagram video link, and I will download it for you.")

async def help_command(update: Update, context) -> None:
    """Sends a help message."""
    await update.message.reply_text(
        "Simply send a YouTube or Instagram link. I'll automatically detect the link and download the video for you. "
        "I support the highest resolution for YouTube videos and video/image posts for Instagram."
    )

async def handle_message(update: Update, context) -> None:
    """Handles incoming messages and routes them based on the content."""
    user_message = update.message.text
    
    # Check for YouTube link
    if "youtube.com" in user_message or "youtu.be" in user_message:
        await update.message.reply_text("I've detected a YouTube link. Downloading the video...")
        file_path = await download_youtube_video(user_message, DOWNLOAD_DIRECTORY)
        if file_path and os.path.exists(file_path):
            await update.message.reply_video(video=open(file_path, 'rb'), caption="YouTube Video Downloaded ✅")
            os.remove(file_path) # Clean up
        else:
            await update.message.reply_text("Sorry, I could not download that YouTube video. Please try again or with another link.")
            
    # Check for Instagram link
    elif "instagram.com" in user_message:
        await update.message.reply_text("I've detected an Instagram link. Processing your request...")
        file_path = await download_instagram_post(user_message, DOWNLOAD_DIRECTORY)
        if file_path and os.path.exists(file_path):
            if file_path.endswith('.mp4'):
                await update.message.reply_video(video=open(file_path, 'rb'), caption="Instagram Video Downloaded ✅")
            elif file_path.endswith('.jpg'):
                await update.message.reply_photo(photo=open(file_path, 'rb'), caption="Instagram Image Downloaded ✅")
            os.remove(file_path) # Clean up
            
            # Remove any associated files created by Instaloader
            for filename in os.listdir(DOWNLOAD_DIRECTORY):
                if filename.startswith(os.path.basename(file_path).split('.')[0]):
                    os.remove(os.path.join(DOWNLOAD_DIRECTORY, filename))
        else:
            await update.message.reply_text("Sorry, I could not download that Instagram post. It might be a private profile or an unsupported post type.")
            
    # If the message is not a known command or link
    else:
        await update.message.reply_text("I only support YouTube and Instagram links. Please send a valid link.")

def main() -> None:
    """Starts the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    logging.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()

