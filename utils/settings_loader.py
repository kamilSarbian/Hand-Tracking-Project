import json
from pathlib import Path


def load_settings(path: str = "settings.json") -> dict:
    settings_path = Path(path)

    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")

    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)