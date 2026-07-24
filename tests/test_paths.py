from pathlib import Path

import pytest

from utils.paths import (
    DATA_DIR_ENVIRONMENT_VARIABLE,
    get_resource_path,
    get_user_data_dir,
)


def test_get_resource_path_resolves_project_resource() -> None:
    resource_path = get_resource_path("settings.json")

    assert resource_path.is_absolute()
    assert resource_path.name == "settings.json"
    assert resource_path.exists()


def test_get_resource_path_rejects_parent_traversal() -> None:
    with pytest.raises(ValueError, match="cannot escape"):
        get_resource_path(Path("..") / "outside.txt")


def test_get_user_data_dir_honors_environment_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    custom_data_dir = tmp_path / "custom-data"
    monkeypatch.setenv(DATA_DIR_ENVIRONMENT_VARIABLE, str(custom_data_dir))

    assert get_user_data_dir() == custom_data_dir.resolve()


def test_get_user_data_dir_uses_configured_absolute_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(DATA_DIR_ENVIRONMENT_VARIABLE, raising=False)
    configured_data_dir = tmp_path / "configured-data"

    assert get_user_data_dir(configured_data_dir) == configured_data_dir.resolve()


def test_get_user_data_dir_resolves_relative_path_from_project(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(DATA_DIR_ENVIRONMENT_VARIABLE, raising=False)

    assert get_user_data_dir("outputs") == get_resource_path("outputs")
