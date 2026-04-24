import math
import time

from ui.components import (
    create_app_canvas,
    draw_button,
    draw_hand_status_badge,
    get_hand_badge_positions,
    draw_panel,
    draw_pointer,
    draw_text,
    draw_text_lines,
    draw_top_bar,
    point_in_rect,
)


class HelpScreen:
    """
    Beginner-friendly help screen.
    """

    def __init__(self):
        self.back_button_rect = None
        self.countdown_seconds = 3.0
        self.back_pending_started_at = None
        self._base_cache = None
        self._base_cache_size = None

    def _build_layout(self, app_width: int, app_height: int):
        top_bar_h = max(90, int(app_height * 0.13))
        footer_h = max(60, int(app_height * 0.08))

        content_y = top_bar_h + 20
        content_h = app_height - content_y - footer_h - 20
        content_x = 20
        content_w = app_width - 40

        return {
            "footer_h": footer_h,
            "content_rect": (content_x, content_y, content_w, content_h),
        }

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

    def render(self, app_width: int, app_height: int, pointer_point=None, hands_data=None):
        layout = self._build_layout(app_width, app_height)
        content_x, content_y, content_w, content_h = layout["content_rect"]
        cache_size = (app_width, app_height)

        if self._base_cache is None or self._base_cache_size != cache_size:
            base = create_app_canvas(app_width, app_height)
            self._render_static_base(base, layout)
            self._base_cache = base
            self._base_cache_size = cache_size

        canvas = self._base_cache.copy()
        hands_panel_x = content_x + content_w - 320
        hands_panel_y = content_y + 92

        draw_panel(
            canvas,
            hands_panel_x,
            hands_panel_y,
            280,
            170,
            bg_color=(29, 34, 40),
            border_color=(78, 90, 109),
        )

        draw_text(
            canvas,
            "Detected hands",
            (hands_panel_x + 18, hands_panel_y + 22),
            font_size=18,
            color=(255, 255, 255),
        )

        if hands_data:
            positions = get_hand_badge_positions(
                x=hands_panel_x + 18,
                y=hands_panel_y + 48,
                available_w=244,
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
            draw_text(
                canvas,
                "No hand detected",
                (hands_panel_x + 18, hands_panel_y + 64),
                font_size=16,
                color=(225, 225, 225),
            )

        self.back_button_rect = (
            content_x + content_w - 390,
            content_y + content_h - 112,
            350,
            82,
        )

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

        footer_y = app_height - layout["footer_h"]
        draw_panel(canvas, 0, footer_y, app_width, layout["footer_h"], bg_color=(15, 15, 15), border_thickness=0)

        draw_text(
            canvas,
            "Hover over Back and hold PINCH for 3 seconds",
            (20, footer_y + 18),
            font_size=18,
            color=(230, 230, 230),
        )

        if pointer_point is not None:
            draw_pointer(canvas, pointer_point)

        return canvas

    def _render_static_base(self, canvas, layout):
        content_x, content_y, content_w, content_h = layout["content_rect"]
        left_col_w = int(content_w * 0.58)
        right_col_x = content_x + left_col_w + 30

        draw_top_bar(
            canvas,
            title="Help",
            subtitle="A quick guide for getting started",
        )
        draw_panel(canvas, content_x, content_y, content_w, content_h, bg_color=(24, 24, 24))
        draw_text(
            canvas,
            "How does this app work?",
            (content_x + 25, content_y + 20),
            font_size=28,
            color=(255, 255, 255),
        )

        left_lines = [
            "Use hand gestures in front of the camera to control the app.",
            "",
            "Using the menu:",
            "1. Show your hand to the camera",
            "2. Use your index finger as a cursor",
            "3. Hover over the option you want",
            "4. PINCH to select it",
            "5. Wait for the 3 second countdown",
            "",
            "Drawing mode:",
            "- POINT: draw",
            "- THREE: change color",
            "- FIST: clear the canvas",
            "- OPEN_HAND: pause",
            "",
            "Screenshot mode:",
            "- PEACE: save a screenshot",
        ]

        right_lines = [
            "",
            "Extra recognized gestures:",
            "- THREE",
            "- ROCK",
            "- THUMBS_UP",
            "",
            "Keyboard shortcuts:",
            "- M: return to menu",
            "- S: save screenshot",
            "- R: start or stop recording",
            "- ESC: exit",
        ]

        draw_text_lines(
            canvas,
            lines=left_lines,
            start_position=(content_x + 25, content_y + 70),
            line_height=29,
            font_size=18,
            color=(225, 225, 225),
        )

        draw_text_lines(
            canvas,
            lines=right_lines,
            start_position=(right_col_x, content_y + 70),
            line_height=30,
            font_size=18,
            color=(225, 225, 225),
        )
