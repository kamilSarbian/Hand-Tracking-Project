import hashlib
from io import BytesIO
from pathlib import Path

import pytest

from scripts import download_model


class FakeResponse(BytesIO):
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def test_download_model_reuses_valid_existing_file(tmp_path: Path) -> None:
    payload = b"valid-model"
    destination = tmp_path / "hand_landmarker.task"
    destination.write_bytes(payload)
    expected_sha256 = hashlib.sha256(payload).hexdigest()

    result = download_model.download_model(
        destination=destination,
        expected_sha256=expected_sha256,
    )

    assert result == destination.resolve()
    assert destination.read_bytes() == payload


def test_download_model_downloads_and_verifies_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = b"downloaded-model"
    destination = tmp_path / "models" / "hand_landmarker.task"
    expected_sha256 = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(
        download_model,
        "urlopen",
        lambda *_args, **_kwargs: FakeResponse(payload),
    )

    result = download_model.download_model(
        destination=destination,
        model_url="https://example.invalid/model.task",
        expected_sha256=expected_sha256,
    )

    assert result == destination.resolve()
    assert destination.read_bytes() == payload


def test_download_model_rejects_invalid_checksum(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "hand_landmarker.task"
    monkeypatch.setattr(
        download_model,
        "urlopen",
        lambda *_args, **_kwargs: FakeResponse(b"invalid-model"),
    )

    with pytest.raises(
        download_model.ModelDownloadError,
        match="checksum mismatch",
    ):
        download_model.download_model(
            destination=destination,
            model_url="https://example.invalid/model.task",
            expected_sha256="0" * 64,
        )

    assert not destination.exists()
    assert not destination.with_suffix(".task.download").exists()
