import sys

import cv2

from app.app_controller import AppController
from app.frame_processor import FrameProcessor
from app.key_handler import KeyHandler
from app.self_check import run_self_check
from config import (
    APP_HEIGHT,
    APP_WIDTH,
    CAMERA_INDEX,
    DRAW_THICKNESS,
    GESTURE_COOLDOWN_SECONDS,
    LOG_PATH,
    MIRRORED_VIEW,
    PINCH_THRESHOLD,
    RECORDING_DIR,
    SCREENSHOT_DIR,
    WINDOW_NAME,
)
from core.detector import HandDetector
from core.renderer import HandRenderer
from gestures.recognizer import GestureRecognizer
from services.action_service import ActionService
from services.drawing_service import DrawingService
from services.hand_service import HandService
from ui.drawing_screen import DrawingScreen
from ui.help_screen import HelpScreen
from ui.menu_screen import MenuScreen
from ui.recording_screen import RecordingScreen
from ui.screen_manager import ScreenManager
from ui.screenshot_screen import ScreenshotScreen
from utils.display import get_screen_size
from utils.logger import setup_logger
from utils.video_recorder import VideoRecorder

logger = setup_logger(log_path=LOG_PATH)


def main() -> int:
    """Run the application.

    Returns:
        Process exit code. Zero indicates a normal shutdown.
    """
    logger.info("Starting application")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        logger.error("Could not open camera")
        return 1

    screen_width, screen_height = get_screen_size(APP_WIDTH, APP_HEIGHT)
    app_width = max(960, min(screen_width - 80, int(screen_width * 0.94)))
    app_height = max(720, min(screen_height - 120, int(screen_height * 0.90)))

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, app_width, app_height)

    detector = HandDetector()
    hand_service = HandService(
        mirrored_view=MIRRORED_VIEW, pinch_threshold=PINCH_THRESHOLD
    )
    recognizer = GestureRecognizer()
    renderer = HandRenderer()

    drawing_service = DrawingService(thickness=DRAW_THICKNESS)
    action_service = ActionService(
        screenshot_dir=SCREENSHOT_DIR, gesture_cooldown_seconds=GESTURE_COOLDOWN_SECONDS
    )
    recorder = VideoRecorder(output_dir=RECORDING_DIR)

    screen_manager = ScreenManager(initial_screen="menu")
    menu_screen = MenuScreen()
    drawing_screen = DrawingScreen()
    help_screen = HelpScreen()
    screenshot_screen = ScreenshotScreen()
    recording_screen = RecordingScreen()

    frame_processor = FrameProcessor(
        detector=detector,
        hand_service=hand_service,
        recognizer=recognizer,
    )

    app_controller = AppController(
        screen_manager=screen_manager,
        menu_screen=menu_screen,
        drawing_screen=drawing_screen,
        help_screen=help_screen,
        screenshot_screen=screenshot_screen,
        recording_screen=recording_screen,
        drawing_service=drawing_service,
        action_service=action_service,
        renderer=renderer,
        recorder=recorder,
        logger=logger,
        app_width=app_width,
        app_height=app_height,
    )

    key_handler = KeyHandler(
        screen_manager=screen_manager,
        action_service=action_service,
        recorder=recorder,
        screenshot_dir=SCREENSHOT_DIR,
        logger=logger,
    )

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                logger.error("Could not read frame")
                break

            if MIRRORED_VIEW:
                frame = cv2.flip(frame, 1)

            h, w, _ = frame.shape
            drawing_service.ensure_canvas(h, w)

            hands_data = frame_processor.process(frame)
            display_frame, should_close = app_controller.render(frame, hands_data)

            if should_close:
                break

            cv2.imshow(WINDOW_NAME, display_frame)

            key = cv2.waitKey(1) & 0xFF
            should_close = key_handler.handle(key, display_frame)

            if should_close:
                break

    finally:
        detector.close()
        recorder.release()
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Application closed")

    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        raise SystemExit(run_self_check(logger))

    raise SystemExit(main())
