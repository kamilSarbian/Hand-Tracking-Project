import ui.drawing_screen as drawing_module
import ui.help_screen as help_module
import ui.recording_screen as recording_module
import ui.screenshot_screen as screenshot_module
from ui.drawing_screen import DrawingScreen
from ui.help_screen import HelpScreen
from ui.recording_screen import RecordingScreen
from ui.screenshot_screen import ScreenshotScreen


def test_drawing_back_requires_full_hold(monkeypatch):
    now = 100.0
    monkeypatch.setattr(drawing_module.time, "monotonic", lambda: now)

    screen = DrawingScreen()
    screen.back_button_rect = (0, 0, 100, 100)
    pointer = (50, 50)

    assert screen.try_go_back(pointer, "PINCH") is False

    now = 102.0
    assert screen.try_go_back(pointer, "PINCH") is False

    now = 103.1
    assert screen.try_go_back(pointer, "PINCH") is True


def test_screenshot_back_cancels_when_pinch_released(monkeypatch):
    now = 100.0
    monkeypatch.setattr(screenshot_module.time, "monotonic", lambda: now)

    screen = ScreenshotScreen()
    screen.back_button_rect = (0, 0, 100, 100)
    pointer = (50, 50)

    assert screen.try_go_back(pointer, "PINCH") is False

    now = 101.0
    assert screen.try_go_back(pointer, "UNKNOWN") is False

    now = 104.5
    assert screen.try_go_back(pointer, "PINCH") is False


def test_recording_back_cancels_when_pointer_leaves(monkeypatch):
    now = 100.0
    monkeypatch.setattr(recording_module.time, "monotonic", lambda: now)

    screen = RecordingScreen()
    screen.back_button_rect = (0, 0, 100, 100)

    assert screen.try_go_back((50, 50), "PINCH") is False

    now = 101.0
    assert screen.try_go_back((150, 150), "PINCH") is False

    now = 104.5
    assert screen.try_go_back((50, 50), "PINCH") is False


def test_help_back_requires_full_hold(monkeypatch):
    now = 100.0
    monkeypatch.setattr(help_module.time, "monotonic", lambda: now)

    screen = HelpScreen()
    screen.back_button_rect = (0, 0, 100, 100)
    pointer = (50, 50)

    assert screen.try_go_back(pointer, "PINCH") is False

    now = 103.0
    assert screen.try_go_back(pointer, "PINCH") is True
