import os
import tempfile
import pytest
from PyQt5.QtCore import QCoreApplication
from src.core.queue_manager import QueueManager, QueuedFile


@pytest.fixture(scope="module")
def qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.fixture
def manager():
    return QueueManager()


def test_queued_file_initial_state():
    qf = QueuedFile("/path/to/song.mp3")
    assert qf.path == "/path/to/song.mp3"
    assert qf.status == "pending"
    assert qf.progress == 0.0
    assert qf.error == ""


class TestQueueManager:
    def test_empty_on_init(self, manager):
        assert manager.count == 0
        assert manager.items == []

    def test_add_supported_file(self, manager):
        added = manager.add_files(["song.mp3", "video.mp4"])
        assert added == 2
        assert manager.count == 2

    def test_skip_duplicates(self, manager):
        files = ["song.mp3", "song.mp3", "video.mp4"]
        added = manager.add_files(files)
        assert added == 2

    def test_remove_items(self, manager):
        manager.add_files(["a.mp3", "b.mp3", "c.mp3"])
        manager.remove_items([1])
        assert manager.count == 2
        assert manager.items[1].filename == "c.mp3"

    def test_clear_all(self, manager):
        manager.add_files(["a.mp3", "b.mp3"])
        manager.clear_all()
        assert manager.count == 0

    def test_move_item(self, manager):
        manager.add_files(["a.mp3", "b.mp3", "c.mp3"])
        manager.move_item(0, 2)
        assert manager.items[0].filename == "b.mp3"
        assert manager.items[2].filename == "a.mp3"

    def test_clear_completed(self, manager):
        manager.add_files(["a.mp3", "b.mp3", "c.mp3"])
        manager.update_status(0, "done")
        manager.update_status(1, "error")
        manager.clear_completed()
        assert manager.count == 1
        assert manager.items[0].filename == "c.mp3"

    def test_reset_all(self, manager):
        manager.add_files(["a.mp3"])
        manager.update_status(0, "done", 1.0)
        manager.reset_all()
        assert manager.items[0].status == "pending"
        assert manager.items[0].progress == 0.0

    def test_signal_emitted_on_add(self, manager):
        signals = []
        manager.queue_changed.connect(lambda: signals.append(1))
        manager.add_files(["song.mp3"])
        assert len(signals) == 1
