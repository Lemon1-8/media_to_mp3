from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QAction, QMessageBox,
)

from .file_drop_widget import FileDropWidget
from .queue_widget import QueueWidget
from .settings_panel import SettingsPanel
from .about_dialog import AboutDialog

from ..core.queue_manager import QueueManager
from ..core.converter import ConverterEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qoder - MP3 转换工具")
        self.setMinimumSize(800, 600)

        self._queue_manager = QueueManager()
        self._converter = ConverterEngine(self._queue_manager)

        self._setup_ui()
        self._setup_menu()
        self._connect_signals()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self._drop_widget = FileDropWidget()
        self._drop_widget.on_files_dropped(self._on_files_added)
        main_layout.addWidget(self._drop_widget)

        self._queue_widget = QueueWidget()
        self._queue_widget.set_queue_manager(self._queue_manager)
        main_layout.addWidget(self._queue_widget, 1)

        self._settings_panel = SettingsPanel()
        self._settings_panel.on_convert_clicked(self._on_convert)
        main_layout.addWidget(self._settings_panel)

        self.statusBar().showMessage("就绪")

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")

        add_file_action = QAction("添加文件", self)
        add_file_action.triggered.connect(self._drop_widget.trigger_add_file)
        file_menu.addAction(add_file_action)

        add_folder_action = QAction("添加文件夹", self)
        add_folder_action.triggered.connect(self._drop_widget.trigger_add_folder)
        file_menu.addAction(add_folder_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于 Qoder", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self):
        self._converter.all_finished.connect(self._on_all_finished)
        self._converter.queue_progress.connect(self._on_queue_progress)
        self._converter.file_progress.connect(self._on_file_progress)
        self._converter.phase_changed.connect(self._on_phase_changed)

    def _on_files_added(self, paths: list[str]):
        self._queue_manager.add_files(paths)
        count = self._queue_manager.count
        self.statusBar().showMessage(f"队列: {count} 个文件")

    def _on_convert(self):
        if self._converter.is_running:
            self._converter.cancel()
            self._settings_panel.set_converting(False)
            self.statusBar().showMessage("已取消")
            return

        if self._queue_manager.pending_count == 0:
            QMessageBox.information(self, "提示", "没有等待转换的文件")
            return

        self._converter.set_options(
            bitrate=self._settings_panel.get_bitrate(),
            output_dir=self._settings_panel.get_output_dir(),
            use_source_dir=self._settings_panel.get_use_source_dir(),
            preserve_metadata=self._settings_panel.get_preserve_metadata(),
        )
        self._settings_panel.set_converting(True)
        self._converter.start()
        self.statusBar().showMessage("转换中...")

    def _on_all_finished(self, success: int, failed: int, total: int):
        self._settings_panel.set_converting(False)
        self.statusBar().showMessage(f"转换完成: 成功 {success}, 失败 {failed}")
        QMessageBox.information(
            self, "转换完成",
            f"转换结束\n成功: {success}\n失败: {failed}\n总计: {total}"
        )

    def _on_queue_progress(self, current: int, total: int):
        self.statusBar().showMessage(f"正在处理: {current}/{total}")

    def _on_file_progress(self, filename: str, progress: float):
        self.statusBar().showMessage(f"正在转换: {filename} ({int(progress * 100)}%)")

    def _on_phase_changed(self, phase: str):
        if phase:
            self.statusBar().showMessage(phase)

    def _show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()
