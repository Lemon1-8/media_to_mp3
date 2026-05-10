import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFileDialog

from ..utils.format_registry import ALL_EXTENSIONS
from ..utils.file_utils import is_supported_format


def _build_file_filter() -> str:
    ext_patterns = " ".join(f"*{ext}" for ext in sorted(ALL_EXTENSIONS))
    return f"音视频文件 ({ext_patterns});;所有文件 (*.*)"


class FileDropWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_callback = None
        self._drag_over = False
        self._setup_ui()
        self.setAcceptDrops(True)

    def on_files_dropped(self, callback):
        self._file_callback = callback

    def trigger_add_file(self):
        self._on_add_file()

    def trigger_add_folder(self):
        self._on_add_folder()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self._drop_label = QLabel("将文件拖放到此处")
        self._drop_label.setAlignment(Qt.AlignCenter)
        self._drop_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 16px;
                border: 2px dashed #aaa;
                border-radius: 8px;
                padding: 40px 20px;
                background: #fafafa;
            }
        """)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self._add_file_btn = QPushButton("添加文件")
        self._add_file_btn.clicked.connect(self._on_add_file)

        self._add_folder_btn = QPushButton("添加文件夹")
        self._add_folder_btn.clicked.connect(self._on_add_folder)

        btn_layout.addWidget(self._add_file_btn)
        btn_layout.addWidget(self._add_folder_btn)

        layout.addWidget(self._drop_label)
        layout.addLayout(btn_layout)

    def _emit_files(self, paths: list[str]):
        if self._file_callback:
            self._file_callback(paths)

    def _on_add_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择音视频文件", "", _build_file_filter()
        )
        if files:
            self._emit_files(files)

    def _on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            paths = []
            for root, _, files in os.walk(folder):
                for f in files:
                    path = os.path.join(root, f)
                    if is_supported_format(path):
                        paths.append(path)
            self._emit_files(paths)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._drag_over = True
            self._update_drop_style()

    def dragLeaveEvent(self, event):
        self._drag_over = False
        self._update_drop_style()

    def dropEvent(self, event: QDropEvent):
        self._drag_over = False
        self._update_drop_style()
        urls = event.mimeData().urls()
        if urls and self._file_callback:
            paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
            self._emit_files(paths)

    def _update_drop_style(self):
        if self._drag_over:
            self._drop_label.setStyleSheet("""
                QLabel {
                    color: #1a73e8;
                    font-size: 16px;
                    border: 2px dashed #1a73e8;
                    border-radius: 8px;
                    padding: 40px 20px;
                    background: #e8f0fe;
                }
            """)
        else:
            self._drop_label.setStyleSheet("""
                QLabel {
                    color: #888;
                    font-size: 16px;
                    border: 2px dashed #aaa;
                    border-radius: 8px;
                    padding: 40px 20px;
                    background: #fafafa;
                }
            """)
