import logging
from utils.core_utils import LoggerSetup, I18nSetup
from ui.cli import CLIInterface
from core.config import ConfigManager
from core.downloader import MediaDownloader
from core.updater import Updater, DependencyManager

class MediaFetchApp:
    
    
    def __init__(self):
        LoggerSetup.initialize()
        I18nSetup.initialize()
        self.logger = logging.getLogger(__name__)
        self.logger.info("MediaFetch App Started")
        
        config_manager = ConfigManager()
        media_downloader = MediaDownloader()
        updater = Updater()
        dependency_manager = DependencyManager()
        
        self.ui = CLIInterface(config_manager, dependency_manager, media_downloader, updater)
    
    
    def start(self):
        self.ui.run()


if __name__ == "__main__":
    app = MediaFetchApp()
    app.start()