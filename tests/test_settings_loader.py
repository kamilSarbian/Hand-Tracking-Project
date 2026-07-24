import json
from pathlib import Path

import pytest

from utils.settings_loader import SettingsValidationError, load_settings


def test_load_settings_reads_explicit_path(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps({"camera_index": 2}),
        encoding="utf-8",
    )

    assert load_settings(settings_path) == {"camera_index": 2}


def test_load_settings_reports_missing_path(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError, match="Settings file not found"):
        load_settings(missing_path)


def test_load_settings_merges_local_override(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    override_path = tmp_path / "settings.local.json"
    settings_path.write_text(
        json.dumps({"camera_index": 0, "output_dir": "outputs"}),
        encoding="utf-8",
    )
    override_path.write_text(
        json.dumps({"output_dir": "C:/custom/outputs"}),
        encoding="utf-8",
    )

    assert load_settings(settings_path, override_path) == {
        "camera_index": 0,
        "output_dir": "C:/custom/outputs",
    }


def test_load_settings_rejects_non_object_json(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("[]", encoding="utf-8")

    with pytest.raises(SettingsValidationError, match="JSON object"):
        load_settings(settings_path)
