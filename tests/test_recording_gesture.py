from services.action_service import ActionService
from tests.test_action_service import build_hand


class DummyRecorder:
    def __init__(self):
        self.is_recording = False
        self.started_size = None

    def start(self, frame_width: int, frame_height: int):
        self.is_recording = True
        self.started_size = (frame_width, frame_height)
        return "fake-recording.mp4"

    def stop(self):
        self.is_recording = False
        return "fake-recording.mp4"


def test_recording_actions_toggle_with_rock():
    action_service = ActionService(
        screenshot_dir="outputs/screenshots",
        gesture_cooldown_seconds=0.0,
    )
    recorder = DummyRecorder()

    action_service.apply_recording_actions(
        hands_data=[build_hand(gesture="ROCK")],
        recorder=recorder,
        frame_width=1280,
        frame_height=720,
    )

    assert recorder.is_recording is True
    assert action_service.get_status_message() == "Recording started"

    action_service.last_gesture_per_hand["Right"] = "UNKNOWN"
    action_service.apply_recording_actions(
        hands_data=[build_hand(gesture="ROCK")],
        recorder=recorder,
        frame_width=1280,
        frame_height=720,
    )

    assert recorder.is_recording is False
    assert action_service.get_status_message() == "Recording stopped"


def test_recording_actions_start_uses_camera_frame_size():
    action_service = ActionService(
        screenshot_dir="outputs/screenshots",
        gesture_cooldown_seconds=0.0,
    )
    recorder = DummyRecorder()

    action_service.apply_recording_actions(
        hands_data=[build_hand(gesture="ROCK")],
        recorder=recorder,
        frame_width=640,
        frame_height=480,
    )

    assert recorder.started_size == (640, 480)
