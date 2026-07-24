from datetime import datetime
from pathlib import Path

import cv2


def ensure_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def generate_timestamp_filename(prefix: str, extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{timestamp}.{extension}"


def save_screenshot(frame, output_dir: str) -> str:
    directory = ensure_dir(output_dir)
    filename = generate_timestamp_filename("screenshot", "png")
    file_path = directory / filename

    if not cv2.imwrite(str(file_path), frame):
        raise OSError(f"Could not save screenshot: {file_path}")

    return str(file_path)
