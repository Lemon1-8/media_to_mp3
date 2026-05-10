import os
import tempfile
import pytest
from src.utils.file_utils import (
    is_supported_format,
    guess_format_category,
    format_file_size,
    sanitize_filename,
    generate_output_path,
)


class TestFileUtils:
    def test_is_supported_format(self):
        assert is_supported_format("song.mp3")
        assert is_supported_format("video.MP4")
        assert is_supported_format(os.path.join("path", "to", "song.flac"))
        assert not is_supported_format("readme.txt")
        assert not is_supported_format("image.png")

    def test_guess_format_category(self):
        assert guess_format_category("song.mp3") == "audio"
        assert guess_format_category("video.mp4") == "video"
        assert guess_format_category("file.xyz") == "unknown"

    def test_format_file_size(self):
        assert format_file_size(0) == "0 B"
        assert format_file_size(500) == "500 B"
        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(1048576) == "1.00 MB"
        assert "GB" in format_file_size(1073741824)

    def test_sanitize_filename(self):
        assert sanitize_filename("hello:world") == "hello_world"
        assert sanitize_filename('foo<bar>baz') == "foo_bar_baz"
        assert sanitize_filename("  hello  ") == "hello"
        assert sanitize_filename("...") == "output"

    def test_generate_output_path_use_source_dir(self):
        input_path = os.path.join("home", "user", "song.mp4")
        result = generate_output_path(input_path, bitrate=192, use_source_dir=True)
        assert os.path.dirname(result) == os.path.join("home", "user")
        assert result.endswith("_192kbps.mp3")

    def test_generate_output_path_custom_dir(self):
        input_path = os.path.join("home", "user", "song.mp4")
        result = generate_output_path(
            input_path, output_dir=os.path.sep + "output", bitrate=320, use_source_dir=False
        )
        assert result.startswith(os.path.sep + "output" + os.path.sep)
        assert result.endswith("_320kbps.mp3")

    def test_generate_output_path_handles_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "test.mp4")
            first = generate_output_path(input_path, bitrate=192, use_source_dir=True)
            open(first, "w").close()
            second = generate_output_path(input_path, bitrate=192, use_source_dir=True)
            assert second != first
            assert second.endswith("_1.mp3")
