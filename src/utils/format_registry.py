SUPPORTED_FORMATS = {
    ".mp3":  {"category": "audio", "mime": "audio/mpeg"},
    ".wav":  {"category": "audio", "mime": "audio/wav"},
    ".flac": {"category": "audio", "mime": "audio/flac"},
    ".ogg":  {"category": "audio", "mime": "audio/ogg"},
    ".aac":  {"category": "audio", "mime": "audio/aac"},
    ".wma":  {"category": "audio", "mime": "audio/x-ms-wma"},
    ".m4a":  {"category": "audio", "mime": "audio/mp4"},
    ".mp4":  {"category": "video", "mime": "video/mp4"},
    ".avi":  {"category": "video", "mime": "video/x-msvideo"},
    ".mkv":  {"category": "video", "mime": "video/x-matroska"},
    ".mov":  {"category": "video", "mime": "video/quicktime"},
    ".webm": {"category": "video", "mime": "video/webm"},
    ".flv":  {"category": "video", "mime": "video/x-flv"},
    ".3gp":  {"category": "video", "mime": "video/3gpp"},
}

AUDIO_EXTENSIONS = {ext for ext, info in SUPPORTED_FORMATS.items() if info["category"] == "audio"}
VIDEO_EXTENSIONS = {ext for ext, info in SUPPORTED_FORMATS.items() if info["category"] == "video"}
ALL_EXTENSIONS = set(SUPPORTED_FORMATS.keys())


def is_supported(ext: str) -> bool:
    return ext.lower() in ALL_EXTENSIONS


def get_category(ext: str) -> str:
    info = SUPPORTED_FORMATS.get(ext.lower())
    return info["category"] if info else "unknown"


def get_mime(ext: str) -> str:
    info = SUPPORTED_FORMATS.get(ext.lower())
    return info["mime"] if info else "application/octet-stream"
