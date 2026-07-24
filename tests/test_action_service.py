from pathlib import Path

from models.hand_data import FingerState, HandData, HandMetrics, Point2D
from services.action_service import ActionService
from services.drawing_service import DrawingService


def build_hand(label="Right", gesture="POINT", x=100, y=100):
    """
    Builds a sample HandData object for tests.
    """
    return HandData(
        label=label,
        landmarks_px=[],
        thumb_tip=Point2D(80, 100),
        index_tip=Point2D(x, y),
        center_point=Point2D(90, 100),
        metrics=HandMetrics(distance_thumb_index=50, pinch_active=False, radius=25),
        fingers=FingerState(
            thumb=False, index=True, middle=False, ring=False, pinky=False
        ),
        gesture_name=gesture,
    )


def test_apply_drawing_actions_point_sets_status_and_draws(tmp_path):
    """
    POINT should start drawing and set the status.
    """
    action_service = ActionService(screenshot_dir=str(tmp_path))
    drawing_service = DrawingService(thickness=5)
    drawing_service.ensure_canvas(300, 300)

    hands_data = [build_hand(gesture="POINT", x=120, y=140)]

    result = action_service.apply_drawing_actions(
        hands_data=hands_data, drawing_service=drawing_service
    )

    assert result is None
    assert action_service.get_status_message() == "Drawing"
    assert drawing_service.last_draw_point == (120, 140)


def test_apply_drawing_actions_fist_clears_canvas(tmp_path):
    """
    FIST should clear the canvas and set the status.
    """
    action_service = ActionService(screenshot_dir=str(tmp_path))
    drawing_service = DrawingService(thickness=5)
    drawing_service.ensure_canvas(200, 200)

    drawing_service.canvas[50:60, 50:60] = 255

    hands_data = [build_hand(gesture="FIST")]

    action_service.apply_drawing_actions(
        hands_data=hands_data, drawing_service=drawing_service
    )

    assert drawing_service.canvas.sum() == 0
    assert action_service.get_status_message() == "Canvas cleared"


def test_apply_drawing_actions_three_changes_color(tmp_path):
    action_service = ActionService(screenshot_dir=str(tmp_path))
    drawing_service = DrawingService(thickness=5)
    drawing_service.ensure_canvas(200, 200)

    original_color = action_service.get_color()

    action_service.apply_drawing_actions(
        hands_data=[build_hand(gesture="THREE")], drawing_service=drawing_service
    )

    assert action_service.get_color() != original_color
    assert action_service.get_status_message() == "Color changed"


def test_apply_screenshot_actions_peace_creates_file(tmp_path):
    """
    PEACE in screenshot mode should save a file.
    """
    action_service = ActionService(screenshot_dir=str(tmp_path))
    fake_frame_path_ready = __import__("numpy").zeros((100, 100, 3), dtype="uint8")

    hands_data = [build_hand(gesture="PEACE")]

    file_path = action_service.apply_screenshot_actions(
        hands_data=hands_data, frame=fake_frame_path_ready
    )

    assert file_path is not None
    assert Path(file_path).exists()


def test_apply_screenshot_actions_no_hands_sets_wait_status(tmp_path):
    """
    No hands should set the waiting status.
    """
    action_service = ActionService(screenshot_dir=str(tmp_path))
    fake_frame = __import__("numpy").zeros((100, 100, 3), dtype="uint8")

    file_path = action_service.apply_screenshot_actions(hands_data=[], frame=fake_frame)

    assert file_path is None
    assert action_service.get_status_message() == "Waiting for a hand"
