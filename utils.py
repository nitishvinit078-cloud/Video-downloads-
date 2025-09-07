import logging
import os
import re
from pytube import YouTube
import instaloader
import asyncio

logging.basicConfig(level=logging.INFO)

async def download_youtube_video(url, download_path):
    """Downloads a YouTube video and returns the file path."""
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        safe_title = re.sub(r'[^\w\s\.-]', '', yt.title)
        filename = f"{safe_title[:50]}.mp4"
        file_path = os.path.join(download_path, filename)
        
        logging.info(f"Downloading YouTube video: {yt.title}")
        
        await asyncio.to_thread(stream.download, output_path=download_path, filename=filename)
        
        return file_path
        
    except Exception as e:
        logging.error(f"Error downloading YouTube video: {e}")
        return None

async def download_instagram_post(url, download_path):
    """Downloads an Instagram video or image from a post URL."""
    try:
        L = instaloader.Instaloader(download_videos=True, download_pictures=True, save_metadata=False, post_metadata_txt_pattern='')
        
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        original_cwd = os.getcwd()
        os.chdir(download_path)

        match = re.search(r'(?:/p/|/reel|/tv)/([^/?&]+)', url)
        if not match:
            logging.error("Invalid Instagram URL.")
            os.chdir(original_cwd)
            return None

        post_shortcode = match.group(1)
        post = instaloader.Post.from_shortcode(L.context, post_shortcode)

        logging.info(f"Downloading Instagram post from: {url}")
        
        await asyncio.to_thread(L.download_post, post, '')
        
        filename = None
        if post.is_video:
            filename = f"{post.owner_username}_{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.mp4"
        else:
            filename = f"{post.owner_username}_{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.jpg"

        file_path = os.path.join(download_path, filename)
        os.chdir(original_cwd)
        
        return file_path

    except Exception as e:
        logging.error(f"Error downloading Instagram post: {e}")
        return None
