import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QProgressBar, QPushButton, QHeaderView, QAbstractItemView, QMenu, QAction,
    QLabel,
)

from ..utils.file_utils import format_file_size, get_extension

STATUS_COLORS = {
    "pending": QColor("#888"),
    "converting": QColor("#1a73e8"),
    "done": QColor("#34a853"),
    "error": QColor("#ea4335"),
}

STATUS_LABELS = {
    "pending": "等待",
    "converting": "转换中",
    "done": "完成",
    "error": "失败",
}


class QueueWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue_manager = None
        self._setup_ui()

    def set_queue_manager(self, manager):
        self._queue_manager = manager
        self._queue_manager.queue_changed.connect(self._refresh)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.addWidget(QLabel("文件队列"))
        header.addStretch()

        self._clear_done_btn = QPushButton("清除已完成")
        self._clear_done_btn.clicked.connect(self._on_clear_done)
        header.addWidget(self._clear_done_btn)

        self._clear_all_btn = QPushButton("清空全部")
        self._clear_all_btn.clicked.connect(self._on_clear_all)
        header.addWidget(self._clear_all_btn)

        layout.addLayout(header)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["文件名", "格式", "大小", "进度", "状态"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)

        self._empty_label = QLabel("暂无文件\n拖放或点击上方按钮添加", self._table)
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet("color: #aaa; font-size: 14px;")

        layout.addWidget(self._table)

    def _refresh(self):
        if not self._queue_manager:
            return

        items = self._queue_manager.items
        self._table.setRowCount(len(items))

        for i, item in enumerate(items):
            name_item = QTableWidgetItem(item.filename)
            name_item.setToolTip(item.path)
            self._table.setItem(i, 0, name_item)

            self._table.setItem(i, 1, QTableWidgetItem(get_extension(item.filename)))

            try:
                size = os.path.getsize(item.path)
                self._table.setItem(i, 2, QTableWidgetItem(format_file_size(size)))
            except OSError:
                self._table.setItem(i, 2, QTableWidgetItem("?"))

            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setValue(
                100 if item.status == "done"
                else int(item.progress * 100) if item.status == "converting"
                else 0
            )
            progress_bar.setFixedWidth(150)
            self._table.setCellWidget(i, 3, progress_bar)

            status_text = STATUS_LABELS.get(item.status, item.status)
            if item.status == "error" and item.error:
                status_text = f"失败: {item.error}"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(STATUS_COLORS.get(item.status, QColor("#888")))
            self._table.setItem(i, 4, status_item)

        self._update_empty_state()

    def _update_empty_state(self):
        count = self._queue_manager.count if self._queue_manager else 0
        self._empty_label.setVisible(count == 0)
        self._table.setVisible(count > 0)

    def _on_context_menu(self, pos):
        items = self._table.selectedItems()
        if not items:
            return

        menu = QMenu(self)
        remove_action = QAction("移除已选择", self)
        remove_action.triggered.connect(self._on_remove_selected)
        menu.addAction(remove_action)

        menu.addSeparator()
        clear_done_action = QAction("清除已完成", self)
        clear_done_action.triggered.connect(self._on_clear_done)
        menu.addAction(clear_done_action)

        clear_all_action = QAction("清空全部", self)
        clear_all_action.triggered.connect(self._on_clear_all)
        menu.addAction(clear_all_action)

        menu.exec_(self._table.viewport().mapToGlobal(pos))

    def _on_remove_selected(self):
        if not self._queue_manager:
            return
        rows = {index.row() for index in self._table.selectedIndexes()}
        self._queue_manager.remove_items(sorted(rows, reverse=True))

    def _on_clear_done(self):
        if self._queue_manager:
            self._queue_manager.clear_completed()

    def _on_clear_all(self):
        if self._queue_manager:
            self._queue_manager.clear_all()
