import logging
from pathlib import Path

import pytest

from app import self_check


class DummyDetector:
    def close(self) -> None:
        """Simulate a successful MediaPipe detector shutdown."""


def test_run_self_check_validates_runtime_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "hand_landmarker.task"
    ffmpeg_path = tmp_path / "ffmpeg.exe"
    model_path.touch()
    ffmpeg_path.touch()

    monkeypatch.setattr(self_check, "MODEL_PATH", str(model_path))
    monkeypatch.setattr(
        self_check.imageio_ffmpeg,
        "get_ffmpeg_exe",
        lambda: str(ffmpeg_path),
    )
    monkeypatch.setattr(
        self_check.sounddevice,
        "get_portaudio_version",
        lambda: (1, "PortAudio test"),
    )
    monkeypatch.setattr(self_check, "HandDetector", DummyDetector)

    assert self_check.run_self_check(logging.getLogger("test-self-check")) == 0


def test_run_self_check_fails_when_model_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        self_check,
        "MODEL_PATH",
        str(tmp_path / "missing.task"),
    )

    assert self_check.run_self_check(logging.getLogger("test-self-check")) == 1
