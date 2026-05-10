import os
import re

from .format_registry import is_supported, get_category


def get_extension(path: str) -> str:
    _, ext = os.path.splitext(path)
    return ext.lower()


def is_supported_format(path: str) -> bool:
    return is_supported(get_extension(path))


def guess_format_category(path: str) -> str:
    return get_category(get_extension(path))


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*]')


def sanitize_filename(name: str) -> str:
    name = INVALID_CHARS_RE.sub("_", name)
    name = name.strip(". ")
    return name or "output"


def generate_output_path(
    input_path: str,
    output_dir: str | None = None,
    bitrate: int = 192,
    use_source_dir: bool = True,
) -> str:
    dir_name = os.path.dirname(input_path) if use_source_dir else (output_dir or os.path.dirname(input_path))
    base_name, _ = os.path.splitext(os.path.basename(input_path))
    base_name = sanitize_filename(base_name)

    output_name = f"{base_name}_{bitrate}kbps.mp3"
    output_path = os.path.join(dir_name, output_name)

    counter = 1
    while os.path.exists(output_path):
        output_name = f"{base_name}_{bitrate}kbps_{counter}.mp3"
        output_path = os.path.join(dir_name, output_name)
        counter += 1

    return output_path
