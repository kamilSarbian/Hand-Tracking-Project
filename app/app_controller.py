import math

from config import APP_HEIGHT, APP_WIDTH


class AppController:
    """
    Coordinates screen routing, per-screen actions, and rendering.
    """

    def __init__(
        self,
        screen_manager,
        menu_screen,
        drawing_screen,
        help_screen,
        screenshot_screen,
        recording_screen,
        drawing_service,
        action_service,
        renderer,
        recorder,
        logger,
        app_width: int = APP_WIDTH,
        app_height: int = APP_HEIGHT,
    ):
        self.screen_manager = screen_manager
        self.menu_screen = menu_screen
        self.drawing_screen = drawing_screen
        self.help_screen = help_screen
        self.screenshot_screen = screenshot_screen
        self.recording_screen = recording_screen
        self.drawing_service = drawing_service
        self.action_service = action_service
        self.renderer = renderer
        self.recorder = recorder
        self.logger = logger
        self.app_width = app_width
        self.app_height = app_height

        self.last_ui_pointer = None
        self.pointer_smoothing = 0.72

    def _set_screen(self, screen_name: str):
        self.screen_manager.set_screen(screen_name)
        if hasattr(self.action_service, "reset_gesture_state"):
            self.action_service.reset_gesture_state()

    def _record_frame_if_needed(self, display_frame):
        if self.recorder.is_recording:
            self.recorder.write(display_frame)

    def _map_camera_point_to_app_canvas(
        self, point, frame_width: int, frame_height: int
    ):
        """
        Maps a camera-space point to the full app canvas.
        """
        if point is None:
            return None

        x, y = point

        if frame_width <= 0 or frame_height <= 0:
            return None

        margin_x = 0.08
        margin_y = 0.10

        min_x = frame_width * margin_x
        max_x = frame_width * (1 - margin_x)
        min_y = frame_height * margin_y
        max_y = frame_height * (1 - margin_y)

        x = max(min_x, min(max_x, x))
        y = max(min_y, min(max_y, y))

        norm_x = (x - min_x) / (max_x - min_x)
        norm_y = (y - min_y) / (max_y - min_y)

        deadzone = 0.008

        if abs(norm_x - 0.5) < deadzone:
            norm_x = 0.5

        if abs(norm_y - 0.5) < deadzone:
            norm_y = 0.5

        ui_x = int(norm_x * self.app_width)
        ui_y = int(norm_y * self.app_height)

        ui_x = max(0, min(self.app_width - 1, ui_x))
        ui_y = max(0, min(self.app_height - 1, ui_y))

        return ui_x, ui_y

    def _smooth_pointer(self, point):
        """
        Smooths pointer movement.
        """
        if point is None:
            self.last_ui_pointer = None
            return None

        if self.last_ui_pointer is None:
            self.last_ui_pointer = point
            return point

        old_x, old_y = self.last_ui_pointer
        new_x, new_y = point

        dx = new_x - old_x
        dy = new_y - old_y
        distance = math.hypot(dx, dy)

        if distance < 2:
            return self.last_ui_pointer

        if distance >= 120:
            dynamic_smoothing = 1.0
        else:
            dynamic_smoothing = min(0.96, self.pointer_smoothing + distance / 180.0)

        smooth_x = int(old_x + dx * dynamic_smoothing)
        smooth_y = int(old_y + dy * dynamic_smoothing)

        self.last_ui_pointer = (smooth_x, smooth_y)
        return self.last_ui_pointer

    def extract_pointer_and_gesture(
        self, hands_data, frame_width: int, frame_height: int
    ):
        """
        The first detected hand controls the UI.
        """
        if not hands_data:
            return None, None

        primary_hand = hands_data[0]
        camera_pointer = (primary_hand.index_tip.x, primary_hand.index_tip.y)

        ui_pointer = self._map_camera_point_to_app_canvas(
            point=camera_pointer,
            frame_width=frame_width,
            frame_height=frame_height,
        )

        ui_pointer = self._smooth_pointer(ui_pointer)
        gesture_name = primary_hand.gesture_name

        return ui_pointer, gesture_name

    def _build_camera_view(self, frame, hands_data, use_canvas: bool):
        canvas = self.drawing_service.get_canvas() if use_canvas else None
        return self.renderer.draw(
            frame=frame.copy(), hands_data=hands_data, canvas=canvas
        )

    def render(self, frame, hands_data):
        """
        Main per-screen logic.
        """
        frame_height, frame_width = frame.shape[:2]

        pointer_point, gesture_name = self.extract_pointer_and_gesture(
            hands_data=hands_data,
            frame_width=frame_width,
            frame_height=frame_height,
        )

        current_screen = self.screen_manager.get_screen()

        if current_screen == "menu":
            display_frame = self.menu_screen.render(
                app_width=self.app_width,
                app_height=self.app_height,
                pointer_point=pointer_point,
                hands_data=hands_data,
            )

            selected_screen = self.menu_screen.try_select(gesture_name)

            if selected_screen == "exit":
                self.logger.info("Exit selected from menu")
                self._record_frame_if_needed(display_frame)
                return display_frame, True

            if selected_screen is not None:
                self.logger.info("Selected screen: %s", selected_screen)
                self._set_screen(selected_screen)

            self.menu_screen.reset_selection_lock(gesture_name)
            self._record_frame_if_needed(display_frame)
            return display_frame, False

        if current_screen == "drawing":
            self.action_service.apply_drawing_actions(
                hands_data=hands_data, drawing_service=self.drawing_service
            )

            camera_view = self._build_camera_view(
                frame=frame,
                hands_data=hands_data,
                use_canvas=True,
            )

            display_frame = self.drawing_screen.render(
                app_width=self.app_width,
                app_height=self.app_height,
                camera_view=camera_view,
                hands_data=hands_data,
                status_message=self.action_service.get_status_message(),
                current_color=self.action_service.get_color(),
                is_recording=self.recorder.is_recording,
                pointer_point=pointer_point,
            )

            self._record_frame_if_needed(display_frame)

            if self.drawing_screen.try_go_back(pointer_point, gesture_name):
                self.logger.info("Back to menu selected from drawing screen")
                self._set_screen("menu")

            return display_frame, False

        if current_screen == "help":
            display_frame = self.help_screen.render(
                app_width=self.app_width,
                app_height=self.app_height,
                pointer_point=pointer_point,
                hands_data=hands_data,
            )

            if self.help_screen.try_go_back(pointer_point, gesture_name):
                self.logger.info("Back to menu selected from help screen")
                self._set_screen("menu")

            self._record_frame_if_needed(display_frame)
            return display_frame, False

        if current_screen == "screenshot":
            try:
                screenshot_path = self.action_service.apply_screenshot_actions(
                    hands_data=hands_data, frame=frame.copy()
                )
            except OSError as exc:
                screenshot_path = None
                self.logger.error("Gesture screenshot failed: %s", exc)
                self.action_service.set_status("Could not save screenshot")

            if screenshot_path:
                self.logger.info("Gesture screenshot saved: %s", screenshot_path)

            camera_view = self._build_camera_view(
                frame=frame,
                hands_data=hands_data,
                use_canvas=False,
            )

            display_frame = self.screenshot_screen.render(
                app_width=self.app_width,
                app_height=self.app_height,
                camera_view=camera_view,
                hands_data=hands_data,
                pointer_point=pointer_point,
                status_message=self.action_service.get_status_message(),
            )

            if self.screenshot_screen.try_go_back(pointer_point, gesture_name):
                self.logger.info("Back to menu selected from screenshot screen")
                self._set_screen("menu")

            self._record_frame_if_needed(display_frame)
            return display_frame, False

        if current_screen == "recording":
            self.action_service.apply_recording_actions(
                hands_data=hands_data,
                recorder=self.recorder,
                frame_width=frame_width,
                frame_height=frame_height,
            )

            camera_view = self._build_camera_view(
                frame=frame,
                hands_data=hands_data,
                use_canvas=False,
            )

            display_frame = self.recording_screen.render(
                app_width=self.app_width,
                app_height=self.app_height,
                camera_view=camera_view,
                hands_data=hands_data,
                pointer_point=pointer_point,
                is_recording=self.recorder.is_recording,
                status_message=self.action_service.get_status_message(),
            )

            self._record_frame_if_needed(camera_view)

            if self.recording_screen.try_go_back(pointer_point, gesture_name):
                self.logger.info("Back to menu selected from recording screen")
                self._set_screen("menu")

            return display_frame, False

        display_frame = self.menu_screen.render(
            app_width=self.app_width,
            app_height=self.app_height,
            pointer_point=pointer_point,
            hands_data=hands_data,
        )
        self._record_frame_if_needed(display_frame)
        return display_frame, False
