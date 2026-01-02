import os
import tempfile
from pathlib import Path
from .downloader import Downloader
import yt_dlp


class TikTokDownloader(Downloader):
    """Class for downloading a TikTok video from a given URL."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize TikTokDownloader.
        
        Args:
            output_dir: Directory to save downloaded videos. If None, uses temp directory.
        """
        if output_dir is None:
            self.output_dir = tempfile.gettempdir()
        else:
            self.output_dir = output_dir
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def download(self, url: str) -> str:
        """
        Download a TikTok video from a given URL.
        
        Args:
            url: TikTok video URL
            
        Returns:
            Path to the downloaded video file
            
        Raises:
            Exception: If download fails
        """
        ydl_opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4]/best',
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info to get the filename
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                
                # Download the video
                ydl.download([url])
                
                # Return the path to the downloaded file
                if os.path.exists(filename):
                    return filename
                else:
                    # Sometimes the extension might differ, try to find the file
                    base_name = os.path.splitext(filename)[0]
                    for ext in ['.mp4', '.webm', '.mkv']:
                        potential_file = base_name + ext
                        if os.path.exists(potential_file):
                            return potential_file
                    raise FileNotFoundError(f"Downloaded file not found: {filename}")
        except Exception as e:
            raise Exception(f"Failed to download TikTok video: {str(e)}")
