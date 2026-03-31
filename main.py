import logging
import core.constants as constants
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


        pass

if __name__ == "__main__":
    app = MediaFetchApp()