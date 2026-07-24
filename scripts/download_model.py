import argparse
import hashlib
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
DEFAULT_DESTINATION = (
    Path(__file__).resolve().parent.parent / "models_assets" / "hand_landmarker.task"
)


class ModelDownloadError(RuntimeError):
    """Raised when the MediaPipe model cannot be downloaded or verified."""


def calculate_sha256(path: Path) -> str:
    """Calculate a file's SHA-256 digest.

    Args:
        path: File to hash.

    Returns:
        Lowercase hexadecimal SHA-256 digest.

    Raises:
        OSError: If the file cannot be read.
    """
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _remove_partial_download(path: Path) -> str | None:
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        return str(exc)
    return None


def download_model(
    destination: Path = DEFAULT_DESTINATION,
    model_url: str = MODEL_URL,
    expected_sha256: str = MODEL_SHA256,
    force: bool = False,
) -> Path:
    """Download and verify the MediaPipe Hand Landmarker model.

    Args:
        destination: Final model file path.
        model_url: Official model download URL.
        expected_sha256: Expected SHA-256 digest.
        force: Replace an existing file even when its checksum is invalid.

    Returns:
        Path to the verified model.

    Raises:
        ModelDownloadError: If downloading or checksum verification fails.
        OSError: If local directories or files cannot be created.
    """
    destination = destination.resolve()
    if destination.is_file():
        current_sha256 = calculate_sha256(destination)
        if current_sha256 == expected_sha256:
            return destination
        if not force:
            raise ModelDownloadError(
                f"Existing model checksum is invalid: {destination}. "
                "Use --force to replace it."
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial_path = destination.with_suffix(f"{destination.suffix}.download")
    cleanup_error = _remove_partial_download(partial_path)
    if cleanup_error is not None:
        raise ModelDownloadError(
            f"Could not remove stale partial download {partial_path}: "
            f"{cleanup_error}"
        )

    try:
        with urlopen(model_url, timeout=60) as response:
            with partial_path.open("wb") as destination_file:
                while chunk := response.read(1024 * 1024):
                    destination_file.write(chunk)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        cleanup_error = _remove_partial_download(partial_path)
        message = f"Could not download model from {model_url}: {exc}"
        if cleanup_error is not None:
            message += f"; partial-file cleanup failed: {cleanup_error}"
        raise ModelDownloadError(message) from exc

    downloaded_sha256 = calculate_sha256(partial_path)
    if downloaded_sha256 != expected_sha256:
        cleanup_error = _remove_partial_download(partial_path)
        message = (
            "Downloaded model checksum mismatch: "
            f"expected {expected_sha256}, got {downloaded_sha256}"
        )
        if cleanup_error is not None:
            message += f"; partial-file cleanup failed: {cleanup_error}"
        raise ModelDownloadError(message)

    partial_path.replace(destination)
    return destination


def main(argv: list[str] | None = None) -> int:
    """Run the model download command.

    Args:
        argv: Optional command-line arguments.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(
        description="Download the MediaPipe Hand Landmarker model."
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help="Destination model path.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing model with an invalid checksum.",
    )
    arguments = parser.parse_args(argv)

    try:
        model_path = download_model(
            destination=arguments.destination,
            force=arguments.force,
        )
    except (ModelDownloadError, OSError) as exc:
        print(f"Model download failed: {exc}", file=sys.stderr)
        return 1

    print(f"MediaPipe model ready: {model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
