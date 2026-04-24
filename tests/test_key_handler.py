import numpy as np

from app.key_handler import KeyHandler


class DummyScreenManager:
    def __init__(self):
        self.current_screen = "drawing"

    def set_screen(self, screen_name):
        self.current_screen = screen_name


class DummyActionService:
    def __init__(self):
        self.status = None
        self.reset_called = False

    def set_status(self, status):
        self.status = status

    def reset_gesture_state(self):
        self.reset_called = True


class DummyRecorder:
    def __init__(self):
        self.is_recording = False
        self.started = False
        self.stopped = False

    def start(self, width, height):
        self.is_recording = True
        self.started = True
        return "fake_recording.mp4"

    def stop(self):
        self.is_recording = False
        self.stopped = True
        return "fake_recording.mp4"


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_handle_escape_returns_true(tmp_path):
    """
    ESC should close the app.
    """
    handler = KeyHandler(
        screen_manager=DummyScreenManager(),
        action_service=DummyActionService(),
        recorder=DummyRecorder(),
        screenshot_dir=str(tmp_path),
        logger=DummyLogger(),
    )

    frame = np.zeros((100, 100, 3), dtype="uint8")
    should_close = handler.handle(27, frame)

    assert should_close is True


def test_handle_m_returns_to_menu(tmp_path):
    """
    M should return to the menu.
    """
    screen_manager = DummyScreenManager()
    action_service = DummyActionService()

    handler = KeyHandler(
        screen_manager=screen_manager,
        action_service=action_service,
        recorder=DummyRecorder(),
        screenshot_dir=str(tmp_path),
        logger=DummyLogger(),
    )

    frame = np.zeros((100, 100, 3), dtype="uint8")
    should_close = handler.handle(ord("m"), frame)

    assert should_close is False
    assert screen_manager.current_screen == "menu"
    assert action_service.reset_called is True


def test_handle_r_starts_recording(tmp_path):
    """
    R should start recording.
    """
    recorder = DummyRecorder()
    action_service = DummyActionService()

    handler = KeyHandler(
        screen_manager=DummyScreenManager(),
        action_service=action_service,
        recorder=recorder,
        screenshot_dir=str(tmp_path),
        logger=DummyLogger(),
    )

    frame = np.zeros((200, 300, 3), dtype="uint8")
    should_close = handler.handle(ord("r"), frame)

    assert should_close is False
    assert recorder.started is True
    assert action_service.status == "Recording started"
