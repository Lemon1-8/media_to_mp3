import pytest
from src.utils.metadata_handler import MetadataHandler


class TestMetadataHandler:
    def test_read_metadata_nonexistent_file(self):
        handler = MetadataHandler()
        result = handler.read_metadata("/nonexistent/file.mp3")
        assert result is None

    def test_write_tags_noop_without_metadata(self):
        handler = MetadataHandler()
        handler.write_tags("/fake/path.mp3", None)

    def test_write_tags_noop_with_empty_metadata(self):
        handler = MetadataHandler()
        handler.write_tags("/fake/path.mp3", {})
