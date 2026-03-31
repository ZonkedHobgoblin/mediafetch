import logging
from pathlib import Path


logger = logging.getLogger(__name__)
class MediaDownloader:
    
    
    def __init__(self):
        logger.info("MediaDownloader initialized")
        pass
    
    
    def progress_hook(self, d: dict) -> None:
        """Called by yt_dlp during the download process."""
        if d['status'] == 'finished':
            file_name = d.get('filename')
            logger.info("Successfully finished downloading: %s", file_name)
        
        elif d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            s = d.get('_speed_str', 'N/A')
            logger.debug("Downloading %s at %s", p, s)

        elif d['status'] == 'error':
            logger.error("Error occurred while downloading: %s", d.get('filename'))
    
    
    def download_audio(self, url: str, codec: str, quality: str, folder: str) -> None:
        """
        Downloads audio from a YouTube URL using yt_dlp.

        Args:
            url (str): The YouTube video or playlist link.
            codec (str): The target audio format (e.g., 'mp3', 'flac').
            quality (str): The target bitrate (e.g., '256', '320').
            folder (str): The relative or absolute path to save the file.
        """
        import yt_dlp
        ydl_opts = {
            # Audio Settings
            'format': 'bestaudio/best',
            'progress_hooks': [self.progress_hook],
            'outtmpl': f'{folder}/%(title)s.%(ext)s', # Save in the configed downloads folder
            'postprocessors': [{
                'key': "FFmpegExtractAudio",
                'preferredcodec': codec,
                'preferredquality': quality,
            }],
            
            # Pretending to be the Android App (Instead of a web browser) stops
            # "Signature solving" and "n challenges" issues when downloading
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                }
            },

            'quiet': False,
            'no_warnings': True,
        }

        logger.info("Attempting to download media")
        try:
            # Create the downloads folder if it doesn't exist in the current dir
            Path(folder).mkdir(parents=True, exist_ok=True)
            logger.info(f"Downloads folder created: {folder}")
            
            logger.debug(f"Downloading URL: {url}")
            print(_("Downloading: {url}").format(url=url))
            
            # Pass the ydl_opts dict to the downloader
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
                
            print(_("Downloading finished! \n"))
            logger.info("Download finished")
            
        except yt_dlp.utils.DownloadError as error:
            logger.exception("Download error occured")
            return "DL-ER-001"
            print(_("yt_dlp encountered a download error! Error: {error}\n").format(error=error))
            
        except Exception as error:
            logger.exception("Unexpected error occured")
            return "DL-ER-002"
            print(_("Failed to download. Error: {error}\n").format(error=error))