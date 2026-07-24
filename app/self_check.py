import logging
from pathlib import Path

import imageio_ffmpeg
import sounddevice

from config import MODEL_PATH
from core.detector import HandDetector


def run_self_check(logger: logging.Logger) -> int:
    """Validate native dependencies and bundled resources without using a camera.

    Args:
        logger: Configured application logger.

    Returns:
        Zero when all checks pass, otherwise a non-zero process exit code.
    """
    model_path = Path(MODEL_PATH)
    if not model_path.is_file():
        logger.error("Self-check failed: MediaPipe model not found at %s", model_path)
        return 1

    try:
        ffmpeg_path = Path(imageio_ffmpeg.get_ffmpeg_exe())
        if not ffmpeg_path.is_file():
            raise FileNotFoundError(f"FFmpeg executable not found: {ffmpeg_path}")

        portaudio_version = sounddevice.get_portaudio_version()

        detector = HandDetector()
        detector.close()
    except (
        FileNotFoundError,
        OSError,
        RuntimeError,
        sounddevice.PortAudioError,
        ValueError,
    ) as exc:
        logger.exception("Self-check failed: %s", exc)
        return 1

    logger.info(
        "Self-check passed | model=%s | ffmpeg=%s | portaudio=%s",
        model_path,
        ffmpeg_path,
        portaudio_version[1],
    )
    return 0
