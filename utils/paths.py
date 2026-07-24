import os
import sys
from pathlib import Path

APP_DIRECTORY_NAME = "Gesture Drawing App"
DATA_DIR_ENVIRONMENT_VARIABLE = "GESTURE_DRAWING_APP_DATA_DIR"


def get_resource_root() -> Path:
    """Return the root directory containing bundled read-only resources.

    Returns:
        Project root during development or the PyInstaller extraction directory
        in a frozen application.

    Raises:
        RuntimeError: If a frozen application does not expose its bundle path.
    """
    if getattr(sys, "frozen", False):
        bundle_path = getattr(sys, "_MEIPASS", None)
        if bundle_path is None:
            raise RuntimeError("Frozen application bundle path is unavailable")
        return Path(bundle_path).resolve()

    return Path(__file__).resolve().parent.parent


def get_resource_path(relative_path: str | Path) -> Path:
    """Resolve a project resource without allowing traversal outside its root.

    Args:
        relative_path: Path relative to the project or frozen bundle root.

    Returns:
        Absolute path to the requested resource.

    Raises:
        ValueError: If the path is absolute or escapes the resource root.
    """
    requested_path = Path(relative_path)
    if requested_path.is_absolute():
        raise ValueError("Resource path must be relative")

    resource_root = get_resource_root()
    resolved_path = (resource_root / requested_path).resolve()
    if not resolved_path.is_relative_to(resource_root):
        raise ValueError("Resource path cannot escape the resource root")

    return resolved_path


def get_user_data_dir(configured_path: str | Path | None = None) -> Path:
    """Return the writable directory used for user-generated application data.

    The ``GESTURE_DRAWING_APP_DATA_DIR`` environment variable can override the
    configured location, which is useful for portable deployments and
    automated tests.

    Args:
        configured_path: Optional path from application settings. Relative paths
            are resolved from the project or frozen resource root.

    Returns:
        Absolute path to the application data directory.
    """
    environment_path = os.environ.get(DATA_DIR_ENVIRONMENT_VARIABLE)
    if environment_path:
        return Path(environment_path).expanduser().resolve()

    if configured_path is not None:
        settings_path = Path(configured_path).expanduser()
        if settings_path.is_absolute():
            return settings_path.resolve()
        if getattr(sys, "frozen", False):
            return (Path(sys.executable).resolve().parent / settings_path).resolve()
        return (get_resource_root() / settings_path).resolve()

    return (Path.home() / "Documents" / APP_DIRECTORY_NAME).resolve()
