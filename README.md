# Hand Tracking Effects

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

Download the MediaPipe Hand Landmarker task model and place it here:

```text
models_assets/hand_landmarker.task
```

The model file is intentionally ignored by Git because it is a generated/downloaded asset.

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

Screenshots and recordings are saved under `outputs/`, which is ignored by Git.
