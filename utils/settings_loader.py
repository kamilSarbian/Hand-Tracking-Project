import json
from pathlib import Path

from utils.paths import get_resource_path


class SettingsValidationError(ValueError):
    """Raised when a settings file does not contain a JSON object."""


def _read_settings_file(settings_path: Path) -> dict[str, object]:
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    with settings_path.open("r", encoding="utf-8") as settings_file:
        settings = json.load(settings_file)

    if not isinstance(settings, dict):
        raise SettingsValidationError(
            f"Settings file must contain a JSON object: {settings_path}"
        )

    return settings


def load_settings(
    path: str | Path | None = None,
    override_path: str | Path | None = None,
) -> dict[str, object]:
    """Load application settings from JSON.

    Args:
        path: Optional explicit settings path. When omitted, the settings file
            bundled with the application is used.
        override_path: Optional local settings file whose values override the
            base settings. When both arguments are omitted,
            ``settings.local.json`` is loaded automatically if present.

    Returns:
        Parsed and merged settings mapping.

    Raises:
        FileNotFoundError: If the settings file does not exist.
        json.JSONDecodeError: If the settings file is not valid JSON.
        SettingsValidationError: If a settings file is not a JSON object.
        OSError: If the settings file cannot be read.
    """
    settings_path = (
        Path(path) if path is not None else get_resource_path("settings.json")
    )
    settings = _read_settings_file(settings_path)

    local_settings_path: Path | None
    if override_path is not None:
        local_settings_path = Path(override_path)
    elif path is None:
        local_settings_path = get_resource_path("settings.local.json")
    else:
        local_settings_path = None

    if local_settings_path is not None and local_settings_path.exists():
        settings.update(_read_settings_file(local_settings_path))

    return settings
