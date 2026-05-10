import os
import sys


def get_ffmpeg_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.join(sys._MEIPASS, "tools", "ffmpeg")
    else:
        base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "tools",
            "ffmpeg",
        )

    ffmpeg = os.path.join(base, "ffmpeg.exe")
    if os.path.isfile(ffmpeg):
        return ffmpeg

    raise FileNotFoundError(f"找不到 FFmpeg 引擎，请检查 tools/ffmpeg/ffmpeg.exe 是否存在")
