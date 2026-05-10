import pytest
from PyQt5.QtCore import QCoreApplication
from src.core.ffmpeg_wrapper import OUT_TIME_US_RE, DURATION_RE, PROGRESS_END_RE


@pytest.fixture(scope="module")
def qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


class TestProgressParsing:
    def test_duration_regex(self):
        match = DURATION_RE.search(b"Duration: 01:23:45.67")
        assert match is not None
        h, m, s, ms = map(int, match.groups())
        assert h == 1
        assert m == 23
        assert s == 45
        assert ms == 67

    def test_out_time_us_regex(self):
        match = OUT_TIME_US_RE.search(b"out_time_us=5000000")
        assert match is not None
        assert int(match.group(1)) == 5000000

    def test_progress_end_regex(self):
        assert PROGRESS_END_RE.search(b"progress=end")
        assert not PROGRESS_END_RE.search(b"progress=continue")
