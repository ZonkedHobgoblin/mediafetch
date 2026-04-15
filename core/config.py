import logging
import json
from core.constants import MediaData, Env, ErrorCodes

logger = logging.getLogger(__name__)
default_settings = {"codec": "mp3", "quality": "320", "folder": "downloads", "update": True}
class ConfigManager:
    
    
    def __init__(self):
        self.path = Env.SCRIPT_PATH / "config.json"
        self.settings = default_settings
        logger.info("ConfigManager initialized")


    def load(self):
        """Load our config and store it"""
        try:
            if not self.path.exists():
                logger.warning("No config file found! Writing default settings.")
                self.save()
                return "SUCCESS"
            else:
                logger.info("Loading config file")
                with open(self.path, 'r') as config_file:
                    loaded_file = json.load(config_file)
                
                codec = loaded_file.get("codec")
                quality = loaded_file.get("quality")
                
                if codec not in MediaData.VALID_CODECS or quality not in MediaData.VALID_QUALITIES:
                    raise ValueError(f"Invalid codec or quality: {codec}, {quality}")
                self.settings = loaded_file
                return "SUCCESS"
            
        except json.JSONDecodeError:
            logger.exception(ErrorCodes.CONFIG_CORRUPT)
            self.settings = default_settings
            self.save()
            return "ERR_CORRUPT"
            
        except FileNotFoundError:
            logger.exception(ErrorCodes.CONFIG_NOTFOUND)
            self.settings = default_settings
            self.save()
            return "ERR_NOTFOUND"
        
        except ValueError:
            logger.exception(ErrorCodes.CONFIG_PARSE)
            self.settings = default_settings
            self.save()
            return "ERR_PARSE"
        
        except Exception:
            logger.exception(ErrorCodes.CONFIG_UNKOWN)
            self.settings = default_settings
            self.save()
            return "ERR_UNKOWN"


    def save(self):
        """Save current self.settings to the file"""
        try:
            with open(self.path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return "SUCCESS"
        except Exception:
            logger.exception(ErrorCodes.CONFIG_SAVE)
            return "ERR_SAVE"
            
    def get(self, key):
        return self.settings.get(key)