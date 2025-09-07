# utils.py
import logging
import os
import re
from pytube import YouTube
import instaloader

logging.basicConfig(level=logging.INFO)

async def download_youtube_video(url, download_path):
    """Downloads a YouTube video and returns the file path."""
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        
        # Ensure download directory exists
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Sanitize filename
        safe_title = re.sub(r'[^\w\s\.-]', '', yt.title)
        filename = f"{safe_title[:50]}.mp4"
        file_path = os.path.join(download_path, filename)
        
        logging.info(f"Downloading YouTube video: {yt.title}")
        stream.download(output_path=download_path, filename=filename)
        return file_path
        
    except Exception as e:
        logging.error(f"Error downloading YouTube video: {e}")
        return None

async def download_instagram_post(url, download_path):
    """Downloads an Instagram video or image from a post URL."""
    try:
        L = instaloader.Instaloader()
        
        # Ensure download directory exists
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Change current working directory temporarily to control download location
        original_cwd = os.getcwd()
        os.chdir(download_path)

        # Get post shortcode from URL
        match = re.search(r'(?:/p/|/reel/|/tv/)([^/?&]+)', url)
        if not match:
            logging.error("Invalid Instagram URL.")
            os.chdir(original_cwd)
            return None

        post = instaloader.Post.from_shortcode(L.context, match.group(1))

        logging.info(f"Downloading Instagram post from: {url}")
        L.download_post(post, '')
        
        # Get the downloaded file path
        if post.is_video:
            filename = f"{post.owner_username}_{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.mp4"
            file_path = os.path.join(download_path, filename)
        else:
            filename = f"{post.owner_username}_{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.jpg"
            file_path = os.path.join(download_path, filename)
        
        # Cleanup
        os.chdir(original_cwd)
        
        return file_path

    except Exception as e:
        logging.error(f"Error downloading Instagram post: {e}")
        os.chdir(original_cwd)
        return None

