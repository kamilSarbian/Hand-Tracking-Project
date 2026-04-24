import time

from services.drawing_service import DrawingService
from utils.file_utils import save_screenshot


class ActionService:
    """
    Handles user actions in drawing and screenshot modes.
    """

    def __init__(self, screenshot_dir: str, gesture_cooldown_seconds: float = 1.2):
        self.screenshot_dir = screenshot_dir
        self.gesture_cooldown_seconds = gesture_cooldown_seconds

        self.current_color = (0, 0, 255)
        self.color_cycle = [
            (0, 0, 255),    # red
            (0, 255, 0),    # green
            (255, 0, 0),    # blue
            (0, 255, 255),  # yellow
            (255, 0, 255),  # purple
        ]
        self.color_index = 0

        self.last_gesture_per_hand = {}
        self.last_trigger_times = {}
        self.status_message = "Ready"

    def get_color(self):
        return self.current_color

    def get_status_message(self):
        return self.status_message

    def set_status(self, message: str):
        self.status_message = message

    def reset_gesture_state(self):
        """Clear gesture locks when switching app modes."""
        self.last_gesture_per_hand.clear()

    def _next_color(self):
        self.color_index = (self.color_index + 1) % len(self.color_cycle)
        self.current_color = self.color_cycle[self.color_index]
        self.status_message = "Color changed"

    def _save_screenshot(self, frame):
        file_path = save_screenshot(frame, self.screenshot_dir)
        self.status_message = "Screenshot saved"
        return file_path

    def _can_trigger(self, hand_key: str, gesture: str) -> bool:
        """Debounce gestures so one held gesture does not trigger repeatedly."""
        now = time.time()
        trigger_key = f"{hand_key}:{gesture}"
        last_time = self.last_trigger_times.get(trigger_key, 0.0)

        if now - last_time >= self.gesture_cooldown_seconds:
            self.last_trigger_times[trigger_key] = now
            return True

        return False

    def apply_drawing_actions(self, hands_data, drawing_service: DrawingService):
        drawing_detected = False

        if not hands_data:
            drawing_service.pause()
            self.status_message = "Paused"
            return None

        for hand_data in hands_data:
            hand_key = hand_data.label
            gesture = hand_data.gesture_name
            last_gesture = self.last_gesture_per_hand.get(hand_key)

            if gesture == "THREE" and last_gesture != "THREE":
                self._next_color()

            elif gesture == "FIST" and last_gesture != "FIST":
                drawing_service.clear()
                self.status_message = "Canvas cleared"

            elif gesture == "POINT":
                drawing_service.draw_point_path(
                    x=hand_data.index_tip.x,
                    y=hand_data.index_tip.y,
                    color=self.current_color
                )
                drawing_detected = True
                self.status_message = "Drawing"

            elif gesture == "OPEN_HAND":
                drawing_service.pause()
                self.status_message = "Paused"

            elif gesture == "PEACE":
                self.status_message = "PEACE is available in Screenshot mode"

            else:
                self.status_message = f"Gesture: {gesture}"

            self.last_gesture_per_hand[hand_key] = gesture

        if not drawing_detected:
            drawing_service.pause()

        return None

    def apply_screenshot_actions(self, hands_data, frame):
        screenshot_path = None

        if not hands_data:
            self.status_message = "Waiting for a hand"
            return screenshot_path

        for hand_data in hands_data:
            hand_key = hand_data.label
            gesture = hand_data.gesture_name
            last_gesture = self.last_gesture_per_hand.get(hand_key)

            if gesture == "PEACE":
                if last_gesture != "PEACE" and self._can_trigger(hand_key, "PEACE"):
                    screenshot_path = self._save_screenshot(frame)
            else:
                self.status_message = f"Gesture: {gesture}"

            self.last_gesture_per_hand[hand_key] = gesture

        return screenshot_path

    def apply_recording_actions(self, hands_data, recorder, frame_width: int, frame_height: int):
        if not hands_data:
            return None

        for hand_data in hands_data:
            hand_key = hand_data.label
            gesture = hand_data.gesture_name
            last_gesture = self.last_gesture_per_hand.get(hand_key)

            if gesture == "ROCK" and last_gesture != "ROCK" and self._can_trigger(hand_key, "ROCK"):
                if not recorder.is_recording:
                    path = recorder.start(frame_width, frame_height)
                    if path is not None:
                        self.status_message = "Recording started"
                    else:
                        self.status_message = "Could not start recording"
                else:
                    recorder.stop()
                    self.status_message = "Recording stopped"
            else:
                self.status_message = f"Gesture: {gesture}"

            self.last_gesture_per_hand[hand_key] = gesture

        return None
