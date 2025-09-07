# downloader.py
import os
import tempfile
import subprocess
import shutil
from utils import upload_file_to_telegram, is_youtube_url

def download_and_send(bot_token: str, chat_id: int, link: str):
    """
    Download video/audio using yt-dlp and upload to Telegram.
    Runs in background thread from app.py.
    """
    try:
        if not is_youtube_url(link):
            # send a message back (use requests inside util)
            from utils import telegram_api_call
            telegram_api_call(bot_token, "sendMessage", params={
                "chat_id": chat_id,
                "text": "Only YouTube links are supported."
            })
            return

        tmpdir = tempfile.mkdtemp(prefix="ytdl_")
        out_template = "%(title).200s.%(ext)s"
        # we'll default to best (merged mp4 if possible)
        cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "-o", out_template,
            link
        ]
        # run yt-dlp
        proc = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=900)
        if proc.returncode != 0:
            from utils import telegram_api_call
            telegram_api_call(bot_token, "sendMessage", params={
                "chat_id": chat_id,
                "text": f"Download failed: yt-dlp error.\n{proc.stderr[:1000]}"
            })
            return

        # find downloaded file
        files = [f for f in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, f))]
        if not files:
            from utils import telegram_api_call
            telegram_api_call(bot_token, "sendMessage", params={
                "chat_id": chat_id,
                "text": "Download completed but no file found."
            })
            return

        filepath = os.path.join(tmpdir, files[0])
        filesize = os.path.getsize(filepath)

        # Telegram max file size (as of now) is 2GB for cloud upload.
        MAX_BYTES = 2 * 1024**3
        if filesize > MAX_BYTES:
            # try to send audio instead
            subprocess.run([
                "yt-dlp", "-x", "--audio-format", "mp3", "-o", "%(title).200s.%(ext)s", link
            ], cwd=tmpdir)
            # find mp3
            audio_files = [f for f in os.listdir(tmpdir) if f.lower().endswith(".mp3")]
            if audio_files:
                audio_path = os.path.join(tmpdir, audio_files[0])
                upload_file_to_telegram(bot_token, chat_id, audio_path, caption="File was too large; sent audio instead.")
            else:
                from utils import telegram_api_call
                telegram_api_call(bot_token, "sendMessage", params={
                    "chat_id": chat_id,
                    "text": "File too large (>2GB) and audio fallback failed."
                })
            shutil.rmtree(tmpdir, ignore_errors=True)
            return

        # upload file
        upload_resp = upload_file_to_telegram(bot_token, chat_id, filepath, caption="Here is your video (downloaded).")
        # optionally check upload_resp and notify user on failure
        if not upload_resp.get("ok"):
            from utils import telegram_api_call
            telegram_api_call(bot_token, "sendMessage", params={
                "chat_id": chat_id,
                "text": f"Upload failed: {upload_resp.get('error')}"
            })
    except Exception as e:
        from utils import telegram_api_call
        telegram_api_call(bot_token, "sendMessage", params={
            "chat_id": chat_id,
            "text": f"Server error: {e}"
        })
    finally:
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except:
            pass
