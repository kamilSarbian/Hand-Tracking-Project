from utils.file_utils import save_screenshot


class KeyHandler:
    """
    Handles keyboard shortcuts.
    """

    def __init__(
        self, screen_manager, action_service, recorder, screenshot_dir, logger
    ):
        self.screen_manager = screen_manager
        self.action_service = action_service
        self.recorder = recorder
        self.screenshot_dir = screenshot_dir
        self.logger = logger

    def handle(self, key, display_frame):
        """
        Returns should_close: bool.
        """
        if key == 27:
            self.logger.info("ESC pressed. Closing application")
            return True

        if key in (ord("m"), ord("M")):
            self.logger.info("Returning to menu")
            self.screen_manager.set_screen("menu")
            if hasattr(self.action_service, "reset_gesture_state"):
                self.action_service.reset_gesture_state()
            return False

        if key in (ord("s"), ord("S")):
            try:
                path = save_screenshot(display_frame, self.screenshot_dir)
            except OSError as exc:
                self.logger.error("Manual screenshot failed: %s", exc)
                self.action_service.set_status("Could not save screenshot")
                return False

            self.logger.info("Manual screenshot saved: %s", path)
            self.action_service.set_status("Manual screenshot saved")
            return False

        if key in (ord("r"), ord("R")):
            if not self.recorder.is_recording:
                path = self.recorder.start(
                    display_frame.shape[1], display_frame.shape[0]
                )

                if path is not None:
                    self.logger.info("Recording started: %s", path)
                    self.action_service.set_status("Recording started")
                else:
                    self.logger.error("Could not start recording")
                    self.action_service.set_status("Could not start recording")
            else:
                path = self.recorder.stop()
                self.logger.info("Recording stopped: %s", path)
                self.action_service.set_status("Recording stopped")

        return False
