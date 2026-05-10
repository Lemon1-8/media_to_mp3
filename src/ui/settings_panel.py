from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QComboBox, QCheckBox, QPushButton, QFileDialog, QLineEdit,
    QGroupBox,
)


class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._convert_callback = None
        self._setup_ui()

    def on_convert_clicked(self, callback):
        self._convert_callback = callback

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("转换设置")
        group_layout = QVBoxLayout(group)

        bitrate_row = QHBoxLayout()
        bitrate_row.addWidget(QLabel("比特率:"))
        self._bitrate_combo = QComboBox()
        self._bitrate_combo.addItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])
        self._bitrate_combo.setCurrentIndex(1)
        bitrate_row.addWidget(self._bitrate_combo)
        bitrate_row.addStretch()
        group_layout.addLayout(bitrate_row)

        dir_row = QHBoxLayout()
        self._use_source_cb = QCheckBox("输出到源文件夹")
        self._use_source_cb.setChecked(True)
        self._use_source_cb.toggled.connect(self._on_toggle_source_dir)
        dir_row.addWidget(self._use_source_cb)

        self._output_dir_edit = QLineEdit()
        self._output_dir_edit.setPlaceholderText("选择输出目录...")
        self._output_dir_edit.setEnabled(False)
        dir_row.addWidget(self._output_dir_edit)

        self._browse_btn = QPushButton("浏览...")
        self._browse_btn.setEnabled(False)
        self._browse_btn.clicked.connect(self._on_browse)
        dir_row.addWidget(self._browse_btn)
        group_layout.addLayout(dir_row)

        self._preserve_meta_cb = QCheckBox("保留元数据（艺术家、标题等）")
        self._preserve_meta_cb.setChecked(True)
        group_layout.addWidget(self._preserve_meta_cb)

        layout.addWidget(group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._convert_btn = QPushButton("开始转换")
        self._convert_btn.setMinimumWidth(160)
        self._convert_btn.setMinimumHeight(36)
        self._convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 24px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """)
        self._convert_btn.clicked.connect(self._on_convert)
        btn_row.addWidget(self._convert_btn)
        layout.addLayout(btn_row)

    def get_bitrate(self) -> int:
        text = self._bitrate_combo.currentText()
        return int(text.split()[0])

    def get_output_dir(self) -> str:
        return self._output_dir_edit.text()

    def get_use_source_dir(self) -> bool:
        return self._use_source_cb.isChecked()

    def get_preserve_metadata(self) -> bool:
        return self._preserve_meta_cb.isChecked()

    def set_converting(self, converting: bool):
        self._convert_btn.setEnabled(not converting)
        self._convert_btn.setText("转换中..." if converting else "开始转换")
        self._bitrate_combo.setEnabled(not converting)

    def _on_toggle_source_dir(self, checked: bool):
        self._output_dir_edit.setEnabled(not checked)
        self._browse_btn.setEnabled(not checked)

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self._output_dir_edit.setText(folder)

    def _on_convert(self):
        if self._convert_callback:
            self._convert_callback()
