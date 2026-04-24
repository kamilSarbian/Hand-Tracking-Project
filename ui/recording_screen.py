import cv2
import math
import time

from ui.components import (
    create_app_canvas,
    draw_button,
    draw_hand_status_badge,
    draw_icon_dot,
    get_hand_badge_positions,
    draw_panel,
    draw_pointer,
    draw_text,
    draw_text_lines,
    draw_top_bar,
    point_in_rect,
)


class RecordingScreen:
    """
    Recording mode screen.
    """

    def __init__(self):
        self.back_button_rect = None
        self.countdown_seconds = 3.0
        self.back_pending_started_at = None
        self._base_cache = None
        self._base_cache_size = None

    def _build_layout(self, app_width: int, app_height: int):
        top_bar_h = max(90, int(app_height * 0.12))
        side_panel_w = int(app_width * 0.30)

        content_y = top_bar_h + 20
        content_h = app_height - content_y - 20

        camera_rect = (20, content_y, app_width - side_panel_w - 60, content_h)
        side_rect = (camera_rect[0] + camera_rect[2] + 20, content_y, side_panel_w, content_h)

        return {
            "camera_rect": camera_rect,
            "side_rect": side_rect,
        }

    def _fit_frame_to_rect(self, frame, rect):
        _, _, w, h = rect
        return cv2.resize(frame, (w, h))

    def get_hovered_back(self, pointer_point):
        if pointer_point is None or self.back_button_rect is None:
            return False
        return point_in_rect(pointer_point, self.back_button_rect)

    def try_go_back(self, pointer_point, gesture_name: str):
        hovered = self.get_hovered_back(pointer_point)

        if self.back_pending_started_at is not None:
            if not hovered or gesture_name != "PINCH":
                self.back_pending_started_at = None
                return False

            elapsed = time.monotonic() - self.back_pending_started_at
            if elapsed >= self.countdown_seconds:
                self.back_pending_started_at = None
                return True
            return False

        if hovered and gesture_name == "PINCH":
            self.back_pending_started_at = time.monotonic()

        return False

    def _back_countdown_number(self):
        if self.back_pending_started_at is None:
            return None
        remaining = max(0.0, self.countdown_seconds - (time.monotonic() - self.back_pending_started_at))
        return max(1, math.ceil(remaining))

    def render(
        self,
        app_width: int,
        app_height: int,
        camera_view,
        hands_data,
        pointer_point=None,
        is_recording: bool = False,
        status_message: str = "Ready",
    ):
        layout = self._build_layout(app_width, app_height)
        camera_rect = layout["camera_rect"]
        side_rect = layout["side_rect"]
        cache_size = (app_width, app_height)

        if self._base_cache is None or self._base_cache_size != cache_size:
            base = create_app_canvas(app_width, app_height)
            self._render_static_base(base, layout)
            self._base_cache = base
            self._base_cache_size = cache_size

        canvas = self._base_cache.copy()

        cam_x, cam_y, cam_w, cam_h = camera_rect
        fitted_camera = self._fit_frame_to_rect(camera_view, camera_rect)
        canvas[cam_y:cam_y + cam_h, cam_x:cam_x + cam_w] = fitted_camera

        side_x, side_y, side_w, side_h = side_rect
        self.back_button_rect = (side_x + 20, side_y + 20, side_w - 40, 92)
        back_hovered = self.get_hovered_back(pointer_point)

        draw_button(
            canvas,
            rect=self.back_button_rect,
            title="Back to menu",
            subtitle="Hold PINCH for 3 seconds",
            is_hovered=back_hovered,
            is_active=self.back_pending_started_at is not None,
            badge_text=f"{self._back_countdown_number()}s" if self._back_countdown_number() is not None else None,
        )
        draw_text(canvas, f"Status: {status_message}", (side_x + 20, side_y + 520), font_size=18, color=(230, 230, 230))
        y = side_y + 568

        if hands_data:
            positions = get_hand_badge_positions(
                x=side_x + 20,
                y=y,
                available_w=side_w - 40,
                count=len(hands_data[:2]),
            )
            for hand_data, (badge_x, badge_y) in zip(hands_data[:2], positions):
                draw_hand_status_badge(
                    canvas,
                    badge_x,
                    badge_y,
                    f"{hand_data.label} hand",
                    hand_data.gesture_name or "NONE",
                )
        else:
            draw_text(canvas, "No hand detected", (side_x + 20, y + 8), font_size=18)

        rec_color = (0, 0, 255) if is_recording else (120, 120, 120)
        draw_icon_dot(canvas, side_x + 28, side_y + side_h - 90, color=rec_color)

        rec_text = "ROCK = start / stop recording"
        draw_text(
            canvas,
            rec_text,
            (side_x + 48, side_y + side_h - 102),
            font_size=18,
            color=(255, 255, 255),
        )

        state_text = "Recording now" if is_recording else "Recording stopped"
        draw_text(
            canvas,
            state_text,
            (side_x + 48, side_y + side_h - 70),
            font_size=16,
            color=(220, 220, 220),
        )

        if pointer_point is not None:
            draw_pointer(canvas, pointer_point)

        return canvas

    def _render_static_base(self, canvas, layout):
        camera_rect = layout["camera_rect"]
        side_rect = layout["side_rect"]
        cam_x, cam_y, cam_w, cam_h = camera_rect
        side_x, side_y, side_w, side_h = side_rect

        draw_top_bar(
            canvas,
            title="Mode: Recording",
            subtitle="Press R to start or stop recording.",
        )
        draw_panel(canvas, cam_x, cam_y, cam_w, cam_h, bg_color=(18, 18, 18))
        draw_panel(canvas, side_x, side_y, side_w, side_h, bg_color=(24, 24, 24))
        draw_text(canvas, "Recording", (side_x + 20, side_y + 150), font_size=28)

        lines = [
            "How to record:",
            "",
            "1. Make the ROCK gesture",
            "2. Make ROCK again to stop",
            "",
            "Alternative:",
            "- press R to start or stop",
            "",
            "Detected hands:",
        ]
        draw_text_lines(
            canvas,
            lines=lines,
            start_position=(side_x + 20, side_y + 205),
            line_height=32,
            font_size=18,
            color=(230, 230, 230),
        )
