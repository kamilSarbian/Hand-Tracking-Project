import math
import time

from ui.components import (
    create_app_canvas,
    draw_button,
    draw_hand_status_badge,
    draw_panel,
    draw_pointer,
    draw_text,
    draw_text_lines,
    draw_top_bar,
    get_hand_badge_positions,
    point_in_rect,
)


class MenuScreen:
    """
    Main menu screen with a short countdown before opening a mode.
    """

    def __init__(self, countdown_seconds: float = 3.0):
        self.menu_items = [
            {
                "title": "Drawing",
                "subtitle": "Draw in the air with your index finger",
                "screen": "drawing",
                "accent": (102, 181, 255),
            },
            {
                "title": "Screenshot",
                "subtitle": "Save an image with PEACE or the S key",
                "screen": "screenshot",
                "accent": (104, 208, 173),
            },
            {
                "title": "Recording",
                "subtitle": "Record a demo of the app",
                "screen": "recording",
                "accent": (118, 133, 255),
            },
            {
                "title": "Help",
                "subtitle": "Quick guide for new users",
                "screen": "help",
                "accent": (255, 192, 92),
            },
            {
                "title": "Exit",
                "subtitle": "Close the application",
                "screen": "exit",
                "accent": (255, 115, 115),
            },
        ]

        self.countdown_seconds = countdown_seconds
        self.hovered_item_index = None
        self.last_selected_item_index = None
        self.pending_item_index = None
        self.pending_started_at = None
        self._base_cache = None
        self._base_cache_size = None

    def _build_layout(self, app_width: int, app_height: int):
        top_bar_h = max(90, int(app_height * 0.13))
        footer_h = max(60, int(app_height * 0.08))

        left_panel_w = int(app_width * 0.34)
        right_panel_x = left_panel_w + 20
        right_panel_w = app_width - right_panel_x - 20

        content_y = top_bar_h + 20
        content_h = app_height - content_y - footer_h - 20

        return {
            "top_bar_h": top_bar_h,
            "footer_h": footer_h,
            "left_panel": (20, content_y, left_panel_w, content_h),
            "right_panel": (right_panel_x, content_y, right_panel_w, content_h),
        }

    def _build_menu_rects(self, right_panel: tuple[int, int, int, int]):
        x, y, w, h = right_panel
        item_count = len(self.menu_items)
        header_h = max(58, int(h * 0.10))
        bottom_padding = max(14, int(h * 0.03))
        gap = max(8, min(16, int(h * 0.025)))
        available_h = h - header_h - bottom_padding - gap * (item_count - 1)
        tile_h = max(58, available_h // item_count)

        rects = []
        current_y = y + header_h

        for _ in self.menu_items:
            rects.append((x + 20, current_y, w - 40, tile_h))
            current_y += tile_h + gap

        return rects

    def _pending_item(self):
        if self.pending_item_index is None:
            return None
        return self.menu_items[self.pending_item_index]

    def _countdown_remaining(self):
        if self.pending_started_at is None:
            return None

        elapsed = time.monotonic() - self.pending_started_at
        return max(0.0, self.countdown_seconds - elapsed)

    def _countdown_number(self):
        remaining = self._countdown_remaining()
        if remaining is None:
            return None

        return max(1, math.ceil(remaining))

    def _countdown_progress(self):
        if self.pending_started_at is None:
            return 0.0

        elapsed = time.monotonic() - self.pending_started_at
        return min(1.0, max(0.0, elapsed / self.countdown_seconds))

    def update_hover(self, pointer_point, menu_rects):
        self.hovered_item_index = None

        if pointer_point is None:
            return

        for idx, rect in enumerate(menu_rects):
            if point_in_rect(pointer_point, rect):
                self.hovered_item_index = idx
                break

    def try_select(self, gesture_name: str):
        """
        Starts a countdown on PINCH and returns the target screen only if the
        same menu item stays hovered while PINCH is continuously held.
        """
        pending_item = self._pending_item()
        remaining = self._countdown_remaining()

        if pending_item is not None:
            pending_index = self.pending_item_index
            is_same_item_hovered = self.hovered_item_index == pending_index

            if gesture_name != "PINCH" or not is_same_item_hovered:
                self.pending_item_index = None
                self.pending_started_at = None
                self.last_selected_item_index = None
                return None

        if pending_item is not None and remaining == 0.0:
            selected_screen = pending_item["screen"]
            self.pending_item_index = None
            self.pending_started_at = None
            self.last_selected_item_index = None
            return selected_screen

        if pending_item is not None:
            return None

        if gesture_name != "PINCH":
            return None

        if self.hovered_item_index is None:
            return None

        if self.last_selected_item_index == self.hovered_item_index:
            return None

        self.last_selected_item_index = self.hovered_item_index
        self.pending_item_index = self.hovered_item_index
        self.pending_started_at = time.monotonic()
        return None

    def reset_selection_lock(self, gesture_name: str):
        if gesture_name != "PINCH" and self.pending_item_index is None:
            self.last_selected_item_index = None

    def render(
        self, app_width: int, app_height: int, pointer_point=None, hands_data=None
    ):
        layout = self._build_layout(app_width, app_height)
        menu_rects = self._build_menu_rects(layout["right_panel"])
        cache_size = (app_width, app_height)

        if self._base_cache is None or self._base_cache_size != cache_size:
            base = create_app_canvas(app_width, app_height)
            self._render_static_base(base, layout)
            self._base_cache = base
            self._base_cache_size = cache_size

        canvas = self._base_cache.copy()
        lp_x, lp_y, lp_w, lp_h = layout["left_panel"]
        rp_x, rp_y, rp_w, rp_h = layout["right_panel"]

        self.update_hover(pointer_point, menu_rects)

        self._draw_dynamic_left_panel(canvas, lp_x, lp_y, lp_w, lp_h, hands_data)
        self._draw_dynamic_menu(canvas, rp_x, rp_y, rp_w, rp_h, menu_rects)

        if pointer_point is not None:
            draw_pointer(canvas, pointer_point)

        return canvas

    def _render_static_base(self, canvas, layout):
        lp_x, lp_y, lp_w, lp_h = layout["left_panel"]
        rp_x, rp_y, rp_w, rp_h = layout["right_panel"]
        section_x = lp_x + 18
        section_w = lp_w - 36

        draw_top_bar(
            canvas,
            title="Gesture Drawing App",
            subtitle="Point at a tile, then hold PINCH for 3 seconds to open it",
        )

        draw_panel(
            canvas,
            lp_x,
            lp_y,
            lp_w,
            lp_h,
            bg_color=(25, 30, 38),
            border_color=(74, 88, 110),
        )

        draw_text(
            canvas,
            "Quick Start",
            (lp_x + 24, lp_y + 30),
            font_size=26,
            color=(255, 255, 255),
        )

        intro_panel_y = lp_y + 64
        intro_panel_h = 306
        draw_panel(
            canvas,
            section_x,
            intro_panel_y,
            section_w,
            intro_panel_h,
            bg_color=(30, 37, 46),
            border_color=(84, 102, 131),
        )

        draw_text(
            canvas,
            "How to use the menu",
            (section_x + 18, intro_panel_y + 24),
            font_size=18,
            color=(154, 191, 255),
        )

        help_lines = [
            "1. Show one hand clearly to the camera",
            "2. Move your index finger to aim at a tile",
            "3. Hold PINCH for 3 seconds to confirm",
            "",
            "Main gestures",
            "POINT  - move / draw",
            "PINCH  - confirm",
            "THREE  - change color",
            "FIST   - clear canvas",
            "PEACE  - save screenshot",
            "OPEN   - pause drawing",
        ]

        draw_text_lines(
            canvas,
            lines=help_lines,
            start_position=(section_x + 18, intro_panel_y + 58),
            line_height=23,
            font_size=16,
            color=(226, 231, 238),
        )

        tips_panel_y = intro_panel_y + intro_panel_h + 16
        tips_panel_h = 136
        draw_panel(
            canvas,
            section_x,
            tips_panel_y,
            section_w,
            tips_panel_h,
            bg_color=(30, 37, 46),
            border_color=(84, 102, 131),
        )

        draw_text(
            canvas,
            "What happens next",
            (section_x + 18, tips_panel_y + 24),
            font_size=20,
            color=(255, 255, 255),
        )

        tips_lines = [
            "Drawing: sketch with your finger in the air",
            "Screenshot: capture an image with PEACE",
            "Recording: save a demo video",
            "Help: show all controls on one screen",
        ]

        draw_text_lines(
            canvas,
            lines=tips_lines,
            start_position=(section_x + 18, tips_panel_y + 58),
            line_height=22,
            font_size=16,
            color=(214, 221, 230),
        )

        draw_panel(
            canvas,
            rp_x,
            rp_y,
            rp_w,
            rp_h,
            bg_color=(24, 28, 34),
            border_color=(75, 89, 111),
        )

        draw_text(
            canvas,
            "Choose a Mode",
            (rp_x + 24, rp_y + 30),
            font_size=28,
            color=(255, 255, 255),
        )

        draw_text(
            canvas,
            "Hover a card and keep PINCH held until the countdown ends",
            (rp_x + 24, rp_y + 66),
            font_size=16,
            color=(178, 189, 205),
        )

        footer_y = canvas.shape[0] - layout["footer_h"]
        draw_panel(
            canvas,
            14,
            footer_y + 6,
            canvas.shape[1] - 28,
            layout["footer_h"] - 12,
            bg_color=(19, 23, 29),
            border_color=(60, 72, 92),
            border_thickness=1,
        )

        draw_text(
            canvas,
            "Controls: index finger = aim  |  PINCH = confirm  |  M = menu  |  S = screenshot  |  R = record  |  ESC = exit",
            (34, footer_y + 22),
            font_size=17,
            color=(227, 231, 237),
        )

    def _draw_dynamic_left_panel(self, canvas, lp_x, lp_y, lp_w, lp_h, hands_data):
        section_x = lp_x + 18
        section_w = lp_w - 36
        intro_panel_y = lp_y + 64
        intro_panel_h = 306
        tips_panel_y = intro_panel_y + intro_panel_h + 16
        tips_panel_h = 136
        hands_panel_y = tips_panel_y + tips_panel_h + 16
        hands_panel_h = 128

        draw_panel(
            canvas,
            section_x,
            hands_panel_y,
            section_w,
            hands_panel_h,
            bg_color=(30, 37, 46),
            border_color=(84, 102, 131),
        )
        draw_text(
            canvas,
            "Detected hands",
            (section_x + 18, hands_panel_y + 24),
            font_size=20,
            color=(255, 255, 255),
        )

        if hands_data:
            badge_y = hands_panel_y + 54
            positions = get_hand_badge_positions(
                x=section_x + 18,
                y=badge_y,
                available_w=section_w - 36,
                count=len(hands_data[:2]),
            )
            if positions:
                min_x = min(x for x, _ in positions)
                max_x = max(x + 200 for x, _ in positions)
                total_w = max_x - min_x
                offset_x = section_x + (section_w - total_w) // 2 - min_x
                positions = [(x + offset_x, y) for x, y in positions]
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
                (section_x + 18, hands_panel_y + 78),
                font_size=18,
                color=(214, 221, 230),
            )

    def _draw_dynamic_menu(self, canvas, rp_x, rp_y, rp_w, rp_h, menu_rects):
        for idx, item in enumerate(self.menu_items):
            rect = menu_rects[idx]
            is_hovered = idx == self.hovered_item_index
            is_pending = idx == self.pending_item_index
            badge_text = None

            if is_pending:
                countdown = self._countdown_number()
                if countdown is not None:
                    badge_text = f"{countdown}s"

            draw_button(
                canvas,
                rect=rect,
                title=item["title"],
                subtitle=item["subtitle"],
                is_hovered=is_hovered,
                is_active=is_pending,
                accent_color=item["accent"],
                badge_text=badge_text,
            )

            if is_pending:
                x, y, w, h = rect
                progress_w = max(120, w - 68)
                progress_h = 10
                progress_x = x + 34
                progress_y = y + h - 24

                draw_panel(
                    canvas,
                    progress_x,
                    progress_y,
                    progress_w,
                    progress_h,
                    bg_color=(40, 46, 56),
                    border_color=(40, 46, 56),
                    border_thickness=1,
                    shadow=False,
                )

                filled_w = int(progress_w * self._countdown_progress())
                if filled_w > 0:
                    draw_panel(
                        canvas,
                        progress_x,
                        progress_y,
                        filled_w,
                        progress_h,
                        bg_color=item["accent"],
                        border_color=item["accent"],
                        border_thickness=1,
                        shadow=False,
                    )
