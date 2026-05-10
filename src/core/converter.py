from PyQt5.QtCore import QObject, pyqtSignal

from .ffmpeg_wrapper import FFmpegWrapper
from ..utils.resource_manager import get_ffmpeg_path
from ..utils.metadata_handler import MetadataHandler
from ..utils.file_utils import generate_output_path


class ConverterEngine(QObject):
    all_finished = pyqtSignal(int, int, int)
    queue_progress = pyqtSignal(int, int)
    file_progress = pyqtSignal(str, float)
    phase_changed = pyqtSignal(str)
    file_finished = pyqtSignal(int, bool, str)

    def __init__(self, queue_manager, parent=None):
        super().__init__(parent)
        self._queue = queue_manager
        self._ffmpeg = FFmpegWrapper(get_ffmpeg_path())
        self._metadata = MetadataHandler()
        self._running = False
        self._success_count = 0
        self._fail_count = 0
        self._current_index = -1
        self._bitrate = 192
        self._output_dir = ""
        self._use_source_dir = True
        self._preserve_metadata = True
        self._processing = False
        self._source_meta = None
        self._output_path = ""

        self._ffmpeg.progress_updated.connect(self._on_progress)
        self._ffmpeg.phase_changed.connect(self._on_phase)
        self._ffmpeg.finished.connect(self._on_file_done)
        self._ffmpeg.error_occurred.connect(self._on_file_error)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def current_index(self) -> int:
        return self._current_index

    def set_options(self, bitrate: int, output_dir: str, use_source_dir: bool, preserve_metadata: bool):
        self._bitrate = bitrate
        self._output_dir = output_dir
        self._use_source_dir = use_source_dir
        self._preserve_metadata = preserve_metadata

    def start(self):
        if self._running:
            return
        self._running = True
        self._success_count = 0
        self._fail_count = 0
        self._current_index = -1
        self._processing = False
        self._process_next()

    def cancel(self):
        self._ffmpeg.cancel()
        self._queue.reset_all()
        self._running = False
        self._processing = False

    def _process_next(self):
        if self._processing:
            return
        self._processing = True

        try:
            items = self._queue.items
            for i, item in enumerate(items):
                if item.status == "pending":
                    self._current_index = i
                    self._queue.update_status(i, "converting", 0.0)

                    output_path = generate_output_path(
                        item.path,
                        output_dir=self._output_dir,
                        bitrate=self._bitrate,
                        use_source_dir=self._use_source_dir,
                    )

                    source_metadata = None
                    if self._preserve_metadata:
                        source_metadata = self._metadata.read_metadata(item.path)
                    self._source_meta = source_metadata
                    self._output_path = output_path

                    self._ffmpeg.convert(item.path, output_path, self._bitrate)
                    self.queue_progress.emit(i + 1, len(items))
                    return

            self._running = False
            self.all_finished.emit(self._success_count, self._fail_count, len(items))
        finally:
            self._processing = False

    def _on_progress(self, filename: str, progress: float):
        if self._current_index >= 0:
            self._queue.update_status(self._current_index, "converting", progress)
        self.file_progress.emit(filename, progress)

    def _on_phase(self, phase: str):
        self.phase_changed.emit(phase)

    def _on_file_done(self, filename: str, success: bool, error_msg: str):
        if self._current_index >= 0:
            if success:
                self._queue.update_status(self._current_index, "done", 1.0)
                self._success_count += 1
                if self._preserve_metadata and self._source_meta:
                    try:
                        self._metadata.write_tags(self._output_path, self._source_meta)
                    except Exception:
                        pass
            else:
                self._queue.update_status(self._current_index, "error", 0.0, error_msg)
                self._fail_count += 1

            self.file_finished.emit(self._current_index, success, error_msg)

        self._process_next()

    def _on_file_error(self, filename: str, error_msg: str):
        self._on_file_done(filename, False, error_msg)
