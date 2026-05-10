from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 Qoder")
        self.setFixedSize(360, 200)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Qoder")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a73e8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel("版本 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        desc = QLabel("音视频文件转 MP3 格式工具\n基于 FFmpeg 引擎")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)

        ffmpeg_note = QLabel("本工具使用了 FFmpeg (LGPL/GPL 许可证)")
        ffmpeg_note.setAlignment(Qt.AlignCenter)
        ffmpeg_note.setStyleSheet("color: #999; font-size: 10px;")
        layout.addWidget(ffmpeg_note)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
