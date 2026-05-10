import pytest
from src.utils.format_registry import (
    SUPPORTED_FORMATS,
    AUDIO_EXTENSIONS,
    VIDEO_EXTENSIONS,
    ALL_EXTENSIONS,
    is_supported,
    get_category,
    get_mime,
)


class TestFormatRegistry:
    def test_all_formats_have_category_and_mime(self):
        for ext, info in SUPPORTED_FORMATS.items():
            assert "category" in info, f"{ext} missing category"
            assert "mime" in info, f"{ext} missing mime"
            assert info["category"] in ("audio", "video"), f"{ext} invalid category"

    def test_no_duplicate_extensions(self):
        assert len(SUPPORTED_FORMATS) == len(ALL_EXTENSIONS)

    def test_audio_and_video_sets_are_disjoint(self):
        assert AUDIO_EXTENSIONS.isdisjoint(VIDEO_EXTENSIONS)

    def test_is_supported(self):
        assert is_supported(".mp3")
        assert is_supported(".MP4")
        assert is_supported(".wav")
        assert not is_supported(".txt")
        assert not is_supported(".png")

    def test_get_category(self):
        assert get_category(".mp3") == "audio"
        assert get_category(".mp4") == "video"
        assert get_category(".xyz") == "unknown"

    def test_get_mime(self):
        assert get_mime(".mp3") == "audio/mpeg"
        assert get_mime(".mp4") == "video/mp4"
        assert get_mime(".txt") == "application/octet-stream"
