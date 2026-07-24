# Hand Tracking Effects

[![CI](https://github.com/kamilSarbian/Hand-Tracking-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/kamilSarbian/Hand-Tracking-Project/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A real-time gesture-controlled drawing app built with Python, OpenCV, and the MediaPipe Tasks API.

The app reads a webcam feed, detects up to two hands, identifies left and right hands, measures the distance between the thumb and index finger, and maps hand poses to gestures such as `PINCH`, `POINT`, `PEACE`, `FIST`, `OPEN_HAND`, `THREE`, `ROCK`, and `THUMBS_UP`.

## Features

- Real-time hand tracking
- Support for up to two hands
- Left/right hand detection
- Gesture-controlled menu
- Three-second countdown before opening a selected mode
- Drawing mode with color switching and canvas clearing
- Screenshot mode with gesture or keyboard capture
- Recording mode for app demos, with optional microphone audio
- Modular project structure
- Configurable settings from JSON
- Unit tests for service and controller logic

## Controls

- tight `PINCH` in the menu: select an option
- `POINT` in drawing mode: draw
- tight `PINCH` in drawing mode: change color
- `FIST` in drawing mode: clear canvas
- `OPEN_HAND` in drawing mode: pause drawing
- `PEACE` in screenshot mode: save screenshot
- `M`: return to menu
- `S`: save manual screenshot
- `R`: start or stop recording
- `ESC`: close the app

## Tech Stack

- Python
- OpenCV
- MediaPipe Tasks API
- NumPy
- Pillow
- sounddevice
- imageio-ffmpeg
- pytest

## Project Structure

```text
hand_tracking_project/
|-- main.py
|-- config.py
|-- settings.json
|-- settings.local.example.json
|-- hand_tracking.spec
|-- scripts/
|-- app/
|-- core/
|-- gestures/
|-- models/
|-- services/
|-- ui/
|-- utils/
|-- tests/
`-- models_assets/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/kamilSarbian/Hand-Tracking-Project.git
cd Hand-Tracking-Project
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

For development tools and tests:

```bash
pip install -r requirements-dev.txt
```

Download and verify the official MediaPipe Hand Landmarker model:

```bash
python scripts/download_model.py
```

The script stores the model here:

```text
models_assets/hand_landmarker.task
```

The model file is intentionally ignored by Git because it is a downloaded
asset. The download script uses the versioned model published in the official
[MediaPipe Hand Landmarker documentation](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/index#models)
and verifies its SHA-256 checksum.

### Local settings

Public defaults live in `settings.json`. To override them without committing
machine-specific paths, copy the example file:

```powershell
Copy-Item settings.local.example.json settings.local.json
```

Then edit `settings.local.json`. This file is ignored by Git and its values
override matching values from `settings.json`.

Run the app:

```bash
python main.py
```

Run tests:

```bash
pytest
```

On Windows, if pytest cannot access the default temp directory, run it with a custom temp location:

```powershell
python -m pytest -q --basetemp=pytest-tmp-run
```

## Notes

If mirrored view is enabled, hand labels are adjusted so the displayed left/right side matches the webcam preview.

Screenshots, recordings, and rotating logs are saved under the `output_dir`
configured in `settings.json`. The public default is the repository's
`outputs/` directory. A packaged executable without a local override uses an
`outputs/` directory next to the executable.

Set `GESTURE_DRAWING_APP_DATA_DIR` before starting the application to
temporarily override both JSON files.

## Windows executable

Use a dedicated virtual environment so packaging dependencies do not affect the
development environment:

```powershell
python -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
```

Build the diagnostic directory bundle and the final single-file executable:

```powershell
.\scripts\build_exe.ps1
```

Individual build modes are also available:

```powershell
.\scripts\build_exe.ps1 -Mode onedir
.\scripts\build_exe.ps1 -Mode onefile
```

Build artifacts are written to:

```text
dist/onedir/GestureDrawingApp-debug/GestureDrawingApp-debug.exe
dist/onefile/GestureDrawingApp.exe
```

The diagnostic build keeps a console window open to expose startup errors. The
single-file build starts without a console and can take a few seconds to unpack
on first launch. Each build automatically runs an executable self-check for the
MediaPipe model, MediaPipe runtime, FFmpeg, and PortAudio. The same check can be
started manually:

```powershell
.\dist\onefile\GestureDrawingApp.exe --self-test
```

The executable bundles `settings.json`,
`models_assets/hand_landmarker.task`, and `settings.local.json` when the latter
exists during a local build. Generated files use the configured output
directory:

```text
outputs/
|-- logs/application.log
|-- recordings/
`-- screenshots/
```

Build artifacts under `build/` and `dist/` are ignored by Git. Publish compiled
executables through GitHub Releases instead of committing them to the
repository.

## License

This project is licensed under the [MIT License](LICENSE).
