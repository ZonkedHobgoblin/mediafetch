import logging
from utils.core_utils import LoggerSetup, I18nSetup
from ui.cli import CLIInterface, CLIUtils


# 1. Call the initialize methods using parentheses!
LoggerSetup.initialize()
I18nSetup.initialize()

class MediaFetchApp:
    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.info("MediaFetchApp initialized!")
        CLIInterface.about()
        CLIUtils.pause()
        pass

# 3. Standard Python entry point check
if __name__ == "__main__":
    app = MediaFetchApp()