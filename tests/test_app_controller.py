from app.app_controller import AppController


class DummyScreenManager:
    def __init__(self):
        self.current_screen = "menu"

    def get_screen(self):
        return self.current_screen

    def set_screen(self, screen_name):
        self.current_screen = screen_name


class DummyRecorder:
    is_recording = False

    def write(self, frame):
        pass


class DummyObj:
    pass


def build_controller():
    """
    Builds a minimal AppController for helper method tests.
    """
    return AppController(
        screen_manager=DummyScreenManager(),
        menu_screen=DummyObj(),
        drawing_screen=DummyObj(),
        help_screen=DummyObj(),
        screenshot_screen=DummyObj(),
        recording_screen=DummyObj(),
        drawing_service=DummyObj(),
        action_service=DummyObj(),
        renderer=DummyObj(),
        recorder=DummyRecorder(),
        logger=DummyObj(),
    )


def test_map_camera_point_to_app_canvas_inside_bounds():
    """
    A camera point should map inside app_canvas bounds.
    """
    controller = build_controller()

    point = controller._map_camera_point_to_app_canvas(
        point=(320, 240), frame_width=640, frame_height=480
    )

    assert point is not None
    x, y = point

    assert 0 <= x <= 1399
    assert 0 <= y <= 899


def test_map_camera_point_to_app_canvas_none_returns_none():
    """
    None input should return None.
    """
    controller = build_controller()

    point = controller._map_camera_point_to_app_canvas(
        point=None, frame_width=640, frame_height=480
    )

    assert point is None


def test_smooth_pointer_returns_same_point_on_first_call():
    """
    The first smooth call should return the same point.
    """
    controller = build_controller()

    point = controller._smooth_pointer((100, 200))
    assert point == (100, 200)


def test_smooth_pointer_moves_quickly_on_large_distance():
    """
    Large pointer jumps should not lag far behind the target.
    """
    controller = build_controller()
    controller._smooth_pointer((100, 100))

    point = controller._smooth_pointer((500, 500))

    assert point[0] > 300
    assert point[1] > 300
