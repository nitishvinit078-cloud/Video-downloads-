import yt_dlp
import os

def download_youtube_video(url: str, output_dir="downloads"):
    """Download YouTube video"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        "format": "best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        return file_path


def download_instagram_post(url: str, output_dir="downloads"):
    """Download Instagram post"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        "format": "best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        return file_path
