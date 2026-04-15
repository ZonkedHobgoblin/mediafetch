import gettext
import locale
import logging
import core.constants as constants
from logging.handlers import RotatingFileHandler

locales_dir = constants.SCRIPT_PATH / "locales"

class LoggerSetup:
    @staticmethod
    def initialize():
        """
        Set up the logger for usage in logging over prints
        Logs to mediafetch.log in same dir as .py
        Is rotating (At 100kb size on new creation)
        """
        handler = RotatingFileHandler(
            "mediafetch.log", 
            maxBytes=10**5,
            backupCount=3
            )
        
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[handler]
        )
        logger = logging.getLogger(__name__)
        logger.info("Logger initialized")

class I18nSetup:
    @staticmethod
    def initialize() -> None:
        """Get the sys lang and load relevant locale file, otherwise default to English."""
        logger = logging.getLogger(__name__)
        try:
            sys_lang, _enc = locale.getlocale() 
            if sys_lang:
                user_lang = sys_lang.split('_')[0]
            logger.info(f"System language retrieved. Language: {user_lang}")
        except Exception:
            logger.warning("Unable to retrieve sys language, defaulting to English")
            pass

        try:
            lang = gettext.translation('mediafetch', localedir=locales_dir, languages=[user_lang, 'en'])
            lang.install()
            logger.info(".mo file found and loaded for current language.")
        except FileNotFoundError:
            logger.warning("Failed to find .mo file! Using default text.")