"""
Example usage of TikTokDownloader class.
"""
from downloaders.tiktok_downloader import TikTokDownloader


def main():
    # Initialize the downloader
    downloader = TikTokDownloader()
    
    # Example TikTok URL (replace with a real URL)
    url = input("Enter TikTok URL: ").strip()
    
    if not url:
        print("No URL provided!")
        return
    
    try:
        print(f"Downloading video from: {url}")
        file_path = downloader.download(url)
        print(f"✓ Video downloaded successfully!")
        print(f"  Location: {file_path}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()

