import os
from PyQt5.QtCore import QObject, pyqtSignal

from ..utils.file_utils import is_supported_format


class QueuedFile:
    def __init__(self, path: str):
        self.path = path
        self.filename = os.path.basename(path)
        self.status = "pending"
        self.progress = 0.0
        self.error = ""


class QueueManager(QObject):
    queue_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[QueuedFile] = []

    @property
    def items(self) -> list[QueuedFile]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def pending_count(self) -> int:
        return sum(1 for item in self._items if item.status == "pending")

    def add_files(self, file_paths: list[str]) -> int:
        added = 0
        existing = {item.path for item in self._items}
        seen = set()

        for path in file_paths:
            norm = path.replace("\\", "/")
            if norm in seen or norm in existing:
                continue
            seen.add(norm)
            if is_supported_format(path):
                self._items.append(QueuedFile(path))
                added += 1

        if added > 0:
            self.queue_changed.emit()
        return added

    def remove_items(self, indices: list[int]):
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self._items):
                del self._items[i]
        self.queue_changed.emit()

    def clear_completed(self):
        self._items = [item for item in self._items if item.status not in ("done", "error")]
        self.queue_changed.emit()

    def clear_all(self):
        self._items.clear()
        self.queue_changed.emit()

    def move_item(self, from_index: int, to_index: int):
        if 0 <= from_index < len(self._items) and 0 <= to_index < len(self._items):
            item = self._items.pop(from_index)
            self._items.insert(to_index, item)
            self.queue_changed.emit()

    def update_status(self, index: int, status: str, progress: float = 0.0, error: str = ""):
        if 0 <= index < len(self._items):
            self._items[index].status = status
            self._items[index].progress = progress
            self._items[index].error = error
            self.queue_changed.emit()

    def reset_all(self):
        for item in self._items:
            item.status = "pending"
            item.progress = 0.0
            item.error = ""
        self.queue_changed.emit()
