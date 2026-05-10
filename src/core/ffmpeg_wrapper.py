import os
import re
from PyQt5.QtCore import QObject, QProcess, pyqtSignal


OUT_TIME_US_RE = re.compile(rb"out_time_us=(\d+)")
PROGRESS_END_RE = re.compile(rb"progress=end")
DURATION_RE = re.compile(rb"Duration: (\d+):(\d+):(\d+)\.(\d+)")

KNOWN_ERROR_PATTERNS = [
    (rb"Permission denied", "文件被其他程序占用"),
    (rb"No space left on device", "磁盘空间不足"),
    (rb"Invalid data found when processing", "源文件格式无法识别或已损坏"),
    (rb"Decoder not found", "缺少解码器，不支持的格式"),
    (rb"Connection refused", "网络连接被拒绝"),
    (rb"Output file is empty", "输出为空，请检查源文件"),
    (rb"does not contain any audio stream", "该文件不含音轨"),
]


class FFmpegWrapper(QObject):
    progress_updated = pyqtSignal(str, float)
    phase_changed = pyqtSignal(str)
    finished = pyqtSignal(str, bool, str)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, ffmpeg_path: str, parent=None):
        super().__init__(parent)
        self._ffmpeg_path = ffmpeg_path
        self._process: QProcess | None = None
        self._current_file = ""
        self._duration_us = 0
        self._canceled = False
        self._stderr_buf = b""

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.state() == QProcess.Running

    def convert(self, input_path: str, output_path: str, bitrate: int = 192):
        self._current_file = os.path.basename(input_path)
        self._duration_us = 0
        self._canceled = False
        self._stderr_buf = b""

        if self._process:
            self._process.deleteLater()

        args = [
            self._ffmpeg_path,
            "-i", input_path,
            "-vn",
            "-codec:a", "libmp3lame",
            "-b:a", f"{bitrate}k",
            "-id3v2_version", "3",
            "-write_id3v1", "1",
            "-progress", "pipe:1",
            "-y",
            output_path,
        ]

        self.phase_changed.emit("正在分析...")

        self._process = QProcess()
        self._process.setProcessChannelMode(QProcess.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_error)

        self._process.start(args[0], args[1:])

    def cancel(self):
        self._canceled = True
        if self._process and self._process.state() == QProcess.Running:
            self._process.kill()

    def _on_stdout(self):
        data = self._process.readAllStandardOutput().data()

        if self._duration_us > 0:
            for match in OUT_TIME_US_RE.finditer(data):
                current_us = int(match.group(1))
                progress = min(current_us / self._duration_us, 1.0)
                self.progress_updated.emit(self._current_file, progress)

        if PROGRESS_END_RE.search(data):
            self.progress_updated.emit(self._current_file, 1.0)

    def _on_stderr(self):
        data = self._process.readAllStandardError().data()
        if self._duration_us == 0:
            match = DURATION_RE.search(data)
            if match:
                h, m, s, ms = map(int, match.groups())
                self._duration_us = ((h * 3600 + m * 60 + s) * 1000000) + ms * 10000
        self._stderr_buf += data

    def _on_finished(self, exit_code: int):
        self.phase_changed.emit("")
        success = exit_code == 0 and not self._canceled
        if self._canceled:
            self.finished.emit(self._current_file, False, "已取消")
        elif success:
            self.finished.emit(self._current_file, True, "")
        else:
            error_msg = self._map_error(self._stderr_buf)
            self.finished.emit(self._current_file, False, error_msg)

    def _on_error(self, error: QProcess.ProcessError):
        self.phase_changed.emit("")
        if error == QProcess.FailedToStart:
            self.error_occurred.emit(self._current_file, "FFmpeg 引擎未找到，请重新安装应用")
        else:
            self.error_occurred.emit(self._current_file, f"进程错误: {error}")

    def _map_error(self, stderr_data: bytes) -> str:
        for pattern, msg in KNOWN_ERROR_PATTERNS:
            if pattern.search(stderr_data):
                return msg
        lines = stderr_data.decode("utf-8", errors="replace").strip().split("\n")
        non_empty = [l.strip() for l in lines if l.strip()]
        if non_empty:
            last_msg = non_empty[-1][:200]
            return f"转换失败: {last_msg}"
        return "转换失败，未知错误"
