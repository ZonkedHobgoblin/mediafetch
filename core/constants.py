import platform
from pathlib import Path

class Env:
    OS_NAME = platform.system()
    SCRIPT_PATH = Path(__file__).resolve().parent.parent
class AppMeta:
    MEDIAFETCH_VER = "v1.1.0"
    REPO_URL = "https://api.github.com/repos/ZonkedHobgoblin/mediafetch/releases/latest"

class MediaData:
    MMA_Q = ["128", "192", "256", "320"]
    OPUS_Q = ["96", "128", "160"]
    VORBIS_Q = ["128", "192"]
    NA_Q = ["0"]

    CODEC_TYPES = {
        "mp3": MMA_Q, "m4a": MMA_Q, "aac": MMA_Q, 
        "opus": OPUS_Q, "vorbis": VORBIS_Q, 
        "flac": NA_Q, "alac": NA_Q, "wav": NA_Q
    }

    VALID_CODECS = list(CODEC_TYPES.keys())
    VALID_QUALITIES = {item for sublist in CODEC_TYPES.values() for item in sublist}

class ErrorCodes:
    DOWNLOAD_ERROR = "DL-ER-001"
    DOWNLOAD_OTHER = "DL-ER-002"
    
    CONFIG_SAVE = "CMN-ER-000"
    CONFIG_CORRUPT = "CMN-ER-001"
    CONFIG_NOTFOUND = "CMN-ER-002"
    CONFIG_PARSE = "CMN-ER-003"
    CONFIG_UNKOWN = "CMN-ER-004"