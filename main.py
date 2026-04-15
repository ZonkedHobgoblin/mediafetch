import logging
import sys
import traceback
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
        self.logger.info("Starting MediaFetch")
        
        config_manager = ConfigManager()
        dependency_manager = DependencyManager()
        updater = Updater()
        media_downloader = MediaDownloader()
        
        self.ui = CLIInterface(config_manager, dependency_manager, media_downloader, updater)
        self.logger.info("MediaFetch initialized")
    
    
    def start(self):
        self.ui.run()
        self.logger.info("MediaFetch stopped")


if __name__ == "__main__":
    try:
        app = MediaFetchApp()
        app.start()
        
    except KeyboardInterrupt:
        print("\nExiting MediaFetch...")
        sys.exit(0)
        
    except Exception as e:
        # if launch fails, we can fallback to traceback if logger wasnt setup
        error_details = traceback.format_exc()
        
        logger = logging.getLogger(__name__)
        
        if logging.getLogger().hasHandlers():
            logger.critical("A fatal unhandled exception occurred!", exc_info=True)
            print("\nAn unexpected error occurred. Please check mediafetch.log for details.")
            
        else:
            fallback_file = "mediafetch_crash.log"
            try:
                with open(fallback_file, "a", encoding="utf-8") as f:
                    f.write(f"FATAL CRASH PRE-INIT:\n{error_details}\n")
                print(f"\nCritical failure before initialization. Check {fallback_file} for details.")
            except Exception:
                print("\nCritical failure and cannot write to disk. Error details:")
                print(error_details, file=sys.stderr)
                
        sys.exit(1)