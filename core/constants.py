# core/constants.py
import platform
from pathlib import Path

MEDIAFETCH_VER = "v1.1.0"
REPO_URL = "https://api.github.com/repos/ZonkedHobgoblin/mediafetch/releases/latest"

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
OS_NAME = platform.system()